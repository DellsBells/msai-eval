"""resolution_verdict.py — BACK-COMPAT SHIM.

The four-state implementation moved into the package (`msai_eval.resolution`) in core-pass
commit B so compare() and certificate.py share one code path. This module re-exports it so
existing benchmark scripts (frontier_reanalyze.py) that `from resolution_verdict import ...`
keep working byte-for-byte. New code should import from `msai_eval.resolution`.
"""
from msai_eval.resolution import (  # noqa: F401
    Z95,
    BAND_A_BASIS,
    BAND_B_BASIS,
    welch_satterthwaite_dof,
    dominant_typeA_dof,
    four_state,
)
