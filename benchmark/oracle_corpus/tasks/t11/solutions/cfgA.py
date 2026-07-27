def coverage_stats(intervals):
    from collections import defaultdict

    events = []
    for start, end in intervals:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))

    events.sort()

    total_covered = 0
    multi_covered = 0
    current_depth = 0
    last_position = None

    for position, change in events:
        if last_position is not None:
            covered_length = position - last_position
            if current_depth > 0:
                total_covered += covered_length
            if current_depth >= 2:
                multi_covered += covered_length

        current_depth += change
        last_position = position

    return total_covered, multi_covered