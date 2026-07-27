from collections import deque


def generations(graph: dict):
    """Partition nodes into longest-path levels, or None if the graph cycles."""
    if not graph:
        return []

    # Collapse duplicate edges.
    succ = {u: set(vs) for u, vs in graph.items()}

    indeg = {u: 0 for u in graph}
    for u in succ:
        for v in succ[u]:
            indeg[v] += 1

    # Kahn's algorithm; longest-path level via relaxation.
    level = {u: 0 for u in graph}
    queue = deque(u for u in graph if indeg[u] == 0)
    processed = 0
    while queue:
        u = queue.popleft()
        processed += 1
        for v in succ[u]:
            if level[u] + 1 > level[v]:
                level[v] = level[u] + 1
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)

    if processed != len(graph):
        # Some nodes never reached in-degree 0 -> cycle.
        return None

    max_level = max(level.values())
    buckets = [[] for _ in range(max_level + 1)]
    for node, lvl in level.items():
        buckets[lvl].append(node)
    for bucket in buckets:
        bucket.sort()
    return buckets
