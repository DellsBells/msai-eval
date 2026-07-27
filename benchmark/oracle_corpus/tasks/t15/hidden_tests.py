import solution

import random
from datetime import date, timedelta


def test_empty():
    assert solution.iso_week_counts([]) == []


def test_basic_two_weeks_with_duplicate():
    assert solution.iso_week_counts(["2026-01-01", "2026-01-05", "2026-01-05"]) == [
        ("2026-W01", 1),
        ("2026-W02", 2),
    ]


def test_year_boundary_iso_year():
    assert solution.iso_week_counts(["2021-01-01", "2019-12-30"]) == [
        ("2020-W01", 1),
        ("2020-W53", 1),
    ]


def test_single_date():
    assert solution.iso_week_counts(["2026-06-15"]) == [("2026-W25", 1)]


def test_all_same_date():
    res = solution.iso_week_counts(["2026-03-10"] * 5)
    assert res == [("2026-W11", 5)]


def test_sorted_lexicographically():
    ds = ["2026-12-31", "2026-01-05", "2026-06-15"]
    res = solution.iso_week_counts(ds)
    keys = [k for k, _ in res]
    assert keys == sorted(keys)


def test_zero_padding_week():
    # Week 1 must render as W01, not W1.
    res = solution.iso_week_counts(["2026-01-01"])
    assert res == [("2026-W01", 1)]


def test_late_december_belongs_to_next_iso_year():
    # 2020-12-31 is ISO 2020-W53; but e.g. 2018-12-31 is ISO 2019-W01.
    res = solution.iso_week_counts(["2018-12-31"])
    assert res == [("2019-W01", 1)]


def test_counts_sum_to_input_length():
    ds = ["2026-01-01", "2026-01-01", "2021-01-01", "2019-12-30", "2026-06-15"]
    res = solution.iso_week_counts(ds)
    assert sum(c for _, c in res) == len(ds)


def test_week53_year():
    # 2020-12-31 -> ISO 2020-W53.
    res = solution.iso_week_counts(["2020-12-31"])
    assert res == [("2020-W53", 1)]


def test_three_digit_iso_year_is_zero_padded():
    # ISO year 999 must render as a 4-digit, left-zero-padded "0999", not "999".
    res = solution.iso_week_counts(["0999-06-15"])
    assert res == [("0999-W24", 1)]


def test_single_digit_iso_year_is_zero_padded():
    # ISO year 7 -> "0007". (0007-12-31 falls in ISO year 8, week 1.)
    res = solution.iso_week_counts(["0007-12-31"])
    assert res == [("0008-W01", 1)]


def test_low_year_lexicographic_sort():
    # The 4-digit zero-padding is what makes lexicographic sort chronological.
    # "0999-W24" must sort before "1000-W24"; a 3-digit "999-W24" would sort
    # AFTER "1000-W24" and produce the wrong order.
    res = solution.iso_week_counts(["1000-06-15", "0999-06-15"])
    assert res == [("0999-W24", 1), ("1000-W24", 1)]


def test_low_year_iso_boundary_and_padding():
    # 0100-01-01 belongs to the previous ISO year's last week: "0099-W53".
    res = solution.iso_week_counts(["0100-01-01"])
    assert res == [("0099-W53", 1)]


def test_all_keys_are_eight_chars_including_low_years():
    ds = ["0001-01-04", "0050-03-10", "0999-06-15", "1000-06-15", "2026-06-15"]
    res = solution.iso_week_counts(ds)
    for key, _ in res:
        assert len(key) == 8, "key must be exactly 8 chars: %r" % (key,)
        assert key[4:6] == "-W"
        assert key[:4].isdigit()


def test_property_random_matches_reference():
    # Span the whole supported range, including ISO years below 1000, so that
    # zero-padding and padding-dependent lexicographic ordering are exercised.
    rng = random.Random(7)
    base = date(1, 1, 1)
    max_offset = (date(9999, 12, 31) - base).days
    for _ in range(80):
        n = rng.randint(0, 30)
        picks = [base + timedelta(days=rng.randint(0, max_offset)) for _ in range(n)]
        ds = [p.isoformat() for p in picks]

        # Independent reference computation.
        expected = {}
        for p in picks:
            ic = p.isocalendar()
            key = "{:04d}-W{:02d}".format(ic[0], ic[1])
            expected[key] = expected.get(key, 0) + 1
        expected_sorted = sorted(expected.items(), key=lambda kv: kv[0])

        assert solution.iso_week_counts(ds) == expected_sorted


def test_property_low_years_matches_reference():
    # Concentrate entirely on ISO years < 1000 to force the 3-digit/4-digit
    # distinction and check the ordering across a 999/1000 seam.
    rng = random.Random(1234)
    base = date(1, 1, 1)
    # ~ up to year ~1200 so the 999 <-> 1000 boundary is crossed often.
    max_offset = (date(1200, 12, 31) - base).days
    for _ in range(80):
        n = rng.randint(0, 25)
        picks = [base + timedelta(days=rng.randint(0, max_offset)) for _ in range(n)]
        ds = [p.isoformat() for p in picks]

        expected = {}
        for p in picks:
            ic = p.isocalendar()
            key = "{:04d}-W{:02d}".format(ic[0], ic[1])
            expected[key] = expected.get(key, 0) + 1
        expected_sorted = sorted(expected.items(), key=lambda kv: kv[0])

        result = solution.iso_week_counts(ds)
        assert result == expected_sorted
        # Result must be sorted ascending by key.
        keys = [k for k, _ in result]
        assert keys == sorted(keys)


def test_property_total_and_key_format():
    rng = random.Random(2024)
    base = date(1, 1, 1)
    max_offset = (date(9999, 12, 31) - base).days
    for _ in range(60):
        n = rng.randint(1, 20)
        ds = [(base + timedelta(days=rng.randint(0, max_offset))).isoformat() for _ in range(n)]
        res = solution.iso_week_counts(ds)
        assert sum(c for _, c in res) == n
        for key, _ in res:
            # Key is always exactly 8 chars: 4-digit year, "-W", 2-digit week.
            assert len(key) == 8 and key[4:6] == "-W"
            assert key[:4].isdigit()
            assert key[6:].isdigit()
