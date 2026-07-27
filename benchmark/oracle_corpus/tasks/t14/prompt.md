# Nth-Weekday-of-Month Recurrence Expander

Implement a single function using only Python's standard library (the `datetime`
module is available):

```python
def nth_weekday_dates(year: int, weekday: int, n: int) -> list[str]:
    ...
```

## Behavior

Return every date in the given calendar `year` that is the **n-th occurrence of a
given weekday within its month**, as ISO date strings `"YYYY-MM-DD"`, in
chronological order (January through December).

- `weekday` is an integer 0..6 where `0 == Monday`, `1 == Tuesday`, ...,
  `6 == Sunday` (matching `datetime.date.weekday()`).
- `n` selects which occurrence within the month:
  - `n == 1` -> the **first** such weekday of the month.
  - `n == 2` -> the **second**, `n == 3` -> the **third**, `n == 4` -> the **fourth**.
  - `n == -1` -> the **last** such weekday of the month.

For each of the 12 months of `year`, compute the requested occurrence. Positive
`n` may not exist in a given month (e.g. some months have only four Mondays, so
the fifth would not exist) — in that case that month contributes **no** date.
`n == -1` (the last occurrence) always exists for every month, so it always
yields exactly 12 dates.

### Return value

A list of ISO date strings in chronological order. The list has at most 12
entries (fewer when a positive `n` does not occur in some months).

## Constraints

- Use only the standard library. Do not read the system clock, files, network,
  or environment. The output depends solely on the arguments.
- Assume valid inputs: `1 <= year <= 9999`, `0 <= weekday <= 6`, and
  `n` is one of `1, 2, 3, 4, -1`.

## Examples

```python
# First Monday of each month in 2026.
nth_weekday_dates(2026, 0, 1) == [
    "2026-01-05", "2026-02-02", "2026-03-02", "2026-04-06",
    "2026-05-04", "2026-06-01", "2026-07-06", "2026-08-03",
    "2026-09-07", "2026-10-05", "2026-11-02", "2026-12-07",
]

# Last Friday of each month in 2026 (weekday 4).
nth_weekday_dates(2026, 4, -1) == [
    "2026-01-30", "2026-02-27", "2026-03-27", "2026-04-24",
    "2026-05-29", "2026-06-26", "2026-07-31", "2026-08-28",
    "2026-09-25", "2026-10-30", "2026-11-27", "2026-12-25",
]

# Fifth Sunday does not exist in every month; asking for the 4th Sunday
# (weekday 6, n=4) yields exactly one date per month, all present.
len(nth_weekday_dates(2026, 6, 4)) == 12
```
