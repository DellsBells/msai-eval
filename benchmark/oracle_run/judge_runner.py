"""judge_runner.py — the blind judge panel (prereg §5).

Panel: gemma4:12b / llama3.2-vision:11b / LFM2-24B / minicpm-v — four lineages, ZERO Qwen, so no
judge ever rates its own lineage (self-preference eliminated by construction, §3). R=3, temp 0.6,
think-off, seeded. Judges rate a single solution 1-5 by OPAQUE ID and NEVER see test results,
config labels, or tier labels (§2/§5). Output rows are frontier_api_scores.json-compatible so the
existing compare()/four_state/certificate.py pipeline consumes them unchanged (§7).

Three-way null path (Exhibit 1 / §5): every reply is VALID / EXCLUDED-AND-DISCLOSED /
REFUSE-THE-RUN. parse_rating -> nan is a null, NEVER a score or a silent drop. Per-judge null rate
> 10% excludes that judge (disclosed); panel J < 3 after exclusions REFUSES the study (§8).
"""
from __future__ import annotations
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, BENCH)
import common      # noqa: E402
import elo_validation as ev   # noqa: E402  (single hardened parser: ev.parse_rating)

RATING_INSTRUCTION = (
    "You are judging the quality of a candidate solution to a programming task. Consider correctness, "
    "clarity, and how well it follows the task. Give a single overall quality rating from 1 (poor) to "
    "5 (excellent).\n\nOutput ONLY a single integer 1-5. Nothing else."
)


def build_judge_prompt(task_prompt, solution_code):
    """Blind rating prompt: the task + the candidate solution, by opaque presentation. No test
    results, no config/tier labels — the judge cannot know which generator produced this or how it
    scored on the hidden tests."""
    return (f"{RATING_INSTRUCTION}\n\n## Task\n{task_prompt.strip()}\n\n"
            f"## Candidate solution\n```python\n{solution_code.strip()}\n```\n\nRating (1-5):")


def judge_one(model, task_prompt, solution_code, seed, timeout=300):
    """One blind rating from one judge. Returns (score_or_nan, raw). think-off, seeded, temp 0.6."""
    prompt = build_judge_prompt(task_prompt, solution_code)
    raw = common.ollama_chat(model, prompt, temperature=common.JUDGE_TEMP, seed=seed,
                             think=False, timeout=timeout)
    return ev.parse_rating(raw), raw


def classify_null_path(rows):
    """Exhibit 1 three-way classification over the collected rows (each {judge, score, ...}).
    Returns per-judge {n, nulls, null_rate, status} where status is VALID / EXCLUDED / (panel) REFUSE,
    plus a panel-level refuse flag when fewer than MIN_JUDGES survive."""
    by_judge = {}
    for r in rows:
        j = r["judge"]
        d = by_judge.setdefault(j, {"n": 0, "nulls": 0})
        d["n"] += 1
        s = r.get("score")
        if s is None or (isinstance(s, float) and s != s):
            d["nulls"] += 1
    out = {}
    survivors = 0
    for j, d in by_judge.items():
        rate = d["nulls"] / d["n"] if d["n"] else 1.0
        status = "EXCLUDED" if rate > common.NULL_RATE_REFUSE else "VALID"
        if status == "VALID":
            survivors += 1
        out[j] = {"n": d["n"], "nulls": d["nulls"], "null_rate": round(rate, 4), "status": status}
    panel_refuse = survivors < common.MIN_JUDGES
    return {"per_judge": out, "survivors": survivors, "panel_refuse": panel_refuse,
            "reason": (f"panel REFUSES: only {survivors} judge(s) with null rate <= "
                       f"{common.NULL_RATE_REFUSE:.0%} (need >= {common.MIN_JUDGES})") if panel_refuse else "ok"}


def row(tier, task_id, config, judge, rep, score, raw, blind):
    """frontier_api_scores.json-compatible row. The oracle config (A/B) maps to the pipeline's
    chosen/rejected axis at analysis; here we keep the true config + the opaque blind id for audit."""
    return {"tier": tier, "pair": task_id, "config": config, "judge": judge, "rep": rep,
            "score": (None if (isinstance(score, float) and score != score) else score),
            "raw": str(raw)[:4000], "blind_id": blind}


def _synthetic_ratings(n_judges=4, reps=3, null_judge=None):
    """Build synthetic rows to exercise the null-path logic WITHOUT any model call (structural smoke)."""
    rows = []
    for ji, j in enumerate(common.JUDGE_PANEL[:n_judges]):
        for r in range(reps):
            sc = float("nan") if (null_judge is not None and ji == null_judge) else float(3 + (r % 3) - 1)
            rows.append(row("subtle", "t05", "A", j, r, sc, "3", common.blind_id("t05", "A", "salt")))
    return rows


if __name__ == "__main__":
    # STRUCTURAL smoke (no model call — honors "do NOT start judging"): show a blind prompt, the opaque
    # IDs, and exercise the three-way null path on synthetic ratings. A live single-task panel run is
    # gated behind the ledger check and rev-lane's greenlight (do not batch-judge before ledger CLEAN).
    tid = sys.argv[1] if len(sys.argv) > 1 else "t05"
    tasks = {t["id"]: t for t in common.discover_tasks(split=None, include_pilot=True)}
    common.require_clean_ledger(list(tasks.values()), allow_smoke_on=[tid])
    task = tasks[tid]
    ref = open(os.path.join(task["dir"], "reference_solution.py"), encoding="utf-8").read()
    prompt = build_judge_prompt(open(os.path.join(task["dir"], "prompt.md"), encoding="utf-8").read(), ref)
    print(f"JUDGE STRUCTURAL SMOKE on {tid} (no model call)")
    print(f"  panel: {common.JUDGE_PANEL}  R={common.JUDGE_R} temp={common.JUDGE_TEMP} think=off")
    print(f"  blind id for ({tid},A): {common.blind_id(tid, 'A', 'demo-salt')}  "
          f"(config/tier NOT shown to judge)")
    print(f"  blind prompt ({len(prompt)} chars), head:\n    " + prompt[:180].replace("\n", "\n    "))
    clean = classify_null_path(_synthetic_ratings())
    dead = classify_null_path(_synthetic_ratings(null_judge=0))            # one all-null judge
    collapsed = classify_null_path(_synthetic_ratings(n_judges=2, null_judge=0))  # -> J<3 survivors
    print(f"  null-path CLEAN: survivors={clean['survivors']} refuse={clean['panel_refuse']}")
    print(f"  null-path DEAD-JUDGE: {json.dumps(dead['per_judge'][common.JUDGE_PANEL[0]])} "
          f"survivors={dead['survivors']} refuse={dead['panel_refuse']}")
    print(f"  null-path J<3: refuse={collapsed['panel_refuse']} — {collapsed['reason']}")
    print(json.dumps({"smoke": tid, "status": "blind protocol + three-way null path verified (structural)"}, indent=1))
