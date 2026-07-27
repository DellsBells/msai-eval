def neighbor_sum_grid(grid):
    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])
    out = []
    for r in range(rows):
        out_row = []
        for c in range(cols):
            total = 0
            if r - 1 >= 0:
                total += grid[r - 1][c]
            if r + 1 < rows:
                total += grid[r + 1][c]
            if c - 1 >= 0:
                total += grid[r][c - 1]
            if c + 1 < cols:
                total += grid[r][c + 1]
            out_row.append(total)
        out.append(out_row)
    return out
