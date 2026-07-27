"""reference.py — a traceable reference carries an UNCERTAINTY, or it isn't a reference.

Metrology's first rule (VIM / GUM / ISO 17025, and the corpus's "there is no measurement
without an uncertainty statement"): the reference you grade a gauge against must (a) be MORE
trustworthy than the gauge, and (b) carry its own u_ref, which propagates into every accuracy
and En claim. MSAI's accuracy + proficiency tiers otherwise assume u_ref = 0 — that the key is
perfect. This module replaces that assumption with a real, sourced uncertainty.

Build a Reference from:
  - certified_reference(values, u, source)   a proven key / certified value (UPC catalog match,
                                             an exact label) -> small or zero u_ref
  - reference_from_labels(labels, level)     several human labels per item -> value + SEM/disagreement
  - combine_references([refs...])            several INDEPENDENT sources -> inverse-variance
                                             weighted value + Birge-ratio-inflated u_ref (the CODATA
                                             way: if sources disagree more than their stated u, the
                                             truth is LESS certain than any one of them claims)

Then:
  - ref.fitness(gauge_sd)        is u_ref small enough vs the gauge to arbitrate? (4:1 reference-adequacy ratio)
  - flag_if_consensus(ref, ...)  refuse a "reference" that is just the judges' own consensus
  - score(ref, predictions)      court-defensible accuracy: a judge within U_ref of a traceable
                                 value is CONFORMANT, not "wrong" — you cannot fault a gauge for a
                                 deviation smaller than the reference's own uncertainty.

    from msai_eval import certified_reference, combine_references, score

Grounded in the field: "if you're not 100% comfortable with that established reference value and the
associated uncertainty... the entire test is meaningless" (Shah, chatnapt-ep10); traceability is earned,
not asserted — "what is NIST traceability? Just by saying that doesn't mean you have it" (Doty,
chatnapt-ep22, corroborated by qcast-ep195). See METROLOGY_BRIEF.md §2a.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
import numpy as np
from .data import safe_print


@dataclass
class Reference:
    values: dict                       # item -> assigned reference value
    u: dict                            # item -> standard uncertainty u_ref (>= 0)
    source: dict                       # item -> provenance string
    traceability: str                  # certified | human_labels | independent_multi | consensus (INVALID)
    warnings: list = field(default_factory=list)

    def items(self):
        return list(self.values.keys())

    def expanded(self, item, k: float = 2.0):
        """Expanded uncertainty U_ref = k * u_ref (k=2 ~ 95%)."""
        return k * self.u.get(item, float("nan"))

    def to_truth_dict(self):
        """Bare {item: value} to plug into reliability(reference=...)'s existing accuracy tier."""
        return dict(self.values)

    def fitness(self, gauge_sd: float, k: float = 2.0) -> dict:
        """Is the reference trustworthy ENOUGH to arbitrate this gauge? The 4:1 test-uncertainty-
        ratio rule: U_gauge / U_ref >= 4 means the reference comfortably out-resolves the gauge.
        Below 1 the reference is noisier than the gauge and CANNOT serve as truth."""
        us = [v for v in self.u.values() if v is not None and np.isfinite(v)]
        if not us or gauge_sd is None or not np.isfinite(gauge_sd):
            return {"ratio": None, "verdict": "INDETERMINATE",
                    "reason": "need a finite gauge SD and at least one finite u_ref."}
        # govern on the WORST (largest u_ref) item — a loose item is not rescued by tighter ones
        u_ref = float(np.max(us)); U_ref = k * u_ref; U_gauge = k * gauge_sd
        spread_note = ""
        if len(us) >= 2 and float(np.min(us)) > 0 and float(np.max(us)) / float(np.min(us)) >= 3:
            spread_note = (f" (governed by the worst item u_ref={u_ref:.3g}; per-item u_ref spans "
                           f"{float(np.min(us)):.3g}-{float(np.max(us)):.3g} — tighter items don't rescue it)")
        if U_ref == 0:
            return {"ratio": float("inf"), "U_gauge": round(U_gauge, 4), "U_ref": 0.0,
                    "verdict": "FIT — exact reference (u_ref=0)",
                    "reason": "reference asserts zero uncertainty (an exact proven key); valid only if that is literally true."}
        ratio = U_gauge / U_ref
        if ratio >= 4:
            v, why = "FIT (>= 4:1)", "reference out-resolves the gauge; clean arbiter."
        elif ratio >= 1:
            v, why = "MARGINAL (1-4:1)", ("reference is only somewhat tighter than the gauge — guard-band "
                                          "the accept zone by U_ref before calling a judge wrong.")
        else:
            v, why = "UNFIT (< 1:1)", ("the reference is NOISIER than the gauge it grades — it cannot serve "
                                       "as truth. Get a tighter reference before claiming accuracy.")
        return {"ratio": round(ratio, 2), "U_gauge": round(U_gauge, 4),
                "U_ref": round(U_ref, 4), "U_ref_mean": round(k * float(np.mean(us)), 4),
                "verdict": v, "reason": why + spread_note}

    def to_dict(self):
        return {"values": self.values, "u": self.u, "source": self.source,
                "traceability": self.traceability, "warnings": self.warnings}

    def summary(self):
        us = [v for v in self.u.values() if v is not None and np.isfinite(v)]
        umean = float(np.mean(us)) if us else float("nan")
        L = ["=" * 62,
             "  MSAI — reference (traceable value + uncertainty)",
             "=" * 62,
             f"  traceability class : {self.traceability}",
             f"  items              : {len(self.values)}",
             f"  mean u_ref         : {umean:.4f}    (expanded U_ref@k=2 = {2*umean:.4f})"]
        for w in self.warnings:
            L.append(f"  [!] {w}")
        L.append("=" * 62)
        text = "\n".join(L)
        safe_print(text)
        return text


# ----------------------------------------------------------------------------- builders

def certified_reference(values: dict, u=0.0, source: str = "certified") -> Reference:
    """A proven key / certified value. `u` is a scalar (same for all items) or a per-item dict.
    u=0 asserts an EXACT reference — only valid for a literal proven key (an exact UPC/string
    match), never for anything measured or labeled."""
    u_map = {it: (float(u.get(it, 0.0)) if isinstance(u, dict) else float(u)) for it in values}
    warns = []
    if any(v < 0 for v in u_map.values()):
        warns.append("negative u_ref supplied — uncertainty cannot be negative; using |u_ref|.")
        u_map = {it: abs(v) for it, v in u_map.items()}
    if any(v == 0 for v in u_map.values()):
        warns.append("u_ref=0 on some items asserts a PERFECT reference — valid ONLY for an exact "
                     "proven key (e.g. an exact UPC/string match). Any measured or labeled value has u>0.")
    return Reference(values=dict(values), u=u_map,
                     source={it: source for it in values}, traceability="certified", warnings=warns)


def reference_from_labels(labels: dict, level: str = "ordinal") -> Reference:
    """Several human labels per item -> assigned value + u_ref. For interval/ordinal: mean +
    standard error of the mean. For nominal: modal category + disagreement fraction (a PRECISION
    proxy, not a metric SD). Human labels capture inter-annotator spread, NOT correctness — shared
    annotator bias stays invisible (same firewall as panel consensus)."""
    values, u, source, warns = {}, {}, {}, []
    singletons = 0
    is_nominal = (level == "nominal")
    for it, labs in labels.items():
        labs = [x for x in labs if x is not None]
        if not labs:
            continue
        n = len(labs)
        if is_nominal:
            top, cnt = Counter(labs).most_common(1)[0]
            values[it] = top
            u[it] = float(1.0 - cnt / n)               # disagreement rate (0 = unanimous)
        else:
            try:
                arr = np.asarray(labs, float)
            except (ValueError, TypeError):
                raise ValueError(f"reference_from_labels(level={level!r}): item {it!r} has non-numeric "
                                 f"labels {labs!r}. Use level='nominal' for category labels.")
            values[it] = float(arr.mean())
            u[it] = float(arr.std(ddof=1) / np.sqrt(n)) if n >= 2 else float("nan")
        if n < 2:
            singletons += 1
        source[it] = f"{n} human label(s)"
    if singletons:
        warns.append(f"{singletons} item(s) have a single label — u_ref is unmeasured (nan); a lone "
                     "annotator carries no uncertainty estimate.")
    warns.append("human labels measure inter-annotator PRECISION, not correctness — a bias shared by "
                 "the annotators is not captured here.")
    return Reference(values=values, u=u, source=source, traceability="human_labels", warnings=warns)


def combine_references(refs, ) -> Reference:
    """Fuse several INDEPENDENT references per item: inverse-variance weighted value, with the u_ref
    inflated by the Birge ratio when the sources scatter more than their stated uncertainties
    (CODATA/BIPM practice). Two 'exact' (u=0) sources that disagree is a provenance error and is
    flagged loudly, not silently averaged.

    R5 (disclosed): when agreeing sources combine, u_ref SHRINKS below every single source (inverse-variance,
    e.g. two u=0.1 -> 0.0707). That is correct ONLY IF the sources are independent — a bias COMMON to them is
    NOT reduced by combining, so the fused reference can look more certain than it is. The shrink is flagged."""
    refs = [r for r in refs if r is not None]
    all_items = []
    for r in refs:
        for it in r.values:
            if it not in all_items:
                all_items.append(it)
    values, u, source, warns = {}, {}, {}, []
    high_birge = []; shrunk = []
    for it in all_items:
        xs, us, srcs = [], [], []
        for r in refs:
            if it in r.values and r.values[it] is not None:
                xs.append(float(r.values[it])); us.append(float(r.u.get(it, float("nan")))); srcs.append(r.source.get(it, "?"))
        xs = np.asarray(xs, float); us = np.asarray(us, float)
        n = len(xs)
        source[it] = " + ".join(srcs)
        if n == 0:
            continue
        zero = (us == 0)
        if zero.any():                                  # exact source(s) present
            zvals = xs[zero]
            if np.allclose(zvals, zvals[0]):
                exact_val = float(zvals[0]); values[it] = exact_val; u[it] = 0.0
            else:
                exact_val = float(zvals.mean())
                values[it] = exact_val; u[it] = float(zvals.std(ddof=1))
                warns.append(f"item {it!r}: conflicting EXACT (u=0) sources disagree "
                             f"({zvals.tolist()}) — a provenance error; u_ref widened to their spread.")
            # an exact source dominates, but a NON-exact source that disagrees is a provenance signal,
            # not noise to discard silently.
            for v, uu in zip(xs[~zero], us[~zero]):
                band = (2.0 * uu) if (np.isfinite(uu) and uu > 0) else 0.0
                if abs(v - exact_val) > max(band, 1e-12):
                    warns.append(f"item {it!r}: a non-exact source (value {v:g}) disagrees with the exact "
                                 f"reference ({exact_val:g}) beyond its stated uncertainty — possible "
                                 "provenance conflict; the exact value was used, verify it.")
            continue
        finite = np.isfinite(us) & (us > 0)
        if finite.sum() == 0:                           # no usable uncertainties -> fall back to spread
            values[it] = float(xs.mean())
            u[it] = float(xs.std(ddof=1)) if n >= 2 else float("nan")
            continue
        n_dropped = int((~finite).sum())
        if n_dropped:
            warns.append(f"item {it!r}: {n_dropped} source(s) dropped (non-finite u_ref); the combined "
                         f"value rests only on the {int(finite.sum())} source(s) with a stated uncertainty.")
        xs, us = xs[finite], us[finite]; n = len(xs)
        w = 1.0 / us**2
        xbar = float(np.sum(w * xs) / np.sum(w))
        u_int = float(1.0 / np.sqrt(np.sum(w)))
        if n >= 2:
            chi2 = float(np.sum((xs - xbar) ** 2 / us**2))
            birge = float(np.sqrt(chi2 / (n - 1)))
            u_ref = u_int * max(1.0, birge)
            if birge > 2:
                high_birge.append((it, round(birge, 2)))
            if u_ref < float(us.min()):
                shrunk.append(str(it))
        else:
            u_ref = u_int
        values[it] = xbar; u[it] = u_ref
    if high_birge:
        warns.append("sources materially disagree (Birge ratio > 2) on: "
                     + ", ".join(f"{it} (R={b})" for it, b in high_birge)
                     + " — u_ref was inflated; the assigned value there is shaky.")
    if shrunk:
        warns.append(f"u_ref SHRANK below every single source on {len(shrunk)} item(s) (inverse-variance "
                     "combine of agreeing sources). Correct ONLY IF the sources are INDEPENDENT — a bias COMMON "
                     "to them is NOT reduced by combining, so the fused reference can look more certain than it "
                     "is. Confirm the sources are genuinely independent.")
    return Reference(values=values, u=u, source=source, traceability="independent_multi", warnings=warns)


# ------------------------------------------------------------------------- firewall + scoring

def flag_if_consensus(reference: Reference, panel_consensus: dict, level: str = "ordinal",
                      tol: float = 0.5) -> bool:
    """Honesty firewall: if the 'reference' simply IS the judges' own consensus, grading them
    against it is circular (agreement, not correctness). Detect it, mark the reference INVALID,
    and return True. (Mirrors the reference_is_consensus guard in reliability().)

    HEURISTIC LIMITS (R4, disclosed): fires when >=90% of items land within `tol` (default 0.5) of
    consensus, and ONLY when >=3 items overlap — a smaller reference cannot be checked and escapes
    this guard entirely. It is a VALUES match, so it cannot distinguish a circular reference (derived
    from the judges) from an INDEPENDENT one that legitimately agrees with them; provenance must decide."""
    match = total = 0
    for it, val in reference.values.items():
        if it not in panel_consensus or val is None or panel_consensus[it] is None:
            continue
        total += 1
        if level == "nominal":
            match += int(val == panel_consensus[it])
        else:
            match += int(abs(float(val) - float(panel_consensus[it])) <= tol)
    if total >= 3 and match / total >= 0.9:
        reference.traceability = "consensus (INVALID)"
        reference.warnings.insert(0, f"reference_is_consensus: matches the judges' own consensus on "
                                      f"{match}/{total} items (within tol={tol}). Accuracy against consensus is "
                                      "circular — it measures agreement, not correctness. NOTE: a values match "
                                      "cannot PROVE circularity — an INDEPENDENT reference that legitimately agrees "
                                      "with the panel trips this too; verify the reference's PROVENANCE (is it "
                                      "derived FROM the judges?). If independent, this is corroboration, not "
                                      "circularity.")
        return True
    return False


def score(reference: Reference, predictions: dict, u_pred=None, k: float = 2.0,
          tol: float = 0.0, gauge_sd=None) -> dict:
    """Grade one prediction set against a traceable reference, carrying U_ref.

    Per item: En = (pred - assigned) / sqrt(U_pred^2 + U_ref^2). A judge is CONFORMANT when its
    deviation is within the combined expanded uncertainty (|En| <= 1) — i.e. indistinguishable
    from the traceable value. 'conformance_rate' is the honest accuracy; 'exact_rate' is the naive
    within-tol match that ignores u_ref.

    HONESTY GATES (a 'conformant' verdict must not rest on a reference that cannot resolve the
    judge): conformance achieved only because U_ref is wide relative to the signal is downgraded to
    INDISTINGUISHABLE; pass `gauge_sd` to apply the explicit 4:1 reference-adequacy-ratio fitness test; a reference
    marked consensus/INVALID is flagged CIRCULAR. Items with a non-finite/negative u_ref or u_pred
    are unscorable and excluded, never scored against a broken uncertainty."""
    u_pred = u_pred or {}
    per, skipped, warnings = [], [], []
    u_ref_std, assigned_vals = [], []
    for it, pred in predictions.items():
        if it not in reference.values or reference.values[it] is None or pred is None:
            continue
        ur = reference.u.get(it, 0.0); up = u_pred.get(it, 0.0)
        ur = float(ur) if (ur is not None and np.isfinite(ur)) else None
        up = float(up) if (up is not None and np.isfinite(up)) else None
        if ur is None or ur < 0 or up is None or up < 0:
            skipped.append(str(it)); continue          # non-finite/negative uncertainty -> unscorable
        d = float(pred) - float(reference.values[it])
        U_ref = k * ur; U_p = k * up
        denom = float(np.hypot(U_ref, U_p))
        if denom == 0:                                  # exact reference AND exact prediction
            En = 0.0 if d == 0 else float("inf")
            conformant = (d == 0)
        else:
            En = d / denom
            conformant = abs(d) <= denom
        u_ref_std.append(ur); assigned_vals.append(float(reference.values[it]))
        per.append({"item": str(it), "pred": float(pred), "assigned": float(reference.values[it]),
                    "delta": round(d, 4), "U_ref": round(U_ref, 4),
                    "En": (round(En, 2) if np.isfinite(En) else "inf"),
                    "conformant": bool(conformant), "exact": bool(abs(d) <= tol)})
    if skipped:
        warnings.append(f"{len(skipped)} item(s) unscorable — non-finite/negative u_ref or u_pred "
                        f"(e.g. {skipped[0]}); excluded rather than scored against a broken uncertainty.")
    n = len(per)
    if n == 0:
        return {"n": 0, "verdict": "NO OVERLAP", "per_item": [], "warnings": warnings}
    ens = [p["En"] for p in per if isinstance(p["En"], float)]
    conf = sum(p["conformant"] for p in per) / n
    exact = sum(p["exact"] for p in per) / n
    en_pass = (sum(abs(e) <= 1 for e in ens) / len(ens)) if ens else None
    max_abs_d = max((abs(p["delta"]) for p in per), default=0.0)

    if conf >= 0.99:
        verdict = "TRACEABLY CONFORMANT (within U_ref on all items)"
    elif conf >= 0.8:
        verdict = "MOSTLY CONFORMANT"
    else:
        verdict = "NONCONFORMANT vs traceable reference"

    # gate 1 — is the reference even fit to arbitrate? conformance reached only because U_ref dwarfs
    # the signal (item-to-item spread) proves the reference can't resolve the judge, not correctness.
    mean_U_ref = k * float(np.mean(u_ref_std)) if u_ref_std else 0.0
    sig = float(np.std(assigned_vals, ddof=1)) if len(assigned_vals) >= 2 else None
    fit = reference.fitness(gauge_sd, k=k) if gauge_sd is not None else None
    # R2: a PERFECT judge (no deviation beyond tol) can't be "unresolvable" — the reference has nothing to
    # fail to resolve, so item-truth clustering (tiny sig) must NOT trip this gate on a tight reference.
    too_loose = (sig is not None and sig > 0 and mean_U_ref >= sig and max_abs_d > tol)
    unfit = fit is not None and not str(fit["verdict"]).startswith("FIT")
    if conf >= 0.8 and (too_loose or unfit):
        verdict = "INDISTINGUISHABLE — reference too loose to resolve the judge"
        warnings.append("conformance was reached only because U_ref is wide"
                        + (f" (mean U_ref={mean_U_ref:.3g} vs item spread {sig:.3g})" if sig else "")
                        + (f"; fitness={fit['verdict']}" if fit else "")
                        + " — this proves the reference cannot resolve the judge, NOT that the judge is right.")
    elif conf >= 0.8 and (sig is None or sig == 0) and fit is None:
        # R1: no item-to-item spread (single item / identical truths) AND no gauge_sd -> resolving power is
        # UNVERIFIABLE; do NOT certify TRACEABLY CONFORMANT silently (a judge biased by ~U_ref still "passes").
        verdict = "CONFORMANT — reference FITNESS UNVERIFIED"
        warnings.append("reference_fitness_unverified: the reference has no item-to-item spread (single item "
                        "or identical truths) and no gauge_sd was given, so its RESOLVING POWER could not be "
                        f"checked. 'Conformant' here means only 'within U_ref' (mean U_ref={mean_U_ref:.3g}) — "
                        "uninformative if U_ref is large relative to the bias you care about (a judge biased by "
                        "nearly U_ref still passes). Provide gauge_sd, or a reference whose truths span a range.")

    # gate 2 — circularity: a consensus-derived reference is not independent truth.
    if "INVALID" in reference.traceability or "consensus" in reference.traceability:
        verdict = "CIRCULAR — reference is consensus, not independent: " + verdict
        warnings.append(f"reference traceability is {reference.traceability!r}; grading against it "
                        "measures agreement, not correctness.")

    # R3: the conformance RATE is count-based — a catastrophic per-item miss can hide behind a high rate
    # (4/5 perfect + 1 huge miss still reads MOSTLY CONFORMANT). Disclose the worst miss's magnitude.
    worst_en = max((abs(e) for e in ens), default=0.0)
    if conf >= 0.8 and worst_en > 3:
        warnings.append(f"large_miss_masked: conformance rate is {conf:.0%}, but at least one item is badly "
                        f"off (max |En| = {worst_en:.1f}, far beyond the |En|<=1 bound) — the count-based "
                        f"'{verdict.split(' —')[0]}' headline hides magnitude. Read the per-item En, not the rate.")

    return {"n": n, "verdict": verdict, "conformance_rate": round(conf, 3),
            "exact_rate": round(exact, 3),
            "en_pass_rate": (round(en_pass, 3) if en_pass is not None else None),
            "max_abs_En": (round(max(abs(e) for e in ens), 2) if ens else None),
            "fitness": (fit["verdict"] if fit else None),
            "traceability": reference.traceability, "warnings": warnings, "per_item": per}
