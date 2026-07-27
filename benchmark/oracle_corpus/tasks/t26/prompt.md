# Deterministic Topological Order

Implement a function that returns a topological ordering of a directed acyclic
graph, using a fixed tie-breaking rule so the output is fully deterministic.

## Function signature

```python
def topo_order(graph: dict) -> list:
    ...
```

## Input

- `graph` is a `dict` mapping each node to a `list` of its direct successors
  (nodes it has an outgoing edge to). Every node of the graph appears as a key,
  including sink nodes, whose value is an empty list. You may assume every
  successor named in some list is also present as a key.
- All node keys are mutually comparable with `<` (for the tests they are all
  strings, or all integers). This lets you break ties by the natural ordering of
  the nodes.

## Behavior

Return a `list` containing every node exactly once such that for every edge
`u -> v`, `u` appears before `v` in the list.

When more than one node could legally come next, always choose the one that is
**smallest by natural ordering** (`min`). Concretely, use Kahn's algorithm:

1. Compute the in-degree of every node.
2. Repeatedly, among all nodes whose in-degree is currently `0` and which have
   not yet been output, remove the **smallest** one, append it to the result,
   and decrement the in-degree of each of its successors.
3. Continue until all nodes are output.

Rules and edge cases:

1. The empty graph (`{}`) returns `[]`.
2. A graph with nodes but no edges returns all nodes sorted in ascending natural
   order.
3. The input graph must not be mutated.
4. You may assume the graph is acyclic; you do not need to detect cycles.
5. If a successor list contains a **duplicate edge** (the same `u -> v` listed
   twice), treat it as a single edge: it must not distort the in-degree
   bookkeeping in a way that changes the result. (Two distinct listings of the
   same edge should be collapsed.)

## Examples

Example 1:

```python
graph = {
    "shirt": ["tie", "belt"],
    "tie":   ["jacket"],
    "belt":  ["jacket"],
    "jacket": [],
}
topo_order(graph)
# -> ["shirt", "belt", "tie", "jacket"]
# (after "shirt", both "belt" and "tie" are available; "belt" < "tie")
```

Example 2 (no edges -> sorted):

```python
graph = {3: [], 1: [], 2: []}
topo_order(graph)   # -> [1, 2, 3]
```

Example 3 (duplicate edge is collapsed):

```python
graph = {"a": ["b", "b"], "b": []}
topo_order(graph)   # -> ["a", "b"]
```

## Constraints

- Standard library only.
- At most a few thousand nodes and edges.
- The output is a `list` of length equal to the number of keys in `graph`.
