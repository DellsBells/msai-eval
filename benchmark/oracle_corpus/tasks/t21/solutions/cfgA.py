def neighbor_sum_grid(grid):
    if not grid or not grid[0]:
        return []

    rows = len(grid)
    cols = len(grid[0])
    result = [[0] * cols for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            total = 0
            if r > 0:
                total += grid[r - 1][c]
            if r < rows - 1:
                total += grid[r + 1][c]
            if c > 0:
                total += grid[r][c - 1]
            if c < cols - 1:
                total += grid[r][c + 1]
            result[r][c] = total

    return result