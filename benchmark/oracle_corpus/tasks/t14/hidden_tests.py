import solution

import random
from datetime import date, timedelta


def test_first_monday_2026():
    assert solution.nth_weekday_dates(2026, 0, 1) == [
        "2026-01-05", "2026-02-02", "2026-03-02", "2026-04-06",
        "2026-05-04", "2026-06-01", "2026-07-06", "2026-08-03",
        "2026-09-07", "2026-10-05", "2026-11-02", "2026-12-07",
    ]


def test_last_friday_2026():
    assert solution.nth_weekday_dates(2026, 4, -1) == [
        "2026-01-30", "2026-02-27", "2026-03-27", "2026-04-24",
        "2026-05-29", "2026-06-26", "2026-07-31", "2026-08-28",
        "2026-09-25", "2026-10-30", "2026-11-27", "2026-12-25",
    ]


def test_last_always_twelve():
    for wd in range(7):
        assert len(solution.nth_weekday_dates(2026, wd, -1)) == 12


def test_fourth_sunday_all_present():
    res = solution.nth_weekday_dates(2026, 6, 4)
    assert len(res) == 12


def test_fifth_positive_not_requested_but_fourth_boundary():
    # n=4 for a weekday that only occurs 4 times some months still yields those months.
    res = solution.nth_weekday_dates(2026, 0, 4)
    # Every month has at least 4 Mondays, so all 12 present.
    assert len(res) == 12


def test_chronological_order():
    res = solution.nth_weekday_dates(2026, 2, 1)  # first Wednesday
    parsed = [date.fromisoformat(s) for s in res]
    assert parsed == sorted(parsed)


def test_february_non_leap_last_weekday():
    # 2025 is not a leap year; Feb has 28 days. Last Saturday (weekday 5).
    res = solution.nth_weekday_dates(2025, 5, -1)
    # Index 1 is February.
    assert res[1] == "2025-02-22"


def test_february_leap_year():
    # 2024 is a leap year; Feb has 29 days. Last Thursday (weekday 3).
    res = solution.nth_weekday_dates(2024, 3, -1)
    assert res[1] == "2024-02-29"


def test_first_occurrence_is_within_first_seven_days():
    for wd in range(7):
        res = solution.nth_weekday_dates(2026, wd, 1)
        for s in res:
            assert date.fromisoformat(s).day <= 7


def test_last_occurrence_within_last_seven_days():
    for wd in range(7):
        res = solution.nth_weekday_dates(2026, wd, -1)
        for s in res:
            d = date.fromisoformat(s)
            # A "last" occurrence must be within the final 7 days of its month.
            nxt = (date(d.year + 1, 1, 1) if d.month == 12
                   else date(d.year, d.month + 1, 1))
            last_day = (nxt - timedelta(days=1)).day
            assert d.day > last_day - 7


def _brute_first(year, month, weekday):
    d = date(year, month, 1)
    while d.weekday() != weekday:
        d += timedelta(days=1)
    return d


def _brute_last(year, month, weekday):
    nxt = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    d = nxt - timedelta(days=1)
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d


def test_property_matches_bruteforce():
    rng = random.Random(99)
    for _ in range(120):
        year = rng.randint(1900, 2100)
        wd = rng.randint(0, 6)
        n = rng.choice([1, 2, 3, 4, -1])
        got = solution.nth_weekday_dates(year, wd, n)
        expected = []
        for month in range(1, 13):
            if n == -1:
                expected.append(_brute_last(year, month, wd).isoformat())
            else:
                first = _brute_first(year, month, wd)
                cand = first + timedelta(days=7 * (n - 1))
                if cand.month == month:
                    expected.append(cand.isoformat())
        assert got == expected, (year, wd, n, got, expected)
