import copy
import random

import solution


def _leaf(name):
    return {"name": name, "children": []}


def _node(name, children):
    return {"name": name, "children": children}


def test_root_only_is_zero():
    assert solution.deepest_level(_leaf("root")) == 0


def test_single_child():
    tree = _node("root", [_leaf("a")])
    assert solution.deepest_level(tree) == 1


def test_example_two():
    tree = _node("root", [
        _node("a", [_leaf("a1")]),
        _leaf("b"),
    ])
    assert solution.deepest_level(tree) == 2


def test_example_three():
    tree = _node("root", [
        _node("x", [
            _node("x1", [_leaf("x1a")]),
            _leaf("x2"),
        ]),
    ])
    assert solution.deepest_level(tree) == 3


def test_deepest_comes_from_leaf_not_shallow_branch():
    # A wide shallow branch plus one deep chain.
    deep = _node("d0", [_node("d1", [_node("d2", [_leaf("d3")])])])
    tree = _node("root", [_leaf("s1"), _leaf("s2"), deep])
    assert solution.deepest_level(tree) == 4


def test_tie_at_deepest_level():
    tree = _node("root", [
        _node("a", [_leaf("a1")]),
        _node("b", [_leaf("b1")]),
    ])
    assert solution.deepest_level(tree) == 2


def test_internal_node_deep_but_leaf_shallower_on_another_branch():
    # Left branch: leaf at level 1. Right branch: leaf at level 3.
    tree = _node("root", [
        _leaf("left"),
        _node("r", [_node("r1", [_leaf("r2")])]),
    ])
    assert solution.deepest_level(tree) == 3


def test_does_not_mutate_input():
    tree = _node("root", [_node("a", [_leaf("a1")]), _leaf("b")])
    snapshot = copy.deepcopy(tree)
    solution.deepest_level(tree)
    assert tree == snapshot


def test_property_matches_recursive_height_over_random_trees():
    # Independent reference: height in edges via a simple recursion.
    def height(node):
        kids = node["children"]
        if not kids:
            return 0
        return 1 + max(height(c) for c in kids)

    def gen(rng, depth_budget):
        if depth_budget <= 0 or rng.random() < 0.35:
            return _leaf("L")
        n = rng.randint(1, 3)
        return _node("N", [gen(rng, depth_budget - 1) for _ in range(n)])

    rng = random.Random(20240607)
    for _ in range(200):
        tree = gen(rng, rng.randint(0, 6))
        assert solution.deepest_level(tree) == height(tree)
