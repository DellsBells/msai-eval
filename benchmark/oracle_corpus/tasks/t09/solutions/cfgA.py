def merge_intervals(intervals):
    if not intervals:
        return []

    # Sort intervals by their start value
    sorted_intervals = sorted(intervals, key=lambda x: x[0])

    merged = [sorted_intervals[0][:]]  # Make a copy of the first interval

    for current in sorted_intervals[1:]:
        last_merged = merged[-1]
        if current[0] <= last_merged[1] + 1:
            # Merge intervals
            last_merged[1] = max(last_merged[1], current[1])
        else:
            # Add new interval
            merged.append(current[:])

    return merged