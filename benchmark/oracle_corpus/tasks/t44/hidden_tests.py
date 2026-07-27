import solution

import pytest


def _brute(readings, k):
    n = len(readings)
    if n < k:
        return (0, -1, "none")

    def stats(window):
        # Longest strictly rising / falling contiguous streak via explicit scan.
        best_up = 1
        best_down = 1
        m = len(window)
        # rising
        i = 0
        while i < m:
            j = i
            while j + 1 < m and window[j + 1] > window[j]:
                j += 1
            best_up = max(best_up, j - i + 1)
            i = j + 1 if j > i else i + 1
        # falling
        i = 0
        while i < m:
            j = i
            while j + 1 < m and window[j + 1] < window[j]:
                j += 1
            best_down = max(best_down, j - i + 1)
            i = j + 1 if j > i else i + 1
        return best_up, best_down

    best = None
    best_start = -1
    best_dir = "none"
    for start in range(n - k + 1):
        w = readings[start:start + k]
        up, down = stats(w)
        score = max(up, down)
        if up > down:
            d = "up"
        elif down > up:
            d = "down"
        else:
            d = "flat"
        if best is None or score > best:
            best = score
            best_start = start
            best_dir = d
    return (best, best_start, best_dir)


def test_example_one():
    assert solution.best_monotone_window([1, 2, 3, 1, 2], 4) == (3, 0, "up")


def test_example_two_all_falling():
    assert solution.best_monotone_window([5, 4, 3, 2, 1], 3) == (3, 0, "down")


def test_example_three_flat():
    assert solution.best_monotone_window([7, 7, 7], 2) == (1, 0, "flat")


def test_window_larger_than_input():
    assert solution.best_monotone_window([1, 2], 5) == (0, -1, "none")


def test_empty_input():
    assert solution.best_monotone_window([], 3) == (0, -1, "none")


def test_k_one_all_flat_earliest():
    assert solution.best_monotone_window([9, 3, 5, 1], 1) == (1, 0, "flat")


def test_k_equals_length_single_window():
    # One window over the whole list; strictly rising throughout.
    assert solution.best_monotone_window([1, 2, 4, 8], 4) == (4, 0, "up")


def test_equal_values_break_streak():
    # 3,3 breaks any run through it. Longest rising streak is 1<2<3 (length 3),
    # then the tie 3,3 resets it; up_len=3, down_len=1 -> score 3, "up".
    assert solution.best_monotone_window([1, 2, 3, 3, 4], 5) == (3, 0, "up")


def test_tie_score_prefers_earliest_window():
    # Windows of size 3: [3,2,1] falls (score 3, down) at start 0, and
    # [9,4,3] / [4,3,2] also reach score 3 later. Earliest (start 0) wins.
    assert solution.best_monotone_window([3, 2, 1, 9, 4, 3, 2], 3) == (3, 0, "down")


def test_direction_reported_is_chosen_window():
    # Falling window comes first with the max score, so "down" is reported even
    # though a later window rises.
    result = solution.best_monotone_window([4, 3, 2, 1, 2, 3, 4, 5], 4)
    assert result == (4, 0, "down")


def test_invalid_k_zero():
    with pytest.raises(ValueError):
        solution.best_monotone_window([1, 2, 3], 0)


def test_invalid_k_negative():
    with pytest.raises(ValueError):
        solution.best_monotone_window([1, 2, 3], -3)


def test_does_not_mutate_input():
    data = [1, 3, 2, 4, 6, 5]
    snapshot = list(data)
    solution.best_monotone_window(data, 3)
    assert data == snapshot


def test_float_values():
    # Falling 0.2>0.15>0.05 has length 3; rising only 0.1<0.2 length 2.
    assert solution.best_monotone_window([0.1, 0.2, 0.15, 0.05], 4) == (3, 0, "down")


def test_property_matches_brute_force():
    import random
    rng = random.Random(444444)
    for _ in range(400):
        n = rng.randint(0, 18)
        readings = [rng.randint(0, 4) for _ in range(n)]
        k = rng.randint(1, 8)
        assert solution.best_monotone_window(readings, k) == _brute(readings, k)
