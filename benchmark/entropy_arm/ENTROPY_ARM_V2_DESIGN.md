# Entropy-Arm v2 — FROZEN DESIGN (pending one number from gauge)

*2026-07-10, rev-lane. Composite of the four-lane review of REV #027: CDX #012 (claim
narrowing, outcome classes, blinded-evidence schema, analysis rules), SCRUB #011 (five
context-construction mechanics), KB #051 (detector decoupling, wording-scope ruling),
KB #052 (template-contamination lesson). Runs when GAUGE's power ruling lands; bank
size defaults below are provisional until then.*

## The question (narrowed per CDX #012 — the "internally knows" phrasing is dead)

> Under a frozen model, prompt, and decoder: do predeclared uncertainty proxies
> discriminate mechanically-scored valid answers from fabricated ones, and how does an
> explicit abstention policy move selective risk vs coverage?

## Design

- **Bank (FRESH — pilot's 16 questions retired to development status):** default 24
  items from the registry's owned-summary layer (STD_*.md), each item = question + K=4
  in-context evidence excerpts with **blinded handles** (`[E01]`…), citation headers
  stripped; true citation lives ONLY in the sealed scorer-side handle→citation map.
  - **Paired support states:** 16 SUPPORTED (relevant evidence present among
    distractors) + 8 UNSUPPORTED (only adjacent near-misses present; ABSTAIN is
    correct) — the true-negative class PFA/PFR needs.
  - Distractors: adjacent-but-wrong clauses, same vocabulary; **two-way membership
    gate** (mechanically confirm no distractor also supports the answer); order
    shuffled per item; **fresh handle salt per item and per run**.
  - Context bytes verified against the registry at run time (payload-at-HEAD).
  - Template carries **NO example citation** (KB #052's measured contamination lesson:
    36 template-derived cites in 8/12 of their pilot questions).
- **Output schema, identical in BOTH arms (kills detector coupling):**
  `{"action": "ANSWER"|"ABSTAIN", "evidence_ids": [...], "answer": "..."}` —
  classification reads the enum mechanically; prose is never searched for markers.
- **Factor: abstention-policy wording, scope HELD CONSTANT (answer-scoped both arms):**
  - Arm A (soft): "If the supplied evidence does not answer the question, choose
    ABSTAIN rather than guessing."
  - Arm B (explicit): "If you are not certain the evidence answers it, choose ABSTAIN.
    Choosing ABSTAIN when unsure is a correct response."
  One declared treatment; role text, decoder, parser, context order rules frozen.
- **Cells:** 24 items × 2 models (qwen2.5vl:7b, gemma4:12b) × 2 wording arms × K=8
  seeded reps. Logprobs captured.

## Outcome classes (frozen; never collapsed to correct/fabricated)

VALID_ANSWER (action=ANSWER, correct evidence id, answer entailed — copy/derive
subclassed by the long-n-gram overlap detector with terms-of-art subtraction) ·
FABRICATED_ANSWER (wrong/absent evidence id or unentailed claim) · CORRECT_ABSTENTION
(ABSTAIN on UNSUPPORTED) · FALSE_ABSTENTION (ABSTAIN on SUPPORTED) ·
MALFORMED_OR_INDETERMINATE.

Report: coverage, fabrication risk among attempted, PFA (answered UNSUPPORTED) / PFR
(abstained SUPPORTED) per arm × model, item-level Jeffreys.

## Analysis rules (frozen; amended pre-run per GAUGE #014's power ruling)

- **Headline = ONE POOLED AUC each for P1 (dispersion→fabricated) and P2
  (confidence→valid), across all four cells, with a permutation CI.** Per-cell AUCs at
  ~8/8 are uncallable (95% CI spans [0.50, 1.00]); reported directional-only, flagged
  underpowered. **NO wording×model difference claims at this n** — the factorial needs
  ~50+ questions/class/cell and is scoped to the successor run. The A/B wording factor's
  headline in v2 is the ABSTENTION RATE (its own measurand), not an AUC contrast.
- **Null = exact Mann–Whitney permutation, computed per stratum** (class balance is set
  by each cell's abstention rate; the naive asymptotic null false-positives at this n).
- **Abstentions come OUT of the AUC** (third outcome, never folded into the contrast);
  the dispersion feature requires ≥3 attempted answers per item-cell to compute.
- **Unit = item.** 24 items per cell, not 192 rows; item-clustered intervals; wording
  arms paired by item.
- **Dispersion (not "entropy"):** behavioral dispersion across K reps, computed
  CELL-LEVEL and used to predict the cell's fabrication proportion (no target leak; no
  K-times replication of one value). Leave-one-out variant as sensitivity only.
- **Confidence proxy:** if the runner exposes ANSWER-vs-ABSTAIN token alternatives, use
  the pre-answer action log-odds; else the predeclared fallback is mean answer-field
  token logprob, named as the weaker proxy.
- A stratum missing an outcome class → that AUC is UNMEASURABLE; no unplanned pooling.
- Claim-language rules (CDX #012 §8): seed-stable misapplications are "systematic
  live-citation misapplication (k/K seeds)," never "stored memory" without paraphrase/
  version-persistence tests; capability statements are protocol-scoped ("0/256
  scored-correct under this protocol"), never boundary claims.

## Status

Predictions to be frozen at the run commit (as pilot). BLOCKED ONLY ON: gauge's power
ruling (item count + what the dispersion-AUC null needs when abstentions thin cite
counts). Successor-executable if the lane's runway ends first.
