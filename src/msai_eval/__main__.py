"""CLI:  python -m msai_eval scores.csv [--level ordinal] [--reference]

CSV needs columns: item, judge, score. Optional: trial, reference.
If a `reference` column is present (the trusted true value per item), the accuracy
tier runs too. Score values may be numbers (ordinal/interval) or labels (nominal).
"""
from __future__ import annotations
import argparse, csv, sys


def _num(x):
    try:
        f = float(x)
        return int(f) if f.is_integer() else f
    except (ValueError, TypeError):
        return x


def main(argv=None):
    ap = argparse.ArgumentParser(prog="msai_eval", description="Gage R&R for LLM-as-judge evals.")
    ap.add_argument("csv", help="CSV with columns item, judge, score [, trial, reference]")
    ap.add_argument("--level", default="ordinal", choices=["ordinal", "interval", "nominal"])
    ap.add_argument("--tol", type=float, default=0.0, help="accuracy tolerance (ordinal/interval)")
    ap.add_argument("--json", action="store_true", help="print machine-readable JSON instead")
    ap.add_argument("--compare", metavar="BASELINE", default=None,
                    help="run the config-vs-baseline acceptance test, treating this item id as the baseline")
    args = ap.parse_args(argv)

    import msai_eval as msai

    records, reference = [], {}
    with open(args.csv, newline="") as f:
        rdr = csv.DictReader(f)
        cols = {c.lower(): c for c in (rdr.fieldnames or [])}
        for need in ("item", "judge", "score"):
            if need not in cols:
                ap.error(f"CSV missing required column '{need}'. Found: {rdr.fieldnames}")
        for row in rdr:
            it = row[cols["item"]]
            records.append({"item": it, "judge": row[cols["judge"]],
                            "score": _num(row[cols["score"]])})
            if "reference" in cols and row[cols["reference"]] not in (None, ""):
                reference[it] = _num(row[cols["reference"]])

    if args.compare:
        rep = msai.compare(records, baseline=args.compare, level=args.level)
    else:
        rep = msai.reliability(records, level=args.level,
                               reference=reference or None, tol=args.tol)
    if args.json:
        import json
        print(json.dumps(rep.to_dict(), indent=2, default=str))
    else:
        rep.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
