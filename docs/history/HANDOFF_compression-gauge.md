# Handoff: using MSAI as the gauge for the compression experiment

For the session running the RAM/quality-compression work. MSAI ships `compare()` (added in
`v0.3.0`; package is now `v0.7.0`), the acceptance test you spec'd. This is everything you need
to wire it in.

```bash
pip install -e .      # or: pip install msai-eval (once published)
```

## The one rule that makes this valid: qualify the gauge BEFORE you trust a delta

The field skips this; it's the whole point. You run **two steps, in order**:

1. **Qualify the gauge** with `reliability()` — is your judge panel even able to see
   the effect you're chasing?
2. **Measure the effect** with `compare()` — is each config different from FP16 beyond
   the gauge's own noise?

If step 1 fails, step 2 is meaningless. `compare()` self-checks and will mark its
verdicts *provisional* if the gauge is unqualified, but check it explicitly anyway.

## How to shape the data

`compare()` takes the same input as `reliability()`. Map your experiment like this:

| MSA role | Your experiment |
|---|---|
| **items** (the "parts") | the configs you're A/B-ing: `{fp16, q4, q2, delta_kv, dither_2bit, …}` |
| **judges** (the "appraisers") | your judge panel — **held fixed, independent of the models under test** |
| **trials** | repeat scorings of the same item by the same judge, **at temperature > 0** |
| **baseline** | the reference config, almost always `fp16` |

```python
import msai_eval as msai

scores = [
    {"item": "fp16",     "judge": "judge_A", "score": 5},   # one row per (config, judge, trial)
    {"item": "fp16",     "judge": "judge_A", "score": 4},   # >= 2 trials/cell, temp>0
    {"item": "q2",       "judge": "judge_A", "score": 3},
    {"item": "delta_kv", "judge": "judge_A", "score": 5},
    # ... every config x every judge x every trial
]

# Step 1 — qualify the gauge
rel = msai.reliability(scores, level="ordinal")
rel.summary()
# look at: the guard band + deterministic_judges flag (THE qualification criteria). ndc is
# advisory context only — selection-sensitive on hand-picked configs, NOT a gate. %GRR likewise.

# Step 2 — the acceptance test
cmp = msai.compare(scores, baseline="fp16", level="ordinal")
cmp.summary()
```

## How to read `compare()`

Each config gets a verdict from two gates, **kept separate on purpose**:

- **resolvable** — the bootstrap CI on Δ excludes 0 (statistically distinct), *after*
  Holm correction across the family of configs-vs-baseline tests.
- **beyond gauge resolution** — `|Δ| > guard band` (default `2 · GRR_SD`): the
  difference is bigger than the measurement system's own resolution.

Verdicts:
- `REAL drop (beyond gauge resolution)` → both gates → ship-blocker if it's a quality drop.
- `statistically real drop, but BELOW gauge resolution` → real but smaller than the
  gauge can resolve; treat as "probably fine, sharpen the rubric if you care."
- `within noise (indistinguishable on this gauge)` → the difference is **below this gauge's
  resolution** (smaller than the guard band) — NOT proof the configs are equal or "lossless."
  A real difference smaller than the guard band reads this way. Treat it as a *provisional*
  accept for `delta_kv` / `dither_2bit`, and before trusting it on a small frontier delta,
  confirm the guard band is fine enough (a real-but-sub-resolution drop is reported separately
  as "statistically real but BELOW gauge resolution," never folded into "within noise").
- `gauge unqualified — provisional` → fix the gauge first; the number is not trustworthy.

On ordinal scores, **Cliff's δ** (rank-based, in [-1,1]) is reported beside the mean Δ.
When the two disagree, trust Cliff's δ — the mean assumes interval spacing a 1–5 scale
doesn't have.

## Three traps (your own code warns about the first two)

1. **Frozen gauge.** If you score at temperature 0, every repeat trial is identical →
   within-cell variance 0 → fake-perfect repeatability. MSAI flags `deterministic_judges`
   and refuses to certify. **Run trials at temperature > 0 with independent seeds.**

2. **%GRR is selection-sensitive — do NOT use it as the grade here.** Because your
   "parts" are hand-picked configs (not a random sample), throwing in a deliberately
   broken 1-bit config inflates the config spread and makes `%GRR` look great for free.
   **Lean on `ndc` and the per-config effect-size-vs-guard-band (`compare()`), never
   `%GRR`-as-pass/fail.** This is exactly why `compare()` exists instead of a Gage R&R grade.

3. **Circular judging.** Never let a model that's being compressed sit on its own judge
   panel — that's the consensus-as-reference circularity `reliability()` already flags.

## The north star (later, not now)

For resale-ai the defensible reference isn't a judge at all — it's **did the listing
sell, how fast, at what price.** A grounding adapter that grades against *marketplace
outcomes* would let you eventually measure "did compressing the listing model hurt
quality" against real conversion, not a rubric. The accuracy math is already in MSAI;
this is wiring it to a live oracle (roadmap: grounding adapters). That's the
benevolence-is-efficient thesis with a real instrument under it.

— shipped in `msai-eval` `v0.3.0`; `compare()` API and three guardrails are in the README.
