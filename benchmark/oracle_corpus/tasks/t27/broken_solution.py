def find_cycle(graph: dict):
    """Return one directed cycle as a list of nodes, or None.

    Subtly wrong: when a cycle is found, it appends the closing node again at
    the end, returning [w, ..., u, w] instead of [w, ..., u]. Cycle detection
    (returning None vs. a cycle) is correct, but the shape of a returned cycle
    repeats the start node.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def neighbors(node):
        return sorted(graph[node])

    for start in sorted(graph.keys()):
        if color[start] != WHITE:
            continue
        path = []
        stack = [(start, iter(neighbors(start)))]
        color[start] = GRAY
        path.append(start)
        while stack:
            node, it = stack[-1]
            advanced = False
            for w in it:
                if color[w] == GRAY:
                    idx = path.index(w)
                    return path[idx:] + [w]
                if color[w] == WHITE:
                    color[w] = GRAY
                    path.append(w)
                    stack.append((w, iter(neighbors(w))))
                    advanced = True
                    break
            if not advanced:
                stack.pop()
                color[node] = BLACK
                path.pop()
    return None
