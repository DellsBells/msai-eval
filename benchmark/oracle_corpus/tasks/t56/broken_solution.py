def dispatch(num_elevators, calls):
    floor = [0] * num_elevators
    idle = [True] * num_elevators
    target = [None] * num_elevators
    serving = [None] * num_elevators
    distance = [0] * num_elevators

    unassigned = {order: f for (f, order) in calls}
    total_calls = len(calls)

    served_tick = {}
    last_tick = -1

    tick = 0
    served_count = 0

    while served_count < total_calls:
        # Phase A: dispatch.
        while unassigned:
            idle_elevators = [i for i in range(num_elevators) if idle[i]]
            if not idle_elevators:
                break
            chosen_order = min(unassigned)
            call_floor = unassigned[chosen_order]
            best = None
            best_dist = None
            for i in idle_elevators:
                d = abs(floor[i] - call_floor)
                # On ties, keep the later (higher-index) elevator.
                if best is None or d <= best_dist:
                    best = i
                    best_dist = d
            idle[best] = False
            target[best] = call_floor
            serving[best] = chosen_order
            del unassigned[chosen_order]

        # Phase B: movement.
        for i in range(num_elevators):
            if idle[i]:
                continue
            if floor[i] < target[i]:
                floor[i] += 1
                distance[i] += 1
            elif floor[i] > target[i]:
                floor[i] -= 1
                distance[i] += 1
            if floor[i] == target[i]:
                served_tick[serving[i]] = tick
                if tick > last_tick:
                    last_tick = tick
                served_count += 1
                idle[i] = True
                target[i] = None
                serving[i] = None

        tick += 1

    return {
        "served_tick": served_tick,
        "distance": distance,
        "last_tick": last_tick,
    }
