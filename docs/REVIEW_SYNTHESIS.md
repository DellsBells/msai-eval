# Cross-lineage / cross-context review — Codex + Gemini, adjudicated

Independent review of MSAI's open gaps by two model lineages in two contexts: **Codex** (had the metrology
knowledge base — *inside* the metrology frame) and **Gemini** (chat window, no KB — *outside* the frame).
The divergence was adjudicated by four code-grounded investigations + an adversarial synthesis (the author's
bias deliberately removed from the verdict; full run in the workflow transcript). This is the record.

## Why the inside/outside split mattered

Codex, KB-grounded, gave the better *application* advice (operating-window/expiry framing, the
degradation-sweep-as-calibration-curve, controls). Gemini, ungrounded, questioned whether the framework
*applies at all* (the ordinal-vs-continuous critique). That is exactly what the KB-benchmark predicted: the
KB grounds application, not foundational reasoning — it makes you fluent *inside* the paradigm, which makes
the "does this paradigm fit?" question harder to see. The outsider walked straight to it. Net: weight
Gemini's *foundational* signal heavily; verify its *specific prescriptions* against the code (it never saw
the source).

## Convergence (both lineages agreed — strong signal)

- The gauge core (crossed-ANOVA variance components → grr_sd → guard band U → %GRR → ndc) is **interval-math
  applied to ordinal scores**, and runs byte-identically whether `level="ordinal"` or `"interval"`.
- The keystone "real but BELOW gauge resolution" is the right *kind* of result — emitting "real but
  unresolvable" is a feature.
- **Two judges is the structural weak point** (dof_repro=1 → Welch k swings 2–13×).
- MSAI already self-discloses these weaknesses in code/warnings (neither reviewer found an undisclosed
  overclaim on them).
- A predict-then-measure run against a known signal is the right apparatus to close the resolution tier.

## Divergences — who was right, grounded in the code

| Point | Codex | Gemini | Verdict | Why |
|---|---|---|---|---|
| MSAI "forces ordinal into continuous / lacks ordinal tools" | ordinal-aware already | switch to ordinal tools | **Codex** | `level="ordinal"` is the default; ordinal Krippendorff (rank-marginal distance), Cliff's δ, weighted kappa, and the mean-vs-rank WITHHOLD already exist (agreement.py:57-60, compare.py:55-61/93-96, agreement.py:108). The tools Gemini prescribed are shipped. |
| Guard band is a "placebo," abandon the tier | keep + validate | interval-math = magnitudes in a non-existent space | **Both partly** | Premise right, FATAL wrong: the band is **one-sided conservative** (floored at 2·grr_sd) — interval mis-spacing can only *over-refuse*, never fabricate a false "REAL." Refusal degrades **fail-safe, not placebo.** Direction is rank-policed; the keystone rests on rank-survivable judge disagreement. |
| Instability is ordinal-forced-continuous; fix via Fleiss/Kendall/IRT | small-n sampling + 1-dof term | scale-type bug | **Codex** | **Empirically falsified** on MSAI's synthetic gauge: quantizing to ordinal barely moved the %GRR band (23 vs 24pp); rank metrics are *as unstable or worse* in the decision regime (rank-ICC sign-flips, CV≈1.4). Any 2-rater term reproduces the 1-dof blow-up. Lever = ≥4–5 judges, not new math. |
| Validation reference: synthetic degradation vs human Elo | inject continuous degradation | human-anchored Elo/win-rate | **Both partly → combine** | Codex owns the *apparatus* (predict-then-measure loop + monotonicity gate — already built in `lever_predict.py` + `objrubric_validation.py:120`). Gemini owns the *reference* (human Elo closes the measurand-substitution gap three independent reviewers flagged). |

## The one real gap (surfaced by the outside view, missed by the insiders)

**MSAI guards the *direction* of every ordinal verdict (the Cliff's-δ sign-disagreement WITHHOLD) but the
*magnitude* gate — does |Δ| clear the guard band — is computed in raw interval points.** If true rubric
steps are non-uniform (4→5 a bigger real jump than 2→3), interval distortion can flip the *resolvability*
call even when mean and rank effect agree in sign, and the existing WITHHOLD won't catch it. This is the one
place the interval assumption can quietly change a headline verdict rather than just over-withhold. Neither
Codex nor the MSAI team caught it; Gemini did.

## Recommended path

1. **Keep the resolution tier.** Do not adopt the placebo/abandon reading; do not re-platform to IRT (both
   refuted on the actual code + data).
2. **Quick, lockable:** a legibility doc note ("the gauge layer is interval-by-construction and identical
   across levels; the rank tools are the assumption-free layer; a rank-contradicted mean verdict is withheld
   on ordinal"); and arm the rank cross-check (at least as a warning) even under `level="interval"`
   (currently disabled, compare.py:93).
3. **Close the real gap:** add a **rank-based magnitude counterpart** to the resolvability gate — a parallel
   resolvability check in Cliff's-δ units; downgrade/caveat "REAL beyond resolution" when the
   interval-magnitude and rank-magnitude gates disagree (mirroring the existing sign WITHHOLD).
4. **The big experiment — combine both, don't choose:** drive Codex's apparatus (`lever_predict` A/B
   predict-then-measure + the `objrubric` monotonicity gate) with Gemini's reference (human-anchored
   RewardBench / Chatbot Arena Elo gaps as the known true delta). Pass = verdicts monotone in the Elo gap,
   small gaps flagged below-resolution / large gaps resolved, replicate held-out, beat naive significance.
   A void (as the objrubric preflight already produced — judges gave negative agreement on the objectified
   rubric) is a publishable honest null, with the operating window logged. (Design: `docs/ELO_VALIDATION_DESIGN.md`.)
5. **Engineering default:** ≥4–5 judges (k collapses 12.71→2.0); shrinkage/bootstrap on the %GRR ratio for
   tighter small-n bands without more judges.
