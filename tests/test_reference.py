"""Tests for reference.py — a traceable reference carries u_ref, combines sources with
Birge-ratio inflation, judges its own fitness (4:1 TUR), refuses consensus, and scores conformance.
"""
import numpy as np
import msai_eval as msai
from msai_eval.reference import (Reference, certified_reference, reference_from_labels,
                                 combine_references, flag_if_consensus, score)


def test_certified_zero_u_warns():
    r = certified_reference({"a": 7.48, "b": 7.49}, u=0.0, source="upc")
    assert r.traceability == "certified"
    assert any("PERFECT reference" in w for w in r.warnings)


def test_labels_give_sem():
    r = reference_from_labels({"a": [5, 5, 6]}, level="ordinal")
    assert abs(r.values["a"] - 5.3333) < 1e-3
    assert abs(r.u["a"] - (np.std([5, 5, 6], ddof=1) / np.sqrt(3))) < 1e-6


def test_combine_consistent_reduces_u_no_inflation():
    r1 = certified_reference({"a": 7.50}, u=0.1)
    r2 = certified_reference({"a": 7.52}, u=0.1)
    c = combine_references([r1, r2])
    # consistent sources: combined u ~ internal (1/sqrt(1/.01+1/.01)=0.0707), tighter than either
    assert c.u["a"] < 0.1 and abs(c.u["a"] - 0.0707) < 0.01


def test_combine_inflates_u_on_disagreement():
    r1 = certified_reference({"a": 7.0}, u=0.1)
    r2 = certified_reference({"a": 7.6}, u=0.1)          # disagree by 6 stated-sigmas
    c = combine_references([r1, r2])
    assert c.u["a"] > 0.2                                 # Birge-inflated well above the 0.07 internal
    assert any("Birge" in w for w in c.warnings)


def test_conflicting_exact_sources_flagged():
    c = combine_references([certified_reference({"a": 7.0}, u=0.0),
                            certified_reference({"a": 7.5}, u=0.0)])
    assert c.u["a"] > 0                                   # widened from the impossible u=0
    assert any("conflicting EXACT" in w for w in c.warnings)


def test_fitness_tur_verdicts():
    fit = certified_reference({"a": 5.0, "b": 6.0}, u=0.01).fitness(gauge_sd=0.2)
    assert fit["verdict"].startswith("FIT")
    unfit = certified_reference({"a": 5.0, "b": 6.0}, u=0.5).fitness(gauge_sd=0.1)
    assert unfit["verdict"].startswith("UNFIT")


def test_score_conformance_within_u_ref():
    r = certified_reference({"a": 5.0, "b": 5.0}, u=0.2)   # U_ref = 0.4 at k=2
    s = score(r, {"a": 5.1, "b": 6.0})
    pa = next(p for p in s["per_item"] if p["item"] == "a")
    pb = next(p for p in s["per_item"] if p["item"] == "b")
    assert pa["conformant"] and not pb["conformant"]       # 0.1 within U_ref, 1.0 outside
    assert abs(pa["En"] - 0.25) < 0.01 and pb["En"] > 1


def test_consensus_firewall_marks_invalid():
    consensus = {"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0}
    r = certified_reference(dict(consensus), u=0.1)
    assert flag_if_consensus(r, consensus, level="ordinal") is True
    assert "INVALID" in r.traceability
    assert any("reference_is_consensus" in w for w in r.warnings)


# --- wiring: Reference flows into reliability()'s accuracy tier and proficiency() ---

def test_reliability_accepts_reference_object():
    ref = certified_reference({"a": 1.0, "b": 3.0}, u=0.5)   # U_ref = 1.0 per item
    # J1: off 0.5 on a (within the 1.0 band -> correct), off 2.0 on b (outside -> wrong)
    data = [{"item": "a", "judge": "J1", "score": 1.5}, {"item": "b", "judge": "J1", "score": 5.0},
            {"item": "a", "judge": "J2", "score": 1.0}, {"item": "b", "judge": "J2", "score": 3.0}]
    rep = msai.reliability(data, level="ordinal", reference=ref)
    assert rep.to_dict()["accuracy"]["tol"] == "per-item U_ref"
    j1 = rep.accuracy["by_judge"]["J1"]
    assert j1["n"] == 2 and abs(j1["accuracy"] - 0.5) < 1e-9   # 1 of 2 within the U_ref band proves it's applied


def test_nominal_string_labels_work():
    # the README's headline nominal example uses string labels ("A"/"C") — must not crash, and
    # the reference must encode with the SAME label map so "A" matches "A"
    scores = [{"item": it, "judge": jg, "score": truth}
              for it, truth in {"r1": "A", "r2": "C", "r3": "B"}.items() for jg in ["J1", "J2", "J3"]]
    rep = msai.reliability(scores, level="nominal", reference={"r1": "A", "r2": "C", "r3": "B"})
    assert rep.accuracy["overall_accuracy"] == 1.0   # string labels encoded + matched the reference


def test_nominal_digit_string_labels_work():
    # DIGIT-string category IDs ("1"/"2"/"3", the README's "category IDs") must not silently score 0
    # against a string reference (the review BLOCKER): a string "1" must match a numeric label 1
    scores = [{"item": it, "judge": jg, "score": t}
              for it, t in {"r1": "1", "r2": "2", "r3": "3"}.items() for jg in ["J1", "J2"]]
    rep = msai.reliability(scores, level="nominal", reference={"r1": "1", "r2": "2", "r3": "3"})
    assert rep.accuracy["overall_accuracy"] == 1.0   # was silently 0.0 before the level-driven encoding


def test_reliability_accuracy_fitness_gate():
    # a reference far looser than the data scale must NOT yield a clean 100% accuracy with no flag
    ref = certified_reference({"a": 0.0, "b": 10.0, "c": 5.0}, u=100.0)   # U_ref=200, absurdly loose
    data = [{"item": it, "judge": jg, "score": v + 50.0}                  # off by 50, inside the 200 band
            for it, v in {"a": 0.0, "b": 10.0, "c": 5.0}.items() for jg in ["J1", "J2"]]
    rep = msai.reliability(data, level="ordinal", reference=ref)
    assert rep.accuracy["overall_accuracy"] == 1.0                        # the misleading "100%" still computes
    assert any("reference_not_fit_for_accuracy" in f for f in rep.flags)  # but now it is flagged loudly


def test_reliability_surfaces_invalid_reference():
    truth = {"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0}
    ref = certified_reference(dict(truth), u=0.2)
    flag_if_consensus(ref, truth)                                # mark the REFERENCE invalid (it == this consensus)
    assert "INVALID" in ref.traceability
    # judges do NOT match the reference -> reliability's OWN consensus re-detector cannot fire,
    # so only the PROPAGATED traceability flag can surface
    data = [{"item": it, "judge": jg, "score": float(5 - v)}
            for it, v in truth.items() for jg in ["J1", "J2", "J3"]]
    rep = msai.reliability(data, level="ordinal", reference=ref)
    assert any("traceability_invalid" in f for f in rep.flags)


def test_proficiency_reference_catches_whole_panel_error():
    # the WHOLE panel agrees on 5.0 for item x, but the traceable truth is 2.0
    rng = np.random.default_rng(5)
    data = []
    for it, q in {"a": 1, "b": 3, "c": 5}.items():
        for jg in ["J1", "J2", "J3", "J4"]:
            data.append({"item": it, "judge": jg, "score": float(q + rng.normal(0, 0.3))})
    for jg in ["J1", "J2", "J3", "J4"]:
        data.append({"item": "x", "judge": jg, "score": 5.0})    # unanimous, and wrong
    ref = certified_reference({"x": 2.0}, u=0.1)                  # tight traceable truth

    panel_only = msai.proficiency(data)                          # blind: agreement hides the error
    assert panel_only.by_item["x"]["s_robust"] == 0              # unanimous -> no panel discrimination (the mechanism)
    assert not any("OUTLIER" in d["verdict"] for d in panel_only.by_judge.values())

    with_ref = msai.proficiency(data, reference=ref)             # sees it: all judges off the reference
    assert with_ref.n_reference_items == 1
    assert with_ref.by_item["x"]["source"] == "reference"
    assert all(d.get("en_fail", 0) >= 1 for d in with_ref.by_judge.values())
    assert all("OUTLIER" in d["verdict"] for d in with_ref.by_judge.values())


def test_fitness_marginal_band_and_indeterminate():
    f = certified_reference({"a": 5.0}, u=0.1).fitness(gauge_sd=0.2)   # U_gauge=0.4, U_ref=0.2 -> ratio 2
    assert f["verdict"].startswith("MARGINAL") and abs(f["ratio"] - 2.0) < 1e-9
    assert certified_reference({"a": 5.0}, u=0.05).fitness(gauge_sd=None)["verdict"] == "INDETERMINATE"


def test_reference_from_labels_nominal_path():
    r = reference_from_labels({"a": ["x", "x", "y"]}, level="nominal")
    assert r.values["a"] == "x" and abs(r.u["a"] - (1 - 2 / 3)) < 1e-9   # modal category + disagreement rate


def test_score_verdict_tiers_and_en_pass_rate():
    r = certified_reference({"a": 5.0, "b": 5.0}, u=0.5)              # U_ref = 1.0; assigned identical so no 'too loose'
    s = score(r, {"a": 5.2, "b": 9.0})                               # a within band, b far out
    assert s["conformance_rate"] == 0.5 and s["en_pass_rate"] == 0.5
    assert s["verdict"] == "NONCONFORMANT vs traceable reference"
