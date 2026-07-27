"""frontier_batch.py — run a FREE cross-lineage frontier panel (Codex / Gemini / Fable chat windows) instead
of a paid API. MSAI rates each response INDEPENDENTLY, so we hand judges a SHUFFLED, BLIND flat list (no pairs,
no tiers, no 'which is better') and they rate quality 1-5. R=1: the gauge qualifies on between-judge
reproducibility (3 independent lineages), the confirmed reproducibility-only path. Batched to ~a dozen pastes.

Emits benchmark/frontier_batches/batch_*.txt (paste each into EACH judge window) + key.json (uid -> tier/pair/
config, for reassembly — the judge never sees it). Pair back with frontier_ingest.py."""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import elo_validation as ev

N = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--n=")), 10))
MAX_ITEMS = 30                       # items per batch (a frontier window handles this in one message)
CLIP_PROMPT, CLIP_ANSWER = 700, 1200  # quality is judgeable from the opening; truncation applies to both configs
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontier_batches")


def clip(s, n):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n].rstrip() + " …[truncated]"
os.makedirs(OUT, exist_ok=True)

lad = ev.keystone_ladder(n_per_tier=N, seed=0)
items = []
for t in lad:
    for pi, pair in enumerate(t["pairs"]):
        for cfg in ("chosen", "rejected"):
            items.append({"tier": t["name"], "pair": pi, "config": cfg, "prompt": pair["prompt"], "text": pair[cfg]})
random.Random(0).shuffle(items)
for i, it in enumerate(items):
    it["uid"] = f"r{i:03d}"

json.dump({it["uid"]: {"tier": it["tier"], "pair": it["pair"], "config": it["config"]} for it in items},
          open(os.path.join(OUT, "key.json"), "w"))

HEADER = ("This is a SELF-CONTAINED rating task. Disregard any prior conversation, saved memory, or "
          "personalization — judge ONLY on what is shown below, as a neutral first-time rater.\n\n"
          "You are rating the QUALITY of answers to prompts, each on a 1-5 INTEGER scale (5=excellent, "
          "1=poor). Rate each item INDEPENDENTLY on its own merits — do NOT compare items to each other. "
          "When done, output ONLY lines of the form `ID: score`, one per item, and nothing else.\n\n")
FOOTER = "\n\nNow output one `ID: score` line per item above (score = integer 1-5). Output nothing else.\n"

batches, cur = [], []
for it in items:
    block = f"[{it['uid']}]\nPROMPT: {clip(it['prompt'], CLIP_PROMPT)}\nANSWER: {clip(it['text'], CLIP_ANSWER)}\n\n"
    if len(cur) >= MAX_ITEMS:
        batches.append(cur)
        cur = []
    cur.append(block)
if cur:
    batches.append(cur)

for bi, b in enumerate(batches, 1):
    open(os.path.join(OUT, f"batch_{bi}.txt"), "w").write(HEADER + "".join(b) + FOOTER)

print(f"{len(items)} responses (n={N}/tier) -> {len(batches)} batches -> {OUT}/batch_*.txt")
print(f"WORKFLOW: paste each of the {len(batches)} batches into EACH judge window (Codex, Gemini, Fable).")
print(f"  => {len(batches)} batches x 3 judges = {len(batches) * 3} paste-and-relay cycles, one sitting, $0.")
print(f"Relay each judge's full 'ID: score' list back; frontier_ingest.py reassembles + runs the gauge.")
