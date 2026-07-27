from datetime import datetime, timedelta, timezone


def _parse_hhmm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def _parse_utc(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)


def earliest_slot(day, duration_minutes, attendees):
    day_start = _parse_utc(day + "T00:00")

    parsed = []
    for a in attendees:
        offset = timedelta(minutes=a["offset"])
        av_s = _parse_hhmm(a["avail_start"])
        av_e = _parse_hhmm(a["avail_end"])
        busy = [(_parse_utc(b0), _parse_utc(b1)) for b0, b1 in a.get("busy", [])]
        parsed.append((offset, av_s, av_e, busy))

    dur = timedelta(minutes=duration_minutes)

    for minute in range(1440):
        t = day_start + timedelta(minutes=minute)
        t_end = t + dur
        ok = True
        for offset, av_s, av_e, busy in parsed:
            local = t + offset
            sod = local.hour * 60 + local.minute
            eod = sod + duration_minutes
            if not (av_s <= sod and eod <= av_e):
                ok = False
                break
            conflict = False
            for b0, b1 in busy:
                # Bug: treats the busy interval as closed at both ends,
                # so a meeting starting exactly when a busy block ends is
                # wrongly rejected (t == b1 should be allowed).
                if t <= b1 and t_end >= b0:
                    conflict = True
                    break
            if conflict:
                ok = False
                break
        if ok:
            return t.strftime("%Y-%m-%dT%H:%M")
    return None
