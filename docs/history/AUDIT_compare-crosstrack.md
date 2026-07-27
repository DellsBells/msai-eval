# Audit — `compare()` ↔ v0.7.0 cross-track (from the compression/gauge session)

*msai-eval v0.7.0 · 2026-06-25. Requested by the metrology-modules track. Angles taken are the
ones where gauge/compression context is the expertise; I did **not** re-audit the new modules'
internals (correctness/edge-cases) — that's your audit. Everything below is verified against the
code and, where it matters, against runnable receipts.*

## Bottom line

- **compare.py is honest and correct as it stands** (15/15 tests pass). One real finding — a mean-Δ
  vs Cliff's-δ tension — **I fixed in-file** (it's my lane); details in §1.
- **The headline cross-track finding (§2): `compare()`'s guard band should adopt
  `uncertainty_budget()`'s expanded `U` — with two non-negotiable guards.** It's *more* honest
  (adds the quantization floor + honest small-panel coverage) and, verified empirically, can only
  ever *widen* the within-noise zone — it can never turn a "within noise" into a confident finding.
  But naive adoption reintroduces an overclaim, so it needs guarding. **This one needs your sign-off**
  because it makes `compare.py` depend on `uncertainty.py` — I did not land it unilaterally.
- **u_ref does NOT belong in the pairwise guard band (§3)** — it's common-mode in a config-vs-baseline
  delta and cancels. The reference's right role in `compare()` is a `fitness()` *precondition gate*,
  not a widening term. u_ref enters the accept zone only at the absolute-reference/threshold boundary
  (that's `conformity.py`).

---

## §1 — Self-audit of `compare.py`  (verdict: honest; one fix landed)

| Concern | Verdict | Notes |
|---|---|---|
| ndc decoupling / guard-band qualification | **clean** | Qualification (`compare.py:226`) keys only on `(k≥2) and (not deterministic) and (guard_band is not None)`. ndc has no path back into `qualified` — advisory warning only. All three real "can't tell" states (single judge, frozen, no replicates) force `qualified=False`. |
| Holm correction | **clean** | Correct monotone step-down; passes 20k randomized property checks + a manual tie example `[0.02,0.02,0.04]→[0.06,0.06,0.06]`. NaN p-values coerced to 1.0 before Holm, so they can't manufacture significance. |
| "within noise" wording | **clean** | Never paraphrased as lossless/equivalent; the SCOPE note explicitly disowns that reading and distinguishes it from "statistically real but BELOW gauge resolution." |
| Cliff's δ vs mean Δ | **FIXED** (was a real minor tension) | See below. |

**The fix.** The verdict's direction word and significance gate were both driven by the **mean** Δ,
while the notes tell users to **trust Cliff's δ** on ordinal data. On asymmetric-magnitude ordinal
data these can disagree in *sign* (constructed: per-cell `[4,4,4,4,1,1]` vs baseline `3` → mean Δ
= −0.20 "drop", but Cliff's δ = +0.20, config ranks *better*). The interval-spacing caveat was printed
but not wired into the verdict, so the headline could assert a directional "drop" the endorsed effect
size contradicts.

Wired a guard into `_verdict()`: on ordinal/nominal, when a **confident directional** verdict is about
to be asserted (`significant_adj`) but Cliff's δ points the opposite way with real magnitude
(`|δ|≥0.1`, opposite sign), the direction is **withheld** — reported as *"statistically real
difference, but mean Δ and rank-effect (Cliff's δ) DISAGREE in sign — interval-spacing assumption
suspect; direction not trustworthy."* within-noise makes no directional claim, so it's untouched;
interval level is untouched (the mean is the right tool there). New test
`test_verdict_withholds_direction_when_mean_and_cliffs_disagree`; suite 15/15.

---

## §2 — Reconcile the guard band with the GUM budget  (the high-value one)

**Confirmed against code.** With `grr_sd = sqrt(σ²_repeat + σ²_int + σ²_judge)` (`variance.py:65,94`):

```
compare() guard band   = 2 · grr_sd
uncertainty_budget() U = k_WS · sqrt( grr_sd²  +  Δ²/12  +  u_ref² )      (uncertainty.py:181,188-191)
```

They are the **same resolution concept**, but the guard band drops two terms:
1. **the score-quantization floor `Δ/√12`** (≈0.289 on a 1–5 scale), and
2. **honest coverage** — it uses a flat `k=2` instead of a Welch-Satterthwaite `k` that is *larger*
   on a small panel (3 judges → dof≈2 → k≈4.3).

Both omissions make the guard band **too narrow**, so `compare()` can stamp *"REAL drop beyond gauge
resolution"* on a difference that's actually inside the honest expanded uncertainty — an overclaim,
and it bites hardest exactly where we operate: **sharp gauges and small panels chasing sub-point
frontier deltas.** When `grr_sd` is small, the `Δ/√12` floor *dominates*, and the bare `2·grr_sd`
band pretends to a resolution the 1–5 rubric physically can't deliver.

### Verdict: **adopt `U` as the guard-band magnitude — with two guards.**

Why it's safe (empirically verified, §4): in the realistic small-panel regime (eff-dof ≤ 60, so
k ≥ 2.0) `U ≥ 2·grr_sd` **always** — quantization only adds in quadrature. So swapping in `U` only
ever *widens* the within-noise zone; it **cannot** convert a "within noise" into a confident "REAL"
verdict. The quantization double-count (grr, computed from already-integer scores, partly reflects
quantization; adding `Δ²/12` again slightly over-counts) is in the **conservative/safe** direction —
it never lets a sub-resolution difference read as resolved.

**Guard A (mandatory — or you reintroduce an overclaim).** Qualification must stay gated on the
**Type-A gauge noise actually being measured**, *not* on "U is finite." Receipt: a no-replicates
design returns `variance_components → None` yet `uncertainty_budget` still yields `U = 0.566` **from
quantization alone**, and the `deterministic` flag does **not** fire (vc is None). A rule keyed on
"U finite" would *falsely qualify* a gauge whose noise was never characterized. Keep the gate on
`vc and vc["grr_sd"] > 0` (and `not deterministic`, `k≥2`).

**Guard B (cheap insurance).** There is a narrow corner — eff-dof ≥ 120 *and* `grr_sd > 1.42` on a
1–5 scale (an already-failing gauge with a huge panel) — where `k_WS → 1.96` makes `U` up to ~2%
*narrower* than `2·grr_sd`. Floor it: `guard_band = max(U, 2·grr_sd)` so the new band is never less
conservative than the legacy one. (Academic in practice; costs nothing.)

### Proposed change (your call to land — it adds a `compare.py → uncertainty.py` dependency)

```python
# in compare()'s gauge block, replacing:  guard_band = guard_k * grr_sd if grr_sd>0 else None
if vc and vc["grr_sd"] > 0:                          # Type-A gauge noise actually measured
    U = uncertainty_budget(ds, level=level).U        # GUM expanded U: adds Δ/√12 + Welch-Satterthwaite k
    gauge["guard_band"] = max(U, guard_k * vc["grr_sd"])   # Guard B: never narrower than legacy
else:
    gauge["guard_band"] = None                       # frozen-perfect or no replicates -> resolution unmeasured
# qualification expression UNCHANGED -> Guard A holds for free (guard_band is None exactly when
# grr_sd==0 or vc is None, i.e. Type-A noise was not measured).
# NOTE: NO reference passed here -> u_ref term omitted on purpose (see §3).
```

This unifies the two tracks on one resolution number (your handoff already calls `U` "the principled
version of your guard band") and makes the budget's per-source breakdown the natural drill-down when a
config reads "within noise."

---

## §3 — Should `compare()` consume a `Reference` (u_ref)?

**Not into the guard band, for the current pairwise job.** `compare()` measures config − baseline,
both scored by the same panel on the same scale; the reference value (and its u_ref) is **common-mode
and cancels in the difference**. Folding `u_ref` into a *pairwise* guard band would over-widen for the
wrong reason — it answers "can I resolve this vs absolute truth?", not "vs the baseline config?" This
is why the proposed §2 change calls `uncertainty_budget(ds)` **without** a reference.

**But the reference has a real role: a `fitness()` precondition gate.** A "within noise" verdict that's
meant to stand in for "as good as baseline" is only meaningful if the gauge (and any reference truth)
can actually arbitrate. Recommendation: `compare(..., reference=None)` — when supplied, run
`ref.fitness(grr_sd)` and surface its verdict as a gauge warning. If the reference is **UNFIT**
(noisier than the gauge, TUR < 1:1), flag that accuracy-flavored verdicts are meaningless regardless
of the CI. Receipt (§4): the three-band fitness check works exactly on the 4:1 boundaries.

**Where u_ref *does* widen the accept zone:** comparing a config to an **absolute reference value /
threshold** (the marketplace-outcome north star), not to a baseline config. That's a threshold
conformity decision — `conformity.py` territory — and there `score()`'s `En = d / √(U_pred²+U_ref²)`
is the right machinery. Clean boundary; documenting it here so neither track folds u_ref into the
pairwise path by reflex.

---

## §4 — Empirical receipts (synthetic config runs; `.venv/bin/python`)

- **Frontier** (good-clustered `{fp16≈4.5, q4kv≈4.45, deltakv3≈4.48}`, 6 judges × 5 trials):
  `grr_sd=0.588`, legacy guard band `2·grr_sd=1.176`, **`U=1.310`** (`k=2.0`, nu_eff≈106; split:
  repeatability 68.6% / resolution 19.4% / reproducibility 12.0%). Deltas 0.20 / 0.13 — both within
  *both* bands. **No verdict flips**; `U > 2·grr_sd`, so the swap only widens within-noise.
- **No-replicates** (1 trial/cell): `variance_components → None`, but `U=0.566` from the resolution
  term alone (100% quantization). → **Guard A proof.**
- **Frozen** (temp-0): `deterministic=True`; `U=1.187` still finite via quantization, but `compare()`
  marks everything **provisional** — the deterministic clause refuses; a finite U did not rescue it.
- **`ref.fitness(grr_sd=0.588)`:** tight `u_ref=0.074` → **FIT (8:1)**; medium `0.294` → **MARGINAL
  (2:1)**; loose `1.176` → **UNFIT (0.5:1)**. Exactly on the 4:1 / 1:1 boundaries.
- **Budget lever** (frontier + fit reference): dominant = **repeatability 68%** → lever *"lower judge
  temperature / average more trials"* — correctly **not** "more judges" (reproducibility 12%), not a
  finer rubric (resolution 19%), not a tighter reference (u_ref 1.2%). It names the right knob to
  shrink the band toward a `delta_kv`-sized difference, which is exactly the workflow your handoff
  promised.

---

## What I changed vs what's yours to land

- **Landed (my file):** the Cliff's-δ direction guard in `_verdict()` + test (§1). Suite 15/15.
- **Recommended, not landed (needs your sign-off — touches the shared resolution concept and adds a
  `compare.py → uncertainty.py` dependency):** adopt `U` as the guard-band magnitude with Guards A+B
  (§2); add an optional `reference=` to `compare()` for a `fitness()` precondition gate (§3).
- **Housekeeping:** `__version__` is `0.7.0`; my `README.md` / `HANDOFF_compression-gauge.md` still say
  older versions — I'll bump on commit. compare.py edits remain uncommitted and conflict-free with yours.

— compression/gauge session
