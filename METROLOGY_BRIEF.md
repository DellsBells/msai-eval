# Metrology Brief — where MSAI goes next

*Synthesis of a 14-agent metrology deep-dive (six pillars, each adversarially
verified against the actual source) + the Michelli Weighing & Measurement podcast +
the **ChatNAPT corpus** (30 episodes / ~27 hrs / 387 sourced claims, in
a private podcast-grounding corpus) + the `compare()` build shipped today.*

## TL;DR

- MSAI is, on the evidence of its own source, a **genuinely honest precision-and-
  conformance instrument** — the load-bearing claim (*accuracy without a traceable
  reference is undefined*) is enforced across the accuracy, proficiency, and conformity
  tiers (cross-lineage review found and closed the two places it wasn't), and the field's
  hardest honesty stances are live guards, not slogans.
- The six metrology pillars all map to AI evaluation **literally, not by analogy** —
  every one survived an adversarial skeptic and is buildable on the existing
  `Dataset`/`cells`/`flags` plumbing.
- The **single highest-leverage build** given the eBay/resale-ai context is
  **execution-feedback grounding**: wire a live oracle (test suite, compiler, or a
  *marketplace outcome*) as the reference. It's the only thing that converts MSAI's
  accuracy math from a promise into a defensible correctness claim.
- `compare()` (shipped today) is the **first piece of the conformity/decision-rules
  pillar.** The podcast confirms the strategic frame — the buyer can't verify the
  measurement, so what they ultimately buy is your defensible process — but
  **"accreditation, not a tool" is the *earned destination*, not the launch posture:**
  ship the honest tool, earn replications, *then* claim it.

## 1. What we've honed (verified against the code)

The reproducibility tier (Krippendorff α, ICC(2,1), weighted κ, crossed-ANOVA Gage
R&R) plus a scoped accuracy tier, with the honesty stances encoded as live guards:
frozen-gauge (temp-0) detection, consensus-is-not-correctness, negative-variance-as-
diagnostic, selection-sensitive-%GRR labeling, and no-true-value scope discipline.
The deep-dive's verdict: the discipline is real. The honest limitation it confirmed is
that **every shipped number is a single time-agnostic snapshot, against a zero-
uncertainty reference, with a symmetric accuracy figure** — which is exactly what the
three new directions fix.

## 2. The field maps literally — six pillars (all HIGH, all held up)

| Metrology pillar | AI-eval mapping | Status |
|---|---|---|
| **Attribute Agreement MSA** (AIAG MSA-4, κ) | categorical judge agreement + the asymmetric miss/false-alarm ledger | deepen `accuracy` |
| **GUM uncertainty budgets** (JCGM 100/101) | a stated `± U` on the headline number, with the dominant source named | new `uncertainty.py` |
| **Traceability / reference values** (ISO 13528, Guide 35) | a constructed consensus reference *with* assigned-value uncertainty | new `reference.py` |
| **Proficiency testing** (ISO 13528 / 17043) | calibrating a judge's *stated* confidence via En/ζ vs a peer panel | new `proficiency.py` |
| **SPC / stability** (Shewhart, EWMA) | judge **drift** over time → a defensible recalibration trigger | new `stability.py` |
| **ISO 17025 validation + decision rules** | **guard-banded conformity** under uncertainty | `compare()` ✅ + new `conformity.py` |

## 2a. Grounded in the field — the multi-show metrology corpus (1,435 claims, 2 shows)

*The mappings are no longer ours alone, and no longer one source. Every MSAI module now traces to
named practitioners in the private KB index — **1,435 canonical
claims distilled from 208 episodes across TWO independent shows** (ChatNAPT / NAPT, 30 eps; Quality
Cast / Quality Magazine, 178 eps), each annotated with the module it informs and, where a claim
recurs across both shows, a `corroborated by` cross-show link. **196 corroboration clusters, 58
spanning both shows** — cross-show agreement is the highest-authority grounding the corpus offers.
**Any Claude instance can read that index to operate as a metrology expert here.***

**The loudest signal is MSAI's whole thesis.** The most-recurring claim, across both shows, is that
*proficiency testing — demonstrated competence against a proctored peer/reference check — is the only
objective proof of competence; documentation proves intent, not performance.* The one claim with
genuine **chatnapt↔qcast** corroboration captures it exactly: *"You've got to be able to show you can
do it. Proctoring it, proving it, that's where the application is required."* (Stahley, chatnapt-ep25,
corroborated by qcast-ep191). That is the field's own consensus, and it *is* MSAI.

**Each module, now cited — ★ = corroborated across both shows. Every quote verified verbatim against
the source EXTRACT (15 mined, 15 verified, 0 fabricated):**

| Module | Keystone sourced practice (verified claim) |
|---|---|
| **reliability** | ★ Rote step-following yields a number but not the judgment to know it's wrong — *"they just looked for a sine wave at a certain voltage and checked the box"* (Thomas, chatnapt-ep09 ↔ qcast-ep092); *"make sure you have a good Gage R&R in place ahead of time... a baseline... an understanding of truth"* (qcast-ep278). |
| **proficiency** | ★ *"You've got to be able to show you can do it. Proctoring it, proving it."* (Stahley, chatnapt-ep25 ↔ qcast-ep191); the En-score is the pass/fail judge — *"you use the e sub n number... to say whether we pass the PT or not"* (Shah, chatnapt-ep10). |
| **reference** | *"If you're not 100% comfortable with that established reference value and the associated uncertainty... the entire test is meaningless"* (Shah, chatnapt-ep10) — `reference.py`'s thesis verbatim; ★ traceability is earned, not asserted — *"what is NIST traceability — just by saying that doesn't mean you have it"* (Doty, chatnapt-ep22 ↔ qcast-ep195 *"do not use the NIST number as evidence of traceability"*). |
| **uncertainty** | ★ The complete budget = *"the five R's: reference standard and certainty, reference stability, resolution, repeatability, reproducibility... and environmental factors"* (Zumbrun, chatnapt-ep18 ↔ qcast); ★ a pass/fail without uncertainty is unsafe — *"a resulting probability that it's called a pass, but it has a high probability it could be a fail"* (qcast-ep243 ↔ chatnapt); ★ uncertainty is per-measurement, not per-instrument (qcast-ep222 ↔ chatnapt). |
| **stability** | ★ Don't trust the maker's interval — *"if you rely just on the manufacturer's recommended calibration interval you are setting yourself up for risk"* and *"if it's critical... do intermediate checks in between your calibration intervals"* (Shah, chatnapt-ep10 ↔ qcast) — the live drift monitor, verbatim. |

*(conformity / decision-rules grounding is the gauge track's lane — the "Proficiency Testing &
Decision Rules" community: guard-banded acceptance, the 4:1 TUR, judgement-box. See their commit.)*

**Where the corpus does NOT back us — cited honestly, never overclaimed:**
- **No verbatim `ndc` claim exists** in 208 episodes (full grep across both shows confirms it,
  matching the gauge track's independent finding). The *resolution floor* ndc relates to IS grounded
  (rating granularity, *"interpolate only to ~half a division by eye"*, Shah ep10) — but ndc as a
  named metric is cited at **principle level only**, never as a practitioner quote.
- **En/ζ and blind interlaboratory comparison have no qcast backing** — chatnapt-only at the verbatim
  level (qcast's "proficiency" claims are about third-party *certification*, a distinct thing). So the
  proficiency module is single-show on the *mechanism*, cross-show on the *principle*.
- **Root-sum-square combination is single-show** (qcast-ep142); the GUM/budget framing rests on the
  five R's enumeration, not a verbatim cross-show "root-sum-square" claim.

**It also corrects the UPC benchmark.** An in-house-only comparison is circular — the exact reason the
899 annotator-approved listings are a **start, not the gold standard** (an AI scored only against
AI-approved listings closes a circle). **UPC catalog truth is the independent anchor that breaks it**
— and before trusting that truth, validate it by multi-source agreement within an assigned uncertainty
(chatnapt-ep24-thomas), because *a test is only as meaningful as its reference value.*

## 3. Deepen what exists (priority order)

1. **Outlier-robust `rater_effects`.** Replace the panel `nanmean` (a single rogue
   judge currently poisons the very mean it's measured against) with ISO 13528
   Algorithm A robust consensus + banded z-scores. The skeptic called this
   *"unambiguously sound."* Cheapest high-value fix.
2. **Asymmetric accuracy ledger.** Split the one symmetric accuracy number into
   **miss rate (consumer's risk)** vs **false-alarm rate (producer's risk)** with the
   existing bootstrap CIs + a base-rate-masking flag. *Fix first:* define denominators
   at the **item** level (current loop double-counts multi-trial cells).
3. **Categorical repeatability vs reproducibility** for nominal data (within-judge flip
   rate vs between-judge disagreement) — tells you *fix the prompt* vs *fix the rubric*.
   *Fix first:* write a **new** nominal degenerate-detector — the continuous one in
   `variance.py` is unreachable on the nominal path.
4. **Reference uncertainty.** Stop treating the reference as an exact point; carry
   `u(x_pt)` and a ζ-verdict (a judge is "wrong" only when `|ζ|>2`, never inside the
   reference's own noise). Needs a small-p guard (2-4 judges → unstable).
5. **GUM budget on the headline accuracy.** Type-A sampling + ordinal quantization +
   optional reference-trust terms → `acc ± U (k=2)`. Keep conformance-sampling and
   reference-trust as **two separate budgets**, never one.

## 4. The three new directions

**① Execution-feedback grounding — the keystone.** *Let reality grade the judge.* The
accuracy math already exists; what's missing is the wiring that **fetches** a reference
from a real oracle instead of a human-typed key. An execution oracle is the one
reference that is **independent by construction**, breaking the consensus-circularity
MSAI can warn about but not otherwise escape.
→ *Step:* define `ReferenceOracle.fetch(item_id) -> {value, u, source_rank, timestamp}`;
ship one cheap deterministic adapter first (pytest exit-code / compiler-pass, no
network) to prove the seam; then a **`MarketplaceOracle`** against the resale-ai backend.

> ⚠ **The `MarketplaceOracle` must be an *experiment design*, not a dashboard query —
> or it launders noise into the gauge.** Raw "did it sell, how fast, at what price" is a
> *confounded* reference: sell-through is dominated by price, demand, season,
> competition, photos, and the item itself — mostly things the listing-**text** model
> doesn't control. Grade the model on raw sell/no-sell and you attribute marketplace
> noise to it — the exact failure mode MSAI exists to prevent. The defensible oracle is a
> **controlled comparison**: A/B the *same item* with different generated text, holding
> price/category fixed, so the reference isolates what the model actually owns. (That A/B
> *is* a `compare()` setup — the text variants are the "configs," the marketplace outcome
> is the grounded, independent reference.) This is literally our own *"your reference is
> only as good as you make it"* rule applied to the oracle. Done right, it's the cleanest
> proof of benevolence-is-efficient there is — the judge graded by **money changing
> hands**, not by other models agreeing with it.

**② Guard-banded conformity (`conformity.py`).** `compare()` does the *pairwise* version;
this does the *threshold* version: convert `score >= 7` into `score >= 7 + g` (`g = r·U`),
classify each item **PASS / FAIL / INDETERMINATE**, and report **consumer's vs producer's
risk separately**. No LLM-eval tool does this — everyone hard-thresholds the raw score and
silently eats false-accept risk.
→ *Build discipline:* `grr_sd` is a single dataset-level uncertainty, so report per-item
PASS/FAIL under a shared `U` and only compute per-item *risk* when per-cell replicate SD
exists; if `deterministic_judges` is set, **refuse** and raise
`uncertainty_unmeasured_guard_band_invalid` rather than print a false zero-risk verdict.

**③ Judge drift / stability (`stability.py`) — the missing time axis.** An LLM judge is
non-stationary in a way no steel gauge is; a silent overnight model update can invalidate
every score since. Today MSAI is a one-shot lab report. An SPC layer over a **frozen
anchor set** (EWMA + s-chart, Phase-I baseline, Western Electric rules) makes drift a
first-class, false-alarm-controlled event with a defensible "re-run *now*" trigger.
→ *Build discipline:* anchor set ≥ 5–10 items, baseline ≥ 8–12 runs (short noisy baselines
give false alarms); document that **DRIFT ≠ WRONG** — it flags that the measurement
*process* changed, not that the post-drift judge is incorrect (respect the precision-vs-
accuracy firewall).

## 5. Three build-discipline rules (recurring across the adversarial checks)

1. **Don't credit reuse of a guard that lives in a different module or is unreachable on
   the relevant path** (e.g. the temp-0 detector keys off continuous variance and is
   `None` on the nominal path).
2. **Never thread an LLM's self-reported confidence in as a calibrated σ.** A model
   saying "90% sure" is not a measured standard uncertainty.
3. **Don't promise per-item risk when only a pooled, dataset-level uncertainty exists.**

## 6. The strategic frame (from the Michelli podcast)

- **"Doing it right *is* the marketing."** Michelli's growth is trust-pull, not sales-
  push — satisfied customers *ask* them to expand; he calls it *"free marketing."* A real
  data point that quality drives expansion revenue at ≈zero CAC.
- **The honest wrinkle that sharpens the thesis.** It all rests on *unverifiable* trust
  ("the only thing the customer sees is that final cert… blind trust"). A less-benevolent
  competitor could free-ride on the same opacity — what stops them is **accreditation and
  regulation** (ISO 17025, proficiency testing, licensing), not virtue. So the defensible
  thesis is: ***benevolence is efficient, but it's the accreditation scaffolding that
  makes the trust durable and keeps extraction from paying off.***
- **"Accreditation, not a tool" is the *earned destination*, not the launch posture.**
  The customer can't inspect the measurement, so they ultimately buy the institution's
  integrity — the same structure as LLM-eval. But accreditation is a *trust institution*
  that NIST and the ISO bodies took decades and third-party legitimacy to earn. MSAI is a
  one-author package whose own README correctly says "this is a starting point, not a
  standard." Leading with "we're an accreditation body" before independent replication
  would trip the *exact* overclaim our three-lineage review already caught — and the
  tool's entire moat is that it doesn't overclaim. So the sequence is: **ship the honest
  tool → earn replications and adoption → then the accreditation position is yours by
  right.** The marketing must never outrun the credibility, because honesty *is* the product.
- **The field's own consensus now grounds the thesis.** The ChatNAPT corpus's single
  most-repeated claim — *proficiency testing is the **only** objective proof of competence,
  never self-report* (~20+ episodes) — is MSAI's reason to exist. The positioning is
  **"proficiency testing for AI judges,"** underwritten by the metrology field itself, and
  the private KB index is a guide any Claude instance can read to
  operate as a metrology expert on this codebase. The corpus compounds as more experts are added.
- **Convergence:** the episode's core decision frame is **false-accept / false-reject**,
  the conceptual parent of the guard-banding shipped in `compare()` and proposed in
  `conformity.py`. Real metrology and what we built are the same idea.

## 7. Benevolence-is-efficient, made literally measurable

The thesis stops being a slogan inside MSAI:
- **Guard-banding** = choosing to over-reject your *own* good outputs to protect the
  consumer from bad ones. Non-extraction, expressed as a risk number.
- **Reference-uncertainty propagation** = refusing to launder a noisy key into a tight,
  confident score. Honesty, expressed as `± U`.
- **Execution grounding** = the judge graded by money changing hands, not by other models
  agreeing with it. Benevolence, traced to a real outcome.

## 8. Recommended sequence

1. ✅ **`compare()`** — the pairwise acceptance test (done).
2. **Execution-feedback grounding** — `ReferenceOracle` + a pytest/compiler adapter to
   prove the seam, then the eBay `MarketplaceOracle` for resale-ai. *(Highest leverage.)*
3. **`conformity.py`** — guard-banded threshold verdicts; reuses `compare()`'s guard-band
   machinery and the GRR uncertainty.
4. **`stability.py`** — drift/recalibration trigger.
5. **Deepen as you go** — robust `rater_effects` (#1) and the asymmetric ledger (#2) are
   cheap and high-value; fold them in alongside.

*Corpus priority signal:* the ChatNAPT index flags **stability** as "highest interest" — a
silent overnight model swap invalidates every prior score (ep30-finale-4) — and makes
**reference** (validated gold labels) a **prerequisite for the UPC benchmark**, not a later
step (ep12-sims-8 circularity; ep10-shah-15 *a test is only as good as its reference value*).
So: ground the benchmark's reference first, then conformity, then stand up stability monitoring.

— per-pillar adversarial verdicts are in the deep-dive run output; the full sourced roadmap
(every module → its keystone metrology claims, with episode + speaker) is
the private KB index. This brief is the actionable
distillation; the corpus is the citable foundation.
