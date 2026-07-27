# Single Elevator Trip Log

You are simulating a single elevator in a building. The elevator starts at a
given floor and must service a list of floor requests **in the order given**.
Write a function that replays the trip and reports what happened.

## Function to implement

```python
def simulate_elevator(start_floor, requests, min_floor, max_floor):
    ...
```

### Parameters

- `start_floor` (int): the floor the elevator begins on.
- `requests` (list of int): floors to visit, serviced strictly in order.
- `min_floor` (int): the lowest valid floor in the building.
- `max_floor` (int): the highest valid floor in the building.

You may assume `min_floor <= max_floor` and `min_floor <= start_floor <= max_floor`.

### Behavior

The elevator processes each request one at a time, from the current floor to the
requested floor:

1. **Out-of-range requests are ignored.** If a requested floor is less than
   `min_floor` or greater than `max_floor`, skip it entirely — the elevator does
   not move for that request and it does not count as a stop.
2. **No-op requests still count as a stop.** If a valid request equals the floor
   the elevator is currently on, the elevator does not move (adds 0 to distance)
   but it *does* count as a stop (the doors open).
3. Moving from floor `a` to floor `b` adds `abs(b - a)` to the total distance
   traveled.
4. After servicing a valid request, the current floor becomes that requested
   floor.

Return a dictionary with exactly these keys:

- `"final_floor"`: the floor the elevator ends on (int).
- `"distance"`: the total distance traveled across all valid requests (int).
- `"stops"`: the number of valid requests that were serviced (int). Out-of-range
  requests do not count; no-op requests do count.

If `requests` is empty, the elevator never moves: `final_floor` equals
`start_floor`, `distance` is `0`, and `stops` is `0`.

## Examples

```python
simulate_elevator(1, [3, 1, 5], 1, 10)
# floor 1 -> 3 (dist 2), 3 -> 1 (dist 2), 1 -> 5 (dist 4)
# => {"final_floor": 5, "distance": 8, "stops": 3}

simulate_elevator(4, [4, 20, 2], 1, 10)
# request 4: no-op (dist 0, counts as stop); request 20: out of range (ignored);
# request 2: 4 -> 2 (dist 2)
# => {"final_floor": 2, "distance": 2, "stops": 2}

simulate_elevator(5, [], 1, 10)
# => {"final_floor": 5, "distance": 0, "stops": 0}
```

## Constraints

- All floor values are integers (possibly negative, e.g. basement floors).
- Do not use any randomness, I/O, or external libraries.
