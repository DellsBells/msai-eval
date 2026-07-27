"""Tests for stability() — SPC drift detection for a judge/model over time.

These check the HONESTY behavior, not just that a number comes out: stable reads
in-control, a real drop is caught AFTER the baseline and localized to its run, a frozen
(zero-variance) baseline still localizes a later shift, a genuinely-flat series is NOT
falsely called drifted, and the baseline is honest about being too short.
"""
import msai_eval as msai


def test_stable_in_control():
    rep = msai.stability([0.78, 0.79, 0.77, 0.80, 0.78, 0.79, 0.81, 0.78, 0.79, 0.80])
    assert rep.in_control is True
    assert rep.first_drift_run is None
    assert rep.sigma > 0


def test_drift_detected_and_localized():
    rep = msai.stability([0.78, 0.79, 0.77, 0.80, 0.78, 0.79, 0.81, 0.78, 0.62, 0.61, 0.60])
    assert rep.in_control is False
    assert rep.first_drift_run == 8                      # first post-baseline violation
    assert any("σ" in f["rule"] for f in rep.flags)      # Shewhart 3σ rule fired


def test_frozen_baseline_localizes_later_shift():
    # zero run-to-run variance (e.g. temp-0 anchor) -> no probabilistic limits, but a later
    # change is still, by definition, a process shift, and must be localized.
    rep = msai.stability([0.9] * 8 + [0.5, 0.5])
    assert rep.sigma == 0
    assert any("degenerate_baseline" in w for w in rep.warnings)
    assert rep.in_control is False
    assert rep.first_drift_run == 8


def test_fully_flat_is_in_control():
    # genuinely stable (all identical) is in-control, just flagged that future small drift
    # can't be caught without baseline variance.
    rep = msai.stability([0.9] * 10)
    assert rep.sigma == 0
    assert rep.in_control is True
    assert any("degenerate_baseline" in w for w in rep.warnings)


def test_short_baseline_warns():
    rep = msai.stability([0.80, 0.78, 0.79, 0.81, 0.62, 0.61])
    assert any("short_baseline" in w for w in rep.warnings)


def test_min_shift_filters_jitter_but_keeps_real_drift():
    # frozen baseline; a single-item flip (1/12 ~ 0.083) is below a 1.5/12 floor -> no alarm,
    # but a multi-item drop is real drift -> alarm.
    base = [0.75] * 8
    assert msai.stability(base + [0.667], min_shift=1.5 / 12).in_control is True
    assert msai.stability(base + [0.333], min_shift=1.5 / 12).in_control is False


def test_summary_and_dict_honesty():
    rep = msai.stability([0.78, 0.79, 0.77, 0.80, 0.78, 0.79, 0.81, 0.78, 0.62, 0.61])
    txt = rep.summary().lower()
    assert "drift monitor" in txt and "wrong" in txt      # the DRIFT != WRONG firewall is printed
    d = rep.to_dict()
    assert "first_drift_run" in d and "center" in d and "flags" in d


def test_default_baseline_does_not_swallow_drift():
    # REV-007: on a short series (n=6 < 2·min_baseline) the default baseline must be the FIRST HALF,
    # not clamped UP to min_baseline — otherwise the whole series becomes the baseline and the
    # illustrated 0.78->0.61 drift wrongly reads in_control=True.
    rep = msai.stability([0.78, 0.79, 0.77, 0.80, 0.62, 0.61])
    assert rep.in_control is False
    assert rep.baseline_n == 3                 # n//2, not max(min_baseline, n//2)
    assert rep.first_drift_run == 4
    assert any("short_series" in w for w in rep.warnings)


def _series(fn, n=12, seed=0):
    import numpy as np
    rng = np.random.default_rng(seed)
    return [fn(i, rng) for i in range(n)]


def test_two_gate_trend_boundary_jitter_must_not_alarm():
    # Exhibit 2 (KB #018): boundary jitter — a tiny slope buried in wobble — MUST NOT read as drift.
    # This is the exact A3-overclaim the two-gate fix killed ("slope 7e-5 through ±5e-4 wobble").
    jitter = _series(lambda i, rng: 0.900 + 7e-5 * i + rng.normal(0, 5e-4))
    tr = msai.stability(jitter, scale_span=1.0).trend
    assert tr["is_drift"] is False                       # not a drift finding
    assert tr["gate2"] is False                          # trend does not outrun scatter 2x
    assert "within noise floor" in tr["verdict"]         # NAMED refusal, not silence
    # the refusal carries BOTH gate numbers (P10 auditability)
    assert tr["gate2_threshold"] > 0 and tr["gate1_floor"] == 0.02  # 2% of span=1.0
    assert "scatter=" in tr["verdict"] and "gate1 floor=" in tr["verdict"]


def test_two_gate_trend_real_ramp_must_alarm():
    # A genuine ramp that clears both gates MUST be flagged as drift, both gate numbers printed.
    ramp = _series(lambda i, rng: 3.0 + 0.08 * i + rng.normal(0, 0.02))   # ~1.0 rise on a 1-5 scale
    tr = msai.stability(ramp, scale_span=4.0).trend
    assert tr["is_drift"] is True
    assert tr["gate1"] is True and tr["gate2"] is True
    assert "meaningful drift" in tr["verdict"]


def test_two_gate_trend_meaningfulness_undeclared_without_scale_span():
    # Gate 1 needs a DECLARED scale span; without it, a trend that outruns scatter is reported as
    # meaningfulness-undeclared, never silently promoted to "drift" or silently dropped.
    ramp = _series(lambda i, rng: 3.0 + 0.08 * i + rng.normal(0, 0.02))
    tr = msai.stability(ramp).trend
    assert tr["gate1"] is None and tr["gate1_floor"] is None
    assert tr["is_drift"] is False                       # cannot claim drift without the floor
    assert "UNDECLARED" in tr["verdict"]


def test_two_gate_trend_composes_with_baseline_flat_series():
    # Composes with REV-007's baseline fix: a genuinely flat series has no trend and no SPC drift.
    flat = [0.80, 0.79, 0.81, 0.80, 0.80, 0.79, 0.81, 0.80]
    rep = msai.stability(flat, scale_span=1.0)
    assert rep.trend["is_drift"] is False
    assert rep.in_control is True                         # SPC layer agrees; two systems, both quiet


def test_two_gate_trend_exactly_flat_reads_as_flat_not_outrunning_scatter():
    # Skeptic edge (commit-B verify): an EXACTLY-flat series has slope/scatter at floating-point
    # roundoff. Gate 2 must NOT read roundoff as "trend outruns scatter" even without a declared
    # scale_span — the honest verdict is "flat", never a drift or a strong-sounding trend claim.
    tr = msai.stability([0.5, 0.5, 0.5, 0.5, 0.5, 0.5]).trend   # no scale_span on purpose
    assert tr["is_drift"] is False
    assert tr["gate2"] is False
    assert "flat" in tr["verdict"] and "outruns" not in tr["verdict"]
