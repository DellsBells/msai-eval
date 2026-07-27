"""regime_sweep.py — the misspecification-regime pass + verdict-error surface (modules lane).

The matched-model n-sweep is the SMOKE baseline (recover everything, ~100% coverage). The real calibration
result lives HERE, where the estimator's assumptions are VIOLATED and the pass condition is a FIRED GUARD or
a coverage NUMBER, not a recovered value:
  - common_mode(config) : config-correlated shared bias -> understated U -> FALSE REAL. Pass-as-LIMIT: the
                          guard-band coverage (covU) DROPS below nominal = the documented trust limit.
  - ordinal_flip        : mean-vs-rank sign disagreement -> compare must WITHHOLD direction.
  - heavy_tail (t3)     : heavy-tailed repeatability -> robust methods should stay near the clean coverage.
  - biased_judge        : one judge offset -> proficiency must flag it (at nj>=4).
Plus a VERDICT-ERROR surface: Δtrue swept across the boundary, P(verdict matches the oracle).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_gauge import generate_block
from recover_check import recover_check

REPS = 300


def base(seed, **kw):
    t = {"items": 14, "judges": 4, "trials": 3, "scale": [1, 5],
         "sigma_item": 1.0, "sigma_repro": 0.40, "sigma_repeat": 0.30,
         "judge_bias": {}, "configs": {"weak": 0.0, "good": 0.0}, "seed": seed}
    t.update(kw)
    return t


def run(truth_fn, reps=REPS, seed0=0):
    return [recover_check(generate_block(truth_fn(seed0 + r))[0], truth_fn(seed0 + r)) for r in range(reps)]


def rate(rcs, fn):
    v = [fn(rc) for rc in rcs if fn(rc) is not None]
    return float(np.mean(v)) if v else float("nan")


def bucket(verdict):
    s = verdict.lower()
    if "disagree" in s or "not trustworthy" in s:
        return "WITHHOLD"
    if "within noise" in s:
        return "within-noise"
    if "below gauge resolution" in s:
        return "below-res"
    if "real" in s:
        return "REAL"
    return "other"


# ── regimes ─────────────────────────────────────────────────────────────────────────────────────────
matched = run(lambda s: base(s))
common_mode = run(lambda s: base(s, common_mode={"corr_with": "config", "sd": 1.0}))
ordinal_flip = run(lambda s: {"items": 24, "judges": 4, "trials": 3, "scale": [1, 50],
                              "sigma_item": 0.3, "sigma_repro": 0.3, "sigma_repeat": 0.3, "judge_bias": {},
                              "configs": {"weak": 0.0, "good": 0.0}, "level": "ordinal",
                              "mean_rank_flip": {"config": "good", "frac": 0.15, "out_shift": 8, "bulk_shift": -1.0},
                              "seed": s})
heavy_tail = run(lambda s: base(s, repeat_dist="t3"))
biased = run(lambda s: base(s, judge_bias={0: 1.5}))

print(f"=== MISSPECIFICATION REGIMES ({REPS} reps, cell items=14 judges=4 trials=3 unless noted) ===\n")
print(f"{'regime':16s} {'covU':>6} {'covCI':>6} {'withhold':>9} {'oracle_ok':>10}  verdict mix")
print("-" * 88)
for name, rcs in [("matched (Δ=0)", matched), ("common_mode/cfg", common_mode),
                  ("ordinal_flip", ordinal_flip), ("heavy_tail t3", heavy_tail), ("biased_judge", biased)]:
    cu = rate(rcs, lambda r: r["coverage"]["covered"])
    cc = rate(rcs, lambda r: r["coverage"]["covered_ci"])
    wh = rate(rcs, lambda r: r["guards"]["withhold_fired"])
    ok = rate(rcs, lambda r: r["verdict"]["oracle_ok"])
    mix = {}
    for r in rcs:
        b = bucket(r["verdict"]["actual"]); mix[b] = mix.get(b, 0) + 1
    mixs = " ".join(f"{k}:{100*v//len(rcs)}%" for k, v in sorted(mix.items(), key=lambda x: -x[1]))
    print(f"{name:16s} {cu:>6.0%} {cc:>6.0%} {wh:>9.0%} {ok:>10.0%}  {mixs}")

print("\nKEY READS:")
print(f"  common_mode/cfg: guard-band coverage {rate(common_mode, lambda r: r['coverage']['covered']):.0%} "
      f"(matched {rate(matched, lambda r: r['coverage']['covered']):.0%}) — a DROP here is the documented")
print("    false-REAL trust limit (shared bias inflates Δ but not U). Verify it's < nominal.")
print(f"  ordinal_flip:    WITHHOLD fired {rate(ordinal_flip, lambda r: r['guards']['withhold_fired']):.0%} of reps.")
print(f"  biased_judge:    proficiency recovered the injected bias "
      f"{rate(biased, lambda r: r['proficiency']['bias_recovered']):.0%} (nj=4, OUTLIER via LOO).")

# ── verdict-error surface: Δtrue swept across the boundary ───────────────────────────────────────────
print("\n=== VERDICT-ERROR SURFACE (Δtrue swept; does compare's bucket match the oracle?) ===")
print(f"{'Δtrue':>7} {'oracle_ok':>10}  verdict mix (actual)")
print("-" * 60)
for dt in (0.0, 0.3, 0.6, 1.0, 1.6, 2.4):
    rcs = run(lambda s: base(s, configs={"weak": 0.0, "good": dt}), reps=200)
    ok = rate(rcs, lambda r: r["verdict"]["oracle_ok"])
    mix = {}
    for r in rcs:
        b = bucket(r["verdict"]["actual"]); mix[b] = mix.get(b, 0) + 1
    mixs = " ".join(f"{k}:{100*v//len(rcs)}%" for k, v in sorted(mix.items(), key=lambda x: -x[1]))
    print(f"{dt:>7.1f} {ok:>10.0%}  {mixs}")
print("\n(oracle_ok = compare's verdict matches the oracle's expected bucket for the REALIZED Δ,U,cd,qualified.)")
