"""fetch_mtbench.py — build the keystone ladder from MT-Bench HUMAN judgments (ungated). Multiple humans vote
per (question, model-pair), giving a per-pair preference MARGIN = the direct, human-anchored subtle-gap measure
GLM specified. Emits a 3-tier ladder anchored on human margin (turn-1, >=3 votes):
  tie (<58%)      -> a PROPER sham (real different responses humans split on; true gap ~= 0)
  subtle (58-79%) -> the KEYSTONE (real but small gap -> should read 'real but BELOW resolution')
  decisive (>=80%)-> resolve control (clear gap)"""
import ast
import collections
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mtbench_ladder_pairs.json")
from datasets import load_dataset

ds = load_dataset("lmsys/mt_bench_human_judgments")["human"]


def conv(c):
    return ast.literal_eval(c) if isinstance(c, str) else c


def turn1(c):
    """(prompt, first assistant response) for turn 1."""
    m = conv(c)
    return m[0]["content"], m[1]["content"]


# aggregate human votes per (question_id, turn-1, unordered pair)
agg = collections.defaultdict(lambda: collections.Counter())
rowof = {}
for r in ds:
    if str(r.get("turn")) != "1":
        continue
    ma, mb, w = r["model_a"], r["model_b"], r["winner"]
    key = (r["question_id"], frozenset((ma, mb)))
    if w in ("model_a", "model_b"):
        agg[key][ma if w == "model_a" else mb] += 1
    elif w and "tie" in w:
        agg[key]["__tie__"] += 1
    rowof.setdefault(key, r)

ladder = {"tie": [], "subtle": [], "decisive": []}
for key, votes in agg.items():
    total = sum(votes.values())
    if total < 3:
        continue
    nontie = {m: c for m, c in votes.items() if m != "__tie__"}
    if not nontie:
        continue
    win = max(nontie, key=nontie.get)
    margin = nontie[win] / total
    tier = "tie" if margin < 0.58 else "subtle" if margin < 0.80 else "decisive"
    r = rowof[key]
    win_is_a = (r["model_a"] == win)
    try:
        prompt, w_resp = turn1(r["conversation_a"] if win_is_a else r["conversation_b"])
        _, l_resp = turn1(r["conversation_b"] if win_is_a else r["conversation_a"])
    except Exception:
        continue
    loser = [m for m in key[1] if m != win][0]
    ladder[tier].append({"prompt": prompt, "chosen": w_resp, "rejected": l_resp,
                         "margin": round(margin, 2), "n_votes": total,
                         "winner_model": win, "loser_model": loser})

for t in ladder:
    ms = [p["margin"] for p in ladder[t]]
    print(f"  {t:9s}: {len(ladder[t]):3d} pairs  margin range "
          f"{min(ms):.2f}-{max(ms):.2f}" if ms else f"  {t:9s}: 0 pairs")
json.dump(ladder, open(OUT, "w"))
print(f"\nsaved -> {OUT}  ({os.path.getsize(OUT)//1024} KB)")
print("\nsample SUBTLE (keystone) pair:")
s = ladder["subtle"][0]
print(f"  {s['winner_model']} > {s['loser_model']}  margin={s['margin']} ({s['n_votes']} votes)")
print(f"  PROMPT:   {s['prompt'][:120]}")
print(f"  CHOSEN:   {s['chosen'][:120]}")
print(f"  REJECTED: {s['rejected'][:120]}")
