"""frontier_api_analyze.py — re-analyze the saved frontier scores WITHOUT re-spending.
Reads frontier_api_scores.json, prints the full compare()/gauge diagnostics per tier plus a
per-judge chosen/rejected breakdown, so we understand exactly why each verdict lands where it does."""
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elo_validation as ev

data = json.load(open(os.path.join(HERE, "frontier_api_scores.json")))
print("meta:", json.dumps(data["meta"], indent=1), "\n")

scores = [s for s in data["scores"] if s["score"] is not None]
by_tier = defaultdict(list)
for s in scores:
    by_tier[s["tier"]].append(s)

for tier in ("resolve", "subtle", "tie"):
    rows = [{"item": s["config"], "unit": f"{tier}_{s['pair']}", "judge": s["judge"], "score": s["score"]}
            for s in by_tier[tier]]
    c = ev.msai.compare(rows, baseline="rejected", level="ordinal", resolution=1.0).to_dict()
    cmp = c["comparisons"]["chosen"]
    g = c.get("gauge", {}) or {}
    print("=" * 78)
    print(f"TIER: {tier}   (n_rows={len(rows)})")
    print("  comparison keys:", ", ".join(cmp.keys()))
    for k in ("delta", "significant_adj", "beyond_gauge", "cliffs_delta", "ci_low", "ci_high",
              "verdict", "resolution", "guard_band"):
        if k in cmp:
            print(f"    {k:16s} = {cmp[k]}")
    print("  gauge:", json.dumps(g, indent=1, default=str))

    # per-judge chosen/rejected means + within-judge repeat SD (repeatability)
    print("  per-judge (mean chosen | mean rejected | Δ | repeat-SD):")
    pj = defaultdict(lambda: defaultdict(list))
    for s in by_tier[tier]:
        pj[s["judge"]][s["config"]].append(s["score"])
    for j in sorted(pj):
        ch, rj = pj[j].get("chosen", []), pj[j].get("rejected", [])
        # repeat SD = mean over pairs of the SD across the R repeats within each (pair,config) cell
        cellsd = []
        cells = defaultdict(list)
        for s in by_tier[tier]:
            if s["judge"] == j:
                cells[(s["pair"], s["config"])].append(s["score"])
        for v in cells.values():
            if len(v) >= 2:
                cellsd.append(np.std(v, ddof=1))
        rsd = float(np.mean(cellsd)) if cellsd else float("nan")
        print(f"    {j:8s}  {np.mean(ch):.2f}  |  {np.mean(rj):.2f}  |  {np.mean(ch)-np.mean(rj):+.2f}  |  {rsd:.2f}")
    print()
