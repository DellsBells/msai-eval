"""verdict_oracle.py — the FROZEN contract for compare()'s three-way resolution verdict.

Gauge-track owns this (it owns compare()._verdict). It exists for the synthetic gauge-block (modules/KB
track): the synthetic block generates data that lands Δ_true in each regime, runs the INSTALLED compare()
as a black box, and asserts report.comparisons[name]['verdict'] == expected_verdict(...). It must NOT
re-derive the verdict from a reimplementation — a reimplementation checking "|Δ|>U => REAL" would pass
while never exercising the Cliff WITHHOLD, the frozen demotion, or the beyond_gauge-None defense, silently
certifying code paths the real tool doesn't run (compare.py:_verdict, branch order 79-108).

This is an INDEPENDENT restatement of the intended semantics, not a copy of the code. The __main__
self-test asserts the real _verdict matches it across the full input grid, so:
  - if they ever diverge, either _verdict regressed OR the design contract changed — both demand a
    DELIBERATE edit here. RULE: whoever edits compare._verdict updates this oracle in the SAME commit.

The verdict is a pure function of six inputs that compare() assembles per config:
  qualified       gauge["qualified"]       — did the gauge pass (k>=2, not frozen, finite guard band)
  delta           c["delta"]               — mean(config) - mean(baseline); sign sets direction
  significant_adj c["significant_adj"]     — Holm-adjusted CI excludes 0 (the STATISTICAL gate)
  cliffs_delta    c["cliffs_delta"]        — rank effect (ordinal/nominal only); guards interval assumption
  beyond_gauge    c["beyond_gauge"]        — |delta| > guard band U (True/False), or None if U is None
  level           "interval" | "ordinal" | "nominal"
"""
from __future__ import annotations
import math

# Canonical verdict strings (the literal outputs compare() emits — assert on these exact strings).
V_UNQUALIFIED = "gauge unqualified — provisional"
V_WITHIN_NOISE = "within noise (indistinguishable on this gauge)"
V_WITHHOLD = ("statistically real difference, but mean Δ and rank-effect (Cliff's δ) DISAGREE "
              "in sign — interval-spacing assumption suspect; direction not trustworthy")
def V_UNKNOWN_RES(direction): return f"statistically real {direction} (gauge resolution unknown — no replicates)"
def V_BELOW(direction):       return f"statistically real {direction}, but BELOW gauge resolution"
def V_REAL(direction):        return f"REAL {direction} (beyond gauge resolution)"
def V_RANK_NEGLIGIBLE(direction, cd):
    return (f"statistically real {direction} beyond the interval guard band, but the rank effect "
            f"(Cliff's δ={cd:+.2f}) is NEGLIGIBLE — resolution may be an interval-spacing artifact; "
            "treat as unresolved on the rank scale")


def expected_verdict(qualified, delta, significant_adj, cliffs_delta, beyond_gauge, level):
    """The intended verdict contract, branch order load-bearing (must match compare._verdict exactly)."""
    if not qualified:
        return V_UNQUALIFIED                                   # 1. gauge can't support the comparison
    direction = "drop" if delta < 0 else "gain"
    if not significant_adj:
        return V_WITHIN_NOISE                                  # 2. statistical gate fails -> within noise
    # 3. Cliff WITHHOLD: on ordinal/nominal, if the rank effect contradicts the mean's sign with real
    #    magnitude, the interval-spacing assumption is unsafe -> withhold the DIRECTION (significant path only).
    if level in ("ordinal", "nominal") and cliffs_delta is not None and not math.isnan(cliffs_delta) \
            and abs(cliffs_delta) >= 0.1 and (cliffs_delta * delta < 0):
        return V_WITHHOLD
    # 4. resolution tier. beyond_gauge is None is a LOAD-BEARING conservative branch (no replicates / U
    #    unknown): it must fall to the cautious verdict, never past into a confident REAL.
    if beyond_gauge is None:
        return V_UNKNOWN_RES(direction)
    if beyond_gauge is False:
        return V_BELOW(direction)                              # statistically real but sub-resolution
    # 5. MAGNITUDE counterpart to the direction WITHHOLD: ordinal/nominal Δ clears the interval band but the
    #    rank effect is NEGLIGIBLE (<0.147) -> resolution may be an interval-spacing artifact -> unresolved-on-rank.
    if level in ("ordinal", "nominal") and cliffs_delta is not None and not math.isnan(cliffs_delta) \
            and abs(cliffs_delta) < 0.147:
        return V_RANK_NEGLIGIBLE(direction, cliffs_delta)
    return V_REAL(direction)                                   # 6. resolved: beyond the guard band, rank concurs


# Frozen table of canonical regions -> expected string. Each row is a region the synthetic block must hit.
# (qualified, delta, significant_adj, cliffs_delta, beyond_gauge, level) -> expected
ORACLE_TABLE = [
    ("unqualified gauge",                (False, 0.8, True,  None,  True,  "interval"), V_UNQUALIFIED),
    ("qualified, not significant",       (True,  0.8, False, None,  True,  "interval"), V_WITHIN_NOISE),
    ("sig, ordinal, Cliff disagrees",    (True,  0.8, True,  -0.4,  True,  "ordinal"),  V_WITHHOLD),
    ("sig, ordinal, Cliff agrees, REAL", (True,  0.8, True,  +0.4,  True,  "ordinal"),  V_REAL("gain")),
    ("sig, ordinal, Cliff NEGLIGIBLE (<0.147) -> unresolved-on-rank", (True, -0.8, True, +0.05, True, "ordinal"), V_RANK_NEGLIGIBLE("drop", +0.05)),
    ("sig, interval, tiny Cliff ignored -> REAL", (True, -0.8, True, +0.05, True, "interval"), V_REAL("drop")),
    ("sig, beyond_gauge None (no reps)", (True,  0.8, True,  None,  None,  "interval"), V_UNKNOWN_RES("gain")),
    ("sig, below resolution",            (True,  0.8, True,  None,  False, "interval"), V_BELOW("gain")),
    ("sig, REAL gain",                   (True,  0.8, True,  None,  True,  "interval"), V_REAL("gain")),
    ("sig, REAL drop",                   (True, -0.8, True,  None,  True,  "interval"), V_REAL("drop")),
    ("interval level ignores Cliff",     (True,  0.8, True,  -0.4,  True,  "interval"), V_REAL("gain")),
]


def _selftest():
    from msai_eval.compare import _verdict
    grid_q = [True, False]; grid_sig = [True, False]; grid_d = [-0.8, 0.8]
    grid_cd = [None, float("nan"), -0.4, 0.4, 0.05, -0.05]
    grid_bg = [None, True, False]; grid_lvl = ["interval", "ordinal", "nominal"]
    mism = 0; n = 0
    for q in grid_q:
        for sig in grid_sig:
            for d in grid_d:
                for cd in grid_cd:
                    for bg in grid_bg:
                        for lvl in grid_lvl:
                            n += 1
                            c = {"delta": d, "significant_adj": sig, "cliffs_delta": cd, "beyond_gauge": bg}
                            got = _verdict(c, {"qualified": q}, lvl)
                            exp = expected_verdict(q, d, sig, cd, bg, lvl)
                            if got != exp:
                                mism += 1
                                print(f"  MISMATCH q={q} sig={sig} d={d} cd={cd} bg={bg} lvl={lvl}\n"
                                      f"    real ={got!r}\n    oracle={exp!r}")
    print(f"\n  grid: {n} combinations, {mism} mismatches")
    # table check
    tmism = 0
    for name, args, exp in ORACLE_TABLE:
        q, d, sig, cd, bg, lvl = args
        c = {"delta": d, "significant_adj": sig, "cliffs_delta": cd, "beyond_gauge": bg}
        got = _verdict(c, {"qualified": q}, lvl)
        ok = (got == exp == expected_verdict(*args))
        print(f"  [{'OK ' if ok else 'BAD'}] {name:34s} -> {got[:48]}")
        tmism += (0 if ok else 1)
    status = "OK — oracle matches installed compare._verdict (frozen contract intact)" if (mism == 0 and tmism == 0) \
        else f"DRIFT — {mism} grid + {tmism} table mismatches; reconcile _verdict and this oracle DELIBERATELY"
    print(f"\n  {status}")
    return mism == 0 and tmism == 0


if __name__ == "__main__":
    import sys
    print("=" * 72 + "\n  VERDICT ORACLE — frozen contract self-test vs installed compare._verdict\n" + "=" * 72)
    sys.exit(0 if _selftest() else 1)
