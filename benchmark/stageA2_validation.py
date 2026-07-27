"""Stage A2 — the predictive-validity GATE for MSAI's resolution / guard-band tier.

Per the gauge<->modules agreement. This is the only test that gates MSAI's distinctive claim (the
judge-reproducibility-dominated guard band), as opposed to the lever/brand test which gates the
statistical-CI + accuracy-vs-truth tiers only.

Design:
  - GRADED listing-quality, 1-5 anchored rubric, judge panel @ temp 0.7, replicate trials (non-frozen).
  - A LADDER of generator configs (excellent/good/mediocre/terrible prompts) so the 6 pairwise quality
    gaps SPAN the resolution boundary -> MSAI emits BOTH 'REAL' and 'within-noise' calls (needed for a
    separation test, not a single anecdote).
  - TWO independent product samples (different draws). Record MSAI's verdict + bootstrap CI per pair on
    sample 1; measure the held-out delta on sample 2.

Criterion (modules track, accepted):
  - replicated/STABLE = sample-2 delta point estimate lands INSIDE sample-1's bootstrap CI; bounces = outside.
  - PASS = REAL-called pairs are STABLE at a materially higher rate than within-noise-called pairs
    (separation), AND MSAI beats naive significance (>=1 p<.05 pair whose held-out delta bounces).
    No separation => the verdicts add no information => placebo.
  - POWER caveat: a handful of pairs is a DIRECTIONAL first look, not a rate.

    .venv/bin/python benchmark/stageA2_validation.py --n 5 --trials 2           # collect + analyze
    .venv/bin/python benchmark/stageA2_validation.py --analyze-only             # re-analyze saved raw
"""
from __future__ import annotations
import argparse, json, os, sys, itertools
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_tier2 import fetch_obf
from stageA_validation import gen_listing, judge_quality  # reuse generator + judge helpers
import msai_eval as msai

JUDGES = ["gemma4:12b", "qwen2.5vl:7b", "qwen3.6:35b-mlx"]   # diverse, qualified; generator excluded
CONFIGS = ["terrible", "mediocre", "good", "excellent"]      # quality ladder (worst -> best)
LADDER = {
    "excellent": ("Write a resale marketplace listing for this product: a clear, compelling TITLE and a "
                  "DESCRIPTION covering the brand, key features/benefits, likely condition notes, and why a "
                  "buyer would want it. Be accurate, specific, and well-written.\n\nPRODUCT: {p}\n\nLISTING:"),
    "good":      "Write a resale listing (a title and a few sentences) for: {p}",
    "mediocre":  "write a short listing for {p}",
    "terrible":  "name this product in one word: {p}",       # degenerate -> near floor quality
}
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stageA2_raw.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stageA2_result.json")


def collect(n, trials, temp, seeds):
    raw = []   # {sample, config, product, judge, trial, score}
    for si, seed in enumerate(seeds):
        prods = [f"{it['brand']} {it['name']}" for it in fetch_obf(n * 2, None, seed)[:n]]
        print(f"\n=== sample {si} (seed {seed}), {len(prods)} products ===")
        listings = {}
        for pi, p in enumerate(prods):
            for cfg in CONFIGS:
                listings[(cfg, pi)] = gen_listing(p, LADDER[cfg])
            print(f"  generated product {pi}", flush=True)
        for cfg in CONFIGS:
            for pi, p in enumerate(prods):
                for jg in JUDGES:
                    for t in range(trials):
                        s = judge_quality(jg, p, listings[(cfg, pi)], temp)
                        if s is not None:
                            raw.append({"sample": si, "config": cfg, "product": pi,
                                        "judge": jg, "trial": t, "score": s})
            print(f"  scored config={cfg} (sample {si})", flush=True)
    json.dump(raw, open(RAW, "w"), indent=0)
    print(f"\nsaved raw -> {RAW}")
    return raw


def _rows(raw, sample):
    return [{"item": r["config"], "judge": r["judge"], "score": r["score"]} for r in raw if r["sample"] == sample]


def _pair_delta_ci(rows, A, B, n_boot=2000, seed=0):
    """delta = mean(A) - mean(B), bootstrap CI by resampling judges paired across configs (mirrors compare)."""
    by = {}
    for r in rows:
        by.setdefault((r["item"], r["judge"]), []).append(r["score"])
    judges = sorted({j for (_, j) in by})
    def mean_over(cfg, js):
        vals = [v for j in js for v in by.get((cfg, j), [])]
        return float(np.mean(vals)) if vals else float("nan")
    d_obs = mean_over(A, judges) - mean_over(B, judges)
    rng = np.random.default_rng(seed)
    boot = []
    for _ in range(n_boot):
        js = [judges[i] for i in rng.integers(0, len(judges), len(judges))]
        d = mean_over(A, js) - mean_over(B, js)
        if not np.isnan(d):
            boot.append(d)
    lo, hi = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))) if boot else (float("nan"),) * 2
    return d_obs, (lo, hi)


def analyze(raw):
    out = {"judges": JUDGES, "configs": CONFIGS, "pairs": {}, "samples": {}}
    gauge_U = {}
    for s in (0, 1):
        rows = _rows(raw, s)
        rep = msai.compare(rows, baseline=CONFIGS[0], level="ordinal", resolution=1.0)
        gauge_U[s] = rep.gauge.get("guard_band")
        qmean = {c: float(np.mean([r["score"] for r in raw if r["sample"] == s and r["config"] == c]))
                 for c in CONFIGS}
        out["samples"][str(s)] = {"guard_band_U": gauge_U[s], "qualified": rep.gauge["qualified"],
                                  "mean_quality": qmean,
                                  "warnings": [w[:60] for w in rep.gauge["warnings"]]}
    # per pair: sample-1 call + CI, sample-2 delta, stability
    rows0, rows1 = _rows(raw, 0), _rows(raw, 1)
    U0 = gauge_U[0]
    for A, B in itertools.combinations(CONFIGS, 2):
        d0, ci0 = _pair_delta_ci(rows0, A, B)
        d1, _ = _pair_delta_ci(rows1, A, B)
        sig0 = bool(ci0[0] > 0 or ci0[1] < 0)                       # naive: sample-1 CI excludes 0
        beyond0 = bool(U0 is not None and abs(d0) > U0)
        if not out["samples"]["0"]["qualified"]:
            call = "provisional"
        elif sig0 and beyond0:
            call = "REAL"
        elif sig0:
            call = "within-resolution (significant but below guard band)"
        else:
            call = "within-noise"
        stable = bool(ci0[0] <= d1 <= ci0[1])                       # held-out delta inside sample-1 CI
        out["pairs"][f"{A}|{B}"] = {"delta_s1": round(d0, 3), "ci_s1": [round(ci0[0], 3), round(ci0[1], 3)],
                                    "delta_s2": round(d1, 3), "naive_significant": sig0,
                                    "msai_call": call, "stable": stable}
    # separation
    pr = out["pairs"]
    real = [p for p in pr.values() if p["msai_call"] == "REAL"]
    wn = [p for p in pr.values() if p["msai_call"] in ("within-noise", "within-resolution (significant but below guard band)")]
    sig = [p for p in pr.values() if p["naive_significant"]]
    def rate(g): return (sum(p["stable"] for p in g) / len(g)) if g else None
    out["separation"] = {
        "n_pairs": len(pr),
        "REAL_stable_rate": rate(real), "n_REAL": len(real),
        "within_noise_stable_rate": rate(wn), "n_within_noise": len(wn),
        "naive_significant_stable_rate": rate(sig), "n_naive_sig": len(sig),
        "msai_beats_naive": bool([p for p in sig if not p["stable"] and p["msai_call"] != "REAL"]),
    }
    json.dump(out, open(OUT, "w"), indent=2)
    print("\n" + "=" * 70 + "\n  STAGE A2 — predictive-validity (guard-band resolution tier)\n" + "=" * 70)
    for s in ("0", "1"):
        g = out["samples"][s]
        print(f"  sample {s}: U={g['guard_band_U']}, qualified={g['qualified']}, quality={ {k:round(v,2) for k,v in g['mean_quality'].items()} }")
    print("\n  PAIRS (sample-1 call -> held-out stability):")
    for k, p in pr.items():
        print(f"    {k:22s} Δs1={p['delta_s1']:+.2f} CI[{p['ci_s1'][0]:+.2f},{p['ci_s1'][1]:+.2f}] "
              f"Δs2={p['delta_s2']:+.2f}  {p['msai_call']:<48s} stable={p['stable']}")
    sp = out["separation"]
    print(f"\n  SEPARATION: REAL stable {sp['REAL_stable_rate']} (n={sp['n_REAL']})  vs  "
          f"within-noise stable {sp['within_noise_stable_rate']} (n={sp['n_within_noise']})")
    print(f"  naive-significant stable {sp['naive_significant_stable_rate']} (n={sp['n_naive_sig']})  "
          f"| MSAI beats naive (downgraded a significant non-replicator): {sp['msai_beats_naive']}")
    print(f"\n  saved -> {OUT}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--seeds", default="0,101")
    ap.add_argument("--analyze-only", action="store_true")
    args = ap.parse_args()
    if args.analyze_only:
        raw = json.load(open(RAW))
    else:
        raw = collect(args.n, args.trials, args.temp, [int(s) for s in args.seeds.split(",")])
    analyze(raw)


if __name__ == "__main__":
    main()
