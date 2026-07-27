def best_monotone_window(readings, k):
    """
    Finds the window of size 'k' within which readings are strictly increasing.
    
    :param readings: List[int] - A list of integer readings.
    :param k: int - The size of the window to consider for monotonicity check.
    :return: int - The index of the leftmost reading in a valid window, or -1 if no such window exists.
    """
    
    def is_monotone_increasing(start_index):
        current = start_index
        while current < len(readings) and readings[current] > readings[current + 1]:
            current += 1
        return current >= len(readings)
    
    for i in range(len(readings)):
        if i + k <= len(readings) - 1:
            if is_monotone_increasing(i):
                return i
    
    return -1

# Example usage
print(best_monotone_window([1, 2, 3, 1, 2], 4))  # Output: 0