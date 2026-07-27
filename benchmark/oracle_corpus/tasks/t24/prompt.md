# Deterministic Region Labeling by Value

You are given a rectangular grid of non-negative integers. Group the grid into
**regions** and assign each region a distinct positive label, then return a grid
of the same shape holding the label of every cell.

## Region definition

Two cells belong to the same region iff they are **orthogonally adjacent** (up,
down, left, right) **and hold the same integer value**. Diagonal adjacency never
connects cells. So a region is a maximal orthogonally-connected group of cells
that all share one value.

There is one special value: `0` is the **background**. Every background cell
gets label `0` and is never grouped into a numbered region (even two adjacent
background cells stay label `0`; background is not "a region").

## Labeling order (this is the exact rule the output must follow)

Scan the grid in **row-major order**: row `0` left-to-right, then row `1`, and so
on. The first not-yet-labeled non-background cell you encounter starts region
`1`; flood-fill its whole region and give every cell in it label `1`. Continue
scanning; the next unlabeled non-background cell you meet starts region `2`, and
so on. Labels are therefore assigned in the order regions are **first touched**
by the row-major scan, which is the order of each region's top-most, then
left-most cell (its "anchor").

Implement:

```python
def label_regions(grid):
    ...
```

Return a new grid (list of lists of ints) of the same dimensions, where each cell
holds its region label (`0` for background, or a positive region id).

## Input

`grid` is a list of rows; each row is a list of non-negative integers; the grid
is rectangular. It may be `[]` (return `[]`). It will not contain empty rows
unless the grid itself is `[]`.

## Output

A new grid of labels. Background cells (value `0`) map to `0`. Non-background
cells map to their region's label as defined above. Do not mutate the input.

## Behavior details

- Two cells with the same non-zero value that are only diagonally adjacent are in
  **different** regions (unless linked by an orthogonal same-value path).
- Two adjacent cells with **different** non-zero values are in different regions.
- Region labels are consecutive integers `1, 2, 3, ...` with no gaps; the count
  of distinct positive labels equals the number of regions.
- A single isolated non-background cell is its own region.

## Examples

Example 1:

```
grid = [[1, 1, 0],
        [0, 1, 2],
        [2, 2, 2]]
```

Row-major scan: `(0,0)=1` starts region 1 → the connected `1`s are
`(0,0),(0,1),(1,1)`. Next unlabeled non-zero is `(1,2)=2` → region 2 → connected
`2`s are `(1,2),(2,2),(2,1),(2,0)`. Result:

```
label_regions(grid) == [[1, 1, 0],
                        [0, 1, 2],
                        [2, 2, 2]]
```

Example 2 — same value split by a gap and by diagonal-only adjacency:

```
grid = [[5, 0, 5],
        [0, 5, 0],
        [5, 0, 5]]
```

Each `5` is orthogonally isolated (neighbors are all `0`), so every `5` is its
own region. Scanning row-major, they are labeled 1..5 in reading order:

```
label_regions(grid) == [[1, 0, 2],
                        [0, 3, 0],
                        [4, 0, 5]]
```

Example 3 — different values do not merge:

```
grid = [[7, 7, 8],
        [7, 8, 8]]

label_regions(grid) == [[1, 1, 2],
                        [1, 2, 2]]
```

The three `7`s form region 1; the three `8`s form region 2 (anchor `(0,2)` comes
after the `7` anchor `(0,0)` in reading order).
