"""proficiency.py — En / zeta / z scoring of a judge against the peer panel.

The metrology corpus's loudest claim (~20 episodes): proficiency testing — blind comparison
against a peer panel / reference — is the ONLY objective proof of competence, never
self-report. This is that, for AI judges.

For each item the ASSIGNED value is the ROBUST consensus of the panel (ISO 13528 Algorithm A),
so a rogue judge cannot corrupt the reference it is then scored against. Each judge is scored
against it:

    z    = (judge - assigned) / s*                                 (always available)
    zeta = (judge - assigned) / sqrt(u_judge^2 + u_assigned^2)     (needs replicate trials)
    En   = (judge - assigned) / sqrt(U_judge^2 + U_assigned^2)     (expanded, k=2; |En|<=1 = ok)

A judge is competent when it stays consistent with the robust consensus: |z| <= 2 (ISO 13528
warning at 2<|z|<3, action at |z|>=3) and |En| <= 1.

HONESTY FIREWALL: the reference here is the robust panel CONSENSUS, not truth. Proficiency
proves a judge AGREES with the qualified panel — it does NOT prove the panel is RIGHT. A
panel-wide shared error needs an external reference (the accuracy tier), which proficiency
cannot see. (Same consensus-is-not-correctness stance as the rest of MSAI.)

    from msai_eval import proficiency
    proficiency(data, level="ordinal").summary()

Field grounding (private practitioner corpus, not redistributed here): competence is
DEMONSTRATED under proctored comparison, never self-reported. Clause-level grounding:
docs/SPEC_GROUNDING.md.

STANDARDS CONFORMANCE — verified against the standards layer we actually hold (Eurachem PT Guide +
ISO/IEC 17043; ISO 13528 itself is NOT in the layer, so we anchor to the held clauses that carry the
same formulas and keep 13528 only as origin), with two DELIBERATE departures disclosed:
Conformant: Algorithm A robust consensus (1.5·s* winsorization) — METHOD from Eurachem §F.2 (which names
Algorithm A but carries no constants); the 1.483/1.134 CONSTANTS are ISO 13528 Annex C (not held; cited by name),
the assigned-value standard uncertainty u = 1.25·s*/√p (Eurachem §D.1; ISO 13528 §7.7 origin), the En
definition with |En| ≤ 1 (Eurachem §E.4), and the z evaluation limits — |z| ≤ 2 satisfactory,
2 < |z| < 3 warning, |z| ≥ 3 action (Eurachem §7.2.3; ISO/IEC 17043 §7.2.2). Two things depart ON
PURPOSE, for small-panel rogue/edge-case robustness:
  1. LEAVE-ONE-OUT consensus — the standards form the assigned value from ALL participants; we score
     each judge against the robust consensus of the OTHERS (excluding itself), so a rogue can't anchor
     its own reference. This changes the z reference relative to the standard.
  2. z-SCALE FLOOR — the standards divide by the assigned-value SD directly; we floor that SD at 5% of
     the score scale so near-unanimous peers can't inflate |z| into meaningless ranges. Non-standard
     regularization.
These are enhancements for AI-judge panels, not claims of strict conformance.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

from .data import normalize, safe_print


def algorithm_a(values, max_iter: int = 50, tol: float = 1e-7):
    """ISO 13528 Algorithm A robust mean (x*) + robust SD (s*): iterative Huber
    winsorization at 1.5 s*, the standard way to assign a consensus value resistant to
    outlier participants. Returns (x_star, s_star, n)."""
    x = np.asarray([v for v in values if v is not None and np.isfinite(v)], float)
    n = len(x)
    if n == 0:
        return float("nan"), float("nan"), 0
    if n == 1:
        return float(x[0]), 0.0, 1
    xm = float(np.median(x))
    s = 1.483 * float(np.median(np.abs(x - xm)))            # MAD-based start
    if s == 0:
        s = float(np.std(x, ddof=1))
    for _ in range(max_iter):
        if s == 0:
            break
        phi = 1.5 * s
        xw = np.clip(x, xm - phi, xm + phi)
        nm = float(xw.mean())
        ns = 1.134 * float(np.std(xw, ddof=1))             # 1.134 corrects the winsor bias
        if abs(nm - xm) <= tol and abs(ns - s) <= tol:
            xm, s = nm, ns
            break
        xm, s = nm, ns
    return xm, s, n


@dataclass
class ProficiencyReport:
    by_judge: dict
    by_item: dict
    n_items: int
    n_judges: int
    has_replicates: bool
    warnings: list = field(default_factory=list)
    n_reference_items: int = 0

    def to_dict(self):
        return {"by_judge": self.by_judge, "by_item": self.by_item,
                "n_items": self.n_items, "n_judges": self.n_judges,
                "has_replicates": self.has_replicates,
                "n_reference_items": self.n_reference_items, "warnings": self.warnings}

    def summary(self):
        L = ["=" * 66,
             "  MSAI — proficiency: each judge vs the robust peer panel (En / z)",
             "=" * 66,
             f"  design: {self.n_judges} judges x {self.n_items} items"
             f"{f' ({self.n_reference_items} vs traceable reference)' if self.n_reference_items else ''}   "
             f"reference = ISO 13528 robust consensus ({'En/z' if self.has_replicates else 'z only'})"]
        for w in self.warnings:
            L.append(f"  [!] {w}")
        L.append("")
        L.append("  PER-JUDGE VERDICT (competent = consistent: |z|<=2, |En|<=1)")
        for jg, d in self.by_judge.items():
            if d.get("n_scored", 0) == 0:
                L.append(f"    {str(jg):<26s} {d['verdict']}")
                continue
            zpart = (f"bias z̄={d['mean_z']:+.2f}  max|z|={d['max_abs_z']}"
                     if d.get("max_abs_z") is not None else "z: n/a (no panel spread)")
            en = f"  max|En|={d['max_abs_En']}" if d.get("max_abs_En") is not None else ""
            L.append(f"    {str(jg):<26s} {d['verdict']}")
            L.append(f"        {zpart}{en}   "
                     f"(2<|z|<3: {d['n_warn']}, |z|>=3: {d['n_action']} of {d['n_scored']} items)")
        L.append("")
        if self.n_reference_items:
            L.append("  NOTE: items marked 'vs traceable reference' are scored against EXTERNAL truth and")
            L.append("  test correctness ONLY TO WITHIN their u_ref (a loose u_ref proves little — see any")
            L.append("  reference_marginal / reference_unfit warnings). The remaining items use the robust")
            L.append("  panel consensus, which proves AGREEMENT, not correctness — a shared error there is")
            L.append("  invisible until you supply a reference for those items too.")
        else:
            L.append("  NOTE: the reference is the ROBUST panel CONSENSUS, not truth. This proves a")
            L.append("  judge AGREES with the qualified panel (proficiency) — NOT that the panel is")
            L.append("  RIGHT. A whole-panel shared error needs an external reference (accuracy),")
            L.append("  which proficiency cannot see.")
        L.append("=" * 66)
        text = "\n".join(L)
        safe_print(text)
        return text


def proficiency(data, level: str = "ordinal", k: float = 2.0, reference=None) -> ProficiencyReport:
    """Score each judge against the robust peer-panel consensus via En / zeta / z.

    If `reference` (a Reference carrying u_ref, or a bare {item: value} dict) is given, its value
    becomes the ASSIGNED truth and its u_ref the assigned-value uncertainty on covered items — so
    on those items judges are scored against TRACEABLE truth (En vs u_ref), catching a whole-panel
    error that consensus-only scoring is blind to. The panel still sets the z-scale."""
    ds = normalize(data)
    judges, items = list(ds.judges), list(ds.items)
    nj, ni = len(judges), len(items)

    # a Reference object or a bare dict -> {item: value}, {item: u_ref}
    ref_vals, ref_u = {}, {}
    if reference is not None:
        if hasattr(reference, "values") and hasattr(reference, "u"):
            ref_vals, ref_u = reference.values, reference.u
        elif isinstance(reference, dict):
            ref_vals = reference

    ref_unfit, ref_marginal = [], []

    # per (item, judge): mean over trials + repeatability standard uncertainty (nan-safe)
    mean = np.full((ni, nj), np.nan)
    u_rep = np.full((ni, nj), np.nan)
    for i in range(ni):
        for j in range(nj):
            t = ds.cells[i][j]
            if t:
                arr = np.array([x for x in t if x is not None], float)
                arr = arr[np.isfinite(arr)]
                if arr.size:
                    mean[i, j] = float(arr.mean())
                    if arr.size >= 2:
                        u_rep[i, j] = float(arr.std(ddof=1)) / np.sqrt(arr.size)
    has_replicates = bool(np.isfinite(u_rep).any())

    # scale for the reference-fitness gate: the item-to-item signal the reference must resolve.
    # We use the item signal, NOT GRR — GRR is inflated by a rogue judge, which would self-defeatingly
    # reject the reference exactly when it's needed; the item signal averages over judges and is robust.
    item_grand = np.array([np.nanmean(mean[i]) if np.isfinite(mean[i]).any() else np.nan
                           for i in range(ni)])
    sig_scale = float(np.nanstd(item_grand)) if np.isfinite(item_grand).any() else 0.0
    fit_scale = sig_scale if sig_scale > 0 else None

    # per item: the panel robust consensus always sets the z-scale (s_rob); a reference, where it
    # covers the item, overrides the assigned value + its uncertainty (u_asg).
    assigned = np.full(ni, np.nan); s_rob = np.full(ni, np.nan); u_asg = np.full(ni, np.nan)
    item_src = ["panel"] * ni
    by_item = {}
    for i in range(ni):
        col = mean[i, np.isfinite(mean[i])]
        xm, ss, p = algorithm_a(col)
        s_rob[i] = ss
        it = items[i]
        panel_u = (1.25 * ss / np.sqrt(p)) if (p > 0 and np.isfinite(ss)) else np.nan
        use_ref = it in ref_vals and ref_vals[it] is not None
        ur = None
        if use_ref:
            uref = ref_u.get(it, float("nan"))
            ur = float(uref) if (uref is not None and np.isfinite(uref)) else None
            # fitness gate: a u_ref too loose to resolve the item-to-item signal cannot arbitrate ->
            # reject, revert to panel; within ~4x of the signal is marginal (kept, flagged provisional).
            if ur is not None and fit_scale is not None and ur >= fit_scale:
                ref_unfit.append(str(it)); use_ref = False
            elif ur is not None and fit_scale is not None and ur >= fit_scale / 4.0:
                ref_marginal.append(str(it))
        if use_ref:
            assigned[i] = float(ref_vals[it])
            u_asg[i] = ur if ur is not None else panel_u
            item_src[i] = "reference"
        else:
            assigned[i] = xm
            u_asg[i] = panel_u
        by_item[it] = {
            "assigned": round(float(assigned[i]), 3) if np.isfinite(assigned[i]) else None,
            "s_robust": round(float(ss), 3) if np.isfinite(ss) else None,
            "u_assigned": round(float(u_asg[i]), 3) if np.isfinite(u_asg[i]) else None,
            "source": item_src[i], "n_judges": p,
        }
    n_ref_items = sum(1 for s in item_src if s == "reference")

    by_judge = {}
    score_scale = float(np.nanmax(mean) - np.nanmin(mean)) if np.isfinite(mean).any() else 1.0
    for j in range(nj):
        per = []
        for i in range(ni):
            if not np.isfinite(mean[i, j]):
                continue
            # LEAVE-ONE-OUT panel consensus (exclude judge j) so a rogue cannot anchor its OWN
            # reference — without this, {0,0,100} reads all-CONSISTENT including the rogue.
            others = np.array([mean[i, jj] for jj in range(nj)
                               if jj != j and np.isfinite(mean[i, jj])], float)
            xm_loo, s_loo, p_loo = algorithm_a(others) if others.size else (np.nan, np.nan, 0)
            is_ref = (item_src[i] == "reference") and np.isfinite(assigned[i])
            if is_ref:
                assigned_ij, u_asg_ij = assigned[i], u_asg[i]      # external reference value
            elif p_loo > 0 and np.isfinite(xm_loo):
                assigned_ij = xm_loo                               # leave-one-out panel consensus
                u_asg_ij = (1.25 * s_loo / np.sqrt(p_loo)) if (np.isfinite(s_loo) and s_loo > 0) else np.nan
            else:
                continue                                           # no others and no reference: nothing to score
            d = mean[i, j] - assigned_ij
            rec = {"item": str(items[i]), "src": item_src[i]}
            # floor the LOO scale so near-equal peers can't drive |z| into the thousands on trivial
            # jitter (the review's 5.001-vs-5.0 reading OUTLIER, identical to 105). Floor = 5% of scale.
            # LIMITATION (degenerate input only): if items have NO real variation, score_scale is set by
            # the sole deviating judge (circular), so a lone deviation can still over-flag. Graded tasks
            # with real item spread don't hit this; it can't be closed from data alone.
            s_floor = 0.05 * score_scale if score_scale > 0 else 0.0
            s_eff = max(s_loo, s_floor) if np.isfinite(s_loo) else s_floor
            if s_eff > 0:
                rec["z"] = round(d / s_eff, 2)
            u_j = u_rep[i, j] if np.isfinite(u_rep[i, j]) else 0.0
            if np.isfinite(u_asg_ij) and (is_ref or np.isfinite(u_rep[i, j])):
                uc = float(np.hypot(k * u_j, k * u_asg_ij))
                if uc > 0:
                    rec["En"] = round(d / uc, 2)
                    rec["zeta"] = round(d / float(np.hypot(u_j, u_asg_ij)), 2)
                elif is_ref:                                       # exact reference (u_ref=0), no judge spread
                    rec["En"] = 0.0 if d == 0 else float("inf")
                    rec["zeta"] = rec["En"]
            per.append(rec)

        if not per:
            by_judge[judges[j]] = {"verdict": "INDETERMINATE",
                                   "reason": "no items with panel spread or a reference to score against",
                                   "n_scored": 0}
            continue
        zv = np.array([r["z"] for r in per if "z" in r], float)
        ens = [r["En"] for r in per if "En" in r]
        max_en = max((abs(e) for e in ens), default=None)
        en_fail = sum(1 for e in ens if abs(e) > 1)
        n_action = int((np.abs(zv) >= 3).sum()) if zv.size else 0          # Eurachem §7.2.3: |z|>=3 = action
        n_warn = int(((np.abs(zv) > 2) & (np.abs(zv) < 3)).sum()) if zv.size else 0   # 2<|z|<3 = warning
        judge_has_ref = any(r.get("src") == "reference" for r in per)
        tail = "reference / panel" if judge_has_ref else "panel"
        if n_action > 0 or en_fail > 0:
            verdict = f"OUTLIER — off the {tail}"
        elif n_warn > 0:
            verdict = "QUESTIONABLE"
        elif nj < 4 and not judge_has_ref:
            # a 3-judge panel leaves only 2 peers per LOO — too few to certify competence
            verdict = "INDETERMINATE — panel too small to certify competence without an external reference"
        else:
            verdict = f"CONSISTENT — competent vs {tail}"
        by_judge[judges[j]] = {
            "verdict": verdict,
            "mean_z": round(float(zv.mean()), 2) if zv.size else None,
            "max_abs_z": round(float(np.abs(zv).max()), 2) if zv.size else None,
            "max_abs_En": round(float(max_en), 2) if max_en is not None else None,
            "n_warn": n_warn, "n_action": n_action, "en_fail": en_fail,
            "n_scored": len(per), "per_item": per,
        }

    warnings = []
    if nj < 4:
        warnings.append(f"small_panel: {nj} judges — the robust consensus and its uncertainty are "
                        "coarse; En/z are unstable with few peers (need a fuller panel to trust an outlier call).")
    if not has_replicates:
        warnings.append("no_replicates: judge repeatability (u_judge) is unmeasured — z vs the robust panel "
                        "SD is reported; where a reference is used, En treats the judge as exactly repeatable "
                        "(u_judge=0), which is strict. Add replicate trials to size u_judge.")
    if n_ref_items:
        warnings.append(f"reference_used: {n_ref_items}/{ni} item(s) scored against a TRACEABLE reference "
                        "(En vs its u_ref) — these test correctness TO WITHIN u_ref; a loose u_ref proves little.")
    if ref_marginal:
        warnings.append(f"reference_marginal: on {len(ref_marginal)} item(s) u_ref is within ~4x of the "
                        "item-to-item signal — treat 'competent vs reference' there as provisional.")
    if ref_unfit:
        warnings.append(f"reference_unfit_rejected: {len(ref_unfit)} item(s) had a u_ref too loose to resolve "
                        "the item-to-item signal — it cannot arbitrate, so those reverted to panel consensus and "
                        f"were NOT scored for correctness (e.g. {ref_unfit[0]}). Get a tighter reference.")
    ref_assigned = [assigned[i] for i in range(ni) if item_src[i] == "reference" and np.isfinite(assigned[i])]
    if len(ref_assigned) >= 2 and (max(ref_assigned) - min(ref_assigned)) < 1e-9:
        warnings.append("reference_constant: the reference assigns the SAME target value to every item, so En "
                        "reduces to accuracy-from-a-fixed-target, NOT peer-relative competence — read the "
                        "per-judge accuracy/bias, not the OUTLIER verdict (which here just flags any deviation "
                        "beyond u_ref, so a near-perfect judge can still read OUTLIER on one tight item).")
    en_out = sum(1 for d in by_judge.values()
                 if str(d.get("verdict", "")).startswith("OUTLIER") and d.get("en_fail", 0) > 0)
    z_out = sum(1 for d in by_judge.values()
                if str(d.get("verdict", "")).startswith("OUTLIER") and d.get("n_action", 0) > 0)
    if en_out >= 2 and en_out > z_out:
        warnings.append(f"outlier_en_saturated: {en_out} judges read OUTLIER via the En test (|En|>1) and only "
                        f"{z_out} via a peer-relative z action (|z|>=3). En uses each judge's REPLICATE "
                        "uncertainty as the yardstick; on a low-replicate / high-reproducibility panel that "
                        "yardstick is tiny next to the real between-judge spread, so En flags judges that z "
                        "says are in range — the OUTLIER label is firing on ordinary disagreement, NOT "
                        "incompetence, and cannot fingerprint a biased judge. Read per-judge bias (mean_z) and "
                        "its separation across judges, NOT the OUTLIER verdict. (Synthetic coverage: OUTLIER "
                        "fires on a judge ~100% regardless of its bias; bias shows in mean_z only at >= ~2x the "
                        "reproducibility SD.)")
    return ProficiencyReport(by_judge=by_judge, by_item=by_item, n_items=ni, n_judges=nj,
                             has_replicates=has_replicates, warnings=warnings, n_reference_items=n_ref_items)
