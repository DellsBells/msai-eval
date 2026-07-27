import random

import solution


def test_basic_overlap():
    assert solution.merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [
        [1, 6],
        [8, 10],
        [15, 18],
    ]


def test_touching_endpoints_merge():
    assert solution.merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]


def test_adjacent_integers_merge():
    # 2 and 3 are adjacent with no integer between them
    assert solution.merge_intervals([[1, 2], [3, 4]]) == [[1, 4]]


def test_real_gap_preserved():
    # gap of 3 and 4 between the intervals
    assert solution.merge_intervals([[5, 7], [1, 2]]) == [[1, 2], [5, 7]]


def test_empty_input():
    assert solution.merge_intervals([]) == []


def test_single_interval():
    assert solution.merge_intervals([[7, 9]]) == [[7, 9]]


def test_nested_intervals():
    assert solution.merge_intervals([[1, 10], [2, 3], [4, 5]]) == [[1, 10]]


def test_duplicates():
    assert solution.merge_intervals([[2, 4], [2, 4], [2, 4]]) == [[2, 4]]


def test_negative_values():
    assert solution.merge_intervals([[-5, -3], [-4, 0], [2, 3]]) == [[-5, 0], [2, 3]]


def test_input_not_mutated():
    # Unsorted on purpose: an in-place sort of the caller's list would reorder
    # these and be caught here. Also verifies inner interval lists are untouched.
    data = [[5, 7], [1, 2]]
    snapshot = [list(iv) for iv in data]
    solution.merge_intervals(data)
    assert data == snapshot
    assert data[0] is not snapshot[0]


def test_input_not_mutated_when_merging():
    # Overlapping + unsorted: in-place sort reorders; mutating an inner list to
    # extend its end (e.g. data[0][1] = 6) would also be caught.
    data = [[2, 6], [1, 3], [8, 10]]
    snapshot = [list(iv) for iv in data]
    result = solution.merge_intervals(data)
    assert result == [[1, 6], [8, 10]]
    assert data == snapshot


def test_returns_lists_not_tuples():
    out = solution.merge_intervals([(1, 2), (5, 6)])
    assert all(isinstance(iv, list) for iv in out)
    assert out == [[1, 2], [5, 6]]


def test_property_result_is_disjoint_and_sorted():
    rng = random.Random(1234)
    for _ in range(200):
        n = rng.randint(0, 20)
        ivs = []
        for _ in range(n):
            a = rng.randint(-30, 30)
            b = a + rng.randint(0, 10)
            ivs.append([a, b])
        merged = solution.merge_intervals(ivs)
        # sorted by start
        starts = [iv[0] for iv in merged]
        assert starts == sorted(starts)
        # each valid and strictly separated by a real gap (>1) from the next
        for iv in merged:
            assert iv[0] <= iv[1]
        for i in range(len(merged) - 1):
            assert merged[i + 1][0] > merged[i][1] + 1


def test_property_coverage_matches_pointset():
    rng = random.Random(99)
    for _ in range(150):
        n = rng.randint(1, 12)
        ivs = []
        covered = set()
        for _ in range(n):
            a = rng.randint(0, 20)
            b = a + rng.randint(0, 6)
            ivs.append([a, b])
            covered.update(range(a, b + 1))
        merged = solution.merge_intervals(ivs)
        rebuilt = set()
        for s, e in merged:
            rebuilt.update(range(s, e + 1))
        assert rebuilt == covered
