"""Tests for record-normalization edge cases in data.py."""
import pytest

import msai_eval as msai


def test_nan_score_raises_not_silent_category():
    # REV-008: a NaN score must NEVER become a nominal 'nan' category or silently poison a numeric
    # matrix — it must raise a clear error for every level, telling the caller to omit the missing cell.
    rows = [{"item": "i1", "judge": "j1", "score": float("nan")},
            {"item": "i1", "judge": "j2", "score": 3},
            {"item": "i2", "judge": "j1", "score": 2},
            {"item": "i2", "judge": "j2", "score": 4}]
    for level in ("interval", "ordinal", "nominal"):
        with pytest.raises(ValueError, match="NaN"):
            msai.reliability(rows, level=level)
