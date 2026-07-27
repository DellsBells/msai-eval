def prune(tree, max_depth):
    """Return a new tree with a depth cap and empty-directory collapse.

    Rule 1: drop nodes deeper than ``max_depth`` (root at depth 0).
    Rule 2: drop any non-root ``dir`` node that has no surviving children;
            files are never dropped by rule 2. Root is always kept.
    """

    def build(node, depth, is_root):
        # Depth cap: a node deeper than max_depth should not exist. This is
        # handled by the parent (it won't recurse past the cap), but guard
        # for the root case too.
        if depth > max_depth:
            return None

        if node["kind"] == "file":
            # Files are leaves; keep as-is (fresh copy).
            return {"name": node["name"], "kind": "file", "children": []}

        # Directory: recurse into children only if they'd be within the cap.
        new_children = []
        if depth < max_depth:
            for child in node["children"]:
                built = build(child, depth + 1, False)
                if built is not None:
                    new_children.append(built)

        if not new_children and not is_root:
            # Empty directory (non-root) collapses.
            return None

        return {"name": node["name"], "kind": "dir", "children": new_children}

    return build(tree, 0, True)
