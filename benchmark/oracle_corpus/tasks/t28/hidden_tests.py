import copy
import random

import solution


def _reference_generations(graph):
    # Independent longest-path level computation via memoized DFS.
    # Returns None on cycle.
    succ = {u: set(vs) for u, vs in graph.items()}
    if not graph:
        return []
    # preds
    preds = {u: set() for u in graph}
    for u in succ:
        for v in succ[u]:
            preds[v].add(u)

    VISITING, DONE = 1, 2
    state = {}
    level = {}

    def longest(u):
        if state.get(u) == DONE:
            return level[u]
        if state.get(u) == VISITING:
            raise ValueError("cycle")
        state[u] = VISITING
        best = 0
        for p in preds[u]:
            best = max(best, longest(p) + 1)
        level[u] = best
        state[u] = DONE
        return best

    try:
        for u in graph:
            longest(u)
    except ValueError:
        return None

    max_level = max(level.values())
    buckets = [[] for _ in range(max_level + 1)]
    for node, lvl in level.items():
        buckets[lvl].append(node)
    for b in buckets:
        b.sort()
    return buckets


def test_diamond():
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    assert solution.generations(graph) == [["a"], ["b", "c"], ["d"]]


def test_long_path_dominates():
    graph = {"a": ["b", "d"], "b": ["c"], "c": ["d"], "d": []}
    assert solution.generations(graph) == [["a"], ["b"], ["c"], ["d"]]


def test_no_edges_single_generation():
    graph = {2: [], 1: [], 3: []}
    assert solution.generations(graph) == [[1, 2, 3]]


def test_empty_graph():
    assert solution.generations({}) == []


def test_cycle_returns_none():
    graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
    assert solution.generations(graph) is None


def test_self_loop_is_cycle():
    graph = {"x": ["x"], "y": []}
    assert solution.generations(graph) is None


def test_single_node():
    assert solution.generations({"only": []}) == [["only"]]


def test_duplicate_edge_ignored():
    graph = {"a": ["b", "b"], "b": ["c"], "c": []}
    assert solution.generations(graph) == [["a"], ["b"], ["c"]]


def test_input_not_mutated_with_duplicate_edges():
    # A duplicate edge is the natural place to mutate the input (in-place
    # dedup). The graph -- including every successor list -- must be left
    # exactly as the caller passed it, both keys and list contents/order.
    graph = {"a": ["b", "b", "c"], "b": ["c"], "c": []}
    before = copy.deepcopy(graph)
    solution.generations(graph)
    assert graph == before
    # The successor list objects must still hold their original contents,
    # in the original order (no dedup, sort, or reordering in place).
    assert graph["a"] == ["b", "b", "c"]
    assert graph["b"] == ["c"]
    assert graph["c"] == []


def test_input_not_mutated_on_cycle():
    # Even on the None (cycle) path the input must be untouched.
    graph = {"a": ["b", "b"], "b": ["c"], "c": ["a"]}
    before = copy.deepcopy(graph)
    assert solution.generations(graph) is None
    assert graph == before
    assert graph["a"] == ["b", "b"]


def test_multiple_sources_and_sinks():
    graph = {
        "a": ["c"],
        "b": ["c"],
        "c": ["d", "e"],
        "d": [],
        "e": [],
    }
    # level: a=0, b=0, c=1, d=2, e=2
    assert solution.generations(graph) == [["a", "b"], ["c"], ["d", "e"]]


def test_levels_within_generation_are_sorted():
    graph = {"z": [], "a": [], "m": []}
    gens = solution.generations(graph)
    assert gens == [["a", "m", "z"]]


def test_property_matches_reference_on_random_dags():
    rng = random.Random(70707)
    for _ in range(200):
        n = rng.randint(1, 9)
        graph = {node: [] for node in range(n)}
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < 0.45:
                    graph[i].append(j)
                    # Occasionally add a duplicate edge so the invariant below
                    # also exercises in-place deduplication.
                    if rng.random() < 0.3:
                        graph[i].append(j)
        before = copy.deepcopy(graph)
        assert solution.generations(graph) == _reference_generations(graph)
        # Invariant: computing generations never mutates the input graph.
        assert graph == before


def test_property_cycles_detected_on_random_graphs():
    rng = random.Random(24680)
    for _ in range(200):
        n = rng.randint(1, 7)
        graph = {node: [] for node in range(n)}
        for u in range(n):
            for _ in range(rng.randint(0, 2)):
                graph[u].append(rng.randrange(n))
        got = solution.generations(graph)
        expected = _reference_generations(graph)
        assert got == expected
