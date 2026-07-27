import solution

import pytest


def _brute(readings, window, threshold):
    # Independent reference using the strictly-preceding window.
    flagged = []
    n = len(readings)
    for i in range(n):
        if i < window:
            continue
        prev = readings[i - window:i]
        baseline = sorted(prev)[window // 2]
        if abs(readings[i] - baseline) > threshold:
            flagged.append(i)
    return flagged


def test_basic_spike():
    assert solution.flag_anomalies([10, 10, 10, 10, 50, 10, 10], 3, 5) == [4]


def test_no_full_window():
    assert solution.flag_anomalies([1, 2, 3, 4, 5], 5, 0) == []


def test_window_one():
    assert solution.flag_anomalies([5, 5, 8, 5, 5], 1, 2) == [2, 3]


def test_empty_input():
    assert solution.flag_anomalies([], 3, 1) == []


def test_threshold_boundary_is_strict():
    # Deviation exactly equal to threshold is NOT an anomaly.
    assert solution.flag_anomalies([0, 0, 0, 5], 3, 5) == []
    # One more than the threshold flags it.
    assert solution.flag_anomalies([0, 0, 0, 6], 3, 5) == [3]


def test_first_window_never_flagged():
    # The very first `window` elements can never be anomalies.
    result = solution.flag_anomalies([100, 100, 100, 0, 0, 0], 3, 1)
    assert 0 not in result and 1 not in result and 2 not in result


def test_multiple_anomalies():
    # Baseline is the median of the three preceding readings each step.
    # i=3: median(1,1,1)=1 -> |9-1|=8 flag; i=4: median(1,1,9)=1 -> |1-1|=0;
    # i=5: median(1,9,1)=1 -> |9-1|=8 flag; i=6: median(9,1,9)=9 -> |1-9|=8 flag.
    assert solution.flag_anomalies([1, 1, 1, 9, 1, 9, 1], 3, 2) == [3, 5, 6]


def test_median_uses_middle_value():
    # Preceding window [1, 100, 1] has median 1, not the mean.
    assert solution.flag_anomalies([1, 100, 1, 2], 3, 3) == []
    assert solution.flag_anomalies([1, 100, 1, 50], 3, 3) == [3]


def test_current_reading_excluded_from_baseline():
    # If the current reading were (wrongly) part of its own baseline window,
    # the median would shift and the flag would differ. With window=3 and the
    # strictly-preceding baseline, index 3 sees median(2,2,2)=2 and |20-2|=18>3.
    assert solution.flag_anomalies([2, 2, 2, 20, 2, 2, 2], 3, 3) == [3]


def test_invalid_window_zero():
    with pytest.raises(ValueError):
        solution.flag_anomalies([1, 2, 3], 0, 1)


def test_invalid_window_even():
    with pytest.raises(ValueError):
        solution.flag_anomalies([1, 2, 3, 4], 2, 1)


def test_invalid_negative_threshold():
    with pytest.raises(ValueError):
        solution.flag_anomalies([1, 2, 3], 1, -1)


def test_does_not_mutate_input():
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    snapshot = list(data)
    solution.flag_anomalies(data, 3, 2)
    assert data == snapshot


def test_property_matches_brute_force():
    import random
    rng = random.Random(430430)
    odd_windows = [1, 3, 5, 7]
    for _ in range(300):
        n = rng.randint(0, 25)
        readings = [rng.randint(0, 30) for _ in range(n)]
        window = rng.choice(odd_windows)
        threshold = rng.randint(0, 10)
        assert solution.flag_anomalies(readings, window, threshold) == _brute(readings, window, threshold)
