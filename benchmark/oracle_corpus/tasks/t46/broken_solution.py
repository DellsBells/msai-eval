def prune(tree, max_depth):
    """Return a new pruned tree.

    Subtly wrong: rule 2 is implemented as "remove any non-root node with no
    surviving children", which incorrectly also deletes files (files always
    have empty children). A file that survives the depth cap should be kept,
    but this drops it.
    """

    def build(node, depth, is_root):
        if depth > max_depth:
            return None

        new_children = []
        if depth < max_depth:
            for child in node["children"]:
                built = build(child, depth + 1, False)
                if built is not None:
                    new_children.append(built)

        # BUG: collapses *any* childless non-root node, files included.
        if not new_children and not is_root:
            return None

        return {"name": node["name"], "kind": node["kind"], "children": new_children}

    return build(tree, 0, True)
