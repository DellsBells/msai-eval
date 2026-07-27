# Orthogonal Neighbor Sum Grid

You are given a rectangular grid of integers. For every cell, compute the sum of
its **orthogonal** neighbors (the cells directly up, down, left, and right).
Diagonal cells are **not** neighbors, and the cell's own value is **not**
included. Cells on an edge or corner simply have fewer neighbors — treat any
position that falls outside the grid as contributing nothing (not zero-padding,
just absent).

Implement a single function:

```python
def neighbor_sum_grid(grid):
    ...
```

## Input

`grid` is a list of rows, where each row is a list of integers. The grid is
rectangular: every row has the same length. The grid may be empty (`[]`), and it
may contain rows of length zero only if the whole grid is `[]` — you will never
receive `[[]]`. Values may be negative.

## Output

Return a **new** grid (list of lists) with the same dimensions as the input.
Cell `(r, c)` of the output holds the sum of the up/down/left/right neighbors of
cell `(r, c)` in the input. Do not modify the input grid.

## Behavior details

- A cell in the interior has exactly 4 neighbors.
- A cell on a non-corner edge has 3 neighbors.
- A corner cell has 2 neighbors.
- A grid with a single cell (`[[x]]`) has no neighbors for that cell, so its
  output is `[[0]]`.
- For the empty grid `[]`, return `[]`.

## Examples

Example 1:

```
grid = [[1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]]

neighbor_sum_grid(grid) == [[6, 9, 8],
                            [13, 20, 17],
                            [12, 21, 14]]
```

Explanation for the center cell `(1,1)=5`: neighbors are `2` (up), `8` (down),
`4` (left), `6` (right), summing to `20`. For the top-left corner `(0,0)=1`:
neighbors are `2` (right) and `4` (down), summing to `6`.

Example 2:

```
grid = [[10, -3]]

neighbor_sum_grid(grid) == [[-3, 10]]
```

Each cell's only neighbor is the other one.

Example 3:

```
grid = [[5]]

neighbor_sum_grid(grid) == [[0]]
```
