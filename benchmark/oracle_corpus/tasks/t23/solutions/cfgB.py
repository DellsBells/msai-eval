def count_enclosed_regions(grid):
    def dfs(x, y):
        if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == '.':
            grid[x][y] = 'X'
            for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                dfs(x + dx, y + dy)

    count = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '.':
                dfs(i, j)
                count += 1

    return count