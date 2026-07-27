import random

import solution


def test_empty():
    assert solution.coverage_stats([]) == (0, 0)


def test_empty_returns_int_zeros():
    total, multi = solution.coverage_stats([])
    # A zero produced by integer arithmetic must be the int 0, not 0.0.
    assert type(total) is int
    assert type(multi) is int


def test_single_interval():
    assert solution.coverage_stats([[0, 5]]) == (5, 0)


def test_integer_inputs_return_ints():
    # Every accumulated interval has integer endpoints, so both returned
    # lengths must be Python ints -- including a length that lands on zero.
    total, multi = solution.coverage_stats([[0, 5], [2, 7]])
    assert type(total) is int
    assert type(multi) is int
    # multi_covered is a genuine positive int here, total too.
    assert (total, multi) == (7, 3)

    # A case where multi_covered is zero: it must be int 0, not 0.0.
    total0, multi0 = solution.coverage_stats([[0, 5]])
    assert type(total0) is int
    assert type(multi0) is int
    assert (total0, multi0) == (5, 0)

    # All-integer input where nothing is covered -> int (0, 0).
    tz, mz = solution.coverage_stats([[5, 5], [3, 1]])
    assert type(tz) is int
    assert type(mz) is int


def test_simple_overlap():
    assert solution.coverage_stats([[0, 5], [2, 7]]) == (7, 3)


def test_touching_no_double():
    assert solution.coverage_stats([[0, 2], [2, 4]]) == (4, 0)


def test_triple_overlap_region():
    # the >=2 region here is [1,4) = length 3, NOT 6 (which pairwise/subtraction
    # style solutions produce)
    assert solution.coverage_stats([[0, 4], [1, 3], [2, 6]]) == (6, 3)


def test_full_nesting():
    # [1,4) sits inside [0,10); the nested part is doubly covered
    assert solution.coverage_stats([[0, 10], [1, 4]]) == (10, 3)


def test_identical_duplicates():
    # two identical sensors -> whole thing doubly covered
    assert solution.coverage_stats([[2, 5], [2, 5]]) == (3, 3)


def test_three_identical():
    # union 3, and every point covered by >=2 -> multi is also 3
    assert solution.coverage_stats([[0, 3], [0, 3], [0, 3]]) == (3, 3)


def test_degenerate_intervals_ignored():
    assert solution.coverage_stats([[5, 5], [3, 1]]) == (0, 0)
    assert solution.coverage_stats([[0, 4], [2, 2], [6, 3]]) == (4, 0)


def test_disjoint_intervals():
    assert solution.coverage_stats([[0, 2], [5, 8]]) == (5, 0)


def test_negative_and_float():
    total, multi = solution.coverage_stats([[-2.0, 2.0], [0.0, 3.0]])
    assert total == 5.0
    assert multi == 2.0
    # Float endpoints contribute to both lengths, so both must be floats.
    assert type(total) is float
    assert type(multi) is float


def test_float_endpoints_produce_float_lengths():
    # Overlap length is a float because a float endpoint feeds the width.
    total, multi = solution.coverage_stats([[0, 5], [2.5, 7]])
    assert total == 7
    assert multi == 2.5
    assert type(total) is float
    assert type(multi) is float


def test_invariant_total_ge_multi_ge_zero():
    total, multi = solution.coverage_stats([[0, 10], [2, 8], [4, 6], [1, 9]])
    assert total >= multi >= 0


def test_input_not_mutated():
    data = [[0, 5], [2, 7]]
    snapshot = [list(iv) for iv in data]
    solution.coverage_stats(data)
    assert data == snapshot


def test_property_matches_bruteforce_integer_grid():
    rng = random.Random(2024)
    for _ in range(300):
        n = rng.randint(0, 10)
        ivs = []
        depth = {}
        for _ in range(n):
            a = rng.randint(0, 20)
            b = a + rng.randint(-2, 8)  # some degenerate
            ivs.append([a, b])
            if a < b:
                for x in range(a, b):
                    depth[x] = depth.get(x, 0) + 1
        total, multi = solution.coverage_stats(ivs)
        expected_total = sum(1 for d in depth.values() if d >= 1)
        expected_multi = sum(1 for d in depth.values() if d >= 2)
        assert total == expected_total
        assert multi == expected_multi
