# Elo-anchored resolution-tier validation — build-ready design

The combined design the cross-lineage review converged on (Codex's apparatus + Gemini's reference). It
closes the bottom row of the maturity map: *does the resolution tier work on real LLM judges against an
external, traceable known truth* — not synthetic, not the judges' own construct. Combines the two reviews:
Codex owns the **apparatus** (predict-then-measure A/B loop + the monotonicity gate — already built);
Gemini owns the **reference** (human-anchored Elo gaps — closes the measurand-substitution gap that three
independent reviewers flagged).

## The core idea

Take pairs of models (or configs) whose **true quality delta is an established human win-rate / Elo gap**
from a public preference dataset — RewardBench, Chatbot Arena Hard, MT-Bench. The Elo gap is the traceable
reference (external, human-anchored, on the *preference* scale, not a judge-internal construct). Run the
MSAI judge panel on response pairs across a ladder of Elo gaps, and check that MSAI's resolution verdicts
track the human truth: **small Elo gaps read "below gauge resolution," large Elo gaps read "resolved."**

This dissolves the measurand-substitution gap (VALIDATION §6): the reference now lives on the human-preference
scale, so a correct resolution verdict can be checked against an external truth, not the judges' own scale.

## Design

**Reference (Gemini).** Bucket model pairs by their human Elo gap into a continuous ladder:
`negligible (~30 Elo) / small / medium / large (~300+ Elo)`. The Elo gap is the *known true delta*. (For
win-rate datasets, use the human win-rate margin as the delta.)

**Apparatus (Codex), reusing existing code:**
- `benchmark/lever_predict.py` — the disjoint A/B predict-then-measure + Holm harness. Reuse as the template:
  draw a double sample of pairs, call MSAI's verdict on sample A, hold sample B for replication.
- `benchmark/objrubric_validation.py:120` — the monotonicity/qualification gate, **verbatim**. It is
  literally the manipulation check Codex prescribed, and it already self-voids.

**Gate (must pass before any resolution verdict is trusted):**
1. **Manipulation check** — judge-mean MONOTONE in the human Elo gap (the panel must actually perceive the
   human-established ordering). If it isn't monotone, the known delta isn't landing on the judges' scale →
   the test VOIDS (an honest null, not a wasted run — see below).
2. **Gauge qualification** — judge agreement above an `α ≥ 0.4` floor. If the panel can't agree, it isn't a
   gauge on this measurand.

## Pass criterion (pre-registered, all four)

1. **Monotone** — MSAI's verdict severity is monotone in the human Elo gap (gate #1 passes).
2. **Right ends** — small-Elo-gap pairs flagged "below gauge resolution"; large-Elo-gap pairs flagged
   "resolved" (Gemini's acceptance test).
3. **Replicate** — the resolvable/within-noise calls on sample A hold on held-out sample B (Codex).
4. **Beat naive** — MSAI's calls beat a naive significance test on the same data (already demonstrated in
   `lever_predict`: resolvable calls replicate 3/3, raw-significant-but-noise calls correctly fail).

## Controls

- **Negative / sham** — a no-op "difference" (same model, re-sampled, or paraphrase-only): MSAI must NOT
  certify. (Guards against a gauge that certifies anything.)
- **Positive** — a maximal Elo gap (e.g. a frontier model vs a small one): MSAI must certify. (Guards against
  a gauge that resolves nothing.)
- **Leave-one-judge-out** — the verdicts must survive dropping any single judge (no single rater carries it).

## The honest-null path (per Codex's operating-window framing)

If the gate VOIDS — as the `objrubric` preflight already did on the local panel (per-attribute judge
agreement came back near-zero/negative, gauge_tightened=false) — that is a **publishable result**, not a
failure: "this judge panel cannot serve as a gauge on this measurand." Log the **operating window** where it
holds (judge models, prompt, temperature, item population) and the **expiry** (any of those change → re-check).
Non-stationarity is handled by declaring the window, not by claiming permanent calibration.

## Two arms (Gemini's frontier-first point)

Run the harness on **two panels** to separate "is the harness valid?" from "are local judges good enough?":
- **Arm 1 — frontier judges** (e.g. a cross-lineage panel of strong API models) on the Elo ladder. Proves
  the harness correctly maps a known human delta when the gauge is precise. *Validate the instrument here
  first.*
- **Arm 2 — the local panel** (qwen2.5vl + minicpm, the qualified-but-coarse panel). The expected outcome,
  given Stage A + the objrubric preflight, is an honest "too coarse to resolve sub-band gaps" — which is the
  instrument doing its job, with the operating window logged.

## What this is NOT

It does not prove the metrology→LLM transfer is universally sound; it proves the resolution tier tracks an
*external human-anchored* known delta on a *specified* panel + operating window. That is the strongest
achievable transfer evidence short of a production deployment, and it's the answer to the "sophisticated
placebo" question: the verdicts are checked against a truth the judges did not author.

## Build order

1. Adapter: load RewardBench / Arena pairs + their Elo gaps → the known-delta ladder (modules/KB lane —
   reuse the `reference.py` traceable-reference machinery; the Elo gap is the assigned value, its CI the u_ref).
2. Wrap `lever_predict.py`'s A/B harness around the ladder; wire `objrubric_validation.py:120`'s gate.
3. Run Arm 1 (frontier) first; only then Arm 2 (local).
4. Report against the four pass criteria + the controls; stamp the operating window.
