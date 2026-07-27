# NOTICE — third-party data and what this release does not vendor

The MIT license in `LICENSE` covers the original code and documents in this
repository. Third-party datasets are **not** vendored in the public release; the
fetch scripts below re-derive them from their sources, under those sources' own
licenses, which remain theirs:

- **RewardBench** (`benchmark/fetch_rewardbench.py`) — allenai/reward-bench,
  ODC-BY-1.0. Attribution: AllenAI, *RewardBench: Evaluating Reward Models for
  Language Modeling* (Lambert et al., 2024). Subsets carry their own upstream terms.
- **MT-Bench human judgments** (`benchmark/fetch_mtbench.py`) —
  lmsys/mt_bench_human_judgments, CC-BY-4.0. Attribution: LMSYS Org, *Judging
  LLM-as-a-Judge with MT-Bench and Chatbot Arena* (Zheng et al., 2023).
- **Chatbot Arena leaderboard snapshot** (`benchmark/fetch_arena.py`,
  `benchmark/arena_elo.json`) — factual Elo rankings from LMSYS/LMArena,
  retained as a small factual snapshot with attribution.

Model names appearing in study artifacts (gemma, qwen, minicpm-v, LFM2, llama,
and frontier API models) identify the instruments under test; no model weights or
proprietary outputs beyond study ratings are redistributed.

The oracle corpus (`benchmark/oracle_corpus/`, tasks t01–t56) is original authored
content — not derived from HumanEval, MBPP, SWE-bench, or any published benchmark.

One generated candidate solution (`benchmark/oracle_corpus/tasks/t51/solutions/`)
imports the GPL-2.0 `Levenshtein` package at runtime; the import statement is study
data (a model's answer, preserved verbatim under the sealed-corpus rule), and no GPL
code is vendored here.

Withheld from this release for copyright reasons, with sha256 hashes published in
`benchmark/entropy_arm/BANK_WITHHELD.md`: the entropy-arm evidence bank and row-level
transcripts, which embed near-verbatim text from paid standards documents
(ISO/IEC 17025, ISO/IEC 17043, AIAG MSA-4, UKAS LAB-48, Eurachem PT, JCGM/VIM).
