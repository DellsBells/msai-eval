"""MSAI (msai-eval) — Measurement System Analysis for Intelligence.

Gage R&R for LLM-as-judge evals: measure your measurement system, not your model.

    import msai_eval as msai
    report = msai.reliability(data, level="ordinal")
    report.summary()

`data` can be: a list of dicts {item, judge, score}; a pandas DataFrame with
those columns; a dict {item: {judge: score_or_list}}; or a 2D items x judges
array. Repeat scorings of the same item by the same judge (trials) unlock the
repeatability / Gage R&R variance decomposition.

Optional accuracy tier: pass `reference={item_id: true_value}` to grade the judges
against a TRUSTED key (a proven label set, a consented/ratified baseline, or a real
execution outcome). Accuracy is conformance to that reference and is only as valid
as the reference is — consensus among judges is not a valid reference.
"""
from __future__ import annotations
import numpy as np
from collections import Counter

from .data import normalize, Dataset, _label_key
from .agreement import (krippendorff_alpha, icc_2_1, weighted_kappa,
                        percent_agreement, bootstrap_ci)
from .variance import variance_components
from .accuracy import accuracy_report
from .report import Report
from .compare import compare, ComparisonReport
from .stability import stability, StabilityReport
from .proficiency import proficiency, ProficiencyReport
from .reference import (Reference, certified_reference, reference_from_labels,
                        combine_references, flag_if_consensus, score)
from .uncertainty import uncertainty_budget, UncertaintyReport
from .resolution import four_state, welch_satterthwaite_dof, dominant_typeA_dof

__version__ = "0.8.0"
__all__ = ["reliability", "compare", "stability", "proficiency", "uncertainty_budget",
           "Report", "ComparisonReport", "StabilityReport", "ProficiencyReport",
           "UncertaintyReport", "Reference", "certified_reference", "reference_from_labels",
           "combine_references", "flag_if_consensus", "score", "Dataset", "krippendorff_alpha",
           "icc_2_1", "weighted_kappa", "percent_agreement", "variance_components",
           "accuracy_report", "normalize", "four_state", "welch_satterthwaite_dof",
           "dominant_typeA_dof"]


def _mode(vals):
    vals = [v for v in vals if v is not None and not (isinstance(v, float) and np.isnan(v))]
    if not vals:
        return float("nan")
    return Counter(vals).most_common(1)[0][0]


def _mode_matrix(ds):
    """judges x items matrix of the per-cell MODE (correct aggregation for nominal)."""
    M = np.full((ds.n_judges, ds.n_items), np.nan)
    for i in range(ds.n_items):
        for j in range(ds.n_judges):
            if ds.cells[i][j]:
                M[j, i] = _mode(ds.cells[i][j])
    return M


def reliability(data, level: str = "ordinal", reference: dict | None = None,
                tol: float = 0.0, n_boot: int = 2000, seed: int = 0) -> Report:
    """Compute the reproducibility report (and, if `reference` is given, the
    accuracy/bias report) for an LLM-as-judge eval. See module docstring."""
    ds = normalize(data, level=level)
    flags = list(ds.flags)
    is_nominal = (level == "nominal")

    # For NOMINAL data, category values are labels, not magnitudes: aggregate
    # trials by mode (not mean), and never compute mean-based or interval stats.
    matrix = _mode_matrix(ds) if is_nominal else ds.matrix

    # Krippendorff alpha — always applicable; handles missing + multi-judge
    alpha = krippendorff_alpha(matrix, level=level)
    alpha_ci = bootstrap_ci(lambda m: krippendorff_alpha(m, level=level),
                            matrix, n_boot=n_boot, seed=seed)

    # ICC(2,1) is an interval statistic — meaningless on nominal category ids.
    icc = float("nan")
    icc_ci = (float("nan"), float("nan"))
    if not is_nominal and ds.complete and ds.n_judges >= 2 and ds.n_items >= 2:
        icc = icc_2_1(matrix.T)
        icc_ci = bootstrap_ci(lambda m: icc_2_1(m.T), matrix, n_boot=n_boot, seed=seed)

    raw = percent_agreement(matrix)
    if is_nominal:
        raw["mean_abs_diff"] = None   # undefined for labels

    # Per-judge effect. For interval/ordinal: deviation from panel mean. For
    # nominal: DISSENT RATE — fraction of items where the judge's modal category
    # differs from the panel's modal category. Both are descriptive, not corrections.
    rater_effects = {}
    if is_nominal:
        panel_mode = [_mode(matrix[:, i]) for i in range(ds.n_items)]
        for j, jg in enumerate(ds.judges):
            dissent = [matrix[j, i] != panel_mode[i] for i in range(ds.n_items)
                       if not np.isnan(matrix[j, i])]
            rater_effects[jg] = float(np.mean(dissent)) if dissent else float("nan")
    else:
        panel_mean = np.nanmean(matrix, axis=0)
        for j, jg in enumerate(ds.judges):
            rater_effects[jg] = float(np.nanmean(matrix[j] - panel_mean))

    # Variance decomposition is an interval method — skip for nominal.
    var = None if is_nominal else variance_components(ds)
    if var:
        flags.extend(var.get("flags", []))

    if ds.n_judges == 2 and ds.complete and not is_nominal:
        wk = weighted_kappa(matrix[0], matrix[1], weights="quadratic")
        flags.append(f"two_judges: quadratic-weighted kappa = {wk:.3f} "
                     f"(report this alongside alpha for the pairwise case).")

    # Accuracy / bias tier — only if a trusted reference is supplied. `reference` may be a bare
    # {item: value} dict OR a Reference object that carries per-item u_ref (preferred).
    ref_obj = reference if isinstance(reference, Reference) else None
    ref_dict = reference.to_truth_dict() if ref_obj is not None else reference
    # encode a nominal reference with the SAME canonical label map the data used, so "A"/"1"/1 match
    if is_nominal and ds.label_map and ref_dict:
        unknown_labels = [v for v in ref_dict.values() if _label_key(v) not in ds.label_map]
        if unknown_labels:
            flags.append(f"reference_label_not_in_data: reference label {unknown_labels[0]!r} was used by "
                         f"no judge — it can never match, so it scores as wrong everywhere. Check the labels.")
        ref_dict = {it: ds.label_map.get(_label_key(v), v) for it, v in ref_dict.items()}

    accuracy = None
    if ref_dict:
        # With a Reference, each item's accept band is its expanded uncertainty U_ref = k*u_ref
        # (k=2), floored by the caller's tol: "wrong" means outside the reference's OWN uncertainty.
        if ref_obj is not None:
            acc_tol = {}
            for it in ref_obj.values:                       # key off the GRADED set; missing/non-finite
                u = ref_obj.u.get(it)                        # u_ref still gets at least the tol floor
                acc_tol[it] = max(tol, 2.0 * abs(u)) if (u is not None and np.isfinite(u)) else tol
        else:
            acc_tol = tol
        accuracy = accuracy_report(ds, ref_dict, level=level, tol=acc_tol)

        # propagate a Reference's provenance: its build-time warnings + any invalid traceability
        if ref_obj is not None:
            for w in ref_obj.warnings:
                flags.append(f"reference: {w}")
            if "INVALID" in ref_obj.traceability or "consensus" in ref_obj.traceability:
                flags.append("reference_traceability_invalid: this reference is marked "
                             f"{ref_obj.traceability!r}; its accuracy claim is not independent.")

        # FITNESS GATE on the ACCURACY headline (BLOCKER): a reference far looser than the gauge
        # cannot certify accuracy — overall_accuracy=1.0 against a u=100 reference is meaningless.
        if ref_obj is not None and accuracy is not None and not is_nominal:
            gauge_sd = float(var["grr_sd"]) if (var and np.isfinite(var.get("grr_sd", float("nan")))) else None
            fit = ref_obj.fitness(gauge_sd) if gauge_sd is not None else None
            if fit is not None and not str(fit["verdict"]).startswith("FIT"):
                accuracy["fitness"] = fit["verdict"]
                accuracy["accuracy_label"] = "conformance within a loose reference (NOT a resolved correctness claim)"
                flags.append(f"reference_not_fit_for_accuracy: the reference is {fit['verdict']} vs the gauge "
                             f"(TUR {fit.get('ratio')}) — the ACCURACY number is conformance within a reference "
                             "too loose to resolve the judges, NOT a resolved correctness claim. Tighten the reference.")
            elif gauge_sd is None:
                us = [v for v in ref_obj.u.values() if v is not None and np.isfinite(v)]
                refvals = [float(v) for v in ref_dict.values() if v is not None]
                span = (max(refvals) - min(refvals)) if len(refvals) >= 2 else None
                if us and span and span > 0 and 2 * max(us) >= span:
                    accuracy["fitness"] = "UNFIT (U_ref >= item span)"
                    accuracy["accuracy_label"] = "conformance within a loose reference (NOT a resolved correctness claim)"
                    flags.append("reference_not_fit_for_accuracy: U_ref is as large as the spread of the reference "
                                 "values themselves — the accuracy number is conformance within a band too wide to "
                                 "distinguish items, NOT a resolved correctness claim.")

        # honesty guard: flag references that aren't actually in the data
        item_set = set(ds.items)
        missing = [k for k in ref_dict if k not in item_set]
        if missing:
            flags.append(f"reference_keys_not_in_data: {len(missing)} reference key(s) "
                         f"match no item (e.g. {missing[0]!r}) — check for id/type mismatches.")

        # honesty guard: detect the one circular case we can see — a reference that
        # IS the judges' own consensus. Grading judges against their own average is
        # circular; warn so the accuracy number is never read as corroboration.
        match, total = 0, 0
        for i, it in enumerate(ds.items):
            if it not in ref_dict:
                continue
            col = matrix[:, i]
            col = col[~np.isnan(col)]
            if len(col) == 0:
                continue
            total += 1
            if is_nominal:
                if ref_dict[it] == _mode(col):
                    match += 1
            else:
                if abs(float(ref_dict[it]) - float(np.mean(col))) <= max(tol, 0.5):
                    match += 1
        if total >= 3 and match / total >= 0.9:
            flags.append(
                "reference_is_consensus: the supplied reference matches the judges' own "
                f"consensus on {match}/{total} items. Accuracy against consensus is circular "
                "— it measures agreement, not correctness. Use an independent reference."
            )

    # per-item / per-cell detail for the visual report (the heatmap + particle field)
    detail = _compute_detail(ds, matrix, is_nominal, ref_dict, tol)

    return Report(
        n_items=ds.n_items, n_judges=ds.n_judges, n_trials_max=ds.n_trials_max,
        alpha=alpha, alpha_ci=alpha_ci, alpha_level=level,
        icc=icc, icc_ci=icc_ci, raw=raw, rater_effects=rater_effects,
        variance=var, flags=flags, is_nominal=is_nominal, accuracy=accuracy,
        detail=detail,
    )


def _compute_detail(ds, matrix, is_nominal, reference, tol):
    """Per-cell grid for visualization: each cell is 1 (good), 0 (off), or None
    (missing). 'Good' = matches the reference if one was given, else matches the
    panel's modal answer. Also per-item agreement (fraction matching the mode)."""
    try:
        def good(v, target):
            if is_nominal:
                return v == target
            return abs(float(v) - float(target)) <= max(tol, 0.5)

        panel = []
        for i in range(ds.n_items):
            col = matrix[:, i]; col = col[~np.isnan(col)]
            panel.append(_mode(col) if len(col) else None)

        grid, item_agreement = [], []
        for j in range(ds.n_judges):
            row = []
            for i in range(ds.n_items):
                v = matrix[j, i]
                if np.isnan(v):
                    row.append(None); continue
                if reference and ds.items[i] in reference:
                    row.append(1 if good(v, reference[ds.items[i]]) else 0)
                elif panel[i] is not None:
                    row.append(1 if good(v, panel[i]) else 0)
                else:
                    row.append(None)
            grid.append(row)
        for i in range(ds.n_items):
            vals = [matrix[j, i] for j in range(ds.n_judges) if not np.isnan(matrix[j, i])]
            if vals:
                m = _mode(vals)
                item_agreement.append(float(np.mean([x == m for x in vals])))
            else:
                item_agreement.append(float("nan"))

        return {"items": [str(x) for x in ds.items], "judges": [str(x) for x in ds.judges],
                "grid": grid, "item_agreement": item_agreement,
                "graded_against": "reference" if reference else "panel consensus"}
    except Exception:
        return None
