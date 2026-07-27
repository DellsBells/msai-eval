import solution


def test_three_by_three():
    grid = [[1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]]
    assert solution.neighbor_sum_grid(grid) == [[6, 9, 8],
                                                [13, 20, 17],
                                                [12, 21, 14]]


def test_single_cell():
    assert solution.neighbor_sum_grid([[5]]) == [[0]]


def test_single_cell_negative():
    assert solution.neighbor_sum_grid([[-7]]) == [[0]]


def test_empty_grid():
    assert solution.neighbor_sum_grid([]) == []


def test_single_row():
    assert solution.neighbor_sum_grid([[10, -3]]) == [[-3, 10]]
    assert solution.neighbor_sum_grid([[1, 2, 3, 4]]) == [[2, 4, 6, 3]]


def test_single_column():
    assert solution.neighbor_sum_grid([[1], [2], [3]]) == [[2], [4], [2]]


def test_negatives_mixed():
    grid = [[-1, -2],
            [-3, -4]]
    # (0,0): right -2 + down -3 = -5
    # (0,1): left -1 + down -4 = -5
    # (1,0): up -1 + right -4 = -5
    # (1,1): up -2 + left -3 = -5
    assert solution.neighbor_sum_grid(grid) == [[-5, -5], [-5, -5]]


def test_does_not_mutate_input():
    grid = [[1, 2], [3, 4]]
    snapshot = [row[:] for row in grid]
    solution.neighbor_sum_grid(grid)
    assert grid == snapshot


def test_output_is_new_object():
    grid = [[1, 2], [3, 4]]
    out = solution.neighbor_sum_grid(grid)
    assert out is not grid
    for r in range(len(grid)):
        assert out[r] is not grid[r]


def test_dimensions_preserved():
    grid = [[1, 2, 3], [4, 5, 6]]
    out = solution.neighbor_sum_grid(grid)
    assert len(out) == 2
    assert all(len(row) == 3 for row in out)


def test_property_sum_of_all_equals_weighted_edges():
    # Property: the sum over all output cells equals the sum over all input
    # cells weighted by each cell's orthogonal degree (number of in-bounds
    # neighbors). Verified against an independent brute-force over seeded grids.
    import random
    rng = random.Random(20240607)
    for _ in range(40):
        rows = rng.randint(1, 6)
        cols = rng.randint(1, 6)
        grid = [[rng.randint(-9, 9) for _ in range(cols)] for _ in range(rows)]
        out = solution.neighbor_sum_grid(grid)
        total_out = sum(sum(row) for row in out)
        # Weighted sum: each cell contributes value * (its own degree).
        weighted = 0
        for r in range(rows):
            for c in range(cols):
                deg = 0
                if r - 1 >= 0:
                    deg += 1
                if r + 1 < rows:
                    deg += 1
                if c - 1 >= 0:
                    deg += 1
                if c + 1 < cols:
                    deg += 1
                weighted += grid[r][c] * deg
        assert total_out == weighted
