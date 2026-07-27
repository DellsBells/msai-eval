def _normalize(intervals):
    """Merge a list of half-open intervals into sorted, joined [a,b) pieces.

    Touching intervals ([a,b) and [b,c)) are joined because no point lies
    between them. Empty intervals (start >= end) are dropped.
    """
    cleaned = [(s, e) for s, e in intervals if s < e]
    if not cleaned:
        return []
    cleaned.sort(key=lambda iv: (iv[0], iv[1]))
    result = [[cleaned[0][0], cleaned[0][1]]]
    for s, e in cleaned[1:]:
        last = result[-1]
        if s <= last[1]:  # overlap OR touch (half-open) -> join
            if e > last[1]:
                last[1] = e
        else:
            result.append([s, e])
    return result


def _peak_depth(intervals):
    events = []
    for s, e in intervals:
        if s < e:
            events.append((s, 1))
            events.append((e, -1))
    if not events:
        return 0
    # Half-open semantics: at a shared boundary b, an interval [a, b) no longer
    # covers b while [b, c) does. So ends (-1) must be applied before starts
    # (+1) at equal positions; otherwise touching intervals momentarily inflate
    # the depth. Ascending sort on (pos, delta) puts -1 before +1.
    events.sort(key=lambda ev: (ev[0], ev[1]))
    depth = 0
    peak = 0
    for _, delta in events:
        depth += delta
        if depth > peak:
            peak = depth
    return peak


def _subtract(base, remove):
    """Subtract normalized `remove` from normalized `base`; both sorted."""
    result = []
    ri = 0
    n = len(remove)
    for bs, be in base:
        cur = bs
        # advance over remove intervals that end at or before cur
        while ri < n and remove[ri][1] <= cur:
            ri += 1
        j = ri
        while j < n and remove[j][0] < be:
            rs, re = remove[j]
            if rs > cur:
                result.append([cur, min(rs, be)])
            if re > cur:
                cur = re
            if cur >= be:
                break
            j += 1
        if cur < be:
            result.append([cur, be])
    return result


def resolve_ranges(allowed, blocked):
    allowed_list = [(s, e) for s, e in allowed]
    blocked_list = [(s, e) for s, e in blocked]

    peak = _peak_depth(allowed_list)

    base = _normalize(allowed_list)
    remove = _normalize(blocked_list)
    available = _subtract(base, remove)

    return {"available": available, "peak_depth": peak}
