# CERTIFICATE_SPEC grounding table — clause citations resolved via metrology-advisor KB

*2026-07-02, review lane. First live use of the KB skill: the normative claims in
CERTIFICATE_SPEC.md / resolution_verdict.py resolved to held clauses. For the gauge lane:
fold into the spec as §10 (or keep as companion) in the next ledger pass. Retrieval:
hybrid mode, `rag/retrieve.py --cite`; fidelity tiers preserved per KB honesty rules.*

## The four spec claims, grounded

| Spec claim | Clause (as held in KB) | Tier / how to cite |
|---|---|---|
| Four-state verdict (WITHIN-NOISE / BELOW / AT-EDGE / RESOLVED) | **ILAC-G8:09/2019 §4.2.3** — non-binary decision rules: Pass / Conditional Pass (inside guard band, below TL) / Conditional Fail / Fail; "conformity … is inherently connected to the decision rule employed" | official_guidance — cite directly |
| Guard-banded acceptance (AL = TL − w) | **ILAC-G8:09/2019 §4.2.1–4.2.2** — binary simple-acceptance and guard-banded rules | official_guidance — cite directly |
| Documented decision rule w/ false-accept/false-reject risk | **ISO/IEC 17025:2017 §7.8.6** | *interpreted paraphrase of paid ISO* — write "operationalizing ISO/IEC 17025:2017 §7.8.6", never quote |
| Decision-rule definition (uncertainty accounted for in accept/reject) | **JCGM 106:2012 §3.3.12** (adapted from ASME B89.7.3.1-2001); corroborated UKAS LAB-48 Ed5 Appendix A glossary | licensed primary copy — short attributed quotes only |
| Multi-state rules legitimate (PASS/FAIL/Retest) | **UKAS LAB-48 Ed5:2024, Decision rules — Basics** | licensed primary copy — short attributed quotes only |
| Conformity probability / risk framing | **JCGM 106:2012 §8.2.1** (simple acceptance/shared risk), **§8.2.3** (U ≤ Umax criterion, k=2) | licensed primary copy — short attributed quotes only |
| Expanded uncertainty U = k·u_c | **JCGM 200:2012 (VIM) §2.35, §2.38**; **JCGM 100:2008 (GUM) §2.3.6, §6.3.3** (k=2 ≈ 95%) | licensed primary copy — short attributed quotes only |
| Welch–Satterthwaite ν_eff (the dof contract) | **JCGM 100:2008 §G.4.1 Eq.(G.2b)**: ν_eff = u_c⁴ / Σ(u_i⁴/ν_i), ν_eff ≤ Σν_i; U_p = t_p(ν_eff)·u_c | formula/exact — quotable; this is literally what `resolution_verdict.py` implements |
| ndc definition + ≥5 adequacy threshold (advisory) | **AIAG MSA-4 §III.B** — ndc = 1.41·(PV/GRR) truncated; ndc ≥ 5 adequate, <5 inadequate | **paid manual** — cite as "AIAG MSA-4 convention", never as quotation |
| %GRR bands (10/30) if ever cited | **AIAG MSA-4 §III.B** — <10% acceptable, 10–30% marginal, >30% unacceptable | same convention rule |

## Three finds beyond the ask

1. **Pre-registration is normative, not just house discipline.** ILAC-G8 §4.2.3 (with
   ISO/IEC 17025 §7.1.3): the decision rule "is expected to be agreed BEFORE the
   measurements are taken." P13 (PRE-REGISTER THE CUT) now cites a standards clause.
2. **AT-EDGE has a normative reason to exist.** JCGM 106:2012 §9.1.3: the probability of
   an incorrect decision "is greatest when measured values are close to the tolerance
   limits." The AT-EDGE state is the verdict-level acknowledgment of exactly that zone.
3. **The capability-index clause for the accuracy anchor — CORRECTED (was mislabeled
   "TUR" in v1 of this table; caught by the KB session's re-verification, REV-003 by a
   second road).** JCGM 106:2012 §3.3.17 defines the **measurement capability index Cm**
   (tolerance over a multiple — taken as 4, cf. §7.6.3 — of standard uncertainty). It is
   the same 4:1 family as TUR but a different named quantity. **TUR itself is ILAC-G8:09/2019
   §1.13 (redistributable with attribution): TUR = TL/U, tolerance over process uncertainty.**
   Consequences: (a) reference.py's U_ref adequacy ratio contains no tolerance and must not
   be called TUR — rename to "reference adequacy ratio (Cm-style, per JCGM 106 §3.3.17)";
   (b) CERTIFICATE_SPEC §6.4's "adequacy ratio (TUR)" must be renamed the same way, with
   TUR reserved for contexts holding a real tolerance limit. GC/1.1 item.

## Convergence event #4 (logged 2026-07-02, same day, two directions)

ILAC-G8 §4.2.3 was hit twice independently within hours: this table found it **validates**
the four-state verdict; the KB session's fidelity reviewer found its other half **indicts**
the spec (REV-004 — the agreed-BEFORE-measurement requirement, via ISO/IEC 17025 §7.1.3,
has no counterpart: `guard_k`/`resolution=` are free post-hoc knobs and no certificate
field attests the decision rule predates the scores). Both are true. GC/1.1 therefore
gains a **required Decision-Rule field**: construction, multiplier, dof basis, and *when
it was fixed relative to measurement* — plus an honesty invariant that a rule tuned after
scores exist voids the certificate.

## Redistribution tiers (per KB fidelity rules, for anything quoted onward)

- **ILAC-G8** clauses: `redistributable` — quote freely with attribution.
- **JCGM 100/106/200** holdings: `licensed primary copies`, *private-only for wholesale
  carriage* — short attributed definition quotes fine; never reproduce sections.
- **ISO/IEC 17025**: `interpreted` paraphrase of a paid standard — "operationalizing §X".
- **AIAG MSA-4**: paid manual; formulas/thresholds held as conventions — cite as
  "AIAG MSA-4 convention", never as quotation.

## The meta-finding

The four-state verdict was derived in-session from first principles (binary beyond_gauge
is dishonest at small dof) and only afterward grounded: it reconverges with ILAC-G8
§4.2.3's non-binary scheme almost state-for-state. Independent reconvergence with the
written standard is stronger than derivation FROM the standard — same argument as the
two-lane Guarded Claim convergence. Note it in the preprint.

## Conformance notes (per KB honesty rules)

- ISO/IEC 17025 clauses in the KB are interpreted paraphrases of a paid standard —
  license holders should verify against the actual text.
- AIAG MSA-4 values are held as uncopyrightable conventions from a licensed manual —
  cite as convention.
- Edition currency checked: all cited editions current per KB edition table (ILAC-G8
  09/2019; JCGM 100:2008; JCGM 200:2012; LAB-48 Ed5:2024; 17025:2017; MSA-4).
- A qualified human must review against the actual current standards before any
  compliance-critical use. (Advise, don't certify.)
