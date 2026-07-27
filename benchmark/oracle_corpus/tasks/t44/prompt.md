# Windowed Monotone Streak Scanner

For each sliding window of a signal you must find the strongest *monotone streak*
inside it — the longest run of consecutive readings that are either strictly
increasing or strictly decreasing — and report the single best window.

## Function to implement

```python
def best_monotone_window(readings, k):
    ...
```

- `readings` is a list of numbers (`int` or `float`).
- `k` is a positive integer window size (`k >= 1`).

## Definitions

Consider a window: `k` consecutive readings. Inside a window:

- A **rising streak** is a maximal run of consecutive readings each strictly
  greater than the previous one (`a < b < c ...`).
- A **falling streak** is a maximal run of consecutive readings each strictly
  less than the previous one (`a > b > c ...`).
- The length of a streak is the number of readings in it (a single reading is a
  streak of length 1 that is neither rising nor falling on its own).

For a window, define:

- `up_len` = the length of the longest rising streak in the window (at least 1).
- `down_len` = the length of the longest falling streak in the window (at least 1).

The window's **score** is `max(up_len, down_len)`. The window's **direction** is:

- `"up"` if `up_len > down_len`,
- `"down"` if `down_len > up_len`,
- `"flat"` if `up_len == down_len` (this includes the case where the best streak
  has length 1, e.g. a strictly non-monotone or constant window).

## What to return

Slide a window of exactly `k` readings across `readings`. Among all windows, pick
the one with the **highest score**. Return the tuple:

```
(score, start_index, direction)
```

- `score` is that highest score.
- `start_index` is the start index of the chosen window.
- `direction` is the direction string of the chosen window.

Tie-breaking, applied in order:

1. Highest `score` wins.
2. If scores tie, the **earliest** window (smallest `start_index`) wins.

(Once the window is chosen by the rules above, its own direction is reported,
even if another window with the same score had a different direction.)

Edge cases:

- If `len(readings) < k`, no complete window exists: return `(0, -1, "none")`.
- If `k == 1`, every window has `up_len == down_len == 1`, so every score is 1
  and every direction is `"flat"`; the earliest window (index 0) is chosen.
- If `k` is less than 1, raise a `ValueError`.

## Constraints

- Do not mutate the input list.
- Use only the Python standard library.
- Equal adjacent readings break both rising and falling streaks (equality is
  neither strictly increasing nor strictly decreasing).

## Examples

Example 1:

```python
best_monotone_window([1, 2, 3, 1, 2], 4)
# Window [1,2,3,1] (start 0): rising streak 1<2<3 length 3, longest falling 3>1
#   length 2. up_len=3, down_len=2 -> score 3, direction "up".
# Window [2,3,1,2] (start 1): rising 2<3 len 2 and 1<2 len 2 -> up_len=2;
#   falling 3>1 len 2 -> down_len=2 -> score 2, direction "flat".
# Best score 3 at start 0.
# -> (3, 0, "up")
```

Example 2:

```python
best_monotone_window([5, 4, 3, 2, 1], 3)
# Every window is strictly falling: score 3, direction "down".
# Earliest is start 0.
# -> (3, 0, "down")
```

Example 3:

```python
best_monotone_window([7, 7, 7], 2)
# Windows [7,7] and [7,7]: no strict move, up_len=down_len=1 -> score 1, "flat".
# Earliest start 0.
# -> (1, 0, "flat")
```
