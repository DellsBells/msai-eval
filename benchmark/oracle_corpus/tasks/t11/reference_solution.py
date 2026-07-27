def coverage_stats(intervals):
    events = []
    for start, end in intervals:
        if start >= end:
            continue
        events.append((start, 1))   # coverage begins
        events.append((end, -1))    # coverage ends

    if not events:
        return (0, 0)

    # Sort by position. Ties don't affect the measured lengths because we
    # accumulate over the segment between consecutive distinct positions using
    # the depth active on that segment.
    events.sort(key=lambda e: e[0])

    total_covered = 0
    multi_covered = 0
    depth = 0
    prev_pos = events[0][0]

    for pos, delta in events:
        if pos > prev_pos:
            width = pos - prev_pos
            if depth >= 1:
                total_covered += width
            if depth >= 2:
                multi_covered += width
            prev_pos = pos
        depth += delta

    return (total_covered, multi_covered)
