def best_monotone_window(readings, k):
    if k < 1:
        raise ValueError("Window size k must be at least 1.")
    if len(readings) < k:
        return (0, -1, "none")
    
    def find_streaks(window):
        up_len = down_len = 1
        max_up = max_down = 1
        
        for i in range(1, len(window)):
            if window[i] > window[i - 1]:
                up_len += 1
                down_len = 1
            elif window[i] < window[i - 1]:
                down_len += 1
                up_len = 1
            else:
                up_len = down_len = 1
            
            max_up = max(max_up, up_len)
            max_down = max(max_down, down_len)
        
        return max_up, max_down
    
    best_score = 0
    best_start_index = -1
    best_direction = "none"
    
    for i in range(len(readings) - k + 1):
        window = readings[i:i + k]
        up_len, down_len = find_streaks(window)
        score = max(up_len, down_len)
        
        if (score > best_score or
            (score == best_score and i < best_start_index)):
            best_score = score
            best_start_index = i
            if up_len > down_len:
                best_direction = "up"
            elif down_len > up_len:
                best_direction = "down"
            else:
                best_direction = "flat"
    
    return (best_score, best_start_index, best_direction)