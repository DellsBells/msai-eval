# Deepest Leaf Level in a Category Tree

You are given a **category tree** describing a nested taxonomy. Each node is a
Python `dict` with exactly these two keys:

- `"name"`: a non-empty string, the category's name.
- `"children"`: a `list` of child nodes (each child is itself a node dict with
  the same shape). This list may be empty.

Write a single function:

```python
def deepest_level(tree):
    ...
```

## Behavior

The **level** of a node is its distance from the root, measured in edges: the
root node is at level `0`, the root's direct children are at level `1`, their
children at level `2`, and so on.

A **leaf** is a node whose `"children"` list is empty.

`deepest_level(tree)` must return an `int`: the largest level at which any leaf
appears.

Rules and edge cases:

- The root is guaranteed to be a valid node dict (never `None`).
- If the root itself is a leaf (its `"children"` list is empty), every path ends
  at the root, so the answer is `0`.
- When several leaves are tied at the same deepest level, that shared level is
  the answer (there is exactly one number to return).
- Only **leaf** levels count. An internal node that happens to sit at a deep
  level does **not** contribute unless a leaf is found at least that deep on some
  path through it. (Since every path eventually ends at a leaf, the deepest leaf
  level always equals the height of the tree in edges — but you must derive it
  from leaves, not by assuming a balanced tree.)
- Do not mutate the input tree.

## Examples

Example 1:

```python
tree = {"name": "root", "children": []}
deepest_level(tree)  # -> 0
```

Example 2:

```python
tree = {
    "name": "root",
    "children": [
        {"name": "a", "children": [
            {"name": "a1", "children": []},
        ]},
        {"name": "b", "children": []},
    ],
}
deepest_level(tree)  # -> 2   (leaf "a1" is at level 2)
```

Example 3:

```python
tree = {
    "name": "root",
    "children": [
        {"name": "x", "children": [
            {"name": "x1", "children": [
                {"name": "x1a", "children": []},
            ]},
            {"name": "x2", "children": []},
        ]},
    ],
}
deepest_level(tree)  # -> 3   (leaf "x1a" is at level 3; leaf "x2" is only level 2)
```

## Constraints

- Python 3, standard library only.
- The tree may be up to a few thousand nodes deep/wide; a straightforward
  recursive or iterative traversal is fine.
