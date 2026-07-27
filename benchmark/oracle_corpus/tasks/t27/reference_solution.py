def find_cycle(graph: dict):
    """Return one directed cycle as a list of nodes, or None.

    Deterministic DFS: start nodes in ascending order, neighbors in ascending
    order. Returns [w, ..., u] where u -> w closes the cycle.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def neighbors(node):
        return sorted(graph[node])

    for start in sorted(graph.keys()):
        if color[start] != WHITE:
            continue
        # Iterative DFS carrying the explicit path.
        path = []
        # Stack of (node, iterator over its neighbors).
        stack = [(start, iter(neighbors(start)))]
        color[start] = GRAY
        path.append(start)
        while stack:
            node, it = stack[-1]
            advanced = False
            for w in it:
                if color[w] == GRAY:
                    # w is on the current path -> cycle from w to node.
                    idx = path.index(w)
                    return path[idx:]
                if color[w] == WHITE:
                    color[w] = GRAY
                    path.append(w)
                    stack.append((w, iter(neighbors(w))))
                    advanced = True
                    break
                # BLACK -> already fully explored, skip.
            if not advanced:
                # Done with this node.
                stack.pop()
                color[node] = BLACK
                path.pop()
    return None
