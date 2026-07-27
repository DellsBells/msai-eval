from datetime import date, timedelta


def _first_of_next_month(year: int, month: int) -> date:
    if month == 12:
        return date(year + 1, 1, 1)
    return date(year, month + 1, 1)


def nth_weekday_dates(year: int, weekday: int, n: int) -> list:
    result = []
    for month in range(1, 13):
        if n == -1:
            last = _first_of_next_month(year, month) - timedelta(days=1)
            # Bug: subtraction reversed, so the offset points the wrong way.
            offset = (weekday - last.weekday()) % 7
            result.append((last - timedelta(days=offset)).isoformat())
        else:
            first = date(year, month, 1)
            offset = (weekday - first.weekday()) % 7
            occurrence = first + timedelta(days=offset + 7 * (n - 1))
            if occurrence.month == month:
                result.append(occurrence.isoformat())
    return result
