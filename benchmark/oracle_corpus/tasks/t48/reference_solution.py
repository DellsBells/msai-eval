"""Wildcard path query over nested dicts/lists.

Nodes are tracked by their *path* from the root (a tuple whose elements are
dict keys (str) or list indices (int)). Tracking by path — rather than by
``id()`` — is necessary because equal scalars (e.g. two ``10``s, or two equal
strings) may be the same interned object, which would make identity-based
de-duplication and ordering incorrect. Paths uniquely name every tree position.
"""


def _is_int_index(step):
    return isinstance(step, int) and not isinstance(step, bool)


def _resolve(data, path):
    node = data
    for part in path:
        node = node[part]
    return node


def _child_steps(node):
    """Yield the child access-keys of a node in document order."""
    if isinstance(node, dict):
        for k in node.keys():
            yield k
    elif isinstance(node, list):
        for i in range(len(node)):
            yield i


def _doc_order_index(data):
    """Map each node's path (tuple) to its pre-order rank."""
    ranks = {}

    def walk(path):
        ranks[path] = len(ranks)
        node = _resolve(data, path)
        for step in _child_steps(node):
            walk(path + (step,))

    walk(())
    return ranks


def query(data, pattern):
    ranks = _doc_order_index(data)

    # Frontier is a list of paths (tuples). Start at the root path ().
    current = [()]

    for step in pattern:
        nxt = []
        if step == "*":
            for path in current:
                node = _resolve(data, path)
                for cs in _child_steps(node):
                    nxt.append(path + (cs,))
        elif step == "**":
            for path in current:
                # descendant-or-self, pre-order, for this subtree
                stack = [path]
                i = 0
                collected = [path]
                while i < len(collected):
                    p = collected[i]
                    i += 1
                    node = _resolve(data, p)
                    for cs in _child_steps(node):
                        collected.append(p + (cs,))
                nxt.extend(collected)
        elif _is_int_index(step):
            for path in current:
                node = _resolve(data, path)
                if isinstance(node, list) and 0 <= step < len(node):
                    nxt.append(path + (step,))
        elif isinstance(step, str):
            for path in current:
                node = _resolve(data, path)
                if isinstance(node, dict) and step in node:
                    nxt.append(path + (step,))
        else:
            nxt = []

        # Sort by document order and de-duplicate by path.
        nxt_sorted = sorted(nxt, key=lambda p: ranks[p])
        deduped = []
        seen = set()
        for p in nxt_sorted:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        current = deduped

    return [_resolve(data, p) for p in current]
