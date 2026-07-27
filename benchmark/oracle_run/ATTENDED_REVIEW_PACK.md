# ATTENDED REVIEW PACK — code-oracle study (prereg 60c6525, seal REV-LANE #013)

*You are verifying RECEIPTS, not code. If any question seems to ask for a code*
*quality opinion, the answer is NO to Q12 and the pack is defective.*

Selection rule: all 3 consensus-wrong events (t01, t35, t48) + both
tie tasks + 2 lowest-id subtle + 3 lowest-id resolve not already selected.
Items: t01, t35, t48, t33, t45, t05, t08, t02, t03, t04

## t01 — “Slug Normalizer” (tier: resolve, CONSENSUS-WRONG EVENT)

- LIVE lever runs (just executed on your machine):
  - reference: pass_rate 1.000 → all tests pass: **YES**
  - machine A: LIVE 1.000 vs recorded 1.000 → **MATCH**
  - machine B: LIVE 0.000 vs recorded 0.000 → **MATCH**
  - gap arithmetic: 1.000 − 0.000 = 1.000, recorded g = 1.000 → **MATCH**
- Blindness scan of the harness wrapper (what the judge sees beyond the task text): forbidden words found: **NONE**
- Judge ratings (recorded | first line of the judge's own words):
  - gemma4:12b             machine A: [2, 2, 3]  raw₁: “2”
  - gemma4:12b             machine B: [2, 1, 4]  raw₁: “The candidate's code is missing from the prompt. Since I cannot evaluate a non-existent so”
  - LFM2-24B-A2B-GGUF:Q4   machine A: [3, 5, 4]  raw₁: “3”
  - LFM2-24B-A2B-GGUF:Q4   machine B: [5, 5, 5]  raw₁: “5”
  - minicpm-v:latest       machine A: [3, 3, 4]  raw₁: “3”
  - minicpm-v:latest       machine B: [2, 3, null]  raw₁: “2”
- **THE CONTRADICTION, in two lines you can check by eye:**
  - panel means: A = 3.22, B = 3.38 → panel prefers **B**
  - live levers: A = 1.000, B = 0.000 → levers prefer **A**

## t35 — “Configurable multi-key sort” (tier: resolve, CONSENSUS-WRONG EVENT)

- LIVE lever runs (just executed on your machine):
  - reference: pass_rate 1.000 → all tests pass: **YES**
  - machine A: LIVE 0.667 vs recorded 0.667 → **MATCH**
  - machine B: LIVE 0.000 vs recorded 0.000 → **MATCH**
  - gap arithmetic: 0.667 − 0.000 = 0.667, recorded g = 0.667 → **MATCH**
- Blindness scan of the harness wrapper (what the judge sees beyond the task text): forbidden words found: **NONE** · incidental words inside the task's own statement (same for both machines, authored before tiers existed — not leakage): ['config']
- Judge ratings (recorded | first line of the judge's own words):
  - gemma4:12b             machine A: [2, 2, 1]  raw₁: “2”
  - gemma4:12b             machine B: [2, 2, 2]  raw₁: “2”
  - LFM2-24B-A2B-GGUF:Q4   machine A: [2, 1, 1]  raw₁: “2

I'll explain why. The solution correctly captures the idea of sorting by multiple field”
  - LFM2-24B-A2B-GGUF:Q4   machine B: [2, 3, 4]  raw₁: “2


The code attempts to build a sorting key but fails in several critical areas: it does ”
  - minicpm-v:latest       machine A: [4, 4, 4]  raw₁: “4”
  - minicpm-v:latest       machine B: [4, 4, 4]  raw₁: “4”
- **THE CONTRADICTION, in two lines you can check by eye:**
  - panel means: A = 2.33, B = 3.00 → panel prefers **B**
  - live levers: A = 0.667, B = 0.000 → levers prefer **A**

## t48 — “Wildcard path query over nested dicts and lists” (tier: subtle, CONSENSUS-WRONG EVENT)

- LIVE lever runs (just executed on your machine):
  - reference: pass_rate 1.000 → all tests pass: **YES**
  - machine A: LIVE 0.000 vs recorded 0.000 → **MATCH**
  - machine B: LIVE 0.062 vs recorded 0.062 → **MATCH**
  - gap arithmetic: 0.000 − 0.062 = -0.062, recorded g = -0.062 → **MATCH**
- Blindness scan of the harness wrapper (what the judge sees beyond the task text): forbidden words found: **NONE** · incidental words inside the task's own statement (same for both machines, authored before tiers existed — not leakage): ['subtle']
- Judge ratings (recorded | first line of the judge's own words):
  - gemma4:12b             machine A: [2, 2, 3]  raw₁: “2”
  - gemma4:12b             machine B: [2, 2, 2]  raw₁: “2”
  - LFM2-24B-A2B-GGUF:Q4   machine A: [4, 4, 4]  raw₁: “4”
  - LFM2-24B-A2B-GGUF:Q4   machine B: [2, 4, 3]  raw₁: “2”
  - minicpm-v:latest       machine A: [4, 4, 4]  raw₁: “4”
  - minicpm-v:latest       machine B: [4, 4, 4]  raw₁: “4”
- **THE CONTRADICTION, in two lines you can check by eye:**
  - panel means: A = 3.44, B = 3.00 → panel prefers **A**
  - live levers: A = 0.000, B = 0.062 → levers prefer **B**

## t33 — “Roster multi-key ordering” (tier: tie, sampled)

- LIVE lever runs (just executed on your machine):
  - reference: pass_rate 1.000 → all tests pass: **YES**
  - machine A: LIVE 1.000 vs recorded 1.000 → **MATCH**
  - machine B: LIVE 1.000 vs recorded 1.000 → **MATCH**
  - gap arithmetic: 1.000 − 1.000 = 0.000, recorded g = 0.000 → **MATCH**
- Blindness scan of the harness wrapper (what the judge sees beyond the task text): forbidden words found: **NONE**
- Judge ratings (recorded | first line of the judge's own words):
  - gemma4:12b             machine A: [4, 3, 2]  raw₁: “4”
  - gemma4:12b             machine B: [4, 4, 4]  raw₁: “4”
  - LFM2-24B-A2B-GGUF:Q4   machine A: [4, 3, 3]  raw₁: “4”
  - LFM2-24B-A2B-GGUF:Q4   machine B: [5, 5, 5]  raw₁: “5”
  - minicpm-v:latest       machine A: [4, 4, 4]  raw₁: “4”
  - minicpm-v:latest       machine B: [4, 4, 4]  raw₁: “4”

## t45 — “Deepest leaf level in a category tree” (tier: tie, sampled)

- LIVE lever runs (just executed on your machine):
  - reference: pass_rate 1.000 → all tests pass: **YES**
  - machine A: LIVE 1.000 vs recorded 1.000 → **MATCH**
  - machine B: LIVE 1.000 vs recorded 1.000 → **MATCH**
  - gap arithmetic: 1.000 − 1.000 = 0.000, recorded g = 0.000 → **MATCH**
- Blindness scan of the harness wrapper (what the judge sees beyond the task text): forbidden words found: **NONE**
- Judge ratings (recorded | first line of the judge's own words):
  - gemma4:12b             machine A: [5, 5, 5]  raw₁: “5”
  - gemma4:12b             machine B: [2, 4, 4]  raw₁: “2”
  - LFM2-24B-A2B-GGUF:Q4   machine A: [4, 4, 5]  raw₁: “4

The provided solution correctly computes the deepest leaf level by recursively traversi”
  - LFM2-24B-A2B-GGUF:Q4   machine B: [4, 4, 5]  raw₁: “4

Explanation: The code correctly implements a recursive traversal that computes the dept”
  - minicpm-v:latest       machine A: [4, 4, 4]  raw₁: “4”
  - minicpm-v:latest       machine B: [4, 4, 4]  raw₁: “4”

## t05 — “Parse semicolon-delimited settings string” (tier: subtle, sampled)

- LIVE lever runs (just executed on your machine):
  - reference: pass_rate 1.000 → all tests pass: **YES**
  - machine A: LIVE 0.917 vs recorded 0.917 → **MATCH**
  - machine B: LIVE 0.667 vs recorded 0.667 → **MATCH**
  - gap arithmetic: 0.917 − 0.667 = 0.250, recorded g = 0.250 → **MATCH**
- Blindness scan of the harness wrapper (what the judge sees beyond the task text): forbidden words found: **NONE**
- Judge ratings (recorded | first line of the judge's own words):
  - gemma4:12b             machine A: [2, 2, 2]  raw₁: “2”
  - gemma4:12b             machine B: [2, 2, 2]  raw₁: “2”
  - LFM2-24B-A2B-GGUF:Q4   machine A: [5, 5, 4]  raw₁: “5”
  - LFM2-24B-A2B-GGUF:Q4   machine B: [2, 2, 3]  raw₁: “2”
  - minicpm-v:latest       machine A: [4, 4, 3]  raw₁: “4”
  - minicpm-v:latest       machine B: [4, 4, 4]  raw₁: “4”

## t08 — “Parse nested brace-record mini-format” (tier: subtle, sampled)

- LIVE lever runs (just executed on your machine):
  - reference: pass_rate 1.000 → all tests pass: **YES**
  - machine A: LIVE 0.067 vs recorded 0.067 → **MATCH**
  - machine B: LIVE 0.000 vs recorded 0.000 → **MATCH**
  - gap arithmetic: 0.067 − 0.000 = 0.067, recorded g = 0.067 → **MATCH**
- Blindness scan of the harness wrapper (what the judge sees beyond the task text): forbidden words found: **NONE** · incidental words inside the task's own statement (same for both machines, authored before tiers existed — not leakage): ['resolve']
- Judge ratings (recorded | first line of the judge's own words):
  - gemma4:12b             machine A: [2, 2, 2]  raw₁: “2”
  - gemma4:12b             machine B: [null, 1, 1]  raw₁: “The candidate did not provide a solution.

0”
  - LFM2-24B-A2B-GGUF:Q4   machine A: [4, 4, 4]  raw₁: “4”
  - LFM2-24B-A2B-GGUF:Q4   machine B: [5, 5, 3]  raw₁: “5”
  - minicpm-v:latest       machine A: [4, 4, 3]  raw₁: “4”
  - minicpm-v:latest       machine B: [3, 4, 4]  raw₁: “3”

## t02 — “Tag Canonicalizer” (tier: resolve, sampled)

- LIVE lever runs (just executed on your machine):
  - reference: pass_rate 1.000 → all tests pass: **YES**
  - machine A: LIVE 0.778 vs recorded 0.778 → **MATCH**
  - machine B: LIVE 0.000 vs recorded 0.000 → **MATCH**
  - gap arithmetic: 0.778 − 0.000 = 0.778, recorded g = 0.778 → **MATCH**
- Blindness scan of the harness wrapper (what the judge sees beyond the task text): forbidden words found: **NONE**
- Judge ratings (recorded | first line of the judge's own words):
  - gemma4:12b             machine A: [5, 5, 5]  raw₁: “5”
  - gemma4:12b             machine B: [1, null, 1]  raw₁: “The candidate's code is missing from the prompt. Since I cannot evaluate a non-existent so”
  - LFM2-24B-A2B-GGUF:Q4   machine A: [4, 4, 3]  raw₁: “4”
  - LFM2-24B-A2B-GGUF:Q4   machine B: [5, 5, 3]  raw₁: “5

The code correctly implements all steps: trimming, lowercasing, collapsing whitespace w”
  - minicpm-v:latest       machine A: [4, 4, 4]  raw₁: “4”
  - minicpm-v:latest       machine B: [4, null, 1]  raw₁: “4”

## t03 — “Headline Title-Caser” (tier: resolve, sampled)

- LIVE lever runs (just executed on your machine):
  - reference: pass_rate 1.000 → all tests pass: **YES**
  - machine A: LIVE 0.895 vs recorded 0.895 → **MATCH**
  - machine B: LIVE 0.000 vs recorded 0.000 → **MATCH**
  - gap arithmetic: 0.895 − 0.000 = 0.895, recorded g = 0.895 → **MATCH**
- Blindness scan of the harness wrapper (what the judge sees beyond the task text): forbidden words found: **NONE**
- Judge ratings (recorded | first line of the judge's own words):
  - gemma4:12b             machine A: [3, 4, 4]  raw₁: “3

3”
  - gemma4:12b             machine B: [1, null, null]  raw₁: “No candidate solution provided.

1”
  - LFM2-24B-A2B-GGUF:Q4   machine A: [4, 5, 5]  raw₁: “4”
  - LFM2-24B-A2B-GGUF:Q4   machine B: [4, 3, 2]  raw₁: “4”
  - minicpm-v:latest       machine A: [4, 4, 4]  raw₁: “4”
  - minicpm-v:latest       machine B: [3, 3, 4]  raw₁: “3”

## t04 — “Identifier Canonicalizer” (tier: resolve, sampled)

- LIVE lever runs (just executed on your machine):
  - reference: pass_rate 1.000 → all tests pass: **YES**
  - machine A: LIVE 0.500 vs recorded 0.500 → **MATCH**
  - machine B: LIVE 0.000 vs recorded 0.000 → **MATCH**
  - gap arithmetic: 0.500 − 0.000 = 0.500, recorded g = 0.500 → **MATCH**
- Blindness scan of the harness wrapper (what the judge sees beyond the task text): forbidden words found: **NONE**
- Judge ratings (recorded | first line of the judge's own words):
  - gemma4:12b             machine A: [3, 3, 3]  raw₁: “3”
  - gemma4:12b             machine B: [1, null, 1]  raw₁: “Since no candidate solution was provided, I cannot evaluate it. However, based on the inst”
  - LFM2-24B-A2B-GGUF:Q4   machine A: [4, 4, 2]  raw₁: “4”
  - LFM2-24B-A2B-GGUF:Q4   machine B: [4, 3, 5]  raw₁: “4

”
  - minicpm-v:latest       machine A: [4, 4, 4]  raw₁: “4”
  - minicpm-v:latest       machine B: [3, 3, null]  raw₁: “3”

## Global receipts
- Quarantined t32 rows present in the analysis data: **0** (must be 0)
- Gauge-excluded units (unbalanced cells): **['t01', 't02', 't03', 't04', 't06', 't08', 't10', 't23']** — must match the certificate
- Disclosed nulls: **14/828**; per judge: gemma4:12b 9/276, LFM2-24B-A2B-G 0/276, minicpm-v:late 5/276
- All-items rollup: reference all-pass everywhere: **YES** · A rates all MATCH: **YES** · B rates all MATCH: **YES** · g arithmetic all MATCH: **YES** · blindness scans all clean: **YES**

## The 13 questions (answer YES/NO; any NO → write one line about what you saw)

1. This script ran on your machine and printed live test results for every item.
2. Every reference solution passed all its tests, live (rollup line says YES).
3. Every machine-A live rate says MATCH against the recorded rate.
4. Every machine-B live rate says MATCH.
5. Every gap line says MATCH (the subtraction is right).
6. Every blindness scan says NONE (the judges' prompt never mentions tiers, tests,
   configs, or the oracle).
7. Spot-checking the judge tables: the recorded numbers match the digits in the
   judges' own quoted words (nulls appear as 'null', never as a number).
8. Each judge has 3 ratings per machine, or the shortfall is visible as nulls in
   the disclosed-nulls line.
9. For each of the three CONSENSUS-WRONG items, the two-line contradiction shows
   the panel preferring the machine the live levers scored LOWER.
10. The quarantined-t32 count printed 0.
11. The excluded-units list matches the certificate's list (compare when cert #3
    is in front of you; leave blank until then if needed).
12. At no point did this review ask you to judge code quality.
13. Nothing you saw looked wrong, altered, or confusing — or if it did, you wrote
    it down.

*Sign-off format: 'Attended review: Q1–Q13 = <answers>, <date>, <name>' in a*
*message or a bus drop. Your answers get stamped into certificate #3 verbatim.*
