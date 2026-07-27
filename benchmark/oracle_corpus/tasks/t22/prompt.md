# Quarter-Turn Matrix Rotation

Implement a function that rotates a rectangular matrix by a multiple of 90
degrees.

```python
def rotate_quarters(matrix, k):
    ...
```

## Semantics

- `matrix` is a list of rows (each a list of values). It is rectangular: all rows
  have the same length. It may be empty (`[]`), representing a 0-row matrix. It
  will never contain empty rows unless the matrix itself is `[]`.
- `k` is an integer number of **clockwise** quarter turns. It may be zero,
  positive, or negative. A negative `k` rotates counter-clockwise. `k` may have a
  magnitude larger than 4; you must reduce it modulo 4 (so `k = 5` behaves like
  `k = 1`, and `k = -1` behaves like `k = 3`).

A single clockwise quarter turn maps an `R x C` matrix to a `C x R` matrix where
the new cell `(i, j)` equals the old cell `(R - 1 - j, i)`. Equivalently, the
first column of the original (read top-to-bottom) becomes the first row of the
result (read left-to-right)... no: the **first column read bottom-to-top**
becomes the first row. Concretely, the original top row becomes the rightmost
column of the result.

## Requirements

- Return a **new** matrix; do not mutate the input.
- After reducing `k` modulo 4, apply that many clockwise quarter turns.
- `k = 0` (or any multiple of 4) returns a copy of the matrix with identical
  contents and shape.
- The empty matrix `[]` rotates to `[]` for any `k`.

## Examples

Example 1 — one clockwise turn of a 2x3 matrix:

```
matrix = [[1, 2, 3],
          [4, 5, 6]]

rotate_quarters(matrix, 1) == [[4, 1],
                               [5, 2],
                               [6, 3]]
```

The original top row `[1, 2, 3]` becomes the rightmost column (top-to-bottom
`1, 2, 3`).

Example 2 — two turns (180 degrees) reverse everything:

```
matrix = [[1, 2, 3],
          [4, 5, 6]]

rotate_quarters(matrix, 2) == [[6, 5, 4],
                               [3, 2, 1]]
```

Example 3 — negative k rotates counter-clockwise; `k = -1` equals three
clockwise turns:

```
matrix = [[1, 2, 3],
          [4, 5, 6]]

rotate_quarters(matrix, -1) == [[3, 6],
                                [2, 5],
                                [1, 4]]
```

Example 4 — large k reduces modulo 4:

```
rotate_quarters([[1, 2], [3, 4]], 5) == rotate_quarters([[1, 2], [3, 4]], 1)
                                     == [[3, 1],
                                         [4, 2]]
```
