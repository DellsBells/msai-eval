"""Claim-tracking ledger — MSAI's discipline turned on MSAI's own code.

Every verdict / flag / headline number the instrument emits is a CLAIM. A claim may ship only if a
synthetic test injects known truth and proves the claim either (a) TRACKS that truth within a stated bound,
or (b) fires a DISCLOSURE when it can't. This file is the permanent gate: a passing test = resolved + locked
forever; an xfail = a documented, known overclaim still open. Resolving a finding = remove its xfail and make
it pass. A future change that re-breaks a claim fails CI.

LEDGER (from the module-overclaim audit, adversarially verified):
  variance:
    - ndc had no sampling-band caveat (where %GRR does)            RESOLVED   (test_ndc_carries_sampling_caveat)
    - %GRR>30 reason blamed gauge noise, could be item clustering  RESOLVED   (test_grr_over_30_discloses_item_selection)
    - frozen gauge on a CONTINUOUS grid reads FULLY ACCEPTABLE     RESOLVED   (test_frozen_continuous_gauge_detected)
  compare (gauge-track lane):
    - guard band inflated by item-pooling -> real wins under-resolve RESOLVED (test_compare_resolves_clean_gauge_real_delta, f9aa72b)
    - 'REAL and resolved' unreachable for sub-1.5pt deltas          RESOLVED (same fix — unit-level gauge decomposition)
    - frozen-gauge detection flips with a multi-item suite          RESOLVED (unit routing + V1's 1e-6 floor compose; f9aa72b+a8a4fac)
    - ordinal MAGNITUDE gate was interval-only (negligible rank->REAL) RESOLVED (test_ordinal_resolution_requires_rank_concurrence)
    - guard band carried common-mode judge LEVEL -> delta band inflated RESOLVED (test_compare_delta_band_drops_common_mode_judge_level)
  uncertainty (gauge-track lane):
    - U swings ~14x on identical truth at small panels, no band     RESOLVED  (test_uncertainty_small_panel_U_unstable)
    - dominant-lever flips to wrong source ~19% at 2 judges         RESOLVED  (same disclosure)
    - u_ref collapsed to a mean masks heterogeneous reference unc.  RESOLVED  (test_uncertainty_discloses_heterogeneous_u_ref)
  reference:
    - loose/single-item ref + biased judge -> TRACEABLY CONFORMANT  RESOLVED  (test_loose_reference_not_conformant)
    - tight ref + perfect judge -> false INDISTINGUISHABLE (clustered) RESOLVED (test_tight_reference_perfect_judge_not_indistinguishable)
    - MOSTLY CONFORMANT with one catastrophic miss                  RESOLVED  (test_conformant_rate_discloses_large_miss)
    - flag_if_consensus false-positives on independent close refs   RESOLVED  (test_consensus_flag_discloses_provenance_ambiguity)
    - combine_references inverse-variance shrink (shared-bias)       RESOLVED  (test_combine_references_discloses_shrink)
  stability:
    - DRIFT gate ~11% false alarm + weak power; caveat mis-aimed    RESOLVED  (test_stability_drift_discloses_false_alarm_rate)
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmark"))
import msai_eval as msai
from msai_eval.variance import gauge_judgement


def _gj(pct_grr, ndc, grr_sd=0.1, deterministic=False):
    return gauge_judgement({"msi_grr_pct": pct_grr, "ndc": ndc, "grr_sd": grr_sd, "deterministic": deterministic})


# ── RESOLVED — locked ────────────────────────────────────────────────────────────────────────────────
def test_ndc_carries_sampling_caveat():
    """ndc must disclose its sampling band (it swings ~1-13 on identical truth), like %GRR."""
    near = _gj(pct_grr=8.0, ndc=5)          # ndc at the >=5 cutoff -> band straddles it
    assert near["ndc_caveat"] is not None and "sampling band" in near["ndc_caveat"]
    assert near["ndc_ambiguous"] is True
    far = _gj(pct_grr=8.0, ndc=20)          # ndc far above the cutoff -> band does not straddle
    assert far["ndc_ambiguous"] is False
    assert far["ndc_caveat"] is not None    # still disclosed


def test_grr_over_30_discloses_item_selection():
    """%GRR>30 must NOT assert 'gauge noise too large' as the sole cause — item clustering inflates %GRR too."""
    v = _gj(pct_grr=40.0, ndc=6, grr_sd=0.05)
    assert v["verdict"] == "NOT ACCEPTABLE"
    assert v.get("likely_item_selection_possible") is True
    assert "cluster" in v["reason"].lower() or "item" in v["reason"].lower()


def test_uncertainty_small_panel_U_unstable():
    """U1/U2: at <5 judges, U is an unstable point estimate and the dominant-lever can flip — the budget must
    disclose it (and stay quiet on an adequate panel)."""
    from synth_gauge import generate_block, reliability_rows
    small = {"items": 8, "judges": 2, "trials": 3, "scale": [1, 5], "sigma_item": 1.0,
             "sigma_repro": 0.4, "sigma_repeat": 0.3, "judge_bias": {}, "configs": {"x": 0.0}, "seed": 0}
    w = msai.uncertainty_budget(reliability_rows(generate_block(small)[0], "x"), level="interval").warnings
    assert any("small_panel_U_unstable" in x for x in w)
    big = msai.uncertainty_budget(reliability_rows(generate_block(dict(small, judges=6))[0], "x"), level="interval").warnings
    assert not any("small_panel_U_unstable" in x for x in big)


# ── OPEN — documented overclaims (xfail until resolved; remove the marker when fixed) ─────────────────
def test_frozen_continuous_gauge_detected():
    """V1/V2 (RESOLVED): a genuinely frozen gauge (zero gauge noise) on a CONTINUOUS scale must read frozen,
    raise the frozen_gauge flag, and NOT emit the reassuring 'does NOT disqualify' repeatability text."""
    from synth_gauge import generate_block, reliability_rows
    t = {"items": 12, "judges": 4, "trials": 3, "scale": [1, 5], "sigma_item": 1.0,
         "sigma_repro": 0.0, "sigma_repeat": 0.0, "judge_bias": {}, "configs": {"x": 0.0}, "seed": 0}
    d = msai.reliability(reliability_rows(generate_block(t)[0], "x"), level="interval").to_dict()
    assert "frozen" in d["gauge_judgement"]["verdict"].lower()
    flags = d.get("flags") or []
    assert any("frozen_gauge" in f for f in flags)              # V2: the frozen flag, not the reassuring one
    assert not any("does NOT disqualify" in f for f in flags)


def test_compare_resolves_clean_gauge_real_delta():
    """A clean gauge (true noise ~0.05) with a real full-point config win must read RESOLVED, not below-resolution."""
    from synth_gauge import generate_block, compare_rows
    t = {"items": 8, "judges": 4, "trials": 3, "scale": [1, 5], "sigma_item": 0.8,
         "sigma_repro": 0.05, "sigma_repeat": 0.05, "judge_bias": {}, "configs": {"base": 0.0, "treat": 1.0}, "seed": 1}
    g = msai.compare(compare_rows(generate_block(t)[0]), baseline="base", level="interval").to_dict()["comparisons"]["treat"]
    assert g.get("beyond_gauge") is True


def test_compare_delta_band_drops_common_mode_judge_level():
    """Level-shift finding (keystone panel, RESOLVED): the guard band must NOT carry the judge MAIN effect
    (each appraiser's overall scale LEVEL). The same judge rates config AND baseline, so the level is
    common-mode in the within-judge delta and cancels EXACTLY (identical algebra to u_ref). Inject a HUGE
    pure judge-level spread (sigma_repro=6) with a real Δ_true=2 on a wide unclipped scale: if the band still
    carried the level it would be ~k·6≈15 and the real Δ=2 would read 'below resolution'; with the level
    dropped the band is gap-disagreement-only (~0.3 SD) and the true Δ correctly RESOLVES. The centering is
    disclosed (Guard C) and recorded in the budget (Guard #3 auditability)."""
    from synth_gauge import generate_block, compare_rows
    t = {"items": 12, "judges": 5, "trials": 4, "scale": [-1000, 1000],   # wide scale -> no clipping
         "sigma_item": 1.0, "sigma_repro": 6.0,                           # HUGE per-judge LEVEL spread
         "sigma_repeat": 0.3, "judge_bias": {}, "configs": {"base": 0.0, "cand": 2.0}, "seed": 3}
    rep = msai.compare(compare_rows(generate_block(t)[0]), baseline="base", level="interval", resolution=0.5)
    rb = rep.gauge["resolution_budget"]
    assert rb["grr_sd_delta"] < 0.25 * rb["grr_sd_full"]                  # the injected level is dropped...
    assert any("delta_band_level_centered" in w for w in rep.gauge["warnings"])         # ...disclosed (Guard C)
    assert any("level_centered_for_delta" in w for w in rb["warnings"])                 # ...recorded (Guard #3)
    cand = rep.comparisons["cand"]
    assert cand["beyond_gauge"] is True and "REAL" in cand["verdict"]     # real Δ resolves on the delta band
    assert rep.gauge["guard_band"] < 2.0                                  # band would be ~15 if level were carried


def test_loose_reference_not_conformant():
    """R1 (RESOLVED): a loose single-item reference + a badly-biased judge must NOT read unqualified TRACEABLY
    CONFORMANT — resolving power is unverifiable there, so it must disclose that."""
    from msai_eval.reference import certified_reference, score
    out = score(certified_reference({"x": 1.0}, u=100.0), {"x": 200.0})   # U_ref=200, judge biased by 199
    assert "UNVERIFIED" in out["verdict"]                                 # not a silent "TRACEABLY CONFORMANT"
    assert any("fitness_unverified" in w for w in out["warnings"])


def test_tight_reference_perfect_judge_not_indistinguishable():
    """R2 (RESOLVED): a tight reference + a PERFECT judge must NOT read INDISTINGUISHABLE just because the item
    truths cluster — a perfect judge has no deviation for the reference to fail to resolve."""
    from msai_eval.reference import certified_reference, score
    out = score(certified_reference({"a": 2.9, "b": 3.0, "c": 3.1}, u=0.05), {"a": 2.9, "b": 3.0, "c": 3.1})
    assert "INDISTINGUISHABLE" not in out["verdict"] and "CONFORMANT" in out["verdict"]


def test_conformant_rate_discloses_large_miss():
    """R3 (RESOLVED): a high conformance RATE hiding one catastrophic per-item miss must disclose the miss."""
    from msai_eval.reference import certified_reference, score
    ref = certified_reference({"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0, "e": 5.0}, u=0.1)
    out = score(ref, {"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0, "e": 105.0})   # 4 perfect, 1 catastrophic
    assert any("large_miss_masked" in w for w in out["warnings"])


def test_consensus_flag_discloses_provenance_ambiguity():
    """R4 (RESOLVED): the consensus firewall must disclose it's a values heuristic — independent agreement
    trips it too — rather than asserting circularity as proven."""
    from msai_eval.reference import certified_reference, flag_if_consensus
    ref = certified_reference({"a": 1.0, "b": 2.0, "c": 3.0}, u=0.1)
    assert flag_if_consensus(ref, {"a": 1.0, "b": 2.0, "c": 3.0}) is True
    assert any("provenance" in w.lower() for w in ref.warnings)


def test_combine_references_discloses_shrink():
    """R5 (RESOLVED): combining agreeing sources shrinks u_ref below each source — must disclose that the
    shrink assumes independence (a shared bias isn't reduced)."""
    from msai_eval.reference import certified_reference, combine_references
    out = combine_references([certified_reference({"a": 1.0, "b": 2.0}, u=0.1),
                              certified_reference({"a": 1.0, "b": 2.0}, u=0.1)])
    assert out.u["a"] < 0.1
    assert any("shrank" in w.lower() for w in out.warnings)


def test_uncertainty_discloses_heterogeneous_u_ref():
    """U3 (RESOLVED): a reference whose per-item u_ref varies widely must disclose it — the flat-mean budget
    understates the loose items."""
    from msai_eval.reference import certified_reference
    from synth_gauge import generate_block, reliability_rows
    ref = certified_reference({f"i{j}": 1.0 for j in range(8)},
                              u={**{f"i{j}": 0.01 for j in range(6)}, "i6": 5.0, "i7": 5.0})
    rows = reliability_rows(generate_block({"items": 8, "judges": 4, "trials": 3, "scale": [1, 5],
        "sigma_item": 1.0, "sigma_repro": 0.4, "sigma_repeat": 0.3, "judge_bias": {}, "configs": {"x": 0.0},
        "seed": 0})[0], "x")
    w = msai.uncertainty_budget(rows, level="interval", reference=ref).warnings
    assert any("HETEROGENEOUS" in x for x in w)


def test_stability_drift_discloses_false_alarm_rate():
    """S1/S2/S3 (RESOLVED): a DRIFT verdict (SPC rules, non-frozen baseline) must disclose the gate's ~10%
    false-alarm rate so a single flag and its re-adjudicate anchor aren't over-trusted."""
    rep = msai.stability([0.80, 0.83, 0.78, 0.81, 0.79, 0.82, 0.77, 0.80, 0.60, 0.61, 0.59, 0.60], baseline=8)
    assert rep.in_control is False
    assert any("drift_false_alarm_rate" in w for w in rep.warnings)


def test_ordinal_resolution_requires_rank_concurrence():
    """Cross-lineage review gap (RESOLVED): the |Δ|>guard_band MAGNITUDE gate is interval-only. On ordinal data
    a Δ that clears the interval band but has a NEGLIGIBLE rank effect (|Cliff's δ|<0.147) must downgrade to
    unresolved-on-rank (the resolution may be an interval-spacing artifact); a non-negligible rank effect keeps
    REAL; interval data ignores the rank (the mean is the right tool there)."""
    from msai_eval.compare import _verdict
    g = {"qualified": True}; base = {"delta": 0.8, "significant_adj": True, "beyond_gauge": True}
    neg = _verdict({**base, "cliffs_delta": 0.05}, g, "ordinal")        # negligible rank -> downgrade
    assert "NEGLIGIBLE" in neg and "REAL" not in neg
    assert "REAL gain" in _verdict({**base, "cliffs_delta": 0.5}, g, "ordinal")   # strong rank concurs -> REAL
    assert "REAL gain" in _verdict({**base, "cliffs_delta": 0.05}, g, "interval") # interval ignores the rank
