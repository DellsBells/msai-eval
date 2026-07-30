"""stability.py — drift detection for an AI judge/model over time (the time axis).

MSAI's other modules are one-shot snapshots. This one watches a FROZEN anchor set
re-measured across runs and flags when the measurement process has DRIFTED — a silent
model update, a prompt edit, a quantization swap, a vendor model-version bump — using
Shewhart control limits + EWMA + Western Electric rules.

Field grounding (private practitioner corpus, not redistributed here):
  - Don't trust the maker's interval alone; schedule intermediate checks between calibrations.
  - When drift fires, look BACKWARD and re-adjudicate prior outputs; the worst failure is a silent
    shift with no visible error. Clause-level grounding: docs/SPEC_GROUNDING.md.

HONESTY FIREWALL: DRIFT != WRONG. An out-of-control flag means the measurement *process*
changed, not that the post-drift value is incorrect — that's a precision signal, not an
accuracy verdict (respect the precision-vs-accuracy boundary the rest of MSAI keeps).

    from msai_eval import stability
    rep = stability([0.78, 0.79, 0.77, 0.80, 0.62, 0.61])  # accuracy on the anchor set per run
    rep.summary()
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class StabilityReport:
    in_control: bool                 # no out-of-control point AFTER the baseline window
    center: float                    # Phase-I baseline mean (the calibrated center line)
    sigma: float                     # Phase-I baseline SD (run-to-run noise)
    ucl: float
    lcl: float
    baseline_n: int
    flags: list                      # [{run, value, rule}] — every rule violation, any run
    first_drift_run: Optional[int]   # earliest post-baseline violation (the "look back to here" point)
    warnings: list
    n_runs: int
    # Exhibit 2 (KB #018) two-gate TREND discipline — "a trend the noise can explain is not a trend".
    # Distinct from the point/shift SPC flags above; gates a linear-drift (slope) reading so boundary
    # jitter can never be called "steadily rising". Both gate numbers are always populated (P10).
    trend: dict = field(default_factory=dict)  # {slope,total,scatter,gate1_floor,gate2_threshold,gate1,gate2,is_drift,verdict}

    def to_dict(self):
        return {k: getattr(self, k) for k in
                ("in_control", "center", "sigma", "ucl", "lcl", "baseline_n",
                 "flags", "first_drift_run", "warnings", "n_runs", "trend")}

    def summary(self):
        L = []
        L.append("=" * 62)
        L.append("  MSAI — stability / drift monitor (frozen anchor set)")
        L.append("=" * 62)
        L.append(f"  runs: {self.n_runs}   baseline (Phase-I): first {self.baseline_n}")
        L.append(f"  center (calibrated) = {self.center:.4f}   run-to-run SD = {self.sigma:.4f}")
        if self.sigma > 0:
            L.append(f"  control limits (3σ): [{self.lcl:.4f}, {self.ucl:.4f}]")
        for w in self.warnings:
            L.append(f"  [!] {w}")
        tr = self.trend or {}
        if tr.get("verdict"):
            tag = "DRIFT (trend)" if tr.get("is_drift") else "no trend finding"
            L.append(f"  trend (two-gate): {tag} — {tr['verdict']}")
        if self.in_control:
            L.append("  -> IN CONTROL — no drift after baseline; the gauge is stable, scores comparable.")
        else:
            L.append(f"  -> DRIFT DETECTED — first at run {self.first_drift_run}. Re-calibrate, and")
            L.append(f"     RE-ADJUDICATE everything scored since run {self.first_drift_run} (drift != wrong,")
            L.append("     but the process changed, so prior verdicts are no longer comparable).")
            for f in self.flags:
                if f["run"] >= self.baseline_n:
                    L.append(f"       run {f['run']}: value={f['value']:.4f}  [{f['rule']}]")
        L.append("  NOTE: a flag means the measurement PROCESS shifted, not that the new value is")
        L.append("        wrong. It is a trigger to investigate + re-anchor, not an accuracy claim.")
        L.append("=" * 62)
        print("\n".join(L))
        return "\n".join(L)


def _two_gate_trend(v, scale_span, min_trend_frac, scatter_mult):
    """Exhibit 2 (KB #018) — 'a trend the noise can explain is not a trend.' Two gates, both printed:

      Gate 1 (meaningful floor): |total trend over the window| >= min_trend_frac * scale_span.
             scale_span is the rating-scale span, DECLARED by the caller (not the observed data range —
             deriving the floor from a jittery series' own range defeats the gate). Unknown if not declared.
      Gate 2 (outruns scatter):  |total trend over the window| >= scatter_mult * residual scatter.

    A drift-by-trend claim needs BOTH gates; otherwise a NAMED refusal carrying both numbers. Gate 2 needs
    only the data; Gate 1 needs a declared scale — without it, meaningfulness is UNDECLARED, never assumed.
    """
    v = np.asarray(v, float)
    fin = np.isfinite(v)
    vv, x = v[fin], np.arange(v.size, dtype=float)[fin]
    if vv.size < 3:
        return {"slope": 0.0, "total": 0.0, "scatter": 0.0, "gate1_floor": None,
                "gate2_threshold": 0.0, "gate1": None, "gate2": None, "is_drift": False,
                "verdict": "no trend assessed: need >=3 finite runs"}
    slope, intercept = (float(c) for c in np.polyfit(x, vv, 1))
    total = slope * (x.max() - x.min())                       # rise across the observed window
    scatter = float((vv - (slope * x + intercept)).std(ddof=1))
    g2_thresh = scatter_mult * scatter
    flat_eps = 1e-9 * max(1.0, float(np.abs(vv).max()))       # roundoff floor: a slope this tiny is flat,
    flat = abs(total) <= flat_eps                             # not a "trend" — guard so exactly-flat series
    gate2 = bool(abs(total) >= g2_thresh and not flat)        # don't read roundoff as "outrunning scatter".
    floor = (min_trend_frac * scale_span) if scale_span is not None else None
    gate1 = bool(abs(total) >= floor) if floor is not None else None
    is_drift = bool(gate2 and gate1 is True)
    nums = (f"|total trend|={abs(total):.4g} over {int(x.max() - x.min())} runs; scatter={scatter:.4g} "
            f"(gate2 needs >= {g2_thresh:.4g}" + (f"; gate1 floor={floor:.4g})" if floor is not None else "; gate1 floor UNDECLARED)"))
    if flat:
        verdict = f"no trend: series is flat (|total trend|={abs(total):.2g}, at roundoff)"
    elif not gate2:
        verdict = f"refused: trend within noise floor — {nums}"
    elif floor is None:
        verdict = f"trend outruns scatter, but meaningfulness UNDECLARED (pass scale_span) — {nums}"
    elif not gate1:
        verdict = f"refused: below meaningful floor — {nums}"
    else:
        verdict = f"meaningful drift: passes both gates — {nums}"
    return {"slope": slope, "total": float(total), "scatter": scatter, "gate1_floor": floor,
            "gate2_threshold": float(g2_thresh), "gate1": gate1, "gate2": bool(gate2),
            "is_drift": is_drift, "verdict": verdict}


def stability(values, baseline: Optional[int] = None, k: float = 3.0,
              ewma_lambda: float = 0.3, min_baseline: int = 8,
              min_shift: float = 0.0, scale_span: Optional[float] = None,
              min_trend_frac: float = 0.02, trend_scatter_mult: float = 2.0) -> StabilityReport:
    """Watch a metric measured on a FROZEN anchor set across runs for drift.

    values        per-run measurement on the anchor set (accuracy, mean judge score,
                  agreement — anything stable when the process is stable). Runs in order.
    baseline      # of initial runs as the Phase-I baseline (default: first half, >= min_baseline).
    k             control-limit width in σ (3 = Shewhart default).
    ewma_lambda   EWMA weight (smaller = more sensitive to small sustained drift).
    min_baseline  below this, control limits are flagged unstable (false-alarm prone).
    min_shift     practical-significance floor: a deviation must exceed this magnitude to
                  flag, so single-item measurement jitter (esp. on a frozen baseline) doesn't
                  trip a false alarm. Set to ~1.5/(anchor size) for a count-based accuracy.
    scale_span    the rating-scale span (e.g. 4.0 for a 1-5 scale, 1.0 for accuracy) used by the
                  two-gate trend detector's meaningful-drift floor (Gate 1). DECLARE it — the floor
                  must not be derived from the jittery data's own range. Unknown if left None.
    min_trend_frac  Gate 1 floor as a fraction of scale_span (default 0.02 = 2% of span across the
                  window; KB #018 exhibit 2). Printed on the trend verdict.
    trend_scatter_mult  Gate 2 multiplier: a trend must exceed this × residual scatter to count as
                  drift (default 2.0 — "total trend must outrun scatter 2×"). Printed on the verdict.
    """
    v = np.asarray(list(values), float)
    n = len(v)
    _trend = _two_gate_trend(v, scale_span, min_trend_frac, trend_scatter_mult)
    if n < 2:
        return StabilityReport(True, float(v[0]) if n else float("nan"), 0.0, float("nan"),
                               float("nan"), n, [], None,
                               ["insufficient_runs: need >=2 runs to assess stability"], n,
                               trend=_trend)

    b = baseline if baseline is not None else max(2, n // 2)   # default = first half; do NOT clamp UP to
    # min_baseline (REV-007: max(min_baseline, n//2) swallowed drift when n < 2·min_baseline — the whole series
    # became the baseline, so a post-baseline drift had no runs left to flag).
    b = max(2, min(b, n))
    base = v[:b]
    bf = base[np.isfinite(base)]                    # nan/inf must not poison the Phase-I baseline
    center = float(bf.mean()) if bf.size else float("nan")
    sigma = float(bf.std(ddof=1)) if bf.size >= 2 else 0.0
    ucl, lcl = center + k * sigma, center - k * sigma

    warnings = []
    if baseline is None and n < 2 * min_baseline:
        warnings.append(f"short_series: n={n} < 2·min_baseline ({2 * min_baseline}); the default baseline "
                        f"(first {b}) leaves few Phase-I runs and unstable control limits — pass baseline= "
                        "explicitly with a known-stable Phase-I window.")
    if not np.isfinite(v).all():
        warnings.append(f"non_finite_values: {int((~np.isfinite(v)).sum())} run(s) are nan/inf — excluded from "
                        "baseline stats and not assessable for drift; fix the upstream metric.")
    if not np.isfinite(center):
        warnings.append("baseline_unusable: no finite values in the baseline window — control limits are nan.")
    if b < min_baseline:
        warnings.append(f"short_baseline: {b} runs (<{min_baseline}) — control limits are wide/unstable. NOTE: a "
                        "short baseline is NOT more false-alarm-prone (wide limits absorb noise); the false-alarm "
                        "risk comes from the multi-rule gate itself (see drift_false_alarm_rate), at any baseline.")
    if sigma == 0:
        warnings.append("degenerate_baseline: zero run-to-run variance (frozen/identical runs) — "
                        "cannot set Shewhart limits; any later change reads as drift")

    flags = []
    if sigma > 0:
        # Rule 1 — any point beyond k-sigma AND past the practical-shift floor
        for i in range(n):
            if (v[i] > ucl or v[i] < lcl) and abs(v[i] - center) > min_shift:
                flags.append({"run": i, "value": float(v[i]), "rule": f"beyond {k:g}σ"})
    else:
        # Frozen baseline: no probabilistic limits, but any post-baseline deviation past the
        # practical-shift floor is, by definition, a change in the process.
        for i in range(b, n):
            if abs(v[i] - center) > min_shift:
                flags.append({"run": i, "value": float(v[i]), "rule": "deviation from frozen baseline"})
    # Western-Electric shift — 8 consecutive points on one side of the center line
    side = np.sign(v - center)
    rl = 1
    for i in range(1, n):
        if side[i] != 0 and side[i] == side[i - 1]:
            rl += 1
            if rl >= 8:
                flags.append({"run": i, "value": float(v[i]), "rule": "8 consecutive one side of center"})
        else:
            rl = 1
    # EWMA — catches small sustained drift the raw chart misses
    if sigma > 0:
        z, ew = center, []
        for x in v:
            z = ewma_lambda * x + (1 - ewma_lambda) * z
            ew.append(z)
        ew_sigma = sigma * np.sqrt(ewma_lambda / (2 - ewma_lambda))
        for i in range(b, n):
            if abs(ew[i] - center) > k * ew_sigma and abs(ew[i] - center) > min_shift:
                flags.append({"run": i, "value": float(ew[i]), "rule": f"EWMA beyond {k:g}σ"})

    post = sorted({f["run"] for f in flags if f["run"] >= b})
    if post and sigma > 0:
        # S1/S2: the combined SPC rules compound into a ~10% false-alarm rate on a STABLE process, with weak
        # power for small drift — disclose it so a single flag isn't over-trusted (and the anchor isn't either).
        warnings.append("drift_false_alarm_rate: the combined SPC rules (beyond-kσ + Western-Electric 8-run + "
                        "EWMA) have a ~10% false-positive rate per assessment on a genuinely STABLE process (the "
                        "rules compound) and only ~30-45% power for sub-1.5σ drift. A single DRIFT flag is a SIGNAL "
                        f"TO INVESTIGATE, not proof — confirm with more runs before re-adjudicating, and treat "
                        f"first_drift_run (run {post[0]}) as a CANDIDATE anchor, not a certainty.")
    return StabilityReport(
        in_control=(len(post) == 0),
        center=center, sigma=sigma, ucl=ucl, lcl=lcl, baseline_n=b,
        flags=sorted(flags, key=lambda f: f["run"]),
        first_drift_run=(post[0] if post else None),
        warnings=warnings, n_runs=n, trend=_trend)
