import solution


def _expected(n):
    # Independent reference computation for property tests.
    s = str(n)
    total = 0
    for i, ch in enumerate(s):
        pos = i + 1
        sign = 1 if pos % 2 == 1 else -1
        total += sign * pos * int(ch)
    return total


def test_worked_example_1234():
    assert solution.digit_signature(1234) == -10


def test_worked_example_505():
    assert solution.digit_signature(505) == 20


def test_single_digit_seven():
    assert solution.digit_signature(7) == 7


def test_zero():
    assert solution.digit_signature(0) == 0


def test_all_single_digits():
    for d in range(10):
        assert solution.digit_signature(d) == d


def test_two_digits():
    # 42 -> 1*4 - 2*2 = 4 - 4 = 0
    assert solution.digit_signature(42) == 0
    # 90 -> 1*9 - 2*0 = 9
    assert solution.digit_signature(90) == 9
    # 19 -> 1*1 - 2*9 = 1 - 18 = -17
    assert solution.digit_signature(19) == -17


def test_repeated_digits():
    # 1111 -> 1 - 2 + 3 - 4 = -2
    assert solution.digit_signature(1111) == -2
    # 999 -> 9 - 18 + 27 = 18
    assert solution.digit_signature(999) == 18


def test_leading_digit_matters():
    # Position weighting is from the left, so these must differ.
    assert solution.digit_signature(120) != solution.digit_signature(210)


def test_large_number():
    n = 12345678901234567890
    assert solution.digit_signature(n) == _expected(n)


def test_property_matches_independent_reference():
    # Deterministic, seeded generation of test cases.
    import random
    rng = random.Random(20240607)
    for _ in range(300):
        n = rng.randint(0, 10 ** rng.randint(0, 18))
        assert solution.digit_signature(n) == _expected(n)


def test_property_single_digit_identity():
    # Invariant: any single digit maps to itself.
    for d in range(10):
        assert solution.digit_signature(d) == d
