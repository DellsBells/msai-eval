import random

import solution


def _brute_block(a, b):
    bestk = 0
    bi = 0
    bj = 0
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            if k > bestk or (k == bestk and k > 0 and (i, j) < (bi, bj)):
                bestk = k
                bi = i
                bj = j
    return (bestk, bi, bj)


def _brute_m(a, b):
    k, i, j = _brute_block(a, b)
    if k == 0:
        return 0
    return k + _brute_m(a[:i], b[:j]) + _brute_m(a[i + k:], b[j + k:])


def _brute_sim(a, b):
    tot = len(a) + len(b)
    if tot == 0:
        return 1.0
    return round(2.0 * _brute_m(a, b) / tot, 4)


def test_both_empty():
    assert solution.block_similarity("", "") == 1.0


def test_identical_nonempty():
    assert solution.block_similarity("abc", "abc") == 1.0
    assert solution.block_similarity("hello world", "hello world") == 1.0


def test_no_overlap():
    assert solution.block_similarity("abc", "xyz") == 0.0


def test_one_empty():
    assert solution.block_similarity("abc", "") == 0.0
    assert solution.block_similarity("", "abc") == 0.0


def test_shifted_block():
    assert solution.block_similarity("abcd", "bcde") == 0.75


def test_recursive_example():
    assert solution.block_similarity("tortoise", "torso") == 0.6154


def test_asymmetric_lengths_use_sum_normalization():
    # "aaa" vs "aaaaaa": longest block "aaa" (k=3), M=3, ratio = 2*3/(3+6)=6/9
    assert solution.block_similarity("aaa", "aaaaaa") == round(6 / 9, 4)


def test_result_in_unit_interval():
    assert 0.0 <= solution.block_similarity("mississippi", "missouri") <= 1.0


def test_single_shared_char():
    # "x" vs "axb": block "x" k=1, M=1, ratio = 2*1/(1+3) = 0.5
    assert solution.block_similarity("x", "axb") == 0.5


def test_case_sensitive():
    # "ABC" vs "abc" share nothing -> 0.0
    assert solution.block_similarity("ABC", "abc") == 0.0


def test_bounds_and_identity_property():
    # For arbitrary strings the score stays in [0, 1]; and a string compared
    # with itself always scores exactly 1.0.
    rng = random.Random(31337)
    alphabet = "abab"
    for _ in range(300):
        a = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 9)))
        b = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 9)))
        v = solution.block_similarity(a, b)
        assert 0.0 <= v <= 1.0
        assert solution.block_similarity(a, a) == 1.0


def test_matches_brute_force_property():
    rng = random.Random(2718)
    alphabet = "abab"  # collisions force recursion and tie-breaks
    for _ in range(400):
        a = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 9)))
        b = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 9)))
        assert solution.block_similarity(a, b) == _brute_sim(a, b)
