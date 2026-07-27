# MSAI → AI-Safety Metrology: the pivot brief

*Written 2026-07-02 by the review lane (Fable), at the close of the §6 resolution arc.
Audience: the operator + both work lanes + any future session. This is the durable version of the plan.*

---

## 1. The thesis

Metrology became load-bearing in manufacturing because accurate measurement saved lives,
time, and money — boiler codes needed calibrated pressure gauges, interchangeable parts
needed gauge blocks, trade needed NIST. **Regulation, insurance, and trust can only attach
to things that can be measured with stated uncertainty.** AI is pre-metrological: every
responsible-scaling policy, capability threshold, and "the model does not cross line X"
claim is a conformity decision made with an unqualified gauge — no uncertainty budgets, no
gauge R&R on judges, no drift monitoring, no guard bands sized to the asymmetry of a
false-accept. MSAI is the reference implementation of the missing measurement layer.

**The sharpest form of the pitch:** *if a safety eval's noise floor is wider than the
threshold it gates on, the safety case is theater — and MSAI is the instrument that
measures whether that's true.* The below-resolution / AT-EDGE verdict is a safety-audit
primitive, not a product feature.

Role model: Shewhart invented control charts as one person at Bell Labs; institutions
codified them later. The open role here is "wrote the Gage R&R of LLM evaluation before
the field knew it needed it." the operator's sales background is the adoption edge — standards
win by being sold, not just by being right.

## 2. What exists (asset inventory, post-§6)

- **Validated instrument**: crossed-design gauge (compare.py) with delta-basis
  reproducibility, level-centering, GUM budgets, guard bands, frozen-gauge refusal,
  four-state resolution verdict (WS-dof contract ratified; being folded into compare()).
- **Three-panel validation arc**: local coarse (Ollama) → chat frontier J=3 → API
  frontier J=5 (gpt-5.5, grok-4.3, gemini-3.1-pro-preview, opus-4-8, deepseek-v4-pro).
  Keystone pattern reproduced on all three; verdicts move lawfully with gauge precision.
  Headline: resolve RESOLVED / subtle AT-EDGE / tie BELOW. Total API spend: $2.23.
- **Honesty machinery**: precision-only claims, consensus-≠-correctness firewall,
  36 adversarially-found defects locked in strict-xfail ledgers, 123+ tests.
- **Measured paraphrase term** (~30% of gauge noise; frozen-fixture vs rubric-robust scopes).
- **THE GAUGE CERTIFICATE** (`benchmark/certificate.py`): renders a calibration-certificate
  artifact from persisted scores — see §3. First instance:
  `benchmark/CERTIFICATE_MSAI-8C06733F42F0.md` (900 ratings, J=5, sha256-bound).
- **Key finding with legs**: the frontier panel's noise floor sits at the human-ambiguity
  zone of the preference construct (subtle AT-EDGE; diversity widens the band) —
  consistent with *definitional uncertainty*, discriminable from shared-lineage bias only
  by a judge-independent reference. That discriminating experiment is the named successor.

## 3. The wedge: the Gauge Certificate

Metrology's killer artifact is not the math — it's the **calibration certificate**: a
standardized document a decision-maker holds. Nobody in AI eval issues one. MSAI now does:
instrument identity (exact model IDs), procedure, replication, per-tier resolution
verdicts with U and U's own CI, full uncertainty budget with dof, verbatim disclosures,
qualification statement, scope-of-validity, content-hash certificate number, and the
honesty footer (NO ACCURACY CLAIMED). Presentation-layer only — it rides the validated
compare()+four_state() path, so a certificate is exactly as trustworthy as the gauge.

Why it's the wedge: an eval team can't act on "read our paper"; they can act on
"here is your judge panel's certificate — it cannot resolve the delta you're shipping
decisions on." It converts MSAI from a library into an audit service.

## 4. The thunderclap demonstration (next study)

**Goal:** publish the gauge certificate of a *public, safety-relevant, LLM-judged eval* —
one that real decisions ride on (harmfulness graders / refusal classifiers / a
safety-benchmark judge, e.g. an MLCommons-style harm benchmark or a widely used
harmfulness-judge prompt).

Design sketch (same harness, new anchor):
1. Pick the eval + its published judge prompt. Freeze it (frozen-fixture scope).
2. Build tiers from *its own decision thresholds* (e.g. items near the pass/fail cut vs
   clearly-over vs clearly-under — threshold-anchored, not Elo-anchored).
3. Run the J=5 frontier panel + the eval's own judge through the blind protocol,
   R=3, one response per call (~$5–20 depending on n).
4. Publish the certificate. Two outcomes, both news:
   - Band swallows the threshold → "this safety eval cannot resolve the line it gates on"
     (constructive: the budget says which lever — panel size, replication, rubric — buys
     the missing resolution).
   - Gauge qualifies → first safety eval with a stated, defensible resolution. Also new.
5. Pre-register predictions and the band-edge rule before scoring (house discipline).

## 5. The preprint

Working title: *"Can your eval resolve the threshold it gates on? Measurement system
analysis for LLM-as-judge evaluation."*
Spine: thesis → methods (gauge model, delta basis, four-state verdict) → three-panel
validation arc → thunderclap case study → definitional-uncertainty finding → limitations
(precision-only; the accuracy anchor as future work).
**Must-position related work** (reviewers will check): generalizability theory (the
psychometric twin of Gage R&R — differentiate via the conformity/guard-band/qualification
layer); Anthropic's error-bars-on-evals work; prompt-sensitivity/position-bias literature;
"science of evals" calls (Apollo et al.); ILAC-G8 / ISO 14253 decision rules; AIAG MSA.
Venue: arXiv → TMLR (rigor-friendly) or an evals workshop. Remaining gaps: n=50 scale run
(~$15–20), related-work sweep, writing. Est. 3–5 focused weeks.

## 6. Go-to-market (sell the instrument)

Sequence: preprint + certificate of a public eval (owners notified well in advance,
per the project rails) → then approach the owners of the problem: AI safety institutes (US/UK), METR, Apollo, MLCommons, eval-tooling vendors.
The ask isn't "adopt my library" — it's "require a gauge certificate for any eval that
gates a safety decision." Long-term: MSAI as reference implementation of an
eval-metrology standard (the ISO-17025-shaped hole in AI governance).

## 7. 90-day shape (budget: tens of dollars, not thousands)

1. **Now**: fold-in lands (other lane); certificate module reviewed + adopted; close-out written.
2. **Weeks 1–2**: n=50 scale run ($15–20); pick thunderclap target; pre-register.
3. **Weeks 3–4**: thunderclap run + certificate ($5–20); related-work sweep.
4. **Weeks 5–8**: preprint draft; circulate to 2–3 evals-adjacent reviewers.
5. **Weeks 9–12**: arXiv + outreach (certificate attached to every email).
Parked but named: execution-feedback / marketplace-outcome accuracy anchor — the
PILOT→CLOSED path and the construct-vs-bias discriminating experiment.

## 8. Handoff notes (for the other lane / next session)

- `benchmark/certificate.py` is **presentation-layer only** — no gauge-contract changes.
  It imports `four_state` from `benchmark/resolution_verdict.py`; when the dof contract
  lands inside compare(), swap that import for the package path (grep the NOTE in the
  module docstring). Then consider promoting to `src/msai_eval/certificate.py` + a CLI
  entry point (`msai certify <scores.json>`).
- Certificate regeneration is deterministic from persisted scores:
  `python benchmark/certificate.py [scores.json] [--out X.md]`.
- Standing discipline unchanged: pre-register before scoring; band-edge is a verdict,
  not an embarrassment; every PASS gets adversarially checked; caveat travels with claim.
