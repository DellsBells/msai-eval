def deepest_level(tree):
    """Return the largest level (edges from root) at which any leaf appears."""

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

    return walk(tree, 0)
