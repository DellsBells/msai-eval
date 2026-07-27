def _window_stats(window):
    up_len = 1
    down_len = 1
    cur_up = 1
    cur_down = 1
    for i in range(1, len(window)):
        # Bug: uses >= / <= so equal adjacent values wrongly extend the streaks
        # instead of breaking them (equality should count as neither direction).
        if window[i] >= window[i - 1]:
            cur_up += 1
            cur_down = 1
        elif window[i] <= window[i - 1]:
            cur_down += 1
            cur_up = 1
        else:
            cur_up = 1
            cur_down = 1
        if cur_up > up_len:
            up_len = cur_up
        if cur_down > down_len:
            down_len = cur_down
    return up_len, down_len


def best_monotone_window(readings, k):
    if k < 1:
        raise ValueError("k must be a positive integer")
    n = len(readings)
    if n < k:
        return (0, -1, "none")

    best_score = None
    best_start = -1
    best_direction = "none"
    for start in range(n - k + 1):
        window = readings[start:start + k]
        up_len, down_len = _window_stats(window)
        score = up_len if up_len >= down_len else down_len
        if up_len > down_len:
            direction = "up"
        elif down_len > up_len:
            direction = "down"
        else:
            direction = "flat"
        if best_score is None or score > best_score:
            best_score = score
            best_start = start
            best_direction = direction
    return (best_score, best_start, best_direction)
