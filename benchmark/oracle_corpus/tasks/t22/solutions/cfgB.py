def rotate_quarters(matrix, k):
    n = len(matrix)
    if not matrix or not matrix[0]:
        return matrix
    
    # Normalize the number of turns to be within 0-3 range.
    k %= 4
    
    for _ in range(k):
        top_row = [row[0] for row in matrix]
        del matrix[0]
        matrix.insert(0, top_row)
    
    return matrix