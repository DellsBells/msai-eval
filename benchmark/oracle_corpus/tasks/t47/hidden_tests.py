import copy
import random

import solution


def N(id_, tags, reports):
    return {"id": id_, "tags": list(tags), "reports": list(reports)}


def test_deep_match():
    tree = N("ceo", ["exec"], [
        N("vp1", ["eng"], [N("e1", ["eng", "oncall"], [])]),
        N("vp2", ["sales"], []),
    ])
    assert solution.first_path_with_tag(tree, "oncall") == ["ceo", "vp1", "e1"]


def test_shallow_later_sibling():
    tree = N("ceo", ["exec"], [
        N("vp1", ["eng"], [N("e1", ["eng"], [])]),
        N("vp2", ["sales"], []),
    ])
    assert solution.first_path_with_tag(tree, "sales") == ["ceo", "vp2"]


def test_root_matches():
    tree = N("solo", ["x", "y"], [])
    assert solution.first_path_with_tag(tree, "y") == ["solo"]


def test_no_match_returns_empty():
    tree = N("r", ["a"], [N("c", ["b"], [])])
    assert solution.first_path_with_tag(tree, "zzz") == []


def test_empty_tags_root():
    tree = N("r", [], [])
    assert solution.first_path_with_tag(tree, "anything") == []


def test_preorder_beats_bfs():
    # The distinguishing case: a deep match in the first subtree must win over
    # a shallow match in a later sibling.
    tree = N("root", [], [
        N("a", [], [N("a1", ["target"], [])]),
        N("b", ["target"], []),
    ])
    assert solution.first_path_with_tag(tree, "target") == ["root", "a", "a1"]


def test_first_of_duplicate_tags():
    # Two nodes carry "dup"; pre-order should pick the earlier one.
    tree = N("root", [], [
        N("left", ["dup"], []),
        N("right", ["dup"], []),
    ])
    assert solution.first_path_with_tag(tree, "dup") == ["root", "left"]


def test_case_sensitive():
    tree = N("root", ["Tag"], [])
    assert solution.first_path_with_tag(tree, "tag") == []
    assert solution.first_path_with_tag(tree, "Tag") == ["root"]


def test_exact_equality_not_substring():
    # Membership is exact string equality, not substring containment. A node
    # tagged "oncall" does NOT match the search "call"; only a node whose tags
    # list literally contains "call" matches.
    tree = N("root", ["oncall"], [
        N("child", ["engineering"], []),
        N("other", ["call"], []),
    ])
    # "call" is a substring of "oncall" but not equal -> the only real match is
    # the node literally tagged "call".
    assert solution.first_path_with_tag(tree, "call") == ["root", "other"]
    # "eng" is a substring of "engineering" but no node is tagged exactly "eng".
    assert solution.first_path_with_tag(tree, "eng") == []
    # A node whose tag merely contains the query as a substring never matches.
    only_super = N("r", ["oncall"], [N("c", ["oncall"], [])])
    assert solution.first_path_with_tag(only_super, "call") == []


def test_does_not_mutate_input():
    tree = N("root", ["a"], [N("c", ["b"], [])])
    snap = copy.deepcopy(tree)
    solution.first_path_with_tag(tree, "b")
    assert tree == snap


def test_property_returned_path_is_valid_and_first():
    # Independent pre-order reference producing (path, node) in visit order.
    def preorder(node, prefix):
        path = prefix + [node["id"]]
        yield path, node
        for child in node["reports"]:
            yield from preorder(child, path)

    # Tags that are proper supersets containing the query "cat" as a substring
    # but are NOT equal to it. A substring-membership implementation would
    # wrongly treat these as matches, so including them alongside the real
    # "cat" tag exercises the exact-equality requirement.
    SUPERSETS = ["category", "scatter", "concat", "cats"]

    def gen(rng, budget, counter):
        cid = "n%d" % counter[0]
        counter[0] += 1
        tags = []
        # Randomly attach the searchable tag (exact "cat") to some nodes.
        if rng.random() < 0.3:
            tags.append("cat")
        # Randomly attach a distractor that merely *contains* "cat" as a
        # substring; these must never be treated as a match.
        if rng.random() < 0.5:
            tags.append(rng.choice(SUPERSETS))
        if rng.random() < 0.4:
            tags.append("other")
        rng.shuffle(tags)
        reports = []
        if budget > 0:
            for _ in range(rng.randint(0, 3)):
                reports.append(gen(rng, budget - 1, counter))
        return N(cid, tags, reports)

    rng = random.Random(13572468)
    for _ in range(200):
        tree = gen(rng, rng.randint(0, 5), [0])
        got = solution.first_path_with_tag(tree, "cat")
        # Compute the true first match via the independent generator, using
        # exact equality (a node matches iff "cat" is literally in its tags).
        expected = []
        for path, node in preorder(tree, []):
            if "cat" in node["tags"]:
                expected = path
                break
        assert got == expected
