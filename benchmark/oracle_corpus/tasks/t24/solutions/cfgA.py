def label_regions(grid):
    if not grid or not grid[0]:
        return []

    rows, cols = len(grid), len(grid[0])
    labels = [[0] * cols for _ in range(rows)]
    region_count = 0

    def flood_fill(r, c, label):
        stack = [(r, c)]
        while stack:
            x, y = stack.pop()
            if 0 <= x < rows and 0 <= y < cols and grid[x][y] == value and labels[x][y] == 0:
                labels[x][y] = label
                stack.append((x + 1, y))
                stack.append((x - 1, y))
                stack.append((x, y + 1))
                stack.append((x, y - 1))

    for r in range(rows):
        for c in range(cols):
            value = grid[r][c]
            if value != 0 and labels[r][c] == 0:
                region_count += 1
                flood_fill(r, c, region_count)

    return labels