# Count Enclosed Zero-Regions

You are given a rectangular grid of single-character cells. Two characters
matter: `'.'` marks an *open* cell and `'#'` marks a *wall*. A **region** is a
maximal group of open cells connected to each other **orthogonally** (up, down,
left, right — never diagonally).

A region is **enclosed** if none of its cells sits on the outer border of the
grid (i.e. no cell in the region is in the first/last row or the first/last
column). A region that touches the border in any cell "escapes" and is not
enclosed.

Implement:

```python
def count_enclosed_regions(grid):
    ...
```

Return the **number** of enclosed open-regions.

## Input

`grid` is a list of strings; each string is one row and all rows have the same
length. Every character is either `'.'` or `'#'`. The grid may be empty (`[]`),
and rows may be empty strings only if the grid is `[]` (you will not receive
`[""]`).

## Output

An integer: how many distinct orthogonally-connected regions of `'.'` cells are
fully enclosed (touch no border cell).

## Behavior details

- Connectivity is 4-directional only. Diagonally adjacent open cells belong to
  **different** regions unless linked through an orthogonal path.
- A single open cell not on the border counts as an enclosed region (size 1 is
  allowed).
- If every open cell touches the border, the answer is `0`.
- A grid with fewer than 3 rows or fewer than 3 columns has no interior, so the
  answer is always `0` (every cell is a border cell).
- The empty grid returns `0`.

## Examples

Example 1 — one pocket in the middle:

```
grid = ["#####",
        "#.#.#",
        "#####"]
```

Row indices 0 and 2 are border rows; columns 0 and 4 are border columns. The two
`'.'` cells are at `(1,1)` and `(1,3)`; neither is on the border, and they are
not orthogonally connected (a wall sits between them). So there are 2 enclosed
regions → `count_enclosed_regions(grid) == 2`.

Example 2 — a region that escapes to the border:

```
grid = ["#.###",
        "#...#",
        "#####"]
```

The open cells form one connected region including `(0,1)`, which lies on the top
border. The whole region escapes, so it is not enclosed →
`count_enclosed_regions(grid) == 0`.

Example 3 — mixed:

```
grid = [".....",
        ".###.",
        ".#.#.",
        ".###.",
        "....."]
```

The outer ring of `'.'` cells touches the border and escapes. The single `'.'`
at `(2,2)` is walled off in the interior and touches no border →
`count_enclosed_regions(grid) == 1`.
