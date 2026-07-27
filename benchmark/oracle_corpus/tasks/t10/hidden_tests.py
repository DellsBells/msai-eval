import random

import solution


def test_basic_gaps():
    assert solution.find_gaps([[1, 3], [5, 8]], 0, 10) == [[0, 1], [3, 5], [8, 10]]


def test_half_open_tiling_no_gap():
    assert solution.find_gaps([[0, 2], [2, 4]], 0, 4) == []


def test_reservations_clipped_to_window():
    assert solution.find_gaps([[-5, 2], [8, 20]], 0, 10) == [[2, 8]]


def test_empty_reservations_whole_window():
    assert solution.find_gaps([], 0, 5) == [[0, 5]]


def test_degenerate_window_returns_empty():
    assert solution.find_gaps([[1, 2]], 5, 5) == []
    assert solution.find_gaps([[1, 2]], 6, 3) == []


def test_degenerate_reservation_ignored():
    # start >= end reservations cover nothing
    assert solution.find_gaps([[3, 3], [7, 2]], 0, 10) == [[0, 10]]


def test_nested_reservations():
    # a big reservation with a smaller one inside; out of end-order after sort
    assert solution.find_gaps([[1, 9], [3, 4]], 0, 10) == [[0, 1], [9, 10]]


def test_reservation_covers_whole_window():
    assert solution.find_gaps([[-1, 11]], 0, 10) == []


def test_overlapping_reservations_merge_coverage():
    assert solution.find_gaps([[1, 5], [4, 8]], 0, 10) == [[0, 1], [8, 10]]


def test_reservation_entirely_outside_window():
    assert solution.find_gaps([[20, 30]], 0, 10) == [[0, 10]]


def test_float_endpoints_exact():
    out = solution.find_gaps([[0.5, 1.5]], 0.0, 2.0)
    assert out == [[0.0, 0.5], [1.5, 2.0]]


def test_endpoints_preserved_without_rounding():
    # High-precision reservation endpoints must be carried through verbatim:
    # no rounding, no truncation. The gap boundaries are exactly the clipped
    # reservation edges.
    out = solution.find_gaps([[0.123456789, 5.000000001]], 0, 10)
    assert out == [[0, 0.123456789], [5.000000001, 10]]
    # The precise values must survive bit-for-bit (round(x, 6) would break this).
    assert out[0][1] == 0.123456789
    assert out[1][0] == 5.000000001


def test_irrational_window_bounds_preserved():
    # Window bounds themselves are preserved exactly when they bound a gap.
    import math

    lo = math.pi          # 3.141592653589793
    hi = math.e * 10      # 27.18281828459045
    out = solution.find_gaps([[10.0, 20.0]], lo, hi)
    assert out == [[lo, 10.0], [20.0, hi]]
    assert out[0][0] == math.pi
    assert out[1][1] == math.e * 10


def test_input_not_mutated():
    # UNSORTED input: an in-place sort would reorder these and be detectable.
    data = [[5, 8], [1, 3]]
    snapshot = [list(iv) for iv in data]
    # Preserve object identity of each inner list too, so a swap of the outer
    # list's element references is caught even if values happen to match.
    id_snapshot = [id(iv) for iv in data]
    solution.find_gaps(data, 0, 10)
    # Deep value equality: order and contents must be byte-for-byte unchanged.
    assert data == snapshot
    # The outer list must not have been reordered (element identities in order).
    assert [id(iv) for iv in data] == id_snapshot


def test_input_not_mutated_unsorted_with_nested_and_degenerate():
    # A messier unsorted input that also contains an out-of-order, a nested,
    # and a degenerate reservation. Any in-place reordering or clipping-in-place
    # would corrupt this and be caught by the deep snapshot.
    data = [[5, 8], [1, 9], [3, 4], [7, 2], [-5, 2]]
    snapshot = [list(iv) for iv in data]
    solution.find_gaps(data, 0, 10)
    assert data == snapshot


def test_property_endpoints_are_exact_members():
    # Every gap endpoint must be exactly one of the raw values it came from:
    # either a window bound or a (clipped) reservation edge, with full float
    # precision. A solution that rounds any endpoint would produce a value that
    # is not identically equal to any source value and fail here.
    rng = random.Random(11)
    for _ in range(300):
        ws = round(rng.uniform(0.0, 3.0), 9)
        we = ws + round(rng.uniform(0.0, 12.0), 9)
        n = rng.randint(0, 6)
        res = []
        for _ in range(n):
            a = round(rng.uniform(-2.0, 15.0), 9)
            b = round(rng.uniform(-2.0, 15.0), 9)
            res.append([a, b])
        # Snapshot the input BEFORE the call so we can (a) build expectations
        # from the original ordering/values and (b) detect any mutation.
        res_snapshot = [list(iv) for iv in res]
        gaps = solution.find_gaps(res, ws, we)
        # The function must not mutate or reorder its input list.
        assert res == res_snapshot

        # Build the set of legal endpoint values from the SNAPSHOT (not res):
        # window bounds plus every reservation edge (raw and clipped forms).
        legal = {ws, we}
        for a, b in res_snapshot:
            legal.add(a)
            legal.add(b)
            legal.add(max(a, ws))
            legal.add(min(b, we))
        for a, b in gaps:
            # Identity-level equality: no rounding may have altered the value.
            assert a in legal
            assert b in legal


def test_property_gaps_are_uncovered_and_covered_are_not():
    rng = random.Random(7)
    for _ in range(300):
        ws = rng.randint(0, 5)
        we = ws + rng.randint(0, 15)
        n = rng.randint(0, 8)
        res = []
        for _ in range(n):
            a = rng.randint(-3, 18)
            b = a + rng.randint(-2, 6)  # can be degenerate
            res.append([a, b])
        # Snapshot before the call to detect in-place mutation/reordering.
        res_snapshot = [list(iv) for iv in res]
        gaps = solution.find_gaps(res, ws, we)
        # The function must not mutate or reorder its input list.
        assert res == res_snapshot

        # gaps sorted, positive width, inside window
        for a, b in gaps:
            assert a < b
            assert ws <= a and b <= we
        for i in range(len(gaps) - 1):
            assert gaps[i][1] < gaps[i + 1][0]

        # sample integer points across the window and verify classification.
        # Use the SNAPSHOT so coverage is judged against the original input.
        def is_covered(x):
            for s, e in res_snapshot:
                if s < e and s <= x < e:
                    return True
            return False

        for x in range(ws, we):
            in_gap = any(a <= x < b for a, b in gaps)
            # a point in window is in a gap iff not covered
            assert in_gap == (not is_covered(x))
