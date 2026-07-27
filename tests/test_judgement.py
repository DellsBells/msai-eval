"""Tests for gauge_judgement() — the AIAG %GRR x ndc acceptance verdict, with the
item-selection caveat that distinguishes a bad gauge from a non-representative sample.
"""
import numpy as np
import msai_eval as msai
from msai_eval.variance import gauge_judgement


def test_fully_acceptable():
    assert gauge_judgement({"msi_grr_pct": 7.0, "ndc": 8.0})["verdict"] == "FULLY ACCEPTABLE"


def test_conditional():
    assert gauge_judgement({"msi_grr_pct": 20.0, "ndc": 7.0})["verdict"] == "ACCEPTABLE — CONDITIONAL"


def test_not_acceptable_high_grr():
    assert gauge_judgement({"msi_grr_pct": 45.0, "ndc": 8.0})["verdict"] == "NOT ACCEPTABLE"


def test_ndc_fail_flags_item_selection_when_grr_ok():
    # good gauge (%GRR fine) but ndc<5 -> not acceptable BY ndc, flagged as likely item-selection,
    # NOT a condemnation of the gauge. This is the caliper-study / clustered-items case.
    j = gauge_judgement({"msi_grr_pct": 8.0, "ndc": 2.0})
    assert "ndc" in j["verdict"].lower()
    assert j.get("likely_item_selection") is True
    assert "item" in j["reason"].lower()


def test_frozen_gauge_indeterminate():
    j = gauge_judgement({"msi_grr_pct": 0.0, "ndc": float("inf"), "deterministic": True})
    assert j["verdict"].startswith("INDETERMINATE")


def test_none_when_no_variance():
    assert gauge_judgement(None) is None


def test_renders_in_reliability_summary_and_dict():
    rng = np.random.default_rng(0)
    data = []
    for it, q in {"a": 1, "b": 3, "c": 5, "d": 2, "e": 4}.items():
        for jg in ["J1", "J2", "J3"]:
            for _ in range(3):
                data.append({"item": it, "judge": jg,
                             "score": float(np.clip(round(q + rng.normal(0, 0.3)), 1, 5))})
    rep = msai.reliability(data, level="ordinal")
    assert "GAUGE JUDGEMENT" in rep.summary()
    VALID = {"FULLY ACCEPTABLE", "ACCEPTABLE — CONDITIONAL", "NOT ACCEPTABLE",
             "NOT ACCEPTABLE (ndc < 5)", "INDETERMINATE — frozen gauge", "INDETERMINATE"}
    assert rep.to_dict()["gauge_judgement"]["verdict"] in VALID   # a real verdict, not just truthy


def test_pct_grr_sampling_caveat_and_category_ambiguity():
    # The n-sweep found %GRR carries a ~±15pp sampling band at LLM-judge panel sizes; gauge_judgement must
    # disclose it and flag when that band straddles the 10%/30% acceptance boundaries (category not resolvable).
    near_30 = gauge_judgement({"msi_grr_pct": 28.0, "ndc": 6, "deterministic": False})
    assert "pct_grr_caveat" in near_30 and "sampling band" in near_30["pct_grr_caveat"]
    assert near_30["category_ambiguous"] is True            # 28 ± 15 straddles 30 -> could be NOT ACCEPTABLE
    near_10 = gauge_judgement({"msi_grr_pct": 8.0, "ndc": 7, "deterministic": False})
    assert near_10["category_ambiguous"] is True            # 8 ± 15 straddles 10 -> could be CONDITIONAL
    robust_bad = gauge_judgement({"msi_grr_pct": 99.0, "ndc": 1, "deterministic": False})
    assert robust_bad["category_ambiguous"] is False        # 99 ± 15 clears both boundaries -> robustly NOT ACCEPTABLE
