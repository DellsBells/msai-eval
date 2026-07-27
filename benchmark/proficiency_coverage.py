"""proficiency_coverage.py — synthetic-coverage envelope for proficiency() (gauge-track lane).

Maps the OUTLIER flag's operating envelope against KNOWN injected judge bias, per the agreed spec + the
sensitivity the modules track surfaced (moderate bias undetected at the minimum panel). Three regimes:
  (a) DETECTION sensitivity: P(biased judge flagged OUTLIER) vs bias magnitude × n_judges × scale
      (clipped [1,5] vs wide), + the bias=0 FALSE-POSITIVE baseline.
  (b) z-FLOOR: near-unanimous panel + a trivially-jittering judge -> the 5%-of-scale z-floor must keep the
      false-OUTLIER rate LOW (else near-unanimity manufactures meaningless |z|).
  (c) ZERO-ITEM-SIGNAL degenerate: no item spread -> MEASURE the false-OUTLIER rate (the documented hole,
      proficiency.py:241-244 — score_scale set by the sole deviator; can't be closed from data alone).

    .venv/bin/python benchmark/proficiency_coverage.py
"""
from __future__ import annotations
import os, sys
import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "src")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msai_eval as msai
from synth_gauge import generate_block, reliability_rows


def _scores(rows, level="interval"):
    """Run proficiency; return per-judge {verdict, zbar, outlier, en_fail, n_action} keyed by str(judge)."""
    rep = msai.proficiency(reliability_rows(rows, "weak"), level=level)
    out = {}
    for j, d in rep.by_judge.items():
        out[str(j)] = {"verdict": d.get("verdict", ""), "zbar": d.get("mean_z"),
                       "outlier": "OUTLIER" in d.get("verdict", ""), "en_fail": d.get("en_fail", 0),
                       "n_action": d.get("n_action", 0)}
    return out


def _truth(nj, scale, bias, si=1.0, sr=0.4, se=0.3, items=12, trials=3, seed=0):
    return {"items": items, "judges": nj, "trials": trials, "scale": scale,
            "sigma_item": si, "sigma_repro": sr, "sigma_repeat": se,
            "judge_bias": ({0: bias} if bias else {}), "configs": {"weak": 0.0},
            "seed": seed, "level": "interval"}


def detect_rate(nj, scale, bias, reps=120):
    """Detection via the per-judge BIAS z̄ (the VALIDATION §4 verdict), NOT the OUTLIER flag (which the
    diagnostic showed is En-saturated at the LLM regime). Reports z̄-detection (|z̄_0|>=2 = action-level
    bias on the injected judge), the bias=0 z̄ false-positive rate, the OUTLIER-flag rate (to document its
    saturation), and how often judge0's OUTLIER is En-driven with z in-range (z-floor holds, En doesn't)."""
    zhit = zfp = out_any = en_only = 0; sep = []
    for r in range(reps):
        rows, _ = generate_block(_truth(nj, scale, bias, seed=r))
        s = _scores(rows)
        z0 = abs(s["0"]["zbar"]) if s.get("0", {}).get("zbar") is not None else 0.0
        others = [abs(s[k]["zbar"]) for k in s if k != "0" and s[k].get("zbar") is not None]
        out_any += any(s[k]["outlier"] for k in s)
        if bias:
            zhit += (z0 >= 2.0)
            en_only += (s["0"]["en_fail"] > 0 and s["0"]["n_action"] == 0 and z0 < 2.0)
            if others:
                sep.append(z0 - max(others))
        else:
            zfp += any(o >= 2.0 for o in others)
    n = reps
    return {"z_detect": (zhit / n if bias else None), "z_fp": (zfp / n if not bias else None),
            "outlier_any": out_any / n, "en_masks": (en_only / n if bias else None),
            "sep": (float(np.mean(sep)) if sep else None)}


def main():
    print("=" * 84 + "\n  PROFICIENCY SYNTHETIC-COVERAGE ENVELOPE  (realistic [1,5] rubric scale)\n" + "=" * 84)

    print("\n(a) BIAS DETECTION via z̄ (the VALIDATION §4 verdict) vs the OUTLIER flag — reps=120, sr=0.4:")
    print(f"    {'bias':>5} {'nj':>3} | {'z̄-detect(|z̄0|>=2)':>18} {'z̄ sep(0 vs others)':>20} {'OUTLIER-flag rate':>18}")
    for nj in (4, 8):
        for bias in (0.0, 0.5, 1.0, 1.5, 2.0):
            r = detect_rate(nj, [1, 5], bias)
            det = f"{r['z_detect']:.0%}" if r['z_detect'] is not None else f"FP={r['z_fp']:.0%}"
            sep = f"{r['sep']:+.2f}" if r['sep'] is not None else "—"
            print(f"    {bias:>5.1f} {nj:>3} | {det:>18} {sep:>20} {r['outlier_any']:>17.0%}")
    print("    -> z̄ cleanly fingerprints injected bias once it exceeds ~2x the reproducibility SD; the")
    print("       OUTLIER flag stays ~100% regardless of bias (En-saturated) -> use z̄, not OUTLIER.")

    print("\n(b) z-FLOOR holds for z, but OUTLIER fires via En — near-unanimous (sr=se=0.05)+judge0 0.1, [1,5]:")
    zno = enout = 0
    for r in range(120):
        s = _scores(generate_block(_truth(6, [1, 5], 0.1, sr=0.05, se=0.05, seed=r))[0])
        j0 = s["0"]; zno += (j0["n_action"] == 0); enout += (j0["outlier"] and j0["n_action"] == 0)
    print(f"    judge0 z stays sub-action (z-floor works): {zno/120:.0%};  yet OUTLIER fires via En alone: {enout/120:.0%}")
    print("       -> the 5%-scale z-floor protects z, NOT En; the OUTLIER verdict can still fire on a tight panel.")

    print("\n(c) ZERO-ITEM-SIGNAL — si=0.01, nj=6, [1,5], reps=120 (the documented degenerate hole):")
    out = 0
    for r in range(120):
        s = _scores(generate_block(_truth(6, [1, 5], 0.0, si=0.01, seed=r))[0])
        out += any(s[k]["outlier"] for k in s)
    print(f"    false-OUTLIER rate = {out/120:.0%}  (measured, not asserted zero — proficiency.py:241 can't close it from data)")


if __name__ == "__main__":
    main()
