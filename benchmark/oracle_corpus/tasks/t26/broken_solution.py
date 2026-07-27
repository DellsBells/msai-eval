import heapq


def topo_order(graph: dict) -> list:
    """Return a deterministic (smallest-first) topological ordering.

    Subtly wrong: in-degree is counted from the raw successor lists (so a
    duplicated edge inflates the in-degree), but each node is only decremented
    once per distinct successor. A node that is the target of a duplicated edge
    never reaches in-degree 0 and is silently dropped from the output.
    """
    indeg = {node: 0 for node in graph}
    for node, neighbors in graph.items():
        for v in neighbors:
            indeg[v] += 1

    heap = [node for node in graph if indeg[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in sorted(set(graph[u])):
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    return result
