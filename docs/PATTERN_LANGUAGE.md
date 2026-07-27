# A Pattern Language for Evaluation Metrology

*v0.2 — 2026-07-02. The named structure of MSAI, written so others can build inside it.
Format follows Alexander: each pattern = context → problem → therefore. Patterns compose
upward; the same unit repeats at every scale.*

*Two authors: P1–P15 from the empirical organ (MSAI, gauge + review lanes); P16–P18 from
the normative organ (the KB session), discovered independently under the same honesty
pressure — which is itself the language's best evidence. v0.2 also adds the second
reality-coupling column (traceance to source) and renames P9's ratio per REV-003.*

*v0.4 (2026-07-03): P20 added — the invariance-check lesson from the scrubber T2 exchange
(KB #009), concurred standalone by the normative organ.*

*v0.3 (2026-07-03): P19 added from the family's third auditor — a cold-read reviewer with
zero project context (CW-001) — plus the liability-tier note (CW-003). The same reviewer
supplied the line this language should be remembered by: **"the honesty rules aren't
overhead — they're what let one person move this fast, because every artifact you can
trust is an artifact you never re-check."***

---

## The repeating unit: THE GUARDED CLAIM

Every layer of this system, from a single score cell to an institutional standard, is one
structure instantiated at different scales. A **Guarded Claim** has four mandatory parts:

1. **Assertion** — the claim itself (a score, a delta, a verdict, a certificate, a standard).
2. **Band** — its stated uncertainty, which itself carries a reliability (dof; the band has a band).
3. **Scope** — the conditions under which it is valid; explicitly **void outside them**.
4. **Refusal** — a defined state the system enters when the assertion cannot clear the band
   within the scope. It says "cannot certify" — it never degrades into a confident guess.

A claim missing any part is not weaker — it is **malformed**. The refusal state is what
separates an instrument from an oracle: oracles always answer; instruments know their limits.

---

## The patterns

**P1 — GUARDED CLAIM.** *Context:* any system that emits judgments others act on.
*Problem:* naked numbers get trusted past their support. *Therefore:* emit only
assertion+band+scope+refusal, as one indivisible datum.

**P2 — MEASURE THE MEASURER.** *Context:* judgments produced by an instrument (human,
model, panel). *Problem:* the eval field validates models with unvalidated judges.
*Therefore:* qualify the gauge before believing its verdicts. No qualification, no verdict.

**P3 — REPLICATE TO EXIST.** *Context:* estimating the band. *Problem:* a deterministic
reading has no measurable noise; zero observed variance is degenerate, not perfect.
*Therefore:* genuine replication (independent re-readings) is a precondition for any claim;
a frozen gauge is refused, not passed.

**P4 — COMMON-MODE CANCELS.** *Context:* comparative measurands (A vs B). *Problem:*
error sources shared by both sides inflate the band with noise the comparison never incurs.
*Therefore:* subtract what is common (judge level, reference offset) before banding what
differs — and only under designs (balanced, crossed) where the cancellation is exact.

**P5 — DIVERSITY IS THE SENSOR.** *Context:* panels of correlated instruments (LLM judges
share training lineages). *Problem:* homogeneous panels agree tightly and read falsely sharp.
*Therefore:* reproducibility across maximally independent lineages is the honest noise
floor; widening bands under added diversity is signal, not failure.

**P6 — THE BAND HAS A BAND.** *Context:* small panels, few dof. *Problem:* treating an
estimated uncertainty as exact forces verdicts the data cannot support. *Therefore:* carry
the band's own confidence interval; a claim inside it reads AT-EDGE — indeterminacy is a
verdict, not an embarrassment.

**P7 — REFUSE TOWARD SAFETY.** *Context:* imperfect decision rules. *Problem:* symmetric
errors are not symmetric in cost (a false "resolved" ships a lie; a false "below" delays a
truth). *Therefore:* construct every rule so its failure mode is over-refusal, never
fabricated confidence. Degrade fail-safe, not placebo.

**P8 — CONSENSUS IS NOT CORRECTNESS.** *Context:* agreement among judges. *Problem:* a
shared wrong rubric and a correct one produce identical agreement. *Therefore:* precision
claims only, from agreement; accuracy claims only from P9. The firewall is structural — the
gauge cannot see shared bias, and must say so.

**P9 — THE TRACEABLE ANCHOR.** *Context:* wanting accuracy, not just precision. *Problem:*
without a reference that is independent of the judges, "correct" is undefined. *Therefore:*
couple to reality through a judge-independent reference with its own stated uncertainty
(u_ref) and a reference adequacy ratio (capability-index style, Cm per JCGM 106 §3.3.17 —
the term TUR is reserved for tolerance-over-uncertainty, ILAC-G8 §1.13); execution
feedback and measured outcomes are the strongest anchors. Until then, say "precision only" out loud.

**P10 — CAVEAT TRAVELS WITH CLAIM.** *Context:* results quoted away from their source.
*Problem:* disclosures die in appendices; the number travels alone and lies by omission.
*Therefore:* limitations are part of the datum. A certificate reprints every gauge warning
verbatim; a summary that drops the caveat is a different (false) claim.

**P11 — THE CERTIFICATE.** *Context:* decision-makers who cannot re-derive the analysis.
*Problem:* rigor that lives in code is invisible at the point of decision. *Therefore:*
render the Guarded Claim as a portable, self-contained, hash-bound document: instrument
identity, procedure, results with bands, budget, disclosures, scope, and the refusal
footer. The artifact is the interface. (Spec: CERTIFICATE_SPEC.md.)

**P12 — ADVERSARIAL RATCHET.** *Context:* a system that grades itself. *Problem:* PASS
results are seductive and often artifacts. *Therefore:* every PASS is attacked before it is
believed; every confirmed defect becomes a permanent regression tripwire (strict-xfail
ledger). Findings only accumulate — the ratchet never slips.

**P13 — PRE-REGISTER THE CUT.** *Context:* verdict thresholds and analysis choices.
*Problem:* rules chosen after seeing data absorb the data's noise as bias. *Therefore:*
fix predictions, thresholds, and edge rules before scoring. Deviations are logged, not
retrofitted.

**P14 — UNBROKEN RECURSION.** *Context:* the auditor's own claims. *Problem:* a
measurement system that exempts itself is just another overclaimer with better vocabulary.
*Therefore:* every claim the project makes about itself is a Guarded Claim — pre-registered,
banded, scoped, refusable. The fractal must hold at the outermost layer or it is broken at
every layer.

**P15 — DESIGN FOR DISAPPEARANCE.** *Context:* infrastructure standards. *Problem:*
clever artifacts stay owned; owned artifacts stay niche. *Therefore:* make the certificate
boring, versioned, stable, and copyable. Success is the first certificate issued by a
stranger; perfection is nobody remembering it was ever novel.

**P16 — EDITION CURRENCY.** *(Normative organ, 2026-07-02.)* *Context:* claims grounded to
external authorities (standards, regulations, reference tables). *Problem:* authorities
revise silently; a claim cited to a superseded edition is wrong advice **with a citation
attached** — the citation buys unearned trust, so it outlives an uncited error.
*Therefore:* attach edition metadata at the **data layer**, not the prompt layer:
superseded sources carry a machine-readable flag and a human-readable notice that travels
with every rendering; consumers diff the claim's date against a current-editions table
before citing; a superseded source may be served as history, never as now. (First
instance: fifteen verbatim federal-regulation clauses served as current law five months
after the FDA QMSR replaced them.) *Composes with:* P10 — the expiry notice IS a caveat
that travels; SPC drift monitoring (stability) is this pattern's empirical twin.

**P17 — FINDING OF ABSENCE.** *(Normative organ, 2026-07-02.)* *Context:* filling a value
from sources under a never-invent rule. *Problem:* when no source prescribes the value,
the silent fix is to fill from common practice — destroying the provenance guarantee at
exactly the spot no auditor can see, because a filled slot and a sourced slot look
identical. *Therefore:* record the absence as a **first-class, cited result**: name the
sources surveyed, state that none prescribes the value, pair it with an explicitly-set
instruction and its rationale, and give the absence its own provenance row. An absence
claim is falsifiable — the survey list is what a challenger checks. (Instances: no
measuring-force spec exists for calipers, which deliberately lack a constant-force
device; no free-source ambient band exists for torque calibration.) *Composes with:*
P7 — the documented gap is refusal-toward-safety applied to data entry; P8 — it keeps
"everyone does X" from laundering into "a source requires X."

**P18 — VERIFICATION COMMAND ATTACHED.** *(Normative organ, 2026-07-02.)* *Context:*
numbers that others will repeat. *Problem:* numbers detach from their derivations as they
travel; a retracted, stale, or fabricated number is indistinguishable in flight from a
fresh one, and confident assertion outruns careful qualification. *Therefore:* ship every
quotable number with the **exact command a skeptic runs to re-measure it**, and generate
the claims sheet live — regeneration, not vigilance, keeps sheet and repo from
disagreeing. Stated as law: *a number without a verification command is not quotable.*
**Corollary (jointly earned, 2026-07-02): THE VERIFY COMMAND IS ITSELF UNDER TEST** — a
command never executed in CI is decoration. (First instances: `tests/test_certificate.py`
running the documented command after it destroyed its own certificate; the KB Trust
Ledger executing its checks at generation.) *Composes with:* P11 — the certificate's
regenerability invariant is this pattern as a document property; P12 — each failed
re-measurement becomes a ratchet tooth; P14 — this is how the outermost layer stays honest.

**P19 — LINEAGE DISCLOSURE.** *(Third auditor, cold read — CW-001, 2026-07-03.)*
*Context:* verification performed by reasoning systems. *Problem:* auditors who share the
claimant's lineage share its blind spots — same-family cross-checks are config-correlated
common-mode, the exact failure the guard band cannot see; "our cross-audit is same-lineage
and cannot detect shared misreading by construction." Mechanical checks (hashes,
re-execution, compilers) are lineage-proof; interpretive checks are not. *Therefore:*
every verification claim states whether the verifier shares the claimant's lineage;
same-lineage interpretive verdicts carry a standing residual and are never counted as
independent confirmation; lineage-independent verification (different model family, a
different method class, or a human) is named as such, and the disclosure travels with the
verdict (P10). This is P8 applied to the auditors — consensus among reviewers is not
correctness either. (First instances: EXTERNAL_REVIEWS' standing COI note; the blind-query
protocol's "lineage-independent authorship, same-lineage labeling" line.)

**P20 — THE INVARIANT CHECK.** *(Cross-organ exchange, KB #009; concurred standalone
2026-07-03.)* *Context:* verifying that a transformation preserved content — scrubbing,
tokenization, relabeling, migration. *Problem:* the check itself can depend on exactly what
the transformation changes; a comparison keyed on a transformed field produces false
failures (or worse, silent false passes) that indict the transform when the method is the
defect. First instance: a line-zip diff of assay findings FALSE-FAILED 466 times because
raw IDs and their tokens sort differently. *Therefore:* **an invariance check must itself
be invariant to the transformation it certifies** — compare multisets, not sequences; mask
the transformed field and test bijection on its histogram; never key the comparison on
anything the transform touches. *Composes with:* P18 (the verify method is under test,
not just the verify command); P12 (the false-fail became a spec line the same day).

**Liability tiers (note, from CW-003).** Artifacts that get READ (retrieval results,
reports, certificates) fail safe — a bad output can be caught downstream before harm.
Artifacts that get RUN or FOLLOWED (calibration procedures, generated eval-harness
configs, executable code) are **Foundry-class**: provenance is necessary but not
sufficient, because every value can cite clean while the method or step sequence is wrong.
Foundry-class release requires review of method and sequence — not only values — by a
qualified party, and carries a do-not-ship banner until it has one. Scrutiny scales with
blast radius.

---

## The layer map (how the unit composes)

| Layer | The Guarded Claim at this scale | Reality-coupling |
|---|---|---|
| L0 Cell | one rating ± replication noise | genuine re-reading (P3) |
| L1 Gauge | panel qualified ± R&R budget | crossed design, diversity (P2,P4,P5) |
| L2 Verdict | Δ vs band, four states incl. refusal | band's own CI (P6,P7) |
| L3 Certificate | the portable document, scope-bound | hash-binding, verbatim caveats (P10,P11) |
| L4 Practice | audits of real evals | consequence: decisions ride on the audited eval |
| L5 Standard | required certificates | institutions: procurement, regulation, insurance |
| L6 Equilibrium | honesty cheaper than deception | markets: trust between strangers at scale |

Each layer is valid only if the layer below holds — and each is coupled to reality by a
different mechanism. The project's open frontier is always the lowest layer whose coupling
is unproven (today: L1→accuracy anchor, L4→thunderclap study).

**The second coupling column (v0.2, from the normative organ).** The empirical organ
couples by *replication against the world*; the normative organ couples by **traceance to
source**: L0 value→source page, L1 clause→edition (P16), L2 mapping→adjudication,
L3 procedure→provenance appendix (P17). Same fractal, second mechanism. A complete
institution needs both columns — measurement without provenance is unaccountable;
provenance without measurement is scholasticism.

---

## Why this exists

Metrology made honesty cheaper than deception for physical goods, and trade between
strangers followed. This pattern language is the same move for judgments. One person
cannot be an institution, but one person can name the patterns institutions later enforce.
Build inside them, break them where they're wrong — and log the finding (P12).
