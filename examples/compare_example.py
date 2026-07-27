"""The two-step acceptance-test workflow: qualify the gauge, then compare configs.

Scenario: you're A/B-ing model/compression configs {fp16, q4, q2, delta_kv, dither_2bit}.
A held panel of 5 judges scores each config's outputs, 5 trials per cell at temperature>0.
Question: which configs are worse than fp16 by MORE than the judge panel's own noise?

    python examples/compare_example.py
"""
import numpy as np
import msai_eval as msai

# --- synthesize a realistic eval: configs x judges x trials, ordinal 1-5 scores ---
rng = np.random.default_rng(7)
true_quality = {"fp16": 4.9, "q4": 4.0, "q2": 2.0, "delta_kv": 4.9, "dither_2bit": 3.6}
judge_bias   = {"A": -0.15, "B": 0.10, "C": 0.0, "D": 0.12, "E": -0.05}   # judges run hot/cold

scores = []
for cfg, q in true_quality.items():
    for jg, bias in judge_bias.items():
        for _ in range(5):                       # >= 2 trials at temp>0 unlock the gauge study
            s = q + bias + rng.normal(0, 0.20)
            scores.append({"item": cfg, "judge": jg, "score": float(np.clip(round(s), 1, 5))})

# --- step 1: qualify the gauge (is the panel even able to see the effect?) ---
print("STEP 1 — qualify the gauge\n")
msai.reliability(scores, level="ordinal").summary()

# --- step 2: the acceptance test (which configs really differ from fp16?) ---
print("\n\nSTEP 2 — the acceptance test\n")
report = msai.compare(scores, baseline="fp16", level="ordinal")
report.summary()

# machine-readable, for a CI gate / dashboard:
# for cfg, c in report.comparisons.items():
#     if "REAL drop" in c["verdict"]:
#         raise SystemExit(f"quality regression: {cfg} {c['verdict']} (Δ={c['delta']:+.2f})")
