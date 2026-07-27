"""Tests for proficiency() — En/z scoring vs the robust peer panel (ISO 13528).

Key checks: Algorithm A resists an outlier (so the rogue can't corrupt the reference it's
scored against), a rogue judge is flagged OUTLIER while the honest ones stay CONSISTENT,
replicates unlock En, and the summary keeps the consensus-is-not-truth firewall.
"""
import numpy as np
import msai_eval as msai
from msai_eval.proficiency import proficiency, algorithm_a


def test_algorithm_a_resists_outlier():
    x = [5.0, 5.1, 4.9, 5.0, 5.2, 4.8, 5.0, 5.1, 4.9, 50.0]   # one wild outlier
    xm, s, n = algorithm_a(x)
    assert abs(xm - 5.0) < 0.3 and n == 10                     # consensus stays near 5


def test_consistent_panel_no_outliers():
    rng = np.random.default_rng(0)
    data = []
    for it, q in {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}.items():
        for jg in ["J1", "J2", "J3", "J4", "J5"]:
            data.append({"item": it, "judge": jg, "score": float(q + rng.normal(0, 0.3))})
    rep = msai.proficiency(data)
    verdicts = [d["verdict"] for d in rep.by_judge.values()]
    assert not any("OUTLIER" in v for v in verdicts)
    assert all(("CONSISTENT" in v or "QUESTIONABLE" in v) for v in verdicts)  # scored, not silently INDETERMINATE


def test_rogue_judge_flagged_and_consensus_protected():
    rng = np.random.default_rng(3)
    data = []
    for it, q in {"a": 1, "b": 2, "c": 4, "d": 5, "e": 1, "f": 5, "g": 2, "h": 4}.items():
        for jg in ["J1", "J2", "J3", "J4"]:
            data.append({"item": it, "judge": jg, "score": float(q + rng.normal(0, 0.2))})
        data.append({"item": it, "judge": "ROGUE", "score": float(6 - q)})   # inverted = far off
    rep = msai.proficiency(data)
    assert "OUTLIER" in rep.by_judge["ROGUE"]["verdict"]
    assert "CONSISTENT" in rep.by_judge["J1"]["verdict"]       # robust consensus wasn't dragged
    # prove it was ROBUST consensus, not a plain mean: the assigned value stays near the honest q
    # despite the inverted ROGUE (a plain mean would be pulled ~(6-2q)/5 toward it)
    for it, q in {"a": 1, "b": 2, "c": 4, "d": 5, "e": 1, "f": 5, "g": 2, "h": 4}.items():
        assert abs(rep.by_item[it]["assigned"] - q) < 0.6


def test_replicates_unlock_En_gates_competence():
    # with replicates u_judge is measured; against a tight reference, En must SEPARATE good from bad
    ref = msai.certified_reference({"a": 1, "b": 3, "c": 5, "d": 2, "e": 4}, u=0.15)
    rng = np.random.default_rng(1)
    data = []
    for it, q in {"a": 1, "b": 3, "c": 5, "d": 2, "e": 4}.items():
        for jg in ["GOOD", "P2", "P3"]:
            for _ in range(3):
                data.append({"item": it, "judge": jg, "score": float(q + rng.normal(0, 0.2))})
        for _ in range(3):                                  # a judge a clear 2 points off every item
            data.append({"item": it, "judge": "BAD", "score": float(min(5, q + 2))})
    rep = msai.proficiency(data, reference=ref)
    assert rep.has_replicates
    assert rep.by_judge["BAD"]["en_fail"] >= 1 and "OUTLIER" in rep.by_judge["BAD"]["verdict"]
    # En actually separates: the good judge's worst En is far below the bad judge's
    assert rep.by_judge["GOOD"]["max_abs_En"] < rep.by_judge["BAD"]["max_abs_En"]


def test_loo_floors_trivial_jitter():
    # a judge 0.001 off a near-unanimous rest must NOT read OUTLIER (the review's 5.001-vs-5.0 bug),
    # while a judge 100 off the same rest still does — the floored LOO scale separates them
    base = [{"item": it, "judge": jg, "score": float(q)}
            for it, q in {"a": 1, "b": 3, "c": 5, "d": 2, "e": 4}.items() for jg in ["J1", "J2", "J3", "J4"]]
    soft = base + [{"item": it, "judge": "E", "score": float(q) + (0.001 if it == "c" else 0)}
                   for it, q in {"a": 1, "b": 3, "c": 5, "d": 2, "e": 4}.items()]
    hard = base + [{"item": it, "judge": "E", "score": (105.0 if it == "c" else float(q))}
                   for it, q in {"a": 1, "b": 3, "c": 5, "d": 2, "e": 4}.items()]
    assert "OUTLIER" not in msai.proficiency(soft).by_judge["E"]["verdict"]
    assert "OUTLIER" in msai.proficiency(hard).by_judge["E"]["verdict"]


def test_loo_catches_rogue_in_self_consensus_panel():
    # the classic failure: a rogue is part of the consensus it's scored against. {0,0,100} must NOT
    # read all-CONSISTENT — leave-one-out catches the rogue, and a 3-judge panel can't certify the rest
    data = []
    for it in ["a", "b", "c", "d"]:
        data.append({"item": it, "judge": "G1", "score": 0.0})
        data.append({"item": it, "judge": "G2", "score": 0.0})
        data.append({"item": it, "judge": "ROGUE", "score": 100.0})
    rep = msai.proficiency(data)
    assert "OUTLIER" in rep.by_judge["ROGUE"]["verdict"]            # caught, not hidden in its own consensus
    assert "CONSISTENT" not in rep.by_judge["G1"]["verdict"]        # tiny no-ref panel -> not certified competent


def test_constant_reference_warns():
    # a reference that assigns the SAME target to every item -> En reduces to accuracy-from-target;
    # proficiency must flag it so the OUTLIER verdict isn't read as peer-relative competence
    data = []
    for it, base in {"a": 0.95, "b": 0.5, "c": 0.95, "d": 0.6}.items():  # item-difficulty spread
        for jg in ["J1", "J2", "J3"]:
            data.append({"item": it, "judge": jg, "score": base})
    ref = msai.certified_reference({it: 1.0 for it in ["a", "b", "c", "d"]}, u=0.02)  # tight, constant target
    rep = msai.proficiency(data, reference=ref)
    assert any("reference_constant" in w for w in rep.warnings)


def test_no_replicates_and_small_panel_warnings():
    data = [{"item": it, "judge": jg, "score": float(q + (0.3 if jg == "J3" else 0.0))}
            for it, q in {"a": 1, "b": 3, "c": 5}.items() for jg in ["J1", "J2", "J3"]]
    rep = msai.proficiency(data)
    assert any("small_panel" in w for w in rep.warnings)      # 3 judges (< 4)
    assert any("no_replicates" in w for w in rep.warnings)    # 1 trial per cell


def test_summary_and_dict_honesty():
    rng = np.random.default_rng(2)
    data = [{"item": it, "judge": jg, "score": float(q + rng.normal(0, 0.3))}
            for it, q in {"a": 1, "b": 3, "c": 5, "d": 2, "e": 4}.items() for jg in ["J1", "J2", "J3"]]
    rep = msai.proficiency(data)
    txt = rep.summary().lower()
    assert "proficiency" in txt and "consensus" in txt and "not" in txt   # consensus != truth firewall
    d = rep.to_dict()
    assert d["n_judges"] == 3 and "by_judge" in d
