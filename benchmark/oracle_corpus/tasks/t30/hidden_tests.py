import solution


def _from_ref(digits):
    # Independent factoradic->int for property checks.
    total = 0
    fact = 1
    for j, digit in enumerate(reversed(digits)):
        if j == 0:
            fact = 1
        else:
            fact *= j
        total += digit * fact
    return total


def test_to_small_values():
    assert solution.to_factoradic(0) == [0]
    assert solution.to_factoradic(1) == [1, 0]
    assert solution.to_factoradic(2) == [1, 0, 0]


def test_to_worked_example():
    assert solution.to_factoradic(349) == [2, 4, 2, 0, 1, 0]


def test_from_worked_example():
    assert solution.from_factoradic([2, 4, 2, 0, 1, 0]) == 349


def test_from_small_values():
    assert solution.from_factoradic([0]) == 0
    assert solution.from_factoradic([1, 0]) == 1
    assert solution.from_factoradic([1, 0, 0]) == 2


def test_from_empty_list():
    assert solution.from_factoradic([]) == 0


def test_no_leading_zeros_and_minimal_length():
    # n = 6 = 1*3! + 0*2! + 0*1! + 0*0!  -> [1, 0, 0, 0]
    assert solution.to_factoradic(6) == [1, 0, 0, 0]
    # Most significant digit is always nonzero for n >= 1.
    for n in range(1, 200):
        d = solution.to_factoradic(n)
        assert d[0] != 0
        assert d[-1] == 0  # 0! place is always 0


def test_boundary_at_factorials():
    # 24 = 4! exactly -> 1*4! + 0*3! + 0*2! + 0*1! + 0*0!
    assert solution.to_factoradic(24) == [1, 0, 0, 0, 0]
    # 23 = 3*3! + 2*2! + 1*1! + 0*0! = 18 + 4 + 1 = 23
    assert solution.to_factoradic(23) == [3, 2, 1, 0]


def test_digit_range_valid():
    # Each digit at place j! must be in 0..j.
    for n in range(0, 5000):
        d = solution.to_factoradic(n)
        L = len(d)
        for idx, digit in enumerate(d):
            place = (L - 1) - idx  # this element sits on place!
            assert 0 <= digit <= place


def test_round_trip_property():
    for n in range(0, 3000):
        assert solution.from_factoradic(solution.to_factoradic(n)) == n


def test_round_trip_large_seeded():
    import random
    rng = random.Random(424242)
    for _ in range(500):
        n = rng.randint(0, 10 ** rng.randint(0, 15))
        digits = solution.to_factoradic(n)
        assert solution.from_factoradic(digits) == n
        assert _from_ref(digits) == n


def test_from_matches_independent_reference():
    # Build valid factoradic lists directly and check from_factoradic.
    import random
    rng = random.Random(99)
    for _ in range(300):
        length = rng.randint(1, 8)
        # places go from (length-1)! down to 0!
        digits = []
        for idx in range(length):
            place = (length - 1) - idx
            digits.append(rng.randint(0, place))
        assert solution.from_factoradic(digits) == _from_ref(digits)
