import solution


def test_two_pockets():
    grid = ["#####",
            "#.#.#",
            "#####"]
    assert solution.count_enclosed_regions(grid) == 2


def test_region_escapes_to_border():
    grid = ["#.###",
            "#...#",
            "#####"]
    assert solution.count_enclosed_regions(grid) == 0


def test_single_center_pocket():
    grid = [".....",
            ".###.",
            ".#.#.",
            ".###.",
            "....."]
    assert solution.count_enclosed_regions(grid) == 1


def test_diagonal_cells_are_separate_regions():
    # Five interior '.' cells, each walled off orthogonally. Diagonal adjacency
    # must NOT merge them.
    grid = ["#####",
            "#.#.#",
            "##.##",
            "#.#.#",
            "#####"]
    assert solution.count_enclosed_regions(grid) == 5


def test_all_open_touches_border():
    grid = ["...",
            "...",
            "..."]
    assert solution.count_enclosed_regions(grid) == 0


def test_grid_too_small_no_interior():
    assert solution.count_enclosed_regions(["..", ".."]) == 0
    assert solution.count_enclosed_regions([".", "."]) == 0
    assert solution.count_enclosed_regions(["..."]) == 0


def test_empty_grid():
    assert solution.count_enclosed_regions([]) == 0


def test_single_enclosed_multi_cell_region():
    grid = ["#####",
            "#...#",
            "#...#",
            "#...#",
            "#####"]
    # One connected interior blob, no border contact.
    assert solution.count_enclosed_regions(grid) == 1


def test_mixed_enclosed_and_escaping():
    grid = ["#.####",
            "#.#..#",
            "###..#",
            "#....#",
            "######"]
    # The left column '.' at (0,1),(1,1) reaches the top border -> escapes.
    # The right blob at rows 1-3 is fully interior -> 1 enclosed region.
    assert solution.count_enclosed_regions(grid) == 1


def test_region_escapes_only_via_last_column():
    # The open region at (1,1),(1,2) touches the LAST column (col 2) and no
    # other border cell, so it escapes -> 0. Guards against a last-column
    # border check that uses `c == cols` instead of `c == cols - 1`.
    grid = ["###",
            "#..",
            "###"]
    assert solution.count_enclosed_regions(grid) == 0


def test_region_escapes_only_via_last_row():
    # The open region at (1,1),(2,1) touches the LAST row (row 2) and no other
    # border cell, so it escapes -> 0. Guards against a last-row border check
    # that uses `r == rows` instead of `r == rows - 1`.
    grid = ["###",
            "#.#",
            "#.#"]
    assert solution.count_enclosed_regions(grid) == 0


def test_last_column_escape_does_not_inflate_enclosed_count():
    # One genuinely enclosed pocket at (1,1), plus a region at (2,3),(2,4) whose
    # only border contact is the last column (col 4). Correct answer is 1; a
    # last-column off-by-one would wrongly count the escaping region -> 2.
    grid = ["#####",
            "#.###",
            "###..",
            "#####",
            "#####"]
    assert solution.count_enclosed_regions(grid) == 1


def test_does_not_mutate_input():
    grid = ["#####",
            "#.#.#",
            "#####"]
    snapshot = list(grid)
    solution.count_enclosed_regions(grid)
    assert grid == snapshot


def test_property_never_exceeds_open_count_and_nonneg():
    # Property: result is non-negative and never exceeds the number of interior
    # open cells; also, a grid with no interior open cells yields 0. Checked
    # against a brute-force 4-connectivity reference over seeded grids.
    import random
    rng = random.Random(4242)

    def brute(grid):
        rows = len(grid)
        if rows == 0:
            return 0
        cols = len(grid[0])
        if rows < 3 or cols < 3:
            return 0
        seen = set()
        count = 0
        for sr in range(rows):
            for sc in range(cols):
                if grid[sr][sc] != '.' or (sr, sc) in seen:
                    continue
                stack = [(sr, sc)]
                seen.add((sr, sc))
                border = False
                while stack:
                    r, c = stack.pop()
                    if r in (0, rows - 1) or c in (0, cols - 1):
                        border = True
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if grid[nr][nc] == '.' and (nr, nc) not in seen:
                                seen.add((nr, nc))
                                stack.append((nr, nc))
                if not border:
                    count += 1
        return count

    for _ in range(80):
        rows = rng.randint(0, 6)
        cols = rng.randint(1, 6) if rows > 0 else 0
        if rows == 0:
            grid = []
        else:
            grid = ["".join(rng.choice("..#") for _ in range(cols)) for _ in range(rows)]
        result = solution.count_enclosed_regions(grid)
        assert result >= 0
        assert result == brute(grid)
        # never more than number of interior open cells
        interior_open = 0
        if rows >= 3 and cols >= 3:
            for r in range(1, rows - 1):
                for c in range(1, cols - 1):
                    if grid[r][c] == '.':
                        interior_open += 1
        assert result <= interior_open


def test_property_last_border_contact_matches_bruteforce():
    # Adversarial property: build grids seeded so that some regions' ONLY border
    # contact is the last row or last column. A walled interior with a single
    # open "tunnel" that pokes out through exactly one of the four borders lets
    # us hit last-row/last-column-only escapes that the earlier property test's
    # uniform random grids rarely isolate. Checked against a brute-force
    # 4-connectivity reference.
    import random
    rng = random.Random(1337)

    def brute(grid):
        rows = len(grid)
        if rows == 0:
            return 0
        cols = len(grid[0])
        if rows < 3 or cols < 3:
            return 0
        seen = set()
        count = 0
        for sr in range(rows):
            for sc in range(cols):
                if grid[sr][sc] != '.' or (sr, sc) in seen:
                    continue
                stack = [(sr, sc)]
                seen.add((sr, sc))
                border = False
                while stack:
                    r, c = stack.pop()
                    if r in (0, rows - 1) or c in (0, cols - 1):
                        border = True
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if grid[nr][nc] == '.' and (nr, nc) not in seen:
                                seen.add((nr, nc))
                                stack.append((nr, nc))
                if not border:
                    count += 1
        return count

    saw_last_col_escape = 0
    saw_last_row_escape = 0
    for _ in range(120):
        rows = rng.randint(4, 7)
        cols = rng.randint(4, 7)
        # Start with an all-wall grid so the border is solid.
        cells = [['#'] * cols for _ in range(rows)]
        # Carve a random interior open blob.
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if rng.random() < 0.5:
                    cells[r][c] = '.'
        # With some probability, punch a single tunnel out through exactly one
        # border side by opening one border cell adjacent to an interior open
        # cell. Bias toward the last row / last column to exercise those edges.
        side = rng.choice(["last_col", "last_row", "first_col", "first_row",
                           "none", "last_col", "last_row"])
        if side == "last_col":
            r = rng.randint(1, rows - 2)
            if cells[r][cols - 2] == '.':
                cells[r][cols - 1] = '.'
        elif side == "last_row":
            c = rng.randint(1, cols - 2)
            if cells[rows - 2][c] == '.':
                cells[rows - 1][c] = '.'
        elif side == "first_col":
            r = rng.randint(1, rows - 2)
            if cells[r][1] == '.':
                cells[r][0] = '.'
        elif side == "first_row":
            c = rng.randint(1, cols - 2)
            if cells[1][c] == '.':
                cells[0][c] = '.'
        grid = ["".join(row) for row in cells]
        result = solution.count_enclosed_regions(grid)
        assert result == brute(grid), (grid, result, brute(grid))
        # Track whether we produced regions whose sole border contact is a
        # trailing edge (a correct impl counts these as escaped, not enclosed).
        if side == "last_col" and grid[r][cols - 1] == '.':
            saw_last_col_escape += 1
        if side == "last_row" and grid[rows - 1][c] == '.':
            saw_last_row_escape += 1
    # Guard against the generator degenerating and never testing the edges.
    assert saw_last_col_escape >= 1
    assert saw_last_row_escape >= 1
