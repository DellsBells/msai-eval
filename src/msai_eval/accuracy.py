"""The accuracy / bias tier — conformance to a TRUSTED reference.

This is the honest version of "grade against reality." It is the ONLY place MSAI
makes an accuracy claim, and the claim is strictly scoped: accuracy here means
conformance to the reference YOU supply, and it is only as trustworthy as that
reference. A proven key, a consented/ratified baseline, or a real execution
outcome is a valid reference. Consensus among the judges is NOT — grading judges
against their own average is circular calibration.

MSAI cannot verify where your reference came from; ensuring it is trustworthy is
your responsibility. What it CAN and does do: detect the one circular case it can
see — when the supplied reference matches the judges' own consensus — and raise
the `reference_is_consensus` flag so the accuracy number is never read as
independent corroboration. (See reliability() in __init__.py.)
"""
from __future__ import annotations
import numpy as np


def accuracy_report(ds, reference: dict, level: str = "ordinal", tol=0.0) -> dict:
    """ds: Dataset. reference: {item_id: true_value}. Returns the bias ledger.

    nominal  -> exact-match rate per judge vs reference.
    ordinal/interval -> within-tolerance rate + mean absolute error vs reference.

    `tol` may be a scalar OR a {item_id: tol} map. The map lets the caller set each item's
    accept band to that item's expanded reference uncertainty U_ref, so "correct" means "within
    the reference's own uncertainty" — you cannot fault a judge for a deviation the reference
    itself can't resolve. (reliability() builds this map from a Reference object.)
    """
    per = {}          # judge -> dict(correct, total, abs_errors)
    tot = {"correct": 0, "total": 0, "abs": []}
    n_items_scored = 0

    for i, it in enumerate(ds.items):
        if it not in reference:
            continue
        ref = reference[it]
        tol_i = (tol.get(it, 0.0) if isinstance(tol, dict) else tol)
        scored_here = False
        for j, jg in enumerate(ds.judges):
            for s in ds.cells[i][j]:
                scored_here = True
                d = per.setdefault(jg, {"correct": 0, "total": 0, "abs": []})
                d["total"] += 1
                tot["total"] += 1
                if level == "nominal":
                    ok = (s == ref)
                else:
                    err = abs(float(s) - float(ref))
                    ok = err <= tol_i
                    d["abs"].append(err)
                    tot["abs"].append(err)
                if ok:
                    d["correct"] += 1
                    tot["correct"] += 1
        if scored_here:
            n_items_scored += 1

    by_judge = {}
    for jg, d in per.items():
        by_judge[jg] = {
            "accuracy": (d["correct"] / d["total"]) if d["total"] else float("nan"),
            "n": d["total"],
            "mae": (float(np.mean(d["abs"])) if d["abs"] else None),
        }
    return {
        "by_judge": by_judge,
        "overall_accuracy": (tot["correct"] / tot["total"]) if tot["total"] else float("nan"),
        "overall_mae": (float(np.mean(tot["abs"])) if tot["abs"] else None),
        "n_items_scored": n_items_scored,
        "n_predictions": tot["total"],
        "level": level,
        "tol": ("per-item U_ref" if isinstance(tol, dict) else tol),
    }
