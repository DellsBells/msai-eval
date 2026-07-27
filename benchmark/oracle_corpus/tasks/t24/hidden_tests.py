import solution


def test_example_one():
    grid = [[1, 1, 0],
            [0, 1, 2],
            [2, 2, 2]]
    assert solution.label_regions(grid) == [[1, 1, 0],
                                            [0, 1, 2],
                                            [2, 2, 2]]


def test_example_two_diagonal_split_and_order():
    grid = [[5, 0, 5],
            [0, 5, 0],
            [5, 0, 5]]
    assert solution.label_regions(grid) == [[1, 0, 2],
                                            [0, 3, 0],
                                            [4, 0, 5]]


def test_example_three_different_values():
    grid = [[7, 7, 8],
            [7, 8, 8]]
    assert solution.label_regions(grid) == [[1, 1, 2],
                                            [1, 2, 2]]


def test_row_major_order_is_load_bearing():
    # A region anchored later in reading order must get a higher label. Here the
    # value-9 region in the bottom-left is anchored at (2,0); the value-3 region
    # is anchored at (0,2). Reading order visits (0,2) first -> label 1 for 3s,
    # label 2 for 9s. A column-major scan would label the 9s first.
    grid = [[0, 0, 3],
            [0, 0, 3],
            [9, 9, 0]]
    assert solution.label_regions(grid) == [[0, 0, 1],
                                            [0, 0, 1],
                                            [2, 2, 0]]


def test_all_background():
    grid = [[0, 0],
            [0, 0]]
    assert solution.label_regions(grid) == [[0, 0],
                                            [0, 0]]


def test_single_cell_background():
    assert solution.label_regions([[0]]) == [[0]]


def test_single_cell_region():
    assert solution.label_regions([[4]]) == [[1]]


def test_empty_grid():
    assert solution.label_regions([]) == []


def test_adjacent_different_values_not_merged():
    grid = [[1, 2, 1]]
    assert solution.label_regions(grid) == [[1, 2, 3]]


def test_labels_are_consecutive_no_gaps():
    grid = [[1, 0, 2, 0, 3],
            [0, 0, 0, 0, 0],
            [4, 0, 5, 0, 6]]
    out = solution.label_regions(grid)
    labels = sorted({v for row in out for v in row if v != 0})
    assert labels == [1, 2, 3, 4, 5, 6]


def test_does_not_mutate_input():
    grid = [[1, 1, 0], [0, 1, 2], [2, 2, 2]]
    snapshot = [row[:] for row in grid]
    solution.label_regions(grid)
    assert grid == snapshot


def test_returns_new_object():
    grid = [[1, 2], [3, 4]]
    out = solution.label_regions(grid)
    assert out is not grid
    assert out[0] is not grid[0]


def test_property_matches_row_major_reference():
    # Property: output must exactly match an independent row-major flood-fill
    # labeler over many seeded grids. This pins down connectivity, background
    # handling, and labeling order simultaneously.
    import random
    rng = random.Random(13337)

    def reference(grid):
        rows = len(grid)
        if rows == 0:
            return []
        cols = len(grid[0])
        labels = [[0] * cols for _ in range(rows)]
        nxt = 0
        for sr in range(rows):
            for sc in range(cols):
                val = grid[sr][sc]
                if val == 0 or labels[sr][sc] != 0:
                    continue
                nxt += 1
                stack = [(sr, sc)]
                labels[sr][sc] = nxt
                while stack:
                    r, c = stack.pop()
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if grid[nr][nc] == val and labels[nr][nc] == 0:
                                labels[nr][nc] = nxt
                                stack.append((nr, nc))
        return labels

    for _ in range(120):
        rows = rng.randint(0, 5)
        cols = rng.randint(1, 5) if rows > 0 else 0
        if rows == 0:
            grid = []
        else:
            grid = [[rng.randint(0, 3) for _ in range(cols)] for _ in range(rows)]
        expected = reference(grid)
        got = solution.label_regions(grid)
        assert got == expected
        # Invariant: label count equals number of distinct positive labels and
        # they are gap-free.
        if rows > 0:
            distinct = sorted({v for row in got for v in row if v != 0})
            assert distinct == list(range(1, len(distinct) + 1))
