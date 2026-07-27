# llm_judge adapter — design notes from the first real-world review (KB #018)

*Public copy: vendor identity and personal names are redacted; technical content is unchanged.*

*2026-07-03, rev-lane. Three exhibits from the attended review of real production calibration records (vendor withheld),
translated into port requirements BEFORE the build (per the operator's queue #2). The adapter
(`domains/llm_judge.py`, gage-assay) is built after gauge commit B lands, against the
typed two-band contract frozen in REV-LANE #009.*

## Exhibit 1 → THE NULL PATH (their "blank Result exports as Fail")

Their exporter coerced absent results into failures — phantom Fails that both invented
findings AND inflated real findings' windows. Our equivalents: a judge returning empty/
garbage text, `parse_rating` → NaN, a null score cell, a dead judge.

**Requirements:**
- Rating ingest is three-way, never two-way: VALID SCORE / EXCLUDED-AND-DISCLOSED /
  REFUSE-THE-RUN (when null-rate exceeds a declared threshold — a panel that won't answer
  is not a panel). A null NEVER becomes a score, a Fail, or a silent drop.
- Null counts are per-judge and per-tier, printed on every output (the certificate now
  discloses them — landed with its ledger test, commit "null-path accounting").
- STATUS: renderer done; package-level ingest audit rides gauge commit B or the adapter.
**Tests to write:** `test_null_never_coerces`, `test_null_disclosure_matches_evidence`
(landed for the renderer), `test_null_rate_refusal_threshold`.

## Exhibit 2 → TWO-GATE DRIFT ("a trend the noise can explain is not a trend")

Their A3 called boundary jitter "steadily rising" (slope 7e-5/yr through ±5e-4 wobble);
the two-gate fix — meaningful-drift floor AND total-trend-must-outrun-scatter-2x — killed
~80% of drift findings as named refusals, and the first surviving finding human-verified
as real.

**Requirements for judge-drift (stability.py + adapter A3 analog):**
- Gate 1: declared meaningful floor (≥X% of the rating scale span per unit time; X declared
  pre-run, printed).
- Gate 2: |total trend over window| ≥ 2× observed scatter, or the verdict is a NAMED
  refusal ("trend within noise floor"), not a drift finding.
- Composes with REV-007's baseline fix; both gates print their numbers (P10).
**Tests:** synthetic boundary-jitter series MUST NOT alarm; injected real ramp MUST;
refusal carries both gate values.

## Exhibit 3 → PER-EVENT PROVENANCE on exposure metrics (window inflation)

One phantom Fail in their series inflated a REAL finding's window from ~358d to 901d —
corruption of magnitude on true findings, not just false positives.

**Requirements for A4-analog (eval-recall windows — "judge failed re-qual → flag verdicts
since last-known-good"):**
- Every window/aggregate carries the IDs of its contributing events; removing one event
  recomputes affected magnitudes deterministically (and ONLY those).
- Suspect-window reports list the boundary events by ID so a reviewer can check the two
  records that define the window — that's what made their human review 90 minutes instead
  of 90 hours.
**Tests:** `test_window_provenance_ids_present`, `test_single_event_removal_localizes`.

## Standing inputs the adapter consumes (contract refs)
- Two-band fields: `estimate_U` (Band A), `guard_band` (Band B), `bands{}`, `declared_use`
  (REV-LANE #009; frozen from GAUGE #002).
- `resolution_verdict{state, U, U_lo, U_hi, nu_eff, p_beyond, dof_mode, state_dominant}`
  (post fold-in).
- Instrument identity = model+version+prompt-hash (blueprint §6, two-band amendment);
  version bump = renewal event (censoring machinery unchanged).
- Liability tier: adapter outputs that someone RUNS (eval-harness configs) are
  Foundry-class (PATTERN_LANGUAGE liability note) — do-not-ship banner until reviewed.
