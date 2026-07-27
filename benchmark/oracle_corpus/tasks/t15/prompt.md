# ISO Week Bucketing

Implement a single function using only Python's standard library (the `datetime`
module is available):

```python
def iso_week_counts(dates: list[str]) -> list[tuple[str, int]]:
    ...
```

## Behavior

Group a list of dates into **ISO 8601 week** buckets and report how many dates
fall in each bucket.

- Each element of `dates` is an ISO date string `"YYYY-MM-DD"`.
- For each date, compute its **ISO year** and **ISO week number** (as defined by
  the ISO 8601 calendar, which `datetime.date.isocalendar()` returns). Note the
  ISO year can differ from the calendar year for dates in early January or late
  December.
- The bucket **key** is a string of the form `"YYYY-Www"` where `YYYY` is the
  ISO year, **always rendered as exactly 4 digits, zero-padded on the left**,
  and `ww` is the 2-digit, zero-padded ISO week number. So the key is always
  exactly 8 characters long. For example ISO year 2026, week 1 -> `"2026-W01"`;
  ISO year 2020, week 53 -> `"2020-W53"`; ISO year 999, week 24 -> `"0999-W24"`;
  ISO year 7, week 1 -> `"0007-W01"`.

### Return value

Return a list of `(key, count)` tuples, where `count` is the number of input
dates that fall in that ISO week. The list must be sorted:

1. **primarily by the key in ascending lexicographic order** (which, because of
   the fixed-width format, is also chronological by ISO year then week).

Every distinct bucket that has at least one date appears exactly once. Buckets
with zero dates are not included. Duplicate input dates each count.

### Edge cases

- An empty input list returns an empty list `[]`.
- The same calendar date appearing multiple times contributes to the count each
  time.
- Dates near a year boundary must use their **ISO** year/week, not the calendar
  year. For instance `2021-01-01` belongs to ISO week `2020-W53`, and
  `2019-12-30` belongs to ISO week `2020-W01`.

## Constraints

- Use only the standard library. Do not read the system clock, files, network,
  or environment. The output depends solely on the argument.
- Assume all date strings are well-formed `"YYYY-MM-DD"` strings with the year
  written as exactly 4 digits (e.g. `"0999-06-15"`, `"0007-12-31"`). Years are
  in range 1..9999, so ISO years below 1000 do occur and their keys must still
  be zero-padded to 4 digits.

## Examples

```python
iso_week_counts([]) == []

# 2026-01-01 is a Thursday in ISO week 2026-W01; 2026-01-05 is the Monday of
# ISO week 2026-W02.
iso_week_counts(["2026-01-01", "2026-01-05", "2026-01-05"]) == [
    ("2026-W01", 1),
    ("2026-W02", 2),
]

# Year-boundary: 2021-01-01 is ISO week 2020-W53; 2019-12-30 is ISO week 2020-W01.
iso_week_counts(["2021-01-01", "2019-12-30"]) == [
    ("2020-W01", 1),
    ("2020-W53", 1),
]

# Low years pad to 4 digits, and lexicographic sorting must respect that
# padding: "0999-W24" sorts before "1000-W24".
iso_week_counts(["1000-06-15", "0999-06-15"]) == [
    ("0999-W24", 1),
    ("1000-W24", 1),
]
```
