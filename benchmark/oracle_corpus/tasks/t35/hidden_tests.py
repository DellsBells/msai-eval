import functools
import random

import pytest

import solution


def _oracle(records, keys):
    """Independent reference for property testing."""
    decorated = list(enumerate(records))

    def compare(a, b):
        ia, ra = a
        ib, rb = b
        for field, direction in keys:
            va, vb = ra[field], rb[field]
            if va == vb:
                continue
            base = -1 if va < vb else 1
            if direction == "desc":
                base = -base
            return base
        return -1 if ia < ib else (1 if ia > ib else 0)

    decorated.sort(key=functools.cmp_to_key(compare))
    return [rec for _, rec in decorated]


def test_example_1_tie_keeps_input_order():
    recs = [
        {"team": "B", "wins": 3, "name": "y"},
        {"team": "A", "wins": 5, "name": "x"},
        {"team": "A", "wins": 5, "name": "w"},
    ]
    out = solution.multisort(recs, [("team", "asc"), ("wins", "desc")])
    assert [r["name"] for r in out] == ["x", "w", "y"]


def test_example_2_desc_single_key_tiebreak():
    recs = [{"v": 2}, {"v": 1}, {"v": 2}]
    out = solution.multisort(recs, [("v", "desc")])
    # Two v==2 records keep input order: the first-appearing (index 0) stays first.
    assert out[0] is recs[0]
    assert out[1] is recs[2]
    assert out[2] is recs[1]


def test_empty_keys_preserves_order():
    recs = [{"a": 3}, {"a": 1}, {"a": 2}]
    out = solution.multisort(recs, [])
    assert [r["a"] for r in out] == [3, 1, 2]
    assert out is not recs


def test_empty_records():
    assert solution.multisort([], [("x", "asc")]) == []
    assert solution.multisort([], []) == []


def test_single_record():
    recs = [{"a": 9}]
    out = solution.multisort(recs, [("a", "desc")])
    assert out == [{"a": 9}]
    assert out is not recs


def test_desc_string_key():
    recs = [{"s": "apple"}, {"s": "cherry"}, {"s": "banana"}]
    out = solution.multisort(recs, [("s", "desc")])
    assert [r["s"] for r in out] == ["cherry", "banana", "apple"]


def test_mixed_directions():
    recs = [
        {"grp": 1, "score": 10, "tag": "a"},
        {"grp": 1, "score": 20, "tag": "b"},
        {"grp": 2, "score": 5, "tag": "c"},
        {"grp": 1, "score": 20, "tag": "d"},
    ]
    # grp ascending, then score descending.
    out = solution.multisort(recs, [("grp", "asc"), ("score", "desc")])
    tags = [r["tag"] for r in out]
    # grp 1 first: scores 20 (b), 20 (d, tie keeps input order), 10 (a); then grp 2.
    assert tags == ["b", "d", "a", "c"]


def test_full_tie_all_keys_equal_stable():
    recs = [
        {"a": 1, "b": 1, "id": 0},
        {"a": 1, "b": 1, "id": 1},
        {"a": 1, "b": 1, "id": 2},
    ]
    out = solution.multisort(recs, [("a", "desc"), ("b", "desc")])
    assert [r["id"] for r in out] == [0, 1, 2]


def test_invalid_direction_raises():
    with pytest.raises(ValueError):
        solution.multisort([{"a": 1}], [("a", "ascending")])
    with pytest.raises(ValueError):
        solution.multisort([{"a": 1}], [("a", "ASC")])


def test_input_not_mutated():
    recs = [{"a": 2}, {"a": 1}]
    snapshot = [dict(d) for d in recs]
    order_before = list(recs)
    solution.multisort(recs, [("a", "asc")])
    assert recs == snapshot
    assert recs == order_before  # original list order unchanged


def test_returns_same_objects():
    recs = [{"a": 3}, {"a": 1}, {"a": 2}]
    out = solution.multisort(recs, [("a", "asc")])
    assert {id(r) for r in out} == {id(r) for r in recs}


def test_property_against_oracle():
    rng = random.Random(98765)
    for _ in range(400):
        n = rng.randint(0, 12)
        recs = [
            {
                "a": rng.randint(0, 3),
                "b": rng.choice(["p", "q", "r", "s"]),
                "_i": i,
            }
            for i in range(n)
        ]
        possible = ["a", "b"]
        k = rng.randint(0, 2)
        chosen = rng.sample(possible, k)
        keys = [(f, rng.choice(["asc", "desc"])) for f in chosen]
        got = solution.multisort(recs, keys)
        exp = _oracle(recs, keys)
        assert [r["_i"] for r in got] == [r["_i"] for r in exp]
