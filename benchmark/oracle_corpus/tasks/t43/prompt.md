# Rolling Baseline Anomaly Flags

You are monitoring a live signal and want to flag readings that deviate too far
from a **local baseline** built from the immediately preceding readings.

## Function to implement

```python
def flag_anomalies(readings, window, threshold):
    ...
```

- `readings` is a list of numbers (`int` or `float`).
- `window` is a positive **odd** integer: the number of preceding readings used
  to build the baseline.
- `threshold` is a non-negative number.

## Behavior

Walk through `readings` from left to right. For the reading at index `i`, the
baseline is the **median of the `window` readings immediately before it**, i.e.
the readings at indices `i - window` through `i - 1` inclusive.

Because `window` is odd, the median is simply the middle value of those preceding
readings after sorting them ascending.

The reading at index `i` is an **anomaly** when there are at least `window`
readings before it (so a full baseline exists) **and**

```
abs(readings[i] - baseline) > threshold
```

Note the comparison is **strict**: a deviation exactly equal to `threshold` is
**not** an anomaly.

The first `window` readings can never be anomalies, because no complete baseline
window precedes them.

Return a list of the **0-based indices** of all anomalous readings, in ascending
order.

## Validation

- If `window` is less than 1, raise a `ValueError`.
- If `window` is even, raise a `ValueError`.
- If `threshold` is negative, raise a `ValueError`.

## Constraints

- Do not mutate the input list.
- Use only the Python standard library.
- The baseline for index `i` uses only readings strictly before `i`; the current
  reading is never part of its own baseline.

## Examples

Example 1:

```python
flag_anomalies([10, 10, 10, 10, 50, 10, 10], 3, 5)
# Index 3: baseline = median(10,10,10) = 10, |10-10|=0, not an anomaly.
# Index 4: baseline = median(10,10,10) = 10, |50-10|=40 > 5 -> anomaly.
# Index 5: baseline = median(10,10,50) = 10, |10-10|=0, not an anomaly.
# Index 6: baseline = median(10,50,10) = 10, |10-10|=0, not an anomaly.
# -> [4]
```

Example 2:

```python
flag_anomalies([1, 2, 3, 4, 5], 5, 0)
# Only index >= 5 could be flagged, but the list ends at index 4.
# -> []
```

Example 3:

```python
flag_anomalies([5, 5, 8, 5, 5], 1, 2)
# window = 1, baseline is just the single previous reading.
# Index 1: |5-5|=0. Index 2: |8-5|=3 > 2 -> anomaly.
# Index 3: |5-8|=3 > 2 -> anomaly. Index 4: |5-5|=0.
# -> [2, 3]
```
