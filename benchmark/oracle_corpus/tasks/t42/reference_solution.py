def rolling_ranges(readings, k):
    if k < 1:
        raise ValueError("k must be a positive integer")
    n = len(readings)
    if n < k:
        return ([], -1)
    ranges = []
    peak_index = -1
    peak_value = None
    for start in range(n - k + 1):
        window = readings[start:start + k]
        r = max(window) - min(window)
        ranges.append(r)
        if peak_value is None or r > peak_value:
            peak_value = r
            peak_index = start
    return (ranges, peak_index)
