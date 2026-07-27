# Elevator Bank Dispatch

You are simulating a bank of elevators serving a list of pickup calls. Time
advances in discrete **ticks**. Each elevator moves at most one floor per tick.
The dispatch and movement rules below are exact and deterministic — implement
them precisely.

## Function to implement

```python
def dispatch(num_elevators, calls):
    ...
```

### Parameters

- `num_elevators` (int): number of elevators, `>= 1`. Elevators are indexed
  `0 .. num_elevators - 1`. **Every elevator starts on floor 0 and is idle.**
- `calls` (list of tuples): each call is `(floor, order)` where `floor` is a
  non-negative int (the floor a passenger is waiting on) and `order` is a unique
  non-negative int used only to break ties (think of it as a request id — lower
  `order` means the request came in "first"). All `order` values are distinct.
  The list may be given in any order; do not assume it is sorted.

Each call means: some elevator must travel to `floor` and stop there. A call is
**served** at the tick when an assigned elevator arrives on its `floor`.

### State and simulation

Each elevator has:
- a current floor (starts at 0),
- a status: `idle` (no assignment) or `busy` (moving toward an assigned call's
  floor),
- when busy, the target floor it is heading to.

The simulation runs in ticks starting at tick `0`. Each tick has two phases, in
this exact order:

**Phase A — dispatch (assign idle elevators to waiting calls).**
Repeat the following until no more assignments can be made this tick:
- Consider the set of currently **unassigned** calls (calls not yet assigned to
  any elevator) and the set of currently **idle** elevators.
- If either set is empty, stop dispatching.
- Choose the unassigned call with the **lowest `order`** value. Among the idle
  elevators, assign it to the one whose current floor is **closest** to the
  call's `floor` (smallest `abs(elevator_floor - call_floor)`); break ties by
  **lowest elevator index**. That elevator becomes `busy` with this call's floor
  as its target. Mark the call assigned.
- An elevator that is already on the exact target floor at the moment of
  assignment still counts as busy for this tick and will "arrive" (serve the
  call) during Phase B of this same tick (it moves zero floors and serves
  immediately).

**Phase B — movement (advance every busy elevator one step toward its target).**
For each busy elevator, in ascending index order:
- If its current floor is below its target, increase its floor by 1.
- If its current floor is above its target, decrease its floor by 1.
- If its current floor already equals its target (either it just got assigned on
  its floor, or it moved and this is the arrival step), the call it was serving
  is now **served at this tick**; the elevator becomes `idle` again (available
  for dispatch on the *next* tick).

Record, for each call, the tick number at which it was served.

The simulation ends after the tick in which the last remaining call is served.

### Return value

Return a dictionary with exactly these keys:

- `"served_tick"`: a dict mapping each call's `order` value to the integer tick
  at which that call was served.
- `"distance"`: a list of length `num_elevators`; `distance[i]` is the total
  number of floors elevator `i` moved over the whole simulation (each one-floor
  step counts as 1; arriving on the same floor you were assigned adds 0).
- `"last_tick"`: the tick number at which the final call was served (int). If
  `calls` is empty this is `-1`.

### Worked example

```python
dispatch(1, [(3, 0)])
# One elevator at floor 0. tick 0: assign call order 0 (floor 3) to elevator 0.
#   Phase B: elevator moves 0 -> 1. Not arrived.
# tick 1: elevator busy, moves 1 -> 2.
# tick 2: moves 2 -> 3, arrives -> served at tick 2, elevator idle.
# => {"served_tick": {0: 2}, "distance": [3], "last_tick": 2}

dispatch(2, [(2, 0), (2, 1)])
# Two elevators at floor 0.
# tick 0 Phase A: unassigned {0,1}. Pick lowest order 0 (floor 2). Idle
#   elevators 0 and 1 both at floor 0, distance 2 each -> tie -> elevator 0.
#   Now pick order 1 (floor 2). Idle elevator left is 1 -> assign to elevator 1.
#   Phase B: elevator 0: 0->1, elevator 1: 0->1.
# tick 1 Phase B: elevator 0: 1->2 arrives (order 0 served tick 1);
#   elevator 1: 1->2 arrives (order 1 served tick 1).
# => {"served_tick": {0: 1, 1: 1}, "distance": [2, 2], "last_tick": 1}

dispatch(1, [(0, 5)])
# Call is on floor 0, elevator already there. tick 0 Phase A: assign to
#   elevator 0 (target 0). Phase B: floor already equals target -> served at
#   tick 0, distance 0.
# => {"served_tick": {5: 0}, "distance": [0], "last_tick": 0}
```

## Constraints

- `num_elevators >= 1`. `calls` may be empty.
- All `order` values across `calls` are distinct non-negative ints; `floor`
  values are non-negative ints (not necessarily distinct).
- The process always terminates (every call is eventually served).
- Do not use any randomness, I/O, or external libraries.
