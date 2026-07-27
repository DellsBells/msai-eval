"""msai_eval quickstart — two realistic LLM-as-judge scenarios."""
import numpy as np
import msai_eval

print("\nSCENARIO 1 — 3 judge models, 20 responses, 1-5 rubric, single scoring each")
print("(the common case: each judge scores each item once)\n")
rng = np.random.default_rng(7)
true_quality = rng.integers(1, 6, size=20)          # latent item quality
data = []
for i in range(20):
    for judge, bias, noise in [("gpt-judge", 0.0, 0.4),
                               ("claude-judge", 0.3, 0.5),
                               ("llama-judge", -0.4, 0.9)]:
        s = int(np.clip(round(true_quality[i] + bias + rng.normal(0, noise)), 1, 5))
        data.append({"item": f"resp_{i}", "judge": judge, "score": s})
msai_eval.reliability(data, level="ordinal").summary()

print("\n\nSCENARIO 2 — 2 judges, 15 items, 3 REPEAT trials each at temperature>0")
print("(repeats unlock the repeatability / Gage R&R variance decomposition)\n")
data2 = []
true2 = rng.uniform(20, 90, size=15)
for i in range(15):
    for judge, bias in [("judge_A", -2.0), ("judge_B", 3.0)]:
        for _ in range(3):
            s = float(np.clip(true2[i] + bias + rng.normal(0, 6), 0, 100))
            data2.append({"item": i, "judge": judge, "score": s})
msai_eval.reliability(data2, level="interval").summary()
