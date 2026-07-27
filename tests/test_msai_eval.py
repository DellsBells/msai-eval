"""Validation tests. The agreement stats are checked against published
reference values so the package's core promise — correct measurement — is
itself measured.
"""
import math
import numpy as np
import msai_eval
from msai_eval.agreement import krippendorff_alpha, icc_2_1, weighted_kappa


def test_krippendorff_canonical():
    # Krippendorff's canonical reliability-data example (raters x units), with missing.
    nan = np.nan
    data = np.array([
        [1, 2, 3, 3, 2, 1, 4, 1, 2, nan, nan, nan],
        [1, 2, 3, 3, 2, 2, 4, 1, 2, 5,   nan, 3],
        [nan, 3, 3, 3, 2, 3, 4, 2, 2, 5, 1,   nan],
        [1, 2, 3, 3, 2, 4, 4, 1, 2, 5,   1,   nan],
    ], dtype=float)
    assert abs(krippendorff_alpha(data, "nominal") - 0.743) < 0.01
    assert abs(krippendorff_alpha(data, "interval") - 0.849) < 0.01
    assert abs(krippendorff_alpha(data, "ordinal") - 0.815) < 0.02


def test_icc_shrout_fleiss():
    # Shrout & Fleiss (1979) example; ICC(2,1) absolute agreement ~ 0.29.
    M = np.array([
        [9, 2, 5, 8],
        [6, 1, 3, 2],
        [8, 4, 6, 8],
        [7, 1, 2, 6],
        [10, 5, 6, 9],
        [6, 2, 4, 7],
    ], dtype=float)
    assert abs(icc_2_1(M) - 0.29) < 0.02


def test_weighted_kappa_perfect():
    r = [1, 2, 3, 4, 5, 1, 2, 3]
    assert abs(weighted_kappa(r, r) - 1.0) < 1e-9


def test_perfect_agreement_alpha_one():
    # all judges give identical scores per item -> alpha = 1
    data = {f"item{i}": {"A": i % 5, "B": i % 5, "C": i % 5} for i in range(20)}
    rep = msai_eval.reliability(data)
    assert rep.alpha > 0.999


def test_repeatability_unmeasured_but_not_frozen():
    # judges DISAGREE (real reproducibility) but each has identical trials (temp 0). This is NOT a
    # frozen gauge — it can resolve via reproducibility — so deterministic must be FALSE, with an
    # honest repeatability_unmeasured flag (the cross-track frozen-gate fix).
    data = []
    for i in range(12):
        for j in ["A", "B"]:
            base = (i * 7 + (0 if j == "A" else 3)) % 10
            for _ in range(3):                      # 3 identical trials, but A and B disagree
                data.append({"item": f"i{i}", "judge": j, "score": base})
    rep = msai_eval.reliability(data)
    assert rep.variance is not None
    assert rep.variance["deterministic"] is False        # real reproducibility -> not a frozen gauge
    assert any("repeatability_unmeasured" in f for f in rep.flags)


def test_frozen_gauge_flagged():
    # truly frozen: every judge gives the SAME value, identical trials -> GRR ~ 0 -> deterministic
    data = []
    for i in range(12):
        v = i % 5
        for j in ["A", "B"]:
            for _ in range(3):
                data.append({"item": f"i{i}", "judge": j, "score": v})
    rep = msai_eval.reliability(data)
    assert rep.variance["deterministic"] is True
    assert any("frozen_gauge" in f for f in rep.flags)


def test_single_judge_flagged():
    data = [{"item": f"i{i}", "judge": "A", "score": i % 4} for i in range(15)]
    rep = msai_eval.reliability(data)
    assert any("single_judge" in f for f in rep.flags)


def test_variance_decomposition_runs():
    # balanced, replicated, with real within-cell noise -> full Gage R&R
    rng = np.random.default_rng(0)
    data = []
    item_true = {i: rng.uniform(20, 80) for i in range(15)}
    for i in range(15):
        for j in ["A", "B", "C"]:
            jbias = {"A": -3, "B": 0, "C": 4}[j]
            for _ in range(3):
                s = item_true[i] + jbias + rng.normal(0, 5)
                data.append({"item": i, "judge": j, "score": s})
    rep = msai_eval.reliability(data, level="interval")
    v = rep.variance
    assert v is not None
    assert 0 <= v["measurement_noise_share_pct"] <= 100
    # item signal should dominate noise in this construction
    assert v["measurement_noise_share_pct"] < 50


def test_report_summary_states_scope():
    data = {f"i{i}": {"A": i % 5, "B": (i + 1) % 5} for i in range(12)}
    rep = msai_eval.reliability(data)
    text = rep.summary()
    assert "does NOT, by itself, mean the judges are right" in text
    assert "no\n    accuracy is claimed" in text or "no accuracy is claimed" in text.replace("\n    ", " ")


def test_nominal_skips_magnitude_stats():
    # category IDs as scores: must NOT produce mean-based numeric stats.
    # Two judges agree on category; one is a consistent dissenter.
    cats = [11860, 31774, 180960, 260012, 95672]
    data = []
    for i in range(15):
        true_cat = cats[i % len(cats)]
        data.append({"item": f"x{i}", "judge": "A", "score": true_cat})
        data.append({"item": f"x{i}", "judge": "B", "score": true_cat})
        # C dissents on every 3rd item
        data.append({"item": f"x{i}", "judge": "C",
                     "score": true_cat if i % 3 else cats[(i + 1) % len(cats)]})
    rep = msai_eval.reliability(data, level="nominal")
    assert rep.is_nominal is True
    assert rep.icc != rep.icc or rep.icc is None or str(rep.icc) == "nan"  # ICC suppressed (nan)
    assert rep.raw["mean_abs_diff"] is None                                # no magnitude stat
    assert rep.variance is None                                            # no variance decomp
    # dissent rates are in [0,1], not category-id magnitudes
    for v in rep.rater_effects.values():
        assert 0.0 <= v <= 1.0
    assert rep.rater_effects["C"] > rep.rater_effects["A"]                 # C dissents more


def test_accuracy_tier_vs_reference():
    # Judge A is right; judge B is biased low by 1 on a 1-5 scale.
    ref = {f"q{i}": (i % 5) + 1 for i in range(20)}
    data = []
    for i in range(20):
        truth = (i % 5) + 1
        data.append({"item": f"q{i}", "judge": "A", "score": truth})
        data.append({"item": f"q{i}", "judge": "B", "score": max(1, truth - 1)})
    rep = msai_eval.reliability(data, level="ordinal", reference=ref)
    assert rep.accuracy is not None
    assert abs(rep.accuracy["by_judge"]["A"]["accuracy"] - 1.0) < 1e-9      # A perfect
    assert rep.accuracy["by_judge"]["B"]["accuracy"] < 0.3                  # B mostly off
    assert rep.accuracy["by_judge"]["B"]["mae"] > 0.5                       # and biased
    text = rep.summary()
    assert "judge consensus is NOT a valid reference" in text


def test_high_agreement_can_be_wrong_together():
    # Both judges AGREE but are both WRONG vs reference: shared bias.
    ref = {f"q{i}": (i % 4) + 1 for i in range(16)}
    data = []
    for i in range(16):
        wrong = ((i % 4) + 1) % 4 + 1   # both judges give the same wrong answer
        data.append({"item": f"q{i}", "judge": "A", "score": wrong})
        data.append({"item": f"q{i}", "judge": "B", "score": wrong})
    rep = msai_eval.reliability(data, level="ordinal", reference=ref)
    assert rep.alpha > 0.9                                  # high agreement
    assert rep.accuracy["overall_accuracy"] < 0.2          # but wrong


def test_consensus_reference_flagged():
    # reference IS the judges' consensus -> circular -> must flag
    data, ref = [], {}
    cats = [10, 20, 30, 40]
    for i in range(12):
        c = cats[i % 4]
        for j in ["A", "B", "C"]:
            data.append({"item": f"i{i}", "judge": j, "score": c})
        ref[f"i{i}"] = c                      # reference == what everyone said
    rep = msai_eval.reliability(data, level="nominal", reference=ref)
    assert any("reference_is_consensus" in f for f in rep.flags)


def test_reference_key_mismatch_flagged():
    data = [{"item": f"i{i}", "judge": j, "score": (i % 5) + 1}
            for i in range(12) for j in ["A", "B"]]
    ref = {f"WRONG{i}": 3 for i in range(12)}      # keys don't match any item
    rep = msai_eval.reliability(data, level="ordinal", reference=ref)
    assert any("reference_keys_not_in_data" in f for f in rep.flags)


def test_non_numeric_score_errors_helpfully():
    import pytest
    data = [{"item": "i1", "judge": "A", "score": "N/A"},
            {"item": "i1", "judge": "B", "score": 3}]
    with pytest.raises(ValueError, match="non-numeric score"):
        msai_eval.reliability(data)


def test_empty_data_errors():
    import pytest
    with pytest.raises(ValueError, match="no data"):
        msai_eval.reliability([])


def test_cli_runs(tmp_path):
    import subprocess, sys, textwrap
    csv = tmp_path / "s.csv"
    csv.write_text(textwrap.dedent("""\
        item,judge,score,reference
        q1,A,5,5
        q1,B,5,5
        q2,A,2,3
        q2,B,3,3
        q3,A,4,4
        q3,B,4,4
    """))
    out = subprocess.run([sys.executable, "-m", "msai_eval", str(csv), "--level", "ordinal"],
                         capture_output=True, text=True)
    assert out.returncode == 0
    assert "ACCURACY" in out.stdout and "MSAI" in out.stdout


def test_to_html_renders(tmp_path):
    data = {f"i{i}": {"A": i % 5, "B": (i + 1) % 5, "C": i % 5} for i in range(15)}
    rep = msai_eval.reliability(data, level="nominal")
    assert rep.detail is not None and len(rep.detail["grid"]) == 3
    out = rep.to_html(str(tmp_path / "r.html"))
    html = open(out).read()
    assert "window.__MSAI__" in html and "UnrealBloomPass" in html
    assert "0 " not in html  # token replaced, not literal
