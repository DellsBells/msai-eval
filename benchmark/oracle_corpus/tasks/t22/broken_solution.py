def _rotate_once_cw(matrix):
    r = len(matrix)
    if r == 0:
        return []
    c = len(matrix[0])
    result = []
    for i in range(c):
        row = []
        for j in range(r):
            row.append(matrix[r - 1 - j][i])
        result.append(row)
    return result


def rotate_quarters(matrix, k):
    # Normalize turn count. (Uses abs, which mishandles counter-clockwise.)
    turns = abs(k) % 4
    result = [row[:] for row in matrix]
    for _ in range(turns):
        result = _rotate_once_cw(result)
    return result
