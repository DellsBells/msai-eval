"""Tests for uncertainty_budget() — the GUM budget: combine sources, find the dominant lever,
inflate k when degrees of freedom are small, fold in u_ref."""
import numpy as np
import pytest
import msai_eval as msai
from msai_eval.variance import variance_components
from msai_eval.data import normalize


def test_resolution_uses_modal_gap_not_min_collapse():
    # one near-equal pair (3 vs 3.00001) must NOT collapse the resolution to ~1e-5 (the BLOCKER)
    data = []
    for it, q in {"a": 1, "b": 2, "c": 3, "d": 3.00001, "e": 4, "f": 5}.items():
        for jg in ["J1", "J2"]:
            for _ in range(2):
                data.append({"item": it, "judge": jg, "score": float(q)})
    rep = msai.uncertainty_budget(data, level="ordinal")
    res = next((c for c in rep.components if "resolution" in c["source"]), None)
    assert res is not None and res["u"] > 0.1   # modal gap ~1 -> u~0.289, NOT min-gap 1e-5 -> u~3e-6


def test_deterministic_gate_is_relative_to_scale():
    # within-cell SD ~1.5e-6 on a 1-5 scale is effectively frozen -> must flag deterministic
    data = []
    for it, q in {"a": 1, "b": 3, "c": 5, "d": 2}.items():
        for jg in ["J1", "J2", "J3"]:
            data.append({"item": it, "judge": jg, "score": float(q)})
            data.append({"item": it, "judge": jg, "score": float(q) + 3e-6})   # tiny 2nd-trial jitter
    var = variance_components(normalize(data))
    assert var["deterministic"] is True   # clears the absolute 1e-12 floor, caught by the relative gate


def _tight_agreeing(n_items=6):
    # judges score identically (no repeat/repro variance) -> only the resolution term survives
    data = []
    for it in range(n_items):
        v = it % 5 + 1
        for jg in ["J1", "J2", "J3"]:
            for _ in range(2):
                data.append({"item": f"i{it}", "judge": jg, "score": float(v)})
    return data


def _judges_disagree(n_items=8):
    # fixed per-judge offsets -> reproducibility (between-judge) dominates, repeatability ~0
    data = []
    for it in range(n_items):
        base = it % 3 + 2            # 2..4, so +/-1 never clips
        for jg, off in [("J1", -1), ("J2", 0), ("J3", 1)]:
            for _ in range(2):
                data.append({"item": f"i{it}", "judge": jg, "score": float(base + off)})
    return data


def test_resolution_dominates_when_judges_agree():
    rep = msai.uncertainty_budget(_tight_agreeing())
    assert rep.dominant["source"].startswith("resolution")
    assert abs(rep.u_c - 1.0 / np.sqrt(12)) < 1e-6        # only the quantization term


def test_reproducibility_dominates_when_judges_disagree():
    rep = msai.uncertainty_budget(_judges_disagree())
    assert rep.dominant["source"].startswith("reproducibility")
    assert "judges disagree" in rep._lever()


def test_small_panel_inflates_k_above_2():
    rep = msai.uncertainty_budget(_judges_disagree())     # 3 judges -> dof_repro = 2
    assert rep.k > 2.0                                     # t-based coverage, not the lazy k=2


def test_reference_adds_a_term():
    data = _tight_agreeing()
    ref = msai.certified_reference({f"i{it}": it % 5 + 1 for it in range(6)}, u=0.3)
    rep = msai.uncertainty_budget(data, reference=ref)
    assert any("reference" in c["source"] for c in rep.components)


def test_combined_and_expanded_consistent():
    rep = msai.uncertainty_budget(_judges_disagree())
    assert abs(sum(c["pct"] for c in rep.components) - 100.0) < 0.5
    assert abs(rep.U - rep.k * rep.u_c) < 1e-6


def test_nominal_is_rejected():
    with pytest.raises(ValueError):
        msai.uncertainty_budget([{"item": "a", "judge": "J1", "score": "cat"}], level="nominal")


def test_accepts_dataset_passthrough():
    # a caller that already has a Dataset can pass it straight in (no recompute, identical result)
    from msai_eval.data import normalize
    data = _judges_disagree()
    ds = normalize(data)
    assert normalize(ds) is ds
    assert msai.uncertainty_budget(ds).U == msai.uncertainty_budget(data).U


def test_resolution_auto_inferred_warns_on_non_integer_grid():
    # continuous (non-integer) scores with no resolution= -> warn the step was auto-inferred (defeatable)
    data = [{"item": it, "judge": jg, "score": v}
            for it, v in {"a": 1.3, "b": 2.7, "c": 4.1, "d": 0.6}.items() for jg in ["J1", "J2"] for _ in (0, 1)]
    assert any("resolution_auto_inferred" in w for w in msai.uncertainty_budget(data, level="interval").warnings)
    assert not any("resolution_auto_inferred" in w
                   for w in msai.uncertainty_budget(data, level="interval", resolution=0.1).warnings)
