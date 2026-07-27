import solution

import random
from datetime import datetime, timedelta, timezone


def test_single_attendee_basic():
    assert solution.earliest_slot("2026-03-02", 60, [
        {"offset": 0, "avail_start": "09:00", "avail_end": "17:00", "busy": []},
    ]) == "2026-03-02T09:00"


def test_busy_pushes_start_to_block_end():
    assert solution.earliest_slot("2026-03-02", 60, [
        {"offset": 0, "avail_start": "09:00", "avail_end": "17:00",
         "busy": [["2026-03-02T09:00", "2026-03-02T09:30"]]},
    ]) == "2026-03-02T09:30"


def test_two_offsets_intersection():
    assert solution.earliest_slot("2026-03-02", 30, [
        {"offset": 0,    "avail_start": "09:00", "avail_end": "17:00", "busy": []},
        {"offset": -300, "avail_start": "09:00", "avail_end": "17:00", "busy": []},
    ]) == "2026-03-02T14:00"


def test_impossible_returns_none():
    assert solution.earliest_slot("2026-03-02", 60, [
        {"offset": 0, "avail_start": "00:00", "avail_end": "00:30", "busy": []},
    ]) is None


def test_meeting_starting_exactly_at_busy_end_is_allowed():
    # busy [10:00,11:00); a 30-min meeting starting 11:00 must be accepted,
    # and it is the earliest given availability begins at 11:00.
    assert solution.earliest_slot("2026-03-02", 30, [
        {"offset": 0, "avail_start": "11:00", "avail_end": "12:00",
         "busy": [["2026-03-02T11:00", "2026-03-02T11:30"]]},
    ]) == "2026-03-02T11:30"


def test_meeting_ending_exactly_at_busy_start_is_allowed():
    # Availability 08:00-12:00. Busy [09:00,10:00). A 60-min meeting at 08:00
    # ends at 09:00 == busy start, half-open so NO conflict -> 08:00 wins.
    assert solution.earliest_slot("2026-03-02", 60, [
        {"offset": 0, "avail_start": "08:00", "avail_end": "12:00",
         "busy": [["2026-03-02T09:00", "2026-03-02T10:00"]]},
    ]) == "2026-03-02T08:00"


def test_positive_offset_window():
    # Attendee at UTC+330 (India). Local 09:00 == 03:30 UTC.
    # avail 09:00-10:00 local, 30-min meeting -> earliest UTC 03:30.
    assert solution.earliest_slot("2026-03-02", 30, [
        {"offset": 330, "avail_start": "09:00", "avail_end": "10:00", "busy": []},
    ]) == "2026-03-02T03:30"


def test_exact_fit_window():
    # Window exactly the meeting length: 09:00-10:00 local, 60 minutes.
    assert solution.earliest_slot("2026-03-02", 60, [
        {"offset": 0, "avail_start": "09:00", "avail_end": "10:00", "busy": []},
    ]) == "2026-03-02T09:00"


def test_window_one_minute_short_is_none():
    assert solution.earliest_slot("2026-03-02", 61, [
        {"offset": 0, "avail_start": "09:00", "avail_end": "10:00", "busy": []},
    ]) is None


def test_multiple_busy_blocks():
    # Availability 09:00-12:00. Busy 09:00-10:00 and 10:00-11:00 back to back.
    # 60-min meeting earliest slot is 11:00.
    assert solution.earliest_slot("2026-03-02", 60, [
        {"offset": 0, "avail_start": "09:00", "avail_end": "12:00",
         "busy": [["2026-03-02T09:00", "2026-03-02T10:00"],
                  ["2026-03-02T10:00", "2026-03-02T11:00"]]},
    ]) == "2026-03-02T11:00"


def test_meeting_may_end_after_utc_midnight():
    # Attendee UTC+0, avail 23:00-23:59? window end must be <= 1440.
    # Use avail 23:00-24:00 (23:59 is minute 1439; end 1440 allowed).
    # 30-min meeting: local sod 23:00 -> eod 23:30 <= 1440 ok, start 23:00 UTC.
    res = solution.earliest_slot("2026-03-02", 30, [
        {"offset": 0, "avail_start": "23:00", "avail_end": "24:00", "busy": []},
    ])
    assert res == "2026-03-02T23:00"


def test_only_valid_local_slot_busy_returns_none_not_next_day():
    # UTC+0, availability 00:00-00:30 local. A 30-min meeting only fits at
    # local sod 0 (eod 30 <= 30). The single valid start on this UTC day,
    # 00:00, is blocked by a busy block. Every other minute of the day fails
    # availability (sod 1..1439 -> eod > 30 > avail_end). The search is bounded
    # to the UTC day [00:00, 24:00), so there is NO valid start -> None.
    # An implementation that also probes next-day 00:00 UTC would wrongly
    # return "2026-03-03T00:00"; that instant is OUTSIDE the search day.
    res = solution.earliest_slot("2026-03-02", 30, [
        {"offset": 0, "avail_start": "00:00", "avail_end": "00:30",
         "busy": [["2026-03-02T00:00", "2026-03-02T00:30"]]},
    ])
    assert res is None


def test_next_day_midnight_is_never_a_candidate():
    # UTC-60. Availability 01:00-01:30 local => valid UTC start only at 00:00
    # (local 23:00 of prev day? no: offset -60 means local = UTC - 60 min).
    # local(t) = t - 60min. For local sod=60 (01:00), eod=90 <= 90 ok, need
    # t such that (t - 60min) has local time 01:00 -> t = 02:00 UTC.
    # Block 02:00 UTC busy; then the only in-window minute on the UTC day is
    # gone. Next-day 00:00 UTC has local 23:00 (prev local day), sod=1380,
    # far outside [60,90) -> even a next-midnight probe fails here, so the
    # correct answer is None regardless. This pins the None result.
    res = solution.earliest_slot("2026-03-02", 30, [
        {"offset": -60, "avail_start": "01:00", "avail_end": "01:30",
         "busy": [["2026-03-02T02:00", "2026-03-02T02:30"]]},
    ])
    assert res is None


def test_last_minute_of_day_valid_but_not_beyond():
    # Availability 23:59-24:00 local (minute 1439 only), 1-min meeting.
    # Only valid start on the UTC day is 23:59 (sod 1439, eod 1440 <= 1440).
    # Confirms the search reaches minute 1439 inclusive but treats 24:00 as
    # the exclusive upper bound of the day.
    assert solution.earliest_slot("2026-03-02", 1, [
        {"offset": 0, "avail_start": "23:59", "avail_end": "24:00", "busy": []},
    ]) == "2026-03-02T23:59"


# ---- Independent brute-force reference for the property test ----

def _parse_utc(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)


def _ref(day, duration_minutes, attendees):
    day_start = _parse_utc(day + "T00:00")
    dur = timedelta(minutes=duration_minutes)
    for minute in range(1440):
        t = day_start + timedelta(minutes=minute)
        t_end = t + dur
        good = True
        for a in attendees:
            local = t + timedelta(minutes=a["offset"])
            sod = local.hour * 60 + local.minute
            eod = sod + duration_minutes
            avs = int(a["avail_start"][:2]) * 60 + int(a["avail_start"][3:])
            ave = int(a["avail_end"][:2]) * 60 + int(a["avail_end"][3:])
            if not (avs <= sod and eod <= ave):
                good = False
                break
            for b0, b1 in a.get("busy", []):
                bb0, bb1 = _parse_utc(b0), _parse_utc(b1)
                if t < bb1 and t_end > bb0:
                    good = False
                    break
            if not good:
                break
        if good:
            return t.strftime("%Y-%m-%dT%H:%M")
    return None


def test_property_matches_bruteforce():
    rng = random.Random(31337)
    day = "2026-03-02"
    day_start = _parse_utc(day + "T00:00")
    for _ in range(150):
        dur = rng.choice([15, 30, 45, 60, 90])
        n = rng.randint(1, 3)
        attendees = []
        for _ in range(n):
            offset = rng.choice([-720, -300, -60, 0, 60, 330, 540, 720])
            s = rng.randint(0, 1400)
            e = min(1440, s + rng.randint(30, 300))
            avail_start = "{:02d}:{:02d}".format(s // 60, s % 60)
            avail_end = "{:02d}:{:02d}".format(e // 60, e % 60)
            busy = []
            for _ in range(rng.randint(0, 3)):
                bstart_min = rng.randint(0, 1439)
                blen = rng.randint(1, 120)
                b0 = day_start + timedelta(minutes=bstart_min)
                b1 = b0 + timedelta(minutes=blen)
                busy.append([b0.strftime("%Y-%m-%dT%H:%M"),
                             b1.strftime("%Y-%m-%dT%H:%M")])
            attendees.append({"offset": offset, "avail_start": avail_start,
                              "avail_end": avail_end, "busy": busy})
        expected = _ref(day, dur, attendees)
        got = solution.earliest_slot(day, dur, attendees)
        assert got == expected, (dur, attendees, got, expected)


def test_property_next_midnight_boundary():
    # Adversarial property test: construct single-attendee cases whose ONLY
    # in-window minute on the UTC day is fully covered by a busy block, so the
    # correct answer is None. An implementation that also evaluates next-day
    # 00:00 UTC (minute 1440) as a candidate can spuriously return a next-day
    # start for a subset of these. We tile offset/duration/window so that the
    # sole valid UTC start on the day equals the next-day-midnight local
    # time-of-day, making minute 1440 a live candidate for a buggy search.
    rng = random.Random(90210)
    day = "2026-03-02"
    day_start = _parse_utc(day + "T00:00")
    checked = 0
    for _ in range(200):
        dur = rng.choice([15, 30, 45, 60])
        offset = rng.choice([-720, -300, -180, -60, 60, 180, 300, 720])
        # We want the only valid UTC start on the day to have local
        # time-of-day == (next-day-midnight local time-of-day). Next-day
        # midnight UTC is minute 1440; its local sod is (1440*0 ... ) i.e.
        # local sod at UTC 00:00 of any day == offset mod 1440.
        base_local = offset % 1440
        # Build a window [base_local, base_local+dur) so a meeting whose local
        # start-of-day is exactly base_local fits (eod = base_local+dur).
        if base_local + dur > 1440:
            continue  # window would cross local midnight; skip
        avail_start = "{:02d}:{:02d}".format(base_local // 60, base_local % 60)
        e = base_local + dur
        avail_end = "{:02d}:{:02d}".format(e // 60, e % 60)
        # The UTC start whose local sod == base_local on THIS UTC day:
        # local(t) = t + offset; we need (t+offset) sod == base_local, and the
        # UTC-00:00 instant has local sod base_local already, so t at UTC
        # minute m has local sod (base_local + m) mod 1440. Setting that to
        # base_local means m == 0 (mod 1440) -> only m == 0 on the day.
        valid_utc_min = 0
        b0 = day_start + timedelta(minutes=valid_utc_min)
        b1 = b0 + timedelta(minutes=dur)
        busy = [[b0.strftime("%Y-%m-%dT%H:%M"), b1.strftime("%Y-%m-%dT%H:%M")]]
        attendees = [{"offset": offset, "avail_start": avail_start,
                      "avail_end": avail_end, "busy": busy}]
        expected = _ref(day, dur, attendees)
        got = solution.earliest_slot(day, dur, attendees)
        assert got == expected, (dur, offset, attendees, got, expected)
        if expected is None:
            checked += 1
    # Ensure we actually exercised the None-on-day scenario a meaningful
    # number of times (guards against the generator silently degenerating).
    assert checked >= 20
