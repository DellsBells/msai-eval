from collections import deque


def generations(graph: dict):
    """Partition nodes into longest-path levels, or None if the graph cycles.

    Subtly wrong: assigns each node's level the FIRST time it is reached in a
    breadth-first sweep from the sources and never updates it afterward. This
    computes the *shortest* path length from a source, not the longest one, so
    a node reachable by both a short and a long path is placed too early.
    Cycle detection (via the processed-count check) is still correct.
    """
    if not graph:
        return []

    succ = {u: set(vs) for u, vs in graph.items()}

    indeg = {u: 0 for u in graph}
    for u in succ:
        for v in succ[u]:
            indeg[v] += 1

    level = {u: 0 for u in graph}
    assigned = set(u for u in graph if indeg[u] == 0)
    queue = deque(sorted(assigned))
    processed = 0
    while queue:
        u = queue.popleft()
        processed += 1
        for v in succ[u]:
            if v not in assigned:
                level[v] = level[u] + 1
                assigned.add(v)
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)

    if processed != len(graph):
        return None

    max_level = max(level.values())
    buckets = [[] for _ in range(max_level + 1)]
    for node, lvl in level.items():
        buckets[lvl].append(node)
    for bucket in buckets:
        bucket.sort()
    return buckets
