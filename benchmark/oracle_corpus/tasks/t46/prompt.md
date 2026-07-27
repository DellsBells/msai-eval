# Prune a File-System Tree by Depth and Empty-Directory Collapse

You model a file-system snapshot as a nested structure. Each node is a Python
`dict` with these keys:

- `"name"`: a non-empty string.
- `"kind"`: either the string `"dir"` or the string `"file"`.
- `"children"`: a `list` of child nodes. For a `"file"` node this list is always
  empty. For a `"dir"` node it may contain any number of child nodes.

Write a single function:

```python
def prune(tree, max_depth):
    ...
```

`prune` returns a **new** pruned tree (a fresh nested structure). It must **not
mutate** the input.

## Depth definition

The root is at depth `0`, its children at depth `1`, and so on (depth counts
edges from the root).

## Pruning rules, applied together

1. **Depth cap.** Any node at depth **greater than** `max_depth` is removed
   entirely. Equivalently: keep nodes at depth `0` through `max_depth`
   inclusive; drop everything deeper. `max_depth` is a non-negative integer.

2. **Empty-directory collapse.** After the depth cap is applied, remove every
   `"dir"` node that ends up with **no children** — *unless* it is the root.
   This removal cascades: if pruning a directory's children leaves its parent
   directory empty, that parent is removed too, and so on up the tree. A
   directory that originally had no children (an intentionally empty directory)
   is *also* removed under this rule (again, unless it is the root).
   - `"file"` nodes are **never** removed by rule 2 — a file is a leaf that is
     meaningful on its own.
   - The root node is **always** kept, even if it becomes an empty directory.

Apply rule 1 first (conceptually), then rule 2's cascade. The returned tree
contains only surviving nodes, with `"children"` lists filtered to surviving
children, preserving original left-to-right order.

## Returned shape

Each surviving node in the result is a new dict with the same three keys
(`"name"`, `"kind"`, `"children"`), where `"children"` holds the pruned
children. The result is always a valid single-root tree (the root is never
dropped).

## Examples

Example 1 (depth cap makes a directory empty, so it collapses):

```python
tree = {"name": "/", "kind": "dir", "children": [
    {"name": "a", "kind": "dir", "children": [
        {"name": "f.txt", "kind": "file", "children": []},
    ]},
]}
prune(tree, 1)
# Depth cap keeps depth 0 ("/") and depth 1 ("a") but drops depth 2 ("f.txt").
# Now "a" is an empty dir -> rule 2 removes it. The root is kept though empty.
# -> {"name": "/", "kind": "dir", "children": []}
```

Example 2 (files keep their ancestors alive):

```python
tree = {"name": "root", "kind": "dir", "children": [
    {"name": "keep", "kind": "dir", "children": [
        {"name": "note", "kind": "file", "children": []},
    ]},
    {"name": "empty", "kind": "dir", "children": []},
]}
prune(tree, 5)
# -> {"name": "root", "kind": "dir", "children": [
#        {"name": "keep", "kind": "dir", "children": [
#            {"name": "note", "kind": "file", "children": []},
#        ]},
#    ]}
# "empty" is dropped (empty dir); "keep" survives because it contains a file.
```

Example 3 (cascade up several levels):

```python
tree = {"name": "root", "kind": "dir", "children": [
    {"name": "x", "kind": "dir", "children": [
        {"name": "y", "kind": "dir", "children": [
            {"name": "deep.txt", "kind": "file", "children": []},
        ]},
    ]},
]}
prune(tree, 1)
# Depth cap removes "deep.txt" (depth 3) and "y" (depth 2).
# Then "y" would be empty but it is already gone; "x" (depth 1) now has no
# surviving children -> removed; root ends up empty but is kept.
# -> {"name": "root", "kind": "dir", "children": []}
```

## Constraints

- Python 3, standard library only.
- Do not mutate the input tree; build and return new dicts/lists.
- `max_depth >= 0`. When `max_depth == 0`, only the root survives the depth cap;
  the result is the root with an empty `"children"` list.
