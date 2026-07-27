"""recover_check.py — gauge-track half of the synthetic gauge-block: does MSAI RECOVER injected truth?

Consumed by n_sweep.py (`from recover_check import recover_check`). Runs the MSAI stack on a generate_block
sample and returns the frozen RETURN CONTRACT plus richer fields. Neither lane writes the other's half:
modules owns generate_block + the n-sweep driver; this is the gauge track's checker + the verdict oracle.

"implied" = the closed-form true metric from the injected sigmas, matched to EACH estimator's estimand.
The generative model (synth_gauge) injects NO item×judge interaction, so true sigma2_int = 0, hence:
  grr_pct  (variance.py msi, SD-scale)            = 100*sqrt(se^2+sr^2) / sqrt(se^2+sr^2+si^2)   [no resolution]
  ndc      (variance.py, reported value is FLOORED)= 1.41*si / sqrt(se^2+sr^2)  (implied left UN-floored,
                                                     matching the driver's continuous estimand)
  repro_pct(reproducibility share of TOTAL var)    = 100*sr^2 / (si^2+sr^2+se^2)
Only the EXPANDED U carries the resolution term (delta/sqrt12); %GRR/ndc/repro_pct do not.

Gauge components are estimated on ONE config's crossed item×judge×trial design (components are config-
invariant in the model; pooling configs would leak the delta into within-cell variance). compare() runs on
configs-as-treatments. The verdict is checked against verdict_oracle.expected_verdict — the frozen contract.
"""
from __future__ import annotations
import math
import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "src"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msai_eval as msai
from msai_eval.data import normalize
from msai_eval.variance import variance_components
from synth_gauge import reliability_rows, compare_rows
from verdict_oracle import expected_verdict


def _split_configs(configs):
    """baseline = config with delta nearest 0; primary = the largest-|delta| treatment."""
    base = min(configs, key=lambda c: abs(configs[c]))
    others = [c for c in configs if c != base] or [base]
    primary = max(others, key=lambda c: abs(configs[c]))
    return base, primary


def _proficiency_state(rel, level):
    """Returns (explicit_indeterminate, flagged_outliers, verdict_counts). Defensive — proficiency may
    not run on edge designs. NOTE: proficiency's INDETERMINATE branch (panel<4, no reference) is PREEMPTED
    per-judge by an OUTLIER/QUESTIONABLE call, so at nj=2 genuinely-spread judges read as mutual OUTLIERs
    and explicit-INDETERMINATE stays False even though the panel is too small to TRUST any verdict. The
    caller folds in the categorical nj<4 limit so the reported `indeterminate` reflects the disclosed
    small-panel suppression, not just the preempted branch."""
    from collections import Counter
    try:
        rep = msai.proficiency(rel, level=("ordinal" if level == "ordinal" else "interval"))
        verds = [d.get("verdict", "") for d in rep.by_judge.values()]
        counts = dict(Counter(v.split(" —")[0].split(" -")[0].strip() or "?" for v in verds))
        explicit = any(v.startswith("INDETERMINATE") for v in verds)
        flagged = sorted((j for j, d in rep.by_judge.items() if "OUTLIER" in d.get("verdict", "")), key=str)
        return explicit, flagged, counts
    except Exception as e:
        return True, [], {"error": str(e)[:40]}     # if proficiency can't run at all, treat as indeterminate


def recover_check(rows, truth):
    si = float(truth["sigma_item"]); sr = float(truth["sigma_repro"]); se = float(truth["sigma_repeat"])
    level = truth.get("level", "interval")
    resolution = 1.0 if level == "ordinal" else 0.0            # the TRUE quantization (ordinal=integer grid)
    configs = truth["configs"]
    base, primary = _split_configs(configs)
    delta_true = float(configs[primary]) - float(configs[base])   # compare() estimates the BASELINE-RELATIVE diff

    # ---- gauge: variance components on ONE config's crossed design (config-invariant components) ----
    rel = reliability_rows(rows, base)
    var = variance_components(normalize(rel))
    if var:
        grr_rec = float(var["msi_grr_pct"])
        ndc_rec = float(var["ndc"])
        tv = var["sigma2_item"] + var["sigma2_judge"] + var["sigma2_interaction"] + var["sigma2_repeat"]
        repro_rec = 100.0 * var["sigma2_judge"] / tv if tv > 0 else float("nan")
        neg_trunc = any("negative_variance_truncated" in f for f in var.get("flags", []))
        frozen = bool(var.get("deterministic"))
    else:
        grr_rec = ndc_rec = repro_rec = float("nan")
        neg_trunc = False
        frozen = True

    # implied closed-forms (true sigma2_int = 0)
    denom_tv = se * se + sr * sr + si * si
    grr_imp = 100.0 * math.sqrt(se * se + sr * sr) / math.sqrt(denom_tv) if denom_tv > 0 else 0.0
    ndc_imp = 1.41 * si / math.sqrt(se * se + sr * sr) if (se * se + sr * sr) > 0 else float("inf")
    repro_imp = 100.0 * sr * sr / denom_tv if denom_tv > 0 else 0.0

    # ---- expanded uncertainty U + Welch k (same config view, true quantization) ----
    ub = msai.uncertainty_budget(rel, level=("ordinal" if level == "ordinal" else "interval"),
                                 resolution=resolution)
    U_rec, k_rec = float(ub.U), float(ub.k)
    res_auto = any("resolution_auto_inferred" in w for w in ub.warnings)

    # ---- compare: delta + three-way verdict + guard band (configs as treatments) ----
    cmp = msai.compare(compare_rows(rows), baseline=base, level=level, resolution=resolution).to_dict()
    gauge = cmp["gauge"]
    c = cmp["comparisons"].get(primary, {})
    delta_hat = float(c.get("delta", float("nan")))
    qualified = bool(gauge.get("qualified"))
    guard_band = gauge.get("guard_band")
    verdict = c.get("verdict", "")

    # verdict-oracle check (frozen contract): does compare()'s real verdict match the intended semantics?
    exp_verdict = expected_verdict(qualified, delta_hat, bool(c.get("significant_adj")),
                                   c.get("cliffs_delta"), c.get("beyond_gauge"), level)
    bucket_ok = bool(verdict == exp_verdict)
    withhold_fired = "DISAGREE in sign" in verdict

    # guard-band coverage: is the TRUE delta within one band of the estimate? (uses the verdict-driving band;
    # falls back to the budget U when the gauge is unqualified so the field is always defined.)
    U_eff = float(guard_band) if (qualified and guard_band) else U_rec
    covered = bool(not math.isnan(delta_hat) and abs(delta_hat - delta_true) <= U_eff)
    # guard-band coverage (above) is a gauge-noise-scale band per the contract; covered_ci is the tighter
    # SAMPLING coverage (true diff inside compare's bootstrap CI) — reported alongside as the richer signal.
    ci = c.get("ci") or (float("nan"), float("nan"))
    covered_ci = bool(all(not math.isnan(x) for x in ci) and ci[0] <= delta_true <= ci[1])

    # ---- proficiency: small-panel INDETERMINATE (nj<4) + biased-judge recovery (richer) ----
    nj = int(truth["judges"])
    injected_bias = sorted((truth.get("judge_bias") or {}).keys(), key=str)
    explicit_indet, flagged, prof_counts = _proficiency_state(rel, level)
    # synthetic block passes NO reference, so a panel of <4 judges cannot certify competence (disclosed
    # limit, proficiency.py:277-279). Report that categorically OR an explicit INDETERMINATE verdict.
    indeterminate = (nj < 4) or explicit_indet
    bias_recovered = (sorted(map(str, flagged)) == sorted(map(str, injected_bias))) if injected_bias else None

    return {
        # ---- frozen contract (required by the n-sweep bias table) ----
        "grr_pct":   {"recovered": grr_rec, "implied": grr_imp},
        # ndc.implied is the CONTINUOUS true value; recovered is FLOORED (so recovered-implied carries a
        # deterministic -frac(ndc) offset). implied_floored is provided for a clean floored-vs-floored bias.
        "ndc":       {"recovered": ndc_rec, "implied": ndc_imp,
                      "implied_floored": (float(math.floor(ndc_imp)) if math.isfinite(ndc_imp) else ndc_imp)},
        "repro_pct": {"recovered": repro_rec, "implied": repro_imp},
        "U":         {"recovered": U_rec, "k": k_rec},
        "neg_var_trunc": bool(neg_trunc),
        "indeterminate": bool(indeterminate),
        "coverage":  {"covered": covered, "covered_ci": covered_ci},
        # ---- richer fields (welcome per the contract; for the verdict-error surface + guard map) ----
        "delta":     {"hat": delta_hat, "true": delta_true, "U_eff": U_eff,
                      "config": primary, "baseline": base},
        "verdict":   {"actual": verdict, "expected": exp_verdict, "oracle_ok": bucket_ok},
        "guards":    {"withhold_fired": withhold_fired, "frozen": frozen, "neg_var_trunc": bool(neg_trunc),
                      "resolution_auto_inferred": res_auto, "qualified": qualified},
        "proficiency": {"injected_bias": injected_bias, "flagged_outlier": flagged,
                        "bias_recovered": bias_recovered, "explicit_indeterminate": explicit_indet,
                        "panel_too_small": nj < 4, "verdict_counts": prof_counts,
                        "reference_unfit_rejected": False},   # no reference in the synthetic block -> never fires
    }


if __name__ == "__main__":
    # Self-checks: (1) matched-model CLEAN LIMIT (wide scale, large n) -> recovered ~ implied (recovery is
    # correct, not a recovered-vs-recovered tautology); (2) a small-n cell -> contract keys present + typed.
    from synth_gauge import generate_block
    print("=" * 78 + "\n  RECOVER_CHECK self-test\n" + "=" * 78)

    clean = {"items": 300, "judges": 60, "trials": 10, "scale": [-1000, 1000],
             "sigma_item": 1.00, "sigma_repro": 0.40, "sigma_repeat": 0.30,
             "judge_bias": {}, "configs": {"weak": 0.0, "good": 0.8}, "seed": 7, "level": "interval"}
    rc = recover_check(*generate_block(clean))
    print("\n CLEAN-LIMIT (large n, wide scale) — recovered must ~= implied:")
    for key in ("grr_pct", "ndc", "repro_pct"):
        r, i = rc[key]["recovered"], rc[key]["implied"]
        print(f"   {key:10s} recovered={r:8.3f}  implied={i:8.3f}  abs_err={abs(r-i):6.3f}")
    print(f"   U={rc['U']['recovered']:.3f} k={rc['U']['k']:.2f}  delta hat={rc['delta']['hat']:.3f} "
          f"true={rc['delta']['true']:.3f} covered={rc['coverage']['covered']}  verdict_oracle_ok={rc['verdict']['oracle_ok']}")

    small = {"items": 5, "judges": 2, "trials": 2, "scale": [1, 5],
             "sigma_item": 1.00, "sigma_repro": 0.40, "sigma_repeat": 0.30,
             "judge_bias": {}, "configs": {"weak": 0.0, "good": 0.8}, "seed": 1, "level": "interval"}
    rs = recover_check(*generate_block(small))
    need = ["grr_pct", "ndc", "repro_pct", "U", "neg_var_trunc", "indeterminate", "coverage"]
    ok = all(kk in rs for kk in need)
    print(f"\n SMALL-n (5x2x2, the live operating point): contract keys present = {ok}")
    print(f"   U={rs['U']['recovered']:.2f} k={rs['U']['k']:.2f} (small Welch nu_eff -> k inflated)  "
          f"indeterminate={rs['indeterminate']} (nj=2<4)  neg_var_trunc={rs['neg_var_trunc']}  "
          f"coverage={rs['coverage']['covered']}")
