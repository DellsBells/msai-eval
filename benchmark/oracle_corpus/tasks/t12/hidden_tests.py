import random

import solution


def test_basic_subtraction():
    r = solution.resolve_ranges([[0, 10]], [[3, 5], [7, 8]])
    assert r == {"available": [[0, 3], [5, 7], [8, 10]], "peak_depth": 1}


def test_allowed_overlap_depth_two():
    r = solution.resolve_ranges([[0, 4], [2, 6]], [])
    assert r == {"available": [[0, 6]], "peak_depth": 2}


def test_everything_blocked():
    r = solution.resolve_ranges([[0, 5]], [[0, 5]])
    assert r == {"available": [], "peak_depth": 1}


def test_touching_allowed_ranges_join():
    r = solution.resolve_ranges([[0, 3], [3, 6]], [])
    assert r == {"available": [[0, 6]], "peak_depth": 1}


def test_empty_allowed():
    r = solution.resolve_ranges([], [[1, 2]])
    assert r == {"available": [], "peak_depth": 0}


def test_both_empty():
    r = solution.resolve_ranges([], [])
    assert r == {"available": [], "peak_depth": 0}


def test_blocked_outside_allowed_noop():
    r = solution.resolve_ranges([[0, 5]], [[10, 20]])
    assert r == {"available": [[0, 5]], "peak_depth": 1}


def test_blocked_touching_boundary_removes_nothing():
    # blocked [5,7) touches allowed at 5 boundary; [0,5) point set unaffected
    r = solution.resolve_ranges([[0, 5]], [[5, 7]])
    assert r == {"available": [[0, 5]], "peak_depth": 1}


def test_degenerate_intervals_ignored():
    r = solution.resolve_ranges([[0, 4], [2, 2]], [[6, 3]])
    assert r == {"available": [[0, 4]], "peak_depth": 1}


def test_blocked_spans_multiple_allowed():
    # one blocked interval cuts across two separate allowed pieces
    r = solution.resolve_ranges([[0, 4], [6, 10]], [[3, 8]])
    assert r == {"available": [[0, 3], [8, 10]], "peak_depth": 1}


def test_nested_allowed_depth_three():
    r = solution.resolve_ranges([[0, 9], [1, 8], [2, 3]], [])
    assert r["available"] == [[0, 9]]
    assert r["peak_depth"] == 3


def test_negative_endpoints():
    r = solution.resolve_ranges([[-5, 5]], [[-2, 2]])
    assert r == {"available": [[-5, -2], [2, 5]], "peak_depth": 1}


def test_available_items_are_lists():
    r = solution.resolve_ranges([(0, 5), (7, 9)], [(1, 2)])
    assert all(isinstance(iv, list) for iv in r["available"])


def test_inputs_not_mutated():
    a = [[0, 10]]
    b = [[3, 5]]
    sa = [list(x) for x in a]
    sb = [list(x) for x in b]
    solution.resolve_ranges(a, b)
    assert a == sa and b == sb


def test_float_peak_depth_overlap_no_integer_point():
    # Two allowed intervals overlap on [0.4, 0.6), a sub-unit region that
    # contains no integer point. peak_depth must be 2 (real coverage depth),
    # not 1. A solution that only counts whole-integer points is wrong here.
    r = solution.resolve_ranges([[0.0, 0.6], [0.4, 1.0]], [])
    assert r["available"] == [[0.0, 1.0]]
    assert r["peak_depth"] == 2


def test_float_peak_depth_and_subtraction():
    # Fractional endpoints throughout; overlap [0.5, 1.5) has depth 2.
    r = solution.resolve_ranges([[0.0, 1.5], [0.5, 2.0]], [])
    assert r["available"] == [[0.0, 2.0]]
    assert r["peak_depth"] == 2

    # Deeper fractional nesting: overlap on [1.5, 2.0) reaches depth 3, even
    # though no integer point lies in that sub-unit overlap.
    r3 = solution.resolve_ranges([[0.5, 2.5], [1.0, 3.0], [1.5, 2.0]], [])
    assert r3["available"] == [[0.5, 3.0]]
    assert r3["peak_depth"] == 3

    # Blocked interval with fractional bounds carves a sub-unit hole out of the
    # available set while leaving peak_depth (allowed-only) untouched.
    r4 = solution.resolve_ranges([[0.0, 1.0], [0.5, 1.5]], [[0.7, 0.8]])
    assert r4["available"] == [[0.0, 0.7], [0.8, 1.5]]
    assert r4["peak_depth"] == 2


def test_property_matches_bruteforce_float_grid():
    # Endpoints are drawn on a half-integer grid (multiples of 0.5). Brute force
    # over that grid by scaling everything to integers (x2), so sub-unit overlaps
    # that contain no whole-integer point are still checked. A peak_depth that
    # only counts whole-integer points (an integer-grid solution) is wrong here.
    rng = random.Random(9091)
    SCALE = 2  # grid step 0.5
    for _ in range(300):
        na = rng.randint(0, 6)
        nb = rng.randint(0, 6)
        allowed = []
        blocked = []
        for _ in range(na):
            s = rng.randint(-10, 20) / SCALE
            e = s + rng.randint(-4, 14) / SCALE
            allowed.append([s, e])
        for _ in range(nb):
            s = rng.randint(-10, 20) / SCALE
            e = s + rng.randint(-4, 14) / SCALE
            blocked.append([s, e])

        r = solution.resolve_ranges(allowed, blocked)

        # brute force the available point set on the scaled integer grid
        allowed_pts = set()
        for s, e in allowed:
            si, ei = round(s * SCALE), round(e * SCALE)
            if si < ei:
                allowed_pts.update(range(si, ei))
        blocked_pts = set()
        for s, e in blocked:
            si, ei = round(s * SCALE), round(e * SCALE)
            if si < ei:
                blocked_pts.update(range(si, ei))
        expected_pts = allowed_pts - blocked_pts

        rebuilt = set()
        prev_end = None
        for a, b in r["available"]:
            assert a < b
            if prev_end is not None:
                # normalized: strictly separated (a real gap must exist)
                assert a > prev_end
            prev_end = b
            ai, bi = round(a * SCALE), round(b * SCALE)
            rebuilt.update(range(ai, bi))
        assert rebuilt == expected_pts

        # brute-force peak depth on the scaled grid
        depth_at = {}
        for s, e in allowed:
            si, ei = round(s * SCALE), round(e * SCALE)
            if si < ei:
                for x in range(si, ei):
                    depth_at[x] = depth_at.get(x, 0) + 1
        expected_peak = max(depth_at.values()) if depth_at else 0
        assert r["peak_depth"] == expected_peak


def test_property_matches_bruteforce():
    rng = random.Random(4242)
    for _ in range(300):
        na = rng.randint(0, 6)
        nb = rng.randint(0, 6)
        allowed = []
        blocked = []
        for _ in range(na):
            s = rng.randint(-5, 10)
            e = s + rng.randint(-2, 7)
            allowed.append([s, e])
        for _ in range(nb):
            s = rng.randint(-5, 10)
            e = s + rng.randint(-2, 7)
            blocked.append([s, e])

        r = solution.resolve_ranges(allowed, blocked)

        # brute-force available point set over integer grid
        allowed_pts = set()
        for s, e in allowed:
            if s < e:
                allowed_pts.update(range(s, e))
        blocked_pts = set()
        for s, e in blocked:
            if s < e:
                blocked_pts.update(range(s, e))
        expected_pts = allowed_pts - blocked_pts

        rebuilt = set()
        prev_end = None
        for a, b in r["available"]:
            assert a < b
            if prev_end is not None:
                # normalized: strictly separated (a real gap must exist)
                assert a > prev_end
            prev_end = b
            rebuilt.update(range(a, b))
        assert rebuilt == expected_pts

        # brute-force peak depth
        depth_at = {}
        for s, e in allowed:
            if s < e:
                for x in range(s, e):
                    depth_at[x] = depth_at.get(x, 0) + 1
        expected_peak = max(depth_at.values()) if depth_at else 0
        assert r["peak_depth"] == expected_peak
