"""analyze_study.py — the §7 FROZEN analysis of the code-oracle anchor study.

Prereg 60c6525 (sha256 19bdfc44…14cd5, sealed REV-LANE #013). Estimands H1–H4 as frozen;
pipeline identical to the frontier certificate path: rows -> compare() (delta basis,
two-band gate, typed resolution_verdict from commit B) -> four_state under both dof modes.
Accuracy layer: reference.py with the oracle as certified reference — first run with a
real reference (spec §6.4 activates on the certificate rendered from this output).

DECLARED OPERATIONALIZATIONS (stated here, before results are consumed; the prereg froze
the estimands, not these unit maps — both are the a-priori obvious choices and neither
was tuned against data):
  * Panel/judge preference per task-pair: delta of mean ratings (A - B), on the 1-5 scale
    for compare(); normalized by the 4-point span (range -1..1) for the accuracy layer so
    it shares units with the oracle gap g = passrate_A - passrate_B (range -1..1).
  * Oracle u_ref: declared 0.0 for En computation. NOT silently — the residual is
    test-suite correctness risk, mitigated by adversarial verification (each suite
    survived a blind reimplementation + sneaky-wrong attack; the one suite that failed
    that gate, t36, is dead). Stated on the certificate, not assumed away.
  * DISCLOSURE: a labeled raw peek at direction statistics occurred post-data,
    pre-analysis (REV-LANE session log 2026-07-09). Analysis rules were sealed before
    any data existed; the peek changed nothing and is disclosed anyway.

Ingest is three-way per the adapter contract (KB #018 exhibit 1): VALID / EXCLUDED-AND-
DISCLOSED (None or NaN scores — 14 rows, judges shown degenerate cfg-B output) / REFUSE
(per-judge null rate >10% — not triggered: max 3.3%).
"""
from __future__ import annotations
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src"))

from msai_eval.compare import compare              # noqa: E402
from msai_eval.resolution import four_state        # noqa: E402
from msai_eval import reference as ref_mod         # noqa: E402

SCORES = os.path.join(HERE, "oracle_study_scores.json")
MANIFEST = os.path.join(HERE, "study_manifest.json")
OUT = os.path.join(HERE, "analysis_results.json")
SPAN = 4.0            # 1-5 rating scale span, the declared normalizer
NULL_REFUSE = 0.10
TIERS = ("resolve", "subtle", "tie")


# ---------- exact Jeffreys interval (no scipy: incomplete-beta CF + bisection) ----------
def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 200, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
          + a * math.log(x) + b * math.log(1.0 - x))
    front = math.exp(ln)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def _beta_ppf(q, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _ibeta(a, b, mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def jeffreys(k, n, cl=0.95):
    """Jeffreys interval for a binomial rate: Beta(k+0.5, n-k+0.5) central interval."""
    if n == 0:
        return (0.0, 1.0)
    al = (1.0 - cl) / 2.0
    lo = 0.0 if k == 0 else _beta_ppf(al, k + 0.5, n - k + 0.5)
    hi = 1.0 if k == n else _beta_ppf(1.0 - al, k + 0.5, n - k + 0.5)
    return (round(lo, 4), round(hi, 4))


# ---------- ingest (three-way) ----------
def _val(r):
    s = r["score"][0] if isinstance(r["score"], list) else r["score"]
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return None
    return float(s)


def main():
    with open(SCORES, encoding="utf-8") as f:
        d = json.load(f)
    with open(MANIFEST, encoding="utf-8") as f:
        man = json.load(f)["tasks"]
    meta = d["meta"]

    per_judge_counts = defaultdict(lambda: [0, 0])       # judge -> [valid, null]
    rows_by_tier = defaultdict(list)
    cell = defaultdict(list)                             # (task, cfg, judge) -> [scores]
    n_null = 0
    for r in d["scores"]:
        v = _val(r)
        per_judge_counts[r["judge"]][v is None] += 1
        if v is None:
            n_null += 1
            continue
        rows_by_tier[r["tier"]].append({"item": r["config"], "unit": r["task_id"],
                                        "judge": r["judge"], "score": v})
        cell[(r["task_id"], r["config"], r["judge"])].append(v)

    null_report = {}
    for j, (ok, nu) in per_judge_counts.items():
        rate = nu / (ok + nu)
        null_report[j] = {"nulls": nu, "of": ok + nu, "rate": round(rate, 4)}
        if rate > NULL_REFUSE:
            raise SystemExit(f"§5 REFUSAL: judge {j} null rate {rate:.1%} > {NULL_REFUSE:.0%}")

    judges = sorted({r["judge"] for r in d["scores"]})

    # ---------- per-tier compare() + four_state (frontier path) ----------
    # The crossed variance decomposition requires STRICT balance (equal valid replicates
    # in every task x config x judge cell). Judge nulls on degenerate cfg-B outputs broke
    # balance on some tasks; those UNITS are excluded from the tier GAUGE computation and
    # disclosed by name (absences propagate as exclusions, never as coerced values).
    # H1-H4 below are task-level estimands and use ALL valid ratings.
    counts = defaultdict(int)
    for (t, cfg, j), vs in cell.items():
        counts[(t, cfg, j)] = len(vs)
    balanced_excluded = defaultdict(list)
    task_tier = {t: e["tier"] for t, e in man.items()}
    for t, e in man.items():
        cs = [counts[(t, cfg, j)] for cfg in ("A", "B") for j in judges]
        if len(set(cs)) > 1 or min(cs) < 2:
            balanced_excluded[e["tier"]].append(t)
    tiers_out = {}
    for tier in TIERS:
        rows = [r for r in rows_by_tier.get(tier, [])
                if r["unit"] not in balanced_excluded[tier]]
        if not rows:
            continue
        c = compare(rows, baseline="B", level="ordinal", resolution=1.0).to_dict()
        cmp_ = c["comparisons"]["A"]
        g = c.get("gauge") or {}
        rb = g.get("resolution_budget")
        entry = {"delta": cmp_["delta"], "ci": cmp_.get("ci"),
                 "sig": bool(cmp_.get("significant_adj")),
                 "resolution_verdict": cmp_.get("resolution_verdict"),
                 "bands": cmp_.get("bands"), "qualified": bool(g.get("qualified")),
                 "n_pairs": len({r['unit'] for r in rows}),
                 "gauge_excluded_units": sorted(balanced_excluded[tier])}
        if entry["qualified"] and rb:
            entry["ws"] = four_state(entry["delta"], entry["ci"], rb, entry["sig"], dof_mode="ws")
            entry["dom"] = four_state(entry["delta"], entry["ci"], rb, entry["sig"],
                                      dof_mode="dominant")
        tiers_out[tier] = entry

    # ---------- panel deltas per task ----------
    def judge_delta(t, j):
        a = cell.get((t, "A", j), [])
        b = cell.get((t, "B", j), [])
        if not a or not b:
            return None
        return (sum(a) / len(a) - sum(b) / len(b))

    def panel_delta(t):
        ds = [x for j in judges if (x := judge_delta(t, j)) is not None]
        return sum(ds) / len(ds) if ds else None

    # H1 — sanity: sign agreement on resolve pairs
    res_ids = [t for t, e in man.items() if e["tier"] == "resolve"]
    h1_n = h1_k = 0
    for t in res_ids:
        pd = panel_delta(t)
        if pd is None or man[t]["g"] == 0:
            continue
        h1_n += 1
        h1_k += (pd * man[t]["g"]) > 0
    h1 = {"agree": h1_k, "n": h1_n, "rate": round(h1_k / h1_n, 4) if h1_n else None,
          "jeffreys95": jeffreys(h1_k, h1_n), "frozen_prediction": ">=0.90",
          "pass": (h1_k / h1_n >= 0.90) if h1_n else None}

    # H3 — THE HEADLINE: consensus-wrong rate per tier (+ shared-vs-idiosyncratic)
    h3 = {}
    for tier in TIERS:
        tids = [t for t, e in man.items() if e["tier"] == tier and e["g"] != 0]
        wrongs = []
        for t in tids:
            pd = panel_delta(t)
            if pd is None:
                continue
            if pd * man[t]["g"] < 0:
                jd = {j: judge_delta(t, j) for j in judges}
                wrong_js = [j for j, x in jd.items() if x is not None and x * man[t]["g"] < 0]
                wrongs.append({"task": t, "g": man[t]["g"], "panel_delta": round(pd, 3),
                               "judges_wrong": wrong_js,
                               "shared": len(wrong_js) >= 2})
        k, n = len(wrongs), len(tids)
        h3[tier] = {"consensus_wrong": k, "n": n,
                    "rate": round(k / n, 4) if n else None,
                    "jeffreys95": jeffreys(k, n) if n else None,
                    "events": wrongs}
    all_k = sum(v["consensus_wrong"] for v in h3.values())
    all_n = sum(v["n"] for v in h3.values())
    h3["pooled"] = {"consensus_wrong": all_k, "n": all_n,
                    "rate": round(all_k / all_n, 4) if all_n else None,
                    "jeffreys95": jeffreys(all_k, all_n)}

    # H2 — keystone: subtle tier reads BELOW/AT-EDGE while the ORACLE certifies real gaps
    sub_ids = [t for t, e in man.items() if e["tier"] == "subtle"]
    sub_state = (tiers_out.get("subtle", {}).get("resolution_verdict") or {}).get("state")
    h2 = {"subtle_tier_state": sub_state,
          "oracle_gaps": {t: man[t]["g"] for t in sub_ids},
          "keystone_demonstrated": sub_state in ("BELOW", "AT-EDGE"),
          "reading": "oracle certifies nonzero gaps on every subtle pair while the panel's "
                     "verdict state refuses to certify magnitude — the refusal is calibrated "
                     "against truth, not just consensus"
          if sub_state in ("BELOW", "AT-EDGE") else "keystone NOT shown on this data"}

    # H4 — per-judge En against the oracle reference (accuracy layer, u_ref declared 0)
    all_ids = [t for t in man]
    ref = ref_mod.certified_reference({t: man[t]["g"] for t in all_ids}, u=0.0,
                                      source="oracle: hidden pytest suites, adversarially verified")
    h4 = {}
    for j in judges:
        preds, u_pred = {}, {}
        for t in all_ids:
            jd = judge_delta(t, j)
            if jd is None:
                continue
            preds[t] = jd / SPAN
            a = cell.get((t, "A", j), [])
            b = cell.get((t, "B", j), [])
            reps = min(len(a), len(b))
            if reps >= 2:
                dl = [(a[i] - b[i]) / SPAN for i in range(reps)]
                m = sum(dl) / reps
                sd = math.sqrt(sum((x - m) ** 2 for x in dl) / (reps - 1))
                u_pred[t] = sd / math.sqrt(reps)
            else:
                u_pred[t] = 0.0
        sc = ref_mod.score(ref, preds, u_pred=u_pred, k=2.0)
        ens = [p["En"] for p in sc.get("per_item", []) if isinstance(p["En"], float)]
        h4[j] = {"n": sc.get("n"), "conformance_rate": sc.get("conformance_rate"),
                 "en_pass_rate": sc.get("en_pass_rate"),
                 "max_abs_En": round(max((abs(e) for e in ens), default=0.0), 2),
                 "flagged_|En|>1": sorted(p["item"] for p in sc.get("per_item", [])
                                          if isinstance(p["En"], float) and abs(p["En"]) > 1),
                 "verdict": sc.get("verdict"), "warnings": sc.get("warnings", [])}

    out = {"meta_in": {k: meta.get(k) for k in ("prereg_sha256", "prereg_commit",
                                                "corpus_commit", "panel_alive",
                                                "panel_excluded", "judge_R", "tiers",
                                                "quarantined", "degrade_level")},
           "ingest": {"rows": len(d["scores"]), "nulls_excluded_disclosed": n_null,
                      "per_judge": null_report},
           "tiers": tiers_out, "H1": h1, "H2": h2, "H3": h3, "H4": h4,
           "declared": {"span_normalizer": SPAN, "u_ref": 0.0,
                        "u_ref_residual": "test-suite correctness; adversarially verified, "
                                          "t36 excluded by that gate; stated not assumed",
                        "peek_disclosure": "labeled direction-stats peek post-data pre-analysis"}}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"tiers": {k: {kk: v.get(kk) for kk in ("delta", "sig")}
                                for k, v in tiers_out.items()},
                      "verdicts": {k: (v.get("resolution_verdict") or {}).get("state")
                                   for k, v in tiers_out.items()},
                      "H1": {k: h1[k] for k in ("rate", "jeffreys95", "pass")},
                      "H2": h2["keystone_demonstrated"],
                      "H3_pooled": h3["pooled"],
                      "H3_by_tier": {t: {"rate": h3[t]["rate"], "ci": h3[t]["jeffreys95"],
                                         "k": h3[t]["consensus_wrong"], "n": h3[t]["n"]}
                                     for t in TIERS if t in h3},
                      "H4": {j.split('/')[-1][:20]: {"En_pass": h4[j]["en_pass_rate"],
                                                     "flags": len(h4[j]["flagged_|En|>1"])}
                             for j in h4},
                      "out": OUT}, indent=1))


if __name__ == "__main__":
    main()
