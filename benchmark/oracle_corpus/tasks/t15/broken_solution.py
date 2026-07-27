from datetime import date


def iso_week_counts(dates: list) -> list:
    counts = {}
    for s in dates:
        d = date.fromisoformat(s)
        iso = d.isocalendar()
        # Bug: uses the calendar year (d.year) instead of the ISO year (iso[0]).
        key = "%04d-W%02d" % (d.year, iso[1])
        counts[key] = counts.get(key, 0) + 1
    return sorted(counts.items(), key=lambda kv: kv[0])
