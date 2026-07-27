"""The Report object and its honest plain-language summary.

The summary() output is, deliberately, where MSAI carries its own scope limit.
Every report states what it is (reproducibility / agreement, and — if a trusted
reference was given — conformance accuracy) and what it is NOT (a measure of
whether your model is good, or whether judge consensus is correct).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math

from .variance import gauge_judgement
from .data import safe_print


def _fmt(x, nd=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    if isinstance(x, float) and math.isinf(x):
        return "inf"
    return f"{x:.{nd}f}"


@dataclass
class Report:
    n_items: int
    n_judges: int
    n_trials_max: int
    alpha: float
    alpha_ci: tuple
    alpha_level: str
    icc: float
    icc_ci: tuple
    raw: dict
    rater_effects: dict
    variance: dict | None
    flags: list = field(default_factory=list)
    is_nominal: bool = False
    accuracy: dict | None = None          # conformance-vs-reference ledger, or None
    detail: dict | None = None            # per-item / per-cell grid for visualization

    def agreement_band(self) -> str:
        # Provisional heuristic labels (loosely echoing common kappa/alpha rules of
        # thumb), NOT validated decision cutoffs. Judge by the CI lower bound.
        a = self.alpha
        if a is None or math.isnan(a):
            return "undetermined"
        if a >= 0.80:
            return "high agreement"
        if a >= 0.667:
            return "tentative agreement"
        return "low agreement — measurement system is noisy"

    def to_dict(self) -> dict:
        return {
            "n_items": self.n_items, "n_judges": self.n_judges,
            "n_trials_max": self.n_trials_max,
            "krippendorff_alpha": self.alpha, "alpha_ci": self.alpha_ci,
            "alpha_level": self.alpha_level, "is_nominal": self.is_nominal,
            "icc_2_1": self.icc, "icc_ci": self.icc_ci,
            "raw_agreement": self.raw, "rater_effects": self.rater_effects,
            "variance_components": self.variance, "accuracy": self.accuracy,
            "gauge_judgement": gauge_judgement(self.variance),
            "agreement_band": self.agreement_band(), "flags": self.flags,
            "detail": self.detail,
        }

    def to_html(self, path: str, title: str = "LLM-judge reliability") -> str:
        """Render a self-contained, visual HTML report to `path`. Returns the path.

        The report has a cinematic 3D hero (the measurements as a particle field,
        tight when judges agree) over an impeccably readable data section. Open it
        in a browser; it needs network access once to load the 3D library.
        """
        from .htmlreport import render
        return render(self.to_dict(), path, title=title)

    def summary(self) -> str:
        L = []
        L.append("=" * 66)
        L.append("  MSAI — LLM-as-judge reproducibility report")
        L.append("=" * 66)
        kind = "nominal/categorical" if self.is_nominal else self.alpha_level
        L.append(f"  design: {self.n_items} items x {self.n_judges} judges, "
                 f"up to {self.n_trials_max} trial(s) each  [{kind}]")
        L.append("")
        L.append("  AGREEMENT (do your judges agree with each other?)")
        L.append(f"    Krippendorff's alpha ({self.alpha_level}) = {_fmt(self.alpha)}  "
                 f"[95% CI {_fmt(self.alpha_ci[0])}, {_fmt(self.alpha_ci[1])}]")
        if not self.is_nominal:
            L.append(f"    ICC(2,1) absolute agreement          = {_fmt(self.icc)}  "
                     f"[95% CI {_fmt(self.icc_ci[0])}, {_fmt(self.icc_ci[1])}]")
        L.append(f"    raw exact-agreement rate             = {_fmt(self.raw.get('exact_agreement'))}")
        if not self.is_nominal:
            L.append(f"    mean abs. difference between judges  = {_fmt(self.raw.get('mean_abs_diff'), 2)}")
        L.append(f"    -> {self.agreement_band()}  (heuristic label, not a verdict)")
        L.append("")
        if self.variance:
            v = self.variance
            L.append("  VARIANCE (how much of the spread is real vs. measurement noise?)")
            L.append(f"    real item-to-item differences   = {_fmt(100 - v['measurement_noise_share_pct'], 1)}%")
            L.append(f"    measurement-system noise        = {_fmt(v['measurement_noise_share_pct'], 1)}%")
            L.append(f"    classic %GRR (SD scale)         = {_fmt(v['msi_grr_pct'], 1)}%")
            L.append(f"    distinct categories (ndc)       = {_fmt(v['ndc'], 0)}")
            L.append("    NOTE: this share is selection-sensitive — feeding in more")
            L.append("    spread-out items shrinks it. It is not a pass/fail grade.")
            jg = gauge_judgement(v)
            if jg:
                L.append("")
                L.append(f"  GAUGE JUDGEMENT (AIAG %GRR x ndc):  {jg['verdict']}")
                L.append(f"    {jg['reason']}")
            L.append("")
        if self.rater_effects:
            if self.is_nominal:
                L.append("  PER-JUDGE DISSENT (fraction of items where the judge differs from")
                L.append("  the panel's modal category — DESCRIPTIVE, not a correction)")
                for j, e in self.rater_effects.items():
                    L.append(f"    {str(j):<28s} {_fmt(e, 2)}")
            else:
                L.append("  PER-JUDGE EFFECT (deviation from panel mean — DESCRIPTIVE, not a correction)")
                for j, e in self.rater_effects.items():
                    L.append(f"    {str(j):<28s} {e:+.2f}")
            L.append("")
        if self.accuracy:
            a = self.accuracy
            L.append("  ACCURACY (are the judges RIGHT vs your supplied reference?)")
            for jg, d in a["by_judge"].items():
                mae = "" if d["mae"] is None else f"  (MAE {_fmt(d['mae'], 2)})"
                L.append(f"    {str(jg):<28s} {_fmt(100*d['accuracy'], 0)}%  "
                         f"of {d['n']} preds{mae}")
            L.append(f"    overall                      = {_fmt(100*a['overall_accuracy'], 0)}%  "
                     f"({a['n_predictions']} preds over {a['n_items_scored']} items)")
            if a.get("accuracy_label"):
                L.append(f"    [!] {a['accuracy_label']}  (reference fitness: {a.get('fitness')})")
            L.append("    NOTE: 'accuracy' here is conformance to the reference YOU supplied")
            L.append("    and is only as trustworthy as that reference. A proven key, a")
            L.append("    consented/ratified baseline, or a real execution outcome is valid;")
            L.append("    judge consensus is NOT a valid reference. Compare it with the")
            L.append("    agreement above: high agreement + low accuracy = shared bias.")
            L.append("")
        if self.flags:
            L.append("  FLAGS")
            for f in self.flags:
                L.append(f"    [!] {f}")
            L.append("")
        L.append("  SCOPE — read this before quoting any number above:")
        L.append("    AGREEMENT measures whether judges concur and how reproducible the eval")
        L.append("    is. It does NOT, by itself, mean the judges are right — high agreement")
        L.append("    is equally consistent with a correct rubric, a shared wrong rubric, and")
        L.append("    gaming. ACCURACY (if shown) is correctness ONLY against your stated")
        L.append("    reference. With no trusted reference there is no true score, so no")
        L.append("    accuracy is claimed.")
        L.append("=" * 66)
        text = "\n".join(L)
        safe_print(text)
        return text
