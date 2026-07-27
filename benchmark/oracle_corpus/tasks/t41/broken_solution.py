def longest_above_run(readings, threshold):
    best_len = 0
    best_start = -1
    cur_len = 0
    cur_start = -1
    for i, value in enumerate(readings):
        if value > threshold:
            if cur_len == 0:
                cur_start = i
            cur_len += 1
            # Bug: uses >= so a later run of equal length overwrites the earlier one,
            # violating the earliest-wins tie-break.
            if cur_len >= best_len:
                best_len = cur_len
                best_start = cur_start
        else:
            cur_len = 0
            cur_start = -1
    return (best_len, best_start)
