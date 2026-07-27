"""Re-save RewardBench WITH model identities + inspect the model set in the model-comparison subsets, so we
can build an Arena-Elo lookup for exactly those models (Elo gap = the continuous human-anchored delta)."""
import collections
import json
import os

from datasets import load_dataset

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rewardbench_models.json")
# subsets where chosen/rejected are genuine DISTINCT rated models (not adversarially constructed perturbations)
MODEL_SUBSETS = {"alpacaeval-easy", "alpacaeval-hard", "alpacaeval-length",
                 "mt-bench-easy", "mt-bench-med", "mt-bench-hard"}

ds = load_dataset("allenai/reward-bench", split="filtered")
rows = [{"prompt": r["prompt"], "chosen": r["chosen"], "rejected": r["rejected"], "subset": r["subset"],
         "chosen_model": r["chosen_model"], "rejected_model": r["rejected_model"], "id": r["id"]}
        for r in ds if r["subset"] in MODEL_SUBSETS]
json.dump(rows, open(OUT, "w"))
print(f"saved {len(rows)} model-comparison pairs -> {OUT}\n")

models = collections.Counter()
for r in rows:
    models[r["chosen_model"]] += 1
    models[r["rejected_model"]] += 1
print(f"unique models: {len(models)}")
for m, n in sorted(models.items(), key=lambda x: -x[1]):
    print(f"  {m:34s} appears {n}")

print("\nper-subset pair counts:")
for s, n in sorted(collections.Counter(r["subset"] for r in rows).items()):
    print(f"  {s:22s} {n}")
