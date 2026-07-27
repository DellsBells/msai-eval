def label_regions(grid):
    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])

    labels = [[0] * cols for _ in range(rows)]
    next_label = 0

    for sr in range(rows):
        for sc in range(cols):
            value = grid[sr][sc]
            if value == 0:
                continue  # background stays 0
            if labels[sr][sc] != 0:
                continue  # already part of an earlier region
            next_label += 1
            # Flood fill the region of equal-valued orthogonal neighbors.
            stack = [(sr, sc)]
            labels[sr][sc] = next_label
            while stack:
                r, c = stack.pop()
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] == value and labels[nr][nc] == 0:
                            labels[nr][nc] = next_label
                            stack.append((nr, nc))

    return labels
