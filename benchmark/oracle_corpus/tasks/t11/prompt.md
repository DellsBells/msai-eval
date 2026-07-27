# Total Covered Length and Multiply-Covered Length

You are analyzing sensor coverage along a 1-D line. Each sensor covers a
half-open interval `[start, end)` of positions. Sensors overlap freely. You need
two summary measurements of the combined coverage.

Write a function:

```python
def coverage_stats(intervals):
    ...
```

that returns a tuple `(total_covered, multi_covered)` where:

- `total_covered` is the length of the **union** of all intervals — the total
  measure of the line covered by at least one sensor.
- `multi_covered` is the total length of the line covered by **two or more**
  sensors simultaneously (the measure of the region with coverage depth `>= 2`).

## Rules

- Intervals are **half-open**: `[start, end)`. Its length is `end - start`.
- A sensor with `start >= end` covers nothing (length 0) and contributes to
  neither statistic; ignore it.
- Both returned numbers are lengths (non-negative). Return the numeric value
  that naturally results from subtracting/adding the endpoints — **do not force
  a conversion** with `int(...)`, `float(...)`, `round(...)`, etc. Concretely:
  - If every interval you actually accumulate has integer endpoints, both
    returned lengths must be Python `int`s (`type(x) is int`). A result of zero
    from integer arithmetic is the `int` `0`, not `0.0`.
  - If any interval that contributes to a length has a `float` endpoint, the
    corresponding length is a `float` (as normal Python `int`/`float`
    arithmetic produces).
  - The simplest way to satisfy this is to start each accumulator at the integer
    `0` and add plain `end - start` widths — Python's arithmetic then yields
    `int` for all-integer data and `float` once a float is involved. Never wrap
    the return values in `int()` or `float()`.
- For the empty-input case (and any input where nothing is covered) return the
  integer tuple `(0, 0)` — both elements are `int`.
- Where a boundary touches (e.g. `[0, 2)` and `[2, 4)`), the shared point has
  zero width and contributes nothing to `multi_covered`.
- `total_covered >= multi_covered >= 0` always.
- For empty input, return `(0, 0)`.
- Do not mutate the input.

## Definitions by example

- `[[0, 5)]` — one sensor. `total_covered = 5`, `multi_covered = 0`.
- `[[0, 5), [2, 7)]` — they overlap on `[2, 5)` (length 3). Union is `[0, 7)`
  (length 7). So `total_covered = 7`, `multi_covered = 3`.
- `[[0, 4), [1, 3), [2, 6)]` — union is `[0, 6)` = 6. Depth-2-or-more region:
  positions covered by at least two sensors are `[1, 4)` (length 3)... but check
  carefully: `[1,2)` covered by sensors 1&2 (depth 2), `[2,3)` by all three
  (depth 3), `[3,4)` by sensors 1&3 (depth 2), `[4,6)` by sensor 3 only
  (depth 1). So the `>=2` region is `[1, 4)` of length 3. `total_covered = 6`,
  `multi_covered = 3`.

## Examples

```python
coverage_stats([])
# -> (0, 0)

coverage_stats([[0, 5]])
# -> (5, 0)

coverage_stats([[0, 5], [2, 7]])
# -> (7, 3)

coverage_stats([[0, 2], [2, 4]])
# -> (4, 0)      # touching, no double coverage

coverage_stats([[0, 4], [1, 3], [2, 6]])
# -> (6, 3)
```

## Constraints

- `0 <= len(intervals) <= 20000`
- Endpoints are ints or floats.
- Each interval is a two-element list/tuple `[start, end]`.
