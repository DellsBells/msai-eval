# Merge Touching and Overlapping Intervals

You are given a list of closed integer intervals. Each interval is a two-element
list or tuple `[start, end]` with `start <= end`. Intervals may appear in any
order, may overlap, may be fully nested inside one another, and may merely
*touch* at an endpoint.

Write a function:

```python
def merge_intervals(intervals):
    ...
```

that returns the smallest possible list of non-overlapping intervals that covers
exactly the same set of points as the input.

## Rules

- Intervals are **closed**: `[start, end]` includes both `start` and `end`.
- Two intervals must be merged when they overlap **or when they touch**. Because
  the intervals are closed and integer-valued, `[1, 3]` and `[3, 5]` share the
  point `3`, so they merge into `[1, 5]`. Additionally, intervals that are
  *adjacent* with no gap — such as `[1, 3]` and `[4, 6]`, where `4 == 3 + 1` —
  must also be merged into `[1, 6]`, since there is no integer strictly between
  them. In other words, merge whenever the next interval's start is `<=` the
  current end `+ 1`.
- The returned list must be sorted by start ascending.
- Each element of the returned list must be a two-element `list` `[start, end]`
  (not a tuple), with `start <= end`.
- The input list must **not** be mutated.
- An empty input returns an empty list.
- Input values may be negative.

## Examples

```python
merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])
# -> [[1, 6], [8, 10], [15, 18]]

merge_intervals([[1, 4], [4, 5]])
# -> [[1, 5]]           # they touch at 4

merge_intervals([[1, 2], [3, 4]])
# -> [[1, 4]]           # adjacent integers, no gap between 2 and 3

merge_intervals([[5, 7], [1, 2]])
# -> [[1, 2], [5, 7]]   # a real gap (3 and 4 are uncovered)
```

## Constraints

- `0 <= len(intervals) <= 10000`
- Each interval has integer endpoints with `start <= end`.
- Endpoint magnitudes fit comfortably in normal Python integers.
