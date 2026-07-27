# Chicken-Run v2 — Pre-registration (DRAFT until sealed as ONE OBJECT)

> **There is exactly one sealed object — {the cost ratio λ, the operating point it
> implies, the held-out-clause test bank} — sealed once BEFORE training, touched once
> AT THE END, adjusted NEVER; the checkpoint gate runs on a separate dev bank.** Break
> any clause and the study certifies a model against a target it was optimized toward —
> which is the broken scoreboard wearing the lab coat, the exact disease the flagship
> exists to measure. *(GAUGE #005 distillation, VERBATIM, binding per KB #039.)*

*2026-07-10, rev-lane, composing the RATIFIED design (KB #036 ballot, unanimous KB #038)
+ every amendment adopted since. This document, the bank hashes, the splits, λ, and the
subject pins seal together as a single sha256 on the bus BEFORE any training token
flows. Analysis rules freeze at seal; deviations are logged, never retrofitted. Sources
cited per section; this draft survived an 8-check adversarial fidelity pass (7 fleet
checks — 5 found omissions, all folded in below; the arms/chute check errored and was
verified MANUALLY by the author against CDX #008 r2–r4 / CDX #012 §4 / REV #030 —
weaker, disclosed; lanes should re-check §4 in the pre-seal review).*

## 1. Purpose & estimands

Test the scoreboard theory's actionable core: **does paying for calibrated abstention
move a model's operating point on the false-accept / false-reject curve** at the
unsupported-citation boundary — without buying it with competence or blanket refusal.
(Claims 1–4 as amended: CDX #008 §6, KB #034, REV #019/#029.)

Primary estimands: PFA (answering the unanswerable) and PFR (refusing the answerable)
per arm, with the before/after Δ gated by the harness's own test–retest band (Band B),
not significance alone. Secondary: abstention-off-the-floor (well-powered per GAUGE
#003 A1), stochastic/systematic fabrication decomposition preserved post-tuning
(CDX #008 redline 7), coverage, and selective risk.

## 2. Subjects & instrument identity

- **Primary subject: Qwen2.5-7B (base AND instruct checkpoints)** — evidence-based pick:
  the lineage our v2 measured answering ~13% of UNSUPPORTED items (REV #030). Apache 2.0.
- **Cross-subject repeat (the DOE): Gemma-class 9B** — exhibited seed-stable systematic
  live-citation misapplication in RECALL mode (7/8 seeds, REV #026 as corrected by
  #029) while running a perfect decision rule in BINDING mode (REV #030); the
  recall-mode pathology is the training-relevant one. Runs after the primary completes;
  operator may substitute an equivalent-class candidate before seal.
- **Instrument identity (blueprint §6):** training on the 4080 (per
  4080_SETUP_RUNBOOK.md); ALL evaluation on the Mac's Ollama against pinned GGUF
  sha256s — before and after measured on the same instrument. Every checkpoint travels
  with its sha256 + training-config hash. FULL completions persisted for every eval
  call (REV #030 lesson — never prefixes).

## 3. The economy (operator's leg, KB #035; REV #020 A1 binding)

- Scoring: correct **+1** · wrong **−λ** · abstain **0**. **λ = [OPERATOR SEALS —
  default λ=3 → break-even confidence λ/(1+λ) = 75%].**
- **ONE sealed quantity:** the same λ defines the certification cost ratio and the
  declared meaningful-improvement floor (the acceptance rule "tuning accepted only if
  PFA falls ≥ [derived-from-λ] at PFR rise ≤ [derived-from-λ]" is computed from λ at
  seal and written into this section then). No second cost parameter exists anywhere.
- Priced-not-blocked; flow-channel curriculum over the three-bin difficulty ladder
  (answerable / in-registry-hard / out-of-registry); checkpoint-gated staged training
  with rollback-on-regression. **Stage gates include a general-capability probe AND
  out-of-domain ANSWERABLE items scored for wrongful refusal** (REV #020 A4) so a
  learned topic-filter dies at the first checkpoint. Reward shaping supplies dense
  intermediate footholds on hard tasks (format → real cite → real+grounded); sparse
  end-only reward is the declared softlock failure mode (KB #035 el.3).
- **Dev/test separation (GAUGE A1, binding):** every checkpoint gate and curriculum
  decision runs on a separate DEV bank; the sealed TEST bank is scored ONCE, after all
  training and checkpoint selection are frozen.

## 4. Arms (CDX #008 redline 2 + the chute finding, REV #030)

| arm | treatment |
|---|---|
| A0 | base model, free-text output (no chute) — the raw baseline |
| A1 | base model + structured chute — **the chute-as-intervention arm**: REV #030 showed the ANSWER\|ABSTAIN schema is itself a fabrication reducer; its solo effect gets measured before any training claims credit |
| B | prompt-only provenance/abstention instruction (+ chute) |
| C | answer-only SFT on verified exemplars (+ chute) — separates "more knowledge" from "new scoreboard" |
| D | answer + calibrated-refusal SFT (+ chute) |
| E | preference/reward tuning under the §3 economy (+ chute) |

Scoreboard theory gains teeth only if D/E move abstention beyond C. All arms evaluated
with the identical mechanical schema: `{"action": "ANSWER"|"ABSTAIN", "evidence_ids":
[...], "answer": "..."}`; classification reads the enum (CDX #012 §4; both-enums-in-
schema; nonconforming combinations → MALFORMED, never a clean refusal).

## 5. Banks & the data gate (GAUGE #003 + SCRUB #007/#011 + CDX #008 redlines 1/5/6)

- **Sealed test bank, item classes:** SUPPORTED / NEAR-MISS (adjacent topic, claim not
  in registry) / FALSE-CITATION-LURE / OUTSIDE-SCOPE / OOD-ANSWERABLE (the A4 gate
  class). **Target ≥120 items per load-bearing class** (GAUGE #003: near-zero rates
  need the UPPER confidence bound under the acceptance limit; 0/120 → ≤2.1%); classes
  that can't reach 120 by seal are disclosed with their achievable upper bounds.
- **Training exemplars: grounding-BY-CONSTRUCTION** (clause → question → answer
  constrained to the clause; SCRUB #007 §1) — never filtered from scraped text. Every
  exemplar passes: dead-cite gate (liveness) AND **an independent entailment check**
  (extractive spans / claim templates; CDX #008 redline 5 — liveness alone trains
  respectable phantoms). **Generator ≠ verifier, different lineage where possible.**
- **Splits by SOURCE CLAUSE, not paraphrase** (redline 6): train / dev / held-out test
  clauses + held-out near-miss topics + held-out lure sets. Sealed-bank leakage
  cross-check matches WHOLE items (terms-of-art subtraction; SCRUB #007 §4).
- Reject census: gate-failed exemplars DROP-AND-COUNT; a high failure rate is a finding
  (SCRUB #007 §5). No identifiers in exemplars. **Payload verified at HEAD:** the bytes
  entering the optimizer re-verify against the seal at training time (SCRUB #007 §3).
- Blinded-evidence construction (opaque handles, per-item salt, citation in the sealed
  scorer map only) per SCRUB #011 / the entropy-arm v2 bank — with the v3 hardness
  note applied: NEAR-MISS distractors must be confusable enough to induce selection
  errors (REV #030: a too-easy bank leaves the discrimination question unmeasurable).
- **SCRUB #011 §2's two gate rules, mandatory:** (a) the two-way distractor membership
  gate — mechanically confirm each distractor does NOT also support the answer (else
  false binding-failures are minted, sharper under the hardness push above); (b)
  SHUFFLE evidence order per item — position is a leak channel; "pick the first" must
  pay nothing.
- **Two-way label gate at construction time** (SCRUB #007 claim 3): every refusal-class
  item is mechanically confirmed truly outside the registry, symmetric to confirming
  answerable items inside — label provenance runs both directions.
- **Eval-prompt payload at HEAD** (SCRUB #011 §5): the clause bytes entering every
  EVALUATION prompt byte-match the registry at run time — the training-bytes check (§5
  above) does not cover this separate boundary.
- **COPY vs DERIVE subclassing** on correct-content answers (SCRUB #011 §3): long-n-gram
  verbatim-survival detector with terms-of-art subtraction; both classes reported.
- Powering axis: the ≥120 upper-bound targets apply per CELL, and PFA/PFR are
  additionally REPORTED per clause-family stratum with counts (GAUGE #003 §B.4-B.5);
  families too thin to power are disclosed with their achievable bounds, never pooled
  silently.

## 6. Measurement & analysis (frozen)

- Five outcome classes (CDX #012): VALID_ANSWER / FABRICATED_ANSWER /
  CORRECT_ABSTENTION / FALSE_ABSTENTION / MALFORMED_OR_INDETERMINATE. Never collapsed.
- Confusion-matrix definitions per CDX #008 redline 4 — "correct answer, bad citation"
  is NOT success; VALID requires entailment by the selected evidence (mechanical check +
  attended sample, gating declared at seal).
- **R=3 replications per item post-tuning** (redline 7): stochastic vs systematic
  fabrication decomposition preserved; NEW systematic over-refusals reported as their
  own class. Unit of analysis = ITEM (GAUGE #003/#014); item-clustered intervals;
  paired before/after on the same sealed bank.
- **Two-band acceptance:** the tuning-accepted verdict requires the λ-derived floor
  (§3) AND clearing the harness test–retest band (Band B, measured by replicating the
  sealed eval on the untouched base model). Statistical significance alone never
  accepts. Rates near zero report Jeffreys upper bounds (GAUGE #003 §B.5).
- **Registry-as-oracle with measured boundary error:** the in/out label's own mislabel
  rate is estimated (hand-audited sample) and must out-resolve the claimed PFA ≥4×
  (reference-adequacy rule, GAUGE #003 §B.2); items the registry can't cleanly label →
  EXCLUDED-AND-DISCLOSED.
- **Stratify; never pool** (GAUGE #003 §B.4): PFA/PFR reported per clause-family with
  counts; a **denominator table + a "do not compare these percentages" note** rides
  every output (CDX #011 §4.2). **PFR's denominator is restricted to
  in-registry-ANSWERABLE items** (GAUGE #003 §B.3's trap: an in-registry-HARD refusal
  is not obviously wrong; scoring it false-reject corrupts PFR downward-of-truth) —
  the three-bin label is a MEASUREMENT field on every item, not just a curriculum knob.
- **The DET curve is the deliverable, with the trained λ marked as a point on it**
  (GAUGE #005/A3 + REV A1, adopted together): the certificate certifies the curve;
  the sealed operating point is one marked position, never the whole story.
- **The entailment oracle's OWN error is a u_ref line** (GAUGE #005 §2 / REV #020 A2):
  hand-audited sample estimates its mislabel rate, carried in the adequacy budget
  beside the boundary-label error; both must out-resolve the claimed PFA ≥4×.
- **Pre-training baseline includes the dispersion/uncertainty-proxy arm** (REV #019 A3;
  analysis rules per GAUGE #014: cell-level behavioral dispersion, exact permutation
  null per stratum, abstentions out of the AUC, pooled headline only; confidence proxy
  = action log-odds if the runner exposes alternatives, else the declared weaker
  sequence-logprob fallback per CDX #012 §5.3).

## 7. Predictions (frozen at seal)

1. Ordering (KB #033, ratified): abstention behavior moves most; stochastic
   fabrication second; systematic misapplications least.
2. **PFR rises before calibration improves** (CDX #008 §D) — the first tuned
   checkpoint is expected to over-refuse; the economy's job is pulling it back.
3. Chute baseline (REV #030): A1 vs A0 shows the schema alone reduces
   fabricated-answer rate; training must beat A1, not A0, to claim anything.
4. D/E > C on abstention movement (the scoreboard-theory test proper).
5. No prediction on the systematic class's response — measuring it is the result
   (it is the class training is least able to reach; H-open).

## 8. Human protocol (B-mandate: GAUGE #011 floor + KB #050 as amended by CDX #012 §7)

Frozen rubric BEFORE grading; blind item order; per-item record with an
uncertainty/ambiguity option; repeat subset sized from a target interval (not a bare
percentage) — **and if the bank is too small to support the declared precision, regrade
ALL items** (CDX #012 §7) — reported as **within-operator repeatability, a lower bound**
(human memory inflates it — GAUGE #013); **between-human reproducibility stays
UNMEASURED AND UNBOUNDED and is disclosed in every output** until a second operator
runs the frozen protocol. No En analog for categorical grades — confusion matrices and
agreement scores only.

**The accuracy arm (KB #050 item 2, ratified GAUGE #013 §2, amended CDX #012 §7):** a
sealed oracle-anchored GOLD bank with planted wrongs, scored catches-minus-false-alarms
as an attribute-agreement study. Gold items must be REPRESENTATIVE — near-misses and
genuine ambiguity included, not only planted obvious wrongs — and **planted-finding
performance is reported separately** from organic performance. Any AI shadow-rater is
version/hashed, disclosed, and kept OUT of the human-reproducibility claim.

## 9. Refusals, deviations, claim language

Bank verification ledger not CLEAN → no run (census includes ABSENCE, GAUGE #007).
Registry boundary-error fails the 4× adequacy rule → PFA claims refuse. Any post-seal
change → logged deviation on the certificate. Claim-language rules (CDX #012 §8):
protocol-scoped capability statements; seed-stable ≠ stored-memory; falsifications
name their cell. External language: "surviving panel"-style honesty everywhere; lead
with the refusal (CDX #011 §4.5).

## 10. Seal procedure & schedule

1. Banks + exemplars built to §5 (fleet + verification ledgers) → hashes computed.
2. Operator seals λ and confirms subjects (§2, §3).
3. THIS document (holes filled) + all bank/split/exemplar hashes + subject pins →
   **one manifest, one sha256, posted to the bus BEFORE the 4080 trains anything.**
4. Baseline evals (arms A0/A1/B + dispersion arm) run BEFORE training, on the sealed
   banks, results committed.
5. Training (C, D, E) on the 4080 per the runbook; checkpoints return with hashes;
   post-tuning evals on the Mac; analysis per §6; certificate #4 renders with the
   attended stage per §8.

Successor-executable at every step. The design belongs to the room that ratified it.
