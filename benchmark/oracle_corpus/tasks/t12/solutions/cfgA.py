def resolve_ranges(allowed, blocked):
    def normalize(intervals):
        if not intervals:
            return []
        intervals.sort()
        merged = [intervals[0]]
        for start, end in intervals[1:]:
            if start < merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        return merged

    def calculate_peak_depth(intervals):
        if not intervals:
            return 0
        events = []
        for start, end in intervals:
            events.append((start, 1))
            events.append((end, -1))
        events.sort()
        max_depth = current_depth = 0
        for _, delta in events:
            current_depth += delta
            max_depth = max(max_depth, current_depth)
        return max_depth

    def subtract_intervals(allowed, blocked):
        if not allowed:
            return []
        result = []
        i, j = 0, 0
        while i < len(allowed) and j < len(blocked):
            a_start, a_end = allowed[i]
            b_start, b_end = blocked[j]
            if a_end <= b_start:
                result.append([a_start, a_end])
                i += 1
            elif a_start >= b_end:
                j += 1
            else:
                if a_start < b_start:
                    result.append([a_start, b_start])
                if a_end > b_end:
                    allowed[i] = [b_end, a_end]
                else:
                    i += 1
        while i < len(allowed):
            result.append(allowed[i])
            i += 1
        return normalize(result)

    normalized_allowed = normalize(allowed)
    peak_depth = calculate_peak_depth(normalized_allowed)
    normalized_blocked = normalize(blocked)
    available_intervals = subtract_intervals(normalized_allowed, normalized_blocked)
    return {"available": available_intervals, "peak_depth": peak_depth}