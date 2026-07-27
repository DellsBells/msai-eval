def first_path_with_tag(tree, tag):
    """Return the root-to-node id path to the first pre-order node with ``tag``.

    Returns [] if no node carries the tag.
    """

    def dfs(node, prefix):
        path = prefix + [node["id"]]
        if tag in node["tags"]:
            return path
        for child in node["reports"]:
            found = dfs(child, path)
            if found:
                return found
        return None

    result = dfs(tree, [])
    return result if result is not None else []
