import solution

import random
from datetime import date, timedelta


def test_full_work_week():
    assert solution.working_days("2026-01-05", "2026-01-09", []) == 5


def test_holiday_in_range():
    assert solution.working_days("2026-01-05", "2026-01-09", ["2026-01-07"]) == 4


def test_weekend_span():
    # Fri .. Mon: Fri and Mon count, Sat/Sun do not.
    assert solution.working_days("2026-01-02", "2026-01-05", []) == 2


def test_single_weekday():
    assert solution.working_days("2026-01-06", "2026-01-06", []) == 1


def test_single_weekend_day():
    # 2026-01-03 is a Saturday.
    assert solution.working_days("2026-01-03", "2026-01-03", []) == 0


def test_single_day_that_is_holiday():
    assert solution.working_days("2026-01-06", "2026-01-06", ["2026-01-06"]) == 0


def test_start_after_end_is_zero():
    assert solution.working_days("2026-01-10", "2026-01-05", []) == 0


def test_empty_holidays_default():
    # Two full weeks Mon..Fri twice = 10 working days.
    assert solution.working_days("2026-01-05", "2026-01-16", []) == 10


def test_irrelevant_holidays_ignored():
    # Holidays on a weekend and outside the range must not change the count.
    hol = ["2026-01-03", "2026-01-04", "2025-12-25", "2026-02-01"]
    assert solution.working_days("2026-01-05", "2026-01-09", hol) == 5


def test_duplicate_holidays_counted_once():
    hol = ["2026-01-07", "2026-01-07", "2026-01-07"]
    assert solution.working_days("2026-01-05", "2026-01-09", hol) == 4


def test_holiday_on_weekend_no_effect():
    # A holiday landing on a Saturday within range removes nothing extra.
    # 2026-01-10 is a Saturday.
    assert solution.working_days("2026-01-05", "2026-01-11", ["2026-01-10"]) == 5


def _brute_force(start_d, end_d, holiday_set):
    if start_d > end_d:
        return 0
    c = 0
    cur = start_d
    while cur <= end_d:
        if cur.weekday() < 5 and cur not in holiday_set:
            c += 1
        cur += timedelta(days=1)
    return c


def test_property_matches_bruteforce():
    rng = random.Random(4242)
    base = date(2026, 1, 1)
    for _ in range(200):
        a = base + timedelta(days=rng.randint(0, 400))
        b = base + timedelta(days=rng.randint(0, 400))
        # Build a random holiday set inside a plausible window.
        hset = {base + timedelta(days=rng.randint(0, 400)) for _ in range(rng.randint(0, 5))}
        hlist = [d.isoformat() for d in hset]
        expected = _brute_force(a, b, hset)
        got = solution.working_days(a.isoformat(), b.isoformat(), hlist)
        assert got == expected, (a, b, hlist, got, expected)
