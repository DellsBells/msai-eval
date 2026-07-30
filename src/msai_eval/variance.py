"""Variance components (Gage R&R) — done the correct way, with honesty flags.

This is the "what share of my score variance is real item difference vs.
measurement noise" decomposition. It is only valid on a balanced, replicated,
complete design. When the design can't support it, this module says so and
returns None rather than fabricating a clean number (the failure mode of the
original engine).

KEY HONESTY GUARDS this fixes vs. naive Gage R&R:
  * Deterministic judges (temperature 0): within-cell variance is exactly 0, so
    repeatability looks "perfect". That is the gauge being FROZEN, not
    characterized. We detect it and flag it instead of reporting EV=0 as a pass.
  * The %GRR-vs-total-variation number is selection-sensitive: it shrinks just by
    feeding in more spread-out items. We report it labeled as such, with the
    AIAG-convention advisory grade printed by default; supply your own thresholds to override it.

Field grounding (private practitioner corpus, not redistributed here): qualify the measurement
system before trusting any result it produces. (No verbatim practitioner claim covers ndc anywhere
in the corpus, so ndc is grounded at principle level only — and demoted to advisory here.)
Clause-level grounding: docs/SPEC_GROUNDING.md.
"""
from __future__ import annotations
import numpy as np


def variance_components(ds) -> dict | None:
    """ds: msai_eval.data.Dataset. Requires balanced replicates + complete matrix.

    Two-way crossed random-effects ANOVA (items x judges x replicate trials):
        sigma2_repeat       = MS_error
        sigma2_interaction  = (MS_int - MS_error) / r
        sigma2_judge(repro) = (MS_judge - MS_int) / (n_items * r)
        sigma2_item(part)   = (MS_item - MS_int) / (n_judges * r)
    GRR = repeat + interaction + judge ; TV = GRR + item.
    """
    if not ds.balanced_replicates:
        return None

    n = ds.n_items
    k = ds.n_judges
    r = len(ds.cells[0][0])

    cube = np.array([[ds.cells[i][j] for j in range(k)] for i in range(n)], dtype=float)
    grand = cube.mean()
    item_means = cube.mean(axis=(1, 2))
    judge_means = cube.mean(axis=(0, 2))
    cell_means = cube.mean(axis=2)

    SS_item = k * r * np.sum((item_means - grand) ** 2)
    SS_judge = n * r * np.sum((judge_means - grand) ** 2)
    SS_int = r * np.sum((cell_means - item_means[:, None] - judge_means[None, :] + grand) ** 2)
    SS_total = np.sum((cube - grand) ** 2)
    SS_error = SS_total - SS_item - SS_judge - SS_int

    df_item = n - 1
    df_judge = k - 1
    df_int = df_item * df_judge
    df_error = n * k * (r - 1)
    if df_item <= 0 or df_judge <= 0:
        return None        # a single item or single judge cannot support a crossed decomposition

    MS_item = SS_item / df_item
    MS_judge = SS_judge / df_judge
    MS_int = SS_int / df_int if df_int > 0 else 0.0
    MS_error = SS_error / df_error if df_error > 0 else 0.0

    s2_repeat = max(MS_error, 0.0)
    s2_int = max((MS_int - MS_error) / r, 0.0)
    s2_judge = max((MS_judge - MS_int) / (n * r), 0.0)
    s2_item = max((MS_item - MS_int) / (k * r), 0.0)

    grr = s2_repeat + s2_int + s2_judge
    tv = grr + s2_item

    within_cell_var = cube.var(axis=2, ddof=0).mean()
    within_cell_sd = float(np.sqrt(within_cell_var))
    grr_sd_val = float(np.sqrt(grr))

    # the meaningful score step (resolution): 1 for an integer grid, else the median gap. The gate
    # judges "negligible noise" against the score's own GRAIN — NOT the score range, which is
    # dominated by real item/config separation + between-judge bias and would FALSE-freeze a real
    # gauge (the cross-track regression the review caught).
    _vals = np.unique(np.round(cube[np.isfinite(cube)].ravel(), 9))
    if _vals.size >= 2 and np.allclose(_vals, np.round(_vals)):
        score_step = 1.0
    elif _vals.size >= 2:
        _g = np.diff(_vals); _g = _g[_g > 1e-9]
        score_step = float(np.median(_g)) if _g.size else 1.0
    else:
        score_step = 1.0

    flags = []
    # FROZEN GAUGE = no resolvable measurement noise at all (GRR ~ 0), so no guard band can be formed.
    # Gated on the GAUGE'S OWN noise vs the score step: a panel with real REPRODUCIBILITY (judges
    # genuinely disagree) is NOT frozen even if each judge is internally deterministic.
    # ABSOLUTE FLOOR (1e-6): on a CONTINUOUS frozen gauge, score_step collapses to the float-noise floor
    # (~1e-9), which would sink 1e-3*score_step BELOW grr_sd's own float residue (~1e-8) and mis-read the
    # frozen gauge as a real one (audit V1). A grr_sd below 1e-6 score points is frozen for any real rubric;
    # a genuine gauge's noise (~0.01+) is orders of magnitude above it, so this can't false-freeze.
    deterministic = bool(grr < 1e-30 or grr_sd_val < max(1e-3 * score_step, 1e-6))
    if deterministic:
        flags.append(
            "frozen_gauge: GRR ~ 0 — the measurement system shows no resolvable noise (temperature 0, or "
            "a deterministic task with no between-judge spread either). It cannot form a guard band, so "
            "differences cannot be certified. Use a task with genuine variation at temperature > 0."
        )
    elif within_cell_var < 1e-12 or within_cell_sd < 1e-3 * score_step:
        flags.append(
            "repeatability_unmeasured: within-cell variance is ~0 (temperature 0 / deterministic per cell), "
            "but the gauge's REPRODUCIBILITY is measured — this does NOT disqualify the gauge for resolving "
            "config differences; add temperature>0 trials to also size repeatability."
        )
    truncated = any(x < 0 for x in [(MS_int - MS_error), (MS_judge - MS_int), (MS_item - MS_int)])
    if truncated:
        flags.append(
            "negative_variance_truncated: a variance component came out negative and was "
            "clamped to 0. This is a DIAGNOSTIC that the model/data are problematic, not a clean result."
        )

    msi = 100.0 * np.sqrt(grr) / np.sqrt(tv) if tv > 0 else float("nan")
    pct_contrib_grr = 100.0 * grr / tv if tv > 0 else float("nan")
    ndc = float(np.floor(1.41 * np.sqrt(s2_item) / np.sqrt(grr))) if grr > 0 else float("inf")

    return {
        "sigma2_item": s2_item,
        "sigma2_judge": s2_judge,
        "sigma2_interaction": s2_int,
        "sigma2_repeat": s2_repeat,
        "grr_sd": float(np.sqrt(grr)),
        "tv_sd": float(np.sqrt(tv)),
        "measurement_noise_share_pct": float(pct_contrib_grr),   # variance-scale, intuitive
        "msi_grr_pct": float(msi),                               # SD-scale, the classic %GRR
        "ndc": ndc,
        "deterministic": deterministic,
        "flags": flags,
    }


# %GRR sampling-band caveat. The synthetic gauge-block n-sweep found %GRR's 90% sampling interval is
# ~±13-16pp across the ENTIRE practical LLM-judge range (14-45 items, 5-12 judges) and does NOT materially
# tighten with more items/judges — it is a coarse indicator, not a precise percentage, and this is NOT a
# small-panel artifact that resolves with more data. So a quoted %GRR can be off by a full acceptance
# category. gauge_judgement annotates its %GRR verdict with this, and flags when the band straddles 10%/30%.
_GRR_SAMPLING_PP = 15.0   # representative 90% half-width (n-sweep; persists across 14-45 items / 5-12 judges)


def _pct_grr_caveat(pct_grr):
    """Returns (caveat_text, category_ambiguous). The band is a characterized n-sweep figure (a
    representative variance split), not a universal constant — stated as ~±15pp, not exact."""
    band = _GRR_SAMPLING_PP
    txt = (f"%GRR carries a ~±{band:.0f}pp 90% sampling band at realistic LLM-judge panel sizes (synthetic "
           "gauge-block n-sweep; it does NOT tighten materially with more items/judges in range) — treat it "
           "as a coarse indicator, not an exact percentage.")
    ambiguous = (pct_grr - band) < 10 < (pct_grr + band) or (pct_grr - band) < 30 < (pct_grr + band)
    if ambiguous:
        txt += (" That band CROSSES an acceptance boundary (10% / 30%) at this value, so the accept/reject "
                "CATEGORY is not resolvable at this panel size — lean on the guard band and the per-config "
                "verdicts, not %GRR, for the decision.")
    return txt, ambiguous


_NDC_SAMPLING_BAND = 3   # ndc's 90% spread is ~several categories at LLM-judge panel sizes (n-sweep; ~1-13 at 2 judges)


def _ndc_caveat(ndc):
    """Returns (caveat_text, ambiguous). ndc is a noisy integer at these panel sizes — same sampling-band
    honesty as %GRR (this was an undisclosed overclaim: ndc carried no caveat where %GRR does)."""
    if ndc is None or not np.isfinite(ndc):
        return None, False
    txt = (f"ndc = {ndc:g} carries a ~±{_NDC_SAMPLING_BAND}-category 90% sampling band at realistic LLM-judge "
           "panel sizes (synthetic gauge-block n-sweep — ndc swings widely seed-to-seed on IDENTICAL truth, "
           "e.g. ~1-13 at 2 judges). Read it as a coarse 'can this gauge distinguish parts at all' indicator "
           "(ndc < 2 = no), NOT a precise count.")
    ambiguous = (ndc - _NDC_SAMPLING_BAND) < 5 < (ndc + _NDC_SAMPLING_BAND)
    if ambiguous:
        txt += (" That band CROSSES the ndc>=5 adequacy cutoff at this value, so the accept/reject category is "
                "not resolvable from ndc at this panel size — lean on %GRR and the guard band, not ndc.")
    return txt, ambiguous


def gauge_judgement(var):
    """AIAG gauge-acceptance verdict from %GRR (SD-scale) and ndc — the field "judgement
    box" practitioners use to accept/reject a measurement system — with the item-selection
    caveat baked in:

        %GRR < 10%   & ndc >= 5  ->  FULLY ACCEPTABLE
        %GRR 10-30%  & ndc >= 5  ->  ACCEPTABLE (conditional / sign-off)
        %GRR > 30%               ->  NOT ACCEPTABLE (gauge noise too high)
        ndc < 5                  ->  NOT ACCEPTABLE by ndc -- BUT if %GRR passes, the likely
                                     cause is items too clustered to span the range, NOT a bad
                                     gauge (ndc is selection-sensitive); re-run with
                                     representative items before rejecting the gauge.

    Returns None when there's no variance estimate to judge.
    """
    if not var:
        return None
    if var.get("deterministic"):
        return {"verdict": "INDETERMINATE — frozen gauge",
                "reason": ("within-cell variance is ~0 (temperature 0, or an intrinsically deterministic "
                           "task): no repeatability was exercised, so %GRR~0 is degenerate, not a pass. Needs "
                           "a task with genuine run-to-run variation at temperature>0 to size the gauge.")}
    pct_grr = var.get("msi_grr_pct")
    ndc = var.get("ndc")
    if pct_grr is None or (isinstance(pct_grr, float) and np.isnan(pct_grr)):
        return {"verdict": "INDETERMINATE",
                "reason": "%GRR not estimable — need replicate measurements (trials) to size the gauge noise."}
    ndc_inf = isinstance(ndc, float) and np.isinf(ndc)
    if ndc_inf:                                    # grr ~ 0 -> no measurable gauge noise = degenerate, not a pass
        return {"verdict": "INDETERMINATE — frozen gauge",
                "reason": ("ndc is infinite because GRR ~ 0 — the gauge shows no measurable noise (frozen / "
                           "deterministic). %GRR~0 is degenerate; exercise real repeatability before judging it.")}
    ndc_ok = (ndc is not None and ndc >= 5)
    ndc_s = f"{ndc:g}"
    _grr_caveat, _grr_ambiguous = _pct_grr_caveat(float(pct_grr))
    _ndc_cav, _ndc_ambiguous = _ndc_caveat(ndc)
    base = {"pct_grr": round(float(pct_grr), 1), "ndc": ndc,
            "pct_grr_caveat": _grr_caveat, "category_ambiguous": bool(_grr_ambiguous or _ndc_ambiguous),
            "ndc_caveat": _ndc_cav, "ndc_ambiguous": _ndc_ambiguous}
    if pct_grr > 30:
        return {**base, "verdict": "NOT ACCEPTABLE", "likely_item_selection_possible": True,
                "reason": (f"%GRR = {pct_grr:.1f}% exceeds 30%. This is EITHER genuine gauge noise OR clustered "
                           "items: %GRR = gauge SD / total variation, so a small item-to-item signal inflates it "
                           f"even with a clean gauge (absolute gauge SD = {var.get('grr_sd', float('nan')):.3g} — "
                           "check it against the score scale, and confirm items span the range, before rejecting "
                           "the gauge).")}
    if not ndc_ok:
        return {**base, "verdict": "NOT ACCEPTABLE (ndc < 5)", "likely_item_selection": True,
                "reason": (f"ndc = {ndc_s} (< 5), but %GRR = {pct_grr:.1f}% is acceptable, so the gauge noise is "
                           "fine. ndc<5 with a passing %GRR usually means the ITEMS were too clustered to span "
                           "the range (ndc is selection-sensitive), not a bad gauge — re-run with items "
                           "spanning the range before rejecting the gauge.")}
    if pct_grr < 10:
        return {**base, "verdict": "FULLY ACCEPTABLE",
                "reason": f"%GRR = {pct_grr:.1f}% (< 10%) and ndc = {ndc_s} (>= 5)."}
    return {**base, "verdict": "ACCEPTABLE — CONDITIONAL",
            "reason": (f"%GRR = {pct_grr:.1f}% (10-30%) and ndc = {ndc_s} (>= 5) — acceptable for the intended "
                       "use with sign-off, not unconditionally.")}
