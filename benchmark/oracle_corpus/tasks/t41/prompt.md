# Longest Above-Threshold Run

You are analyzing a sequence of numeric sensor readings and need to find the
longest consecutive run of readings that are **strictly greater** than a given
threshold.

## Function to implement

```python
def longest_above_run(readings, threshold):
    ...
```

- `readings` is a list of numbers (`int` or `float`). It may be empty.
- `threshold` is a number (`int` or `float`).

## Behavior

A "run" is a maximal block of consecutive readings whose value is **strictly
greater than** `threshold` (i.e. `reading > threshold`). Return information about
the **longest** such run as a tuple:

```
(length, start_index)
```

where:

- `length` is the number of readings in the longest qualifying run.
- `start_index` is the 0-based index in `readings` where that longest run begins.

Tie-breaking rule: if two or more runs share the same maximal length, return the
one that occurs **earliest** (smallest `start_index`).

If no reading is strictly greater than `threshold` (including when `readings` is
empty), return `(0, -1)`.

Values exactly equal to `threshold` do **not** qualify and break a run.

## Constraints

- Do not mutate the input list.
- Use only the Python standard library.
- Comparisons use ordinary numeric comparison, so mixing `int` and `float` is fine.

## Examples

Example 1:

```python
longest_above_run([1, 5, 6, 2, 7, 8, 9, 3], 4)
# Runs above 4: [5, 6] at index 1 (length 2), [7, 8, 9] at index 4 (length 3).
# Longest is length 3 starting at index 4.
# -> (3, 4)
```

Example 2:

```python
longest_above_run([10, 10, 3, 10, 10], 10)
# Nothing is strictly greater than 10.
# -> (0, -1)
```

Example 3:

```python
longest_above_run([9, 9, 1, 8, 8], 5)
# Two runs of length 2: [9, 9] at index 0 and [8, 8] at index 3.
# Tie broken toward the earliest -> (2, 0)
```
