"""pilot_tune.py — §3 degradation tuning, PILOT SPLIT ONLY (8 tasks, excluded from analysis).

Runs both generator configs on every pilot task, oracles the results (2x replication),
and prints the oracle gap spectrum g = passrate_A - passrate_B with the mechanical tier
each task would land in (resolve |g|>=0.5 / subtle 0<|g|<0.5 / tie g==0). The operator
pins cfg-B's degradation on THIS evidence only; analysis tasks are never touched here
(prereg 60c6525 §3 — the tuning that happens on the tournament arena voids the tournament).

Usage: .venv/bin/python benchmark/oracle_run/pilot_tune.py
"""
from __future__ import annotations
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common            # noqa: E402
import gen_solutions     # noqa: E402
import oracle_runner     # noqa: E402


def tier_of(g):
    if g == 0:
        return "tie"
    return "resolve" if abs(g) >= 0.5 else "subtle"


def main():
    pilot = common.discover_tasks(split="pilot", include_pilot=True)
    common.require_clean_ledger(pilot)  # all-PASS pilot census; REV-021 gate applies
    results = []
    for task in pilot:
        row = {"task": task["id"]}
        rates = {}
        for cfg in ("A", "B"):
            sol = os.path.join(task["dir"], "solutions", f"cfg{cfg}.py")
            if os.path.exists(sol):
                code = open(sol, encoding="utf-8").read()
            else:
                res = gen_solutions.generate(task, cfg, seed=17025)
                gen_solutions.persist(task, cfg, res)
                code = res["code"] or ""
            sc = oracle_runner.oracle_score(task["dir"], code)
            rates[cfg] = sc["pass_rate"]
            row[f"rate_{cfg}"] = round(sc["pass_rate"], 3)
            row[f"replication_ok_{cfg}"] = sc["replication_ok"]
        row["g"] = round(rates["A"] - rates["B"], 3)
        row["tier"] = tier_of(row["g"])
        results.append(row)
        print(json.dumps(row))
    spectrum = {}
    for r in results:
        spectrum[r["tier"]] = spectrum.get(r["tier"], 0) + 1
    out = {"degradation": "harness-default (title + signature + 'infer behavior')",
           "rows": results, "spectrum": spectrum,
           "note": "pin or adjust cfg-B degradation on THIS evidence only; then freeze."}
    with open(os.path.join(HERE, "pilot_tune_results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"spectrum": spectrum}, indent=1))


if __name__ == "__main__":
    main()
