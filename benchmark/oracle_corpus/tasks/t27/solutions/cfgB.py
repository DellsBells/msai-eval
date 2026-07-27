from typing import Dict, List

def find_cycle(graph: Dict[str, List[str]]) -> List[str] | None:
    def dfs(node: str, visited: Set[str], visiting: Set[str]) -> bool:
        if node in visiting:
            return True  # Cycle detected!
        visiting.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited and dfs(neighbor, visited, visiting):
                return True
        visiting.remove(node)  # Backtrack
        return False

    visited = set()
    for node in graph:
        if node not in visited:
            visiting = set([node])
            if dfs(node, visited, visiting):
                cycle = [node]
                while True:
                    node = list(visiting)[0]
                    cycle.append(node)
                    visiting.remove(node)
                    if node == cycle[0]:
                        break
                return cycle[::-1]  # Reverse to match the example order

    return None

# Example usage:
graph = {
    "a": ["b"],
    "b": ["c"],
    "c": ["a"],
}
print(find_cycle(graph))   # -> ["a", "b", "c"]

graph = {"x": ["x"], "y": []}
print(find_cycle(graph))   # -> ["x"]

graph = {"a": ["b", "c"], "b": ["c"], "c": []}
print(find_cycle(graph))   # -> None

graph = {
    1: [2, 3],
    2: [1],       # back-edge to 1 forms cycle [1, 2]
    3: [1],       # would also form a cycle, but 2 is explored first
}
print(find_cycle(graph))   # -> [1, 2]