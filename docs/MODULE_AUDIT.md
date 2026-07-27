# Module overclaim audit — findings + resolution ledger

Each module was probed by injecting **known truth** (via `benchmark/synth_gauge.py`) and checking whether
every verdict / flag / headline number *tracks* that truth or *fails/saturates regardless of it* — the same
pattern as the proficiency OUTLIER En-saturation. Every candidate was then **adversarially verified**
(real? already disclosed? severity), which killed 5 false candidates. Resolution is tracked in
`tests/test_claim_tracking.py` (green = locked, strict-xfail = open). Disclose-the-limit for claims that
can't track truth at small n; fix-the-computation for claims that can but don't.

Lanes: **modules/KB** owns variance / reference / stability / u_ref-collapse; **gauge track** owns compare /
uncertainty / the §5–§6 band disclosure. Per the agreement, the gauge track adversarially verifies each
finding below before any shared edit.

## variance.py
| # | finding (one-line) | sev | disclosed | status |
|---|---|---|---|---|
| V1 | frozen gauge on a **continuous** grid reads `deterministic=False` / FULLY ACCEPTABLE / ndc 7e7–2e9; root: `score_step` collapses to 1e-9 (lines 83-90) so the threshold drops below the float floor. Integer grid correctly reads INDETERMINATE-frozen. | HIGH | no | OPEN (`test_frozen_continuous_gauge_detected`) |
| V2 | `repeatability_unmeasured` — downstream of V1, a truly frozen panel emits the reassuring "this does NOT disqualify the gauge". | HIGH | no | OPEN (same root as V1) |
| V3 | `ndc` had no sampling-band caveat (swings ~1–13 on identical truth) where %GRR does. | MED | no | **RESOLVED** `fa0d1eb` |
| V4 | `%GRR>30` reason asserted "gauge noise too large" as sole cause; clustered items inflate %GRR too. | MED | no | **RESOLVED** `fa0d1eb` |
| — | `negative_variance_truncated` over-fires (17/40 clean) but self-labels DIAGNOSTIC. | LOW | yes | minor |

## compare.py — gauge-track lane (fix in design)
| # | finding | sev | disclosed | status |
|---|---|---|---|---|
| C1 | guard band inflated by **item-pooling**: products pooled into a (config,judge) cell have their spread decomposed as repeatability → grr_sd ≫ true gauge noise. Clean gauge (sd 0.044) + Δ=1.0 → band 2.66, beyond_gauge=False. | HIGH | §5/§6 `0865075` | OPEN — fix in design |
| C2 | "REAL and resolved" unreachable for sub-~1.5pt deltas even on a clean gauge (Δ=1.0 → 0/100). | HIGH | §5/§6 | OPEN (same root) |
| C3 | a temp-0 frozen gauge **qualifies** with a multi-item suite (opposite of correct). | HIGH | §5/§6 | OPEN (same root) |
| C4 | budget reports "repeatability" dominant (item spread mislabeled) + a lever that can't fix item heterogeneity. | MED | no | OPEN (same root) |
| — | killed by verify: Cliff WITHHOLD (disclosed), ndc-advisory (disclosed), config-common-mode-resolvable (correct behavior). | | | |

## uncertainty.py — gauge-track taking the disclosures
| # | finding | sev | disclosed | status |
|---|---|---|---|---|
| U1 | `U` swings ~14× on identical truth at items=6/judges=2 (1-dof reproducibility → nu_eff~1.8 → k=12.71), printed as a hard resolvability number with no band. | HIGH | no | OPEN — gauge track |
| U2 | dominant-lever flips to the **wrong source** ~19% at 2 judges / 6.3% at 3, no warning below ~5 judges. | HIGH | no | OPEN — gauge track |
| U3 | `u_ref` collapsed to a plain mean masks heterogeneous reference uncertainty ({six 0.01, two 5.0} → 1.26). | MED | no | OPEN — **modules** (reference seam) |
| — | killed: Welch-`k` (conservative, safe), resolution auto-inference (works + disclosed). | | | |

## reference.py — modules/KB lane
| # | finding | sev | disclosed | status |
|---|---|---|---|---|
| R1 | `too_loose` gate is blind to single-item / identical-truth refs (signal = std of ref values) → a hopelessly loose ref + a +199-biased judge returns "TRACEABLY CONFORMANT", empty warnings. | HIGH | no | OPEN |
| R2 | same gate fires INDISTINGUISHABLE on a **tight, adequate** ref + perfect judge when item truths cluster (conflates truth-homogeneity with resolving power). | MED | no | OPEN |
| R3 | "MOSTLY CONFORMANT" (conf≥0.8, count-only, no magnitude) on 4/5 perfect + 1 catastrophic miss (delta=100, En=500). | MED | no | OPEN |
| R4 | `flag_if_consensus` false-positives on independent-but-close refs (within tol=0.5 on ≥90%) and is blind below total≥3; thresholds undisclosed. | MED | no | OPEN |
| R5 | `combine_references` inverse-variance shrink (two 0.1 → 0.0707) makes shared-bias sources look more certain; docstring mentions only Birge inflation. | LOW | no | OPEN |
| — | killed: fitness FIT-exact (disclosed by its own reason + builder warning). | | | |

## stability.py — modules/KB lane (barely exercised → handle with care)
| # | finding | sev | disclosed | status |
|---|---|---|---|---|
| S1 | DRIFT gate false-fires ~10.8% on a stable gauge AND catches real drift only ~32–44% (1.0–1.25σ); the one caveat (`short_baseline`) aims at the wrong regime. | HIGH | no | OPEN |
| S2 | `first_drift_run` names a costly "re-adjudicate everything since run X" anchor on ~11% of zero-drift panels. | MED | no | OPEN |
| S3 | `short_baseline` warning covers n=3–6 (0/300 false alarms) while the real ~9–11% regime (n≥12) is unwarned. | MED | no | OPEN |
| — | killed: EWMA-as-top-source (**refuted** — raw 3σ is larger), min_shift (frozen-baseline, already disclosed), WE-8-rule (intended limit), degenerate-baseline (disclosed). | | | |

## Tally
Confirmed real + undisclosed: **variance 2 + compare 4 + uncertainty 3 + reference 5 + stability 3 = 17**
(8 HIGH). Resolved+locked: 2 (V3, V4). False candidates killed by the verify pass: 5. Each open finding
resolves by: add/keep its xfail test → fix or disclose → remove the marker → green.
