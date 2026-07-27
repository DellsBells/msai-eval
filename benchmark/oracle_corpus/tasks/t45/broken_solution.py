def deepest_level(tree):
    """Return the deepest leaf level.

    Subtly wrong: measures level as the number of nodes on the path
    (1-based) rather than the number of edges, so every answer is one
    too large (e.g. a lone root leaf reports 1 instead of 0).
    """

    def walk(node, level):
        children = node["children"]
        if not children:
            return level
        best = level
        for child in children:
            d = walk(child, level + 1)
            if d > best:
                best = d
        return best

    return walk(tree, 1)
