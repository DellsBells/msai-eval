def _normalize(intervals):
    cleaned = [(s, e) for s, e in intervals if s < e]
    if not cleaned:
        return []
    cleaned.sort(key=lambda iv: (iv[0], iv[1]))
    result = [[cleaned[0][0], cleaned[0][1]]]
    for s, e in cleaned[1:]:
        last = result[-1]
        # BUG: strict '<' fails to join touching half-open intervals.
        # [0,3) and [3,6) should join into [0,6) but this leaves them split.
        if s < last[1]:
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
    events.sort(key=lambda ev: (ev[0], ev[1]))
    depth = 0
    peak = 0
    for _, delta in events:
        depth += delta
        if depth > peak:
            peak = depth
    return peak


def _subtract(base, remove):
    result = []
    ri = 0
    n = len(remove)
    for bs, be in base:
        cur = bs
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
