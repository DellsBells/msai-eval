"""compare() — the acceptance-test verb: is a config worse than the baseline,
beyond what the gauge can even resolve?

reliability() asks "do my judges agree / how much of the spread is noise?".
compare() asks the next question down the pipe: given a *fixed set of treatments*
(e.g. compression configs {FP16, Q4, Q2, delta-KV, ...}) each scored by a held
judge panel, is each one's quality different from the baseline by more than the
measurement system's own noise?

This is a measurement decision rule with guard-banding — the metrology of
conformity assessment (ISO/IEC 17025 §7.8, JCGM 106) applied to LLM-judge scores.
It is the right tool *because* the configs are hand-picked treatments, not a
random sample of parts: %GRR/ndc are selection-sensitive under hand-picked parts,
so a direct pairwise mean-difference-with-uncertainty is the honest instrument.

ORDINAL vs INTERVAL (documented so reviewers don't re-litigate the deliberate split): the GAUGE layer —
the crossed-ANOVA variance components, grr_sd, the guard band U, %GRR, ndc — is interval-by-construction and
runs IDENTICALLY whether level=ordinal or interval (it treats rubric points as equal-interval). The
ASSUMPTION-FREE layer is the rank tools: Cliff's δ (the endorsed effect size) and ordinal Krippendorff α. On
ordinal data a directional verdict the rank effect contradicts in SIGN is WITHHELD (below). KNOWN OPEN GAP
(cross-lineage review, see docs/REVIEW_SYNTHESIS.md): the |Δ| > guard_band MAGNITUDE comparison has no
rank-based counterpart yet — it guards direction ordinally but magnitude only on the interval scale.

Two gates, kept separate on purpose:
  * resolvable    — the CI on the difference excludes 0 (statistically distinct),
                    after correcting for the family of configs-vs-baseline tests.
  * beyond_gauge  — |difference| exceeds a guard band (default 2 x gauge-noise SD):
                    the difference is bigger than the measurement system's own
                    resolution. A difference can be statistically real yet below
                    the gauge's resolution; both are reported, never merged.

Honesty guards (why this isn't just a t-test):
  * Self-checks the gauge first. If the gauge is frozen (temperature 0, degenerate
    repeatability) or has no measurable resolution (no balanced replicates → no guard
    band), every verdict is marked provisional and the reason is stated — it will not
    hand back a confident delta from a gauge that can't support one. ndc is reported as
    ADVISORY CONTEXT ONLY and does NOT gate: because the configs are hand-picked
    treatments (not a random part sample), ndc is selection-sensitive — it scales with
    how far apart the configs happen to be — so the gauge's real resolution is the
    guard band, not ndc.
  * Corrects for multiple comparisons (Holm) across the configs-vs-baseline family,
    so you don't "find" a real drop just by running enough configs.
  * On ordinal scores it reports Cliff's delta (rank-based) next to the mean
    difference, because a mean on a 1-5 scale silently assumes interval spacing.
  * The guard band is the gauge DISCRIMINATION band (Band B), NOT the uncertainty of
    the estimated mean difference. It is a PER-USE expanded uncertainty built on the
    gauge's single-measurement noise — U = k·sqrt(repeatability² + interaction² +
    quantization²), floored at 2·GRR_SD (AIAG MSA ndc family; JCGM 106 §8.3.3.2 w=rU
    guard-band FORM with U = per-use gauge uncertainty). Because it is built on
    single-use gauge noise (grr, not grr/√N), it does NOT shrink as you add trials,
    judges, or items: it is a fixed property of the measurement system in its declared
    use, the width below which this gauge cannot DISCRIMINATE two configs no matter how
    many times you re-read them. That is the real-metrology decision rule: a conformity
    statement "cannot be made fully without accounting for measurement uncertainty"
    (Q-Cast ep142, ep310), and U is the root-sum-square of the gauge's error sources —
    the "five R's" (ChatNAPT ep18-zumbrun, Q-Cast ep222). u_ref is excluded here: it is
    common-mode in a config-vs-baseline delta and cancels.
  * The uncertainty of the ESTIMATE — Band A, k·u(Δ̂), the ± on the mean difference we
    actually measured (VIM/JCGM 200 §2.47 metrological compatibility) — is a SEPARATE
    quantity that DOES shrink with study size (√N). It is disclosed beside the gate as
    the bootstrap CI half-width, never as the gate. "Statistically real but below
    resolution" is the honest state where Band A excludes 0 (the estimate is resolved)
    yet |Δ| < Band B (the gauge still cannot discriminate the two in a single use) —
    coherent, not a contradiction: a caliper can establish a 0.02 mm mean difference
    from 1000 readings and still be unable to discriminate those two parts in the hand.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math
import numpy as np

from .data import normalize
from .variance import variance_components
from .uncertainty import uncertainty_budget
from .resolution import four_state, BAND_A_BASIS, BAND_B_BASIS


def _cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    """Rank-based effect size in [-1, 1]: P(x>y) - P(x<y). Assumption-free for ordinal."""
    if len(x) == 0 or len(y) == 0:
        return float("nan")
    gt = sum(int(np.sum(xi > y)) for xi in x)
    lt = sum(int(np.sum(xi < y)) for xi in x)
    return (gt - lt) / (len(x) * len(y))


def _within_judge_cliffs_delta(cells_x, cells_y) -> float:
    """REV-010: Cliff's delta paired WITHIN each judge, then averaged across judges.

    The pooled form ``_cliffs_delta(all_scores(i), all_scores(bi))`` compares every score of
    config i against every score of the baseline, INCLUDING cross-judge pairs. A judge who
    rates on a high absolute level versus one who rates low then injects the judge main-effect
    into the effect size — a level shift the guard band already removes, so it does not belong
    in the direction/magnitude the verdict trusts. Comparing only same-judge pairs cancels that
    main effect: each judge votes on its own scale and we average the per-judge verdicts.

    Judges with an empty cell on either side are skipped; returns nan only if no judge has data
    on both sides. Reproduces the pooled value exactly when every judge sits at the same level.
    """
    deltas = [_cliffs_delta(cx, cy)
              for cx, cy in zip(cells_x, cells_y) if cx.size and cy.size]
    return float(np.mean(deltas)) if deltas else float("nan")


def _holm(pvals: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, returned in the original order."""
    m = len(pvals)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * pvals[idx])
        adj[idx] = min(running, 1.0)
    return adj


def _verdict(c: dict, gauge: dict, level: str = "interval") -> str:
    if not gauge["qualified"]:
        return "gauge unqualified — provisional"
    direction = "drop" if c["delta"] < 0 else "gain"
    if not c["significant_adj"]:
        # A non-significant Δ reads "within noise" ONLY if it is also BELOW the guard band — that
        # is the promise the notes make ("within noise" == below THIS gauge's resolution). If |Δ|
        # EXCEEDS the guard band but the CI still includes 0, it is NOT sub-resolution; it is
        # under-powered, and mislabeling it "within noise" would falsely claim the configs are
        # indistinguishable. (REV-002.)
        if c.get("beyond_gauge") is True:
            return ("not statistically resolvable (|Δ| exceeds the guard band but the CI includes 0 "
                    "— under-powered; add trials / judges / items)")
        return "within noise (indistinguishable on this gauge)"
    # Mean Δ vs rank effect. On ordinal/nominal data the mean assumes interval spacing the
    # scale doesn't have, so the direction of the mean Δ can disagree with Cliff's δ (the
    # assumption-free rank effect the notes tell you to trust) — e.g. a few extreme low
    # scores drag the mean negative while most ratings rank the config HIGHER. If a confident
    # directional verdict is about to be asserted but Cliff's δ points the opposite way with
    # real magnitude, the direction is not trustworthy: WITHHOLD it rather than print a
    # drop/gain the endorsed effect size contradicts. (within-noise makes no directional
    # claim, so this only guards the significant path.)
    cd = c.get("cliffs_delta")
    if level in ("ordinal", "nominal") and cd is not None and not math.isnan(cd) \
            and abs(cd) >= 0.1 and (cd * c["delta"] < 0):
        return ("statistically real difference, but mean Δ and rank-effect (Cliff's δ) DISAGREE "
                "in sign — interval-spacing assumption suspect; direction not trustworthy")
    # LOAD-BEARING DEFENSE — do not delete as "unreachable". Under the current gate
    # (qualified requires guard_band is not None) a qualified gauge always has a finite
    # guard band, so beyond_gauge is never None on the qualified path and this branch is
    # belt-and-suspenders today. KEEP it: if the qualification rule ever changes, removing
    # this branch lets a beyond_gauge=None case fall PAST the `is False` check into the
    # final "REAL drop" return and manufacture a confident false verdict. The unknown case
    # must fail toward the conservative verdict: guard-banding applied to the control flow.
    if c["beyond_gauge"] is None:
        return f"statistically real {direction} (gauge resolution unknown — no replicates)"
    if c["beyond_gauge"] is False:
        return f"statistically real {direction}, but BELOW gauge resolution"
    # MAGNITUDE counterpart to the direction WITHHOLD above (cross-lineage review gap, docs/REVIEW_SYNTHESIS.md):
    # |Δ| > guard_band is an INTERVAL comparison. On ordinal/nominal, if Δ clears the interval band but the
    # rank effect is NEGLIGIBLE (|Cliff's δ| < 0.147, the canonical negligible cutoff), the "resolved" call
    # rests entirely on the interval-spacing assumption — a few non-uniform rubric steps can clear the band
    # while the ranks barely move. Downgrade to unresolved-on-rank rather than assert REAL. Conservative: this
    # can only UN-resolve, never fabricate a REAL (one-sided, like the direction guard).
    if level in ("ordinal", "nominal") and cd is not None and not math.isnan(cd) and abs(cd) < 0.147:
        return (f"statistically real {direction} beyond the interval guard band, but the rank effect "
                f"(Cliff's δ={cd:+.2f}) is NEGLIGIBLE — resolution may be an interval-spacing artifact; "
                "treat as unresolved on the rank scale")
    return f"REAL {direction} (beyond gauge resolution)"


@dataclass
class ComparisonReport:
    baseline: str
    baseline_mean: float
    level: str
    gauge: dict                       # ndc, grr_sd, guard_band, qualified, warnings
    comparisons: dict                 # config -> result dict
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "baseline": self.baseline, "baseline_mean": self.baseline_mean,
            "level": self.level, "gauge": self.gauge,
            "comparisons": self.comparisons, "notes": self.notes,
        }

    def summary(self) -> str:
        def f(x, nd=3):
            if x is None or (isinstance(x, float) and (math.isnan(x))):
                return "n/a"
            if isinstance(x, float) and math.isinf(x):
                return "inf"
            return f"{x:.{nd}f}"
        L = []
        L.append("=" * 70)
        L.append("  MSAI — config-vs-baseline acceptance test")
        L.append("=" * 70)
        L.append(f"  baseline: {self.baseline!r}  (mean quality = {f(self.baseline_mean, 2)})")
        g = self.gauge
        L.append("")
        L.append("  GAUGE (can the measurement system even support this comparison?)")
        L.append(f"    ndc (distinct levels resolvable) = {f(g['ndc'], 0)}")
        L.append(f"    gauge-noise SD (GRR)             = {f(g['grr_sd'])}")
        L.append(f"    discrimination band (Band B: per-use resolution, floored at 2·GRR SD; "
                 f"does NOT shrink with N) = {f(g['guard_band'])}")
        if g.get("declared_use"):
            L.append(f"       declared use: {g['declared_use']}  (Band B is certified for this use)")
        rb = g.get("resolution_budget")
        if rb and rb.get("dominant"):
            L.append(f"       dominant resolution source: {rb['dominant']['source']} "
                     f"({rb['dominant'].get('pct', 0):.0f}%) -> lever: {rb.get('lever', '')}")
        L.append(f"    -> gauge {'QUALIFIED' if g['qualified'] else 'NOT QUALIFIED'}")
        for w in g["warnings"]:
            L.append(f"       [!] {w}")
        L.append("")
        L.append("  COMPARISONS (vs baseline; Holm-corrected across the family)")
        for name, c in self.comparisons.items():
            lo, hi = c["ci"]
            L.append(f"    {str(name):<16s} Δ = {c['delta']:+.3f}  "
                     f"[95% CI {f(lo)}, {f(hi)}]")
            eU = c.get("estimate_U")
            if eU is not None and not (isinstance(eU, float) and math.isnan(eU)):
                # Band A: uncertainty of the ESTIMATE (shrinks with N) — disclosed, NOT the gate.
                a_res = "excludes 0" if (lo > 0 or hi < 0) else "includes 0"
                L.append(f"    {'':<16s} Band A (est. mean-diff U ≈ ±{f(eU)}, shrinks with N; "
                         f"VIM §2.47) {a_res}")
            extra = f"Holm p={f(c['p_holm'])}"
            if self.level in ("ordinal", "nominal"):
                extra += f"  Cliff's δ={f(c['cliffs_delta'], 2)}"
            L.append(f"    {'':<16s} {extra}")
            L.append(f"    {'':<16s} -> {c['verdict']}")
        L.append("")
        L.append("  SCOPE")
        for n in self.notes:
            L.append(f"    {n}")
        L.append("=" * 70)
        text = "\n".join(L)
        try:
            print(text)
        except UnicodeEncodeError:           # non-UTF-8 stdout (e.g. Windows cp1252): don't crash on Δ/δ/σ
            print(text.encode("ascii", "replace").decode("ascii"))
        return text


def compare(data, baseline, level: str = "ordinal", guard_k: float = 2.0,
            min_ndc: int = 5, alpha: float = 0.05, n_boot: int = 2000,
            seed: int = 0, reference=None, resolution=None,
            declared_use: str = "single-panel, single-pass") -> ComparisonReport:
    """Compare each config's quality to a baseline config, gated by gauge noise.

    `data` is the same shape reliability() takes, but here the ITEMS are the
    configs/treatments and `baseline` names the reference config. Judges are the
    held panel; repeat trials (temperature>0) feed the gauge-noise estimate.

    `resolution` is the score-quantization step (the rubric increment, e.g. 1.0 for a
    1-5 scale). For ordinal/nominal scores that are NOT on an integer grid, pass it
    explicitly: otherwise the inferred step is the smallest observed gap, which can
    collapse toward 0 on jittered/continuous scores and falsely qualify a near-frozen
    gauge (a sub-rubric Δ then reads 'REAL'). compare() warns when this risk is present.

    `declared_use` names the certified usage protocol the discrimination band (Band B) is
    valid for. The default — "single-panel, single-pass" — is the conservative floor: Band B
    is the width below which ONE run of this gauge cannot discriminate two configs. It is a
    LABEL that travels onto the outputs (it does not change the numbers): averaging many
    independent passes would shrink the ESTIMATE uncertainty (Band A), never this per-use
    discrimination band, so a tighter declared use must be earned by a re-characterized gauge,
    not asserted here.
    """
    if level == "nominal":
        raise ValueError(
            "compare() needs ordinal or interval quality scores — you cannot rank "
            "configs 'better/worse' on nominal category labels. Use reliability(level='nominal') "
            "for categorical agreement instead."
        )
    ds = normalize(data)
    items = list(ds.items)
    if baseline not in items:
        raise ValueError(f"baseline {baseline!r} is not one of the configs: {items}")
    bi = items.index(baseline)
    k = ds.n_judges
    if k < 2:
        # still runnable, but no reproducibility -> flag hard
        pass

    # precompute trial arrays per cell
    cell = [[np.asarray(ds.cells[i][j], dtype=float) for j in range(k)] for i in range(ds.n_items)]

    def all_scores(i):
        parts = [cell[i][j] for j in range(k) if cell[i][j].size]
        return np.concatenate(parts) if parts else np.array([])

    def config_mean(i, jidx=None, rng=None):
        js = range(k) if jidx is None else jidx
        vals = []
        for j in js:
            c = cell[i][j]
            if c.size == 0:
                continue
            if rng is not None and c.size > 1:
                vals.append(c[rng.integers(0, c.size, c.size)])
            else:
                vals.append(c)
        return float(np.concatenate(vals).mean()) if vals else float("nan")

    base_mean = config_mean(bi)

    # ---- gauge self-check ----
    # GAUGE BASIS (audit fix): grr_sd / the guard band / the frozen-gauge detector must be decomposed on the
    # UNIT(item/product) x judge x trial structure, so genuine between-UNIT signal lands in item variance
    # (EXCLUDED from GRR) and only between-judge + re-scoring remain as gauge noise. When rows carry a `unit`
    # field distinct from the treatment, decompose on the (treatment|unit) composite item. Otherwise fall back
    # to treating each within-cell score as a replicate trial — correct ONLY if the cell is genuine repeats; if
    # it silently pools distinct units (products), the band inflates (product spread mislabeled as
    # repeatability) and the frozen detector is defeated. Pass a per-row `unit` to separate them.
    # SCOPE of consequence (c): routing the frozen detector to this unit-level view catches an EXACTLY-frozen
    # gauge (grr=0 -> qualified=False). A NEAR-frozen gauge (tiny nonzero noise on a continuous grid) can
    # still slip because variance.py's deterministic gate uses a score_step-relative threshold that collapses
    # on near-frozen continuous data — tracked separately as the frozen-continuous finding; (c) is fully
    # closed only WITH that fix. (My commit f9aa72b overstated (c) as fixed; this is the correction.)
    _rows = data if (isinstance(data, list) and data and isinstance(data[0], dict)) else None
    _has_unit = bool(_rows) and all(("unit" in r and r.get("unit") is not None) for r in _rows)
    if _has_unit:
        _SEP = "\x1f"
        _budget_data = [{"item": f"{r['item']}{_SEP}{r['unit']}", "judge": r["judge"], "score": r["score"]}
                        for r in _rows]
        vc = variance_components(normalize(_budget_data))
    else:
        _budget_data = data
        vc = variance_components(ds)
    gauge = {"ndc": None, "grr_sd": None, "guard_band": None, "qualified": False,
             "resolution_budget": None, "reference_fitness": None, "declared_use": declared_use,
             "warnings": []}
    if not _has_unit:
        gauge["warnings"].append(
            "gauge_from_pooled_cells: no per-row `unit` factor was supplied, so the gauge treats each "
            "within-cell score as a replicate TRIAL. If the cell actually pools distinct items/products, the "
            "guard band is inflated (between-product spread is mislabeled as repeatability) and a frozen gauge "
            "can wrongly qualify — pass a `unit` field per row to separate item signal from gauge noise.")
    if k < 2:
        gauge["warnings"].append("single_judge: no reproducibility — between-judge noise is unmeasured; "
                                 "differences may be pure judge idiosyncrasy.")
    elif k < 4:
        gauge["warnings"].append(
            f"few_judges_coarse_ci: only {k} judges — the judge-resample bootstrap has very few "
            f"distinct resamples (k={k} gives {2*k-1}), so the CIs are granular and should NOT be "
            "over-read. Trust the guard band and Cliff's delta over CI width; prefer >=5 judges.")
    _res_untrusted = False
    if level in ("ordinal", "nominal") and resolution is None:
        _allv = [v for i in range(ds.n_items) for j in range(k) for v in ds.cells[i][j] if v is not None]
        if _allv and any(abs(v - round(v)) > 1e-9 for v in _allv):
            _res_untrusted = True
            gauge["warnings"].append(
                "fractional_ordinal_no_resolution: ordinal scores are not on an integer rubric grid and no "
                "resolution= was supplied, so the score-quantization step is UNKNOWN — auto-inference (even a "
                "modal gap, or a range-relative frozen gate) is gameable on jittered/tiny-scale scores and can "
                "falsely qualify a near-frozen gauge. The guard band is therefore WITHHELD and verdicts are "
                "provisional until you pass resolution=<rubric step> (e.g. 1.0 for a 1-5 scale, or the true "
                "scale granularity).")
    if vc:
        gauge["ndc"] = vc["ndc"]
        gauge["grr_sd"] = vc["grr_sd"]
        for _f in (vc.get("flags") or []):                       # surface the honest within-cell~0 caveat:
            if "repeatability_unmeasured" in _f:                 # judges self-consistent on repeats, so
                gauge["warnings"].append(_f)                     # repeatability wasn't exercised — does NOT disqualify (gauge still qualifies on reproducibility)
        # DISCRIMINATION BAND (Band B) = a PER-USE expanded uncertainty (uncertainty_budget), NOT the
        # uncertainty of the estimated mean difference and NOT the bare guard_k*grr_sd. U = k_WS*sqrt(
        # grr^2 + Δ²/12 + u_ref²) is built on single-USE gauge noise (grr, not grr/√N), so it does NOT
        # shrink with N — it is the fixed resolution floor of the gauge in its declared use (AIAG MSA ndc
        # family; JCGM 106 §8.3.3.2 w=rU form with U = per-use gauge uncertainty). It folds in the score-
        # quantization floor and honest small-panel (Welch-Satterthwaite) coverage that 2*grr_sd omits —
        # both omissions make the bare band too NARROW, overclaiming resolution (worst exactly on sharp
        # gauges / small panels chasing sub-point deltas). The uncertainty of the ESTIMATE (Band A, k·u(Δ̂),
        # the CI half-width in comparisons[*]["estimate_U"]) shrinks with N and is disclosed separately —
        # it is never this gate. Real-metrology grounding: a conformity
        # statement "cannot be made fully without accounting for measurement uncertainty"
        # (Q-Cast ep142, ep310); U is the RSS of the gauge's error sources — the "five R's"
        # repeatability/reproducibility/resolution/reference (ChatNAPT ep18-zumbrun, Q-Cast ep222).
        # TWO common-mode terms cancel in a config-vs-baseline DELTA and must NOT be in its band:
        #   (1) u_ref — the reference's own uncertainty (NO reference is passed here ON PURPOSE).
        #   (2) the judge MAIN effect — each appraiser's overall scale LEVEL. The same judge rates both
        #       config and baseline, so the level is common-mode in the within-judge difference and cancels
        #       EXACTLY (identical algebra to u_ref). Carrying it would inflate the band with an error the
        #       delta does not incur — a panel that AGREES on every gap but rates on different absolute
        #       levels would be wrongly judged coarse (this is the level-shift finding from the keystone
        #       panel: judges agreed on Δ but gemma~2.4 vs coder~3.5 in level). So the delta band's gauge
        #       noise is the DELTA basis: grr_sd_delta = sqrt(repeatability + judge×item INTERACTION), and
        #       the GUM U is built with measurand="delta" (drops the judge main-effect from reproducibility,
        #       keeps the interaction = real gap-disagreement). Valid because vc exists ONLY on a balanced
        #       crossed design (every judge rated every config incl. baseline). Scoped to the delta band
        #       ONLY: gauge["grr_sd"] (display / reference.fitness) keeps the FULL appraiser noise. Both
        #       widen the band only for an absolute-reference/threshold comparison — conformity's job.
        # Guard A: keyed on grr_sd>0, so a frozen-perfect / no-replicate gauge (Type-A noise never measured)
        # stays guard_band=None and unqualified — U is finite from quantization alone and must NOT qualify it.
        # Guard B: floored at guard_k*grr_sd_delta so U is never less conservative than the bare delta band.
        if vc["grr_sd"] > 0 and not _res_untrusted:
            _s2_repeat = max(0.0, vc.get("sigma2_repeat", 0.0))
            _s2_int = max(0.0, vc.get("sigma2_interaction", 0.0))
            _s2_judge = max(0.0, vc.get("sigma2_judge", 0.0))
            grr_sd_delta = float(np.sqrt(_s2_repeat + _s2_int))
            _ub = uncertainty_budget(_budget_data, level=level, resolution=resolution, measurand="delta")  # GUM budget for the DELTA: judge level cancels, u_ref omitted; resolution= forwards the rubric step
            gauge["guard_band"] = max(_ub.U, guard_k * grr_sd_delta)
            gauge["resolution_budget"] = {"U": _ub.U, "u_c": _ub.u_c, "k": _ub.k,
                                          "dominant": _ub.dominant, "lever": _ub._lever(),
                                          "components": _ub.components, "warnings": _ub.warnings,
                                          "grr_sd_delta": grr_sd_delta, "grr_sd_full": vc["grr_sd"]}
            # Guard C (disclosure): when the appraiser LEVEL dominated the raw gauge noise, the delta band is
            # materially tighter than the absolute-noise band would be — say so, and warn it is delta-only.
            if grr_sd_delta < 0.7 * vc["grr_sd"]:
                gauge["warnings"].append(
                    f"delta_band_level_centered: appraiser LEVEL spread (sqrt(s2_judge)="
                    f"{float(np.sqrt(_s2_judge)):.4g}) dominated the raw gauge noise (grr_sd={vc['grr_sd']:.4g}); "
                    f"it is common-mode in the config-vs-baseline delta and was removed, so the guard band uses "
                    f"gap-disagreement noise only (grr_sd_delta={grr_sd_delta:.4g}) and is correspondingly "
                    "tighter. Correct for a DELTA — do NOT read this band as an absolute-score resolution.")
        else:
            gauge["guard_band"] = None
        if vc.get("deterministic"):
            gauge["warnings"].append("frozen gauge (temperature 0): repeatability is degenerate, not perfect. "
                                     "Run trials at temperature>0 with independent seeds before trusting a delta.")
        ndc = vc["ndc"]
        if ndc != float("inf") and ndc < min_ndc:
            gauge["warnings"].append(
                f"ndc={ndc:.0f} (<{min_ndc}, the AIAG adequate-gauge bar) — ADVISORY ONLY, NOT a gate. "
                "ndc is selection-sensitive: it scales with how far apart the hand-picked configs happen to "
                "be, so it under-reports when configs cluster into a few quality tiers even on a sharp gauge. "
                "The gauge's real resolution is the guard band — lean on it and the per-config verdicts, "
                "never ndc, as the accept/reject grade.")
        # Qualification keys on RESOLUTION (a finite guard band exists) + not-frozen, NOT on ndc.
        # ndc is selection-sensitive on hand-picked treatments; gating on it suppresses true findings
        # whenever configs cluster (the frontier case). The guard band = guard_k * grr_sd depends only on
        # gauge noise, so it is the honest, selection-invariant resolution criterion. The genuine
        # "can't tell" states (frozen gauge, no replicates) both drive guard_band to None and still fail here.
        gauge["qualified"] = (k >= 2) and (not vc.get("deterministic")) and (gauge["guard_band"] is not None)
        # Typed two-band view (REV-LANE #009 frozen contract; GC/1.1 Profile R cites these names).
        # band_B is gauge-level (one discrimination band per gauge); band_A (the estimate uncertainty)
        # is PER-COMPARISON and rides each comparison as `estimate_U` + a per-comparison `bands` view,
        # since every config-vs-baseline delta has its own CI half-width. Gauge-level band_A is therefore
        # None-with-pointer, never a single misleading constant.
        gauge["bands"] = {"band_A": None, "band_B": gauge["guard_band"],
                          "band_A_basis": BAND_A_BASIS, "band_B_basis": BAND_B_BASIS,
                          "declared_use": declared_use,
                          "band_A_note": "per-comparison; see comparisons[name]['estimate_U'] / ['bands']['band_A']"}
        # Optional reference precondition gate. In a config-vs-baseline comparison the reference's
        # role is NOT to widen the band (u_ref cancels) but to confirm a verdict that stands in for
        # "as good as truth" is arbitrable at all: a reference must out-resolve the gauge (the reference-adequacy ratio
        # rule; Q-Cast ep142, generalized to the full budget per ChatNAPT ep02/ep22). fitness() now
        # governs on worst-case u_ref. Surfaced as a warning; the relative verdict is unaffected.
        if reference is not None and hasattr(reference, "fitness") and gauge["grr_sd"]:
            fit = reference.fitness(gauge["grr_sd"])
            gauge["reference_fitness"] = fit
            if not str(fit.get("verdict", "")).startswith("FIT"):
                gauge["warnings"].append(
                    f"reference {fit.get('verdict', '?')} (reference-adequacy ratio {fit.get('ratio', '?')}:1): {fit.get('reason', '')} "
                    "A reading interpreted as 'config as good as truth' is not arbitrable on this reference; "
                    "the config-vs-baseline verdict itself is unaffected (u_ref is common-mode).")
    else:
        gauge["warnings"].append("no balanced replicates: the gauge-noise SD (and the resolution guard band) "
                                 "cannot be computed. Reporting statistical resolvability only — practical "
                                 "(beyond-gauge) significance is unknown. Add >=2 trials per cell to fix.")

    # ---- bootstrap pairwise deltas (resample judges paired across configs + trials) ----
    rng = np.random.default_rng(seed)
    comparisons, p_list, keys = {}, [], []
    # degenerate inputs (k=1, all-equal cells) legitimately produce empty/constant
    # arrays -> harmless nan/divide warnings; those verdicts all go provisional anyway.
    with np.errstate(divide="ignore", invalid="ignore"):
        for i, name in enumerate(items):
            if i == bi:
                continue
            d_obs = config_mean(i) - base_mean
            boot = np.empty(n_boot)
            for b in range(n_boot):
                jidx = rng.integers(0, k, k) if k >= 1 else None
                boot[b] = config_mean(i, jidx, rng) - config_mean(bi, jidx, rng)
            boot = boot[~np.isnan(boot)]
            lo, hi = (float(np.percentile(boot, 100 * alpha / 2)),
                      float(np.percentile(boot, 100 * (1 - alpha / 2)))) if boot.size else (float("nan"), float("nan"))
            # two-sided bootstrap p-value
            if boot.size:
                p = min(1.0, 2.0 * min(float(np.mean(boot <= 0)), float(np.mean(boot >= 0))))
            else:
                p = float("nan")
            # Cliff's δ is computed for ALL levels: on ordinal/nominal it gates the verdict (direction +
            # magnitude guards); on interval it is reported as a DIAGNOSTIC + powers the sign_divergence_note
            # (the verdict still trusts the mean on interval — the guards in _verdict stay level-gated).
            # REV-010: pair WITHIN each judge then average, so a judge-level shift (one judge rates high,
            # another low) cannot masquerade as an effect. Pooling across judges conflated the two.
            cd = _within_judge_cliffs_delta(cell[i], cell[bi])
            # Band A (REV-001 disclosure): k·u(Δ̂), the expanded uncertainty of the ESTIMATED mean
            # difference — the 95% bootstrap CI half-width. Shrinks with N. Disclosed beside the gate,
            # NEVER the gate (the gate is Band B, the per-use discrimination band). VIM §2.47.
            estimate_U = (hi - lo) / 2.0 if not (math.isnan(lo) or math.isnan(hi)) else float("nan")
            comparisons[name] = {"mean": config_mean(i), "delta": d_obs, "ci": (lo, hi),
                                 "resolvable_raw": bool(lo > 0 or hi < 0), "p_raw": p, "cliffs_delta": cd,
                                 "estimate_U": estimate_U}
            p_list.append(p if not math.isnan(p) else 1.0)
            keys.append(name)

    # ---- multiplicity correction + gates + verdicts ----
    adj = _holm(p_list)
    gb = gauge["guard_band"]
    for name, pa in zip(keys, adj):
        c = comparisons[name]
        c["p_holm"] = pa
        c["significant_adj"] = (pa < alpha) and c["resolvable_raw"]
        c["beyond_gauge"] = (abs(c["delta"]) > gb) if gb is not None else None
        c["verdict"] = _verdict(c, gauge, level)
        # Four-state resolution verdict (folded in, commit B): typed + machine-readable on EVERY comparison,
        # so the adapter never parses the summary string. Same code path as the certificate
        # (msai_eval.resolution.four_state), both dof modes. The conservative dominant-dof state and the
        # WS-νeff provisional-J<5 flag travel in-band, per the cert's inline-caveat precedent.
        rb = gauge.get("resolution_budget")
        c["bands"] = {"band_A": c["estimate_U"], "band_B": gb,
                      "band_A_basis": BAND_A_BASIS, "band_B_basis": BAND_B_BASIS,
                      "declared_use": declared_use}
        if rb is not None and gb is not None:
            _rv = four_state(c["delta"], c["ci"], rb, c["significant_adj"], dof_mode="ws")
            _rv_dom = four_state(c["delta"], c["ci"], rb, c["significant_adj"], dof_mode="dominant")
            c["resolution_verdict"] = {
                "state": _rv["state"], "U": _rv["U"], "U_lo": _rv["U_lo"], "U_hi": _rv["U_hi"],
                "nu_eff": _rv["nu_eff"], "p_beyond": _rv["p_beyond"], "dof_mode": "ws",
                "state_dominant": _rv_dom["state"], "provisional": bool(k < 5)}
        else:
            # no resolution budget (frozen / no-replicate / unqualified gauge) -> no four-state verdict.
            c["resolution_verdict"] = None
        # SECONDARY (cross-lineage review): under level="interval" the mean IS the right tool, so a mean/rank
        # sign disagreement is NOT withheld (deliberate) — but it is still worth surfacing as a soft note: it
        # signals a skewed score distribution where, if the interval-spacing assumption is shaky, the direction
        # would flip under level="ordinal". Informational only; the verdict is unchanged.
        _cd = c.get("cliffs_delta")
        if level == "interval" and c["significant_adj"] and _cd is not None and not math.isnan(_cd) \
                and abs(_cd) >= 0.1 and (_cd * c["delta"] < 0):
            c["sign_divergence_note"] = ("mean Δ and Cliff's δ disagree in sign — the score distribution is "
                "skewed; the mean is correct on a TRUE interval scale, but this direction would be WITHHELD "
                "under level='ordinal'. Inspect if your scale's interval spacing is uncertain.")

    notes = []
    if not gauge["qualified"]:
        notes.append("GAUGE NOT QUALIFIED: every verdict is provisional until the gauge warnings are resolved.")
    if level == "ordinal":
        notes.append("ordinal scores: Δ is a difference of MEANS and assumes interval spacing. "
                     "Cliff's δ (rank-based) is the assumption-free effect size shown alongside. "
                     "A confident directional verdict is WITHHELD when mean Δ and Cliff's δ disagree "
                     "in sign (the interval-spacing assumption is then unsafe) — reported as 'mean Δ "
                     "and rank-effect disagree', not a drop/gain.")
    notes.append("two gates kept separate: 'resolvable' (CI excludes 0, Holm-corrected) vs "
                 "'beyond gauge resolution' (|Δ| > guard band). A drop can be real yet sub-resolution.")
    notes.append("configs are fixed treatments, not a random part sample — this is why compare() uses "
                 "direct pairwise deltas, not selection-sensitive %GRR or ndc, as the verdict. ndc is "
                 "reported as advisory context only and never gates qualification.")
    notes.append("'within noise (indistinguishable on this gauge)' means |Δ| is below THIS gauge's "
                 "resolution (the guard band) — it is NOT a claim the configs are equal or 'lossless'. "
                 "A real difference smaller than the guard band reads this way. To trust a 'within noise' "
                 "verdict for small deltas, first confirm the guard band is fine enough (shrink GRR with "
                 "more trials/judges); a statistically real difference below resolution is reported "
                 "separately as 'statistically real but BELOW gauge resolution', never as 'within noise'.")

    return ComparisonReport(baseline, base_mean, level, gauge, comparisons, notes)
