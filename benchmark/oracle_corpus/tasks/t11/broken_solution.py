def coverage_stats(intervals):
    events = []
    sum_lengths = 0
    for start, end in intervals:
        if start >= end:
            continue
        sum_lengths += end - start
        events.append((start, 1))
        events.append((end, -1))

    if not events:
        return (0, 0)

    events.sort(key=lambda e: e[0])

    total_covered = 0
    depth = 0
    prev_pos = events[0][0]
    for pos, delta in events:
        if pos > prev_pos:
            if depth >= 1:
                total_covered += pos - prev_pos
            prev_pos = pos
        depth += delta

    # BUG: treats "multiply covered" as the leftover after removing the union
    # once. This over-counts regions covered by 3+ sensors: a depth-3 segment
    # of width w contributes 3*w to sum_lengths and w to total_covered, giving
    # 2*w here, but its true depth->=2 measure is only w.
    multi_covered = sum_lengths - total_covered
    return (total_covered, multi_covered)
