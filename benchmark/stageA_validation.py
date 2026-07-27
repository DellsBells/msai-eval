"""Stage A — the keystone: exercise the GUM U-band on a NON-FROZEN, graded task.

Per docs/NONFROZEN_VALIDATION_DESIGN.md. Brand-ID (Phase 4) was frozen + near-binary, so the
resolution/U-band tier (compare's whole reason to exist) was never tested. This is the fix:

  - GRADED: a judge panel scores listing QUALITY 1-5 against an anchored rubric (real resolution).
  - NON-FROZEN: subjective scoring at temp 0.7, >=3 trials -> real run-to-run repeatability.
  - A REAL DELTA TO RESOLVE: two generator configs with a deliberate quality gap (detailed prompt
    vs lazy prompt) so the gap exceeds the ~0.6 quantization floor on a 1-5 scale -> the U-band is
    actually on trial (resolve, not just refuse).

Refinements (from the gauge-track sign-off, baked in):
  1. judges emit INTEGER 1-5 and compare() is called with resolution=1.0 (no fractional-ordinal gate).
  2. the listing set spans a real quality range incl. borderline items (the lazy-config listings) so
     the panel actually wavers run-to-run (else frozen again).
  3. the config pair has a clear (>=~0.7) quality gap so the U-band RESOLVES, not just refuses.
The judge panel EXCLUDES the generator model (no self-judging / consensus circularity).

    .venv/bin/python benchmark/stageA_validation.py --n 6 --trials 3
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
import numpy as np
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_tier2 import fetch_obf
import msai_eval as msai

OLLAMA = "http://localhost:11434/api/chat"
GENERATOR = "qwen3.5:27b"                       # makes both listings; NOT on the judge panel
# Appraisers qualified in preflight (could follow the 1-5 quality rubric). LFM2 + resale-vlm-v2 were
# dropped: both scored a clearly-strong listing a 2, i.e. they don't track the rubric — you qualify
# appraisers before a Gage R&R. (Lineage diversity is thin here — 2 gemma / 2 qwen — noted as a caveat.)
JUDGES = ["gemma4:12b", "gemma4:31b-mlx", "qwen2.5vl:7b", "qwen3.6:35b-mlx"]

GOOD_PROMPT = ("Write a resale marketplace listing for this product. Give a clear, compelling TITLE, then a "
               "DESCRIPTION that covers the brand, the key features and benefits, likely condition notes, and "
               "why a buyer would want it. Be accurate, specific, and well-written.\n\nPRODUCT: {p}\n\nLISTING:")
LAZY_PROMPT = "write a listing for {p}"          # minimal guidance -> terse/generic/lower quality

JUDGE_RUBRIC = (
    "You are grading the QUALITY of a resale marketplace listing against this rubric:\n"
    "  5 = accurate, complete, well-written, genuinely sells the item\n"
    "  4 = good; accurate and clear, minor gaps\n"
    "  3 = usable; does the job but notable omissions or errors\n"
    "  2 = poor; missing or wrong key attributes\n"
    "  1 = unusable or misleading\n\n"
    "PRODUCT: {p}\n\nLISTING:\n{listing}\n\n"
    "Reply with ONLY the single integer 1, 2, 3, 4, or 5. No other text."
)


def _chat(model, prompt, temp, max_tokens, think=None):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "stream": False, "options": {"temperature": temp, "num_predict": max_tokens}}
    if think is not None:
        body["think"] = think
    r = requests.post(OLLAMA, json=body, timeout=300)
    m = r.json().get("message", {}) if r.status_code < 400 else {}
    return ((m.get("content") or "") or (m.get("thinking") or "")).strip()


def gen_listing(product, prompt_tmpl):
    try:
        return _chat(GENERATOR, prompt_tmpl.format(p=product), temp=0.6, max_tokens=320, think=False)
    except Exception as e:
        return f"[gen error: {e}]"


def judge_quality(judge, product, listing, temp):
    """One blind integer 1-5 quality rating. think=False so reasoning judges return a snap score."""
    msg = JUDGE_RUBRIC.format(p=product, listing=listing[:1400])
    for think in (False, None):                  # plain fallback for models without 'think'
        try:
            txt = _chat(judge, msg, temp=temp, max_tokens=16, think=think)
        except Exception:
            continue
        mt = re.search(r"[1-5]", txt)
        if mt:
            return int(mt.group())
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    print(f"=== Stage A: graded listing-quality, U-band on trial ===\n generator={GENERATOR}  "
          f"judges={JUDGES}\n configs=[good,weak]  {args.n} products x {args.trials} trials @ temp {args.temp}\n")

    prods = [f"{it['brand']} {it['name']}" for it in fetch_obf(args.n * 2, None, args.seed)[:args.n]]
    print(f"products ({len(prods)}):"); [print("  -", p[:60]) for p in prods]

    print("\n--- generating listings (good vs weak config) ---")
    listings = {}   # (config, pidx) -> text
    for pi, p in enumerate(prods):
        listings[("good", pi)] = gen_listing(p, GOOD_PROMPT)
        listings[("weak", pi)] = gen_listing(p, LAZY_PROMPT)
        print(f"  product {pi}: good={len(listings[('good',pi)])}c  weak={len(listings[('weak',pi)])}c", flush=True)

    print("\n--- judge panel scoring quality (1-5, temp>0, replicate trials) ---")
    raw = []   # {config, product, judge, trial, score}
    for cfg in ("good", "weak"):
        for pi, p in enumerate(prods):
            for jg in JUDGES:
                for t in range(args.trials):
                    s = judge_quality(jg, p, listings[(cfg, pi)], args.temp)
                    if s is not None:
                        raw.append({"config": cfg, "product": pi, "judge": jg, "trial": t, "score": s})
        print(f"  scored config={cfg}", flush=True)

    # listings-as-items (reliability / uncertainty): can the panel even measure listing quality?
    list_rows = [{"item": f"{r['config']}|{r['product']}", "judge": r["judge"], "score": r["score"]} for r in raw]
    # configs-as-treatments (compare): is good's quality > weak's beyond the gauge's U-band?
    cfg_rows = [{"item": r["config"], "judge": r["judge"], "score": r["score"]} for r in raw]

    print("\n" + "=" * 72 + "\n  MSAI STACK — STAGE A (non-frozen, graded)\n" + "=" * 72)
    rel = msai.reliability(list_rows, level="ordinal"); rel.summary()
    ub = msai.uncertainty_budget(list_rows, level="ordinal", resolution=1.0); ub.summary()
    cmp = msai.compare(cfg_rows, baseline="weak", level="ordinal", resolution=1.0); cmp.summary()

    qmean = {cfg: float(np.mean([r["score"] for r in raw if r["config"] == cfg])) for cfg in ("good", "weak")}
    print(f"\n  mean quality: good={qmean['good']:.2f}  weak={qmean['weak']:.2f}  gap={qmean['good']-qmean['weak']:.2f}")

    out = {"generator": GENERATOR, "judges": JUDGES, "n_products": len(prods), "trials": args.trials,
           "temp": args.temp, "mean_quality": qmean, "raw": raw,
           "reliability": rel.to_dict(), "uncertainty": ub.to_dict(), "compare": cmp.to_dict()}
    path = os.path.join(os.path.dirname(__file__), "stageA_result.json")
    json.dump(out, open(path, "w"), indent=2, default=str)
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
