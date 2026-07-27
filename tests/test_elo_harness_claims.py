"""test_elo_harness_claims.py — permanent ledger locking the audit findings on benchmark/elo_validation.py.

Each test reproduces a finding's trigger and asserts the CORRECTED behavior the rebuild delivers. GREEN = the
fix is locked; a regression flips it red. (Audit: adversarial workflow wf_35f104c9-07a — 18 confirmed defects,
14 verdict-flipping; the measurement-model rebuild + robustness fixes close them.)

LEDGER
  parse        finding 4/9  — robust 1-5 parse (no first-digit mis-scoring)          -> test_parse_rating_robust       RESOLVED
  clone        finding 1    — clone/shared-bias panel not certified resolving        -> test_clone_panel_not_certified  RESOLVED (exact-clone; shared bias -> external tier)
  constant     finding 3    — degenerate constant judge surfaced + excluded          -> test_constant_judge_excluded    RESOLVED
  dead         (orig fix)   — all-nan judge surfaced; VOID under 2 live               -> test_dead_judge_voids           RESOLVED
  partial      finding 6/7/14 — partial-nan judge surfaced + excluded                -> test_partial_judge_surfaced     RESOLVED
  below_gate   finding 2    — 'below' tier IS gated (a resolving below-tier fails)    -> test_below_tier_is_gated        RESOLVED
  sham_qual    finding 11   — sham credited only on a QUALIFIED gauge                 -> test_sham_requires_qualified    RESOLVED
  pooling      finding 5/10/12/15/16 — heterogeneous pairs resolve (no pooling fail)  -> test_heterogeneous_pairs_resolve RESOLVED
  SHARED-BIAS LIMIT: reproducibility floor catches EXACT clones; a panel sharing a SYSTEMATIC bias (e.g. all
  length-biased) agrees genuinely, so it is caught by the external-truth adversarial 'hard' tier, not by repro.
  LADDER LIMIT (finding 9/10): length-confound + weak sham are artifacts of the hand-built ladder; the real run
  uses rewardbench_ladder() (length-balanced, adversarial-hard) + a chosen-vs-chosen zero-gap sham.
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmark"))
import elo_validation as ev


# ── judge_fn variants reproducing the failure triggers ────────────────────────────────────────────────
def honest(judge, prompt, response, q, seed):
    rng = np.random.default_rng(abs(hash((judge, prompt, response, seed))) % (2 ** 32))
    return float(np.clip(round(q + rng.normal(0, 0.4)), 1, 5))


def clone(judge, prompt, response, q, seed):        # ignores judge AND seed -> identical, deterministic
    return float(np.clip(round(q), 1, 5))


def constant(judge, prompt, response, q, seed):     # always 3 regardless of input
    return 3.0


def L():
    return ev.constructed_ladder()


# ── finding 4/9 — robust parse ────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("text,expect", [
    ("4", 4), ("4/5", 4), ("5/5 stars", 5), ("Quality: 3", 3), ("on a 1-5 scale, I rate 4", 4),
    ("8/10", None), ("10/10", None), ("3.5", None), ("I cannot rate this", None), ("", None),
    ("I rate this 4 out of 5", 4), ("4 out of 5", 4)])   # REV-005: worded out-of-5 must not grab the trailing 5
def test_parse_rating_robust(text, expect):
    v = ev.parse_rating(text)
    if expect is None:
        assert np.isnan(v), f"{text!r} should be nan, got {v}"
    else:
        assert v == expect, f"{text!r} -> {v}, expected {expect}"


# ── finding 1 — clone / shared-bias panel must NOT be certified as resolving ───────────────────────────
def test_clone_panel_not_certified():
    out = ev.validate(L(), ["a", "b", "c"], clone, R=3)
    large = out["tiers"]["large"]
    # a clone is deterministic + identical across judges -> frozen / zero-reproducibility gauge
    assert not (large.get("beyond_gauge") is True and large.get("repro_ok")), \
        "clone panel certified as resolving — the shared-bias pathology the gauge exists to catch"
    assert not out["checks"].get("large_resolves", True)


# ── finding 3 — degenerate constant judge surfaced + excluded ──────────────────────────────────────────
def test_constant_judge_excluded():
    judges = ["a", "b", "c", "stuck"]
    fn = lambda j, p, r, q, s: constant(j, p, r, q, s) if j == "stuck" else honest(j, p, r, q, s)
    res = ev.run_tier(L()[0]["pairs"], judges, fn, R=3)
    assert "stuck" in res["degenerate"], "constant (zero-variance) judge not surfaced"
    assert res["n_live"] == 3 and not res["void"]


# ── pilot fix — degeneracy check must NOT misfire on a genuinely uniform tier ──────────────────────────
def test_uniform_tier_does_not_exclude():
    # equal-quality pairs + a deterministic judge -> every judge correctly flat -> NONE degenerate (the
    # smoke-pilot bug: a uniform high-quality sham falsely excluded the whole panel and VOIDed)
    pairs = [{"prompt": f"p{i}", "chosen": "x", "rejected": "x", "q_chosen": 4, "q_rejected": 4} for i in range(3)]
    res = ev.run_tier(pairs, ["a", "b", "c"], clone, R=2)
    assert not res["degenerate"], "uniform-quality tier falsely flagged judges as degenerate (relative-check regression)"


# ── original fix — all-nan judge surfaced; VOID under 2 live ───────────────────────────────────────────
def test_dead_judge_voids():
    judges = ["a", "d1", "d2"]
    fn = lambda j, p, r, q, s: float("nan") if j.startswith("d") else honest(j, p, r, q, s)
    res = ev.run_tier(L()[0]["pairs"], judges, fn, R=3)
    assert set(res["dead"]) == {"d1", "d2"} and res["void"], "dead judges not surfaced / not VOIDed under 2 live"


# ── finding 6/7/14 — partial-nan judge surfaced + excluded ─────────────────────────────────────────────
def test_partial_judge_surfaced():
    judges = ["a", "b", "flaky"]
    # flaky nan's on every 'rejected' of the first pair -> live (valid>0) but ragged
    def fn(j, p, r, q, s):
        if j == "flaky" and q is not None and q <= 2:
            return float("nan")
        return honest(j, p, r, q, s)
    res = ev.run_tier(L()[0]["pairs"], judges, fn, R=3)
    assert "flaky" in res["partial"], "partial-dropout judge not surfaced"
    assert "flaky" not in res["dead"]


# ── finding 2 — the 'below' tier role IS gated (a resolving below-tier must FAIL) ──────────────────────
def test_below_tier_is_gated():
    ladder = L()
    ladder[1]["pairs"] = ladder[0]["pairs"]      # put a BIG-gap (resolving) set into the 'below' slot
    out = ev.validate(ladder, ["a", "b", "c"], honest, R=3)
    assert not out["checks"]["hard_real_but_below"], \
        "a resolving 'below' tier passed — pre-registered criterion #2 is ungated"


# ── finding 11 — sham credited only on a QUALIFIED gauge ───────────────────────────────────────────────
def test_sham_requires_qualified():
    out = ev.validate(L(), ["a", "b", "c"], clone, R=3)   # clone -> degenerate/frozen sham gauge
    # the sham must NOT be credited as within-noise on a collapsed gauge, and the run must not PASS
    assert out["checks"].get("sham_within_noise") is not True, \
        "sham credited as within-noise on a collapsed gauge — passes by collapse, not by a correct equal-call"
    assert not out["PASS"]


# ── finding 5/10/12/15/16 — heterogeneous-difficulty pairs RESOLVE (no false-fail from pooling) ─────────
def test_heterogeneous_pairs_resolve():
    # every pair a real +3 gap but spanning absolute difficulty; with unit=pair the between-pair spread is
    # decomposed OUT of the gauge, so this must still resolve (pre-rebuild it false-failed 'below resolution')
    def P(pr, qc, qr):
        return {"prompt": pr, "chosen": f"good-{pr}", "rejected": f"bad-{pr}", "q_chosen": qc, "q_rejected": qr}
    pairs = [P("a", 5, 2), P("b", 4, 1), P("c", 5, 2), P("d", 4, 1)]
    res = ev.run_tier(pairs, ["x", "y", "z"], honest, R=3)
    assert res["beyond_gauge"] is True, \
        f"heterogeneous real-gap tier failed to resolve (delta={res.get('delta')}, band pooling regression)"


# ── Elo re-anchor — the ladder must order by Arena-Elo gap MAGNITUDE, not RewardBench category ──────────
_RB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmark", "rewardbench_models.json")
needs_rewardbench = pytest.mark.skipif(
    not os.path.exists(_RB),
    reason="RewardBench data is not vendored (see NOTICE.md); run benchmark/fetch_rewardbench.py first")


@needs_rewardbench
def test_elo_ladder_is_magnitude_monotone():
    # direction filter (chosen higher-Elo) + null-model drop + magnitude bucketing -> a descending-gap ladder
    ladder = ev.elo_ladder(n_per_tier=6, seed=0)
    assert [t["name"] for t in ladder] == ["resolve", "mid", "below", "sham"]
    gaps = [t["mean_elo_gap"] for t in ladder[:3]]
    assert gaps[0] > gaps[1] > gaps[2] >= 0, f"Elo-gap ladder not descending by magnitude: {gaps}"
    assert ladder[3]["mean_elo_gap"] == 0, "sham tier should be zero-gap"
    assert all(t["pairs"] for t in ladder), "an Elo tier came back empty (insufficient anchored pairs)"


@needs_rewardbench
def test_elo_ladder_drops_unrated_models():
    # a pair is usable only if BOTH models carry a verified Arena Elo; unrated baselines (alpaca-7b etc.) drop
    import json
    elo = {k: v for k, v in json.load(open(ev.ARENA_ELO_JSON)).items() if not k.startswith("_")}
    rows = json.load(open(ev.RB_MODELS_JSON))
    usable = sum(1 for r in rows if elo.get(r["chosen_model"]) and elo.get(r["rejected_model"])
                 and elo[r["chosen_model"]] > elo[r["rejected_model"]])
    assert 0 < usable < len(rows), f"expected a strict subset of anchored pairs, got {usable}/{len(rows)}"
