# First Root-to-Node Path Matching a Tag

You are given an **org tree** built from nested Python `dict`s. Each node has:

- `"id"`: a string, unique within the tree.
- `"tags"`: a `list` of strings (possibly empty). Tags are **not** unique — the
  same tag may appear on many nodes.
- `"reports"`: a `list` of child nodes (each with the same shape). May be empty.

Write a single function:

```python
def first_path_with_tag(tree, tag):
    ...
```

## Behavior

Search the tree in **depth-first pre-order**, visiting each node before its
children, and visiting a node's `"reports"` in their given left-to-right order.

Return the path to the **first** node (in that pre-order traversal) whose
`"tags"` list contains `tag`. The path is a `list` of the `"id"` strings from
the root down to and including the matching node.

- The root node itself is eligible to match.
- If **no** node contains `tag`, return an empty list `[]`.
- Membership is exact string equality (case-sensitive): a node matches iff
  `tag in node["tags"]`.
- Do not mutate the input.

"First in pre-order" means: check the current node, then recurse into its first
child's subtree fully, then the second child's subtree, and so on. The first
match encountered in that order wins — even if a shallower match exists in a
*later* sibling's subtree.

## Examples

Example 1:

```python
tree = {
    "id": "ceo",
    "tags": ["exec"],
    "reports": [
        {"id": "vp1", "tags": ["eng"], "reports": [
            {"id": "e1", "tags": ["eng", "oncall"], "reports": []},
        ]},
        {"id": "vp2", "tags": ["sales"], "reports": []},
    ],
}
first_path_with_tag(tree, "oncall")   # -> ["ceo", "vp1", "e1"]
first_path_with_tag(tree, "sales")    # -> ["ceo", "vp2"]
first_path_with_tag(tree, "exec")     # -> ["ceo"]
first_path_with_tag(tree, "missing")  # -> []
```

Example 2 (pre-order picks the deeper-but-earlier match):

```python
tree = {
    "id": "root",
    "tags": [],
    "reports": [
        {"id": "a", "tags": [], "reports": [
            {"id": "a1", "tags": ["target"], "reports": []},
        ]},
        {"id": "b", "tags": ["target"], "reports": []},
    ],
}
first_path_with_tag(tree, "target")  # -> ["root", "a", "a1"]
# "a1" (depth 2) is visited before "b" (depth 1) in pre-order, so it wins.
```

Example 3 (root matches):

```python
tree = {"id": "solo", "tags": ["x", "y"], "reports": []}
first_path_with_tag(tree, "y")   # -> ["solo"]
first_path_with_tag(tree, "z")   # -> []
```

## Constraints

- Python 3, standard library only.
- Return a new list; do not mutate the tree.
- Traversal order is significant — a breadth-first search would give wrong
  answers on inputs like Example 2.
