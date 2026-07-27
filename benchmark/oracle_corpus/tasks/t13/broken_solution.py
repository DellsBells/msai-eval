from datetime import date, timedelta


def _parse(s: str) -> date:
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))


def working_days(start: str, end: str, holidays: list) -> int:
    start_d = _parse(start)
    end_d = _parse(end)
    if start_d > end_d:
        return 0

    holiday_set = {_parse(h) for h in holidays}

    count = 0
    cur = start_d
    one = timedelta(days=1)
    # Off-by-one: treats the range as exclusive of the end date.
    while cur < end_d:
        if cur.weekday() < 5 and cur not in holiday_set:
            count += 1
        cur += one
    return count
