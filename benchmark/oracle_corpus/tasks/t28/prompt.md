# Topological Generations (Longest-Path Layers)

Partition the nodes of a directed graph into ordered "generations" (layers)
based on dependency depth, or report that the graph has a cycle.

## Function signature

```python
def generations(graph: dict) -> list | None:
    ...
```

## Input

- `graph` is a `dict` mapping each node to a `list` of its direct successors
  (nodes it has an outgoing edge to). Every node appears as a key (sinks map to
  an empty list); every successor named in a list is also a key.
- Node keys are mutually comparable with `<` (in the tests they are all strings
  or all integers).

## Definitions

For an acyclic graph, define the **level** of a node as the length of the
*longest* directed path that ends at that node:

- A node with no incoming edges (no predecessors) has level `0`.
- Otherwise, `level(v) = 1 + max(level(u) for every edge u -> v)`.

Generation `i` is the sorted list of all nodes whose level equals `i`.

## Behavior

- If the graph contains a **cycle**, return `None`.
- Otherwise return a `list` of generations: element `i` is the **ascending
  sorted list** of all nodes with level `i`. Because at least one node has
  level 0 (any non-empty acyclic graph has a source), and levels are contiguous
  from 0 up to the maximum, no returned generation is empty.

Edge cases and rules:

1. The empty graph (`{}`) returns `[]` (an empty list of generations).
2. A graph with nodes but no edges returns a single generation containing all
   nodes sorted ascending: `[[all nodes sorted]]`.
3. A self-loop makes the graph cyclic, so return `None`.
4. **Duplicate edges** (the same `u -> v` listed twice) must not affect the
   result; treat them as a single edge.
5. The input graph must not be mutated. Neither the outer `dict` nor any of
   its successor `list` values may be changed in any way (no reordering, no
   in-place deduplication, no sorting). After the call, the caller's graph must
   be identical to what was passed in, on both the success and cycle paths.

## Examples

Example 1 (diamond):

```python
graph = {
    "a": ["b", "c"],
    "b": ["d"],
    "c": ["d"],
    "d": [],
}
generations(graph)
# level(a)=0, level(b)=1, level(c)=1, level(d)=2
# -> [["a"], ["b", "c"], ["d"]]
```

Example 2 (long path dominates):

```python
graph = {
    "a": ["b", "d"],
    "b": ["c"],
    "c": ["d"],
    "d": [],
}
generations(graph)
# level(a)=0, level(b)=1, level(c)=2, level(d)=3
# (d's level is 3 via a->b->c->d, not 1 via a->d)
# -> [["a"], ["b"], ["c"], ["d"]]
```

Example 3 (no edges):

```python
graph = {2: [], 1: [], 3: []}
generations(graph)   # -> [[1, 2, 3]]
```

Example 4 (cycle):

```python
graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
generations(graph)   # -> None
```

## Constraints

- Standard library only.
- At most a few thousand nodes and edges.
- Return a `list` of lists of nodes, or `None`.
