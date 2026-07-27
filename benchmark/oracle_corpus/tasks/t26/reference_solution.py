import heapq


def topo_order(graph: dict) -> list:
    """Return a deterministic (smallest-first) topological ordering."""
    # Collapse duplicate edges: successors of each node become a set.
    succ = {node: set(neighbors) for node, neighbors in graph.items()}

    indeg = {node: 0 for node in graph}
    for node, neighbors in succ.items():
        for v in neighbors:
            indeg[v] += 1

    heap = [node for node in graph if indeg[node] == 0]
    heapq.heapify(heap)

    result = []
    while heap:
        u = heapq.heappop(heap)
        result.append(u)
        for v in sorted(succ[u]):
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    return result
