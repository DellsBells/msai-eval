"""Phase 4 — gauge/compare HALF, on the same real brand-ID task.

Companion to phase4_validation.py (modules half). Re-collects the real panel data, then runs the
COMPARE track: the 3 vision models are the treatments, the 14 products are the panel/conditions,
each (model, product) cell has `trials` replicate brand-reads. compare(baseline) asks whether each
model's brand-read quality differs from the baseline model BEYOND the gauge's resolution (the
U-band). Persists the raw rows (the modules half did not).

    .venv/bin/python benchmark/phase4_compare_half.py --n 14 --trials 2 --temp 0.7
"""
from __future__ import annotations
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_benchmark import norm
from run_tier2 import fetch_obf, get_image
from phase4_validation import ask_brand, overlap
import msai_eval as msai


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--models", default="qwen3.5:27b,resale-vlm-v2:12b,qwen2.5vl:7b")
    ap.add_argument("--baseline", default="qwen3.5:27b")
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    models = args.models.split(",")

    print("=== Phase 4 compare-half: models as treatments, products as panel ===")
    raw = fetch_obf(args.n * 3, None, args.seed)
    items = []
    for it in raw:
        if len(items) >= args.n:
            break
        b64 = get_image(it["img"])
        if b64:
            it["b64"] = b64; items.append(it)
    print(f"  collected {len(items)} items")

    # rows in COMPARE framing: item = model (treatment), judge = product (condition), trials replicate
    rows = []
    for m in models:
        t0 = time.time()
        for it in items:
            for _ in range(args.trials):
                pred = ask_brand(m, [it["b64"]], args.temp)
                rows.append({"item": m, "judge": it["upc"],
                             "score": overlap(pred.get("brand"), it["brand"])})
        print(f"  {m:22s} done ({time.time()-t0:.0f}s)", flush=True)

    rep = msai.compare(rows, baseline=args.baseline, level="ordinal")
    rep.summary()

    out = {"framing": "item=model, judge=product(upc), trials=replicate brand-reads",
           "models": models, "baseline": args.baseline, "n_products": len(items),
           "trials": args.trials, "temp": args.temp,
           "gauge": rep.gauge, "comparisons": rep.comparisons, "notes": rep.notes,
           "raw_rows": rows}
    path = os.path.join(os.path.dirname(__file__), "phase4_compare_result.json")
    json.dump(out, open(path, "w"), indent=2, default=str)
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
