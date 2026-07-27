"""fetch_arena.py — pull LMSYS Chatbot Arena battles and inspect what SUBTLE-BUT-REAL gap material exists.
The keystone tier needs decisive (non-tie) battles between close models — a small-but-real per-pair gap — not
50/50 ties (which are shams). Inspect winner distribution, turns, and model-pair closeness vs our Elo table."""
import collections
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arena_battles.json")
ELO = {k: v for k, v in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
       "arena_elo.json"))).items() if not k.startswith("_")}

try:
    from datasets import load_dataset
    ds = load_dataset("lmsys/chatbot_arena_conversations", split="train")
except Exception as e:
    print(f"LOAD FAILED (likely gated — needs HF terms acceptance): {type(e).__name__}: {str(e)[:300]}")
    raise SystemExit(0)

print(f"rows={len(ds)}  cols={ds.column_names}\n")
print("winner distribution:")
for k, v in collections.Counter(ds["winner"]).items():
    print(f"  {k:18s} {v}")
if "turn" in ds.column_names:
    print("\nturn distribution:", dict(collections.Counter(ds["turn"]).most_common(6)))

# decisive single-turn battles between BOTH-rated models, bucketed by |Elo gap|
decisive = 0
gap_bucket = collections.Counter()
keep = []
for r in ds:
    if r["winner"] not in ("model_a", "model_b"):
        continue
    if r.get("turn", 1) != 1:
        continue
    ma, mb = r["model_a"], r["model_b"]
    if ma not in ELO or mb not in ELO:
        continue
    decisive += 1
    gap = abs(ELO[ma] - ELO[mb])
    b = "tie-ish(<30)" if gap < 30 else "subtle(30-90)" if gap < 90 else "clear(>=90)"
    gap_bucket[b] += 1
    keep.append({"model_a": ma, "model_b": mb, "winner": r["winner"], "elo_gap": gap,
                 "conversation_a": r["conversation_a"], "conversation_b": r["conversation_b"]})

print(f"\ndecisive single-turn battles w/ both models Elo-rated: {decisive}")
print("by |Elo gap| bucket:", dict(gap_bucket))
json.dump(keep, open(OUT, "w"))
print(f"saved {len(keep)} battles -> {OUT}  ({os.path.getsize(OUT)//1024} KB)")
