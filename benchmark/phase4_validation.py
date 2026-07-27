"""Phase 4 — the whole MSAI stack on REAL data with a cross-source UPC reference.

The proof we kept deferring. Build a traceable Reference from TWO independent UPC sources
(Open Beauty Facts x upcitemdb) so u_ref reflects real cross-source (dis)agreement, run a panel
of local vision models on the real product photos with replicate trials (temp>0 = real
repeatability), and feed the lot through reliability / uncertainty_budget / proficiency.

The measurement: each model reads the brand off the photo; the score is the token-overlap of its
brand vs the OBF brand (continuous [0,1]). The Reference target is 1.0 (a perfect read), and its
per-item u_ref is small where OBF and upcitemdb agree, large where they disagree or only one source
exists -- so a model is faulted only where the truth itself is tight (the audit-hardened behavior,
now on real data).

    .venv/bin/python benchmark/phase4_validation.py --n 12 --trials 2
"""
from __future__ import annotations
import argparse, json, os, sys, time
import numpy as np
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import re
from run_benchmark import field_match, norm, GENERIC, PROMPT, OLLAMA
from run_tier2 import fetch_obf, get_image
import msai_eval as msai


def ask_brand(model, images, temp):
    """Like run_benchmark.ask_model but with a real temperature (so replicate trials vary)."""
    body = {"model": model, "messages": [{"role": "user", "content": PROMPT, "images": images}],
            "stream": False, "think": False, "options": {"temperature": temp, "num_predict": 200}}
    try:
        r = requests.post(OLLAMA, json=body, timeout=300)
        txt = ((r.json().get("message") or {}).get("content")) or ""
    except Exception as e:
        return {"_error": str(e)}
    m = re.search(r"\{.*\}", txt, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    g = lambda k: (re.search(rf'"{k}"\s*:\s*"([^"]*)"', txt, re.I) or [None, ""])[1]
    return {"brand": g("brand"), "product_type": g("product_type")}


def overlap(pred, ref):
    """Containment: fraction of reference brand tokens present in the prediction, in [0,1]."""
    a = set(norm(pred or "").split()); b = set(norm(ref or "").split())
    return (len(a & b) / len(b)) if b else 0.0


_VENDOR = re.compile(r"^(amazon\w*|walmart\w*|wal-?mart|ebay\w*|target\w*)[/:]\s*", re.I)


def canon_brand(s):
    """Canonicalize a catalog brand string: drop vendor prefixes ('AmazonUs/...'), take the last
    vendor segment, lowercase, strip punctuation. (upcitemdb often returns 'AmazonUs/<BRAND>'.)"""
    s = _VENDOR.sub("", (s or "").strip())
    s = s.split("/")[-1].split(":")[-1]
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def brands_agree(a, b):
    """Do two catalog brand strings denote the same brand? Robust to vendor prefixes and truncations
    (so 'AmazonUs/WELED' agrees with 'Weleda') — the source-matching artifact the review caught."""
    ca, cb = canon_brand(a), canon_brand(b)
    if not ca or not cb:
        return False
    if ca == cb:
        return True
    sa, sb = ca.replace(" ", ""), cb.replace(" ", "")
    if len(min(sa, sb, key=len)) >= 4 and (sa.startswith(sb) or sb.startswith(sa) or sa in sb or sb in sa):
        return True
    return bool(set(ca.split()) & set(cb.split()))


def upcitemdb_brand(upc):
    """Second independent UPC source (trial API, rate-limited)."""
    try:
        r = requests.get(f"https://api.upcitemdb.com/prod/trial/lookup?upc={upc}", timeout=15)
        if r.status_code == 200:
            its = r.json().get("items", [])
            if its:
                return ((its[0].get("brand") or "").strip()) or None
    except Exception:
        pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--models", default="resale-vlm-v2:12b,qwen3.5:27b,gemma4:12b")
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--temp", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    models = args.models.split(",")

    print("=== Phase 4: full MSAI stack on REAL UPC truth ===")
    print(f" models {models} x {args.trials} trials @ temp {args.temp}\n")

    raw = fetch_obf(args.n * 3, None, args.seed)
    items = []
    for it in raw:
        if len(items) >= args.n:
            break
        b64 = get_image(it["img"])
        if b64:
            it["b64"] = b64; items.append(it)
            print(f"  img ok {it['upc']:>14}  brand='{it['brand'][:22]}'  [{len(items)}/{args.n}]", flush=True)

    print("\n--- building the UPC reference (OBF x upcitemdb cross-check -> u_ref) ---")
    for it in items:
        udb = upcitemdb_brand(it["upc"]); time.sleep(0.4)
        if udb:
            agree = brands_agree(udb, it["brand"])   # vendor-prefix + truncation robust (the review's fix)
            it["u_ref"] = 0.05 if agree else 0.30
            it["src"] = "agree" if agree else f"DISAGREE (obf='{it['brand']}' vs udb='{udb}')"
        else:
            it["u_ref"] = 0.15; it["src"] = "OBF only (no 2nd source)"
        it["udb"] = udb
        print(f"  {it['upc']:>14}  u_ref={it['u_ref']:.2f}  {it['src']}", flush=True)

    print(f"\n--- running panel ({len(items)} items) ---")
    data, brand_pred = [], {}
    for m in models:
        t0 = time.time()
        for it in items:
            for _ in range(args.trials):
                pred = ask_brand(m, [it["b64"]], args.temp)
                data.append({"item": it["upc"], "judge": m, "score": overlap(pred.get("brand"), it["brand"])})
                brand_pred.setdefault((m, it["upc"]), []).append(pred.get("brand"))
        print(f"  {m:22s} done ({time.time()-t0:.0f}s)", flush=True)

    ref = msai.certified_reference({it["upc"]: 1.0 for it in items},
                                   u={it["upc"]: it["u_ref"] for it in items},
                                   source="UPC truth: OBF x upcitemdb")

    print("\n" + "=" * 72 + "\n  MSAI STACK ON REAL DATA\n" + "=" * 72)
    rep = msai.reliability(data, level="ordinal", reference=ref); rep.summary()
    ub = msai.uncertainty_budget(data, level="ordinal"); ub.summary()
    prof = msai.proficiency(data, level="ordinal", reference=ref); prof.summary()
    print("\n  READ THIS task as ACCURACY + bias, NOT the proficiency OUTLIER verdict: the Reference target")
    print("  is constant (1.0 = a perfect read) and the brand score is near-binary, so En reduces to")
    print("  distance-from-target (see the reference_constant warning). And brand-ID is intrinsically FROZEN")
    print("  (the read doesn't change run-to-run), so the resolution/guard-band tier is NOT exercised here.")

    print("\n--- per-model: mean brand-overlap + first-trial brand-match accuracy (field_match vs OBF) ---")
    per_model = {}
    for m in models:
        scs = [d["score"] for d in data if d["judge"] == m]
        accs = [field_match(brand_pred[(m, it["upc"])][0], it["brand"]) for it in items]
        per_model[m] = {"mean_overlap": float(np.mean(scs)), "brand_acc": float(np.mean(accs))}
        print(f"  {m:22s}  mean_overlap={np.mean(scs):.2f}   brand_acc={100*np.mean(accs):.0f}%")

    out = {"models": models, "n_items": len(items), "trials": args.trials, "temp": args.temp,
           "items": [{"upc": it["upc"], "obf_brand": it["brand"], "udb_brand": it.get("udb"),
                      "u_ref": it["u_ref"], "src": it["src"]} for it in items],
           "per_model": per_model, "data": data,   # raw (item,judge,score) so re-analysis needs no model re-run
           "reliability": rep.to_dict(), "uncertainty": ub.to_dict(), "proficiency": prof.to_dict()}
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "phase4_result.json"), "w"),
              indent=2, default=str)
    print("\nsaved -> benchmark/phase4_result.json")


if __name__ == "__main__":
    main()
