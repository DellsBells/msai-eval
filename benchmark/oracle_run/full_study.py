"""full_study.py — THE ANALYSIS RUN (prereg 60c6525 / seal REV-LANE #013, §9).

Released by REV-LANE #015 §4 (both conditions discharged, see REV-LANE #021).
Runs the 47 ledger-PASS analysis tasks through:
  1. GENERATION  — cfg-A (qwen2.5-coder:32b, full prompt) / cfg-B (qwen2.5vl:7b,
                   level-2 degraded prompt, pinned on pilot evidence). Raw persisted.
  2. ORACLE      — hidden pytest suites, 2x replication inside oracle_score;
                   discordance => task QUARANTINED (excluded, disclosed).
  3. TIERS       — mechanical: g = rate_A - rate_B; resolve |g|>=0.5, subtle 0<|g|<0.5,
                   tie g==0. Assigned AFTER oracle, BEFORE judging.
  4. JUDGING     — alive panel (dead judges excluded-and-disclosed at probe time,
                   J<3 refuses), R=3, temp 0.6, seeded, blind (task prompt + code only,
                   opaque IDs, no oracle/tier/config labels).

Resume-safe: every judge rating appends to oracle_study_rows.jsonl immediately; on
restart, existing (task,config,judge,rep) keys are skipped. Final assembly writes
oracle_study_scores.json (frontier_api_scores.json-compatible) for the §7 analysis.

Usage: .venv/bin/python benchmark/oracle_run/full_study.py
"""
from __future__ import annotations
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common            # noqa: E402
import gen_solutions     # noqa: E402
import judge_runner      # noqa: E402
import oracle_runner     # noqa: E402

ROWS_PATH = os.path.join(HERE, "oracle_study_rows.jsonl")
MANIFEST_PATH = os.path.join(HERE, "study_manifest.json")
OUT_PATH = os.path.join(HERE, "oracle_study_scores.json")
GEN_SEED = 17025
BLIND_SALT = "oracle-study-2026-07-09"


def tier_of(g):
    return "tie" if g == 0 else ("resolve" if abs(g) >= 0.5 else "subtle")


def probe_panel():
    """Exclude judges that cannot answer a trivial call (dead instrument != crash)."""
    alive, excluded = [], {}
    for j in common.JUDGE_PANEL:
        try:
            common.ollama_chat(j, "Reply with the single digit 3.", temperature=0.0,
                               seed=1, timeout=120)
            alive.append(j)
        except Exception as e:
            excluded[j] = str(e)[:120]
    if len(alive) < common.MIN_JUDGES:
        raise SystemExit(f"prereg §8 REFUSAL: alive panel J={len(alive)} < {common.MIN_JUDGES}")
    return alive, excluded


def main():
    tasks = common.discover_tasks(split="analysis")
    tasks = [t for t in tasks
             if t["verdict"] and str(t["verdict"].get("verdict", "")).upper() == "PASS"]
    common.require_clean_ledger(tasks)          # §8 gate incl. REV-021 census
    alive, excluded = probe_panel()
    print(f"panel alive J={len(alive)}: {alive}; excluded: {list(excluded)}", flush=True)

    # ---- Phase 1+2+3: generate, oracle, tier ----
    manifest = {}
    quarantined = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            saved = json.load(f)
        manifest = saved.get("tasks", {})
        quarantined = saved.get("quarantined", {})
    for task in tasks:
        tid = task["id"]
        if tid in manifest or tid in quarantined:
            continue
        entry = {}
        discord = False
        for cfg in ("A", "B"):
            sol = os.path.join(task["dir"], "solutions", f"cfg{cfg}.py")
            if os.path.exists(sol):
                code = open(sol, encoding="utf-8").read()
            else:
                res = gen_solutions.generate(task, cfg, seed=GEN_SEED)
                gen_solutions.persist(task, cfg, res)
                code = res["code"] or ""
            sc = oracle_runner.oracle_score(task["dir"], code)
            entry[f"rate_{cfg}"] = sc["pass_rate"]
            entry[f"replication_ok_{cfg}"] = sc["replication_ok"]
            discord = discord or not sc["replication_ok"]
        if discord:
            quarantined[tid] = entry            # §2: oracle discordance => quarantine
            print(f"QUARANTINED {tid}: {entry}", flush=True)
        else:
            entry["g"] = round(entry["rate_A"] - entry["rate_B"], 4)
            entry["tier"] = tier_of(entry["g"])
            manifest[tid] = entry
            print(f"{tid}: g={entry['g']} tier={entry['tier']}", flush=True)
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump({"tasks": manifest, "quarantined": quarantined,
                       "degrade_level": gen_solutions.DEGRADE_LEVEL,
                       "gen_seed": GEN_SEED}, f, indent=1)

    spectrum = {}
    for e in manifest.values():
        spectrum[e["tier"]] = spectrum.get(e["tier"], 0) + 1
    print(f"tiers: {spectrum}; quarantined: {len(quarantined)}", flush=True)

    # ---- Phase 4: blind judging, resume-safe ----
    done = set()
    if os.path.exists(ROWS_PATH):
        with open(ROWS_PATH, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    done.add((r["task_id"], r["config"], r["judge"], r["rep"]))
                except (ValueError, KeyError):
                    continue
    by_id = {t["id"]: t for t in tasks}
    total = len(manifest) * 2 * len(alive) * common.JUDGE_R
    n = len(done)
    for judge in alive:                          # judge-outer: minimizes model swaps
        for tid in sorted(manifest):
            task = by_id[tid]
            task_prompt = open(os.path.join(task["dir"], "prompt.md"), encoding="utf-8").read()
            for cfg in ("A", "B"):
                code = open(os.path.join(task["dir"], "solutions", f"cfg{cfg}.py"),
                            encoding="utf-8").read()
                for rep in range(1, common.JUDGE_R + 1):
                    key = (tid, cfg, judge, rep)
                    if key in done:
                        continue
                    try:
                        r = judge_runner.judge_one(judge, task_prompt, code,
                                                   seed=GEN_SEED + rep)
                        score, raw = (r if isinstance(r, tuple) else
                                      (r.get("score"), r.get("raw", "")))
                    except Exception as e:       # null path: absence recorded, never coerced
                        score, raw = None, f"JUDGE_ERROR: {str(e)[:200]}"
                    if isinstance(score, tuple):
                        score, raw = score[0], score[1]
                    row = {"tier": manifest[tid]["tier"], "task_id": tid, "config": cfg,
                           "judge": judge, "rep": rep, "score": score, "raw": str(raw)[:400],
                           "blind_id": common.blind_id(tid, cfg, BLIND_SALT)}
                    with open(ROWS_PATH, "a", encoding="utf-8") as f:
                        f.write(json.dumps(row) + "\n")
                    n += 1
                    if n % 50 == 0:
                        print(f"judging {n}/{total}", flush=True)

    # ---- Assembly ----
    rows = []
    with open(ROWS_PATH, encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    out = {"meta": {"prereg_sha256": "19bdfc445742a2ca3970f82ac84350519a55ce99bf6fe10c137533381d614cd5",
                    "prereg_commit": "60c6525", "corpus_commit": "5d64dca",
                    "panel_alive": alive, "panel_excluded": excluded,
                    "judge_R": common.JUDGE_R, "judge_temp": common.JUDGE_TEMP,
                    "gen_seed": GEN_SEED, "degrade_level": gen_solutions.DEGRADE_LEVEL,
                    "tiers": spectrum, "quarantined": quarantined,
                    "blind_salt_sha256_of": "salt withheld from judges; blind ids stable"},
           "scores": rows}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    nulls = sum(1 for r in rows if r["score"] is None)
    print(json.dumps({"rows": len(rows), "null_scores": nulls,
                      "tiers": spectrum, "quarantined": list(quarantined),
                      "out": OUT_PATH}, indent=1), flush=True)


if __name__ == "__main__":
    main()
