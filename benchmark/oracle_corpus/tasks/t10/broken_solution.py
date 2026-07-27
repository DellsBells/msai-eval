def find_gaps(reservations, window_start, window_end):
    if window_start >= window_end:
        return []

    clipped = []
    for start, end in reservations:
        if start >= end:
            continue
        lo = start if start > window_start else window_start
        hi = end if end < window_end else window_end
        if lo < hi:
            clipped.append((lo, hi))

    if not clipped:
        return [[window_start, window_end]]

    clipped.sort(key=lambda iv: (iv[0], iv[1]))

    gaps = []
    cursor = window_start
    for lo, hi in clipped:
        if lo > cursor:
            gaps.append([cursor, lo])
        # BUG: unconditionally advances cursor to hi. When an interval is
        # nested inside an earlier one (hi < cursor), this pulls the cursor
        # backwards and fabricates a spurious gap on the next iteration.
        cursor = hi
    if cursor < window_end:
        gaps.append([cursor, window_end])
    return gaps
