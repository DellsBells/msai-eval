import random

import solution


def _is_valid_cycle(graph, cyc):
    if not isinstance(cyc, list) or len(cyc) == 0:
        return False
    # No repeated node in the reported cycle.
    if len(set(cyc)) != len(cyc):
        return False
    k = len(cyc)
    for i in range(k):
        u = cyc[i]
        w = cyc[(i + 1) % k]
        if w not in graph.get(u, []):
            return False
    return True


def _has_cycle_kahn(graph):
    # Independent acyclicity check via Kahn's algorithm.
    indeg = {u: 0 for u in graph}
    succ = {u: set(vs) for u, vs in graph.items()}
    for u in succ:
        for v in succ[u]:
            indeg[v] += 1
    queue = [u for u in graph if indeg[u] == 0]
    removed = 0
    while queue:
        u = queue.pop()
        removed += 1
        for v in succ[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return removed != len(graph)


def test_simple_three_cycle():
    graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
    assert solution.find_cycle(graph) == ["a", "b", "c"]


def test_self_loop():
    graph = {"x": ["x"], "y": []}
    assert solution.find_cycle(graph) == ["x"]


def test_acyclic_returns_none():
    graph = {"a": ["b", "c"], "b": ["c"], "c": []}
    assert solution.find_cycle(graph) is None


def test_empty_graph_returns_none():
    assert solution.find_cycle({}) is None


def test_deterministic_tiebreak():
    graph = {1: [2, 3], 2: [1], 3: [1]}
    assert solution.find_cycle(graph) == [1, 2]


def test_cycle_not_at_first_start_node():
    # "a" leads into a cycle among b, c but "a" itself is not part of it.
    graph = {"a": ["b"], "b": ["c"], "c": ["b"]}
    assert solution.find_cycle(graph) == ["b", "c"]


def test_single_node_no_edges():
    assert solution.find_cycle({"solo": []}) is None


def test_disconnected_cycle_found():
    graph = {"a": [], "b": ["c"], "c": ["b"]}
    assert solution.find_cycle(graph) == ["b", "c"]


def test_returned_cycle_has_no_repeated_nodes():
    graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
    cyc = solution.find_cycle(graph)
    assert len(cyc) == len(set(cyc))
    assert _is_valid_cycle(graph, cyc)


def test_tiebreak_among_multiple_onpath_successors():
    # Node 2 has TWO successors already on the DFS path: 0 and 1. Visiting
    # successors in ascending order, edge 2 -> 0 is traversed first, so the
    # cycle closes on 0: [0, 1, 2]. A variant that instead closes on the
    # nearest/last on-path node (shortest cycle) would return [1, 2].
    graph = {0: [1], 1: [2], 2: [0, 1]}
    assert solution.find_cycle(graph) == [0, 1, 2]


def test_tiebreak_prefers_smallest_onpath_over_shortest_cycle():
    # Node 3 sees three on-path successors [0, 1, 2]; ascending order closes on
    # 0, giving the LONGEST cycle [0, 1, 2, 3], not the shortest [2, 3].
    graph = {0: [1], 1: [2], 2: [3], 3: [0, 1, 2]}
    assert solution.find_cycle(graph) == [0, 1, 2, 3]


def test_tiebreak_among_onpath_successors_strings():
    # Same rule with string nodes: c's on-path successors are ["a", "b"];
    # ascending order closes on "a" -> ["a", "b", "c"], not ["b", "c"].
    graph = {"a": ["b"], "b": ["c"], "c": ["a", "b"]}
    assert solution.find_cycle(graph) == ["a", "b", "c"]


def _find_cycle_ref(graph):
    # Independent recursive reference implementing the mandated deterministic
    # DFS: start nodes ascending, successors ascending, close on the FIRST
    # (smallest) successor already on the current path.
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    path = []
    found = [None]

    def dfs(u):
        color[u] = GRAY
        path.append(u)
        for w in sorted(graph[u]):
            if found[0] is not None:
                break
            if color.get(w) == GRAY:
                idx = path.index(w)
                found[0] = path[idx:]
                break
            if color.get(w) == WHITE:
                dfs(w)
        if found[0] is None:
            color[u] = BLACK
        path.pop()

    for start in sorted(graph.keys()):
        if color[start] == WHITE:
            dfs(start)
            if found[0] is not None:
                return found[0]
    return None


def test_property_exact_match_deterministic_reference():
    # Stronger property: the EXACT returned cycle must equal an independent
    # deterministic reference, so a wrong tie-break among on-path successors is
    # caught even when it still yields a valid cycle. Grids are biased toward
    # nodes with several back-edges to exercise the tie-break.
    rng = random.Random(24680)
    for _ in range(300):
        n = rng.randint(1, 8)
        graph = {node: [] for node in range(n)}
        for u in range(n):
            for _ in range(rng.randint(0, 4)):
                graph[u].append(rng.randrange(n))
        got = solution.find_cycle(graph)
        expected = _find_cycle_ref(graph)
        assert got == expected, (graph, got, expected)


def test_property_result_agrees_with_kahn():
    rng = random.Random(31337)
    for _ in range(300):
        n = rng.randint(1, 8)
        graph = {node: [] for node in range(n)}
        for u in range(n):
            for _ in range(rng.randint(0, 3)):
                graph[u].append(rng.randrange(n))
        result = solution.find_cycle(graph)
        expected_has_cycle = _has_cycle_kahn(graph)
        if result is None:
            assert not expected_has_cycle
        else:
            assert expected_has_cycle
            assert _is_valid_cycle(graph, result)
