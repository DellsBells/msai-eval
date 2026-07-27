import copy
import random

import solution


def test_keys_and_index():
    data = {"a": {"b": [10, 20, 30]}}
    assert solution.query(data, ["a", "b", 1]) == [20]
    assert solution.query(data, ["a", "b"]) == [[10, 20, 30]]
    assert solution.query(data, ["a", "x"]) == []
    assert solution.query(data, ["a", "b", 5]) == []


def test_single_level_wildcard():
    data = {"users": [{"n": "amy"}, {"n": "bo"}]}
    assert solution.query(data, ["users", "*", "n"]) == ["amy", "bo"]
    assert solution.query(data, ["users", "*"]) == [{"n": "amy"}, {"n": "bo"}]


def test_recursive_wildcard_then_key():
    data = {
        "team": {
            "lead": {"name": "amy",
                     "reports": [{"name": "bo"}, {"name": "cy"}]},
        }
    }
    assert solution.query(data, ["**", "name"]) == ["amy", "bo", "cy"]


def test_empty_pattern_returns_root():
    data = [1, 2, 3]
    assert solution.query(data, []) == [[1, 2, 3]]
    data2 = {"k": 5}
    assert solution.query(data2, []) == [{"k": 5}]


def test_star_and_index_at_root():
    data = [1, 2, 3]
    assert solution.query(data, ["*"]) == [1, 2, 3]
    assert solution.query(data, [0]) == [1]
    assert solution.query(data, [2]) == [3]


def test_bool_is_not_an_index():
    data = [10, 20]
    assert solution.query(data, [True]) == []
    assert solution.query(data, [False]) == []
    assert solution.query(data, [1]) == [20]
    assert solution.query(data, [0]) == [10]


def test_negative_index_matches_nothing():
    data = [10, 20, 30]
    assert solution.query(data, [-1]) == []


def test_key_on_nondict_drops():
    data = [{"k": 1}, 99, {"k": 2}]
    # "*" then "k": only the dict elements have key "k".
    assert solution.query(data, ["*", "k"]) == [1, 2]


def test_double_star_lists_every_node_once_in_preorder():
    data = {"a": [1, 2], "b": 3}
    got = solution.query(data, ["**"])
    # Pre-order: root, a([1,2]), 1, 2, b(3)
    assert got == [{"a": [1, 2], "b": 3}, [1, 2], 1, 2, 3]


def test_duplicate_equal_scalars_not_collapsed():
    # Two equal ints and two equal strings must each be reported.
    data = {"x": [10, 10], "y": ["s", "s"]}
    assert solution.query(data, ["x", "*"]) == [10, 10]
    assert solution.query(data, ["y", "*"]) == ["s", "s"]
    # And under "**" every position appears.
    got = solution.query(data, ["**"])
    # root, [10,10], 10, 10, ["s","s"], "s", "s"
    assert got == [
        {"x": [10, 10], "y": ["s", "s"]},
        [10, 10], 10, 10,
        ["s", "s"], "s", "s",
    ]


def test_document_order_across_frontier():
    # After "**" the "v" step must come out in whole-tree document order,
    # not in the order subtrees were visited.
    data = {
        "p": {"v": 1, "child": {"v": 2}},
        "q": {"v": 3},
    }
    # "**" visits: root, p, p.v(1)... then "v": p.v, p.child.v, q.v -> 1,2,3
    assert solution.query(data, ["**", "v"]) == [1, 2, 3]


def test_chained_double_star_dedups_across_frontier():
    # A second "**" applied to the frontier produced by the first "**" must not
    # re-emit tree positions that are reachable from more than one frontier
    # node. Because "**" is descendant-or-self, ["**", "**"] must collapse to
    # exactly the same set of positions as ["**"]: every node once, in
    # pre-order. This exercises cross-frontier de-duplication, which a per-step
    # sort-only implementation (no dedup) would fail by producing duplicates.
    data = {"a": [1, 2], "b": 3}
    single = solution.query(data, ["**"])
    doubled = solution.query(data, ["**", "**"])
    assert single == [{"a": [1, 2], "b": 3}, [1, 2], 1, 2, 3]
    assert doubled == single
    tripled = solution.query(data, ["**", "**", "**"])
    assert tripled == single


def test_star_then_double_star_no_duplicate_positions():
    # "*" fans out to the direct children; the following "**" descends into
    # each. Sibling subtrees are disjoint here, but the root is NOT reachable,
    # while overlapping frontiers created by combining wildcards must still
    # yield each descendant position exactly once and in document order.
    data = {"a": {"x": 1}, "b": {"y": 2}}
    # "*" -> [{"x":1}, {"y":2}]; "**" on each -> those nodes plus descendants.
    assert solution.query(data, ["*", "**"]) == [
        {"x": 1}, 1, {"y": 2}, 2,
    ]
    # Now force overlap: "**" then "*" then "**". The final "**" is applied to
    # a frontier whose subtrees overlap (children of ancestors on the same
    # path), so without cross-frontier dedup the same positions repeat.
    nested = {"outer": {"inner": {"leaf": 7}}}
    got = solution.query(nested, ["**", "*", "**"])
    # No position may appear twice; scalars 7 must appear exactly once.
    assert got.count(7) == 1


def test_does_not_mutate_input():
    data = {"a": {"b": [10, 20, 30]}}
    snap = copy.deepcopy(data)
    solution.query(data, ["**"])
    solution.query(data, ["a", "b", "*"])
    assert data == snap


def test_property_double_star_equals_manual_preorder():
    # Build random JSON-like trees; ["**"] must equal a manual pre-order walk.
    def gen(rng, budget):
        if budget <= 0 or rng.random() < 0.4:
            choice = rng.randint(0, 3)
            if choice == 0:
                return rng.randint(-5, 5)
            if choice == 1:
                return rng.choice(["p", "q", "r"])
            if choice == 2:
                return rng.choice([True, False])
            return None
        if rng.random() < 0.5:
            n = rng.randint(0, 3)
            return [gen(rng, budget - 1) for _ in range(n)]
        keys = ["k%d" % i for i in range(rng.randint(0, 3))]
        return {k: gen(rng, budget - 1) for k in keys}

    def preorder(node):
        out = [node]
        if isinstance(node, dict):
            for v in node.values():
                out.extend(preorder(v))
        elif isinstance(node, list):
            for v in node:
                out.extend(preorder(v))
        return out

    rng = random.Random(2468013579)
    for _ in range(150):
        data = gen(rng, rng.randint(0, 4))
        assert solution.query(data, ["**"]) == preorder(data)


def test_property_star_matches_direct_children():
    def gen(rng, budget):
        if budget <= 0 or rng.random() < 0.4:
            return rng.randint(0, 9)
        if rng.random() < 0.5:
            return [gen(rng, budget - 1) for _ in range(rng.randint(0, 3))]
        return {("k%d" % i): gen(rng, budget - 1)
                for i in range(rng.randint(0, 3))}

    def direct_children(node):
        if isinstance(node, dict):
            return list(node.values())
        if isinstance(node, list):
            return list(node)
        return []

    rng = random.Random(112358)
    for _ in range(150):
        data = gen(rng, rng.randint(0, 4))
        assert solution.query(data, ["*"]) == direct_children(data)
