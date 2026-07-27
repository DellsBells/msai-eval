def reachable_from(graph: dict, start) -> set:
    """Return the set of nodes reachable from ``start`` (inclusive).

    Subtly wrong: only enqueues successors that are themselves keys in the
    graph, so reachable nodes that are named as successors but have no entry
    of their own are dropped.
    """
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for succ in graph.get(node, ()):
            if succ in graph and succ not in visited:
                stack.append(succ)
    return visited
