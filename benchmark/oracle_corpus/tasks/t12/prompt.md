# Interval Set Difference and Peak Coverage Depth

You maintain two collections of half-open intervals over a real number line: a
set of **allowed** ranges and a set of **blocked** ranges. Endpoints may be
integers or floats, and intervals are reasoned about as continuous real
intervals (not as sets of integer points). You must compute what remains
available after removing everything blocked, and separately report how heavily
the *allowed* ranges overlapped before subtraction.

Write a function:

```python
def resolve_ranges(allowed, blocked):
    ...
```

that returns a dictionary with exactly these two keys:

- `"available"`: the normalized list of half-open intervals covering every point
  that is inside **at least one** allowed interval **and** inside **no** blocked
  interval.
- `"peak_depth"`: the maximum number of *allowed* intervals that cover any single
  real point (the maximum coverage depth over the allowed set alone, before any
  subtraction). This is a maximum over **all** real points in the covered
  region, not merely over integer points: if two allowed intervals overlap on a
  sub-unit region such as `[0.4, 0.6)` that contains no integer, that region
  still has depth `2`. Blocked intervals do **not** affect this number.

## Semantics

- All intervals are **half-open**: `[start, end)` covers every real `x` with
  `start <= x < end`.
- An interval with `start >= end` is empty and is ignored everywhere (it neither
  contributes coverage, depth, nor blocking).
- **Normalized** means: sorted by start ascending, non-overlapping, and with no
  two intervals that could be joined without changing the covered point set. For
  half-open intervals `[a, b)` and `[b, c)` that share the boundary `b`, they
  tile contiguously and MUST be joined into `[a, c)` (there is no point between
  them). Intervals with a genuine gap stay separate.
- Each interval in `"available"` is a two-element `list` `[start, end]` with
  `start < end`.
- `"peak_depth"` is a non-negative integer. It is `0` when there are no
  effective allowed intervals.
- If nothing is available, `"available"` is `[]`.
- Endpoints may be negative. Do not mutate the inputs.

## Worked reasoning

For `allowed = [[0, 10]]`, `blocked = [[3, 5], [7, 8]]`:
Start from `[0, 10)`. Remove `[3, 5)` -> leaves `[0, 3)` and `[5, 10)`. Remove
`[7, 8)` -> `[5, 10)` splits into `[5, 7)` and `[8, 10)`. Result available:
`[[0, 3], [5, 7], [8, 10]]`. Peak depth of allowed alone is `1`.

For `allowed = [[0, 4], [2, 6]]`, `blocked = []`:
Allowed union is `[0, 6)`, so available is `[[0, 6]]`. The point set `[2, 4)` is
covered by both allowed intervals, so `peak_depth` is `2`.

For `allowed = [[0, 5]]`, `blocked = [[0, 5]]`:
Everything allowed is blocked -> available `[]`, peak_depth `1`.

For `allowed = [[0.0, 0.6], [0.4, 1.0]]`, `blocked = []`:
The two intervals overlap on `[0.4, 0.6)`, a region that contains no integer
point yet is still doubly covered, so `peak_depth` is `2`. Their union is
`[0.0, 1.0)`, so available is `[[0.0, 1.0]]`.

## Examples

```python
resolve_ranges([[0, 10]], [[3, 5], [7, 8]])
# -> {"available": [[0, 3], [5, 7], [8, 10]], "peak_depth": 1}

resolve_ranges([[0, 4], [2, 6]], [])
# -> {"available": [[0, 6]], "peak_depth": 2}

resolve_ranges([[0, 5]], [[0, 5]])
# -> {"available": [], "peak_depth": 1}

resolve_ranges([[0, 3], [3, 6]], [])
# -> {"available": [[0, 6]], "peak_depth": 1}   # touching allowed ranges join

resolve_ranges([], [[1, 2]])
# -> {"available": [], "peak_depth": 0}

resolve_ranges([[0.0, 1.5], [0.5, 2.0]], [])
# -> {"available": [[0.0, 2.0]], "peak_depth": 2}   # overlap [0.5, 1.5) has depth 2
```

## Constraints

- `0 <= len(allowed) <= 20000`, `0 <= len(blocked) <= 20000`
- Endpoints are ints or floats with the half-open meaning above.
- Each interval is a two-element list/tuple `[start, end]`.
