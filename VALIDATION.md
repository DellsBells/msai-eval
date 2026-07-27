# Validation & Review

MSAI was checked three ways before release. This note records exactly how, so the
review process is as transparent as the tool's claims.

## 1. Validated against published reference values

The agreement statistics are tested against textbook values whose answers are
known, so the code's correctness is *measured*, not asserted:

- **ICC(2,1)** reproduces Shrout & Fleiss (1979): our `0.2898` vs published `0.290`.
- **Krippendorff's alpha** reproduces Krippendorff's canonical example: nominal
  `0.743`, interval `0.849`, ordinal `0.815`.

These are in the test suite (`tests/`) and run on every change. They are also the
arbiter used in step 3 below.

## 2. Adversarial code review (one model lineage)

A four-dimension review (statistical correctness, honesty/overclaim, robustness,
packaging) found one blocker: a docstring claimed judge-consensus references were
"refused by design," but nothing enforced it. Fixed — MSAI now *detects* the
circular case (a reference matching the judges' own consensus) and raises a
`reference_is_consensus` flag. Several robustness and labeling fixes followed.

## 3. Independent review across THREE distinct model lineages

The package was then reviewed by three genuinely different model families —
**Gemma**, **Qwen**, and **Liquid (LFM2, a distinct hybrid architecture)** — each
fed the real source and asked to attack it on statistics, honesty, and the
strongest skeptic's case. Using unrelated lineages is deliberate: agreement among
correlated reviewers is weak evidence; agreement across independent ones is strong.

**What they agreed on (strong signal — three independent architectures):**

- *Framing.* All three independently judged that publishing this as "a measurement
  standard for AI safety" overclaims. Their core points — precision is not safety;
  an LLM judge is a non-stationary instrument, not a stable gauge; there is no
  traceable true value; standards are built by community consensus, not one
  author — are now stated as explicit limitations in the README ("What this is
  NOT" and "Status"). The reviewers wrote the limitations section, in effect.
- *Scope.* All three judged the precision-vs-accuracy scoping to be honest, with a
  consistent minor note that the caveats could be more prominent for non-experts.

**Where they disagreed — and how it was resolved:**

The Liquid reviewer flagged the ICC denominator and the Krippendorff ordinal
metric as errors. The other lineages did not. **The disagreement was settled not
by majority vote, but by the published reference values in step 1**: the code
reproduces Shrout-Fleiss `0.290` and Krippendorff `0.815` exactly, so the formulas
are correct and those flags were false positives.

That resolution *is* MSAI's central thesis, applied to MSAI itself: **agreement
among judges is a signal, but correctness requires a grounded reference, not a
vote.** A panel of three reviewers, one confidently wrong, adjudicated by an
external standard — which is precisely the discipline this package exists to bring
to LLM-as-judge evaluation.

## 4. End-to-end on REAL data with a cross-source UPC reference (Phase 4)

A run of the *whole stack* on real data, not synthetic. 14 products from Open Beauty Facts, a panel of
three local vision models (qwen3.5:27b / resale-vlm-v2:12b / qwen2.5vl:7b), 2 trials each at temperature
0.7. Each model reads the brand off the real product photo; the score is the token-overlap of its brand
vs the catalog brand. Reproducible via `benchmark/phase4_validation.py`; raw output (incl. per-(item,
judge,score)) in `benchmark/phase4_result.json`. **This is the corrected re-run** — the gauge-track
review caught two framing bugs in the first pass; both are now fixed in code and the claims below are
the honest, corrected output.

**The reference, and a retraction.** Each item's `u_ref` is set by cross-source agreement (OBF ×
upcitemdb): agree → `u_ref=0.05`, disagree → `0.30`, single-source → `0.15`. **A "contested-truth win"
claimed in the first pass was a bug, not a win:** OBF `"Weleda"` vs upcitemdb's vendor-garbled
`"AmazonUs/WELED"` are the *same* brand, mis-read as a disagreement by naive token matching — so the
`reference_unfit` rejection fired on a normalization artifact, not a genuine contest (fixed:
`canon_brand`/`brands_agree`). In the corrected draw all 14 products were upcitemdb-misses
(single-source, uniform `u_ref=0.15`), so **no genuine cross-source disagreement has occurred on real
data — the contested-truth handling remains UNEXERCISED**, an honest gap, not a demonstrated win.

**The numbers (corrected run):**
- **Accuracy vs UPC truth:** qwen3.5:27b **93%**, qwen2.5vl:7b **93%**, resale-vlm-v2:12b **~57–61%** —
  reproduced across both draws; the fine-tuned `resale-vlm-v2` is materially the laggard.
- **Per-judge bias** (the verdict to read here — NOT the OUTLIER label, see below): qwen3.5 +0.11,
  qwen2.5vl +0.11, **resale-vlm-v2 −0.21** (proficiency `z̄ = −1.53`). Bias cleanly fingers the weak model.
- **Reliability / gauge:** Krippendorff α = 0.267; %GRR = 81%, ndc = 1 → `gauge_judgement = NOT
  ACCEPTABLE` — this panel cannot resolve on the [0,1] brand-overlap scale, because between-judge
  disagreement (the weak model) dominates.
- **Uncertainty budget:** repeatability 6% / **reproducibility 50%** / resolution 44%; `U = ±1.03`,
  `k = 2.36` (honest small-panel coverage). Lever: *"add judges / tighten the rubric"* — the weak model.

**The OUTLIER verdict is demoted to accuracy + bias (review fix #2).** All three judges read OUTLIER in
proficiency, but that is an artifact of scoring a near-binary brand match against a *constant* reference
target (1.0): any miss on a tight item blows `|En|>1`. `proficiency()` now self-flags this with a
`reference_constant` warning, and the honest verdict on this task is the **accuracy rate + per-judge
bias** above, not the En/OUTLIER label.

**What this run validates — and what it does NOT.**
- ✓ **Accuracy** vs independent truth; ✓ **reproducibility / agreement**; ✓ the **honesty firewalls**
  (`reference_is_consensus` flagged — conservatively, a near-false-positive where the models simply
  agree with truth; the new `reference_constant` guard; honest small-panel `k`).
- ✗ **Contested-truth handling** — no real cross-source disagreement has occurred (the one "case" was a
  bug). ✗ **The resolution / `U`-band tier, meaningfully** — `uncertainty_budget` *ran* (`U=±1.03`, NOT
  ACCEPTABLE), but a coarse near-binary task only ever yields "this gauge can't resolve"; it cannot
  validate the GUM `U`-band's ability to *resolve a real sub-point delta*. That needs a **non-frozen,
  graded** task (a subjective quality score at temp>0) — the keystone open item.

**The real, actionable resale-ai finding stands:** the fine-tuned **resale-vlm-v2:12b (~57%) is
materially worse at brand identification than the general qwen models (93%)**, and the uncertainty
budget's dominant lever (between-judge reproducibility) points straight at it.

*Scope, stated plainly:* n=14, clean catalog photos (not the production resale photos), brand-only, a near-binary
score against a constant target. This validates the **instrument's** accuracy / reproducibility /
honesty tiers end-to-end against independent truth — it is **not** a production benchmark of the models,
and it does **not** yet validate the resolution tier. *(The corrected run re-drew products, so the
compare-half below — run on the earlier draw — should be re-run on the current `phase4_result.json` for
coherence.)*

**Compare-half (gauge track) — the resolution tier could NOT be exercised on this task.** Running
`compare()` on the same real panel (the 3 models as treatments, the 14 products as the panel;
`benchmark/phase4_compare_half.py` → `phase4_compare_result.json`) returns **gauge NOT QUALIFIED —
frozen**: brand-ID is deterministic per cell (within-cell variance ≈ 0), so repeatability is unmeasured
and `compare()` correctly refuses to certify a guard-band verdict — the *same* root cause as
`gauge_judgement = INDETERMINATE`, the honesty firewall firing consistently across both halves of the
stack. All verdicts **provisional**: baseline `qwen3.5:27b` mean 0.93; `qwen2.5vl:7b` Δ = 0.000;
`resale-vlm-v2:12b` Δ = **−0.214** (95% CI [−0.429, 0.000], Holm p = 0.148) — not even statistically
resolvable after multiplicity correction in this run, and well inside the guard band (`U = 0.922`,
floored at 2·GRR, reproducibility-dominated 59%). So the **accuracy + reproducibility tiers and the
honesty firewalls are validated end-to-end on real data; the resolution / `U`-band tier is NOT** — a
frozen task structurally cannot exercise it, and at n=14 the laggard's gap is fragile (clear in the
`field_match` accuracy headline, sub-resolution and run-to-run noisy in `compare()`). Validating the
GUM `U`-band on real data is the open item, and it needs a **non-frozen** judge task: a subjective
score (listing quality / description fidelity) at temp>0 that genuinely varies run-to-run — not
brand-ID. *(Two framing corrections from the gauge-track review also belong here before this is final:
the `Weleda` vs `AmazonUs/WELED` "source disagreement" is a normalization artifact, not a real
contested-truth item — so the `reference_unfit` rejection fired on garbage input, not a genuine
contest; and two models at 100% brand accuracy reading OUTLIER is an En artifact of the constant-1.0
reference, so the accuracy rate + bias `z̄` are the verdict, not En. See `PLAN_polish.md`.)*

## 5. The keystone — the resolution / `U`-band tier on a NON-FROZEN graded task (Stage A)

Phase 4 (brand-ID) was frozen and near-binary, so the resolution tier — `compare()`'s whole reason to
exist — was never exercised. Stage A fixes that: a judge panel grades **listing quality 1–5** (anchored
rubric) at temp 0.7, ≥3 trials, over listings from two generator configs (a detailed-prompt "good" vs a
lazy-prompt "weak"), so the gauge sees real run-to-run variance and a real quality gap to resolve.
Reproducible via `benchmark/stageA_validation.py`; raw in `benchmark/stageA_result.json`. 5 products,
4 judges (qualified in preflight — two local models that couldn't track the rubric were dropped; lineage
diversity is thin, 2 gemma / 2 qwen — a stated caveat).

**Non-frozen, confirmed — the tier finally ran.** Krippendorff α = 0.393; the budget shows real
repeatability (`u=0.61`) *and* real between-judge disagreement (`u=0.97`), so `compare()` **QUALIFIED**
the gauge (not provisional, not frozen) — exactly what Phase 4 could not produce.

**The verdict on a real config gap — the thesis, on real data.** good = 3.58, weak = 2.80, **Δ = +0.78
(95% CI [0.03, 1.43], Holm p = 0.036)** → **"statistically real gain, but BELOW gauge resolution."** The
gap is genuinely there and statistically significant, yet the judge-gauge's expanded uncertainty is
**U = 2.89** (the reliability budget over the 10 listings: reproducibility-dominated 68%, k = 2.45) and
`compare()`'s guard band is **2.875** (its config-level budget) — the two views nearly coincide in
magnitude, so either way this gauge cannot resolve a sub-3-point difference. A naive eval
would have shipped "good wins, p = 0.036, significant." MSAI returns the honest middle verdict: real, but
your gauge is too noisy to certify it — *lever: more / tighter judges or a sharper rubric* (these four
local LLMs disagree by ~1.6 points). It refused to let a significant p-value become a confident finding.

**Correction — `compare()`'s guard band is inflated by product-pooling (module audit, both tracks).**
`compare()` pools every product into each `(config, judge)` cell and decomposes their between-product
spread as *repeatability*, so the guard band absorbs product variation, not just gauge noise. Severity
scales inversely with the real gauge noise: on a CLEAN gauge it is catastrophic (a real Δ = 1.0 reads
"below resolution"; reported `grr_sd` 1.33 vs a true 0.04 — ~30× inflation). **Here it is mild** — Stage A's
panel was genuinely coarse (the reliability view, which correctly separates products as items, gives
**U = 2.89** from real ~1-point judge disagreement), so compare's 2.875 only slightly exceeds true gauge
noise and the *qualitative* keystone (a significant delta sitting below a coarse panel's resolution) still
holds — it rests on the **reliability-view U, not on compare's band**. The inflation is now **fixed**
(`f9aa72b`: `compare()` computes gauge noise from the unit-level decomposition, so product spread no longer
masquerades as repeatability — the clean-gauge keystone case is locked green in
`test_compare_resolves_clean_gauge_real_delta`). **Re-validation of the corrected band — DONE** (re-running
the synthetic oracle / regime-sweep on the unit-level decomposition):
- the verdict logic still holds — `oracle_ok = 100%` across the full Δ-sweep and every misspecification regime;
- the point of the fix: the corrected band now **resolves real deltas**. The "REAL / resolved" bucket is
  reachable across the boundary (Δ=1.0 → 38% REAL, Δ=1.6 → 86%, Δ=2.4 → 98% on a realistic coarse panel),
  where the *inflated* band suppressed it to ~67% even at Δ=2.4. The resolution tier can now certify, not
  only refuse;
- the false-REAL trust limit is now correctly *sharper*: common-mode coverage drops to **5%** (was 53%) —
  the inflated band was accidentally over-covering shared bias; the corrected, gauge-noise-only band honestly
  cannot catch treatment-correlated bias, which is the documented limit (the case for independent panels).

So the band **itself** is now validated, not just the logic on it. The reliability-view U was, and remains,
the trustworthy gauge reading.

**Second band-inflation finding — the common-mode judge LEVEL (Elo-validation keystone, both tracks).** The
guard band also carried the judge **main effect** — each appraiser's overall scale *level*. Because the same
judge rates both the config and the baseline, that level is **common-mode in the within-judge delta and
cancels exactly** — the identical algebra by which `u_ref` cancels in a config-vs-baseline comparison.
Carrying it inflates the band with an error the delta never incurs: a panel that *agrees on every gap* but
rates on different absolute levels is wrongly judged coarse. The Elo-validation keystone surfaced it directly
— the panel's reproducibility (`repro_sd ≈ 0.60`) was *uniform level-shift* (judges agreed on the delta but
rated `gemma≈2.4` vs `coder≈3.5`), inflating the subtle tier's band to **2.235**. **Fixed:** `compare()` now
builds the guard band on the **delta basis** — `uncertainty_budget(..., measurand="delta")` drops the judge
main effect from reproducibility and keeps the judge×item interaction (the genuine gap-disagreement), and the
floor uses `grr_sd_delta = √(repeatability + interaction)`. Three guards, all gauge-internal: (1) valid only
on the balanced crossed design `variance_components` already requires; (2) scoped to the **delta path only** —
the default `measurand="absolute"` is unchanged, so an absolute-score budget still carries the level as real
error; (3) **disclosed** — a `delta_band_level_centered` warning reports the removed level spread and the
budget records `grr_sd_delta` / `grr_sd_full`. Locked green in
`test_compare_delta_band_drops_common_mode_judge_level` and `test_guard_band_is_expanded_U_floored`; the
frozen verdict-oracle contract is unaffected (the change moves the band *magnitude*, not the verdict
semantics — 432/432 grid combinations still match).

**§6 (resolution-tier) — PILOT-PASSED, not CLOSED.** *State machine:* OPEN → **PILOT-PASSED** → CLOSED, where
CLOSED is reserved for a reference that meets `reference.py`'s own TUR bar. "Closed, directional, pilot-scale,
against a consensus anchor that fails our own uncertainty-ratio bar" is not closed — it is pilot-passed (the
word on the certificate must carry its uncertainty; caught in cross-lineage review). The corrected re-run
demonstrates the full three-rung CONTRAST on the delta band (5-judge local panel, n=10/tier, Elo-magnitude
`resolve` + human-margin `subtle`/`tie`) — the property a plain significance test cannot reproduce:

| tier | Δ | delta band | verdict |
|---|---|---|---|
| resolve (Elo ~309) | +2.77 | 1.35 | REAL, beyond resolution |
| subtle (margin 0.68) | +0.90 | 2.17 | **statistically real, but BELOW resolution** |
| tie (margin 0.33) | −0.09 | 1.73 | within noise |

`resolve` resolves while `subtle` is refused, so "subtle below" is **not** blanket over-refusal. The verdict
survives every attack raised against it: **(a) the level-shift correction** — subtle stayed below the delta
band, and the correction barely moved it (no `delta_band_level_centered` fired) because the subtle band's
width is genuine judge×item **interaction** (real disagreement on the subtle gap), not appraiser level; **(b)
the temperature dial** (repeatability is partly an experimenter parameter) — a re-run at temp 0.3 (tighter
dial) left subtle BELOW with the band essentially unchanged (2.17→2.36), confirming the band is
interaction-dominated / temperature-independent, not dial-set; **(c) length** — the keystone is length-clean
(chosen *shorter* in 5/10).

**SCOPE (so the claim is not over-read):**
- **External CONSENSUS anchor, not a traceable reference.** Arena Elo and MT-Bench margins are aggregated
  human preference — a *construct definition*, not a VIM-traceable standard with stated uncertainty. §6 shows
  the resolution tier tracks an external **consensus** anchor; a **truth** anchor awaits execution-feedback
  grounding (open thread). Wording is deliberate: not "external truth."
- **The anchor does not meet the tier's own TUR bar.** `reference.py` requires a 4:1 uncertainty ratio;
  MT-Bench margin at n=10 is a noisy reference, almost certainly not 4× sharper than the gauge it validates.
  The closure is therefore **directional / pilot-scale** (n=10/tier, ~46 Arena-anchored pairs), not a
  metrological certification. Scope the claim to the anchor's uncertainty.
- **Ecological-inference in the reference itself (un-budgeted).** Arena Elo gaps are MODEL-level population
  statistics applied as PAIR-level known-deltas. A +309-Elo model does not beat the weaker one by a fixed
  margin on every item — it wins big on some, less on others — so each pair's true gap carries item-level
  variance *around* the model-Elo anchor that is **not** in `u_ref`. That is a between-unit component leaking
  into the reference *value* — the very `unit`-mislabeling the gauge fix prevents, one level up in the chain.
  At n=10/tier it is plausibly a real fraction of the band. A standing reason this is PILOT-PASSED, not CLOSED.
- **Operating window.** `subtle` ndc=1 — the local panel is genuinely coarse on subtle pairs (judges
  disagree), which is *why* a real 0.90 gap reads below resolution. The window: this 5-judge local panel
  resolves clear gaps, not subtle ones. Change panel / rubric / temperature-regime → re-check.

*(Runs: `keystone_result.json` at temp 0.6 and 0.3; ledger `test_elo_harness_claims.py` 20/20 green;
gauge correction `compare.py` commit 120e55a, verified cross-lineage.)*

**Paraphrase / rubric-robustness — disclosed budget line.** The guard band above is a repeatability +
reproducibility band; it does **not** yet include the **paraphrase×condition** term — the sensitivity of the
chosen-vs-rejected delta to semantically-equivalent restatements of the rubric. Metrologically this is
*definitional / method-robustness uncertainty, not repeatability* (the prompt IS the procedure, so rewording
is a different method realization) — a missing budget component, and omitting a known component is the
canonical false-acceptance mechanism (understated U → band too narrow). A K=3 pilot (`paraphrase_probe.py`,
temp 0, 5-judge panel) measured it: **σ(paraphrase×condition) = 0.19 (resolve) / 0.37 (subtle)** on the 1–5
scale — non-trivial but **sub-dominant** (~30% of grr_sd_delta), and larger on subtle pairs (a rewording flips
a close call more easily than a clear one). The paraphrase *main* effect (a wording that shifts all scores)
cancels in the delta, exactly like the judge level-shift. Two **declared scopes** (the honest packaging):
- **frozen-fixture** (the current band): valid only for this exact, hash-versioned rubric string.
- **rubric-robust** (band ⊕ paraphrase term in quadrature): resolve ~1.35→~1.40, subtle ~2.17→~2.30.

**Both §6 verdicts hold under BOTH scopes** — resolve resolves (Δ2.77 ≫ 1.40), subtle stays below (Δ0.90 <
2.30) — so no §6 verdict is paraphrase-fragile. (Caveat: K=3 is thin, dof=2; the conclusion is robust to that
noise. Gauge-level integration — folding σ²_paraphrase into `grr_sd_delta` inside `compare()` — is a
compare-track follow-up; disclosed here at the validation layer.)

**What this validates — and what it does NOT.**
- ✓ The **resolution / `U`-band tier runs honestly end-to-end on real, non-frozen data** and emits the
  correct three-way verdict (real-and-resolved / **real-but-sub-resolution** / within-noise). This is the
  tier every earlier round could not reach.
- ⟳ In **Stage A** it did **not** demonstrate the `U`-band *clearing* the guard band (resolving a delta) — the
  local-LLM panel was too coarse there (U ≈ 2.9 on a 1–5 scale). *Since demonstrated in §6's keystone run:* a
  near-maximal Elo-magnitude `resolve` tier clears the band (Δ 2.77 > 1.35). The budget pointed the lever
  (larger config gap), exactly as predicted.
- *Scope:* n = 5, thin lineage diversity, preflight-qualified judges, and **Stage B (human-gold
  reference → accuracy + proficiency-vs-truth + the fitness gate) is not yet run.** The headline finding —
  that a statistically-significant quality delta can sit below a noisy panel's resolution — is the point.

## 6. Synthetic gauge-block calibration — the instrument against a known answer

Phases 4–5 ran MSAI on real data where the *true* answer is unknown, so they could show the instrument runs
and refuses honestly, but never that its readings are *correct* — there was no known value to check against.
This phase supplies one: a synthetic gauge-block injects a **known** variance decomposition (item / judge /
repeatability sigmas), **known** per-judge bias, and **known** config deltas, then checks whether MSAI
recovers them. Built across two lineages with the checker independent of the generator — *neither lane wrote
the other's half*, which is what makes a calibration a calibration and not a tautology. Reproducible via
`benchmark/synth_gauge.py` (generator), `recover_check.py` (checker), `n_sweep.py`, `regime_sweep.py`.

Matched-Gaussian recovery is, by design, only a **smoke test** — recovering the split from clean data is an
algebraic identity (at the clean limit repeatability and delta recover *exactly*, reproducibility is unbiased
over seeds). The value is in the two things real data cannot give: the finite-sample precision of the
readings, and the behaviour when the estimator's assumptions are **violated**.

**What it found:**

- ✓ **The three-way verdict logic is correct**, not asserted: `oracle_ok = 100%` across every regime and the
  full delta sweep (Δ = 0 → 2.4). compare()'s bucket assignment (within-noise / real-but-below-resolution /
  real-and-resolved) matches an independently frozen oracle everywhere; the middle bucket is populated (not a
  degenerate two-way switch); the Cliff's-δ **WITHHOLD fires on 100%** of mean-vs-rank sign-conflict cases.
- ⚠ **%GRR is intrinsically imprecise at any realistic scale.** Its 90% sampling band is **~±15pp** (13–18pp)
  and it *persists* — barely tightening from 14→45 items or 5→12 judges, and unchanged across heavy-tail,
  shared-bias, and heteroscedastic regimes. So a reported "%GRR = 28%" could truthfully be anywhere ~13–43%,
  **spanning two AIAG acceptance categories**, and more data does not rescue it (it is the coarseness of a
  nonlinear ratio of variance estimates, not a small-panel artifact). `variance.gauge_judgement` now discloses
  this on every verdict (`pct_grr_caveat`, `category_ambiguous`) and points to the guard band + per-config
  verdicts as the trustworthy reading.
- ⚠ **The false-REAL trust limit, measured.** When judges share a bias *correlated with the treatment*
  (injected at Δtrue = 0, so the entire "signal" is bias), a naive significance test is fooled **every time**
  (bootstrap-CI coverage of the null → 0%). MSAI's guard band cuts that to **~47%** — it covers the true null
  53% of the time, *catching roughly half the false-positives a naive eval would ship*. That is the
  distinctive claim demonstrated on a known-answer case — and its boundary: the other half pass, because
  treatment-correlated common-mode bias is, by construction, indistinguishable from a real effect in the data.
  `oracle_ok` stays 100% throughout: the verdict *logic* is correct; the *inputs* are corrupted by bias the
  instrument cannot see. This is "consensus ≠ truth" at the variance level, and the empirical reason a judge
  panel **must** be independent-lineage — a correlated judge does not merely weaken the gauge, it defeats the
  guard band half the time.
- ✓ **Robust to heavy tails:** t3-distributed repeatability leaves guard-band coverage at clean levels
  (Algorithm A winsorization defends it).
- ⚠ **The proficiency OUTLIER flag is En-saturated at the LLM-judge regime — read per-judge bias (z̄), not the
  OUTLIER label.** On a realistic panel (reproducibility SD ≈ 0.4, 3 trials) the OUTLIER label fires on ~100%
  of judges *regardless of injected bias, including zero bias*. It is driven by the En test, whose yardstick —
  a judge's sparse replicate uncertainty — is tiny next to the real between-judge spread, so `|En|>1` fires on
  ordinary disagreement, not incompetence. The z-score meanwhile stays in range (the 5%-of-scale z-floor
  works — but it guards z, **not** En). The reliable detector is the per-judge bias **z̄**: it separates the
  biased judge cleanly by bias ≈ 1.5 (z̄-detection climbs ~30% → ~95% as bias goes 0.5 → 2.0; ~40%
  false-positive at a bare `|z̄|≥2` cut, so read the across-judge *separation*, not the threshold). This
  confirms and generalizes the Phase-4 OUTLIER→bias demotion (§4) from the constant-reference case to the
  everyday consensus case; `proficiency()` now discloses it on the panel itself (`outlier_en_saturated`
  warning — verified to fire on saturated panels and redirect to z̄, silent when a genuine z-outlier dominates).

**What it does NOT validate — the ceiling, stated so a green result is never misread.** This calibrates the
*math and the decision logic*: it shows MSAI **recovers** a known variance split, returns the **correct
three-way verdict** as Δtrue crosses the guard band, and **characterizes its own** estimator bias and
coverage — all *under the model's own assumptions*. It does **NOT** validate that the resolution VERDICT is
correct on real LLM judges. The gap is not merely "we don't know the true delta on real data" — it is a
**measurand-substitution gap**: `compare()` resolves a delta on the JUDGES' perceptual score scale (the
reference uncertainty is common-mode and cancels by design), whereas any real-world truth lives on a
different, coarser, possibly non-interval scale — so a *correct* verdict on the score-delta can legitimately
diverge from the real-world delta for a scale reason the instrument cannot see. And "the assumptions hold on
live data" is only ever checkable as self-consistency, which at n ≤ 14 has almost no power to reject. **So a
green synthetic block must never be read as "the resolution tier is validated on real judges."** It validates
the instrument's *internals*; whether it measures something real on live judges stays **INFERRED** until a
real task with a *known* delta supplies predict-then-measure evidence — the lever test did this for the
statistical tier (passed); the planned known-degradation run is the open piece for the resolution tier. The
±15pp %GRR band is likewise calibrated on one variance split and honest as "~±15pp," not a universal constant.

**And the guard band itself is not yet validated.** The module audit found `compare()` inflates the guard
band by pooling units into treatment-cells (the between-product spread is mislabeled repeatability — see the
§5 correction). The `oracle_ok = 100%` above was run on `compare_rows` (item = config), i.e. it validated the
verdict **LOGIC** *given* a guard band — on the inflated band — and did **not** validate the band's
correctness. The fix has **landed** (`f9aa72b`: gauge noise from the unit-level decomposition; the keystone
clean-gauge case is locked green). What remains open is the **re-run of the synthetic oracle on the
corrected band** — that is what will finally validate the band itself, not just the logic on it.

## 7. Frontier reproduction — the four-state resolution verdict on a 5-lineage API panel (the §6 close-out)

§5–§6 established the keystone contrast on a **coarse local panel** (5 Ollama judges) and asked the
load-bearing question directly: is the distinctive "real-but-below-resolution" verdict a genuine property of
measuring subtle quality gaps, or an artifact of a weak gauge? This close-out reproduces the keystone on
**genuine frontier judges** and sharpens the resolution metric.

**Three-panel arc, lawful scaling.** The same `keystone_ladder(n=10, seed=0)` fixture (identical 60 responses;
resolve = RewardBench Elo-gap ~309, subtle = MT-Bench margin 0.68, tie = margin 0.33) was run on three panels of
increasing quality: local coarse (5 Ollama judges, §6 above) → chat frontier J=3 (claude / codex / gemini, free
chat-window blind batching, R=2) → **API frontier J=5** (gpt-5.5, grok-4.3, gemini-3.1-pro-preview, opus-4-8,
deepseek-v4-pro; R=3; 900 blind ratings; ~$2.23 — the authoritative run, most diverse and best powered).
Resolution moves **lawfully** with gauge precision (a micrometer resolves what a caliper can't). Reproducible via
`benchmark/frontier_api_run.py` → `frontier_api_scores.json`; zero-spend re-analysis via `frontier_reanalyze.py`.

**Four-state resolution verdict (the metric, sharpened).** Binary `beyond_gauge` compares |Δ| to the guard band
U as if U were exact. But at small panels U is itself a noisy estimate — its Welch-Satterthwaite effective dof is
finite — so U carries its own confidence interval, and a significant Δ landing **inside** [U_lo, U_hi] cannot be
forced to a side: that is **AT-EDGE**. `resolution_verdict.py` implements WITHIN-NOISE / BELOW / AT-EDGE /
RESOLVED, plus P(|Δ|>U) as a continuous disclosure. dof contract: **WS νeff** (GUM combined dof; dominant-component
dof shown as a conservative disclosure), with a standing **provisional-J<5** flag (U is unstable below ~5 judges,
the harness's own warning). *(Lives in `resolution_verdict.py` pending fold-in into `compare()`.)*

| tier | Δ | U (WS) | U 95% CI | P(\|Δ\|>U) | verdict [WS] | verdict [dom-dof] |
|---|---|---|---|---|---|---|
| resolve (Elo ~309) | +2.25 | 1.40 | [1.07, 2.02] | 0.99 | **RESOLVED** | AT-EDGE |
| subtle (margin 0.68) | +1.37 | 1.48 | [1.10, 2.26] | 0.30 | **AT-EDGE** | AT-EDGE |
| tie (margin 0.33) | −0.60 | 1.33 | [0.99, 1.99] | 0.00 | **BELOW** | BELOW |

*(The **dom-dof** column is the conservative reading — U's CI taken from the dominant between-judge
component's dof rather than the Welch-Satterthwaite combined νeff. Only the *resolve* tier is dof-sensitive
(RESOLVED under WS νeff, AT-EDGE under the conservative dominant-dof); subtle and tie are robust to the choice.
The certificate prints this resolve-AT-EDGE-under-dominant-dof caveat inline.)*

The keystone 3-tier pattern reproduces on five frontier lineages — large gap RESOLVES, subtle gap sits AT the
gauge's resolution edge, sham gap is BELOW. The distinctive verdict is therefore **not** a coarse-gauge artifact:
even five frontier flagships have a noise floor a subtle gap slips under.

**subtle is AT-EDGE, robustly.** Both dof interpretations agree (WS and dominant-dof), at J=5 (the recommended
minimum). The J=4 pre-DeepSeek run and the J=3 chat run disagreed on subtle (the homogeneous chat panel agreed
tightly → resolved; the more diverse API panel disagreed → at-edge); the fifth lineage settled it. DeepSeek in
particular rated the subtle *chosen* answers **lower** than Claude (subtle/pair-9: DeepSeek 1 vs Claude 4) — not
noise but the mechanism: **panel diversity widens the reproducibility band**, so the same real gap a homogeneous
panel "resolves," a diverse panel places at-edge. The diverse reading is the honest gauge; a lucky-tight
homogeneous panel is the shared-bias trap this package guards against. The noise floor is **between-lineage
disagreement** (~56% reproducibility), not within-judge flakiness (each judge's re-score SD 0.06–0.31) — the
frontier judges are individually steady; the "slip" is cross-lineage.

**Definitional-uncertainty — stated as a HYPOTHESIS, with its discriminating experiment named.** subtle sits at
the human-preference margin (~0.68) where the tier was *built* — the construct's own ambiguity zone. The
hypothesis: near-tie quality gaps are below the **construct's** resolution, not merely the instrument's — no panel
however sharp resolves a difference humans themselves don't agree on (VIM's *definitional uncertainty*), which
would make "band-edge subtle is structural" a feature and AT-EDGE the *correct* report. **But it is a hypothesis,
not a finding:** AT-EDGE on a diverse panel is *also* consistent with shared-lineage bias, and the two are
indistinguishable **without a judge-independent reference**. That discriminating experiment — an external anchor
(execution-feedback / market-outcome transfer standard, budgeted through `reference.py`) — is the named successor
and the PILOT→CLOSED path. Until it runs, this is precision, not accuracy.

**PILOT-PASSED, not CLOSED — unchanged.** The frontier reproduction strengthens the resolution demonstration but
adds no traceable reference: still consensus-anchored (Arena Elo / MT-Bench margins), still n=10/tier, still no
external ground truth, and the anchor still fails `reference.py`'s TUR bar. The first conformant **gauge
certificate** (`benchmark/CERTIFICATE_MSAI-8C06733F42F0.md`, sha256-bound to the J=5 scores) renders exactly this,
with NO ACCURACY CLAIMED printed where a decision-maker cannot miss it. *(Full run + deviations:
`benchmark/frontier_run_log.md`. The caveat travels with the claim.)*

## Standing limitations

The reviewers' criticisms in step 3 are correct and are not "resolved" — they are
boundaries, stated plainly in the README. MSAI measures whether your eval is
reproducible and (against a reference you can defend) accurate. It does not certify
safety, does not make an unstable judge stable, and cannot supply a true value you
do not have. It is an early, honest attempt to bring measurement-system discipline
to AI evaluation — offered to be stress-tested and sharpened, not treated as a
finished standard.
