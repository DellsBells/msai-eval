# Reachable Nodes in a Directed Graph

Implement a function that computes the set of nodes reachable from a given start
node in a directed graph.

## Function signature

```python
def reachable_from(graph: dict, start) -> set:
    ...
```

## Input

- `graph` is a `dict` mapping each node to a `list` of its direct successors
  (the nodes it has an outgoing edge to). Nodes may be any hashable value
  (commonly strings or integers).
- `start` is a node.

## Behavior

Return a `set` containing every node that can be reached from `start` by
following zero or more directed edges.

Rules and edge cases:

1. **`start` is always included** in the result, because a node reaches itself
   with zero edges. This holds even when `start` has no outgoing edges, and even
   when `start` is not a key in `graph`.
2. A node's successor list may name a node that is **not itself a key** in
   `graph`. Such a node is still reachable (include it), but it is treated as
   having no outgoing edges of its own.
3. The graph may contain **cycles**; your traversal must terminate and must not
   revisit nodes.
4. **Duplicate entries** in a successor list must not cause problems and must not
   duplicate work incorrectly.
5. If `start` is not a key in `graph` and appears nowhere else, the result is
   exactly `{start}`.
6. `graph` is never mutated by your function. Do not add, remove, or reorder
   keys, and do not modify any successor list. In particular, when you encounter
   a node that is not a key (a non-key successor, or a `start` that is absent),
   treat it as having no successors **without inserting it into `graph`** — the
   dict's set of keys and every successor list must be identical before and
   after the call.

## Examples

Example 1:

```python
graph = {
    "a": ["b", "c"],
    "b": ["d"],
    "c": ["d"],
    "d": [],
}
reachable_from(graph, "a")   # -> {"a", "b", "c", "d"}
reachable_from(graph, "d")   # -> {"d"}
```

Example 2 (successor not a key, plus a cycle):

```python
graph = {
    1: [2, 3],
    2: [1],       # cycle 1 <-> 2
    3: [4],       # 4 is not a key
}
reachable_from(graph, 1)     # -> {1, 2, 3, 4}
reachable_from(graph, 9)     # -> {9}   (9 is not in the graph)
```

Example 3 (duplicates and self-loop):

```python
graph = {
    "x": ["y", "y", "x"],
    "y": [],
}
reachable_from(graph, "x")   # -> {"x", "y"}
```

## Constraints

- Standard library only.
- The graph has at most a few thousand nodes and edges.
- Return a `set`. The result must contain exactly the reachable nodes, no more
  and no fewer.
