# Uncovered Gaps Within a Window

You are scheduling reservations on a shared resource over a continuous time
window `[window_start, window_end)`. Time is measured with real (floating-point)
values. Each reservation is a half-open interval `[start, end)` that occupies the
resource from `start` (inclusive) up to but **not** including `end`.

Write a function:

```python
def find_gaps(reservations, window_start, window_end):
    ...
```

that returns the list of maximal half-open sub-intervals of
`[window_start, window_end)` that are **not** covered by any reservation. These
are the free slots.

## Rules

- Intervals are **half-open**: `[start, end)` covers points `x` with
  `start <= x < end`. Two reservations `[0, 2)` and `[2, 4)` therefore do **not**
  overlap and leave **no** gap between them — together they cover `[0, 4)`.
- The output covers exactly the portion of `[window_start, window_end)` that no
  reservation touches. It is expressed as a list of half-open intervals
  `[a, b)` with `a < b`.
- Only the part of each reservation that intersects the window matters.
  Reservations may extend outside the window, or lie entirely outside it; clip
  them to the window before reasoning about gaps.
- A reservation with `start >= end` is degenerate (covers nothing) and must be
  ignored.
- The returned list is sorted by start ascending and contains no zero-width
  intervals.
- Each returned interval is a two-element `list` `[a, b]` of the same numeric
  values you were given (do not round).
- If `window_start >= window_end`, return `[]`.
- If there are no (effective) reservations, the entire window is one gap
  (assuming the window is non-empty).
- Do not mutate the input list.

## Examples

```python
find_gaps([[1, 3], [5, 8]], 0, 10)
# -> [[0, 1], [3, 5], [8, 10]]

find_gaps([[0, 2], [2, 4]], 0, 4)
# -> []            # half-open intervals tile [0,4) with no gap

find_gaps([[-5, 2], [8, 20]], 0, 10)
# -> [[2, 8]]      # reservations clipped to the window

find_gaps([], 0, 5)
# -> [[0, 5]]
```

## Constraints

- `0 <= len(reservations) <= 10000`
- Endpoints and window bounds are ints or floats.
- `start` and `end` within a reservation satisfy no ordering guarantee — you must
  handle `start >= end` by ignoring that reservation.
