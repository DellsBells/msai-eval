"""Wildcard path query over nested dicts/lists.

Subtly wrong: the integer-index step uses a plain ``isinstance(step, int)``
check, forgetting that ``bool`` is a subclass of ``int`` in Python. So a
``True`` step is treated as index 1 and ``False`` as index 0, instead of
matching nothing. Everything else follows the spec.
"""


def _resolve(data, path):
    node = data
    for part in path:
        node = node[part]
    return node


def _child_steps(node):
    if isinstance(node, dict):
        for k in node.keys():
            yield k
    elif isinstance(node, list):
        for i in range(len(node)):
            yield i


def _doc_order_index(data):
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
                i = 0
                collected = [path]
                while i < len(collected):
                    p = collected[i]
                    i += 1
                    node = _resolve(data, p)
                    for cs in _child_steps(node):
                        collected.append(p + (cs,))
                nxt.extend(collected)
        elif isinstance(step, int):
            # BUG: bool is a subclass of int; True/False slip through here.
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

        nxt_sorted = sorted(nxt, key=lambda p: ranks[p])
        deduped = []
        seen = set()
        for p in nxt_sorted:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        current = deduped

    return [_resolve(data, p) for p in current]
