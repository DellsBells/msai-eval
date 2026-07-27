import solution


def test_single_elevator_one_call():
    result = solution.dispatch(1, [(3, 0)])
    assert result == {"served_tick": {0: 2}, "distance": [3], "last_tick": 2}


def test_two_elevators_two_calls_same_floor():
    result = solution.dispatch(2, [(2, 0), (2, 1)])
    assert result == {
        "served_tick": {0: 1, 1: 1},
        "distance": [2, 2],
        "last_tick": 1,
    }


def test_call_on_starting_floor():
    result = solution.dispatch(1, [(0, 5)])
    assert result == {"served_tick": {5: 0}, "distance": [0], "last_tick": 0}


def test_empty_calls():
    result = solution.dispatch(3, [])
    assert result == {"served_tick": {}, "distance": [0, 0, 0], "last_tick": -1}


def test_tie_break_lowest_index():
    # A single call with two idle elevators equidistant (both at floor 0): the
    # LOWEST-index elevator must be chosen, so elevator 0 moves and elevator 1
    # stays put.
    result = solution.dispatch(2, [(5, 0)])
    assert result["distance"] == [5, 0]
    assert result["served_tick"] == {0: 4}
    assert result["last_tick"] == 4


def test_queued_calls_single_elevator():
    # Lowest order is served first regardless of input list order.
    result = solution.dispatch(1, [(2, 1), (1, 0)])
    assert result == {"served_tick": {0: 0, 1: 1}, "distance": [2], "last_tick": 1}


def test_unsorted_input_order():
    # The call list is not sorted by order; lowest order still goes first.
    result = solution.dispatch(1, [(4, 2), (1, 0), (3, 1)])
    # order 0 (floor 1): 0->1, served tick 0, dist 1
    # order 1 (floor 3): from 1 -> 3, served tick 2 (1->2->3), dist +2
    # order 2 (floor 4): from 3 -> 4, served tick 3, dist +1
    assert result["served_tick"] == {0: 0, 1: 2, 2: 3}
    assert result["distance"] == [4]
    assert result["last_tick"] == 3


def test_closest_idle_elevator_chosen():
    # Two elevators. First call parks elevator 0 near floor 10; a second call on
    # floor 1 should be served by whichever idle elevator is closest.
    result = solution.dispatch(2, [(10, 0), (1, 1)])
    # tick0 A: order0 floor10 -> both at 0, tie -> elevator 0 (target 10).
    #          order1 floor1 -> only elevator 1 idle -> elevator 1 (target 1).
    # elevator 1 reaches floor 1 at tick 0? B: 0->1 arrives tick 0.
    # elevator 0 reaches floor 10 at tick 9.
    assert result["served_tick"] == {0: 9, 1: 0}
    assert result["distance"] == [10, 1]
    assert result["last_tick"] == 9


def test_closest_wins_between_idle_at_different_floors():
    # Two idle elevators sitting on DIFFERENT floors must serve a new call from
    # the one whose current floor is closest (not the lowest index, not the
    # farthest). This is the case that distinguishes "closest" from every other
    # dispatch rule.
    #
    # dispatch(2, [(1,0),(0,1),(0,2)]):
    #   tick0 A: order0 floor1 -> e0,e1 both at 0 (tie) -> e0 (target 1).
    #            order1 floor0 -> only e1 idle -> e1 (target 0).
    #            order2 floor0 -> no idle left, stop.
    #   tick0 B: e0 0->1 arrives (order0 tick0), idle at floor 1.
    #            e1 at 0==target arrives (order1 tick0), idle at floor 0.
    #   tick1 A: order2 floor0 -> idle e0 at floor1 (dist 1) vs e1 at floor0
    #            (dist 0). Closest is e1. e1 assigned (target 0).
    #   tick1 B: e1 at 0==target -> served tick1, moves 0. e0 stays put.
    # A farthest/lowest-index rule would instead pick e0 and move it 1->0,
    # giving distance [2, 0]; the correct closest rule yields [1, 0].
    result = solution.dispatch(2, [(1, 0), (0, 1), (0, 2)])
    assert result == {
        "served_tick": {0: 0, 1: 0, 2: 1},
        "distance": [1, 0],
        "last_tick": 1,
    }


def test_closest_changes_service_time_and_last_tick():
    # A larger queued scenario where choosing the closer idle elevator changes
    # not just distance but the service ticks and last_tick as well. Wrong
    # proximity rules (farthest / always-lowest-index) diverge here.
    result = solution.dispatch(2, [(3, 0), (6, 1), (0, 2), (8, 3), (3, 4)])
    assert result == {
        "served_tick": {0: 2, 2: 5, 1: 5, 3: 7, 4: 8},
        "distance": [9, 8],
        "last_tick": 8,
    }


def test_property_matches_multi_elevator_oracle():
    # Independent full re-implementation of the two-phase dispatch/movement spec,
    # compared against the solution for MULTIPLE elevators over many
    # deterministic call sets. This pins exact served_tick/distance/last_tick
    # values whenever idle elevators sit on different floors, closing the gap
    # that structural-only invariant checks leave open.
    def oracle(num_elevators, calls):
        floor = [0] * num_elevators
        idle = [True] * num_elevators
        target = [None] * num_elevators
        serving = [None] * num_elevators
        distance = [0] * num_elevators
        unassigned = {o: f for (f, o) in calls}
        total = len(calls)
        served_tick = {}
        last_tick = -1
        tick = 0
        served = 0
        while served < total:
            while unassigned:
                idle_e = [i for i in range(num_elevators) if idle[i]]
                if not idle_e:
                    break
                order = min(unassigned)
                cf = unassigned[order]
                # Closest current floor, ties by lowest index.
                best = min(idle_e, key=lambda i: (abs(floor[i] - cf), i))
                idle[best] = False
                target[best] = cf
                serving[best] = order
                del unassigned[order]
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
                    served += 1
                    idle[i] = True
                    target[i] = None
                    serving[i] = None
            tick += 1
        return {
            "served_tick": served_tick,
            "distance": distance,
            "last_tick": last_tick,
        }

    seed = 918273645
    for _ in range(400):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        ne = 2 + (seed % 3)  # 2..4 elevators
        m = seed % 7  # 0..6 calls
        calls = []
        s = seed
        for k in range(m):
            s = (1103515245 * s + 12345) & 0x7FFFFFFF
            fl = s % 9
            calls.append((fl, k))
        # Deterministic reordering so input is not pre-sorted by order.
        calls = sorted(calls, key=lambda c: (c[0] * 37 + c[1] * 11) % 17)
        assert solution.dispatch(ne, calls) == oracle(ne, calls)


def test_property_matches_single_elevator_oracle():
    # For a single elevator the whole simulation is fully determined: calls are
    # served strictly in ascending order value, each requiring abs(delta) ticks
    # of travel. Compare the implementation against this independent oracle over
    # many deterministic call sets.
    seed = 20240704
    for _ in range(200):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        m = seed % 6
        calls = []
        s = seed
        used_orders = []
        for k in range(m):
            s = (1103515245 * s + 12345) & 0x7FFFFFFF
            fl = s % 8
            calls.append((fl, k))  # orders 0..m-1, already distinct
            used_orders.append(k)
        # Shuffle deterministically by sorting on a hash-like key.
        calls_shuffled = sorted(calls, key=lambda c: (c[0] * 31 + c[1] * 7) % 13)
        res = solution.dispatch(1, calls_shuffled)

        # Independent oracle. A call dispatched on tick d that needs `steps`
        # moves arrives on tick d (if steps == 0, zero movement, served
        # immediately) or on tick d + steps - 1 (the assignment tick already
        # includes the first movement step). The next call is dispatched on the
        # tick after arrival.
        pos = 0
        t = 0  # next dispatch tick
        exp_served = {}
        exp_dist = 0
        for order in sorted(used_orders):
            fl = next(f for (f, o) in calls if o == order)
            steps = abs(fl - pos)
            arrival = t if steps == 0 else t + steps - 1
            exp_served[order] = arrival
            exp_dist += steps
            pos = fl
            t = arrival + 1  # next call dispatched on the following tick
        exp_last = max(exp_served.values()) if exp_served else -1

        assert res["served_tick"] == exp_served
        assert res["distance"] == [exp_dist]
        assert res["last_tick"] == exp_last


def test_property_general_invariants():
    # Invariants that hold for any number of elevators:
    #   - every call order appears exactly once in served_tick
    #   - last_tick == max(served_tick.values()) (or -1 if empty)
    #   - all distances are non-negative
    #   - total distance moved equals the sum of served ticks contributed by
    #     travel is not asserted (dispatch-dependent), but each served tick is
    #     >= 0 and <= last_tick.
    seed = 13579
    for _ in range(200):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        ne = 1 + (seed % 4)
        m = seed % 7
        calls = []
        s = seed
        for k in range(m):
            s = (1103515245 * s + 12345) & 0x7FFFFFFF
            fl = s % 10
            calls.append((fl, k))
        res = solution.dispatch(ne, calls)
        st = res["served_tick"]
        assert set(st.keys()) == set(range(m))
        assert len(res["distance"]) == ne
        assert all(d >= 0 for d in res["distance"])
        if m == 0:
            assert res["last_tick"] == -1
            assert st == {}
        else:
            assert res["last_tick"] == max(st.values())
            assert all(0 <= v <= res["last_tick"] for v in st.values())
