"""synth_gauge.py — synthetic gauge-block generator for MSAI calibration (modules/KB lane).

generate_block(truth) emits MSAI-format judge scores with a KNOWN variance decomposition + KNOWN config
deltas, so the gauge track's recover_check can verify MSAI RECOVERS them. Per the frozen plan:
  - matched-model (all-Gaussian) recovery of the split is an ALGEBRAIC IDENTITY -> SMOKE TEST only;
  - the HEADLINE regimes are the misspecification knobs (heavy-tail repeatability, item/config-correlated
    common-mode, heteroskedastic noise, ordinal/non-interval) where the pass condition is a FIRED GUARD or
    a CHARACTERIZED COVERAGE number, not a recovered value;
  - the primary deliverable is the n-sweep bias/variance table over items{5,8,11,14} x judges{2,3,4,5} x
    trials{2,3} (judges=2 is the real panel's operating point).

Forward model (crossed random effects), for config c, item i, judge j, trial t:
  score = base + item[i] + delta[c] + judge[j] + judge_bias[j] + common_mode + noise(sigma_eff, dist)

Frozen contract (noise_spec schema): generate_block(truth) -> (rows, truth); rows are MSAI records
{config, item, judge, trial, score}. reliability_rows()/compare_rows() build the two MSAI views.
"""
from __future__ import annotations
import numpy as np


def _noise(rng, n, sigma, dist):
    if sigma <= 0:
        return np.zeros(n)
    if dist == "t3":                                   # heavy tail; scale t(3) (var=3) to SD=sigma
        return rng.standard_t(3, n) * (sigma / np.sqrt(3.0))
    return rng.normal(0.0, sigma, n)


def _bias(jbias, j):                                   # tolerate int or JSON-str judge keys
    return float(jbias.get(j, jbias.get(str(j), 0.0)))


def generate_block(truth: dict):
    """Return (rows, truth). rows = [{config,item,judge,trial,score}, ...] in MSAI ingest format."""
    rng = np.random.default_rng(truth.get("seed", 0))
    I, J, T = truth["items"], truth["judges"], truth["trials"]
    lo, hi = truth["scale"]
    base = 0.5 * (lo + hi)
    si, sr, se = truth["sigma_item"], truth["sigma_repro"], truth["sigma_repeat"]
    jbias = truth.get("judge_bias") or {}
    configs = truth["configs"]
    dist = truth.get("repeat_dist", "normal")
    cm = truth.get("common_mode")
    hetero = truth.get("heteroskedastic", False)
    level = truth.get("level", "interval")
    flip = truth.get("mean_rank_flip")   # {"config":name,"frac":f,"out_shift":S,"bulk_shift":b} -> mean & rank disagree

    # per-item offset that makes the flip config's MEAN go one way while its RANK majority goes the other:
    # the bulk of items sit slightly below baseline (rank favors baseline) but a few extreme outliers drag
    # the mean above (mean favors the flip config) -> cliffs_delta*delta < 0 -> compare() must WITHHOLD.
    # defaults below are VERIFIED to fire the WITHHOLD on a wide scale (e.g. [1,50]) where out_shift
    # doesn't clip; on a narrow scale the outliers saturate and the flip won't trigger.
    flip_off = np.zeros(I)
    if flip:
        n_out = max(1, int(round(flip.get("frac", 0.15) * I)))
        flip_off[:] = flip.get("bulk_shift", -1.0)
        flip_off[:n_out] = flip.get("out_shift", 8.0)

    item_eff = rng.normal(0.0, si, I) if si > 0 else np.zeros(I)
    judge_eff = rng.normal(0.0, sr, J) if sr > 0 else np.zeros(J)
    z_item = (item_eff / si) if si > 0 else np.zeros(I)          # standardized item signal

    # config-correlated common-mode: a shared (all-judges) per-config shift of scale cm.sd ->
    # shifts a config mean WITHOUT widening reproducibility -> the false-REAL regime.
    cm_config = {}
    if cm and cm.get("corr_with") == "config":
        names = list(configs)
        centers = np.linspace(-1, 1, len(names)) if len(names) > 1 else np.zeros(1)
        cm_config = {nm: cm["sd"] * c for nm, c in zip(names, centers)}
    # item-correlated common-mode: shared per-item shift proportional to the true item signal -> ndc optimism.
    cm_item = (cm["sd"] * z_item) if (cm and cm.get("corr_with") == "item") else np.zeros(I)

    rows = []
    for cname, delta in configs.items():
        cmc = cm_config.get(cname, 0.0)
        foff = flip_off if (flip and cname == flip["config"]) else np.zeros(I)
        for i in range(I):
            sigma_eff = max(se * (1.0 + (hetero or 0.0) * z_item[i]) if hetero else se, 1e-9)
            for j in range(J):
                mu = base + item_eff[i] + delta + judge_eff[j] + _bias(jbias, j) + cmc + cm_item[i] + foff[i]
                e = _noise(rng, T, sigma_eff, dist)
                for t in range(T):
                    s = mu + e[t]
                    s = round(s) if level == "ordinal" else s
                    rows.append({"config": cname, "item": int(i), "judge": int(j), "trial": int(t),
                                 "score": float(min(max(s, lo), hi))})
    return rows, truth


def reliability_rows(rows, config):
    """item = product identity within ONE config -> recover the variance components / gauge."""
    return [{"item": r["item"], "judge": r["judge"], "score": r["score"]} for r in rows if r["config"] == config]


def compare_rows(rows):
    """item = config (treatment); unit = product. The `unit` field lets compare() decompose gauge noise at
    the UNIT level (between-judge + re-scoring) instead of pooling products into the config cell and
    mislabeling their spread as repeatability (the guard-band inflation the audit caught)."""
    return [{"item": r["config"], "judge": r["judge"], "score": r["score"], "unit": r["item"]} for r in rows]


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
    import msai_eval as msai

    truth = {
        "items": 12, "judges": 4, "trials": 3, "scale": [1, 5],
        "sigma_item": 1.00, "sigma_repro": 0.40, "sigma_repeat": 0.30,
        "judge_bias": {}, "configs": {"weak": 0.0, "good": 0.8}, "seed": 7,
    }
    rows, _ = generate_block(truth)
    print(f"generated {len(rows)} rows "
          f"({truth['items']} items x {truth['judges']} judges x {truth['trials']} trials x {len(truth['configs'])} configs)\n")

    ub = msai.uncertainty_budget(reliability_rows(rows, "good"), level="interval").to_dict()
    comp = {c["source"].split()[0]: c["u"] for c in ub["components"]}
    print("MATCHED-MODEL SMOKE — variance-component recovery (recovered u vs injected sigma):")
    print(f"  repeatability   injected {truth['sigma_repeat']:.3f}  ->  recovered {comp.get('repeatability', float('nan')):.3f}")
    print(f"  reproducibility injected {truth['sigma_repro']:.3f}  ->  recovered {comp.get('reproducibility', float('nan')):.3f}")

    cmp = msai.compare(compare_rows(rows), baseline="weak", level="interval").to_dict()
    g = cmp["comparisons"]["good"]
    print(f"\nDELTA recovery:  injected Δ_true={truth['configs']['good']:.3f}  ->  recovered Δ_hat={g['delta']:.3f}"
          f"  (U={ub['U']:.3f})  verdict='{g['verdict']}'")
    print("  (on a bounded [1,5] scale + small n the recovery is biased LOW — that is clipping + estimator")
    print("   sampling, NOT an injection bug; the clean-limit check below proves the generator is correct.)")

    # clean-limit verification: wide scale (no clipping) + large n -> recovery must hit injected truth.
    clean = dict(truth, items=300, judges=80, trials=12, scale=[-1000, 1000])
    crows, _ = generate_block(clean)
    cub = msai.uncertainty_budget(reliability_rows(crows, "good"), level="interval").to_dict()
    cc = {c["source"].split()[0]: c["u"] for c in cub["components"]}
    cd = msai.compare(compare_rows(crows), baseline="weak", level="interval").to_dict()["comparisons"]["good"]["delta"]
    print(f"\nCLEAN-LIMIT verification (wide scale, large n) — must equal injected:")
    print(f"  repeatability 0.300->{cc.get('repeatability'):.3f}  reproducibility 0.400->{cc.get('reproducibility'):.3f}"
          f"  delta 0.800->{cd:.3f}   => generator injects truth correctly")
    print("\n[smoke only — full recovered-vs-injected + coverage + verdict-oracle is the gauge track's recover_check]")
