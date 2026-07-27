import random
from functools import lru_cache

import solution


def _truth(a, b):
    @lru_cache(maxsize=None)
    def rec(i, j):
        if i == len(a):
            return len(b) - j
        if j == len(b):
            return len(a) - i
        if a[i] == b[j]:
            return rec(i + 1, j + 1)
        return min(2 + rec(i + 1, j + 1), 1 + rec(i + 1, j), 1 + rec(i, j + 1))

    v = rec(0, 0)
    rec.cache_clear()
    return v


def test_identical():
    assert solution.capped_keystroke_distance("cat", "cat", 5) == 0
    assert solution.capped_keystroke_distance("cat", "cat", 0) == 0


def test_single_substitution_costs_two():
    assert solution.capped_keystroke_distance("cat", "car", 5) == 2


def test_insert_costs_one():
    assert solution.capped_keystroke_distance("cat", "cats", 5) == 1
    assert solution.capped_keystroke_distance("cats", "cat", 5) == 1


def test_three_substitutions():
    assert solution.capped_keystroke_distance("cat", "dog", 6) == 6


def test_cap_exceeded_returns_minus_one():
    assert solution.capped_keystroke_distance("cat", "dog", 4) == -1
    assert solution.capped_keystroke_distance("cat", "dog", 5) == -1


def test_empty_strings():
    assert solution.capped_keystroke_distance("", "", 0) == 0
    assert solution.capped_keystroke_distance("abc", "", 3) == 3
    assert solution.capped_keystroke_distance("abc", "", 2) == -1
    assert solution.capped_keystroke_distance("", "abc", 3) == 3


def test_cap_zero_boundary():
    # cap 0: identical -> 0, any difference -> -1
    assert solution.capped_keystroke_distance("x", "x", 0) == 0
    assert solution.capped_keystroke_distance("x", "y", 0) == -1
    assert solution.capped_keystroke_distance("ab", "a", 0) == -1


def test_case_sensitive():
    # 'A' vs 'a' is a real substitution costing 2
    assert solution.capped_keystroke_distance("Abc", "abc", 5) == 2


def test_boundary_cap_equals_distance():
    # distance exactly at the cap must be returned, not -1
    assert solution.capped_keystroke_distance("cat", "dog", 6) == 6


def test_symmetry_property():
    rng = random.Random(2026)
    alphabet = "abcd"
    for _ in range(400):
        a = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 8)))
        b = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 8)))
        cap = rng.randint(0, 16)
        assert (
            solution.capped_keystroke_distance(a, b, cap)
            == solution.capped_keystroke_distance(b, a, cap)
        )


def test_matches_ground_truth_property():
    rng = random.Random(555)
    alphabet = "abc"
    for _ in range(400):
        a = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 7)))
        b = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 7)))
        d = _truth(a, b)
        cap = rng.randint(0, 12)
        expected = d if d <= cap else -1
        assert solution.capped_keystroke_distance(a, b, cap) == expected
