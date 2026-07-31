# Start here — a visitor's guide

*Written for the people we met at NCSLI: fluent in Gage R&R, uncertainty budgets, and
decision rules — maybe less fluent in AI tooling and GitHub. Good news: you already
know the hard half. The statistics in this project are your statistics. The only new
vocabulary is the instrument being measured.*

## What this is, in one paragraph

AI systems are now graded by other AI systems ("LLM judges" — a language model given
a rubric and asked to score another model's output, typically 1–5). Those judge panels
gate real decisions, yet almost nobody qualifies them the way you would qualify a
gauge. This project runs **MSA on AI judges**: Gage R&R, uncertainty budgets, guard
bands, En scores — the discipline you already practice, pointed at a new instrument.
Our flagship result is a panel that **failed qualification honestly**: its noise band
(U ≈ 2.5 on a 4-point span) was wider than every difference it was asked to resolve,
and the method caught that *before* anyone trusted its verdicts.

## The 10-minute path (nothing to install)

1. Open the presentation: **https://dellsbells.github.io/msai-results/** — scroll it
   top to bottom like a story. Everything animates; nothing needs a login.
2. Click **GRAPHS** in the top pill — the by-part-by-measurer chart, the uncertainty
   budget donuts, and one histogram you will recognize instantly as a stuck needle.
3. Click **MSAI STUDIES** — the seven studies, one line each. Click any row and the
   actual formulas slide out, with a plain-English translation under each.

## The trust-but-verify path (10 more minutes, still nothing to install)

Every number on that page has a receipt in this repository. To check one:

1. Open [`docs/PUBLIC_CLAIMS_LEDGER.md`](docs/PUBLIC_CLAIMS_LEDGER.md) — a table
   mapping each public claim to the file that backs it.
2. Worked example — the site claims the consensus-wrong rate is **6.8% [2.0%, 17.1%]**:
   open [`benchmark/oracle_run/analysis_results.json`](benchmark/oracle_run/analysis_results.json)
   right in your browser, press Ctrl+F, search `consensus_wrong`. You'll find
   3 events in 44 pairs with that exact Jeffreys interval. That's the receipt.
3. Worked example — the stuck needle: same file, search `"4"` counts, or open the
   certificate [`benchmark/oracle_run/CERTIFICATE_MSAI-3E19DD3B0061.md`](benchmark/oracle_run/CERTIFICATE_MSAI-3E19DD3B0061.md)
   and read §1. 202 of 271 ratings were the same "4" — a comparator that always reads
   nominal, which you have seen before on a bench.

For the cryptographically inclined: the certificate's ID **is** the SHA-256 of the
frozen scores file. On a Mac: `shasum -a 256 benchmark/oracle_run/oracle_study_scores.json`
— the first 12 hex characters are the certificate number. The prereg seal works the
same way against `docs/CODE_ORACLE_PREREG.md`. A hash here plays the role a tamper
seal plays on your reference standard.

## The run-it-yourself path (~15 minutes, one-time setup)

```bash
git clone https://github.com/DellsBells/msai-eval.git
cd msai-eval
pip install -e ".[dev]"
pytest
```

Expected: **151 passed, 2 skipped** (the skips name the public dataset you'd fetch to
enable them). Then try the library on your own data — a CSV of judge scores works:
see "Install & quickstart" in [`README.md`](README.md).

## Translation table (the only new words you need)

| AI term | The bench equivalent |
|---|---|
| LLM judge | The gauge under test — an AI model scoring another AI's output on a rubric |
| Judge panel | Multiple appraisers measuring the same parts |
| Prompt / rubric | The work instruction handed to the appraiser |
| Temperature | A repeatability knob — 0 freezes the gauge (EV=0 is FROZEN, not perfect) |
| Hidden test suite | The reference standard: executable pass/fail truth the judges never see |
| Hallucination / fabrication | The instrument reporting a value with no measurand behind it |

## Honest scope, before you ask

Read [`WHAT_THIS_IS_NOT.md`](WHAT_THIS_IS_NOT.md) — it's short and it's the part we're
proudest of. n=3 judges, 55 tasks, one lab, no outside replication yet. The claim is
not "we solved AI evaluation." The claim is that evaluation instruments should earn
trust the way your gauges do — by blind comparison against references, with
uncertainty stated — and here is a working, checkable demonstration.

Questions, replication attempts, and hostile audits are all welcome — the hostile ones
especially. [`docs/FAQ.md`](docs/FAQ.md) answers the sharpest ones we've gotten so far.
