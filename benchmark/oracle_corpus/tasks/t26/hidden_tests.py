import copy
import random

import solution


def _is_valid_topo(graph, order):
    # Every node exactly once.
    if sorted(order, key=repr) != sorted(graph.keys(), key=repr):
        return False
    pos = {node: i for i, node in enumerate(order)}
    for u, neighbors in graph.items():
        for v in neighbors:
            if pos[u] >= pos[v]:
                return False
    return True


def test_diamond_tiebreak():
    graph = {
        "shirt": ["tie", "belt"],
        "tie": ["jacket"],
        "belt": ["jacket"],
        "jacket": [],
    }
    assert solution.topo_order(graph) == ["shirt", "belt", "tie", "jacket"]


def test_no_edges_returns_sorted():
    graph = {3: [], 1: [], 2: []}
    assert solution.topo_order(graph) == [1, 2, 3]


def test_empty_graph():
    assert solution.topo_order({}) == []


def test_single_node():
    assert solution.topo_order({"only": []}) == ["only"]


def test_duplicate_edge_collapsed():
    graph = {"a": ["b", "b"], "b": []}
    assert solution.topo_order(graph) == ["a", "b"]


def test_duplicate_edge_in_larger_graph():
    graph = {
        "a": ["c", "c"],
        "b": ["c"],
        "c": [],
    }
    order = solution.topo_order(graph)
    assert order == ["a", "b", "c"]


def test_linear_chain():
    graph = {"d": [], "c": ["d"], "b": ["c"], "a": ["b"]}
    assert solution.topo_order(graph) == ["a", "b", "c", "d"]


def test_smallest_first_when_multiple_sources():
    # Two independent sources; smaller must come first.
    graph = {"z": ["m"], "a": ["m"], "m": []}
    assert solution.topo_order(graph) == ["a", "z", "m"]


def test_integers_ordering():
    graph = {1: [3], 2: [3], 3: [4], 4: []}
    assert solution.topo_order(graph) == [1, 2, 3, 4]


def test_input_graph_not_mutated_diamond():
    graph = {
        "shirt": ["tie", "belt"],
        "tie": ["jacket"],
        "belt": ["jacket"],
        "jacket": [],
    }
    before = copy.deepcopy(graph)
    solution.topo_order(graph)
    # The keys, the successor lists, and their contents/order must be untouched.
    assert graph == before


def test_input_graph_not_mutated_with_duplicate_edge():
    # A destructive in-place dedup would rewrite ["b", "b"] to ["b"]; a
    # destructive Kahn's would empty the lists. Both must be rejected.
    graph = {"a": ["b", "b"], "b": ["c"], "c": []}
    before = copy.deepcopy(graph)
    solution.topo_order(graph)
    assert graph == before
    # Successor lists must still be the exact same list objects' contents.
    assert graph["a"] == ["b", "b"]
    assert graph["b"] == ["c"]
    assert graph["c"] == []


def test_repeated_calls_are_independent():
    # If the first call mutated the graph destructively, the second call would
    # see a corrupted graph and return a different (shorter/wrong) result.
    graph = {
        "a": ["b", "c"],
        "b": ["d"],
        "c": ["d"],
        "d": ["e"],
        "e": [],
    }
    first = solution.topo_order(graph)
    second = solution.topo_order(graph)
    third = solution.topo_order(graph)
    assert first == ["a", "b", "c", "d", "e"]
    assert first == second == third


def test_property_valid_topo_over_random_dags():
    rng = random.Random(99001)
    for _ in range(200):
        n = rng.randint(1, 9)
        # Build a random DAG by only allowing edges from lower to higher index.
        perm = list(range(n))
        rng.shuffle(perm)
        graph = {node: [] for node in range(n)}
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < 0.4:
                    # edge from perm[i] to perm[j] respects a fixed order.
                    graph[perm[i]].append(perm[j])
        snapshot = copy.deepcopy(graph)
        order = solution.topo_order(graph)
        # Result must be a valid topo order of the ORIGINAL graph, and the
        # input graph must be left exactly as it was passed in.
        assert graph == snapshot
        assert _is_valid_topo(graph, order)


def test_property_matches_greedy_min_reference():
    # Independent slow reference: repeatedly pick smallest zero-in-degree node.
    def slow(graph):
        indeg = {u: 0 for u in graph}
        succ = {u: set(vs) for u, vs in graph.items()}
        for u in succ:
            for v in succ[u]:
                indeg[v] += 1
        out = []
        remaining = set(graph)
        while remaining:
            avail = sorted(u for u in remaining if indeg[u] == 0)
            u = avail[0]
            out.append(u)
            remaining.discard(u)
            for v in succ[u]:
                indeg[v] -= 1
        return out

    rng = random.Random(5150)
    for _ in range(150):
        n = rng.randint(1, 8)
        graph = {node: [] for node in range(n)}
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < 0.5:
                    graph[i].append(j)
        assert solution.topo_order(graph) == slow(graph)
