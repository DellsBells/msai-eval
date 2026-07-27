def count_enclosed_regions(grid):
    rows = len(grid)
    if rows == 0:
        return 0
    cols = len(grid[0])
    if rows < 3 or cols < 3:
        return 0

    visited = [[False] * cols for _ in range(rows)]
    enclosed = 0

    for sr in range(rows):
        for sc in range(cols):
            if grid[sr][sc] != '.' or visited[sr][sc]:
                continue
            # Flood fill this region with an explicit stack (4-connectivity).
            stack = [(sr, sc)]
            visited[sr][sc] = True
            touches_border = False
            while stack:
                r, c = stack.pop()
                if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                    touches_border = True
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] == '.' and not visited[nr][nc]:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
            if not touches_border:
                enclosed += 1

    return enclosed
