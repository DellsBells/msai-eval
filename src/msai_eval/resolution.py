"""resolution.py — four-state resolution verdict (ILAC-G8 / ISO 14253 style).

Folded into the package in core-pass commit B (was benchmark/resolution_verdict.py, which now
re-exports from here). certificate.py and compare() both consume this single implementation, so
the four-state numbers on the certificate and the machine-readable `resolution_verdict` key that
compare() attaches to every comparison come from exactly one code path.

Binary beyond_gauge compares |Δ| against the guard band U as if U were exact. But at small
panels U is itself a noisy estimate (Welch-Satterthwaite effective dof can be ~3-10). So U has
its own confidence interval, and when |Δ| lands INSIDE that interval the gauge genuinely cannot
force a side — that is the AT-EDGE state.

States:
  WITHIN-NOISE : Δ not statistically distinguishable from 0.
  RESOLVED     : significant AND |Δ| above U's upper CI (clears the band even at its widest).
  BELOW        : significant AND |Δ| below U's lower CI (real, but under the band even at its tightest).
  AT-EDGE      : significant AND |Δ| inside [U_lo, U_hi] — at the gauge's resolution edge; no side.

U's CI comes from the fiducial distribution of a variance estimate: if u_c is estimated with
nu_eff dof, the true U = k*u_c is distributed as U_est * sqrt(nu_eff / chi2(nu_eff)). We also
report P(|Δ| > U) — the joint probability the true gap exceeds the true band, folding in BOTH
Δ's sampling uncertainty and U's — as a continuous disclosure line.
"""
import numpy as np

Z95 = 1.959964

# Frozen two-band basis strings (REV-LANE #009 contract; GC/1.1 Profile R cites these names).
BAND_A_BASIS = "VIM 2.47 — uncertainty of the estimated mean difference; shrinks ~1/sqrt(N)"
BAND_B_BASIS = ("per-use gauge discrimination (AIAG ndc family / JCGM 106 8.3.3.2 w=rU form); "
                "does not shrink with N")


def welch_satterthwaite_dof(u_c, components):
    """nu_eff = u_c^4 / sum(u_i^4 / dof_i); infinite-dof (Type B) terms contribute 0."""
    denom = 0.0
    for c in components:
        u_i = float(c["u"]); dof_i = c["dof"]
        try:
            dof_i = float(dof_i)
        except (TypeError, ValueError):
            dof_i = float("inf")
        if np.isfinite(dof_i) and dof_i > 0:
            denom += u_i ** 4 / dof_i
    if denom <= 0:
        return float("inf")
    return u_c ** 4 / denom


def dominant_typeA_dof(comps):
    """dof of the largest finite-dof (Type A) component — the poorly-estimated between-judge
    term that actually drives U's small-panel instability. This is the conservative choice."""
    best = None
    for c in comps:
        try:
            dof_i = float(c["dof"])
        except (TypeError, ValueError):
            dof_i = float("inf")
        if np.isfinite(dof_i) and dof_i > 0:
            if best is None or float(c["u"]) > best[0]:
                best = (float(c["u"]), dof_i)
    return best[1] if best else float("inf")


def four_state(delta, delta_ci, gauge, significant, n=400000, seed=0, dof_mode="ws"):
    """Return the four-state verdict dict. `gauge` is compare()'s gauge['resolution_budget'].
    dof_mode: 'ws' = Welch-Satterthwaite combined nu_eff (GUM-standard, optimistic);
              'dominant' = dof of the dominant Type-A (between-judge) term (conservative)."""
    U = float(gauge["U"])
    u_c = float(gauge["u_c"])
    comps = gauge["components"]
    nu = welch_satterthwaite_dof(u_c, comps) if dof_mode == "ws" else dominant_typeA_dof(comps)

    rng = np.random.default_rng(seed)
    if np.isfinite(nu) and nu > 0:
        U_draw = U * np.sqrt(nu / rng.chisquare(nu, n))          # fiducial dist of true U
    else:
        U_draw = np.full(n, U)
    U_lo, U_hi = (float(x) for x in np.percentile(U_draw, [2.5, 97.5]))

    lo, hi = (delta_ci if delta_ci and delta_ci[0] is not None else (delta, delta))
    d_sd = max((hi - lo) / (2 * Z95), 0.0)
    d_draw = rng.normal(delta, d_sd, n) if d_sd > 0 else np.full(n, delta)
    p_beyond = float(np.mean(np.abs(d_draw) > U_draw))

    ad = abs(delta)
    if not significant:
        state = "WITHIN-NOISE"
    elif ad >= U_hi:
        state = "RESOLVED"
    elif ad <= U_lo:
        state = "BELOW"
    else:
        state = "AT-EDGE"

    return dict(state=state, delta=delta, U=U, U_lo=U_lo, U_hi=U_hi,
                nu_eff=nu, p_beyond=p_beyond, d_sd=d_sd, significant=bool(significant))
