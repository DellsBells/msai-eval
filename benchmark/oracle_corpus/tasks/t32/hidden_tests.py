import solution


def _from_ref(digits):
    total = 0
    for dg in digits:
        total = total * 3 + dg
    return total


def _is_canonical(d):
    if any(x not in (-1, 0, 1) for x in d):
        return False
    if d == [0]:
        return True
    if len(d) == 0:
        return False
    return d[0] != 0


def test_to_worked_examples():
    assert solution.to_balanced_ternary(5) == [1, -1, -1]
    assert solution.to_balanced_ternary(-4) == [-1, -1]
    assert solution.to_balanced_ternary(0) == [0]


def test_from_worked_examples():
    assert solution.from_balanced_ternary([1, -1, -1]) == 5
    assert solution.from_balanced_ternary([0, 0, 1]) == 1
    assert solution.from_balanced_ternary([]) == 0


def test_from_empty_and_zero():
    assert solution.from_balanced_ternary([]) == 0
    assert solution.from_balanced_ternary([0]) == 0
    assert solution.from_balanced_ternary([0, 0, 0]) == 0


def test_to_is_canonical():
    for n in range(-500, 501):
        d = solution.to_balanced_ternary(n)
        assert _is_canonical(d)


def test_add_worked_examples():
    assert solution.add_balanced_ternary([1, -1, -1], [-1, -1]) == [1]      # 5 + -4 = 1
    assert solution.add_balanced_ternary([0], [0]) == [0]                    # 0 + 0 = 0
    assert solution.add_balanced_ternary([1], [1]) == [1, -1]                # 1 + 1 = 2


def test_add_with_negatives_and_borrow():
    # -1 + -1 = -2 = -1*3 + 1*1 -> [-1, 1]
    assert solution.add_balanced_ternary([-1], [-1]) == [-1, 1]
    # -4 + -4 = -8 = -1*9 + 0*3 + 1*1 -> [-1, 0, 1]
    a = solution.to_balanced_ternary(-4)
    r = solution.add_balanced_ternary(a, a)
    assert solution.from_balanced_ternary(r) == -8
    assert _is_canonical(r)


def test_add_identity_with_zero_and_empty():
    x = solution.to_balanced_ternary(42)
    assert solution.add_balanced_ternary(x, [0]) == x
    assert solution.add_balanced_ternary(x, []) == x
    assert solution.add_balanced_ternary([], []) == [0]


def test_add_result_is_canonical():
    a = solution.to_balanced_ternary(13)
    b = solution.to_balanced_ternary(-13)
    r = solution.add_balanced_ternary(a, b)
    assert r == [0]  # sums to zero -> canonical zero
    assert _is_canonical(r)


def test_leading_zeros_in_add_inputs():
    a = [0, 0, 1, -1, -1]   # value 5 with leading zeros
    b = [0, -1, -1]         # value -4 with a leading zero
    assert solution.add_balanced_ternary(a, b) == [1]


def test_round_trip_property():
    for n in range(-2000, 2001):
        assert solution.from_balanced_ternary(solution.to_balanced_ternary(n)) == n


def test_round_trip_large_seeded():
    import random
    rng = random.Random(20240704)
    for _ in range(500):
        # Range well beyond 3**30 (~2.06e14) and 3**40 (~1.2e19) so any
        # fixed-width / precision-capped implementation is caught.
        n = rng.randint(-(10 ** 24), 10 ** 24)
        d = solution.to_balanced_ternary(n)
        assert _is_canonical(d)
        assert solution.from_balanced_ternary(d) == n


def test_round_trip_huge_explicit():
    # Explicit magnitudes above the (3**30 - 1) // 2 ~= 1.03e14 threshold where
    # a 30-place capped implementation first fails to round-trip.
    for n in (
        3 ** 30,
        3 ** 30 + 1,
        3 ** 31,
        3 ** 40 + 7,
        -(3 ** 40 + 7),
        10 ** 18,
        -(10 ** 18),
        (3 ** 50 - 1) // 2,
        -((3 ** 50 - 1) // 2),
        3 ** 64 + 123456789,
    ):
        d = solution.to_balanced_ternary(n)
        assert _is_canonical(d)
        assert solution.from_balanced_ternary(d) == n


def test_add_property_seeded():
    import random
    rng = random.Random(777)
    for _ in range(1500):
        x = rng.randint(-100000, 100000)
        y = rng.randint(-100000, 100000)
        a = solution.to_balanced_ternary(x)
        b = solution.to_balanced_ternary(y)
        r = solution.add_balanced_ternary(a, b)
        assert _is_canonical(r)
        assert solution.from_balanced_ternary(r) == x + y
        assert _from_ref(r) == x + y
