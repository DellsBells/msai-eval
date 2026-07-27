def generations(graph: dict) -> list | None:
    from collections import deque

    in_degree = {node: 0 for node in graph}
    for node in graph:
        for successor in graph[node]:
            in_degree[successor] += 1

    zero_in_degree_queue = deque([node for node, degree in in_degree.items() if degree == 0])
    levels = {}
    level = 0

    while zero_in_degree_queue:
        current_level_size = len(zero_in_degree_queue)
        for _ in range(current_level_size):
            node = zero_in_degree_queue.popleft()
            levels[node] = level
            for successor in graph[node]:
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    zero_in_degree_queue.append(successor)
        level += 1

    if len(levels) != len(graph):
        return None

    max_level = max(levels.values())
    result = [[] for _ in range(max_level + 1)]
    for node, lvl in levels.items():
        result[lvl].append(node)

    for layer in result:
        layer.sort()

    return result