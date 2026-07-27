"""frontier_ingest.py — reassemble the frontier chat-window scores into the gauge.

Supports MULTIPLE PASSES (independent re-measurements = repeatability):
  pass 1 -> scores_<judge>.txt      pass 2 -> scores_<judge>_p2.txt   (fresh chats, same batches)
With >=2 passes the VALIDATED gauge qualifies (unit=pair, real repeatability + reproducibility). With 1 pass it
falls back to a PROVISIONAL reproducibility-only band (gauge study without replication; repeatability
unmeasured, disclosed). Significance always comes from compare()'s own pooled bootstrap."""
import glob
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import elo_validation as ev

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontier_batches")
key = json.load(open(os.path.join(DIR, "key.json")))


def parse(path):
    out = {}
    for line in open(path):
        m = re.match(r"\s*\[?(r\d{3})\]?\s*[:=\-]\s*([1-5])\b", line)
        if m:
            out[m.group(1)] = float(m.group(2))
    return out


passes = {}   # judge -> {pass_idx: {uid: score}}
for f in sorted(glob.glob(os.path.join(DIR, "scores_*.txt"))):
    b = os.path.basename(f)[len("scores_"):-len(".txt")]
    judge, pi = (b[:-3], 2) if b.endswith("_p2") else (b, 1)
    passes.setdefault(judge, {})[pi] = parse(f)
if not passes:
    print("no scores_<judge>.txt yet in", DIR)
    raise SystemExit(0)

R = max(len(p) for p in passes.values())
print(f"judges: {sorted(passes)}   passes each: {[len(passes[j]) for j in sorted(passes)]}   => R={R}\n")

rows_by_tier = defaultdict(list)                                        # validated path: one row per uid x judge x pass
cells = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))     # provisional path: tier->pair->judge->config->[scores]
for uid, m in key.items():
    for judge, pmap in passes.items():
        for sc in pmap.values():
            if uid in sc:
                rows_by_tier[m["tier"]].append({"item": m["config"], "unit": f"{m['tier']}_{m['pair']}",
                                                "judge": judge, "score": sc[uid]})
                cells[m["tier"]][m["pair"]].setdefault(judge, {}).setdefault(m["config"], []).append(sc[uid])

roles = {"resolve": "resolve", "subtle": "below", "tie": "sham"}
print("FRONTIER PANEL — keystone verdict" + (f"  (R={R}, VALIDATED gauge)" if R >= 2 else
      "  (R=1, PROVISIONAL reproducibility-only band; repeatability unmeasured)") + ":\n")
print(f"  {'tier':8s} {'role':8s} {'Δ':>6s} {'band':>6s} {'sig':>4s} {'δ':>6s}  verdict")
for tier in ("resolve", "subtle", "tie"):
    rows = rows_by_tier.get(tier, [])
    if not rows:
        continue
    c = ev.msai.compare(rows, baseline="rejected", level="ordinal", resolution=1.0).to_dict()
    cmp, g = c["comparisons"]["chosen"], c.get("gauge", {}) or {}
    delta, sig, cd = cmp["delta"], bool(cmp.get("significant_adj")), cmp.get("cliffs_delta")
    if g.get("qualified") and g.get("guard_band") is not None:          # R>=2: the validated band
        band, basis = g["guard_band"], "validated"
        beyond = cmp.get("beyond_gauge")
    else:                                                               # R=1: provisional reproducibility band
        sd = [float(np.std([cfg["chosen"][0] - cfg["rejected"][0] for cfg in cells[tier][p].values()
                            if "chosen" in cfg and "rejected" in cfg], ddof=1))
              for p in cells[tier] if len([1 for cfg in cells[tier][p].values() if "chosen" in cfg and "rejected" in cfg]) >= 2]
        band, basis = 2.0 * float(np.sqrt(np.mean(np.square(sd)))), "provisional"
        beyond = abs(delta) > band
    verdict = ("REAL gain, BEYOND resolution" if beyond else
               "statistically real, but BELOW resolution" if sig else "within noise (indistinguishable)")
    print(f"  {tier:8s} {roles[tier]:8s} {delta:+6.2f} {band:6.2f} {'yes' if sig else 'no':>4s} {cd:+6.2f}  {verdict}  [{basis}]")
