# MSAI — Measurement System Analysis for Intelligence

*Early research release — install from source (not yet published to PyPI).*

**Gage R&R for LLM-as-judge evals. Measure your measurement system, not your model.**

MSAI brings the discipline manufacturers use to decide whether a gauge can be
trusted — **Measurement System Analysis (MSA)** — to the reproducibility of
LLM-as-judge evaluation. It answers a question the AI-eval field mostly skips:
*when your LLM judges disagree, is that real signal about your models — or just
noise in your scoring rubric?*

```python
import msai_eval as msai
report = msai.reliability(scores, level="ordinal")
report.summary()
```

> **Scope, stated up front and printed on every report:** MSAI measures whether
> your judges **agree** and how **reproducible** your eval is. It does **not**, by
> itself, measure whether the judges are **right**, or whether your model is good.
> Absent a reference there is no "true score" for a rubric judgment, so **no
> accuracy is claimed** — high agreement is equally consistent with a correct
> rubric, a shared *wrong* rubric, and successful gaming. The one exception is the
> opt-in accuracy tier (below): if **you** supply a reference you can defend, MSAI
> reports conformance to *that* reference — a claim only as valid as the reference
> is. Treat agreement as a *precondition* for a trustworthy eval, never as proof.

That honesty is the point. Most eval tools quietly imply a confident score is a
correct score. MSAI refuses to — and that refusal is what makes its numbers
defensible to anyone who actually knows measurement science.

## Studies & receipts

Seven studies run, three gauge certificates issued. The results are presented at
**https://dellsbells.github.io/msai-results/** — and every number there traces to a
committed artifact here:

- **[`docs/PUBLIC_CLAIMS_LEDGER.md`](docs/PUBLIC_CLAIMS_LEDGER.md)** — every public
  claim mapped to its receipt file. Start here if you came to check us.
- **Certificates:** [`benchmark/CERTIFICATE_MSAI-8C06733F42F0.md`](benchmark/CERTIFICATE_MSAI-8C06733F42F0.md)
  (frontier panel) and [`benchmark/oracle_run/CERTIFICATE_MSAI-3E19DD3B0061.md`](benchmark/oracle_run/CERTIFICATE_MSAI-3E19DD3B0061.md)
  (sealed code-oracle study — the certificate ID **is** the sha256 of the scores file).
- **Sealed prereg:** [`docs/CODE_ORACLE_PREREG.md`](docs/CODE_ORACLE_PREREG.md) —
  hash-sealed before any candidate solution existed.
- **Reproduce:** the corpus manifest ([`benchmark/oracle_corpus/CORPUS_MANIFEST.md`](benchmark/oracle_corpus/CORPUS_MANIFEST.md))
  documents the hidden-suite verify loop; `benchmark/oracle_run/render_certificate3.py`
  regenerates certificate 3 from the committed scores; `pytest` runs the gate tests.
- **Honest scope:** [`WHAT_THIS_IS_NOT.md`](WHAT_THIS_IS_NOT.md) ·
  hostile questions answered in [`docs/FAQ.md`](docs/FAQ.md) ·
  third-party data terms in [`NOTICE.md`](NOTICE.md).

## Why "MSA," precisely

MSA is the umbrella discipline for asking *is this measurement system fit to make
decisions?* It contains several study types. MSAI maps them onto AI evaluation —
**parts → items, appraisers → judge models, the gauge → your rubric** — and ships
them one at a time:

| MSA study | Question | Needs | MSAI |
|---|---|---|---|
| **Gage R&R** (repeatability + reproducibility) | do judges agree, and is a judge consistent with itself? | repeated/multi-judge scores | **v0 (this release)** |
| **Attribute agreement** | do judges agree on categorical calls (pass/fail, coercion y/n)? | labels | **v0** (weighted κ) |
| **Bias / linearity** | is a judge *right*, and right across the whole scale? | a **reference standard** (true values) | **v1** — via real-world graders |
| **Stability** | does the judge drift over time? | timestamped runs | v1 |

The crucial line: the **bias study requires a reference standard** — a known true
value. Rubric judgments don't have one, which is exactly why v0 makes *no accuracy
claim*. v1's grounding tier supplies the missing reference the only honest way:
let *reality* grade the judge (a test suite, a compiler, an API outcome), instead
of letting judges grade each other.

## Install & quickstart

```bash
# not yet published to PyPI — install from a clone of the repo:
pip install -e .
```

`scores` can be a list of dicts, a pandas DataFrame, a nested dict, or a 2D array:

```python
import msai_eval as msai

scores = [
    {"item": "resp_1", "judge": "gpt-judge",    "score": 4},
    {"item": "resp_1", "judge": "claude-judge", "score": 4},
    {"item": "resp_1", "judge": "llama-judge",  "score": 3},
    {"item": "resp_2", "judge": "gpt-judge",    "score": 2},
    # ...
]

report = msai.reliability(scores, level="ordinal")
report.summary()       # the honest plain-language report
report.to_dict()       # machine-readable, for CI gates / dashboards
```

Output (abridged):

```
  AGREEMENT (do your judges agree with each other?)
    Krippendorff's alpha (ordinal) = 0.806  [95% CI 0.627, 0.885]
    ICC(2,1) absolute agreement    = 0.815  [95% CI 0.677, 0.903]
    -> high agreement

  PER-JUDGE EFFECT (deviation from panel mean — DESCRIPTIVE, not a correction)
    gpt-judge     +0.22
    claude-judge  +0.27
    llama-judge   -0.48

  SCOPE — ... It does NOT measure whether the judges are RIGHT ...
```

Give each judge **repeat trials at temperature > 0** and MSAI additionally runs the
full Gage R&R variance decomposition — what share of your score spread is real item
difference vs. measurement-system noise. See `examples/quickstart.py`.

### Accuracy tier — grade against a *trusted* reference

If you have a reference you can defend — a proven label key, a consented/ratified
baseline, or a real execution outcome — pass it and MSAI adds an accuracy ledger
*separate from* the agreement ledger:

```python
report = msai.reliability(scores, level="nominal",
                          reference={"resp_1": "A", "resp_2": "C"})  # the trusted key
```

This is the only place MSAI claims accuracy, and the claim is strictly scoped:
**accuracy = conformance to the reference you supplied, and it's only as valid as
that reference.** Judge consensus is *not* a valid reference — grading judges
against their own average is circular. MSAI can't verify where your reference came
from (that's on you), but it *does* detect the circular case it can see: if your
reference matches the judges' own consensus, it raises a `reference_is_consensus`
flag. The payoff is the side-by-side read: **high agreement + low accuracy = your
judges share a bias and are confidently wrong together.**

For categorical scores (category IDs, labels), use `level="nominal"` — MSAI then
aggregates trials by mode and suppresses the magnitude-based statistics (no
"mean difference" on labels), reporting per-judge *dissent rates* instead.

### `compare()` — the config-vs-baseline acceptance test

`reliability()` qualifies your gauge. `compare()` *uses* it. Given a fixed set of
**treatments** (model configs, prompt variants, quantization/compression settings…)
each scored by a held judge panel, it asks: **is each one different from the baseline
by more than the measurement system's own noise?**

```python
report = msai.compare(scores, baseline="fp16", level="ordinal")
report.summary()
```
```
  GAUGE (can the measurement system even support this comparison?)
    ndc = 6 (advisory)   gauge-noise SD (GRR) = 0.270   guard band (GUM expanded U, floored at 2·GRR SD) = 0.760   -> QUALIFIED

  COMPARISONS (vs baseline; Holm-corrected across the family)
    q2         Δ = -2.960  [95% CI -3.000, -2.840]   Cliff's δ=-1.00   -> REAL drop (beyond gauge resolution)
    delta_kv   Δ = +0.000  [95% CI -0.120,  0.120]   Cliff's δ= 0.00   -> within noise (indistinguishable on this gauge)
```
*(Regenerate this block verbatim with `python examples/compare_example.py`.)*

This is a **measurement decision rule with guard-banding** — the metrology of
conformity assessment (ISO/IEC 17025 §7.8, JCGM 106) applied to LLM-judge scores.
It is the right tool *because* your configs are hand-picked treatments, not a random
part sample: `%GRR`/`ndc` are selection-sensitive under hand-picked parts, so a direct
pairwise mean-difference-with-uncertainty is the honest instrument here.

Three guards keep it honest rather than a dressed-up t-test:

- **It self-checks the gauge first.** Qualification keys on **resolution**: if the gauge
  is frozen (temperature 0, degenerate repeatability) or has no measurable resolution (no
  balanced replicates → no guard band), every verdict is marked *provisional* with the
  reason — it will not hand back a confident Δ that a gauge can't support. `ndc` is
  reported as **advisory context only and does NOT gate** (`min_ndc` just tunes the
  advisory warning): because the configs are hand-picked treatments, `ndc` is
  selection-sensitive — it shrinks when configs cluster into a few quality tiers even on a
  sharp gauge, so gating on it would suppress *true* findings. The guard band
  (`2·GRR_SD`, a pure function of gauge noise) is the honest resolution criterion. With
  fewer than ~4 judges it also flags that the bootstrap CI is coarse, so you lean on the
  guard band and Cliff's δ rather than the interval width.
- **It corrects for multiple comparisons** (Holm across the configs-vs-baseline
  family), so you can't manufacture a "real drop" by running enough configs.
- **It separates two gates and never merges them:** *resolvable* (CI excludes 0,
  Holm-corrected) vs *beyond gauge resolution* (`|Δ| > guard band`, default 2·GRR_SD).
  A drop can be statistically real yet below the gauge's resolution — it tells you which.

On ordinal scores it also reports **Cliff's δ** (rank-based) beside the mean Δ, because
a mean on a 1–5 scale silently assumes interval spacing.

The workflow is two steps: `reliability()` to qualify the panel, then `compare()` to
read the effect. Never use a model under test as one of its own judges — that's the
circular case `reliability()` already flags.

### CLI — point it at a CSV you already have

```bash
python -m msai_eval scores.csv --level ordinal        # columns: item, judge, score
python -m msai_eval scores.csv --json                 # machine-readable
python -m msai_eval scores.csv --compare fp16         # the acceptance test, baseline = fp16
```

Add a `reference` column to the CSV and the accuracy tier runs automatically.

## What it computes — and why these statistics

| Statistic | What it tells you | Why this one |
|---|---|---|
| **Krippendorff's α** (ordinal) | overall judge agreement | handles missing data, any number of judges, and *ordinal* rubric scales — most evals are exactly this case |
| **ICC(2,1)** absolute agreement | agreement as a variance ratio | the familiar intraclass correlation; cross-checks α |
| **Quadratic-weighted κ** | pairwise agreement (2 judges) | the right metric when you only have two judges |
| **Variance components / %GRR** | real signal vs. measurement noise | the Gage R&R decomposition — *only* reported on a balanced, replicated design |
| **Bootstrap 95% CIs** | how stable the above are | small eval sets give wide intervals; judge by the lower bound |
| **Per-judge effect** | which judge runs hot/cold | reported as a *descriptive* rater effect — **never** auto-corrected |

All agreement statistics are validated against published reference values in the
test suite (Krippendorff's canonical example; Shrout & Fleiss 1979 for ICC).

## Failure modes it catches (so you don't ship a number that lies)

MSAI was built by debugging an earlier scoring engine that did all of these wrong.
It flags, rather than hides, the conditions that make a reliability number
meaningless:

- **Frozen gauge (temperature 0).** Deterministic judges give identical repeat
  scores → zero within-cell variance → naive Gage R&R reports *perfect*
  repeatability. MSAI flags it as **degenerate, not perfect**.
- **No true value.** It never substitutes judge consensus for ground truth, and
  never "corrects" judges toward the panel mean — that manufactures agreement and
  destroys the only signal (disagreement) you have.
- **Selection-sensitive %GRR.** The noise-share number shrinks just by feeding in
  more spread-out items, so MSAI labels it as such: it prints the AIAG-convention
  advisory grade by default, and you supply your own thresholds to override it.
- **Too few items / single judge / unbalanced design.** Flagged explicitly, with
  the estimate degraded honestly rather than reported as if solid.

## Roadmap

- **v0.1: the R&R studies.** Reproducibility and agreement, done honestly. *Are
  your judges measuring the same thing the same way?*
- **v0.2: the bias study, against a supplied reference.** Pass a
  trusted key/baseline and MSAI reports conformance accuracy as a separate ledger,
  with the scope discipline enforced (the reference must be defensible; consensus
  is refused). Plus correct nominal/categorical handling and a CSV CLI.
- **v0.3: `compare()` — the acceptance test.** A measurement decision
  rule with guard-banding: is a treatment different from a baseline beyond the gauge's
  own noise? Gauge self-check, Holm multiplicity correction, and the resolvable-vs-
  beyond-gauge gates kept separate. Turns MSAI from a gauge-qualifier into the
  acceptance test for A/B-ing model configs, prompts, or compression settings.
- **v0.4–0.7: the metrology modules.** `reference` (traceable values carrying their own
  `u_ref`), `uncertainty_budget` (the GUM budget — the principled version of the guard
  band), `proficiency` (ISO 13528 En/ζ scoring of each judge vs a robust panel),
  `stability` (judge drift over time), and a `gauge_judgement` box on `reliability()`.
  See `HANDOFF_msai-modules.md`; the full write-up lands in the v0.8 coherence pass.
- **next: grounding adapters.** First-class connectors that *fetch* the reference
  from a real grader (a test suite, a compiler, a marketplace API, a verified
  outcome) instead of you passing it in — so "let reality grade the judge" becomes
  one line. The accuracy math is already here; this wires it to live oracles.

## What this is NOT — limitations, stated plainly

This package was stress-tested by independent model reviewers (different lineages)
before release. Their sharpest criticisms are *correct*, and they are stated here
rather than hidden. MSAI is a useful instrument with hard boundaries:

- **It is not a safety certification, and precision is not safety.** A judge can be
  perfectly reproducible and *consistently wrong*. A good MSAI report means your
  measurement system is stable — it says **nothing** about whether your model is
  safe, aligned, or correct. Do not cite an agreement number as evidence a model
  passed a safety bar. That inversion is exactly the misuse this tool warns against.
- **The instrument is non-stationary.** Unlike a steel gauge, an LLM judge can
  change behavior overnight (model updates, prompt/caching changes, context
  shifts). A Gage R&R study assumes the gauge is stable *during* the study. Re-run
  reliability whenever the judge, prompt, or model version changes — and never
  compare runs made against different judge versions.
- **There is no traceable "true value," and your reference is only as good as you
  make it.** Physical metrology is traceable to SI standards with known
  uncertainty. Rubric judgments are not. The accuracy tier grades against the
  reference *you* supply; if that reference is itself uncalibrated (e.g. one
  annotator's opinion), MSAI will faithfully report conformance to a possibly-wrong
  ruler. The tool cannot fix a weak reference — it can only be honest that the
  claim inherits the reference's weakness.
- **It measures the measurement system, not the world.** MSAI tells you whether you
  can *trust the numbers your eval produces*. Whether those numbers measure the
  thing you care about is a question MSAI cannot answer for you.

## The gauge certificate

MSAI renders a **calibration certificate** from a run — metrology's load-bearing artifact,
the document a decision-maker holds, issued here for an LLM-judge panel. It lists the
instrument (exact model IDs), per-tier resolution verdicts with the guard band *U* and *U*'s
own confidence interval, the full uncertainty budget with degrees of freedom, every gauge
warning verbatim, a scope-of-validity statement, and a content-hash certificate number — with
**NO ACCURACY CLAIMED** printed where it can't be missed. It is presentation-layer only: it
rides the validated `compare()` + four-state path, so a certificate is exactly as trustworthy
as the gauge behind it. The framing this enables: *if a safety eval's noise floor is wider than
the threshold it gates on, the safety case is theater* — and the certificate is the instrument
that measures whether that's true. First instance (pilot-scale, a J=5 frontier panel):
`benchmark/CERTIFICATE_MSAI-8C06733F42F0.md`. Spec and pivot: `docs/CERTIFICATE_SPEC.md`,
`docs/SAFETY_PIVOT.md`.

## Status

MSAI is an early, honest attempt to bring measurement-system discipline to
LLM-as-judge evaluation — **not** a finished or official standard. Standards are
forged by a community over time (the way NIST and the metrology bodies forged the
ones manufacturing relies on today); this is a starting point offered in that
spirit, to be stress-tested and sharpened in the open. Issues, replications, and
counter-examples are the point.

## License

MIT. See `LICENSE`.
