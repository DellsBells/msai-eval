import random

import solution


def test_example_1():
    out = solution.rank_contestants([
        {"id": "c1", "score": 100, "penalty": 5},
        {"id": "c2", "score": 100, "penalty": 5},
        {"id": "c3", "score": 90, "penalty": 0},
    ])
    assert out == [("c1", 1), ("c2", 1), ("c3", 3)]


def test_example_2_penalty_tiebreak():
    out = solution.rank_contestants([
        {"id": "x", "score": 50, "penalty": 10},
        {"id": "y", "score": 50, "penalty": 3},
        {"id": "z", "score": 50, "penalty": 3},
    ])
    assert out == [("y", 1), ("z", 1), ("x", 3)]


def test_empty():
    assert solution.rank_contestants([]) == []


def test_single():
    assert solution.rank_contestants([{"id": "solo", "score": 0, "penalty": 0}]) == [("solo", 1)]


def test_all_distinct_scores():
    out = solution.rank_contestants([
        {"id": "a", "score": 1, "penalty": 0},
        {"id": "b", "score": 3, "penalty": 0},
        {"id": "c", "score": 2, "penalty": 0},
    ])
    assert out == [("b", 1), ("c", 2), ("a", 3)]


def test_competition_ranking_skips():
    # Three tied at top -> ranks 1,1,1 then next is rank 4.
    out = solution.rank_contestants([
        {"id": "a", "score": 10, "penalty": 2},
        {"id": "b", "score": 10, "penalty": 2},
        {"id": "c", "score": 10, "penalty": 2},
        {"id": "d", "score": 5, "penalty": 0},
    ])
    assert out == [("a", 1), ("b", 1), ("c", 1), ("d", 4)]


def test_multiple_tie_groups():
    # Two groups of two, then a single.
    out = solution.rank_contestants([
        {"id": "p", "score": 9, "penalty": 1},
        {"id": "q", "score": 9, "penalty": 1},
        {"id": "r", "score": 8, "penalty": 4},
        {"id": "s", "score": 8, "penalty": 4},
        {"id": "t", "score": 7, "penalty": 0},
    ])
    assert out == [("p", 1), ("q", 1), ("r", 3), ("s", 3), ("t", 5)]


def test_negative_scores():
    out = solution.rank_contestants([
        {"id": "a", "score": -5, "penalty": 2},
        {"id": "b", "score": -1, "penalty": 9},
    ])
    # b has higher score -> better.
    assert out == [("b", 1), ("a", 2)]


def test_id_tiebreak_within_group():
    out = solution.rank_contestants([
        {"id": "delta", "score": 4, "penalty": 4},
        {"id": "alpha", "score": 4, "penalty": 4},
        {"id": "charlie", "score": 4, "penalty": 4},
    ])
    assert out == [("alpha", 1), ("charlie", 1), ("delta", 1)]


def test_input_not_mutated():
    inp = [
        {"id": "a", "score": 1, "penalty": 0},
        {"id": "b", "score": 2, "penalty": 0},
    ]
    snapshot = [dict(d) for d in inp]
    solution.rank_contestants(inp)
    assert inp == snapshot


def test_property_rank_invariants():
    rng = random.Random(777)
    for _ in range(200):
        n = rng.randint(0, 25)
        inp = [
            {
                "id": "id%03d" % k,
                "score": rng.randint(-3, 3),
                "penalty": rng.randint(0, 3),
            }
            for k in range(n)
        ]
        out = solution.rank_contestants(inp)
        # Every contestant present exactly once.
        assert sorted(t[0] for t in out) == sorted(c["id"] for c in inp)
        if not out:
            continue
        # Best rank is 1.
        assert out[0][1] == 1
        # Ranks non-decreasing down the list.
        ranks = [t[1] for t in out]
        assert all(a <= b for a, b in zip(ranks, ranks[1:]))
        # Competition ranking: rank at position i (0-based) is either equal to a
        # tie group's rank or exactly i+1 at the start of a group.
        by_id = {c["id"]: c for c in inp}
        # Build sorted key for verification.
        keyed = sorted(inp, key=lambda c: (-c["score"], c["penalty"], c["id"]))
        expected = []
        i = 0
        while i < len(keyed):
            j = i + 1
            while (
                j < len(keyed)
                and keyed[j]["score"] == keyed[i]["score"]
                and keyed[j]["penalty"] == keyed[i]["penalty"]
            ):
                j += 1
            for k in range(i, j):
                expected.append((keyed[k]["id"], i + 1))
            i = j
        assert out == expected
        # sanity: by_id lookups usable
        assert all(t[0] in by_id for t in out)
