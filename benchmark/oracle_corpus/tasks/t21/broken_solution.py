def neighbor_sum_grid(grid):
    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])
    out = []
    # Sum all 8 surrounding cells (accidentally includes diagonals).
    for r in range(rows):
        out_row = []
        for c in range(cols):
            total = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        total += grid[nr][nc]
            out_row.append(total)
        out.append(out_row)
    return out
