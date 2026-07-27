import solution

import pytest


def _brute(readings, k):
    n = len(readings)
    if n < k:
        return ([], -1)
    ranges = []
    for start in range(n - k + 1):
        window = readings[start:start + k]
        ranges.append(max(window) - min(window))
    peak_index = -1
    peak_value = None
    for i, r in enumerate(ranges):
        if peak_value is None or r > peak_value:
            peak_value = r
            peak_index = i
    return (ranges, peak_index)


def test_basic_example():
    assert solution.rolling_ranges([1, 3, 2, 8, 5], 3) == ([2, 6, 6], 1)


def test_flat_sequence():
    assert solution.rolling_ranges([4, 4, 4, 4], 2) == ([0, 0, 0], 0)


def test_window_larger_than_input():
    assert solution.rolling_ranges([9, 1], 3) == ([], -1)


def test_window_equals_length():
    # Exactly one window covering the whole list.
    assert solution.rolling_ranges([5, 1, 9, 3], 4) == ([8], 0)


def test_single_element_window():
    # Every window has range 0 with k == 1.
    ranges, peak = solution.rolling_ranges([3, 7, 2], 1)
    assert ranges == [0, 0, 0]
    assert peak == 0


def test_peak_in_last_window():
    # The widest-range window is the final one.
    assert solution.rolling_ranges([1, 2, 3, 1, 10], 2) == ([1, 1, 2, 9], 3)


def test_tie_prefers_earliest():
    assert solution.rolling_ranges([0, 5, 0, 5], 2) == ([5, 5, 5], 0)


def test_empty_input():
    assert solution.rolling_ranges([], 1) == ([], -1)


def test_invalid_window_zero_raises():
    with pytest.raises(ValueError):
        solution.rolling_ranges([1, 2, 3], 0)


def test_invalid_window_negative_raises():
    with pytest.raises(ValueError):
        solution.rolling_ranges([1, 2, 3], -2)


def test_float_ranges_preserved():
    ranges, peak = solution.rolling_ranges([1.0, 2.5, 2.0], 2)
    assert ranges == [1.5, 0.5]
    assert peak == 0


def test_does_not_mutate_input():
    data = [3, 1, 4, 1, 5, 9, 2]
    snapshot = list(data)
    solution.rolling_ranges(data, 3)
    assert data == snapshot


def test_property_matches_brute_force():
    import random
    rng = random.Random(4042)
    for _ in range(300):
        n = rng.randint(0, 20)
        readings = [rng.randint(-9, 9) for _ in range(n)]
        k = rng.randint(1, 8)
        assert solution.rolling_ranges(readings, k) == _brute(readings, k)
