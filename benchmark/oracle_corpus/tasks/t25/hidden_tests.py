import random

import solution


def test_simple_dag():
    graph = {
        "a": ["b", "c"],
        "b": ["d"],
        "c": ["d"],
        "d": [],
    }
    assert solution.reachable_from(graph, "a") == {"a", "b", "c", "d"}
    assert solution.reachable_from(graph, "d") == {"d"}


def test_sink_node_reaches_only_itself():
    graph = {"a": ["b"], "b": []}
    assert solution.reachable_from(graph, "b") == {"b"}


def test_start_not_a_key_returns_singleton():
    graph = {1: [2, 3], 2: [1], 3: [4]}
    assert solution.reachable_from(graph, 9) == {9}


def test_successor_not_a_key_is_still_reachable():
    graph = {1: [2, 3], 2: [1], 3: [4]}
    assert solution.reachable_from(graph, 1) == {1, 2, 3, 4}


def test_cycle_terminates():
    graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
    assert solution.reachable_from(graph, "a") == {"a", "b", "c"}


def test_self_loop_and_duplicates():
    graph = {"x": ["y", "y", "x"], "y": []}
    assert solution.reachable_from(graph, "x") == {"x", "y"}


def test_empty_graph():
    assert solution.reachable_from({}, "solo") == {"solo"}


def test_disconnected_component_not_included():
    graph = {"a": ["b"], "b": [], "c": ["d"], "d": []}
    assert solution.reachable_from(graph, "a") == {"a", "b"}


def test_does_not_mutate_graph():
    graph = {"a": ["b"], "b": []}
    snapshot = {k: list(v) for k, v in graph.items()}
    solution.reachable_from(graph, "a")
    assert graph == snapshot
    assert set(graph.keys()) == set(snapshot.keys())


def test_does_not_mutate_graph_with_nonkey_successors():
    # A reached successor ("c") and the start's referenced-but-absent nodes are
    # NOT keys in the graph. The function must not insert them (e.g. via a
    # setdefault-style traversal), add keys, or alter any successor list.
    graph = {"a": ["b", "c"], "b": ["c", "d"]}
    snapshot = {k: list(v) for k, v in graph.items()}
    original_keys = set(graph.keys())
    result = solution.reachable_from(graph, "a")
    assert result == {"a", "b", "c", "d"}
    # No new keys were inserted for the non-key successors "c" and "d".
    assert set(graph.keys()) == original_keys
    assert "c" not in graph
    assert "d" not in graph
    # Existing successor lists are untouched (identity and contents preserved).
    assert graph == snapshot
    assert graph["a"] == ["b", "c"]
    assert graph["b"] == ["c", "d"]


def test_does_not_mutate_graph_when_start_is_nonkey():
    # start itself is not a key. It must not be inserted as a new key.
    graph = {"a": ["b"], "b": []}
    snapshot = {k: list(v) for k, v in graph.items()}
    original_keys = set(graph.keys())
    result = solution.reachable_from(graph, "z")
    assert result == {"z"}
    assert set(graph.keys()) == original_keys
    assert "z" not in graph
    assert graph == snapshot


def test_property_reachable_is_transitively_closed():
    # For random small graphs: if u is reachable from start and v is a direct
    # successor of u, then v must also be in the reachable set.
    rng = random.Random(20240607)
    for _ in range(200):
        n = rng.randint(1, 8)
        nodes = list(range(n))
        graph = {}
        for u in nodes:
            outdeg = rng.randint(0, 3)
            graph[u] = [rng.randrange(n) for _ in range(outdeg)]
        start = rng.randrange(n)
        result = solution.reachable_from(graph, start)
        assert start in result
        for u in result:
            for v in graph.get(u, ()):
                assert v in result
