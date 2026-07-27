def merge_intervals(intervals):
    if not intervals:
        return []
    ordered = sorted((list(iv) for iv in intervals), key=lambda iv: (iv[0], iv[1]))
    result = [[ordered[0][0], ordered[0][1]]]
    for start, end in ordered[1:]:
        last = result[-1]
        # BUG: only merges on true overlap/touch, misses adjacent integers
        # (uses <= last[1] instead of <= last[1] + 1)
        if start <= last[1]:
            if end > last[1]:
                last[1] = end
        else:
            result.append([start, end])
    return result
