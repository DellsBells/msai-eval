import copy
import random

import solution


def D(name, children):
    return {"name": name, "kind": "dir", "children": children}


def F(name):
    return {"name": name, "kind": "file", "children": []}


def test_depth_cap_collapses_now_empty_dir():
    tree = D("/", [D("a", [F("f.txt")])])
    assert solution.prune(tree, 1) == D("/", [])


def test_files_keep_ancestors_alive():
    tree = D("root", [
        D("keep", [F("note")]),
        D("empty", []),
    ])
    expected = D("root", [D("keep", [F("note")])])
    assert solution.prune(tree, 5) == expected


def test_cascade_up_multiple_levels():
    tree = D("root", [D("x", [D("y", [F("deep.txt")])])])
    assert solution.prune(tree, 1) == D("root", [])


def test_max_depth_zero_keeps_only_root():
    tree = D("root", [F("a"), D("b", [F("c")])])
    assert solution.prune(tree, 0) == D("root", [])


def test_empty_dir_is_removed_but_root_kept():
    tree = D("root", [])
    assert solution.prune(tree, 3) == D("root", [])


def test_file_directly_under_root_survives():
    tree = D("root", [F("top.txt"), D("gone", [])])
    assert solution.prune(tree, 2) == D("root", [F("top.txt")])


def test_order_is_preserved():
    tree = D("root", [
        D("a", [F("1")]),
        D("b", [F("2")]),
        D("c", [F("3")]),
    ])
    out = solution.prune(tree, 5)
    assert [c["name"] for c in out["children"]] == ["a", "b", "c"]


def test_order_is_preserved_in_nested_dirs():
    # Ordering must be preserved within non-root directories too, not just
    # directly under the root.
    tree = D("root", [
        D("sub", [F("1"), F("2"), F("3")]),
    ])
    out = solution.prune(tree, 5)
    assert [c["name"] for c in out["children"]] == ["sub"]
    sub = out["children"][0]
    assert [c["name"] for c in sub["children"]] == ["1", "2", "3"]


def test_order_preserved_with_pruned_siblings():
    # A survivor's position is defined by original left-to-right order after
    # dropping collapsed siblings; nested ordering must remain stable.
    tree = D("root", [
        D("outer", [
            F("a"),
            D("dead", []),
            F("b"),
            D("keep", [F("c"), F("d")]),
            F("e"),
        ]),
    ])
    out = solution.prune(tree, 5)
    outer = out["children"][0]
    assert [c["name"] for c in outer["children"]] == ["a", "b", "keep", "e"]
    keep = [c for c in outer["children"] if c["name"] == "keep"][0]
    assert [c["name"] for c in keep["children"]] == ["c", "d"]


def test_partial_survival_within_a_dir():
    tree = D("root", [
        D("mix", [F("kept.txt"), D("dead", [])]),
    ])
    expected = D("root", [D("mix", [F("kept.txt")])])
    assert solution.prune(tree, 5) == expected


def test_does_not_mutate_input():
    tree = D("root", [D("a", [F("f")]), D("empty", [])])
    snapshot = copy.deepcopy(tree)
    solution.prune(tree, 2)
    assert tree == snapshot


def test_property_every_surviving_leaf_dir_is_root_and_files_preserved():
    # Invariant checks over random trees:
    #   (1) no non-root "dir" node in the output has empty children;
    #   (2) every file within depth<=max_depth of the input survives, and no
    #       file beyond the cap survives (files never collapse ancestors that
    #       have other surviving content, but here we just check file counts by
    #       recomputing which files are within the cap).
    counter = [0]

    def gen(rng, depth_budget):
        if depth_budget <= 0 or rng.random() < 0.4:
            counter[0] += 1
            return F("f%d" % counter[0])
        n = rng.randint(0, 3)
        counter[0] += 1
        return D("d%d" % counter[0], [gen(rng, depth_budget - 1) for _ in range(n)])

    def surviving_files_expected(node, depth, max_depth):
        # A file survives iff its own depth <= max_depth.
        if node["kind"] == "file":
            return 1 if depth <= max_depth else 0
        if depth >= max_depth:
            return 0  # children would be at depth+1 > max_depth
        return sum(surviving_files_expected(c, depth + 1, max_depth)
                   for c in node["children"])

    def count_files(node):
        if node["kind"] == "file":
            return 1
        return sum(count_files(c) for c in node["children"])

    def surviving_leaf_seq(node, depth, max_depth):
        # Left-to-right pre-order sequence of (name) for every node that
        # survives the depth cap alone (files kept, dirs recursed). This is
        # order-sensitive, so any reordering of children changes the sequence.
        if node["kind"] == "file":
            return [node["name"]] if depth <= max_depth else []
        if depth >= max_depth:
            return []
        seq = []
        for c in node["children"]:
            seq.extend(surviving_leaf_seq(c, depth + 1, max_depth))
        return seq

    def output_leaf_seq(node):
        if node["kind"] == "file":
            return [node["name"]]
        seq = []
        for c in node["children"]:
            seq.extend(output_leaf_seq(c))
        return seq

    def no_empty_nonroot_dirs(node, is_root):
        if node["kind"] == "file":
            return True
        if not is_root and len(node["children"]) == 0:
            return False
        return all(no_empty_nonroot_dirs(c, False) for c in node["children"])

    rng = random.Random(99887766)
    for _ in range(300):
        tree = D("root", [gen(rng, rng.randint(0, 5)) for _ in range(rng.randint(0, 3))])
        md = rng.randint(0, 6)
        out = solution.prune(tree, md)
        # Root always survives with correct identity.
        assert out["name"] == "root" and out["kind"] == "dir"
        # No dangling empty non-root directories.
        assert no_empty_nonroot_dirs(out, True)
        # File preservation matches the independent count.
        assert count_files(out) == surviving_files_expected(tree, 0, md)
        # Left-to-right ordering is preserved at every level: the pre-order
        # sequence of surviving file names in the output equals the sequence
        # obtained by keeping original child order.
        assert output_leaf_seq(out) == surviving_leaf_seq(tree, 0, md)
