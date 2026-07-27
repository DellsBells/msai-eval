from collections import deque

def reachable_from(graph: dict, start) -> set:
    if not graph or start not in graph:
        return {start}
    
    visited = set()
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return visited