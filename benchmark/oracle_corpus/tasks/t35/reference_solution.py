import functools


def multisort(records, keys):
    # Validate directions up front.
    for field, direction in keys:
        if direction not in ("asc", "desc"):
            raise ValueError("invalid direction: %r" % (direction,))

    # Decorate with original index so the final tie-break is a stable
    # ascending-by-index comparison, independent of key directions.
    decorated = list(enumerate(records))

    def compare(a, b):
        ia, ra = a
        ib, rb = b
        for field, direction in keys:
            va = ra[field]
            vb = rb[field]
            if va == vb:
                continue
            if va < vb:
                base = -1
            else:
                base = 1
            if direction == "desc":
                base = -base
            return base
        # All keys equal -> tie-break by original input index, ascending.
        if ia < ib:
            return -1
        if ia > ib:
            return 1
        return 0

    decorated.sort(key=functools.cmp_to_key(compare))
    return [rec for _, rec in decorated]
