# Find a Cycle in a Directed Graph

Implement a function that finds one directed cycle in a graph, or reports that
none exists, using a fixed, deterministic search order.

## Function signature

```python
def find_cycle(graph: dict) -> list | None:
    ...
```

## Input

- `graph` is a `dict` mapping each node to a `list` of its direct successors.
  Every node appears as a key (sinks map to an empty list); every successor
  named in a list is also a key.
- Node keys are mutually comparable with `<` (in the tests they are all strings
  or all integers), so the search can be made deterministic by always visiting
  neighbors in ascending order.

## Behavior

Return one directed cycle if the graph contains one, otherwise return `None`.

A returned cycle is a `list` of nodes `[v0, v1, ..., v(k-1)]` (`k >= 1`) such
that there is an edge `v0 -> v1`, `v1 -> v2`, ..., `v(k-2) -> v(k-1)`, and a
closing edge `v(k-1) -> v0`. The list contains each cycle node **once**; the
closing edge back to `v0` is implied and `v0` is **not** repeated at the end.

To make the answer deterministic, run a depth-first search with the following
fixed rules:

1. Consider start nodes in **ascending sorted order** of the graph's keys.
2. From any node, visit its successors in **ascending sorted order**. (If a
   successor list contains duplicates, that does not change the search — visiting
   an already-considered edge target behaves the same the second time.)
3. Maintain the current DFS path (the stack of nodes from the start to the node
   being expanded). The first time you traverse an edge `u -> w` where `w` is
   already on the current path, you have found a cycle: return the portion of the
   path starting at `w` and ending at `u`, i.e. `[w, ..., u]`.
4. Nodes fully explored without finding a cycle are not revisited.

Edge cases:

1. A **self-loop** (`u -> u`) is a cycle of length 1: return `[u]`.
2. The empty graph (`{}`) has no cycle: return `None`.
3. A DAG returns `None`.
4. The input graph must not be mutated.

## Examples

Example 1 (simple 3-cycle):

```python
graph = {
    "a": ["b"],
    "b": ["c"],
    "c": ["a"],
}
find_cycle(graph)   # -> ["a", "b", "c"]
```

Example 2 (self-loop):

```python
graph = {"x": ["x"], "y": []}
find_cycle(graph)   # -> ["x"]
```

Example 3 (acyclic):

```python
graph = {"a": ["b", "c"], "b": ["c"], "c": []}
find_cycle(graph)   # -> None
```

Example 4 (deterministic choice):

```python
graph = {
    1: [2, 3],
    2: [1],       # back-edge to 1 forms cycle [1, 2]
    3: [1],       # would also form a cycle, but 2 is explored first
}
find_cycle(graph)   # -> [1, 2]
```

## Constraints

- Standard library only.
- At most a few thousand nodes and edges.
- Return the cycle as a `list`, or `None`.
