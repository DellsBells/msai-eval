"""fetch_rewardbench.py — pull RewardBench (allenai/reward-bench) and inspect its structure so we can map
subsets -> difficulty tiers for the Elo-validation ladder. Saves a compact local copy for the harness."""
import collections
import json
import os
import sys

from datasets import load_dataset

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rewardbench_filtered.json")

print("loading allenai/reward-bench ...", flush=True)
dd = load_dataset("allenai/reward-bench")
print("splits:", list(dd.keys()), flush=True)
split = "filtered" if "filtered" in dd else list(dd.keys())[0]
ds = dd[split]
print(f"using split='{split}'  rows={len(ds)}  cols={ds.column_names}", flush=True)

if "subset" in ds.column_names:
    subs = collections.Counter(ds["subset"])
    print("\nsubsets (n):", flush=True)
    for k, v in sorted(subs.items(), key=lambda x: -x[1]):
        print(f"  {k:28s} {v}", flush=True)

print("\nsample row (truncated):", flush=True)
r0 = ds[0]
for k in ds.column_names:
    print(f"  {k:14s} {str(r0[k])[:140]!r}", flush=True)

# save a compact copy (prompt/chosen/rejected/subset only, if present)
keep = [c for c in ("prompt", "chosen", "rejected", "subset", "id") if c in ds.column_names]
rows = [{k: ex[k] for k in keep} for ex in ds]
json.dump(rows, open(OUT, "w"))
print(f"\nsaved {len(rows)} rows ({keep}) -> {OUT}  ({os.path.getsize(OUT)//1024} KB)", flush=True)
