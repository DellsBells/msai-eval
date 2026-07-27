# Oracle Corpus Verification Manifest

- **Prereg sha256:** `19bdfc445742a2ca3970f82ac84350519a55ce99bf6fe10c137533381d614cd5`
- **Lane:** REV-LANE #013
- **Ledger revision:** 2
- **Corpus:** `benchmark/oracle_corpus/`
- **Task dirs censused:** 56
- **Ledger-PASS (feed oracle):** 55
- **Dropped:** 1
- **clean:** `true`

## Counts

- Difficulty (PASS only): easy=14, medium=28, hard=13
- Split (PASS only): analysis=47, pilot=8

## Tasks

| id | title | topic | difficulty | split | status |
|----|-------|-------|-----------|-------|--------|
| t01 | Slug Normalizer | string transformation & normalization | easy | analysis | PASS |
| t02 | Tag Canonicalizer | string transformation & normalization | medium | analysis | PASS |
| t03 | Headline Title-Caser | string transformation & normalization | medium | analysis | PASS |
| t04 | Identifier Canonicalizer | string transformation & normalization | hard | analysis | PASS |
| t05 | Parse semicolon-delimited settings string | tokenizing / parsing structured text | easy | analysis | PASS |
| t06 | Validate nested brackets and measure depth | tokenizing / parsing structured text | medium | analysis | PASS |
| t07 | Split delimited line with quoted fields | tokenizing / parsing structured text | medium | analysis | PASS |
| t08 | Parse nested brace-record mini-format | tokenizing / parsing structured text | hard | analysis | PASS |
| t09 | Merge touching and overlapping intervals | interval & range arithmetic | easy | analysis | PASS |
| t10 | Uncovered gaps within a window | interval & range arithmetic | medium | analysis | PASS |
| t11 | Total and multiply-covered length | interval & range arithmetic | medium | analysis | PASS |
| t12 | Interval set difference and peak coverage depth | interval & range arithmetic | hard | analysis | PASS |
| t13 | Working days between two dates | date & calendar logic using only the datetime stdlib module | easy | analysis | PASS |
| t14 | Nth-weekday-of-month recurrence expander | date & calendar logic using only the datetime stdlib module | medium | analysis | PASS |
| t15 | ISO week bucketing | date & calendar logic using only the datetime stdlib module | medium | analysis | PASS |
| t16 | Earliest common meeting slot across UTC offsets | date & calendar logic using only the datetime stdlib module | hard | analysis | PASS |
| t17 | Bracket Fault Locator | stack/queue state machines | easy | analysis | PASS |
| t18 | Undo/Redo Command Log | stack/queue state machines | medium | analysis | PASS |
| t19 | Tiny Stack Machine | stack/queue state machines | medium | analysis | PASS |
| t20 | Bounded Session Log with Checkpoints | stack/queue state machines | hard | analysis | PASS |
| t21 | Orthogonal neighbor sum grid | grid / matrix operations | easy | analysis | PASS |
| t22 | Quarter-turn matrix rotation | grid / matrix operations | medium | analysis | PASS |
| t23 | Count enclosed open-regions | grid / matrix operations | medium | analysis | PASS |
| t24 | Deterministic region labeling by value | grid / matrix operations | hard | analysis | PASS |
| t25 | Reachable nodes in a directed graph | small-graph basics | easy | analysis | PASS |
| t26 | Deterministic topological order | small-graph basics | medium | analysis | PASS |
| t27 | Find a cycle in a directed graph | small-graph basics | medium | analysis | PASS |
| t28 | Topological generations (longest-path layers) | small-graph basics | hard | analysis | PASS |
| t29 | Alternating Digit Weight Signature | integer math & number representations | easy | analysis | PASS |
| t30 | Factorial-Base (Factoradic) Conversion | integer math & number representations | medium | analysis | PASS |
| t31 | Positional Residue Divisibility | integer math & number representations | medium | analysis | PASS |
| t32 | Balanced Ternary Codec and Addition | integer math & number representations | hard | analysis | PASS |
| t33 | Roster multi-key ordering | sorting & ranking with custom multi-key rules and explicit tie-breaking | easy | analysis | PASS |
| t34 | Contest standings competition ranking | sorting & ranking with custom multi-key rules and explicit tie-breaking | medium | analysis | PASS |
| t35 | Configurable multi-key sort | sorting & ranking with custom multi-key rules and explicit tie-breaking | medium | analysis | PASS |
| t36 | League table with head-to-head tie-break | sorting & ranking with custom multi-key rules and explicit tie-breaking | hard | analysis | DROPPED |
| t37 | Threshold Run-Length Encoding | encoding/decoding schemes | easy | analysis | PASS |
| t38 | Escaped Field Framing | encoding/decoding schemes | medium | analysis | PASS |
| t39 | Byte-Stuffed Frame Splitter | encoding/decoding schemes | medium | analysis | PASS |
| t40 | Two-Tier Run-Length Codec | encoding/decoding schemes | hard | analysis | PASS |
| t41 | Longest above-threshold run | sliding-window & sequence statistics | easy | analysis | PASS |
| t42 | Rolling window range | sliding-window & sequence statistics | medium | analysis | PASS |
| t43 | Rolling baseline anomaly flags | sliding-window & sequence statistics | medium | analysis | PASS |
| t44 | Windowed monotone streak scanner | sliding-window & sequence statistics | hard | analysis | PASS |
| t45 | Deepest leaf level in a category tree | tree structures as nested dicts/lists | easy | analysis | PASS |
| t46 | Prune a file-system tree by depth with empty-dir collapse | tree structures as nested dicts/lists | medium | analysis | PASS |
| t47 | First pre-order root-to-node path matching a tag | tree structures as nested dicts/lists | medium | analysis | PASS |
| t48 | Wildcard path query over nested dicts and lists | tree structures as nested dicts/lists | hard | analysis | PASS |
| t49 | Positional Divergence Score | text metrics & comparison | easy | pilot | PASS |
| t50 | Longest Shared Run | text metrics & comparison | medium | pilot | PASS |
| t51 | Capped Keystroke Distance | text metrics & comparison | medium | pilot | PASS |
| t52 | Recursive Block Similarity | text metrics & comparison | hard | pilot | PASS |
| t53 | Single Elevator Trip Log | small discrete simulations | easy | pilot | PASS |
| t54 | Warehouse Bin Simulation | small discrete simulations | medium | pilot | PASS |
| t55 | Token-Passing Ring | small discrete simulations | medium | pilot | PASS |
| t56 | Elevator Bank Dispatch | small discrete simulations | hard | pilot | PASS |

## Drop list

- **t36** — verdict=FAIL. A plausible sneaky-wrong solution that accumulates head-to-head points only from the HOME team's perspective passes all 14 hidden tests. The suite never exercises a tie decided by an AWAY team's head-to-head win, so a home-only h2h implementation slips through. The task's discriminating power is therefore incomplete; excluded from the oracle set until the hidden suite adds an away-team-h2h-decided tie case.

## Provenance

This is **ledger revision 2**.

- **Revision 1** censused all 56 dirs and dropped **t32, t33, t36, t37, t38** for missing `verdict.json`. A prior verifier had *claimed* verdicts for these tasks without writing them to disk — claims are not receipts, so revision 1 (correctly) treated missing verdicts as DROPPED.
- **Revision 2** (this ledger): t32, t33, t36, t37, t38 were re-verified from scratch and now carry fresh `verdict.json` files on disk. Four of them (t32, t33, t37, t38) verify PASS and were freshly smoked through the harness this run; they are promoted from DROPPED to PASS. **t36 verifies FAIL on its merits** (see drop list) and remains DROPPED — this time for a substantive coverage gap, not a missing file. All other 51 previously-PASS tasks retained their recorded smoke times.

Net change rev1 → rev2: dropped count fell from 5 to 1; PASS count rose from 51 to 55.

## Harness convention

Every task is verified in an isolated fresh temp dir (a new `mktemp -d` per run). **pytest is never run inside a task dir.**

```
WORK=$(mktemp -d)
cp <task_dir>/hidden_tests.py "$WORK"/
cp <candidate>.py "$WORK"/solution.py
cd "$WORK" && python -m pytest -q hidden_tests.py   # exit 0 = pass
```

`hidden_tests.py` imports the module `solution`, so the candidate file is copied in as `solution.py`. Smoke verification copies each PASS task's `reference_solution.py` in as the candidate; all exited 0. Newly-PASS tasks smoked this run: t32 (0.17s, 13 passed), t33 (0.14s, 12 passed), t37 (0.15s, 15 passed), t38 (0.15s, 13 passed). Prior-PASS tasks kept their recorded smoke times.

## Oracle-run rule

**ONLY ledger-PASS tasks feed the oracle run.** Any task marked DROPPED in `VERIFICATION_LEDGER.json` (missing verdict.json, non-PASS verdict, smoke failure, or incomplete 5-file set) is excluded from the oracle set. Currently only **t36** is excluded.
