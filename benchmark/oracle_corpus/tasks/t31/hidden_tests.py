import solution


def _int_from_digits(digits, base):
    n = 0
    for dg in digits:
        n = n * base + dg
    return n


def test_worked_example_405():
    assert solution.residue_mod([4, 0, 5], 10, 7) == 6


def test_worked_example_binary():
    assert solution.residue_mod([1, 0, 1, 1], 2, 3) == 2


def test_empty_is_zero():
    assert solution.residue_mod([], 10, 9) == 0


def test_all_zeros_is_zero():
    assert solution.residue_mod([0, 0], 5, 4) == 0
    assert solution.residue_mod([0, 0, 0, 0], 2, 7) == 0


def test_single_digit():
    assert solution.residue_mod([7], 16, 5) == 2
    assert solution.residue_mod([0], 10, 3) == 0
    assert solution.residue_mod([9], 10, 10) == 9


def test_divisor_one_always_zero():
    assert solution.residue_mod([4, 0, 5], 10, 1) == 0
    assert solution.residue_mod([1, 1, 1, 1], 2, 1) == 0
    assert solution.residue_mod([], 7, 1) == 0


def test_leading_zeros_ignored():
    a = solution.residue_mod([0, 0, 4, 0, 5], 10, 7)
    b = solution.residue_mod([4, 0, 5], 10, 7)
    assert a == b == 6


def test_result_in_range():
    d = 13
    for digs in ([12, 3, 4], [1], [], [9, 9, 9, 9]):
        r = solution.residue_mod(digs, 10, d)
        assert 0 <= r < d


def test_exact_multiple_gives_zero():
    # 405 is divisible by 5 and by 9 and by 3
    assert solution.residue_mod([4, 0, 5], 10, 5) == 0
    assert solution.residue_mod([4, 0, 5], 10, 9) == 0
    assert solution.residue_mod([4, 0, 5], 10, 3) == 0


def test_property_matches_full_int_reduction():
    import random
    rng = random.Random(31313)
    for _ in range(1000):
        base = rng.randint(2, 20)
        length = rng.randint(0, 12)
        digits = [rng.randint(0, base - 1) for _ in range(length)]
        d = rng.randint(1, 97)
        n = _int_from_digits(digits, base)
        assert solution.residue_mod(digits, base, d) == n % d


def test_property_order_sensitivity():
    # A deterministic case where digit order matters, guarding against
    # accidental reversal.
    forward = solution.residue_mod([1, 2, 3], 10, 7)   # 123 % 7 = 4
    assert forward == 4
    reverse = solution.residue_mod([3, 2, 1], 10, 7)   # 321 % 7 = 6
    assert reverse == 6
