# Working Days Between Two Dates

Implement a single function using only Python's standard library (the `datetime`
module is available):

```python
def working_days(start: str, end: str, holidays: list[str]) -> int:
    ...
```

## Behavior

Count the number of **working days** in the inclusive date range from `start`
to `end`. A day counts as a working day when **all** of the following hold:

1. It is a weekday — Monday through Friday. Saturday and Sunday never count.
2. It is **not** listed in `holidays`.

### Inputs

- `start` and `end` are date strings in ISO format `"YYYY-MM-DD"`.
- `holidays` is a list of date strings, each in the same `"YYYY-MM-DD"` format.
  The list may be empty, may contain duplicates, and may contain dates that fall
  outside the `[start, end]` range or that land on weekends — any such entries
  have no effect on the count.
- The range is **inclusive** of both `start` and `end`.

### Ordering and empty ranges

- If `start` and `end` are the same date, the range contains exactly that one day.
- If `start` is **after** `end`, the range is empty and the function returns `0`.
  (Do not swap the endpoints.)

### Return value

Return the integer count of working days.

## Constraints

- Use only the standard library. Do not read the system clock, files, network,
  or environment. The result depends solely on the arguments.
- Dates are always well-formed and use the proleptic Gregorian calendar (the
  calendar `datetime.date` implements). Assume years in the range 1..9999.

## Examples

```python
# Mon 2026-01-05 .. Fri 2026-01-09 is a full work week: 5 working days.
working_days("2026-01-05", "2026-01-09", []) == 5

# Same week but 2026-01-07 (Wednesday) is a holiday: 4 working days.
working_days("2026-01-05", "2026-01-09", ["2026-01-07"]) == 4

# Fri 2026-01-02 .. Mon 2026-01-05 spans a weekend: only Fri and Mon count -> 2.
working_days("2026-01-02", "2026-01-05", []) == 2

# start after end -> empty range -> 0.
working_days("2026-01-10", "2026-01-05", []) == 0
```
