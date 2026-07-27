"""Diagnostic for the Arm-2 'large gap still below resolution' result: dump the per-judge scores + the full
gauge decomposition, so we can tell genuine panel coarseness from a degenerate-judge / small-n artifact."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import msai_eval as msai
from elo_validation import constructed_ladder, ollama_judge

JUDGES = ["gemma4:12b", "qwen3.5:27b", "llama3.2-vision:11b"]
tier = sys.argv[1] if len(sys.argv) > 1 else "large"
pairs = constructed_ladder()[tier]

print(f"=== tier='{tier}'  judges={JUDGES} ===\n")
print(f"{'judge':22s} " + "  ".join(f"p{i}:cho/rej" for i in range(len(pairs))))
rows = []
for j in JUDGES:
    cells = []
    for pr in pairs:
        sc = ollama_judge(j, pr["prompt"], pr["chosen"])
        sr = ollama_judge(j, pr["prompt"], pr["rejected"])
        cells.append(f"{sc:.0f}/{sr:.0f}")
        rows.append({"item": "chosen", "judge": j, "score": sc})
        rows.append({"item": "rejected", "judge": j, "score": sr})
    print(f"{j:22s} " + "    ".join(cells))

print("\n--- per-judge mean (chosen - rejected) ---")
for j in JUDGES:
    cho = np.mean([r["score"] for r in rows if r["item"] == "chosen" and r["judge"] == j])
    rej = np.mean([r["score"] for r in rows if r["item"] == "rejected" and r["judge"] == j])
    print(f"  {j:22s} chosen={cho:.2f}  rejected={rej:.2f}  Δ={cho-rej:+.2f}")

print("\n--- full compare() gauge report ---")
msai.compare(rows, baseline="rejected", level="ordinal").print()
