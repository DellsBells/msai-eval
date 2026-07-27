from collections import deque


def first_path_with_tag(tree, tag):
    """Return the path to the first matching node.

    Subtly wrong: uses breadth-first (level-order) search instead of
    depth-first pre-order. It returns a *shallowest* match, which disagrees
    with pre-order whenever a deeper node in an earlier sibling's subtree
    should win over a shallower node in a later sibling.
    """
    queue = deque([(tree, [tree["id"]])])
    while queue:
        node, path = queue.popleft()
        if tag in node["tags"]:
            return path
        for child in node["reports"]:
            queue.append((child, path + [child["id"]]))
    return []
