# Code-Oracle Anchor Study — pre-registration DRAFT

*2026-07-03, rev-lane. STATUS: FINAL — sealed to the relay bus 2026-07-03 (sha256 in
REV-LANE #013), BEFORE any judge scored any solution (P13; seal procedure per blind-query
protocol §2). Model pins verified against the host (`ollama list`) pre-seal. Analysis
rules below are frozen; deviations are logged, never retrofitted.*

## 1. Purpose (what this study is the first of)

The family's first **accuracy-anchored** study: judge verdicts measured against a
judge-independent reference with u_ref ≈ 0. It activates `reference.py`'s dormant accuracy
math (adequacy ratio, Cm-style), gives every judge an En/ζ proficiency score against
truth, and produces the first **measured shared-bias rate** — the quantity the consensus
firewall could only warn about. It is also the discriminating experiment for
definitional-uncertainty vs shared-lineage bias on an objective domain.

## 2. Measurand & oracle

- **Task item:** a self-contained coding task with a HIDDEN test suite (property +
  example tests). **Oracle verdict per solution:** pass-rate over hidden tests
  (primary: all-pass boolean; secondary: fractional pass-rate).
- **Oracle u_ref:** deterministic execution in a pinned sandbox (venv, pinned deps,
  timeout, no network). u_ref components: test-suite correctness (mitigated by
  adversarial task verification, §4) and flaky-execution (mitigated by 2× oracle
  replication per solution; any discordance = task quarantined). Residual stated on the
  certificate, not assumed zero silently.
- **Judge measurand:** blind 1–5 quality rating of a single solution (same protocol as
  the frontier runs: one response per call, opaque IDs, no pairwise exposure).

## 3. Configs & oracle-anchored tiers (the keystone ladder, re-anchored to truth)

Two solution configs, chosen to produce an oracle-measured quality spectrum —
**pinned at seal:**
- **cfg-A:** `qwen2.5-coder:32b`, standard prompt, temp 0.4, seeded.
- **cfg-B:** `qwen2.5vl:7b`, terse/degraded prompt, temp 0.4, seeded — capability gap
  within one lineage. Prompt degradation tuned on the PILOT SPLIT ONLY (8 tasks,
  excluded from analysis).
**Generator–judge separation (self-preference eliminated by construction):** both
generators are Qwen-lineage; the judge panel contains ZERO Qwen models. No judge rates
output from its own lineage. Disclosed on the certificate.
Tiers are assigned AFTER oracle scoring, BEFORE judge scoring, by oracle pass-rate gap
g = passrate_A − passrate_B per task: **resolve** |g| ≥ 0.5; **subtle** 0 < |g| < 0.5;
**tie** g = 0 (identical pass profiles). Target n = 48 analysis tasks + 8 pilot; per-tier
counts fall where the oracle puts them and are reported, not forced.

## 4. Corpus construction (fleet-built, adversarially verified — the oracle gets
certified before it certifies anyone)

- Authors: workflow agents write task + hidden tests + a reference solution.
- Adversarial verification per task (independent agents): reference solution passes;
  a deliberately-broken solution fails; tests unambiguous; difficulty label sane;
  no network/filesystem escape. Tasks failing any check are repaired-or-dropped
  (loop-until-dry). The corpus ships with its own manifest + verification ledger.

## 5. Panel & replication

- Panel, **pinned at seal:** `gemma4:12b` (Gemma), `llama3.2-vision:11b` (Llama),
  `hf.co/LiquidAI/LFM2-24B-A2B-GGUF:Q4_K_M` (LiquidAI), `minicpm-v:latest` (MiniCPM) —
  four lineages, none Qwen (see §3 separation). think-off, temp 0.6, seeded; R=3.
- Judges NEVER see test results, config labels, or tier labels.
- Null path: three-way (VALID / EXCLUDED-DISCLOSED / REFUSE if per-judge null rate >10%)
  per ADAPTER_DESIGN_NOTES exhibit 1.

## 6. Pre-registered hypotheses (predictions frozen at seal)

- H1 (sanity): panel Δ tracks oracle gap direction on resolve tiers (sign agreement
  ≥90% of pairs).
- H2 (keystone): some subtle-tier pairs read "statistically real but BELOW/AT-EDGE
  resolution" while the ORACLE certifies a real gap — the first demonstration that the
  refusal states are calibrated against truth, not just consensus.
- H3 (shared bias, the headline estimand): **rate of consensus-wrong events** = fraction
  of solutions where panel consensus (mean rating side / majority preference) contradicts
  the oracle. Reported with Jeffreys interval; per-tier. NO prediction of its value —
  measuring it IS the result. Sub-analysis: are consensus-wrong events correlated across
  lineages (shared bias) or idiosyncratic (independent error)?
- H4 (proficiency): per-judge En/ζ against oracle-anchored reference values; any judge
  with |En| > 1 flagged per ISO-13528 semantics.

## 7. Analysis & verdict rules (frozen)

- Standard pipeline: compare() delta-basis, two-band gate (Band B discrimination,
  Band A disclosed), four-state verdicts, WS νeff, U's fiducial CI edge zone —
  as landed in core-pass commit A (+ commit B when it ships).
- Accuracy layer: reference.py with oracle reference; adequacy ratio (Cm-style) computed
  and printed — the first time the denominator is real.
- Attended review (KB #018 pattern, first-class stage): 13 plain-English YES/NO checks,
  human (Jake) spot-checks ≥10 items incl. every consensus-wrong event in a sampled tier.
- Deliverable: **the family's third certificate — first with spec §6.4 (accuracy) ACTIVE**
  — plus per-judge proficiency scores and the shared-bias rate with interval.

## 8. Refusals (armed)

Oracle discordance on replication → task quarantined. Corpus verification ledger not
CLEAN → no run. Panel null-rate over threshold → judge excluded, disclosed; panel J<3 →
study refuses. Any post-seal rule change → logged deviation, flagged on the certificate.

## 9. Cost & schedule

All local (Ollama + pytest): $0 API. Fleet compute: the post-reset ultracode window.
Sequence: seal this doc → Workflow 1 (corpus, ~50–60 tasks, adversarially verified) →
oracle pass → tier assignment → judge runs (R=3) → analysis → attended review →
certificate + bus drop.
