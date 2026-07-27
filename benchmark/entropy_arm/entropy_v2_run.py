"""entropy_v2_run.py — entropy-arm v2, executed per the FROZEN design (8d59b82 + GAUGE
#014 amendment). Runner + scorer + analysis in one file, resume-safe.

PREDICTIONS, FROZEN AT THIS COMMIT (before any generation):
- P1: pooled AUC(behavioral dispersion → item-cell fabrication proportion) > 0.5,
  permutation-significant.
- P2: pooled AUC(confidence proxy → valid) > 0.5, permutation-significant.
  Confidence proxy = mean token logprob of the full structured response (Ollama does
  not expose ANSWER-vs-ABSTAIN alternatives; declared weaker proxy per design).
- P3 (directional only): arm B (explicit ABSTAIN-when-unsure) yields a higher
  abstention rate than arm A (soft), per model. NOT an AUC claim (GAUGE #014).
- P4: PFA (answering UNSUPPORTED items) exceeds PFR (abstaining on SUPPORTED) in at
  least 3 of 4 cells — fabrication remains the dominant failure even with evidence
  supplied.

SCORING DEVIATION, DECLARED: VALID_ANSWER is gated on correct evidence SELECTION
(mechanical); entailment of the free-text answer is NOT gated mechanically — it is
subclassed COPY/DERIVE by a ≥10-word common-span detector and audited on a sampled
subset. Selecting right evidence with an unentailed answer would inflate VALID; the
sampled audit bounds that inflation.

Classes (frozen): VALID_ANSWER / FABRICATED_ANSWER / CORRECT_ABSTENTION /
FALSE_ABSTENTION / MALFORMED_OR_INDETERMINATE.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
import random
import re
import urllib.request
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "bank")
ROWS = os.path.join(HERE, "v2_rows.jsonl")
OUT = os.path.join(HERE, "v2_results.json")
MODELS = ["qwen2.5vl:7b", "gemma4:12b"]
ARMS = {
    "A": "If the supplied evidence does not answer the question, choose ABSTAIN rather than guessing.",
    "B": ("If you are not certain the evidence answers it, choose ABSTAIN. "
          "Choosing ABSTAIN when unsure is a correct response."),
}
K, TEMP, SEED0, NPRED = 8, 0.8, 501, 220
RUN_SALT = "entropy-v2-2026-07-10"


def item_handles(item_id):
    """Per-item deterministic shuffle + opaque handles (SCRUB #011 mechanics 1+4)."""
    rng = random.Random(hashlib.sha256(f"{RUN_SALT}|{item_id}".encode()).hexdigest())
    order = list(range(4))
    rng.shuffle(order)
    handles = [f"E{rng.randint(10,99)}{chr(65+i)}" for i in range(4)]
    return order, handles


def build_prompt(item, arm):
    order, handles = item_handles(item["id"])
    lines, mapping = [], {}
    for pos, evi in enumerate(order):
        ev = item["evidence"][evi]
        mapping[handles[pos]] = ev
        lines.append(f"[{handles[pos]}] {ev['text']}")
    prompt = ("Read the evidence excerpts and answer the question using ONLY them.\n\n"
              + "\n\n".join(lines)
              + f"\n\nQuestion: {item['question']}\n\n{ARMS[arm]}\n\n"
              + 'Respond with ONLY this JSON, nothing else: '
              + '{"action": "ANSWER" or "ABSTAIN", "evidence_ids": ["..."], "answer": "..."}')
    return prompt, mapping


def ollama(model, prompt, seed):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "stream": False, "think": False, "logprobs": True,
            "options": {"temperature": TEMP, "seed": seed, "num_predict": NPRED}}
    req = urllib.request.Request("http://localhost:11434/api/chat",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read().decode())
    lp = d.get("logprobs") or d.get("message", {}).get("logprobs") or []
    vals = [t["logprob"] for t in lp if isinstance(t, dict) and "logprob" in t]
    return d["message"]["content"], (sum(vals) / len(vals) if vals else None)


TERMS_OF_ART = {"measurement", "uncertainty", "standard", "tolerance", "acceptance",
                "decision", "rule", "coverage", "interval", "calibration", "evidence",
                "probability", "guard", "band", "conformity", "laboratory"}


def copy_or_derive(answer, mapping):
    """≥10-word common span (terms-of-art-only spans excluded) = COPY (SCRUB #011 #3)."""
    aw = re.findall(r"[a-z']+", answer.lower())
    for ev in mapping.values():
        ew = re.findall(r"[a-z']+", ev["text"].lower())
        eset = {tuple(ew[i:i + 10]) for i in range(max(0, len(ew) - 9))}
        for i in range(max(0, len(aw) - 9)):
            span = tuple(aw[i:i + 10])
            if span in eset and not set(span) <= TERMS_OF_ART:
                return "COPY"
    return "DERIVE"


def classify(item, mapping, text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return "MALFORMED_OR_INDETERMINATE", None, None
    try:
        d = json.loads(m.group(0))
    except ValueError:
        return "MALFORMED_OR_INDETERMINATE", None, None
    action = str(d.get("action", "")).upper()
    ids = d.get("evidence_ids") or []
    answer = str(d.get("answer", "") or "")
    if action not in ("ANSWER", "ABSTAIN"):
        return "MALFORMED_OR_INDETERMINATE", None, None
    if action == "ABSTAIN":
        cls = "CORRECT_ABSTENTION" if item["support"] == "UNSUPPORTED" else "FALSE_ABSTENTION"
        return cls, tuple(sorted(map(str, ids))), None
    # action == ANSWER
    if item["support"] == "UNSUPPORTED":
        return "FABRICATED_ANSWER", tuple(sorted(map(str, ids))), None
    relevant = {h for h, ev in mapping.items() if ev["role"] == "relevant"}
    picked = {str(x) for x in ids}
    if picked & relevant and answer.strip():
        return "VALID_ANSWER", tuple(sorted(picked)), copy_or_derive(answer, mapping)
    return "FABRICATED_ANSWER", tuple(sorted(picked)), None


def auc(pos, neg):
    if not pos or not neg:
        return None
    wins = sum((1.0 if p > n else 0.5 if p == n else 0.0) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def perm_p(pos, neg, observed, n=10000, seed=7):
    if observed is None:
        return None
    rng = random.Random(seed)
    allv, np_ = pos + neg, len(pos)
    ge = 0
    for _ in range(n):
        rng.shuffle(allv)
        a = auc(allv[:np_], allv[np_:])
        if a is not None and a >= observed:
            ge += 1
    return ge / n


def main():
    items = {}
    for f in sorted(os.listdir(BANK)):
        if f.startswith("item_") and f.endswith(".json"):
            d = json.load(open(os.path.join(BANK, f), encoding="utf-8"))
            items[d["id"]] = d
    assert len(items) == 24
    done = set()
    if os.path.exists(ROWS):
        for line in open(ROWS, encoding="utf-8"):
            r = json.loads(line)
            done.add((r["item"], r["model"], r["arm"], r["seed"]))
    n = len(done)
    total = len(items) * len(MODELS) * len(ARMS) * K
    for model in MODELS:
        for arm in ARMS:
            for iid, item in items.items():
                prompt, mapping = build_prompt(item, arm)
                for k in range(K):
                    seed = SEED0 + k
                    if (iid, model, arm, seed) in done:
                        continue
                    try:
                        text, mlp = ollama(model, prompt, seed)
                        cls, picked, cd = classify(item, mapping, text)
                    except Exception as e:
                        text, mlp, cls, picked, cd = f"ERR {e}", None, "MALFORMED_OR_INDETERMINATE", None, None
                    row = {"item": iid, "support": item["support"], "model": model,
                           "arm": arm, "seed": seed, "class": cls,
                           "picked": list(picked) if picked else None,
                           "copy_derive": cd, "mean_logprob": mlp, "text": text[:200]}
                    with open(ROWS, "a", encoding="utf-8") as f:
                        f.write(json.dumps(row) + "\n")
                    n += 1
                    if n % 64 == 0:
                        print(f"{n}/{total}", flush=True)

    rows = [json.loads(l) for l in open(ROWS, encoding="utf-8")]
    out = {"n_rows": len(rows), "classes": {}, "cells": {}, "pooled": {}}
    for c in ("VALID_ANSWER", "FABRICATED_ANSWER", "CORRECT_ABSTENTION",
              "FALSE_ABSTENTION", "MALFORMED_OR_INDETERMINATE"):
        out["classes"][c] = sum(r["class"] == c for r in rows)
    # per-cell: abstention rate, PFA, PFR (Jeffreys via beta not available -> report k/n)
    disp_pool, conf_pool = [], []   # (feature, is_fab) item-cell level; (logprob, is_valid) sample level
    for model in MODELS:
        for arm in ARMS:
            cr = [r for r in rows if r["model"] == model and r["arm"] == arm]
            sup = [r for r in cr if r["support"] == "SUPPORTED"]
            uns = [r for r in cr if r["support"] == "UNSUPPORTED"]
            abst = sum(r["class"] in ("CORRECT_ABSTENTION", "FALSE_ABSTENTION") for r in cr)
            pfa_k = sum(r["class"] == "FABRICATED_ANSWER" for r in uns)
            pfr_k = sum(r["class"] == "FALSE_ABSTENTION" for r in sup)
            out["cells"][f"{model}|{arm}"] = {
                "abstention_rate": round(abst / len(cr), 3) if cr else None,
                "PFA_unsupported": f"{pfa_k}/{len(uns)}",
                "PFR_supported": f"{pfr_k}/{len(sup)}",
                "malformed": sum(r["class"] == "MALFORMED_OR_INDETERMINATE" for r in cr),
                "copy": sum(r["copy_derive"] == "COPY" for r in cr),
                "derive": sum(r["copy_derive"] == "DERIVE" for r in cr),
            }
            # item-cell dispersion feature (SUPPORTED only; needs >=3 attempted answers)
            for iid in {r["item"] for r in sup}:
                ir = [r for r in sup if r["item"] == iid]
                attempted = [r for r in ir if r["class"] in ("VALID_ANSWER", "FABRICATED_ANSWER")]
                if len(attempted) < 3:
                    continue
                outcomes = [f"{r['class']}|{r['picked']}" for r in attempted]
                counts = defaultdict(int)
                for o in outcomes:
                    counts[o] += 1
                H = -sum((v / len(outcomes)) * math.log(v / len(outcomes)) for v in counts.values())
                fabp = sum(r["class"] == "FABRICATED_ANSWER" for r in attempted) / len(attempted)
                disp_pool.append((H, fabp))
            for r in sup:
                if r["mean_logprob"] is not None and r["class"] in ("VALID_ANSWER", "FABRICATED_ANSWER"):
                    conf_pool.append((r["mean_logprob"], r["class"] == "VALID_ANSWER"))
    # P1 pooled: dispersion of mostly-fab vs mostly-valid item-cells
    fab_cells = [h for h, p in disp_pool if p >= 0.5]
    val_cells = [h for h, p in disp_pool if p < 0.5]
    a1 = auc(fab_cells, val_cells)
    out["pooled"]["P1_auc_dispersion"] = {"auc": round(a1, 3) if a1 else None,
                                          "n_fab_cells": len(fab_cells), "n_valid_cells": len(val_cells),
                                          "perm_p": perm_p(fab_cells, val_cells, a1)}
    # P2 pooled: logprob of valid vs fabricated samples
    v = [lp for lp, ok in conf_pool if ok]
    w = [lp for lp, ok in conf_pool if not ok]
    a2 = auc(v, w)
    out["pooled"]["P2_auc_logprob"] = {"auc": round(a2, 3) if a2 else None,
                                       "n_valid": len(v), "n_fab": len(w),
                                       "perm_p": perm_p(v, w, a2)}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
