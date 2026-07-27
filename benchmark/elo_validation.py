"""elo_validation.py — RewardBench-anchored resolution-tier validation, rebuilt around a CORRECT gauge.

Closes the 18 audit findings (locked in tests/test_elo_harness_claims.py). The corrected measurement model:

  rows = {item: chosen|rejected, unit: pair_id, judge, score}, with R>=2 re-scorings at temperature>0.

  - `unit`=pair  -> compare() decomposes BETWEEN-PAIR spread into item variance (EXCLUDED from gauge noise),
                    so prompt heterogeneity is no longer mislabeled as repeatability.
  - R>=2 temp>0  -> GENUINE repeatability (the same response re-scored), not the temp-0 fiction.
  - reproducibility floor -> a clone / shared-bias panel (judges never disagree) VOIDs, never PASSES.
  - explicit tier ROLES   -> the 'resolve' tier must read beyond-gauge, the 'below' tier must read real-but-
                             below-resolution, the 'sham' tier must read within-noise on a QUALIFIED gauge.
  - robust 1-5 parse; dead / degenerate / partially-dropped judges surfaced and VOIDed; compare() gauge
    warnings surfaced; monotonicity from BALANCED per-judge means.

Ladders: constructed_ladder() (q-driven, for the stub logic test) | rewardbench_ladder() (real, external).
"""
from __future__ import annotations
import collections
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import msai_eval as msai

OLLAMA = "http://localhost:11434/api/generate"
JUDGE_TEMP = 0.6   # the repeatability dial (Fable's critique): temperature INJECTS the repeatability noise that
                   # sets the guard band. Swept (--temp) to check the keystone verdict is robust, not dial-set.
RB_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rewardbench_filtered.json")
RB_MODELS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rewardbench_models.json")
ARENA_ELO_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arena_elo.json")
MTBENCH_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mtbench_ladder_pairs.json")


# ── score parsing ────────────────────────────────────────────────────────────────────────────────────
def parse_rating(text):
    """Parse a standalone 1-5 rating. Rejects fractions/percentages/multi-digit so a non-conforming reply
    surfaces as nan (-> dead judge) instead of a silent mis-score. '4/5'->4, '8/10'->nan, 'a 1-5 scale: 4'->4,
    'I cannot rate'->nan."""
    if not text:
        return float("nan")
    s = str(text).strip()
    if re.fullmatch(r"[1-5]", s):
        return float(s)
    m5 = re.search(r"\b([1-5])\s*(?:/\s*5|\s+out\s+of\s+5)\b", s)   # out-of-5: "4/5" or worded "4 out of 5" (REV-005)
    if m5:
        return float(m5.group(1))
    t = re.sub(r"\d+\s*/\s*\d+|\d+\s*%|\d{2,}", " ", s)  # drop other fractions, percents, multi-digit
    found = re.findall(r"(?<![\d.])([1-5])(?![\d.])", t)
    return float(found[-1]) if found else float("nan")


# ── judges ───────────────────────────────────────────────────────────────────────────────────────────
def stub_judge(judge, prompt, response, q, seed):
    """Logic-test judge: true quality q + per-(judge,response,seed) noise. The seed varies per repeat so
    re-scorings genuinely differ (simulated repeatability). NOT a model."""
    rng = np.random.default_rng(abs(hash((judge, prompt, response, seed))) % (2 ** 32))
    return float(np.clip(round(q + rng.normal(0, 0.4)), 1, 5))


def ollama_judge(model, prompt, response, q, seed):
    """Real judge. temperature>0 + per-repeat seed => genuine re-scoring noise for the repeatability term."""
    import urllib.request
    p = (f"Rate the QUALITY of this answer to the prompt on a 1-5 scale (5=excellent, 1=poor). "
         f"Reply with ONLY the digit.\n\nPROMPT: {prompt}\n\nANSWER: {response}\n\nQuality (1-5):")
    body = json.dumps({"model": model, "prompt": p, "stream": False, "think": False, "keep_alive": "10m",
                       "options": {"temperature": JUDGE_TEMP, "seed": int(seed), "num_predict": 8}}).encode()
    try:
        r = json.loads(urllib.request.urlopen(
            urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"}), timeout=300).read())
        return parse_rating(r.get("response", ""))
    except Exception:
        return float("nan")


# ── ladders ──────────────────────────────────────────────────────────────────────────────────────────
def constructed_ladder():
    """Tiny q-driven ladder for the stub LOGIC test (no model). Roles: resolve / below / sham. The sham is
    equal-quality but DIFFERENTLY-worded (not byte-identical), so it probes whether the panel fabricates a
    gap between equivalent answers."""
    def P(prompt, ch, rj, qc, qr):
        return {"prompt": prompt, "chosen": ch, "rejected": rj, "q_chosen": qc, "q_rejected": qr}
    return [
        {"name": "large", "role": "resolve", "pairs": [
            P("Why is the sky blue?", "Rayleigh scattering: short blue wavelengths scatter ~1/λ⁴ more than red.",
              "Because the ocean reflects up onto it.", 5, 1),
            P("17 × 24?", "408 (17×20=340, +17×4=68).", "Around 350-ish.", 5, 2),
            P("Summarize the water cycle.", "Evaporation, condensation, precipitation, collection — sun-driven.",
              "Water moves around somehow.", 5, 2)]},
        {"name": "hard", "role": "below", "pairs": [
            P("Why is the sky blue?", "Blue light scatters more than red in the air, so the sky looks blue.",
              "The atmosphere scatters sunlight and blue is most visible.", 4, 3),
            P("17 × 24?", "17 × 24 = 408.", "It's 408.", 4, 4),
            P("Summarize the water cycle.", "Water evaporates, forms clouds, rains, returns to the sea.",
              "Evaporation then rain then back to rivers.", 4, 3)]},
        {"name": "sham", "role": "sham", "pairs": [
            P("Why is the sky blue?", "Blue light scatters more than red in the atmosphere.",
              "In the atmosphere, blue scatters more than red light.", 4, 4),
            P("17 × 24?", "The product is 408.", "It equals 408.", 4, 4),
            P("Summarize the water cycle.", "Evaporation, condensation, precipitation, collection.",
              "Precipitation, collection, evaporation, condensation.", 4, 4)]},
    ]


def rewardbench_ladder(n_per_tier=5, seed=0):
    """Real, external-anchored ladder from RewardBench. Subsets carry a known difficulty gradient:
      resolve (clear gap)  <- alpacaeval-easy, mt-bench-easy
      below   (subtle gap) <- llmbar-adver-neighbor/manual, mt-bench-hard  (adversarial: worse answer looks good)
    The chosen>rejected direction is the human-anchored truth. The SHAM pairs a chosen answer with ITSELF
    (scored independently at temp>0) — a true zero-gap control that the gauge must read 'within noise'."""
    rows = json.load(open(RB_JSON))
    by_sub = collections.defaultdict(list)
    for r in rows:
        by_sub[r["subset"]].append(r)
    rng = np.random.default_rng(seed)

    def take(subsets, n):
        pool = [r for s in subsets for r in by_sub.get(s, [])]
        idx = rng.choice(len(pool), size=min(n, len(pool)), replace=False)
        return [pool[i] for i in idx]

    easy = take(["alpacaeval-easy", "mt-bench-easy"], n_per_tier)
    hard = take(["llmbar-adver-neighbor", "llmbar-adver-manual", "mt-bench-hard"], n_per_tier)
    # sham sources span MIXED quality so judges aren't all maxed out -> natural disagreement -> the
    # zero-true-gap gauge can still qualify (it reproduces between-judge, not just frozen unanimity).
    shamsrc = take(["alpacaeval-hard", "llmbar-natural", "mt-bench-med", "alpacaeval-easy"], n_per_tier)
    mk = lambda r: {"prompt": r["prompt"], "chosen": r["chosen"], "rejected": r["rejected"]}
    sham = [{"prompt": r["prompt"], "chosen": r["chosen"], "rejected": r["chosen"]} for r in shamsrc]
    return [
        {"name": "easy", "role": "resolve", "pairs": [mk(r) for r in easy]},
        {"name": "hard", "role": "below", "pairs": [mk(r) for r in hard]},
        {"name": "sham", "role": "sham", "pairs": sham},
    ]


def elo_ladder(n_per_tier=8, boundaries=(80, 130), seed=0):   # boundaries verified by wf_0d2ef81b-188
    """Re-anchor on a CONTINUOUS, human-anchored delta: |Arena-Elo(chosen) - Arena-Elo(rejected)| is the known
    quality-gap MAGNITUDE (vs RewardBench's reward-model-difficulty categories, which don't order by gap size).
    Keeps only pairs where chosen is the HIGHER-Elo model (Elo gap aligns with the human-preferred direction),
    buckets by gap into resolve/mid/below tiers + a zero-gap chosen-vs-chosen sham. Ordered descending by gap so
    the monotonicity gate is meaningful. Requires arena_elo.json (the verified Arena-Elo table)."""
    elo = json.load(open(ARENA_ELO_JSON))
    rows = json.load(open(RB_MODELS_JSON))
    lo, hi = boundaries
    rng = np.random.default_rng(seed)
    aligned = []
    for r in rows:
        ec, er = elo.get(r["chosen_model"]), elo.get(r["rejected_model"])
        if ec is None or er is None or ec <= er:        # both rated + chosen is the stronger model
            continue
        aligned.append({**r, "elo_gap": ec - er})
    bk = {"resolve": [p for p in aligned if p["elo_gap"] >= hi],
          "mid": [p for p in aligned if lo <= p["elo_gap"] < hi],
          "below": [p for p in aligned if p["elo_gap"] < lo]}

    def samp(pool):
        if not pool:
            return []
        idx = rng.choice(len(pool), size=min(n_per_tier, len(pool)), replace=False)
        return [pool[i] for i in idx]

    mk = lambda r: {"prompt": r["prompt"], "chosen": r["chosen"], "rejected": r["rejected"]}
    gapmean = lambda pool: round(float(np.mean([p["elo_gap"] for p in pool])), 1) if pool else None
    shamsrc = samp(aligned)
    sham = [{"prompt": r["prompt"], "chosen": r["chosen"], "rejected": r["chosen"]} for r in shamsrc]
    tiers = []
    for name, role in (("resolve", "resolve"), ("mid", "mid"), ("below", "below")):
        s = samp(bk[name])
        tiers.append({"name": name, "role": role, "pairs": [mk(r) for r in s],
                      "mean_elo_gap": gapmean(s), "n_avail": len(bk[name])})
    tiers.append({"name": "sham", "role": "sham", "pairs": sham, "mean_elo_gap": 0, "n_avail": len(aligned)})
    return tiers


def mtbench_ladder(n_per_tier=10, seed=0):
    """The KEYSTONE ladder, anchored on real MT-Bench HUMAN preference margins (built by fetch_mtbench.py). The
    margin IS the per-pair, human-anchored gap size, so this directly populates the signature middle bucket:
      decisive (>=80% margin) -> 'resolve' (clear gap should resolve)
      subtle   (58-79%)       -> 'below'   (the KEYSTONE: statistically real yet BELOW gauge resolution)
      tie      (<58%)         -> 'sham'    (a PROPER sham: real, differently-worded answers humans split on)."""
    data = json.load(open(MTBENCH_JSON))
    rng = np.random.default_rng(seed)

    def samp(pool):
        idx = rng.choice(len(pool), size=min(n_per_tier, len(pool)), replace=False)
        return [pool[i] for i in idx]

    mk = lambda r: {"prompt": r["prompt"], "chosen": r["chosen"], "rejected": r["rejected"]}
    mg = lambda pool: round(float(np.mean([p["margin"] for p in pool])), 2) if pool else None
    out = []
    for name, role, key in (("decisive", "resolve", "decisive"), ("subtle", "below", "subtle"),
                            ("tie", "sham", "tie")):
        s = samp(data[key])
        out.append({"name": name, "role": role, "pairs": [mk(r) for r in s],
                    "mean_margin": mg(s), "n_avail": len(data[key])})
    return out


def keystone_ladder(n_per_tier=8, resolve_min_gap=220, seed=0):
    """The §6-CLOSING ladder — gives the keystone its CONTRAST (decisive must RESOLVE while subtle stays
    real-but-below). The fix for margin!=magnitude: the resolve tier is anchored on quality MAGNITUDE, not human
    margin — RewardBench strong-vs-clearly-deficient pairs (largest Arena-Elo gaps), which produce a perceived Δ
    with headroom against the 1-5 rubric ceiling. subtle/tie stay on MT-Bench human margins (the keystone+sham).
      resolve -> RewardBench |Elo gap| >= resolve_min_gap (large magnitude)
      subtle  -> MT-Bench 58-79% margin (KEYSTONE: real but below resolution)
      tie     -> MT-Bench <58% margin (proper sham)."""
    elo = {k: v for k, v in json.load(open(ARENA_ELO_JSON)).items() if not k.startswith("_")}
    rb = json.load(open(RB_MODELS_JSON))
    mtb = json.load(open(MTBENCH_JSON))
    rng = np.random.default_rng(seed)
    aligned = []
    for r in rb:
        ec, er = elo.get(r["chosen_model"]), elo.get(r["rejected_model"])
        if ec is None or er is None or (ec - er) < resolve_min_gap:
            continue
        aligned.append({**r, "elo_gap": ec - er})

    def samp(pool):
        idx = rng.choice(len(pool), size=min(n_per_tier, len(pool)), replace=False)
        return [pool[i] for i in idx]

    mk = lambda r: {"prompt": r["prompt"], "chosen": r["chosen"], "rejected": r["rejected"]}
    res, sub, tie = samp(aligned), samp(mtb["subtle"]), samp(mtb["tie"])
    return [
        {"name": "resolve", "role": "resolve", "pairs": [mk(r) for r in res], "n_avail": len(aligned),
         "mean_elo_gap": round(float(np.mean([r["elo_gap"] for r in res])), 1) if res else None},
        {"name": "subtle", "role": "below", "pairs": [mk(r) for r in sub], "n_avail": len(mtb["subtle"]),
         "mean_margin": round(float(np.mean([r["margin"] for r in sub])), 2) if sub else None},
        {"name": "tie", "role": "sham", "pairs": [mk(r) for r in tie], "n_avail": len(mtb["tie"]),
         "mean_margin": round(float(np.mean([r["margin"] for r in tie])), 2) if tie else None},
    ]


# ── panel scoring ────────────────────────────────────────────────────────────────────────────────────
def score_panel(pairs, judges, judge_fn, R):
    """Score chosen & rejected for every pair, R times per (pair,judge,config). Returns rows + per-judge
    diagnostics so DEAD (all-nan), DEGENERATE (zero-variance/constant), and PARTIAL (ragged) judges are
    surfaced rather than silently shaping the gauge."""
    rows, by_judge = [], {j: [] for j in judges}
    cell_n = collections.Counter()           # (config, unit, judge) -> surviving trial count
    for j in judges:                         # JUDGES OUTERMOST: each ollama model loads once, not per call
        for u, pr in enumerate(pairs):       # (lets a >=5-judge panel run without thrashing 64GB of RAM)
            for cfg, qk in (("chosen", "q_chosen"), ("rejected", "q_rejected")):
                for rep in range(R):
                    seed = (abs(hash((u, j, cfg, rep))) % 2_000_000_000)
                    s = judge_fn(j, pr["prompt"], pr[cfg], pr.get(qk), seed)
                    if isinstance(s, float) and np.isnan(s):
                        continue
                    by_judge[j].append(s)
                    cell_n[(cfg, f"p{u}", j)] += 1
                    rows.append({"item": cfg, "unit": f"p{u}", "judge": j, "score": s})
    dead = [j for j in judges if not by_judge[j]]
    # judge-relative degeneracy: a flat judge is only 'stuck' if OTHERS show spread it's missing. On a genuinely
    # uniform tier (e.g. the sham's equal-quality answers) every judge is flat and correct -> exclude none.
    stds = {j: float(np.std(by_judge[j])) for j in judges if by_judge[j]}
    tier_has_spread = max(stds.values(), default=0.0) > 0.05
    degenerate = [j for j in judges if j in stds and stds[j] < 1e-9 and tier_has_spread]
    expected = len(pairs) * 2 * R
    partial = [j for j in judges if j not in dead
               and sum(c for (cfg, u, jj), c in cell_n.items() if jj == j) < expected]
    return rows, {"dead": dead, "degenerate": degenerate, "partial": partial, "by_judge": by_judge}


def _repro_sd(rows, judges):
    """Between-judge spread of per-(item,unit) mean scores — the reproducibility signal. ~0 => clone panel."""
    groups = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        groups[(r["item"], r["unit"])][r["judge"]].append(r["score"])
    sds = []
    for jmap in groups.values():
        means = [np.mean(v) for v in jmap.values()]
        if len(means) >= 2:
            sds.append(np.std(means))
    return float(np.mean(sds)) if sds else 0.0


def _perceived(rows, judges):
    """Balanced perceived delta: each judge's mean(chosen)-mean(rejected), averaged across judges (finding 17)."""
    deltas = []
    for j in judges:
        cho = [r["score"] for r in rows if r["judge"] == j and r["item"] == "chosen"]
        rej = [r["score"] for r in rows if r["judge"] == j and r["item"] == "rejected"]
        if cho and rej:
            deltas.append(np.mean(cho) - np.mean(rej))
    return float(np.mean(deltas)) if deltas else float("nan")


# ── per-tier gauge ───────────────────────────────────────────────────────────────────────────────────
def run_tier(pairs, judges, judge_fn, R, repro_floor=0.02):
    rows, diag = score_panel(pairs, judges, judge_fn, R)
    excluded = set(diag["dead"]) | set(diag["degenerate"]) | set(diag["partial"])
    live = [j for j in judges if j not in excluded]
    out = {"n_live": len(live), "dead": diag["dead"], "degenerate": diag["degenerate"],
           "partial": diag["partial"], "void": False, "reason": ""}
    if len(live) < 2:
        out.update(void=True, reason=f"<2 clean judges (live={live}, excluded={sorted(excluded)})",
                   perceived_delta=float("nan"), delta=float("nan"), beyond_gauge=None,
                   significant=None, qualified=False, repro_sd=float("nan"), verdict="VOID")
        return out
    rows = [r for r in rows if r["judge"] in live]
    repro = _repro_sd(rows, live)
    rep = msai.compare(rows, baseline="rejected", level="ordinal", resolution=1.0).to_dict()
    cmp = rep["comparisons"]["chosen"]
    gauge = rep.get("gauge", {}) or {}
    warns = gauge.get("warnings", [])
    out.update(perceived_delta=round(_perceived(rows, live), 3), delta=cmp["delta"],
               beyond_gauge=cmp.get("beyond_gauge"), significant=cmp.get("significant_adj"),
               qualified=bool(gauge.get("qualified")), guard_band=gauge.get("guard_band"),
               repro_sd=round(repro, 4), repro_ok=bool(repro >= repro_floor),
               verdict=cmp["verdict"], gauge_warnings=[w.split(":")[0] for w in warns])
    # GLM's soft note (disclosure, not a guard): a RESOLVED tier on tight agreement could be precision OR
    # shared bias — the precision gauge can't tell. Surface the limit at the point it bites.
    out["notes"] = []
    if out["beyond_gauge"] is True and repro < 0.10:
        out["notes"].append("tight_agreement_low_reproducibility: judges agree tightly (repro_sd<0.10) — could "
                            "be genuine precision OR shared bias; the gauge cannot distinguish. Verify judge "
                            "lineage independence + an external reference before trusting this resolution.")
    return out


# ── validate ─────────────────────────────────────────────────────────────────────────────────────────
def validate(ladder, judges, judge_fn, R=3):
    res = {t["name"]: run_tier(t["pairs"], judges, judge_fn, R) for t in ladder}
    role = {t["name"]: t["role"] for t in ladder}
    order = [t["name"] for t in ladder]
    perceived = [res[n]["perceived_delta"] for n in order]
    monotone = all(perceived[i] >= perceived[i + 1] - 1e-9 for i in range(len(perceived) - 1)
                   if not (np.isnan(perceived[i]) or np.isnan(perceived[i + 1])))
    checks = {"manipulation_monotone": bool(monotone)}
    for n in order:
        r, ro = res[n], role[n]
        if r["void"]:
            checks[f"{n}_qualified_gauge"] = False
            continue
        if ro == "resolve":                                            # clear gap -> beyond gauge + real repro
            checks[f"{n}_resolves"] = bool(r["beyond_gauge"] is True and r["repro_ok"])
        elif ro == "below":                                            # KEYSTONE: statistically REAL yet BELOW
            checks[f"{n}_real_but_below"] = bool(r["significant"] and r["beyond_gauge"] is False)
        elif ro == "sham":                                             # zero gap -> within noise on a QUALIFIED gauge
            checks[f"{n}_within_noise"] = bool((not r["significant"]) and r["qualified"])
    return {"tiers": res, "perceived_ladder": perceived, "checks": checks,
            "GATE_PASS": bool(monotone), "PASS": all(checks.values())}


if __name__ == "__main__":
    use_real = "--real" in sys.argv
    use_elo = "--elo" in sys.argv                                  # Arena-Elo-gap ladder (vs category ladder)
    use_mtb = "--mtbench" in sys.argv                              # human-margin tie/subtle/decisive
    use_key = "--keystone" in sys.argv                             # §6-closing: large-magnitude resolve + subtle + tie
    R = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--R=")), 3))
    n = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--n=")), 5))
    JUDGE_TEMP = float(next((a.split("=")[1] for a in sys.argv if a.startswith("--temp=")), 0.6))
    # 5-judge panel for the keystone run (more judges -> larger dof_repro -> smaller Welch k -> tighter band,
    # so the 'real but below resolution' window is reachable, per GLM); 3-judge otherwise.
    # keystone panel: 5 judges. diag_judges.py REFUTED a prose-outlier — judges agree on the DELTA (+2.0..+2.7);
    # the inflated repro_sd is uniform LEVEL-shift calibration, so the band is legit (GLM's tree). Keep all 5;
    # the fix is the large-magnitude resolve tier, not panel surgery.
    judges = (["gemma4:12b", "gemma4:31b-mlx", "qwen3.5:27b", "qwen3.6:35b-mlx", "qwen2.5-coder:32b"] if use_key
              else ["gemma4:12b", "gemma4:31b-mlx", "qwen3.5:27b", "qwen3.6:35b-mlx", "qwen2.5-coder:32b"] if use_mtb
              else ["gemma4:12b", "qwen3.5:27b", "qwen3.6:35b-mlx"] if use_real
              else ["jA", "jB", "jC", "jD"])
    jf = ollama_judge if use_real else stub_judge
    if use_key:
        ladder, src = keystone_ladder(n_per_tier=n), f"KEYSTONE contrast (RB-magnitude + MT-margin), n={n}/tier"
    elif use_mtb:
        ladder, src = mtbench_ladder(n_per_tier=n), f"MT-Bench human-margin, n={n}/tier"
    elif use_elo:
        ladder, src = elo_ladder(n_per_tier=n), f"Arena-Elo gap, n={n}/tier"
    elif use_real:
        ladder, src = rewardbench_ladder(n_per_tier=n), f"RewardBench category, n={n}/tier"
    else:
        ladder, src = constructed_ladder(), "constructed (stub)"
    print(f"Elo-validation — {'REAL' if use_real else 'STUB'} panel {judges}  R={R} repeats  ladder={src}\n")
    out = validate(ladder, judges, jf, R=R)
    for t in ladder:
        r = out["tiers"][t["name"]]
        gap = (f" eloGap~{t['mean_elo_gap']}" if "mean_elo_gap" in t
               else f" margin~{t['mean_margin']}" if "mean_margin" in t else "")
        if r["void"]:
            print(f"  {t['name']:7s}[{t['role']:7s}]{gap}: VOID — {r['reason']}")
        else:
            note = "  ⚠tight-agreement" if r.get("notes") else ""
            print(f"  {t['name']:7s}[{t['role']:7s}]{gap}: perceivedΔ={r['perceived_delta']:+.2f} "
                  f"Δ={r['delta']:+.2f} beyond_gauge={r['beyond_gauge']} repro_sd={r['repro_sd']} "
                  f"qual={r['qualified']} n_live={r['n_live']} '{r['verdict'][:36]}'{note}")
    print(f"\n  perceived ladder: {out['perceived_ladder']}")
    print(f"  checks: {out['checks']}")
    print(f"  GATE={out['GATE_PASS']}  PASS={out['PASS']}")
    if use_real:
        out["judges"] = judges
        fn = ("keystone_result.json" if use_key else "mtbench_keystone_result.json" if use_mtb else
              "elo_gap_result.json" if use_elo else "elo_validation_result.json")
        json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), fn), "w"),
                  indent=2, default=str)
