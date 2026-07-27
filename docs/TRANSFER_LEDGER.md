# Transfer Ledger — which metrology disciplines survive contact with AI

*2026-07-10, rev-lane. Proposed by codex-lane (GPT-5.6 instrument, operator-relayed
conversation; provenance: strategic dialogue, not a serialed review). Governing rule,
adopted verbatim:*

> **Transfer the measurement obligation first. Transfer a particular formula only after
> it earns the right to come along.**

*Statuses: SUPPORTED (real-run evidence) · SCOPED (supported within stated limits) ·
ADAPTED (transferred with a documented modification) · FIRST-RUN (activated once;
awaits replication) · MACHINERY-ONLY (built and tested, never exercised on live judges)
· UNPROVEN (open) · DEMOTED (evidence reduced its role). Every row cites its receipt.
A row with no receipt does not get a status — it gets built or refused.*

| # | Metrology principle | AI interpretation | Required assumptions (shakiest first) | Evidence | Status |
|---|---|---|---|---|---|
| 1 | Measurand definition | Δ = mean(config) − mean(baseline) per tier; declared-use label travels with every band | The declared use matches actual use | Frontier cert `MSAI-8C06733F42F0`; oracle cert `MSAI-3E19DD3B0061` | **SUPPORTED** |
| 2 | Instrument identity | judge = model+version+prompt-hash; version bump = renewal event | Identity is checkable at run time | mllama judge death (REV #021); codex 5.6 renewal logged (REV #027) | **SUPPORTED** (practiced twice) |
| 3 | Repeatability (EV) | Same judge re-scores, temp>0, seeded, R≥3 | Instrument frozen during study | 900 + 828 ratings, both studies; u_repeat measured per tier | **SUPPORTED** |
| 4 | Reproducibility (AV) | Between-judge term across lineages | Judges share a comparable rubric reading; panel large enough to estimate | Dominant lever both studies (~44–50% of u_c²); distorted by a near-constant judge at J=3 (GAUGE #010) | **SCOPED** (small-J fragile; constant-judge hazard documented) |
| 5 | Delta basis / level-centering | Judge level main-effect cancels in config-vs-baseline deltas | Balanced crossed design; every judge rates both configs | Commit A `a525e61` + B `52ab23c`; verified REV #015/GAUGE #006 | **SUPPORTED** (design-dependent; unbalanced cells must be excluded — cert #3 §3) |
| 6 | GUM u_c / expanded U as a resolution band (Band B gate) | Per-use discrimination band; does not shrink with N | Ordinal 1–5 treated as interval (disclosed); within-run stationarity; component independence | H2 keystone: verdicts calibrated against oracle truth (cert #3 §5) | **DEMONSTRATED-IN-STUDY**; general validity on nonstationary real-world judges **UNPROVEN** (codex-5.6's level 3) |
| 7 | Welch–Satterthwaite ν_eff | Contract dof for U's own CI; dominant-dof as conservative disclosure | Approximate independence of components | Both certs print k, ν_eff; dof modes agreed on all cert-#3 verdicts but DISAGREED on the frontier resolve tier (RESOLVED vs AT-EDGE — disclosed there as "quote both or quote neither") | **ADAPTED-DISCLOSED** (the disagreement case is why both modes print) |
| 8 | Guard bands / decision rules (ILAC-G8, JCGM 106) | Two-band gate; four-state verdicts; PFA/PFR operating points | Cost asymmetry declared before data | Two-band gate live in compare(), run on both certs; PFA/PFR exists as ratified DESIGN only (KB #038) — no built code | **SUPPORTED** (gate); PFA/PFR **DESIGN-ONLY** (ratified, unbuilt) |
| 9 | Traceability / evidence chain | Certs hash-bound to evidence; seals precede scores; verify commands attached | Artifacts stable and re-hashable | 3 certificates; 2 seals surviving crashes; P18 tests | **SUPPORTED** |
| 10 | Reference adequacy (Cm-style, spec §6.4) | Reference must out-resolve the gauge before accuracy claims | u_ref genuinely small and stated | First activation: oracle study (u_ref declared 0 with residual stated) | **FIRST-RUN** |
| 11 | Proficiency scoring En/ζ (ISO 13528) | Per-judge En vs oracle-anchored values | The declared unit map (span-normalized deltas) is meaningful | H4 (cert #3 §4); human triangulation qualitative-only (CDX #011 §2c) | **FIRST-RUN, SCOPED** (unit map declared, not canonical) |
| 12 | Stability / drift SPC | Judge drift charts; two-gate trend rule (floor + 2× scatter) | Sampling cadence exists; stationarity between renewals | Two-gate rule landed + tested (`52ab23c`); never run on a judge time-series | **MACHINERY-ONLY** |
| 13 | ndc (distinct categories) | Advisory only — never a gate | Treatments not hand-picked (violated by design in our studies) | Ruled selection-sensitive; ADVISORY-ONLY language on the frontier cert; cert #3 omits ndc entirely | **DEMOTED** (evidence-driven) |
| 14 | Reference materials (CRM) | "CRM-inspired" verified task corpus with ledger | No accreditation claim (no ISO 17034) | Oracle corpus `5d64dca` (55 tasks, adversarial verification, rev2 ledger) | **ADAPTED** |
| 15 | Attribute agreement (α, ICC) | Panel agreement statistics where R&R needs balance it lacks | Ordinal level declared | Dogfood-era report (α=0.94); reliability() suite | **SCOPED** (agreement ≠ accuracy — P8 firewall) |
| 16 | Stationarity itself | The load-bearing assumption under rows 3–12 | Judges do not drift/die/renew mid-claim | AGAINST: mllama died mid-study; provider models version-churn | **THE OPEN FRONT** — codex-5.6's named threat; drift machinery (row 12) is the planned instrument |

## The forecast study (registered as a successor candidate, from the same conversation)

The highest-leverage unproven-tier test: a PROSPECTIVE sealed study — MSAI predicts in
advance which known injected degradations will read RESOLVED / BELOW / WITHIN-NOISE,
against a simple-baseline comparator (plain CIs + agreement stats), then truth is
revealed. Passes if MSAI makes better DECISIONS, not more elaborate reports. This is
the "sophisticated placebo" kill-test, and the project should want it run.

## Product sentence (adopted from the same source)

> "Your benchmark moved. Can your measurement system actually tell whether the model
> did?"
