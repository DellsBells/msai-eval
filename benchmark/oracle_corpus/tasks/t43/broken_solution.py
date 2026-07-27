def flag_anomalies(readings, window, threshold):
    if window < 1:
        raise ValueError("window must be a positive integer")
    if window % 2 == 0:
        raise ValueError("window must be odd")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")

    flagged = []
    mid = window // 2
    for i in range(window, len(readings)):
        # Bug: the baseline window includes the current reading itself
        # (indices i-window+1 .. i) instead of the strictly-preceding window.
        baseline_slice = readings[i - window + 1:i + 1]
        baseline = sorted(baseline_slice)[mid]
        if abs(readings[i] - baseline) > threshold:
            flagged.append(i)
    return flagged
