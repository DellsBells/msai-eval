def reachable_from(graph: dict, start) -> set:
    """Return the set of nodes reachable from ``start`` (inclusive)."""
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for succ in graph.get(node, ()):
            if succ not in visited:
                stack.append(succ)
    return visited
