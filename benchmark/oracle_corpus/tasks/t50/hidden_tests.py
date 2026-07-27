import random

import solution


def _brute(a, b):
    best = 0
    start = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a) + 1):
            sub = a[i:j]
            if sub in b and (j - i) > best:
                best = j - i
                start = i
    if best == 0:
        return (0, 0)
    return (best, start)


def test_basic_middle_run():
    assert solution.longest_shared_run("abcdef", "zzcdezz") == (3, 2)


def test_tie_prefers_earlier_start_in_a():
    assert solution.longest_shared_run("abcxyz", "xyzabc") == (3, 0)


def test_single_char_run():
    assert solution.longest_shared_run("hello", "world") == (1, 2)


def test_identical_strings():
    assert solution.longest_shared_run("same", "same") == (4, 0)
    assert solution.longest_shared_run("a", "a") == (1, 0)


def test_no_shared_chars():
    assert solution.longest_shared_run("abc", "xyz") == (0, 0)


def test_empty_inputs():
    assert solution.longest_shared_run("", "anything") == (0, 0)
    assert solution.longest_shared_run("anything", "") == (0, 0)
    assert solution.longest_shared_run("", "") == (0, 0)


def test_case_sensitive():
    # 'A' != 'a', so the only shared run is lowercase "bc"
    assert solution.longest_shared_run("Abc", "abc") == (2, 1)


def test_duplicate_run_tiebreak():
    # "aa" appears at index 0 and index 3 of a; earlier start wins.
    assert solution.longest_shared_run("aaxaa", "aa") == (2, 0)


def test_full_a_contained_in_b():
    assert solution.longest_shared_run("cat", "concatenate") == (3, 0)


def test_length_field_only():
    length, _ = solution.longest_shared_run("xxabcxx", "yyabcyy")
    assert length == 3


def test_matches_brute_force_property():
    rng = random.Random(4242)
    alphabet = "abcab"  # small alphabet forces many collisions and ties
    for _ in range(500):
        a = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 9)))
        b = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 9)))
        assert solution.longest_shared_run(a, b) == _brute(a, b)


def test_run_actually_matches_property():
    # Invariant: the reported run must genuinely be a substring of both a and b.
    rng = random.Random(7)
    alphabet = "xyz"
    for _ in range(300):
        a = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 10)))
        b = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 10)))
        length, start = solution.longest_shared_run(a, b)
        if length > 0:
            run = a[start:start + length]
            assert len(run) == length
            assert run in a
            assert run in b
