"""live_smoke.py — the single-task LIVE smoke released by REV-LANE #015 §4.

Order of the greenlight cascade: THIS (gen+oracle+judge on ONE ledger-PASS task) →
pilot-split degradation tuning (§3) → full study (§9). Runs entirely on local models ($0).
Gate: §8 smoke clause — the chosen task must be individually ledger-PASS.

Usage: .venv/bin/python benchmark/oracle_run/live_smoke.py [task_id]   (default t05)
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


def main():
    tid = sys.argv[1] if len(sys.argv) > 1 else "t05"
    tasks = {t["id"]: t for t in common.discover_tasks(split=None, include_pilot=True)}
    common.require_clean_ledger(list(tasks.values()), allow_smoke_on=[tid])
    task = tasks[tid]
    task_prompt = open(os.path.join(task["dir"], "prompt.md"), encoding="utf-8").read()
    out = {"task": tid, "gen": {}, "oracle": {}, "judge": {}}

    out["excluded_judges"] = {}
    for cfg in ("A", "B"):
        sol_path = os.path.join(task["dir"], "solutions", f"cfg{cfg}.py")
        if os.path.exists(sol_path):  # idempotent: reuse persisted generation, never re-spend
            code = open(sol_path, encoding="utf-8").read()
            out["gen"][cfg] = {"model": "(persisted)", "code_chars": len(code)}
        else:
            res = gen_solutions.generate(task, cfg, seed=17025)
            gen_solutions.persist(task, cfg, res)
            code = res["code"] or ""
            out["gen"][cfg] = {"model": res["model"], "code_chars": len(code)}
        sc = oracle_runner.oracle_score(task["dir"], code)
        out["oracle"][cfg] = {"pass_rate": sc["pass_rate"], "all_pass": sc["all_pass"],
                              "replication_ok": sc["replication_ok"]}
        ratings = {}
        for j in common.JUDGE_PANEL:
            try:
                r = judge_runner.judge_one(j, task_prompt, code, seed=17025)
                ratings[j] = r.get("score") if isinstance(r, dict) else r
            except Exception as e:  # §5/§8 null path: a dead judge is EXCLUDED-DISCLOSED, never a crash
                ratings[j] = None
                out["excluded_judges"][j] = str(e)[:120]
        out["judge"][cfg] = ratings
    alive = [j for j in common.JUDGE_PANEL if j not in out["excluded_judges"]]
    out["panel_J"] = len(alive)
    if len(alive) < common.MIN_JUDGES:
        raise SystemExit(f"prereg §8 REFUSAL: panel J={len(alive)} < {common.MIN_JUDGES}")

    g = out["oracle"]["A"]["pass_rate"] - out["oracle"]["B"]["pass_rate"]
    out["oracle_gap_g"] = round(g, 3)
    print(json.dumps(out, indent=1))
    with open(os.path.join(HERE, f"live_smoke_{tid}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
