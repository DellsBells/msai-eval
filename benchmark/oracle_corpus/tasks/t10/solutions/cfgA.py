def find_gaps(reservations, window_start, window_end):
    if window_start >= window_end:
        return []
    
    # Clip reservations to the window
    clipped_reservations = []
    for start, end in reservations:
        if start < end:
            clipped_start = max(start, window_start)
            clipped_end = min(end, window_end)
            if clipped_start < clipped_end:
                clipped_reservations.append((clipped_start, clipped_end))
    
    # Sort the clipped reservations by start time
    clipped_reservations.sort()
    
    gaps = []
    current_start = window_start
    
    for start, end in clipped_reservations:
        if current_start < start:
            gaps.append([current_start, start])
        current_start = max(current_start, end)
    
    if current_start < window_end:
        gaps.append([current_start, window_end])
    
    return gaps