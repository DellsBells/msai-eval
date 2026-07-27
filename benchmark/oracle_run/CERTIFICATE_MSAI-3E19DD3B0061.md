# GAUGE CERTIFICATE — LLM-AS-JUDGE MEASUREMENT SYSTEM (ACCURACY-ANCHORED)

**Certificate no.** `MSAI-3E19DD3B0061` · **Issued** 2026-07-10 · **Data of** 2026-07-09 ·
**Basis** 828 blind ratings (14 null excluded, disclosed), sha256-bound to
`oracle_study_scores.json` · **Format** `MSAI-GC/1.0-draft` (docs/CERTIFICATE_SPEC.md) ·
**Spec §6.4 (accuracy): ACTIVE** — first certificate in this family with a
judge-independent reference.

> *"We did not ask whether the local judges agreed; we asked whether their agreement was
> resolved against a traceable oracle — and the answer was no for single-use magnitude
> verdicts."* (scope epigraph, CDX #010, adopted REV #023)

> **QUALIFICATION OUTCOME: FAILED for the declared use.** This certificate certifies the
> MEASUREMENT of a judge panel, not the panel. The surviving J=3 local panel produced
> statistically real differences on every tier and could not certify the magnitude of any
> of them: its own discrimination band (Band B ≈ 2.5 on a 4-point span) exceeds even the
> blowout-tier oracle gaps. NO single-use magnitude verdict is certified. The refusal is
> the finding. *(The attended review "APPROVE WITH NOTES" approves this study's handling
> and honesty — it does NOT approve the judges; the panel failed qualification. — CDX
> #011 §4.1 language, adopted.)*

## 1. Measurement system under qualification

| | |
|---|---|
| Instrument | **Surviving J=3** local panel — pinned J=4 minus one dead instrument (see §8.1) |
| — Gemma | `gemma4:12b` |
| — LiquidAI | `hf.co/LiquidAI/LFM2-24B-A2B-GGUF:Q4_K_M` |
| — MiniCPM | `minicpm-v:latest` — **near-constant: 73% of its 276 ratings were "4"** |
| Panel character | Effectively **≈2 informative judges plus a near-constant** (GAUGE #010; adopted REV #024/CDX #011). No RESOLVED magnitude verdicts were issued; recompute-without-minicpm is successor work. |
| Procedure | Blind 1–5 rating; one response/call; opaque IDs; no pairwise exposure; judges never see tests, tiers, configs, or the oracle |
| Replication | R=3 per (task, config, judge); temp 0.6; seeded |
| Generators | cfg-A `qwen2.5-coder:32b` (full prompt) vs cfg-B `qwen2.5vl:7b` (level-2 degraded, pinned on pilot evidence only) — zero generator–judge lineage overlap |
| Measurand | Δ = mean(cfg-A) − mean(cfg-B) per tier, balanced crossed design, delta basis (judge level main-effect cancels) |

## 2. Reference (the oracle) — a real denominator at last

- **Reference:** hidden pytest suites per task ("CRM-inspired reference corpus", 55
  ledger-PASS tasks, adversarially verified — blind reimplementation + sneaky-wrong
  attack per task; msai-eval `5d64dca`). NOT an accredited reference material; no ISO
  17034 claim is made.
- **u_ref: declared 0.0, not assumed silently.** Residual = test-suite correctness risk,
  mitigated by the adversarial gate (the one suite that failed it, t36, was dropped
  before the study). Oracle execution: deterministic sandbox, 2× replication,
  discordance ⇒ quarantine (t32 quarantined, §8.2).
- Tier assignment: mechanical from oracle gap g = passrate_A − passrate_B (resolve
  |g|≥0.5 / subtle 0<|g|<0.5 / tie g=0), assigned after oracle, before judging.

## 3. Resolution verdicts (two-band gate; Band B is THE GATE and it was wider than the truth)

| tier | n (balanced) | Δ | sig | U (Band B) | U 95% CI | ν_eff | verdict [WS] | [dominant] |
|---|---|---|---|---|---|---|---|---|
| resolve | 29 | +1.10 | yes | 2.50 | [1.72, 4.60] | 8.9 | **BELOW** | BELOW |
| subtle | 7 | +0.78 | yes | 2.56 | [1.73, 4.94] | 7.9 | **BELOW** | BELOW |
| tie | 2 | -0.17 | no | 1.66 | [1.19, 2.72] | 12.4 | **WITHIN-NOISE** | WITHIN-NOISE |

- **Scope (CDX #010, adopted):** Band B / U applies to the balanced non-null subset, not
  the full generated population. Units excluded from the gauge for unbalanced cells
  (honest judge refusals on degenerate cfg-B output): **t01, t02, t03, t04, t06, t08, t10, t23** — these are
  exactly where cfg-B failed grossly, so the balanced band can UNDERSTATE the operating
  hazard. Sensitivity: all-valid panel Δ (resolve +1.02, subtle +0.68) tracks the
  balanced Δ in direction and order — consistency, not proof.
- provisional = true on every verdict (J<5, spec §6.6). Both dof modes agree on every
  state.
- "Conservative" is used on this certificate ONLY as: conservative **for the
  no-RESOLVED-magnitude certification** (a near-constant judge deflating the
  between-judge term could not have flattered a refusal; it could only have flattered a
  RESOLVED, and none was issued). It is NOT a blanket claim about the study. (CDX #011
  §2b/§4.3, adopted.)

## 4. Accuracy layer (spec §6.4 ACTIVE) — per-judge proficiency vs the oracle

Declared map: judge preference per task = Δ(mean ratings)/4 (span-normalized, −1..1),
scored against oracle g with u_pred from each judge's own replication scatter (k=2).

| judge | n tasks | conformance | \|En\|≤1 rate | max \|En\| | flagged tasks |
|---|---|---|---|---|---|
| gemma4:12b | 46 | 0.239 | 0.500 | 5.5 | 11 |
| LFM2-24B-A2B-GGUF:Q4_K_M | 46 | 0.457 | 0.489 | 7.0 | 23 |
| minicpm-v:latest | 46 | 0.130 | 0.214 | 6.5 | 22 |

- Every judge deviates from the oracle beyond its own repeatability on most tasks:
  per-instrument bias, not noise.
- **Human triangulation (attended review, GAUGE #010; CDX #011 §2c language adopted):**
  the operator's independent per-judge grades qualitatively corroborated the H4
  direction (LFM2 strongest surviving judge) and independently identified minicpm as
  near-constant. They did NOT provide a decision-grade per-judge ranking (n=30 grades,
  rubric stated after grading, non-coder review of AI-translated cases).

## 5. Pre-registered hypotheses (frozen at seal `19bdfc44…14cd5`, REV-LANE #013)

- **H1 (sanity): PASS.** Panel-Δ sign tracks oracle-gap sign on 33/36 scoreable resolve
  pairs = **91.7%**, Jeffreys 95% [79.4%, 97.6%], frozen bar ≥90%.
- **H2 (keystone): DEMONSTRATED.** Every subtle-tier pair carries an oracle-certified
  nonzero gap; the panel's verdict state is BELOW. "Statistically real but below
  single-use resolution" is calibrated against ground truth, not consensus: the gaps are
  real and the refusal to certify them is correct. To our knowledge — and absent from
  our 40-citation related-work sweep (docs/RELATED_WORK.md, 2026-07-03) — this is the
  first such demonstration for LLM judges.
- **H3 (consensus-wrong rate, the headline estimand): 6.8% pooled, Jeffreys [2.0%,
  17.1%]** (3 events / 44 scoreable pairs; resolve 2/36, subtle 1/8). **Structure at
  n=3: MIXED** — shared errors are REAL and OBSERVED (the panel jointly favoring a
  worse-but-plausible solution; independently confirmed by the attended review), AND
  idiosyncratic single-judge failures are observed; the rate of each is
  hypothesis-generating, not estimated. First observed shared-wrong events: 2/3 wrong
  events were shared in this run; sample too small to estimate shared-error structure.
  (Language per CDX #010 → REV #023 → GAUGE #009 → operator's first-party correction.)
- **H4: measured** (§4). En conformance 13.0%–45.7%; all three judges flagged on
  multiple tasks.

## 6. Attended review (prereg §7, first-class stage) — DISCHARGED

**Outcome: APPROVE WITH NOTES** (operator, 2026-07-10; GAUGE #008 record, verbatim
verdicts preserved). Coverage 10/10 spot-check items including all three consensus-wrong
events. Scope, disclosed: a NON-CODER review of the judges-against-the-oracle via
AI-authored plain-English case translations — it independently validates the
judge-vs-truth comparison, the obvious-garbage failures, and the study's honesty; it
does not re-verify the oracle on subtle cases (operator's check #1: UNSURE, preserved).
Operator's note, verbatim: *"None of them performed at levels that impressed me but
certain models did on average do better than others. That to me is a signal."* Domain
scope flag from the same note: **this study is all code**; transfer to other judgment
domains is unestablished.

*"The human review did not rescue the panel; it made the panel's failure more legible."*
(CDX #011, adopted.)

## 7. Denominator map (do NOT compare percentages across rows — CDX #010/#011)

| number | denominator |
|---|---|
| 828 ratings | all (task, config, judge, rep) rows |
| 14 nulls | of 828 rows (per-judge max 3.3% < 10% refuse threshold) |
| 46 tasks | analysis tasks oracled (47 minus t32 quarantined) |
| 44 pairs | tasks with g≠0 and valid panel data (H1/H3 denominator) |
| 36 / 8 / 2 | tier sizes (resolve / subtle / tie) |
| 29 / 7 / 2 | balanced-subset gauge n per tier (§3) |
| 3 events | consensus-wrong (H3 numerator) |
| 276 ratings | minicpm's rows (73% constant-4 denominator) |
| 30 grades | operator's per-judge human grades (§4 triangulation) |

## 8. Deviations & disclosures (logged, never retrofitted)

1. **Dead pinned judge:** `llama3.2-vision:11b` failed to load on the study host (the
   Ollama runner dropped the `mllama` architecture between pin-verification and run).
   EXCLUDED-AND-DISCLOSED per prereg §5/§8; substitution rejected; panel J=3 = floor.
2. **t32 quarantined** (oracle replication discordance, §2 clause).
3. **14/828 null ratings** via the three-way ingest (None + NaN; the NaN class = judges
   honestly declining to rate degenerate cfg-B output, incl. 31-byte "@@@…" generation
   collapses; the oracle scored those 0.0 deterministically). Judge honesty
   differential, disclosed: gemma4 and minicpm refused to rate garbage; LFM2 graded it
   (5/5) — see §4.
4. **Balanced-subset gauge** (§3) with named exclusions.
5. **Labeled peek containment:** two direction-stat commands ran post-data/pre-analysis
   (session log 2026-07-09, quoted in analyze_study.py header). Rules were sealed
   2026-07-03, six days before any datum existed; no estimand, threshold, exclusion, or
   classification changed post-peek; interpretive prose authored post-analysis as
   results reporting.
6. **Degradation pinned on pilot only** (level 2; level-1 evidence archived in-repo).
7. **Verification chain, lineages disclosed (P19):** authored by rev-lane
   (Anthropic/Fable); gate + study chain independently executed by gauge-lane — same
   model lineage, disclosed (GAUGE #006); adversarial review by codex-lane
   (OpenAI lineage, from relayed primaries; raw artifacts unverified by that lane —
   CDX #010/#011); human row: operator's attended review + per-judge grades (§6, §4).
   A non-Claude evidence-slice run is on the publish checklist (KB #049) before broad
   release.

## 9. Verify (P18 — the skeptic's commands)

```
shasum -a 256 benchmark/oracle_run/oracle_study_scores.json   # → 3e19dd3b0061… (this cert no.)
git show 60c6525:docs/CODE_ORACLE_PREREG.md | shasum -a 256    # → 19bdfc44…14cd5 (the seal)
.venv/bin/python benchmark/oracle_run/analyze_study.py         # → reproduces analysis_results.json
.venv/bin/python benchmark/oracle_run/render_certificate3.py   # → reproduces this document
.venv/bin/python -m pytest -q                                  # → suite green
```

Evidence chain: corpus `5d64dca` → gate `dcc77d2`/`746a02b` → study `bb81cbc` → analysis
`006b04c`. Trust attaches to the receipt, not the author.
