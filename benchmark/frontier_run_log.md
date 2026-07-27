# Frontier keystone run — log & deviations

## Run (2026-07-02)
- **Panel (4 lineages):** openai `gpt-5.5`, xai `grok-4.3`, gemini `gemini-3.1-pro-preview`, claude `claude-opus-4-8`. DeepSeek deferred (5th lineage, pending).
- **Design:** `keystone_ladder(n=10, seed=0)` — identical 60 responses to the chat-window R=2 run (direct comparability). 3 tiers × 10 pairs × 2 configs × R=3 × 4 judges = **720 calls, $1.82, 0 API failures**. Blind self-contained 1–5 rating, one response per call.
- **Raw scores:** `frontier_api_scores.json`. Re-analyze with `frontier_reanalyze.py` (zero spend).

## Result (four-state verdict)

### J=4 (openai, xai, gemini, claude) — first API run
- resolve → AT-EDGE (P(Δ>U)=0.90); subtle → AT-EDGE, leaning below (P≈0.16–0.22); tie → BELOW (P≈0.02).
- Chat R=2 run (claude/codex/gemini) under the same metric: resolve RESOLVED, subtle RESOLVED (P≈0.90), tie WITHIN-NOISE.
- The J=4 API run and the chat run disagree on subtle. Cause localized by the gauge: the chat panel agreed tightly on subtle (small between-judge term → tight band → cleared); the more diverse API panel disagreed (wider band → at-edge). Panel-composition effect: **more lineage diversity → wider resolution band.**

### J=5 (added deepseek `deepseek-v4-pro`) — AUTHORITATIVE
- resolve → **RESOLVED** (Δ+2.25, U 1.40, P(Δ>U)=0.99; WS). Adding the 5th lineage tightened the gauge (νeff 10→20) and promoted resolve from AT-EDGE to clean RESOLVED — exactly the harness's "prefer ≥5 judges" effect.
- subtle → **AT-EDGE** (Δ+1.37, U 1.48, P(Δ>U)=0.30) — **robust to the dof choice** (WS and dominant-dof both AT-EDGE) and at the harness's recommended J≥5. DeepSeek rated the subtle "chosen" items lower than Claude (e.g. subtle/pair9: DeepSeek 1 vs Claude 4), widening reproducibility and holding subtle at the edge rather than tipping it.
- tie → **BELOW** (Δ−0.60, U 1.33, P(Δ>U)=0.00).
- **Endgame read:** on 5 frontier lineages under the four-state metric — big gap RESOLVED, subtle gap AT-EDGE (can't force a side; the gauge's own uncertainty overlaps the gap), sham BELOW. The keystone 3-tier pattern reproduces at frontier scale with metrologically-correct resolution. The chat run's "subtle RESOLVED" is the artifact of a smaller, less diverse panel that got lucky-tight; the diverse J=5 panel is the honest gauge. Definitional-uncertainty framing (Fable): the subtle tier was built at the construct's ambiguity zone, so AT-EDGE is the *correct* report, not a defect. Still PILOT-PASSED (consensus-anchored, no external ground truth; accuracy anchor is the parked next project).
- **Total spend, whole frontier program:** $1.82 (J=4) + $0.41 (deepseek) + ~$0.45 (accidental re-run) + refills ≈ **$2.7 all-in.**

## Deviations from pre-registration
1. **Tie tier.** Pre-registered prediction: within-noise. **API run got "statistically real but BELOW resolution" (Δ=−0.58, negative lean); chat run got within-noise as predicted.** So the deviation is API-panel-specific. The gauge behaved correctly — it refused to certify the magnitude (below resolution in both metrics). A small negative lean on the 0.33-margin sham pairs is plausibly the consensus anchor being arbitrary on those items, not a panel defect. **Action: watch at scale (J=5 and larger n).**

## Data-quality notes
2. **One null cell, honestly re-measured (NOT imputed).** `subtle / pair 9 / chosen / claude / rep 1` returned an unparseable (empty) response at `max_tokens=16`. It was **re-called against the live API**, not imputed: attempt 0 returned empty again (confirming the failure mode), attempt 1 returned a clean `4` — a genuine measured value, matching the cell's other two reps `[4,4]`. Within-cell variance is real, not deflated.
3. **`max_tokens` bumped 16 → 32** for the Claude judge (`CLAUDE_MAX_TOKENS`) to eliminate the occasional empty-response failure mode. Applies to future runs (incl. DeepSeek).
3b. **Two DeepSeek null cells, also honestly re-measured (NOT imputed).** `subtle/pair9/chosen` and `tie/pair4/rejected` returned empty on rep 0 (same failure mode); both re-called live and returned clean values (1.0 and 5.0) matching their cells' other two reps. Genuine measurements, within-cell variance intact.

## Metric change (Bucket 2)
4. **Four-state resolution verdict** added (`resolution_verdict.py`): WITHIN-NOISE / BELOW / AT-EDGE / RESOLVED, where the edge zone is U's own confidence interval derived from the effective dof (not an ad-hoc margin). Continuous disclosure line: P(|Δ| > U), folding in both Δ's and U's sampling uncertainty.
   - **Open contract decision for Fable:** which dof drives U's CI — the Welch-Satterthwaite combined νeff (GUM-standard, but comes out 9–92 here because well-estimated repeatability inflates it; makes bands tight) or the dominant between-judge component's dof (conservative, matches the harness's "small-panel U unstable" warning and Fable's "dof≈3" intuition)? Within each frontier run the subtle verdict is robust to this choice; only the chat *resolve* tier flips (RESOLVED under WS, AT-EDGE under dominant). Recommendation: WS νeff for the state (dominant-dof over-flags large gaps as at-edge), with an explicit "provisional — J<5, band unstable" flag on any RESOLVED/BELOW at small panels.

## Infra note
5. `frontier_api_run.py` was refactored under an `if __name__ == "__main__"` guard after an earlier `import frontier_api_run` accidentally re-triggered the full sweep (~$0.45 wasted, no data lost — the killed run died before its save). Helpers are now safely importable; the run only executes as a script.

## Contract status
6. **dof contract RATIFIED: WS νeff** for the four-state state, with the standing **provisional-J<5** flag. The fold-in into `compare()` (after which `certificate.py` swaps to the package import) is the remaining engineering step — **not yet landed** (deferred as core-module surgery deserving a dedicated ledger-disciplined pass).

## Security close (2026-07-02)
7. **`benchmark/.env` deleted** — verified absent from disk.
8. **No key material ever entered git history** — verified: a history scan for all five key fragments (xAI / OpenAI `sk-proj-` / Anthropic `sk-ant-` / DeepSeek / Gemini) returns nothing on any commit, and `.env` was gitignored from creation and never tracked. The only key-shaped strings in the tree are the **placeholder** examples in the API setup doc (private repo), not real keys. *(Public releases ship as fresh-history snapshots; this attestation covers the private working repo, where the scan ran.)*
9. **Provider keys revoked by the operator at each provider console** (OpenAI, xAI, Gemini, Anthropic, DeepSeek) — **operator-confirmed 2026-07-02**. The five keys had been pasted into the working session; with revocation complete they are dead.
