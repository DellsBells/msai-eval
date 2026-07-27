import random

import solution


def test_identical_strings():
    assert solution.positional_divergence("kitten", "kitten") == 0


def test_both_empty():
    assert solution.positional_divergence("", "") == 0


def test_one_empty():
    assert solution.positional_divergence("", "hello") == 5
    assert solution.positional_divergence("world", "") == 5


def test_equal_length_mismatches():
    # "kitten" vs "sitten": only index 0 differs
    assert solution.positional_divergence("kitten", "sitten") == 1
    # completely different, same length
    assert solution.positional_divergence("aaa", "bbb") == 3


def test_length_difference_trailing():
    assert solution.positional_divergence("abc", "abcd") == 1
    assert solution.positional_divergence("abcd", "abc") == 1


def test_worked_example():
    assert solution.positional_divergence("kitten", "sitting") == 3


def test_case_sensitive():
    assert solution.positional_divergence("ABC", "abc") == 3
    assert solution.positional_divergence("Abc", "abc") == 1


def test_single_char():
    assert solution.positional_divergence("x", "x") == 0
    assert solution.positional_divergence("x", "y") == 1
    assert solution.positional_divergence("x", "") == 1


def test_whitespace_counts():
    assert solution.positional_divergence("a b", "a_b") == 1


def test_trailing_whitespace_counts_as_difference():
    # Extra trailing whitespace in the longer string still counts: there is
    # nothing in the shorter string to compare it against, so each unpaired
    # trailing position contributes 1 regardless of what character it is.
    assert solution.positional_divergence("abc", "abc ") == 1
    assert solution.positional_divergence("abc ", "abc") == 1
    assert solution.positional_divergence("hi", "hi  ") == 2
    assert solution.positional_divergence("hi  ", "hi") == 2
    # A string of pure spaces vs empty: every position is unpaired.
    assert solution.positional_divergence("   ", "") == 3
    assert solution.positional_divergence("", "   ") == 3


def test_distinct_whitespace_chars_differ():
    # Comparison is exact; two different whitespace characters at the same
    # position are a difference, not a match.
    assert solution.positional_divergence(" ", "\t") == 1
    assert solution.positional_divergence("a\tb", "a b") == 1
    assert solution.positional_divergence("\t", "\t") == 0
    # Mixed: newline vs space at an overlapping position.
    assert solution.positional_divergence("x\ny", "x y") == 1


def test_never_negative():
    assert solution.positional_divergence("longer", "s") >= 0
    assert solution.positional_divergence("s", "longer") >= 0


def test_symmetry_property():
    # The metric must be symmetric: d(a, b) == d(b, a) for arbitrary strings.
    rng = random.Random(20240704)
    alphabet = "abcABC 12"
    for _ in range(300):
        la = rng.randint(0, 12)
        lb = rng.randint(0, 12)
        a = "".join(rng.choice(alphabet) for _ in range(la))
        b = "".join(rng.choice(alphabet) for _ in range(lb))
        assert solution.positional_divergence(a, b) == solution.positional_divergence(b, a)


def test_upper_bound_property():
    # Divergence can never exceed the length of the longer string.
    rng = random.Random(99)
    alphabet = "xyz"
    for _ in range(200):
        a = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 10)))
        b = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 10)))
        assert solution.positional_divergence(a, b) <= max(len(a), len(b))


def test_matches_independent_reference_property():
    # Compare against an independent reference over random strings whose
    # alphabet includes several DISTINCT whitespace characters. This exercises
    # both (a) unpaired trailing whitespace, which must count as a difference,
    # and (b) two different whitespace characters at the same position, which
    # must count as a difference (exact comparison, no normalization).
    def expected(a, b):
        n = min(len(a), len(b))
        d = sum(1 for i in range(n) if a[i] != b[i])
        return d + abs(len(a) - len(b))

    rng = random.Random(4242)
    # Multiple whitespace variants plus ordinary chars so trailing positions
    # and overlapping positions can both be whitespace.
    alphabet = "ab \t\n"
    for _ in range(400):
        a = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 12)))
        b = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 12)))
        assert solution.positional_divergence(a, b) == expected(a, b)
