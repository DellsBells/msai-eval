"""Agreement statistics — the correct ones for LLM-judge data.

These are robust to the things that break naive Gage R&R on rubric scores:
Krippendorff's alpha handles missing data, any number of judges, and ordinal
scales; ICC(2,1) is the absolute-agreement intraclass correlation; weighted
kappa is for the two-judge case. All validated against textbook reference values
in the test suite.
"""
from __future__ import annotations
import numpy as np


# ─── Krippendorff's alpha ────────────────────────────────────────────

def krippendorff_alpha(reliability_data, level: str = "ordinal") -> float:
    """reliability_data: 2D array (raters x units), np.nan = missing rating.

    level in {"nominal", "interval", "ordinal"}.
    Returns alpha in (-inf, 1]. 1 = perfect agreement, 0 = chance, <0 = systematic
    disagreement. Validated against Krippendorff's canonical example.
    """
    data = np.asarray(reliability_data, dtype=float)
    obs = data[~np.isnan(data)]
    if obs.size == 0:
        return float("nan")
    values = np.unique(obs)
    V = len(values)
    if V == 1:
        return 1.0  # everyone gave the identical value to everything
    vidx = {v: i for i, v in enumerate(values)}

    # coincidence matrix over pairable values within each unit (column)
    o = np.zeros((V, V))
    for u in range(data.shape[1]):
        col = data[:, u]
        col = col[~np.isnan(col)]
        m_u = len(col)
        if m_u < 2:
            continue
        idx = [vidx[v] for v in col]
        for a in range(m_u):
            for b in range(m_u):
                if a != b:
                    o[idx[a], idx[b]] += 1.0 / (m_u - 1)

    nv = o.sum(axis=1)         # value marginals
    n = nv.sum()
    if n < 2:
        return float("nan")

    def delta2(a: int, b: int) -> float:
        if level == "nominal":
            return 0.0 if a == b else 1.0
        va, vb = values[a], values[b]
        if level == "interval":
            return float((va - vb) ** 2)
        if level == "ordinal":
            lo, hi = (a, b) if a <= b else (b, a)
            s = nv[lo:hi + 1].sum() - (nv[a] + nv[b]) / 2.0
            return float(s ** 2)
        raise ValueError(f"unknown level {level!r}")

    Do = 0.0
    De = 0.0
    for a in range(V):
        for b in range(V):
            d = delta2(a, b)
            Do += o[a, b] * d
            De += nv[a] * nv[b] * d
    Do /= n
    De /= n * (n - 1)
    if De == 0:
        return 1.0
    return float(1.0 - Do / De)


# ─── ICC(2,1): two-way random, absolute agreement, single rater ──────

def icc_2_1(matrix) -> float:
    """matrix: subjects x raters, complete (no NaN). Shrout-Fleiss ICC(2,1).

    Validated against Shrout & Fleiss (1979) Table example (expected ~0.29).
    """
    M = np.asarray(matrix, dtype=float)
    if np.isnan(M).any():
        raise ValueError("ICC requires a complete subjects x raters matrix (no missing).")
    n, k = M.shape
    if n < 2 or k < 2:
        return float("nan")
    grand = M.mean()
    row_means = M.mean(axis=1)
    col_means = M.mean(axis=0)
    SSR = k * np.sum((row_means - grand) ** 2)          # between-subjects
    SSC = n * np.sum((col_means - grand) ** 2)          # between-raters
    SST = np.sum((M - grand) ** 2)
    SSE = SST - SSR - SSC                                # residual
    MSR = SSR / (n - 1)
    MSC = SSC / (k - 1)
    MSE = SSE / ((n - 1) * (k - 1))
    denom = MSR + (k - 1) * MSE + (k / n) * (MSC - MSE)
    if denom == 0:
        return float("nan")
    return float((MSR - MSE) / denom)


# ─── Weighted kappa (2 raters) ───────────────────────────────────────

def weighted_kappa(r1, r2, weights: str = "quadratic") -> float:
    """Cohen's weighted kappa for two raters over ordinal integer categories."""
    a = np.asarray(r1, dtype=float)
    b = np.asarray(r2, dtype=float)
    mask = ~(np.isnan(a) | np.isnan(b))
    a, b = a[mask], b[mask]
    if a.size == 0:
        return float("nan")
    cats = np.unique(np.concatenate([a, b]))
    c2i = {c: i for i, c in enumerate(cats)}
    K = len(cats)
    if K == 1:
        return 1.0
    O = np.zeros((K, K))
    for x, y in zip(a, b):
        O[c2i[x], c2i[y]] += 1
    O /= O.sum()
    r = O.sum(axis=1)
    c = O.sum(axis=0)
    E = np.outer(r, c)
    W = np.zeros((K, K))
    for i in range(K):
        for j in range(K):
            if weights == "quadratic":
                W[i, j] = (i - j) ** 2 / (K - 1) ** 2
            else:  # linear
                W[i, j] = abs(i - j) / (K - 1)
    num = (W * O).sum()
    den = (W * E).sum()
    if den == 0:
        return 1.0
    return float(1.0 - num / den)


# ─── Raw agreement + dispersion ──────────────────────────────────────

def percent_agreement(matrix) -> dict:
    """matrix: raters x units. Mean pairwise exact-agreement rate and mean
    absolute difference across all rater pairs on commonly-rated units."""
    M = np.asarray(matrix, dtype=float)
    R = M.shape[0]
    exact, absdiff, npairs = [], [], 0
    for i in range(R):
        for j in range(i + 1, R):
            mask = ~(np.isnan(M[i]) | np.isnan(M[j]))
            if mask.sum() == 0:
                continue
            a, b = M[i, mask], M[j, mask]
            exact.append(np.mean(np.isclose(a, b)))
            absdiff.append(np.mean(np.abs(a - b)))
            npairs += 1
    return {
        "exact_agreement": float(np.mean(exact)) if exact else float("nan"),
        "mean_abs_diff": float(np.mean(absdiff)) if absdiff else float("nan"),
        "rater_pairs": npairs,
    }


# ─── Bootstrap CI over units (the resampling unit is the item) ───────

def bootstrap_ci(func, matrix, n_boot: int = 2000, seed: int = 0, alpha: float = 0.05):
    """Percentile CI for a statistic computed on a raters x units matrix,
    resampling UNITS (columns) with replacement. Returns (lo, hi)."""
    M = np.asarray(matrix, dtype=float)
    n_units = M.shape[1]
    rng = np.random.default_rng(seed)
    stats = []
    for _ in range(n_boot):
        cols = rng.integers(0, n_units, n_units)
        try:
            v = func(M[:, cols])
            if np.isfinite(v):
                stats.append(v)
        except Exception:
            continue
    if len(stats) < 20:
        return (float("nan"), float("nan"))
    lo = float(np.percentile(stats, 100 * alpha / 2))
    hi = float(np.percentile(stats, 100 * (1 - alpha / 2)))
    return (lo, hi)
