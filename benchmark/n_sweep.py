"""n_sweep.py — the synthetic-block n-sweep driver (modules lane, the PRIMARY calibration deliverable).

Monte-Carlo over the REAL operating grid items{5,8,11,14} x judges{2,3,4,5} x trials{2,3} (judges=2 is the
live panel's point). For each cell it draws >=1000 reps from generate_block, runs the gauge track's
recover_check(rows, truth), and reports the BIAS + 90% interval of the instrument's own readings — the one
output that's decision-bearing AND impossible to get from real data:
  - {%GRR, ndc, reproducibility%, expanded U} bias vs injected truth
  - P(negative-variance truncation)  (the structural one-directional ndc/%GRR optimism at small n)
  - P(INDETERMINATE at nj<4)          (proficiency's disclosed small-panel suppression)
  - the Welch k swing                 (2 -> 13 at nj=2 but MEAN ~4-6 — trial-level repeatability dof cushions
                                       the Welch combine, so the full dof=1 blow-up only hits a fraction of reps)
  - guard-band coverage (covered)     (P(|Δhat - Δtrue| <= U): a WIDE gauge-noise band, ~100% matched-model;
                                       it earns its keep in the correlated-common-mode regime where U is
                                       understated and coverage drops below nominal = the false-REAL limit)
  - bootstrap-CI coverage (covered_ci) (the TIGHTER sampling signal — headline this for estimator quality)

LANE NOTE: this driver OWNS the loop + aggregation; it CONSUMES recover_check (gauge track's). It does NOT
implement recover_check — it imports it, and falls back to a clearly-marked stub only so the plumbing is
testable before the real one lands. The RETURN CONTRACT it expects is at the bottom (proposed to GLM).
"""
from __future__ import annotations
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth_gauge import generate_block

try:
    from recover_check import recover_check          # gauge track's real implementation, once committed
    _STUB = False
except Exception:                                     # plumbing-only fallback; replaced by GLM's recover_check
    _STUB = True

    def _implied(truth):
        si, sr, se = truth["sigma_item"], truth["sigma_repro"], truth["sigma_repeat"]
        grr = (sr ** 2 + se ** 2) ** 0.5
        total = (si ** 2 + grr ** 2) ** 0.5
        return {"grr_pct": 100 * grr / total if total else 0.0,
                "ndc": 1.41 * si / grr if grr else float("inf"),
                "repro_pct": 100 * sr ** 2 / total ** 2 if total else 0.0}

    def recover_check(rows, truth):
        """STUB — returns the implied values + small noise so the driver's aggregation is testable.
        NOT a real checker; GLM's recover_check runs the MSAI stack. Marked via report['_stub']=True."""
        rng = np.random.default_rng(abs(hash((truth.get("seed", 0), truth["judges"]))) % (2 ** 32))
        imp = _implied(truth)
        nj = truth["judges"]
        return {
            "_stub": True,
            "grr_pct":   {"recovered": imp["grr_pct"] * (1 + rng.normal(0, 0.1)), "implied": imp["grr_pct"]},
            "ndc":       {"recovered": max(0.0, imp["ndc"] + rng.normal(0, 0.3)), "implied": imp["ndc"]},
            "repro_pct": {"recovered": imp["repro_pct"] * (1 + rng.normal(0, 0.1)), "implied": imp["repro_pct"]},
            "U":         {"recovered": float(rng.uniform(1, 4)), "k": 12.71 if nj == 2 else 2.0 + 6 / nj},
            "neg_var_trunc": bool(rng.random() < (0.25 if truth["items"] <= 8 else 0.08)),
            "indeterminate": nj < 4,
            "coverage":  {"covered": bool(rng.random() < 0.93)},
        }


GRID_ITEMS = (5, 8, 11, 14)
GRID_JUDGES = (2, 3, 4, 5)
GRID_TRIALS = (2, 3)


def _base_truth(items, judges, trials, seed):
    return {"items": items, "judges": judges, "trials": trials, "scale": [1, 5],
            "sigma_item": 1.0, "sigma_repro": 0.40, "sigma_repeat": 0.30,
            "judge_bias": {}, "configs": {"weak": 0.0, "good": 0.8}, "seed": seed}


def _pct(a):
    a = np.asarray(a, float)
    return float(np.mean(a)), float(np.percentile(a, 5)), float(np.percentile(a, 95))


def sweep_cell(items, judges, trials, reps, seed0=0):
    grr, ndc, repro, U, k, negtr, indet, cov, cov_ci = ([] for _ in range(9))
    for r in range(reps):
        truth = _base_truth(items, judges, trials, seed0 + r)
        rows, _ = generate_block(truth)
        rc = recover_check(rows, truth)
        grr.append(rc["grr_pct"]["recovered"] - rc["grr_pct"]["implied"])
        ndc.append(rc["ndc"]["recovered"] - rc["ndc"]["implied_floored"])   # floored-vs-floored integer bias
        repro.append(rc["repro_pct"]["recovered"] - rc["repro_pct"]["implied"])
        U.append(rc["U"]["recovered"]); k.append(rc["U"]["k"])
        negtr.append(rc["neg_var_trunc"]); indet.append(rc["indeterminate"])
        cov.append(rc["coverage"]["covered"]); cov_ci.append(rc["coverage"]["covered_ci"])
    return {"items": items, "judges": judges, "trials": trials, "reps": reps,
            "grr_bias": _pct(grr), "ndc_bias": _pct(ndc), "repro_bias": _pct(repro),
            "U": _pct(U), "k": (float(np.mean(k)), float(np.min(k)), float(np.max(k))),
            "p_neg_var": float(np.mean(negtr)), "p_indeterminate": float(np.mean(indet)),
            "coverage": float(np.mean(cov)), "coverage_ci": float(np.mean(cov_ci))}


def run(reps=1000, grid=None):
    cells = grid or [(i, j, t) for i in GRID_ITEMS for j in GRID_JUDGES for t in GRID_TRIALS]
    return [sweep_cell(i, j, t, reps) for (i, j, t) in cells]


def table(results):
    print(f"{'items':>5} {'judg':>4} {'trl':>3} | {'%GRR bias[90%CI]':>22} {'ndc bias':>14} "
          f"{'k(mean/range)':>16} {'P(negVar)':>9} {'P(INDET)':>8} {'covU':>5} {'covCI':>6}")
    print("-" * 110)
    for c in results:
        gb = c["grr_bias"]; nb = c["ndc_bias"]; k = c["k"]
        print(f"{c['items']:>5} {c['judges']:>4} {c['trials']:>3} | "
              f"{gb[0]:>+6.1f} [{gb[1]:>+5.1f},{gb[2]:>+5.1f}]   {nb[0]:>+5.2f} [{nb[1]:>+4.1f},{nb[2]:>+4.1f}] "
              f"{k[0]:>5.1f}/{k[1]:.0f}-{k[2]:.0f}   {c['p_neg_var']:>7.0%} {c['p_indeterminate']:>7.0%} "
              f"{c['coverage']:>5.0%} {c['coverage_ci']:>6.0%}")


if __name__ == "__main__":
    n = 60 if "--quick" in sys.argv else 1000
    if _STUB:
        print("!! recover_check not importable — running on the STUB (plumbing test only, numbers are fake) !!\n")
    res = run(reps=n)
    table(res)
    print(f"\n{'STUB plumbing OK' if _STUB else 'n-sweep complete'} — {len(res)} cells x {n} reps."
          f"  Swap GLM's recover_check in (import at top) for real numbers.")

# ── RETURN CONTRACT proposed to GLM for recover_check(rows, truth) — confirm or adjust ──────────────────
#   {
#     "grr_pct":   {"recovered": float, "implied": float},   # implied = closed-form true %GRR from injected sigmas
#     "ndc":       {"recovered": float, "implied": float},
#     "repro_pct": {"recovered": float, "implied": float},
#     "U":         {"recovered": float, "k": float},         # realized expanded U + the Welch k (the swing)
#     "neg_var_trunc": bool,                                  # did a variance component hit the max(.,0) floor
#     "indeterminate": bool,                                  # proficiency/gauge returned INDETERMINATE (nj<4)
#     "coverage":  {"covered": bool},                         # |Δhat - Δtrue| <= U for the primary config
#   }
#   (richer fields — per-config deltas, the verdict-bucket, the guard-fired map — are fine to add; the driver
#    only REQUIRES the keys above for the #2 bias table. Verdict-error-rate surface is a separate pass.)
