# GAUGE CERTIFICATE — LLM-AS-JUDGE MEASUREMENT SYSTEM

**Certificate no.** `MSAI-8C06733F42F0` &nbsp;·&nbsp; **Issued** 2026-07-06 &nbsp;·&nbsp; **Data of** 2026-07-02 &nbsp;·&nbsp; **Basis** 900 blind ratings (0 null-score rows excluded, disclosed) (sha256-bound to `frontier_api_scores.json`) &nbsp;·&nbsp; **Format** `MSAI-GC/1.0-draft` (docs/CERTIFICATE_SPEC.md)

> **NO ACCURACY CLAIMED.** This certificate states what the measurement system can
> **resolve** — its precision, reproducibility, and resolution under the stated conditions.
> **It does not state that the system's judgments are correct.** No traceable reference was
> supplied; accuracy without a traceable reference is undefined. High panel agreement is
> equally consistent with a correct rubric, a shared wrong rubric, or successful gaming —
> shared-bias detection is outside this gauge's scope, by construction.

## 1. Measurement system under qualification

| | |
|---|---|
| Instrument | Panel of 5 LLM judges, distinct provider lineages (see Disclosures: training-data independence is NOT established) |
| &nbsp;&nbsp;— openai | `gpt-5.5` |
| &nbsp;&nbsp;— xai | `grok-4.3` |
| &nbsp;&nbsp;— gemini | `models/gemini-3.1-pro-preview` |
| &nbsp;&nbsp;— claude | `claude-opus-4-8` |
| &nbsp;&nbsp;— deepseek | `deepseek-v4-pro` |
| Procedure | Blind, self-contained 1–5 quality rating; one response per call; opaque IDs; no pairwise exposure |
| Replication | R=3 independent re-scorings per response; temperature >0 (per-provider details: `frontier_run_log.md`) |
| Measurand | Δ = mean(config) − mean(baseline), balanced crossed design, per-pair `unit`; judge level main-effect cancels (delta basis) |
| Design | 10 pairs/tier × 2 configs × 5 judges × R=3 |

## 2. Reference conditions (consensus anchors — NOT traceable references)

- **resolve** — RewardBench pairs, Arena-Elo gap-anchored (mean gap ~309 Elo)
- **subtle** — MT-Bench pairs, human preference margin ~0.68 (the keystone tier)
- **tie** — MT-Bench pairs, human preference margin ~0.33 (negative control)

## 3. Results — resolution verdicts per tier

State machine: WITHIN-NOISE / BELOW / AT-EDGE / RESOLVED. The band U carries its own
confidence interval (fiducial, from its effective dof); a significant Δ inside [U_lo, U_hi]
reads AT-EDGE — the gauge refuses to force a side it cannot support. Contract dof: WS νeff
(GUM); dominant-dof shown as conservative disclosure.

**Two-band structure (REV-001):** the verdict gate — the band `U` in the table below — is the
gauge DISCRIMINATION band (Band B): a per-use expanded uncertainty (AIAG ndc family / JCGM 106
§8.3.3.2 w=rU form) that does NOT shrink with study size. The uncertainty of the ESTIMATED mean
difference (Band A, k·u(Δ̂), VIM §2.47) is a separate quantity that DOES shrink with N — the ± on
Δ, carried by the CI, never the gate. 'Statistically real but BELOW resolution' is the coherent
state where Band A excludes 0 yet |Δ| < Band B (a caliper can establish a 0.02 mm mean difference
from 1000 readings and still be unable to discriminate those two parts in the hand). An earlier
draft mislabeled Band B as the GUM U of the estimate and speculated BELOW/AT-EDGE might promote
under correction — wrong on both counts, corrected 2026-07-02 (commit A). Both bands now ride each
comparison as typed fields (`bands`, `resolution_verdict`); this table shows Band B, the gate.

**Coverage basis (spec §4):** every U on this certificate is expanded at ~95 % coverage,
k = t(ν_eff) with ν_eff per Welch–Satterthwaite, JCGM 100:2008 §G.4.1 Eq. (G.2b);
per-tier k and ν_eff are printed below.

**Decision rule as used (spec §6.7; ILAC-G8 §4.2.3 / ISO 17025 §7.1.3):** four-state per
spec §5; AT-EDGE zone = U's 95 % fiducial CI from ν_eff; state dof = WS ν_eff; analysis
knobs guard_k=2.0 (library default), resolution=1.0, level=ordinal. **Timing attested:**
a 20 %-of-band edge rule was pre-registered before scoring; the CI-based edge zone,
ratified after scores existed, superseded it. The three §3 verdicts are identical under
either rule on this data. Post-hoc rule evolution is disclosed, not hidden; no knob was
tuned against a verdict outcome (see frontier_run_log.md).

| tier | Δ | Cliff's δ | U (k·u_c) | U 95% CI | νeff | P(\|Δ\|>U) | **verdict [WS]** | verdict [dom] |
|---|---|---|---|---|---|---|---|---|
| resolve | +2.25 | +0.85 | 1.40 | [1.07, 2.02] | 20.1 | 0.99 | **RESOLVED** | AT-EDGE |
| subtle | +1.37 | +0.53 | 1.48 | [1.10, 2.26] | 16.0 | 0.30 | **AT-EDGE** | AT-EDGE |
| tie | -0.60 | -0.24 | 1.33 | [0.99, 1.99] | 16.9 | 0.00 | **BELOW** | BELOW |

- **resolve → RESOLVED** — real gap; magnitude certified above the gauge's resolution.
  - *Caveat (travels with the claim): under the conservative dominant-dof rule this verdict reads **AT-EDGE**. Quote both or quote neither.*
- **subtle → AT-EDGE** — real gap at the gauge's resolution edge; no side can be forced.
- **tie → BELOW** — statistically real, but below resolution — magnitude NOT certified.

## 4. Uncertainty budget (per tier)

| component (u, 1σ) | resolve | subtle | tie |
|---|---|---|---|
| repeatability (re-scoring) | 0.408 (dof 200) | 0.400 (dof 200) | 0.342 (dof 200) |
| reproducibility (between-judge) | 0.445 (dof 4) | 0.492 (dof 4) | 0.434 (dof 4) |
| resolution (quantization) | 0.289 (dof inf) | 0.289 (dof inf) | 0.289 (dof inf) |

- **resolve**: u_c=0.670, k=2.09, U=1.40; dominant lever: reproducibility (between-judge) (44.2% of u_c²); grr_sd (delta basis)=0.604 vs (full)=0.634
- **subtle**: u_c=0.697, k=2.13, U=1.48; dominant lever: reproducibility (between-judge) (49.8% of u_c²); grr_sd (delta basis)=0.634 vs (full)=0.648
- **tie**: u_c=0.623, k=2.13, U=1.33; dominant lever: reproducibility (between-judge) (48.5% of u_c²); grr_sd (delta basis)=0.552 vs (full)=0.565

## 5. Disclosures and limitations (verbatim from the gauge, plus standing caveats)

- `[resolve]` ndc=3 (<5, the AIAG adequate-gauge bar) — ADVISORY ONLY, NOT a gate. ndc is selection-sensitive: it scales with how far apart the hand-picked configs happen to be, so it under-reports when configs cluster into a few quality tiers even on a sharp gauge. The gauge's real resolution is the guard band — lean on it and the per-config verdicts, never ndc, as the accept/reject grade.
- `[subtle]` ndc=3 (<5, the AIAG adequate-gauge bar) — ADVISORY ONLY, NOT a gate. ndc is selection-sensitive: it scales with how far apart the hand-picked configs happen to be, so it under-reports when configs cluster into a few quality tiers even on a sharp gauge. The gauge's real resolution is the guard band — lean on it and the per-config verdicts, never ndc, as the accept/reject grade.
- `[tie]` ndc=3 (<5, the AIAG adequate-gauge bar) — ADVISORY ONLY, NOT a gate. ndc is selection-sensitive: it scales with how far apart the hand-picked configs happen to be, so it under-reports when configs cluster into a few quality tiers even on a sharp gauge. The gauge's real resolution is the guard band — lean on it and the per-config verdicts, never ndc, as the accept/reject grade.
- Pilot scale: n=10/tier; results are directional at this n.
- Ordinal 1–5 scores treated as interval for variance decomposition (disclosed approximation).
- Cross-anchor: resolve is Elo-gap-anchored; subtle/tie are human-margin-anchored.
- Anchors are human consensus — agreement, not ground truth.
- NULL PATH (KB #018 exhibit): 0 rating rows carried null scores and were
  EXCLUDED from analysis — disclosed here. Exclusion is never coercion: a null is
  not a low score and not a failure; it is an absence, and absences are counted.
- Scope: frozen-fixture (single rubric wording). A rubric-robust scope adds a measured
  paraphrase×condition term to the budget. NOTE (REV-015): the available paraphrase
  estimate (~30% of gauge noise) was measured on a DIFFERENT instrument (local pilot
  panel, temperature 0), not this frontier panel — it is indicative, not this gauge's value.
- EVIDENTIAL BASIS UNDER REVIEW (cross-organ audit 2026-07-02, REV-005): raw judge
  completions were NOT persisted for this run — the hash binds parser outputs, not the
  judges' text, and the run used a parser variant that differs from the project's
  ledger-validated parser. Scores cannot be re-audited from evidence without a re-run
  that persists raw completions and parses via the validated path. Until then, treat
  the verdict magnitudes as provisional.
- SHARED-EXPOSURE CAVEAT (REV-005): judged responses derive from public 2023-era
  benchmarks; all panel judges plausibly trained on these items and on published
  judge scorings of them. Shared exposure would deflate the between-judge term (this
  certificate's dominant lever) and tighten U. "Distinct provider lineages" does NOT
  establish training-data independence.
- BAND CONSTRUCTION UNDER REVIEW (REV-001): the printed U is under review as over-wide
  for the delta measurand (conservative). A corrected band can only tighten: RESOLVED
  verdicts are safe a fortiori; BELOW/AT-EDGE verdicts may promote on re-analysis.
- AT-EDGE on near-tie gaps is consistent with definitional uncertainty of the preference
  construct itself (panel diversity widens, not tightens, the band there); distinguishing
  construct ambiguity from shared-lineage bias requires a judge-independent reference.

## 6. Qualification statement

The panel QUALIFIES as a comparison gauge on 3/3 tiers under the stated conditions (balanced crossed design, genuine replication, finite guard
band). It resolves large quality gaps (resolve tier), correctly refuses magnitude claims on
gaps at or below its resolution, and reports its own resolution edge. **This certificate is
void for any use of the panel outside the stated conditions** (different rubric wording,
unbalanced designs, absolute-score thresholds, or accuracy claims).

*Run metadata: 276057 in / 19750 out tokens, 0 API failures, $2.23 total measurement cost.*

*Renderer: msai-eval v0.8.0 · benchmark/certificate.py · results-digest `sha256:75F35C04795A` (binds this document's §3/§4 tables; the certificate no. binds
only the raw scores — same scores under changed gauge logic yield the same certificate no.
but a different results-digest).*

*Generated from persisted scores; verify by re-running:*
`.venv/bin/python benchmark/certificate.py --data-date 2026-07-02`
