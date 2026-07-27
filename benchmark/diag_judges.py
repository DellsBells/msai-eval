"""Per-judge diagnostic for the keystone panel (GLM's decision tree): is the inflated repro_sd an OUTLIER
judge (drop it) or uniform disagreement (band is legit, need a bigger-magnitude resolve tier)? Scores the
decisive MT-Bench tier with all 5 judges and prints each judge's chosen/rejected means + delta."""
import collections
import sys

import numpy as np

sys.path.insert(0, "benchmark")
import elo_validation as ev

JUDGES = ["gemma4:12b", "gemma4:31b-mlx", "qwen3.5:27b", "qwen3.6:35b-mlx", "qwen2.5-coder:32b"]
dec = [t for t in ev.mtbench_ladder(n_per_tier=6, seed=0) if t["name"] == "decisive"][0]
rows, diag = ev.score_panel(dec["pairs"], JUDGES, ev.ollama_judge, R=1)
print(f"dead={diag['dead']}  degenerate={diag['degenerate']}  partial={diag['partial']}\n")

by = collections.defaultdict(lambda: {"chosen": [], "rejected": []})
for r in rows:
    by[r["judge"]][r["item"]].append(r["score"])
print(f"{'judge':22s}  chosen  reject   delta   |overall mean|")
deltas = {}
for j in JUDGES:
    c, rj = by[j]["chosen"], by[j]["rejected"]
    if not c or not rj:
        print(f"{j:22s}  (no scores)")
        continue
    d = np.mean(c) - np.mean(rj)
    deltas[j] = d
    print(f"{j:22s}  {np.mean(c):.2f}    {np.mean(rj):.2f}    {d:+.2f}    {np.mean(c + rj):.2f}")

if deltas:
    md = np.median(list(deltas.values()))
    print(f"\nmedian per-judge delta = {md:+.2f}")
    print("per-judge deviation from median (outlier = large):")
    for j, d in sorted(deltas.items(), key=lambda x: -abs(x[1] - md)):
        print(f"  {j:22s} {d - md:+.2f}")
