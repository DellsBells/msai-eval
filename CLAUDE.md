# CLAUDE.md — working on msai-eval

**MSAI (Measurement System Analysis for Intelligence)** is a metrology instrument for
LLM-as-judge evaluation: Gage R&R, guard-banded conformity, and reference/proficiency
methods applied to AI judges instead of physical gauges. The guiding principle comes from
the metrology field itself: **an AI judge earns trust only by blind comparison against an
external reference or peer panel — never by self-report.** In one line, MSAI is
*"proficiency testing for AI judges."*

## Be a metrology expert before you touch this code

This package is grounded in real metrology practice, not analogy. Before changing or
extending it, read, in order:

1. **`METROLOGY_BRIEF.md`** — what MSAI is, the seven modules (reliability `BUILT`,
   conformity `PARTIAL`; stability / reference / proficiency / uncertainty / rater_effects
   next), the build sequence, and the honesty guards that must never regress.
2. **The grounding KB** — 387 sourced claims distilled from 30 episodes of working
   metrologists, each mapped to an MSAI module with the named speaker and episode. It
   lives in a private sibling project (not in this repo); `docs/SPEC_GROUNDING.md`
   records which clauses ground which modules.

## Honesty guards — do not weaken these

MSAI's entire moat is that it refuses to overclaim. The load-bearing rules:

- **Accuracy is undefined without a traceable reference.** Never report accuracy against a
  zero-uncertainty key as if it were ground truth; carry the reference's own uncertainty.
- **A gauge that can't resolve the delta must say so** (guard band; `ndc` is *advisory
  context*, never a hard gate). "Within noise" means *below this gauge's resolution* — never
  paraphrase it as "equal" or "lossless."
- **Grading a judge against your own consensus is circular** (ChatNAPT ep12-sims-8); real
  competence needs an external, independent reference.
- **Never thread an LLM's self-reported confidence in as a calibrated σ.**
- **Don't promise per-item risk** when only a pooled, dataset-level uncertainty exists.

When in doubt, the brief and the KB index have the sourced answer.
