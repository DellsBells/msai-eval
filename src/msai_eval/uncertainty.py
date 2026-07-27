"""uncertainty.py — a GUM uncertainty budget: how small a difference can this eval resolve?

The Guide to the Expression of Uncertainty in Measurement (GUM / JCGM 100): a measurement result
is incomplete without a stated uncertainty, AND you should know WHICH source dominates it. This
builds that budget for an LLM-judge eval — it combines every uncertainty source MSAI can see into
one combined standard uncertainty u_c and an expanded U (coverage factor k from the Welch-
Satterthwaite effective degrees of freedom), and — the actionable part — shows each source's %
contribution so you know the single lever to pull.

Sources budgeted:
  repeatability   (Type A)  a judge re-scoring the same item varies     sqrt(sigma2_repeat)
  reproducibility (Type A)  judges disagree (severity + interaction)    sqrt(sigma2_judge+sigma2_int)
  resolution      (Type B)  the score scale is quantized                delta / sqrt(12)
  reference       (Type B)  the truth you grade against is uncertain    mean u_ref

  u_c = sqrt(sum u_i^2);  nu_eff via Welch-Satterthwaite;  U = k(nu_eff) * u_c

HONESTY FIREWALL: a budget covers the sources it MODELS. Un-modeled SYSTEMATIC effects — a wrong
rubric, a bias shared by every judge, a non-representative item sample — are NOT in here and make
the true uncertainty larger. U is a floor on what you can resolve, not a ceiling on how wrong you
can be.

RESOLUTION SCOPE: the "U only ever widens / never manufactures a confident finding" guarantee holds
for a MEANINGFULLY-SCALED or DECLARED input. When scores aren't on an integer grid and no resolution=
is passed, the quantization step is inferred from the data — and an adversarial sub-resolution-jitter
input defeats every data-derived threshold (they all scale WITH the attack). For interval data, pass
resolution= (the smallest meaningful difference); otherwise a `resolution_auto_inferred` warning fires.

    from msai_eval import uncertainty_budget
    uncertainty_budget(data, level="ordinal", reference=ref).summary()

Grounded in the field (corroborated across both shows): the complete budget is "the five R's:
reference standard and certainty, reference stability, resolution, repeatability, reproducibility...
and don't forget environmental factors" (Zumbrun, chatnapt-ep18 ↔ qcast); and a pass/fail without
uncertainty is unsafe — "a resulting probability that it's called a pass, but it has a high probability
it could be a fail" (qcast-ep243 ↔ chatnapt). See METROLOGY_BRIEF.md §2a.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
import numpy as np

from .data import normalize, safe_print
from .variance import variance_components

# Student-t, two-sided 95%, by degrees of freedom (for the coverage factor k).
_T95 = [(1, 12.71), (2, 4.30), (3, 3.18), (4, 2.78), (5, 2.57), (6, 2.45), (7, 2.36), (8, 2.31),
        (9, 2.26), (10, 2.23), (12, 2.18), (15, 2.13), (20, 2.09), (24, 2.06), (30, 2.04),
        (40, 2.02), (60, 2.00), (120, 1.98)]


def _k_from_dof(nu) -> float:
    """Coverage factor k for ~95% from effective dof (t-table; 1.96 at the large-dof limit)."""
    if nu is None or not np.isfinite(nu):
        return 1.96
    if nu >= 120:
        return 1.96
    nu = max(1.0, nu)
    k = _T95[0][1]
    for v, t in _T95:
        if nu >= v:
            k = t
    return k


def _infer_resolution(ds, level) -> float:
    """The score quantization step (1 for an integer 1-5 scale). Uses the MODAL gap between
    distinct observed scores, NOT the minimum — one near-equal pair must not collapse the
    resolution to ~0, which would shrink the guard band and overclaim resolvability (the review
    BLOCKER). 0 disables the term. Pass an explicit resolution= to uncertainty_budget to override."""
    vals = sorted({float(v) for i in range(ds.n_items) for j in range(ds.n_judges)
                   for v in ds.cells[i][j] if v is not None})
    if len(vals) < 2:
        return 1.0 if level != "interval" else 0.0
    if all(abs(v - round(v)) < 1e-6 for v in vals):       # integer grid — the common ordinal case
        return 1.0
    diffs = [round(b - a, 9) for a, b in zip(vals, vals[1:]) if b - a > 1e-9]
    if not diffs:
        return 1.0 if level != "interval" else 0.0
    return float(Counter(diffs).most_common(1)[0][0])      # modal gap = the grid step (robust to a tiny pair)


@dataclass
class UncertaintyReport:
    components: list           # [{source, type, u, dof, pct}, ...]
    u_c: float                 # combined standard uncertainty
    nu_eff: float              # Welch-Satterthwaite effective dof
    k: float                   # coverage factor
    U: float                   # expanded uncertainty (k * u_c)
    dominant: dict | None      # the biggest contributor
    warnings: list = field(default_factory=list)

    def to_dict(self):
        return {"components": self.components, "u_c": self.u_c, "nu_eff": self.nu_eff,
                "k": self.k, "U": self.U, "dominant": self.dominant, "warnings": self.warnings}

    def _lever(self) -> str:
        if not self.dominant:
            return ""
        s = self.dominant["source"]
        if s.startswith("repeatability"):
            return "lower judge temperature, or average more trials per item."
        if s.startswith("reproducibility"):
            return "add judges or tighten the rubric — the judges disagree with each other."
        if s.startswith("resolution"):
            return "use a finer score scale — the 1-N rubric itself is the bottleneck."
        if s.startswith("reference"):
            return "get a tighter / independent reference — your TRUTH is the bottleneck."
        return ""

    def summary(self):
        L = ["=" * 70,
             "  MSAI — GUM uncertainty budget: how small a difference can this resolve?",
             "=" * 70]
        for w in self.warnings:
            L.append(f"  [!] {w}")
        L.append("")
        L.append(f"    {'source':<34s}{'type':<6s}{'u_i':>9s}{'contribution':>15s}")
        L.append("    " + "-" * 62)
        for c in self.components:
            L.append(f"    {c['source']:<34s}{c['type']:<6s}{c['u']:>9.4f}{c['pct']:>13.1f}%")
        L.append("    " + "-" * 62)
        L.append(f"    combined standard uncertainty u_c = {self.u_c:.4f}   "
                 f"(nu_eff = {('inf' if not np.isfinite(self.nu_eff) else round(self.nu_eff,1))}, "
                 f"k = {self.k:.2f})")
        L.append(f"    EXPANDED uncertainty  U(95%)      = +/- {self.U:.4f}")
        L.append(f"    -> differences smaller than ~{self.U:.3f} on this scale are NOT resolvable.")
        if self.dominant:
            L.append("")
            L.append(f"    DOMINANT source: {self.dominant['source']} ({self.dominant['pct']:.0f}%).")
            L.append(f"    Lever -> {self._lever()}")
        L.append("")
        L.append("  NOTE: this budgets the sources MSAI can MODEL. A wrong rubric, a bias shared by")
        L.append("  every judge, or a non-representative item sample are NOT in it and make the true")
        L.append("  uncertainty larger. U is a floor on what you can resolve, not a ceiling on error.")
        L.append("=" * 70)
        text = "\n".join(L)
        safe_print(text)
        return text


def uncertainty_budget(data, level: str = "ordinal", reference=None,
                       resolution=None, measurand: str = "absolute") -> UncertaintyReport:
    """Build the GUM uncertainty budget for an LLM-judge eval. `reference` (a Reference carrying
    u_ref, or a bare dict — bare dicts add no reference term) optionally folds in the truth's own
    uncertainty. `resolution` overrides the inferred score quantization step.

    `measurand` selects what the budget is FOR:
      "absolute" (default) — the uncertainty of an absolute score. Reproducibility carries the full
        appraiser variance: the judge MAIN effect (each judge's scale LEVEL) AND the judge×item
        interaction. This is the correct, unchanged budget for an absolute-score / threshold decision.
      "delta" — the uncertainty of a WITHIN-JUDGE difference (config − baseline), where the SAME judge
        rates both sides. The judge MAIN effect is then COMMON-MODE and cancels EXACTLY in the delta
        (the same reason u_ref cancels in a config-vs-baseline comparison; see compare.py). Carrying it
        would inflate the band with an error the delta does not incur. So reproducibility keeps ONLY the
        judge×item INTERACTION (genuine disagreement about the GAP, which does NOT cancel). Valid only on
        a balanced CROSSED design (every judge rates every item) — the CALLER must guarantee that. Never
        use a "delta" budget for an absolute-score uncertainty: there the level is real error to carry."""
    if level == "nominal":
        raise ValueError("uncertainty_budget is a metric (interval/ordinal) tool; nominal categories "
                         "have no magnitude. Use reliability()'s agreement metrics for nominal data.")
    if measurand not in ("absolute", "delta"):
        raise ValueError(f"measurand must be 'absolute' or 'delta', got {measurand!r}")
    ds = normalize(data)
    var = variance_components(ds)
    warnings = []
    comps = []

    # Type A — repeatability + reproducibility, straight from the variance decomposition
    if var:
        u_repeat = float(np.sqrt(max(0.0, var.get("sigma2_repeat", 0.0))))
        s2_judge = max(0.0, var.get("sigma2_judge", 0.0))
        s2_int = max(0.0, var.get("sigma2_interaction", 0.0))
        if measurand == "delta":
            # The judge MAIN effect (level) is common-mode in a within-judge delta -> cancels -> drop it.
            # Keep only the judge×item interaction (the real gap-disagreement that does NOT cancel).
            u_repro = float(np.sqrt(s2_int))
            u_level_removed = float(np.sqrt(s2_judge))
            if u_level_removed > 0:
                warnings.append(
                    f"level_centered_for_delta: removed the judge MAIN-effect reproducibility (appraiser "
                    f"scale-level spread = {u_level_removed:.4g} SD) — it is common-mode in a within-judge "
                    f"delta and cancels, so it is NOT in this band. Only the judge×item interaction "
                    f"({u_repro:.4g} SD, the genuine gap-disagreement) is carried. This budget is for a DELTA "
                    "measurand ONLY; do NOT use it for an absolute-score uncertainty (there the level is real "
                    "error the band must carry).")
        else:
            u_repro = float(np.sqrt(s2_judge + s2_int))
    else:
        u_repeat = u_repro = 0.0
        warnings.append("no variance decomposition (need >=2 judges and a complete design) — the Type A "
                        "repeatability/reproducibility terms are absent from this budget.")

    n_trials = sum(len(ds.cells[i][j]) for i in range(ds.n_items) for j in range(ds.n_judges))
    n_cells = sum(1 for i in range(ds.n_items) for j in range(ds.n_judges) if ds.cells[i][j])
    dof_repeat = max(1, n_trials - n_cells)
    if n_trials <= n_cells:
        if u_repeat > 0:
            warnings.append("no replicate scorings — repeatability is not separately estimable; it is "
                            "entangled with reproducibility in this budget.")
        dof_repeat = float("inf")
    dof_repro = max(1, ds.n_judges - 1)

    if u_repeat > 0:
        comps.append({"source": "repeatability (re-scoring)", "type": "A", "u": u_repeat, "dof": dof_repeat})
    if u_repro > 0:
        comps.append({"source": "reproducibility (between-judge)", "type": "A", "u": u_repro, "dof": dof_repro})

    # Type B — resolution (score quantization), GUM rectangular distribution: u = delta / sqrt(12)
    delta = _infer_resolution(ds, level) if resolution is None else float(resolution)
    u_res = delta / np.sqrt(12.0)
    # Honest scope of the auto-inferred resolution: when scores aren't on an integer grid and no
    # resolution= was declared, the step is inferred from the data — which a sub-resolution-jitter
    # input can defeat (every data-derived threshold scales WITH the attack). For interval data,
    # declare resolution= (the smallest MEANINGFUL difference) or the U-band can be gamed.
    if resolution is None and level != "nominal":
        _vals = sorted({float(v) for i in range(ds.n_items) for j in range(ds.n_judges)
                        for v in ds.cells[i][j] if v is not None})
        if len(_vals) >= 2 and not all(abs(v - round(v)) < 1e-6 for v in _vals):
            warnings.append(f"resolution_auto_inferred: scores aren't an integer grid and no resolution= was "
                            f"declared — the quantization step ({delta:.3g}) was inferred from the data and can "
                            "be defeated by sub-resolution jitter. Declare resolution= (the smallest meaningful "
                            "difference) for interval data to make the U-band trustworthy.")
    if u_res > 0:
        comps.append({"source": "resolution (quantization)", "type": "B", "u": u_res, "dof": float("inf")})

    # Type B — reference uncertainty, if a Reference was supplied
    if reference is not None and hasattr(reference, "u"):
        us = [v for v in reference.u.values() if v is not None and np.isfinite(v)]
        if us:
            u_ref = float(np.mean(us))
            if u_ref > 0:
                comp = {"source": "reference uncertainty (u_ref)", "type": "B", "u": u_ref, "dof": float("inf")}
                # U3: the flat MEAN masks heterogeneity — if some items' truth is far less certain than
                # others, the budget understates them. Disclose the spread (mirrors Reference.fitness()).
                u_max, u_min = float(np.max(us)), float(np.min(us))
                if len(us) >= 2 and u_min > 0 and u_max / u_min >= 3:
                    comp["u_ref_max"] = round(u_max, 6)
                    warnings.append(f"reference uncertainty is HETEROGENEOUS (per-item u_ref spans {u_min:.3g}-"
                                    f"{u_max:.3g}); the budget's u_ref={u_ref:.3g} is the MEAN, so it UNDERSTATES the "
                                    "budget for the loose items (whose own u_ref is much larger). For a per-item "
                                    "decision on a loose item, use that item's u_ref, not the mean.")
                comps.append(comp)

    if not comps:
        warnings.append("no resolvable uncertainty sources were modeled (deterministic judges, no "
                        "resolution, no reference) — u_c = 0 is degenerate, not a real zero.")
        return UncertaintyReport(components=[], u_c=0.0, nu_eff=float("inf"), k=1.96, U=0.0,
                                 dominant=None, warnings=warnings)

    u_c = float(np.sqrt(sum(c["u"] ** 2 for c in comps)))
    for c in comps:
        c["pct"] = round(100.0 * c["u"] ** 2 / u_c ** 2, 1) if u_c > 0 else 0.0
        c["u"] = round(c["u"], 6)
    # Welch-Satterthwaite effective dof (Type B / infinite-dof terms contribute nothing)
    denom = sum((c["u"] ** 4) / c["dof"] for c in comps if np.isfinite(c["dof"]) and c["dof"] > 0)
    nu_eff = (u_c ** 4 / denom) if denom > 0 else float("inf")
    k = _k_from_dof(nu_eff)
    dominant = max(comps, key=lambda c: c["u"])
    # U1/U2 disclosure (module audit): with few judges the reproducibility dof ~ 1, so nu_eff is small and k is
    # large + UNSTABLE — U is a noisy POINT estimate (the synthetic n-sweep shows the coverage factor k ranging
    # ~2–13 across seeds on identical truth at 2 judges), and the dominant-source 'lever' flips to the WRONG
    # source ~19% at 2 judges / ~6% at 3. Disclose both below ~5 judges so U is not read as a hard threshold.
    if ds.n_judges < 5 and any(str(c["source"]).startswith("reproducibility") for c in comps):
        warnings.append(
            f"small_panel_U_unstable: {ds.n_judges} judges → low reproducibility dof (nu_eff="
            f"{'inf' if not np.isfinite(nu_eff) else round(nu_eff, 1)}, k={round(k, 2)}). U is a NOISY point "
            "estimate here, NOT a hard resolvability threshold — its coverage factor k swings ~2–13x across "
            "seeds on identical truth at ≤2 judges (synthetic n-sweep); read the U-band as ± a margin and "
            "prefer ≥5 judges. The DOMINANT-source lever below is likewise unreliable at this size (it flips "
            "to the wrong source ~19% at 2 judges / ~6% at 3) — confirm it with ≥5 judges before acting on it.")
    return UncertaintyReport(components=comps, u_c=round(u_c, 6), nu_eff=nu_eff, k=round(k, 3),
                             U=round(k * u_c, 6), dominant=dominant, warnings=warnings)
