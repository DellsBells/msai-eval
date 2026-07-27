"""Tests for compare() — the config-vs-baseline acceptance test.

These check that the HONESTY GUARDS fire, not just that a number comes out:
a real drop is flagged beyond the gauge, a within-noise config is NOT flagged,
a frozen (temperature-0) gauge is refused, a clustered all-good gauge still
qualifies (ndc must not gate), Holm only inflates p-values, and nominal data is
rejected (you can't rank categories better/worse).
"""
import numpy as np
import pytest
import msai_eval as msai
from msai_eval.compare import _cliffs_delta, _within_judge_cliffs_delta, _holm, _verdict


def _make_data(seed=0):
    # well-separated configs + modest gauge noise -> qualified gauge (ndc >= 4)
    rng = np.random.default_rng(seed)
    quality = {"fp16": 4.9, "q4": 4.0, "q2": 2.0, "delta_kv": 4.9, "dither_2bit": 3.6}  # delta_kv == fp16 (within noise — no resolvable difference)
    judges = ["A", "B", "C", "D", "E"]
    jbias = {"A": -0.15, "B": 0.1, "C": 0.0, "D": 0.12, "E": -0.05}
    data = []
    for cfg, q in quality.items():
        for jg in judges:
            for _ in range(5):  # 5 trials/cell -> balanced replicates (gauge measurable)
                s = q + jbias[jg] + rng.normal(0, 0.2)
                data.append({"item": cfg, "judge": jg, "score": float(np.clip(round(s), 1, 5))})
    return data


def test_real_drop_flagged_beyond_gauge():
    rep = msai.compare(_make_data(), baseline="fp16", level="ordinal")
    q2 = rep.comparisons["q2"]
    assert q2["delta"] < 0
    assert q2["beyond_gauge"] is True
    assert "REAL" in q2["verdict"]
    assert q2["cliffs_delta"] < -0.3          # rank-based effect agrees it's a real drop


def test_within_noise_config_not_flagged():
    rep = msai.compare(_make_data(), baseline="fp16", level="ordinal")
    dk = rep.comparisons["delta_kv"]
    assert "REAL" not in dk["verdict"]         # identical-quality config must NOT read as a real drop
    assert abs(dk["delta"]) < rep.gauge["guard_band"]


def test_gauge_is_qualified_and_exposed():
    rep = msai.compare(_make_data(), baseline="fp16", level="ordinal")
    assert rep.gauge["grr_sd"] is not None and rep.gauge["grr_sd"] > 0
    assert rep.gauge["guard_band"] is not None
    assert rep.gauge["ndc"] is not None
    assert rep.gauge["qualified"] is True


def test_frozen_gauge_refused():
    # temperature 0: identical score every trial -> degenerate repeatability
    data = []
    for cfg, q in {"fp16": 5, "q2": 3}.items():
        for jg in ["A", "B", "C"]:
            for _ in range(3):
                data.append({"item": cfg, "judge": jg, "score": q})
    rep = msai.compare(data, baseline="fp16", level="ordinal")
    assert rep.gauge["qualified"] is False
    assert any("frozen" in w for w in rep.gauge["warnings"])
    assert "provisional" in rep.comparisons["q2"]["verdict"]   # won't hand back a confident delta


def test_holm_only_inflates():
    rep = msai.compare(_make_data(), baseline="fp16", level="ordinal")
    for c in rep.comparisons.values():
        assert c["p_holm"] >= c["p_raw"] - 1e-9


def test_nominal_rejected():
    data = [{"item": "a", "judge": "j", "score": 1}, {"item": "b", "judge": "j", "score": 2}]
    with pytest.raises(ValueError, match="nominal"):
        msai.compare(data, baseline="a", level="nominal")


def test_baseline_must_exist():
    with pytest.raises(ValueError, match="baseline"):
        msai.compare(_make_data(), baseline="not_a_config", level="ordinal")


def test_no_replicates_unknown_resolution():
    # single trial per cell -> no gauge-noise estimate -> beyond_gauge must be None, stated honestly
    data = []
    for cfg, q in {"fp16": 5, "q2": 3, "q4": 4}.items():
        for jg in ["A", "B", "C", "D"]:
            data.append({"item": cfg, "judge": jg, "score": q})
    rep = msai.compare(data, baseline="fp16", level="ordinal")
    assert rep.gauge["guard_band"] is None
    assert rep.comparisons["q2"]["beyond_gauge"] is None
    assert any("guard band" in n for n in rep.gauge["warnings"]) or \
           any("guard band" in n for n in rep.notes)


def test_verdict_withholds_direction_when_mean_and_cliffs_disagree():
    # On ordinal data the verdict must NOT assert a directional drop/gain that the rank-based
    # effect (Cliff's δ, which the notes tell you to trust) contradicts in sign.
    gauge = {"qualified": True}
    disagree = {"delta": -0.2, "significant_adj": True, "beyond_gauge": True, "cliffs_delta": +0.25}
    v = _verdict(disagree, gauge, "ordinal")
    assert "DISAGREE" in v and "drop" not in v and "gain" not in v
    # signs agree -> the normal directional verdict stands
    agree = {"delta": -0.2, "significant_adj": True, "beyond_gauge": True, "cliffs_delta": -0.25}
    assert "REAL drop" in _verdict(agree, gauge, "ordinal")
    # within-noise makes no directional claim -> sign disagreement is harmless
    noise = {"delta": -0.2, "significant_adj": False, "beyond_gauge": False, "cliffs_delta": +0.25}
    assert "within noise" in _verdict(noise, gauge, "ordinal")
    # interval level: the mean IS the right tool, so no Cliff's-δ guard applies
    interval = {"delta": -0.2, "significant_adj": True, "beyond_gauge": True, "cliffs_delta": float("nan")}
    assert "REAL drop" in _verdict(interval, gauge, "interval")
    # MAGNITUDE guard (cross-lineage review): on ordinal data a NEGLIGIBLE rank effect (|δ|<0.147) downgrades
    # an interval-band 'resolved' to unresolved-on-rank — the resolution may be an interval-spacing artifact.
    tiny = {"delta": -0.2, "significant_adj": True, "beyond_gauge": True, "cliffs_delta": +0.05}
    v_tiny = _verdict(tiny, gauge, "ordinal")
    assert "NEGLIGIBLE" in v_tiny and "unresolved on the rank scale" in v_tiny and "REAL" not in v_tiny
    # on INTERVAL the mean IS the right tool -> the tiny rank effect is ignored and REAL stands
    assert "REAL drop" in _verdict(tiny, gauge, "interval")


def test_underpowered_delta_not_labeled_within_noise():
    # REV-002: a NON-significant Δ that EXCEEDS the guard band is UNDER-POWERED, not "within noise"
    # (the notes promise 'within noise' == BELOW the guard band). It must not claim sub-resolution.
    gauge = {"qualified": True}
    underpowered = {"delta": 2.5, "significant_adj": False, "beyond_gauge": True, "cliffs_delta": 0.3}
    v = _verdict(underpowered, gauge, "ordinal")
    assert "within noise" not in v and ("under-powered" in v or "exceeds the guard band" in v)
    # the genuine within-noise case (below the band, not significant) is unchanged
    below = {"delta": 0.2, "significant_adj": False, "beyond_gauge": False, "cliffs_delta": 0.05}
    assert "within noise" in _verdict(below, gauge, "ordinal")


def test_guard_band_is_expanded_U_floored():
    # The guard band adopts the GUM expanded uncertainty U for a DELTA measurand, floored at
    # guard_k·grr_sd_delta (Guard B). Both the U and the floor are computed on the DELTA basis: the
    # judge MAIN effect (appraiser scale level) is common-mode in a config-vs-baseline difference and
    # cancels (same as u_ref), so it is dropped from reproducibility, leaving the judge×item interaction
    # (the genuine gap-disagreement). U folds in the quantization floor + Welch-Satterthwaite k.
    from msai_eval import uncertainty_budget
    from msai_eval.variance import variance_components
    from msai_eval.data import normalize
    data = _make_data()
    rep = msai.compare(data, baseline="fp16", level="ordinal")
    vc = variance_components(normalize(data))
    grr_delta = (vc["sigma2_repeat"] + vc["sigma2_interaction"]) ** 0.5
    U_delta = uncertainty_budget(data, level="ordinal", measurand="delta").U
    assert abs(rep.gauge["guard_band"] - max(U_delta, 2 * grr_delta)) < 1e-9
    # the delta band drops the common-mode judge LEVEL -> it can only be TIGHTER than (or equal to)
    # the absolute-noise band, never wider. This is the band-inflation fix.
    U_abs = uncertainty_budget(data, level="ordinal").U          # default measurand="absolute"
    assert rep.gauge["guard_band"] <= max(U_abs, 2 * vc["grr_sd"]) + 1e-9
    assert rep.gauge["resolution_budget"]["grr_sd_delta"] <= rep.gauge["grr_sd"] + 1e-12
    assert rep.gauge["resolution_budget"]["dominant"] is not None    # drill-down lever is exposed


def test_delta_band_drops_common_mode_judge_level():
    # Level-shift finding (keystone panel): judges AGREE on the config delta but rate on very different
    # absolute LEVELS. That level is common-mode in a within-judge config-vs-baseline delta and cancels
    # EXACTLY (same algebra as u_ref) -> it must NOT inflate the delta guard band. The contrast that
    # matters: a real ~1.0 gap is BELOW an absolute-noise band (which carries the huge level spread) but
    # ABOVE the delta band (which carries only gap-disagreement) -> centering recovers a true resolution.
    rng = np.random.default_rng(7)
    jlevel = {"A": -1.5, "B": -0.7, "C": 0.0, "D": 0.8, "E": 1.6}    # ~3-point spread in absolute level
    data = []
    for cfg, q in {"base": 3.0, "cand": 4.0}.items():               # a genuine ~1.0 gap, judges agree on it
        for jg, lv in jlevel.items():
            for _ in range(6):
                data.append({"item": cfg, "judge": jg, "score": float(q + lv + rng.normal(0, 0.15))})
    rep = msai.compare(data, baseline="base", level="interval", resolution=0.25)
    rb = rep.gauge["resolution_budget"]
    # the level was removed from the delta band: grr_sd_delta is far below the full appraiser noise...
    assert rb["grr_sd_delta"] < 0.5 * rb["grr_sd_full"]
    # ...and the disclosure fires (Guard C) + the budget records the centering (Guard #3 auditability)
    assert any("delta_band_level_centered" in w for w in rep.gauge["warnings"])
    assert any("level_centered_for_delta" in w for w in rb["warnings"])
    # the real 1.0 gap would be BELOW the inflated absolute-noise band, but RESOLVES on the delta band
    from msai_eval import uncertainty_budget
    U_abs = uncertainty_budget(data, level="interval", resolution=0.25).U
    abs_band = max(U_abs, 2 * rb["grr_sd_full"])
    assert 1.0 < abs_band                                            # absolute band would NOT resolve it
    assert rep.gauge["guard_band"] < abs_band                       # delta band is materially tighter
    cand = rep.comparisons["cand"]
    assert cand["beyond_gauge"] is True and "REAL" in cand["verdict"]  # ...so the true gap is correctly resolved


def test_within_judge_cliffs_delta_cancels_level_shift():
    # REV-010 (verified-then-fixed): a panel where EVERY judge unanimously prefers config over baseline
    # (chosen = rejected + 1 on that judge's own scale), but the judges sit at very different absolute
    # levels. Within each judge the effect is a clean +1.0. Pooling across judges (the old bug) lets a
    # high-rating judge's baseline out-rank a low-rating judge's config, diluting the effect size below
    # the truth. The paired form must recover +1.0; the pooled form must not.
    levels = {"A": 3, "B": 1, "C": 0}          # judge absolute-level offsets (a 3-point spread)
    cells_cfg = [np.array([levels[j] + 1.0], dtype=float) for j in ("A", "B", "C")]  # chosen = rejected+1
    cells_base = [np.array([levels[j] + 0.0], dtype=float) for j in ("A", "B", "C")]
    paired = _within_judge_cliffs_delta(cells_cfg, cells_base)
    pooled = _cliffs_delta(np.concatenate(cells_cfg), np.concatenate(cells_base))
    assert paired == 1.0                        # unanimous within-judge preference, correctly recovered
    assert pooled < 1.0                          # the old pooled form is diluted by the level spread
    assert round(pooled, 3) == 0.444             # exact witnessed dilution (documents the bug magnitude)
    # degenerate check: with all judges at the SAME level, paired == pooled (no cross-judge contamination)
    flat_cfg = [np.array([4.0]), np.array([4.0]), np.array([4.0])]
    flat_base = [np.array([3.0]), np.array([3.0]), np.array([3.0])]
    assert _within_judge_cliffs_delta(flat_cfg, flat_base) == 1.0
    assert _cliffs_delta(np.concatenate(flat_cfg), np.concatenate(flat_base)) == 1.0
    # empty-on-one-side judges are skipped, not counted as nan-poison
    with_gap = [np.array([4.0]), np.array([]), np.array([4.0])]
    base_gap = [np.array([3.0]), np.array([3.0]), np.array([3.0])]
    assert _within_judge_cliffs_delta(with_gap, base_gap) == 1.0
    # no overlapping judge -> nan (nothing comparable), never a silent 0
    import math
    assert math.isnan(_within_judge_cliffs_delta([np.array([]), np.array([])],
                                                 [np.array([1.0]), np.array([2.0])]))


def _two_band_panel(R, seed=0):
    rng = np.random.default_rng(seed)
    jlevel = {"A": -1.0, "B": -0.3, "C": 0.4, "D": 0.9}
    rows = []
    for cfg, q in {"base": 3.0, "cand": 3.5}.items():          # a true Δ = +0.5
        for jg, lv in jlevel.items():
            for _ in range(R):
                rows.append({"item": cfg, "judge": jg, "score": float(q + lv + rng.normal(0, 0.4))})
    return rows


def test_rev001_two_bands_are_distinct_A_shrinks_B_does_not():
    # REV-001 (relabel-and-disclose): the verdict gate is the gauge DISCRIMINATION band (Band B), a
    # per-use property that does NOT shrink with study size. The uncertainty of the ESTIMATED mean
    # difference (Band A, k·u(Δ̂)) is a SEPARATE quantity that DOES shrink with N and is only disclosed.
    # This test proves the two are behaviourally different — the relabel is substantive, not cosmetic.
    r3 = msai.compare(_two_band_panel(3), baseline="base", level="interval", resolution=0.25)
    r48 = msai.compare(_two_band_panel(48), baseline="base", level="interval", resolution=0.25)
    a3, a48 = r3.comparisons["cand"]["estimate_U"], r48.comparisons["cand"]["estimate_U"]
    b3, b48 = r3.gauge["guard_band"], r48.gauge["guard_band"]
    # Band A (estimate uncertainty) collapses with N (16x trials -> ~4x tighter): must at least halve.
    assert a48 < 0.5 * a3
    # Band B (discrimination band) is a per-use gauge property: N-invariant to within sampling noise.
    assert 0.8 < (b48 / b3) < 1.2
    # The gate is Band B, never Band A: even at N where the estimate is rock-solid, the true Δ=0.5 sits
    # BELOW the discrimination band -> the distinctive "statistically real but below resolution" state.
    cand = r48.comparisons["cand"]
    assert cand["resolvable_raw"] is True          # Band A resolved the estimate (CI excludes 0)
    assert abs(cand["delta"]) < b48                 # ...but |Δ| < Band B: the gauge still cannot discriminate
    assert cand["beyond_gauge"] is False            # so the verdict does NOT claim a resolved difference
    assert "below resolution" in cand["verdict"] or "within noise" not in cand["verdict"]
    # the declared use is stamped on the gauge (Band B is certified for exactly this protocol)
    assert r48.gauge["declared_use"] == "single-panel, single-pass"


def test_rev001_declared_use_is_a_label_not_a_number():
    # The declared_use string travels onto outputs but must NOT change any measured value — a tighter
    # declared use has to be earned by re-characterizing the gauge, never asserted via the parameter.
    rows = _two_band_panel(6)
    default = msai.compare(rows, baseline="base", level="interval", resolution=0.25)
    relabel = msai.compare(rows, baseline="base", level="interval", resolution=0.25,
                           declared_use="triple-panel, 5-pass averaged")
    assert relabel.gauge["declared_use"] == "triple-panel, 5-pass averaged"
    assert default.gauge["guard_band"] == relabel.gauge["guard_band"]        # Band B unchanged
    assert (default.comparisons["cand"]["estimate_U"]
            == relabel.comparisons["cand"]["estimate_U"])                    # Band A unchanged
    assert default.comparisons["cand"]["verdict"] == relabel.comparisons["cand"]["verdict"]


def test_commitB_fold_in_typed_resolution_verdict_contract():
    # COMMIT B: four_state folded into compare(). Every qualified comparison must carry the
    # REV-LANE #009 frozen typed contract, machine-readable, from the SAME code path as the
    # certificate (msai_eval.resolution.four_state) — the adapter never parses the summary string.
    from msai_eval.resolution import four_state
    r = msai.compare(_two_band_panel(8), baseline="base", level="interval", resolution=0.25)
    c = r.comparisons["cand"]
    rv = c["resolution_verdict"]
    frozen = {"state", "U", "U_lo", "U_hi", "nu_eff", "p_beyond", "dof_mode", "state_dominant"}
    assert frozen.issubset(rv.keys())                       # frozen contract present
    assert rv["dof_mode"] == "ws"
    assert rv["provisional"] is True                        # k=4 judges (<5) -> WS νeff provisional
    assert rv["state"] in {"WITHIN-NOISE", "RESOLVED", "BELOW", "AT-EDGE"}
    assert rv["state_dominant"] in {"WITHIN-NOISE", "RESOLVED", "BELOW", "AT-EDGE"}
    # the attached numbers ARE the package four_state, byte-for-byte (one code path, same n/seed)
    ref = four_state(c["delta"], c["ci"], r.gauge["resolution_budget"], c["significant_adj"], dof_mode="ws")
    assert rv["state"] == ref["state"] and rv["U_lo"] == ref["U_lo"] and rv["p_beyond"] == ref["p_beyond"]
    # typed two-band view on the comparison: band_A = estimate_U (per-comparison), band_B = guard_band
    assert c["bands"]["band_A"] == c["estimate_U"]
    assert c["bands"]["band_B"] == r.gauge["guard_band"]
    assert c["bands"]["declared_use"] == "single-panel, single-pass"
    # gauge-level bands: band_B concrete, band_A None-with-pointer (Band A is per-comparison)
    assert r.gauge["bands"]["band_B"] == r.gauge["guard_band"]
    assert r.gauge["bands"]["band_A"] is None and "band_A_note" in r.gauge["bands"]


def test_commitB_provisional_flag_clears_at_five_judges():
    # The provisional-J<5 flag must be data-driven: a 5-judge panel clears it.
    rng = np.random.default_rng(1)
    jlevel = {"A": -1.0, "B": -0.4, "C": 0.0, "D": 0.5, "E": 1.0}     # 5 judges
    rows = []
    for cfg, q in {"base": 3.0, "cand": 3.6}.items():
        for jg, lv in jlevel.items():
            for _ in range(6):
                rows.append({"item": cfg, "judge": jg, "score": float(q + lv + rng.normal(0, 0.4))})
    r = msai.compare(rows, baseline="base", level="interval", resolution=0.25)
    assert r.comparisons["cand"]["resolution_verdict"]["provisional"] is False


def test_commitB_no_resolution_budget_yields_none_verdict():
    # A single-trial gauge has no resolution budget -> resolution_verdict is None, never a fabricated state.
    rows = [{"item": c, "judge": j, "score": s}
            for c, s in {"base": 3, "cand": 4}.items() for j, s in [("A", s), ("B", s)]]
    r = msai.compare(rows, baseline="base", level="interval")
    assert r.comparisons["cand"]["resolution_verdict"] is None


def test_adopt_U_does_not_qualify_frozen_or_no_replicates():
    # Guard A: U is finite from quantization alone, but a gauge whose Type-A noise was never
    # measured (frozen / no replicates) must STILL be refused — qualification keys on grr_sd>0,
    # never on "U is finite".
    frozen = []
    for cfg, q in {"fp16": 5, "q2": 3}.items():
        for jg in ["A", "B", "C"]:
            for _ in range(3):
                frozen.append({"item": cfg, "judge": jg, "score": q})
    assert msai.compare(frozen, baseline="fp16", level="ordinal").gauge["qualified"] is False
    no_rep = []
    for cfg, q in {"fp16": 5, "q2": 3, "q4": 4}.items():
        for jg in ["A", "B", "C", "D"]:
            no_rep.append({"item": cfg, "judge": jg, "score": q})
    r = msai.compare(no_rep, baseline="fp16", level="ordinal")
    assert r.gauge["qualified"] is False and r.gauge["guard_band"] is None


def test_reference_fitness_gate():
    # A reference noisier than the gauge (TUR < 1:1) -> not FIT -> a precondition warning fires,
    # but the relative config-vs-baseline verdict is unaffected (u_ref is common-mode).
    from msai_eval import certified_reference
    data = _make_data()
    grr = msai.compare(data, baseline="fp16", level="ordinal").gauge["grr_sd"]
    loose = certified_reference({c: 4.0 for c in ["fp16", "q4", "q2", "delta_kv", "dither_2bit"]}, u=2 * grr)
    rep = msai.compare(data, baseline="fp16", level="ordinal", reference=loose)
    assert rep.gauge["reference_fitness"] is not None
    assert not str(rep.gauge["reference_fitness"]["verdict"]).startswith("FIT")
    assert any("reference" in w.lower() and ("UNFIT" in w or "MARGINAL" in w) for w in rep.gauge["warnings"])
    assert rep.gauge["qualified"] is True       # relative verdict stands; the reference is a precondition note


def test_resolution_escape_hatch_closes_sub_rubric_attack():
    # Cross-lineage blocker (Gemini + Codex): jittered ordinal scores collapse the inferred
    # resolution so a sub-rubric Δ reads "REAL". The gauge-side defenses: (1) warn when ordinal
    # scores are fractional with no declared resolution, (2) honor an explicit resolution= that
    # restores the quantization floor and turns the false "REAL" into "BELOW gauge resolution".
    eps = 1e-5
    data = {it: {f"J{j}": [c - eps / 2, c + eps / 2] for j in range(5)}
            for it, c in [("baseline", 0.0), ("candidate", 0.001)]}
    bad = msai.compare(data, baseline="baseline", level="ordinal")
    assert any("fractional_ordinal_no_resolution" in w for w in bad.gauge["warnings"])
    assert bad.gauge["qualified"] is False                           # AUTO path: resolution untrusted -> guard band withheld
    assert "REAL" not in bad.comparisons["candidate"]["verdict"]     # ...so no manufactured confident finding (provisional)
    fixed = msai.compare(data, baseline="baseline", level="ordinal", resolution=1.0)
    assert "REAL" not in fixed.comparisons["candidate"]["verdict"]   # declared resolution -> honest "BELOW gauge resolution"
    assert fixed.gauge["guard_band"] > 0.2                           # floor restored (~k/sqrt(12)), not 1.7e-5


def test_helpers():
    assert _holm([]) == []
    assert _cliffs_delta(np.array([5, 5, 4]), np.array([1, 2, 2])) == 1.0   # all greater
    adj = _holm([0.01, 0.04, 0.03])
    assert all(a >= p for a, p in zip(adj, [0.01, 0.04, 0.03]))


def test_summary_runs_and_is_honest():
    rep = msai.compare(_make_data(), baseline="fp16", level="ordinal")
    txt = rep.summary()
    assert "acceptance test" in txt and "GAUGE" in txt
    assert "guard band" in txt


def test_few_judges_flagged():
    # 3 judges -> coarse-CI advisory must surface
    data = []
    for cfg, q in {"fp16": 5, "q2": 3}.items():
        for jg in ["A", "B", "C"]:
            for t in range(4):
                data.append({"item": cfg, "judge": jg, "score": q + (t % 2)})  # some within-cell variation
    rep = msai.compare(data, baseline="fp16", level="ordinal")
    assert any("few_judges_coarse_ci" in w for w in rep.gauge["warnings"])


def test_min_ndc_is_advisory_not_gating():
    # ndc no longer gates qualification — qualification keys on a finite guard band.
    # min_ndc only tunes the ADVISORY warning; even an absurd bar cannot disqualify a
    # gauge that has a measurable resolution (the selection-sensitivity fix).
    data = _make_data()
    assert msai.compare(data, baseline="fp16", min_ndc=5).gauge["qualified"] is True
    absurd = msai.compare(data, baseline="fp16", min_ndc=999)
    assert absurd.gauge["qualified"] is True                                  # guard band exists -> still qualified
    assert any("ADVISORY" in w and "ndc" in w for w in absurd.gauge["warnings"])  # but the advisory fires


def test_clustered_good_configs_still_qualify():
    # The frontier case: every config is GOOD and clusters tightly, so ndc is low (the
    # selection-sensitivity trap that used to FAIL the gate). The gauge still has a finite
    # guard band, so it MUST qualify — ndc must not suppress true findings just because the
    # hand-picked configs happen to cluster. This is the unblock the gate change buys.
    rng = np.random.default_rng(1)
    quality = {"fp16": 4.2, "q4kv": 4.1, "deltakv3": 4.15}   # all good, tightly clustered
    judges = ["A", "B", "C", "D", "E"]
    jbias = {"A": -0.2, "B": 0.18, "C": 0.0, "D": 0.15, "E": -0.1}
    data = []
    for cfg, q in quality.items():
        for jg in judges:
            for _ in range(5):
                s = q + jbias[jg] + rng.normal(0, 0.4)
                data.append({"item": cfg, "judge": jg, "score": float(np.clip(round(s), 1, 5))})
    rep = msai.compare(data, baseline="fp16", level="ordinal")
    assert rep.gauge["guard_band"] is not None and rep.gauge["guard_band"] > 0
    assert rep.gauge["ndc"] < 5                       # configs cluster -> ndc is low...
    assert rep.gauge["qualified"] is True             # ...but the gauge still qualifies on its guard band
    for c in rep.comparisons.values():                # and no clustered good config is a false REAL drop
        assert "REAL" not in c["verdict"]


def test_cli_compare(tmp_path):
    import subprocess, sys
    rng = np.random.default_rng(3)
    rows = ["item,judge,score"]
    for cfg, q in {"fp16": 4.9, "q2": 2.0, "q4": 4.0, "delta_kv": 4.9, "dither_2bit": 3.6}.items():
        for jg, b in {"A": -0.1, "B": 0.1, "C": 0.0, "D": 0.12, "E": -0.05}.items():
            for _ in range(5):
                rows.append(f"{cfg},{jg},{int(np.clip(round(q + b + rng.normal(0, 0.2)), 1, 5))}")
    csv = tmp_path / "configs.csv"; csv.write_text("\n".join(rows))
    out = subprocess.run([sys.executable, "-m", "msai_eval", str(csv), "--compare", "fp16", "--level", "ordinal"],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "acceptance test" in out.stdout and "REAL drop" in out.stdout
