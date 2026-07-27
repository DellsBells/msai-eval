# Gauge Certificate Specification — MSAI-GC/1.0-draft

*Status: DRAFT. 2026-07-02. This document defines a portable certificate format for
LLM-as-judge (and general automated-judge) measurement systems. It is deliberately boring:
stable field names, versioned changes, no cleverness. Anyone may implement it without
permission. Conformance is defined entirely by this document.*

Keywords MUST / MUST NOT / SHOULD / MAY are per RFC 2119.

---

## 1. Purpose and scope

A Gauge Certificate states what a judging measurement system can **resolve** — its
precision, reproducibility, and resolution under stated conditions — in a form a
decision-maker can act on without re-deriving the analysis. A certificate is a *Guarded
Claim* (PATTERN_LANGUAGE.md): assertion + band + scope + refusal, rendered as a document.

A certificate **is not** a statement of correctness. Accuracy claims require a traceable
reference (§6.4) and are out of scope for GC/1.0 except as an explicit optional section.

## 2. Versioning and identification

- Spec versions are `MSAI-GC/<major>.<minor>[-draft]`. Minor versions are strictly
  additive (new OPTIONAL fields/sections only). Field semantics never change within a
  major version; renames and removals require a major bump.
- Every certificate MUST print its spec version string verbatim (e.g. `MSAI-GC/1.0-draft`).
- Every certificate MUST carry a certificate number derived from a cryptographic hash of
  the raw score data it was rendered from (RECOMMENDED: `sha256`, first 12 hex chars,
  prefixed by an issuer tag), and MUST name the data file(s) it is bound to.
- A certificate MUST state its issue date and the measurement date(s).

## 3. Required sections (order fixed)

| # | Section | Contents (all REQUIRED unless marked) |
|---|---|---|
| 0 | Header | title, certificate no., issue date, data date, basis (count of ratings), hash binding, **spec version** |
| 1 | Scope banner | the precision-only disclaimer (§6.1, verbatim or equivalent-in-meaning) |
| 2 | Measurement system | instrument identity: every judge's exact model ID; procedure (blinding, rating scale, exposure mode); replication (R, sampling conditions); measurand definition; design (n × configs × judges × R) |
| 3 | Reference conditions | anchors/references used, each labeled either `consensus anchor` (agreement only) or `traceable reference` (with u_ref and TUR) |
| 4 | Results | per comparison: point estimate Δ, effect size (SHOULD), expanded uncertainty U with coverage factor k, U's own 95% interval, effective dof and the dof rule used, continuous disclosure P(\|Δ\|>U) (SHOULD), and the four-state verdict (§5) |
| 5 | Uncertainty budget | every component with u (1σ), dof (or ∞ for Type B), and identification of the dominant component |
| 6 | Disclosures | every warning emitted by the underlying analysis, **verbatim**, plus standing limitations (scale, scale-type approximations, anchor caveats, scope of rubric wording) |
| 7 | Qualification statement | qualified / not qualified, under what conditions, and the void-outside-scope clause (§6.3) |

Machine-readable companion (JSON mirroring §§0–7 field-for-field) is OPTIONAL in GC/1.0
and RECOMMENDED for GC/1.1.

## 4. Field semantics (normative)

- **Δ (delta):** difference of means between a config and an explicitly named baseline,
  on a stated scale. The measurand MUST be stated (absolute vs delta basis; what cancels).
- **U:** expanded uncertainty = k·u_c where u_c is the combined standard uncertainty of
  the gauge for this measurand. The coverage basis for k MUST be stated.
- **U interval [U_lo, U_hi]:** 95% interval for the true U given u_c's effective dof
  (fiducial/chi-square construction or documented equivalent).
- **Effective dof:** the certificate MUST state which dof rule produced the verdict
  (RECOMMENDED contract: Welch–Satterthwaite ν_eff) and SHOULD disclose a conservative
  alternative (e.g. dominant-component dof) when they disagree.
- **Replication (R):** independent re-readings under stated sampling conditions. R=1
  (no replication) MUST render the gauge UNQUALIFIED (P3).

## 5. Verdict state machine (normative)

Exactly four states. Given significance of Δ against gauge noise, and U's interval:

| State | Condition | Meaning printed on certificate |
|---|---|---|
| WITHIN-NOISE | not significant | not distinguishable from zero on this gauge |
| BELOW | significant AND \|Δ\| ≤ U_lo | statistically real; magnitude NOT certified (below resolution) |
| AT-EDGE | significant AND U_lo < \|Δ\| < U_hi | at the gauge's resolution edge; **no side is forced** |
| RESOLVED | significant AND \|Δ\| ≥ U_hi | real and above resolution; magnitude certified |

Implementations MUST NOT collapse AT-EDGE into a binary pass/fail. The refusal states
(WITHIN-NOISE, BELOW, AT-EDGE) are first-class results, not errors.

## 6. Honesty invariants (normative — a certificate violating any of these is not a GC)

1. **Precision-only banner.** Unless §6.4 is satisfied, the certificate MUST state that no
   accuracy is claimed, that no traceable reference was supplied, and that high agreement
   is equally consistent with a correct rubric, a shared wrong rubric, or gaming.
2. **Verbatim disclosure.** Warnings from the underlying analysis MUST appear unedited.
   Summarizing away a caveat voids the certificate.
3. **Void outside scope.** The certificate MUST enumerate its conditions (rubric wording
   frozen vs robust, design shape, score use) and declare itself void outside them.
4. **Accuracy claims** MAY appear only when tied to a judge-independent reference with
   stated u_ref and a **reference adequacy ratio** (capability-index style, Cm per
   JCGM 106:2012 §3.3.17) meeting a declared threshold, and MUST be scoped to that
   reference. The term **TUR is reserved** for tolerance-over-uncertainty (TL/U, ILAC-G8
   §1.13) and MUST NOT label a ratio containing no tolerance. *(Renamed 2026-07-02,
   cross-organ audit REV-003 — the prior draft's "adequacy ratio (TUR)" was a misnomer.)*
5. **Reproducibility of the artifact.** A certificate MUST be regenerable from persisted
   raw scores by a stated command/procedure; the hash binding (§2) makes tampering evident.
6. **Small-panel candor.** Below 5 independent judges, RESOLVED/BELOW/WITHIN-NOISE
   verdicts MUST carry a provisional flag; AT-EDGE needs no flag (it already states
   indeterminacy).
7. **Decision rule declared before measurement.** *(Added 2026-07-02, cross-organ audit
   REV-004; operationalizes ILAC-G8 §4.2.3 with ISO/IEC 17025 §7.1.3 — conformity is
   inherently connected to the rule employed, agreed before measurement.)* The certificate
   MUST print the decision rule as used (band construction, multiplier, dof rule,
   resolution, edge-zone definition) **and attest when it was fixed relative to scoring**.
   A rule tuned after scores exist does not automatically void the certificate — but the
   post-hoc evolution MUST be disclosed on the document, and a rule tuned *against the
   verdict outcome* (knob-sweeping until the verdict flips) does void it. Instances issued
   before 2026-07-02 predate this invariant (see change log).

## 7. Conformance

An implementation conforms if it: produces all required sections with the semantics of §4,
implements the §5 state machine exactly, and enforces every §6 invariant mechanically
(not as documentation). Reference implementation: `benchmark/certificate.py` in msai-eval
(to be promoted to `msai certify`). Independent implementations are the point (P15) —
no permission, trademark, or coordination is required to issue conformant certificates.

## 8. Self-application (the Unbroken Recursion rule, P14)

The project that maintains this spec MUST hold its own public claims to certificate grade:

- Empirical claims about MSAI's performance are pre-registered before scoring, reported
  with bands and scope, and refused (labeled indeterminate) when at-edge.
- Validation runs persist raw scores and are regenerable, hash-bound, like any certificate.
- Confirmed defects become permanent regression tests (the adversarial ratchet); the
  ledger only grows.
- If the maintainers ever exempt their own claims from these rules, this section obliges
  any implementer to say so plainly: the fractal is broken and the spec has lost its
  authority. Honesty here is load-bearing, not aspirational.

## 9. Change log

- 1.0-draft (2026-07-02): initial draft. First conformant instance:
  `benchmark/CERTIFICATE_MSAI-8C06733F42F0.md` (J=5 frontier panel, 900 ratings).
- 1.0-draft, same-day errata (2026-07-02, from the cross-organ adversarial audit — 20
  findings; independent re-verification produced **21 verdicts over 17 of the 20 findings
  plus 2 tier-3 spot-checks: 19 CONFIRMED, 2 PARTIAL, 0 REFUTED**; REV-009/010/012 were
  accepted on the reviewer's evidence but NOT independently re-executed — queued with the
  gauge lane. An earlier statement of this tally ("18/3/0, every finding re-executed") was
  wrong on both counts and is corrected here per P14; caught by the KB session.):
  §6.4 "TUR" renamed to reference adequacy ratio (REV-003); §6.7 decision-rule
  declaration invariant added (REV-004); the first instance re-issued same number with
  hardened renderer (utf-8/atomic/argparse, REV-006), literal NO ACCURACY CLAIMED banner
  (REV-016), stated k coverage basis + declared data date (REV-011), renderer version +
  results digest pinned (REV-020), and evidential-status disclosures (REV-001/005/015).
