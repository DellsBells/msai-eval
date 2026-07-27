# Earliest Common Meeting Slot Across Fixed UTC Offsets

Implement a single function using only Python's standard library. You will work
with `datetime`, `timezone`, and `timedelta` (all from the `datetime` module).

```python
def earliest_slot(day, duration_minutes, attendees):
    ...
```

## Problem

You are scheduling one meeting on a single UTC calendar day. Every attendee lives
in a fixed UTC offset (no daylight-saving transitions ever apply — offsets are
constant) and has a daily *availability window* expressed in their **local** wall
clock, plus a list of already-booked *busy* intervals expressed in **UTC**.

Find the **earliest** start instant (in UTC) at which a meeting of
`duration_minutes` can be held so that, for the entire meeting `[start, start +
duration)`:

- every attendee's meeting time lies **within** that attendee's local
  availability window, and
- the meeting does not overlap **any** attendee's busy interval.

### Inputs

- `day` is a string `"YYYY-MM-DD"`: the UTC calendar day to search. The search
  space for the meeting start ranges over that UTC day; the meeting may end after
  midnight UTC (i.e. `start` is on `day` but `start + duration` may spill into the
  next UTC day — that is allowed).
- `duration_minutes` is a positive integer.
- `attendees` is a list of dicts, each with:
  - `"offset"`: integer, the attendee's fixed UTC offset in **minutes**
    (e.g. `-300` for UTC-5, `330` for UTC+5:30). Range: `-720..720`.
  - `"avail_start"` and `"avail_end"`: strings `"HH:MM"` giving that attendee's
    local availability window, on **their** local calendar day that the meeting
    overlaps. The window is `[avail_start, avail_end)` in local wall-clock minutes
    from local midnight, with `0 <= avail_start < avail_end <= 1440`. A meeting
    minute is inside the window if, converted to that attendee's local time, its
    local minute-of-day is `>= avail_start` and the meeting-end local minute-of-day
    is `<= avail_end`. Treat availability as a window that recurs each local day,
    so a meeting instant is "in the window" whenever its local time-of-day falls in
    `[avail_start, avail_end)` and the full meeting fits before `avail_end` on the
    same local day.
  - `"busy"`: a list of `[start_iso, end_iso]` pairs, each an ISO 8601 UTC
    timestamp `"YYYY-MM-DDTHH:MM"` (minute resolution, UTC). Each pair is a
    half-open busy interval `[start, end)`. The list may be empty.

### Search granularity

Candidate start times are aligned to **whole minutes**. Search every minute-aligned
start instant `t` with `day 00:00 UTC <= t < (day+1) 00:00 UTC` (i.e. the 1440
minute-marks of the UTC day), in increasing order, and return the first `t` that
satisfies all constraints for all attendees.

### Return value

Return the earliest valid start time as an ISO 8601 UTC string
`"YYYY-MM-DDTHH:MM"` (no seconds, no timezone suffix; note the start is always on
`day`). If no minute-aligned start on the UTC day works, return `None`.

## Availability semantics (precise)

For a candidate UTC start `t` and an attendee with offset `o` minutes:

1. Compute the attendee's local start `L = t + o` and local end `L + duration`.
2. Let `sod = local minute-of-day of L` (i.e. minutes since that local day's
   midnight, `0..1439`), and `eod = sod + duration_minutes`.
3. The meeting is inside the window iff `avail_start <= sod` **and**
   `eod <= avail_end`. (Because `eod <= avail_end <= 1440`, the meeting cannot
   cross the attendee's local midnight when valid.)

A meeting conflicts with a busy interval `[b0, b1)` iff `t < b1` and
`t + duration > b0` (standard half-open overlap).

## Constraints

- Use only the standard library. Do not read the system clock, files, network,
  or environment. Output depends solely on the arguments.
- `attendees` is non-empty. Durations and offsets are within the ranges above.
- All timestamps use minute resolution.

## Examples

```python
# One attendee at UTC+0, available 09:00-17:00 local, no busy blocks.
# 60-minute meeting: earliest start is 09:00 UTC.
earliest_slot("2026-03-02", 60, [
    {"offset": 0, "avail_start": "09:00", "avail_end": "17:00", "busy": []},
]) == "2026-03-02T09:00"

# Same attendee but busy 09:00-09:30 UTC pushes the earliest 60-min slot to 09:30.
earliest_slot("2026-03-02", 60, [
    {"offset": 0, "avail_start": "09:00", "avail_end": "17:00",
     "busy": [["2026-03-02T09:00", "2026-03-02T09:30"]]},
]) == "2026-03-02T09:30"

# Two attendees: A at UTC+0 avail 09:00-17:00, B at UTC-5 avail 09:00-17:00 local.
# B's 09:00 local == 14:00 UTC, so the overlap of both windows in UTC starts at
# 14:00 UTC (A allows from 09:00 UTC; B allows from 14:00 UTC). Earliest 30-min
# slot: 14:00 UTC.
earliest_slot("2026-03-02", 30, [
    {"offset": 0,    "avail_start": "09:00", "avail_end": "17:00", "busy": []},
    {"offset": -300, "avail_start": "09:00", "avail_end": "17:00", "busy": []},
]) == "2026-03-02T14:00"

# Impossible: attendee available only 00:00-00:30 local but wants a 60-min meeting.
earliest_slot("2026-03-02", 60, [
    {"offset": 0, "avail_start": "00:00", "avail_end": "00:30", "busy": []},
]) is None
```
