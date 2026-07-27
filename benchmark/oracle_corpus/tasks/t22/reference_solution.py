def _rotate_once_cw(matrix):
    r = len(matrix)
    if r == 0:
        return []
    c = len(matrix[0])
    # Result is c x r; new[i][j] = old[r - 1 - j][i]
    result = []
    for i in range(c):
        row = []
        for j in range(r):
            row.append(matrix[r - 1 - j][i])
        result.append(row)
    return result


def rotate_quarters(matrix, k):
    turns = k % 4  # python modulo of negatives yields 0..3
    # Start with a deep-ish copy so k==0 (and multiples of 4) returns a new object.
    result = [row[:] for row in matrix]
    for _ in range(turns):
        result = _rotate_once_cw(result)
    return result
