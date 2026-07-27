"""frontier_reanalyze.py — re-score BOTH frontier runs under the four-state resolution verdict.
Zero spend: reads persisted scores only.
  - API run  (R=3, 4 judges): benchmark/frontier_api_scores.json
  - Chat run (R=2, 3 judges): benchmark/frontier_batches/scores_*.txt (+ _p2), key.json
Prints, per tier: Δ, U with its CI [U_lo,U_hi], effective dof, P(|Δ|>U), and the four-state verdict.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elo_validation as ev
from resolution_verdict import four_state

TIERS = ("resolve", "subtle", "tie")
ROLE = {"resolve": "big-gap", "subtle": "small-gap", "tie": "sham"}


def rows_api():
    d = json.load(open(os.path.join(HERE, "frontier_api_scores.json")))
    by = defaultdict(list)
    for s in d["scores"]:
        if s["score"] is not None:
            by[s["tier"]].append({"item": s["config"], "unit": f"{s['tier']}_{s['pair']}",
                                  "judge": s["judge"], "score": s["score"]})
    return by, d["meta"].get("judges", {})


def rows_chat():
    DIR = os.path.join(HERE, "frontier_batches")
    key = json.load(open(os.path.join(DIR, "key.json")))
    by = defaultdict(list)
    judges = set()
    for f in sorted(glob.glob(os.path.join(DIR, "scores_*.txt"))):
        b = os.path.basename(f)[len("scores_"):-len(".txt")]
        judge = b[:-3] if b.endswith("_p2") else b
        judges.add(judge)
        for line in open(f):
            m = re.match(r"\s*\[?(r\d{3})\]?\s*[:=\-]\s*([1-5])\b", line)
            if m and m.group(1) in key:
                k = key[m.group(1)]
                by[k["tier"]].append({"item": k["config"], "unit": f"{k['tier']}_{k['pair']}",
                                      "judge": judge, "score": float(m.group(2))})
    return by, sorted(judges)


def report(title, by_tier, judges):
    print("\n" + "=" * 96)
    print(f"{title}   judges={judges if isinstance(judges, list) else list(judges)}")
    print("=" * 96)
    print(f"  {'tier':8s} {'role':9s} {'Δ':>6s} {'U':>6s} | "
          f"{'WS νeff':>7s} {'P(Δ>U)':>7s} {'verdict[WS]':>12s} | "
          f"{'dom dof':>7s} {'P(Δ>U)':>7s} {'verdict[dom]':>12s}")
    for tier in TIERS:
        rows = by_tier.get(tier, [])
        if not rows:
            continue
        c = ev.msai.compare(rows, baseline="rejected", level="ordinal", resolution=1.0).to_dict()
        cmp = c["comparisons"]["chosen"]
        g = (c.get("gauge") or {})
        rb = g.get("resolution_budget")
        delta = cmp["delta"]
        sig = bool(cmp.get("significant_adj"))
        ci = cmp.get("ci")
        if not (g.get("qualified") and rb):
            print(f"  {tier:8s} {ROLE[tier]:9s} {delta:+6.2f}   ---   gauge unqualified (no balanced replicates)")
            continue
        ws = four_state(delta, ci, rb, sig, dof_mode="ws")
        dm = four_state(delta, ci, rb, sig, dof_mode="dominant")
        print(f"  {tier:8s} {ROLE[tier]:9s} {delta:+6.2f} {ws['U']:6.2f} | "
              f"{ws['nu_eff']:7.1f} {ws['p_beyond']:7.2f} {ws['state']:>12s} | "
              f"{dm['nu_eff']:7.1f} {dm['p_beyond']:7.2f} {dm['state']:>12s}")


api_by, api_judges = rows_api()
report("API RUN  (R=3, 4 lineages)", api_by, api_judges)
chat_by, chat_judges = rows_chat()
report("CHAT RUN (R=2, 3 lineages)", chat_by, chat_judges)
print("\nverdicts: WITHIN-NOISE | BELOW (real, under band) | AT-EDGE (inside band's own CI) | RESOLVED (above band)\n")
