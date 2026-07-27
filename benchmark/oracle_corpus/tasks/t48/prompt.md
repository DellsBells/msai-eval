# Wildcard Path Query Over Nested Dicts and Lists

You are given a JSON-like value `data` built only from these Python types:
`dict` (string keys), `list`, `int`, `float`, `str`, `bool`, and `None`. It
forms a tree: dicts and lists are internal nodes, and scalars
(`int`/`float`/`str`/`bool`/`None`) are leaves.

You must implement a small path-query language and one function:

```python
def query(data, pattern):
    ...
```

`pattern` is a `list` of **steps**. Starting from `data` (the root), each step
advances the set of currently-matched nodes to a new set of nodes. `query`
returns the `list` of **values at the nodes matched after the final step**, in
**document order** (defined below). Return a new list; do not mutate `data`.

## Step types

Each step is one of:

1. A **string key** `k` (any string that is not one of the wildcards below):
   from each current node that is a `dict` containing key `k`, advance to
   `node[k]`. Current nodes that are not dicts, or dicts lacking key `k`, are
   dropped (they contribute nothing).

2. An **integer index** `i` (a Python `int`, and `bool` is *not* allowed here —
   only true ints): from each current node that is a `list` with
   `0 <= i < len(node)`, advance to `node[i]`. Out-of-range indices and
   non-list current nodes contribute nothing. Negative indices are **not**
   supported and match nothing.

3. The string `"*"` (single-level wildcard): from each current node,
   advance to **all** of its direct children — every value of a `dict` (in the
   dict's insertion order) and every element of a `list` (in list order).
   Scalar current nodes have no children and contribute nothing.

4. The string `"**"` (recursive descendant-or-self wildcard): from each current
   node, advance to that node **and every node reachable beneath it**
   (all descendants at any depth, plus the node itself), in document order (see
   below). Each reachable node is produced **once**.

## Document order

"Document order" is the order of a **pre-order** traversal of the tree: a node
comes before its children; a dict's children are ordered by the dict's insertion
order of keys; a list's children are ordered by index. When a step produces
matches, they must come out in the document order of the *whole tree*, i.e. the
order in which those nodes would be visited by a single pre-order walk of
`data`.

Two subtleties:

- After a `"**"` step you may reach the same underlying node through only one
  route (there are no shared references in the input — it is a pure tree), so
  **de-duplication is by identity of tree position**: never emit the same tree
  node twice within one step's output. Concretely, `["**"]` on any input lists
  every node of the tree exactly once, in pre-order, with the root first.
- The empty pattern `[]` matches the root itself: `query(data, [])` returns
  `[data]`.

## Result values

The returned list contains the **values** at the final matched nodes (the actual
sub-objects — dicts, lists, or scalars — by reference into `data`, not copies).
Order is document order. If nothing matches, return `[]`.

## Examples

Example 1 (keys and index):

```python
data = {"a": {"b": [10, 20, 30]}}
query(data, ["a", "b", 1])          # -> [20]
query(data, ["a", "b"])             # -> [[10, 20, 30]]
query(data, ["a", "x"])             # -> []        (no key "x")
query(data, ["a", "b", 5])          # -> []        (index out of range)
```

Example 2 (single-level wildcard):

```python
data = {"users": [{"n": "amy"}, {"n": "bo"}]}
query(data, ["users", "*", "n"])    # -> ["amy", "bo"]
query(data, ["users", "*"])         # -> [{"n": "amy"}, {"n": "bo"}]
```

Example 3 (recursive wildcard then key):

```python
data = {
    "team": {
        "lead": {"name": "amy", "reports": [{"name": "bo"}, {"name": "cy"}]},
    }
}
query(data, ["**", "name"])         # -> ["amy", "bo", "cy"]
# "**" visits every node in pre-order; the "name" step then keeps, from each,
# the value under key "name" where present, in document order.
```

Example 4 (root and star at root):

```python
data = [1, 2, 3]
query(data, [])                     # -> [[1, 2, 3]]
query(data, ["*"])                  # -> [1, 2, 3]
query(data, [0])                    # -> [1]
```

Example 5 (bool is not an index; True must not act like 1):

```python
data = [10, 20]
query(data, [True])                 # -> []   (True is a bool, not a valid index)
query(data, [1])                    # -> [20]
```

## Ordering guarantee (important)

Whenever a single step yields multiple matches, they are ordered by the
document order of the entire tree, **not** by the order in which the previous
step's nodes were listed. In practice, implementing each step as "collect all
matched nodes, then sort/emit them in a single global pre-order" — or,
equivalently, walking the tree once in pre-order and testing membership — gives
the required order. For steps 1, 2, and 3 the natural left-to-right processing
already coincides with document order as long as you process current nodes in
the order they were produced and, within each, children left-to-right; the
`"**"` step is where you must be careful to emit whole subtrees in pre-order.

## Constraints

- Python 3, standard library only.
- Keys are always strings in the input dicts.
- Do not mutate `data`; return references into it.
- Distinguish `bool` from `int`: `True`/`False` are never valid list indices.
