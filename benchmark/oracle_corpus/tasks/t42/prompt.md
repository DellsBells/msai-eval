# Rolling Window Range

Given a stream of numeric readings and a fixed window size `k`, compute the
range (max minus min) of every contiguous window of length `k`, and report where
the largest range occurs.

## Function to implement

```python
def rolling_ranges(readings, k):
    ...
```

- `readings` is a list of numbers (`int` or `float`).
- `k` is a positive integer window size (`k >= 1`).

## Behavior

Slide a window of exactly `k` consecutive readings across `readings` from left to
right. There are `len(readings) - k + 1` such windows when `len(readings) >= k`.
For each window compute its **range**: `max(window) - min(window)`.

Return a tuple `(ranges, peak_index)`:

- `ranges` is a list of the per-window range values, in window order. The window
  starting at index `i` produces `ranges[i]`.
- `peak_index` is the **start index** of the window with the largest range. If
  several windows share the largest range, choose the **earliest** (smallest
  start index).

Edge cases:

- If `len(readings) < k`, there are no complete windows: return `([], -1)`.
- Invalid window sizes must be rejected: if `k` is less than 1, raise a
  `ValueError`.

## Constraints

- Do not mutate the input list.
- Use only the Python standard library.
- Ranges are computed with ordinary subtraction, so `int` inputs give `int`
  ranges and `float` inputs give `float` ranges. Do not force a type conversion.

## Examples

Example 1:

```python
rolling_ranges([1, 3, 2, 8, 5], 3)
# Windows: [1,3,2] range 2, [3,2,8] range 6, [2,8,5] range 6.
# ranges = [2, 6, 6]; largest range is 6, earliest at start index 1.
# -> ([2, 6, 6], 1)
```

Example 2:

```python
rolling_ranges([4, 4, 4, 4], 2)
# Every window has range 0; earliest peak is index 0.
# -> ([0, 0, 0], 0)
```

Example 3:

```python
rolling_ranges([9, 1], 3)
# Window size exceeds the number of readings.
# -> ([], -1)
```
