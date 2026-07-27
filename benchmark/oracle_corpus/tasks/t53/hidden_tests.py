import solution


def test_basic_trip():
    result = solution.simulate_elevator(1, [3, 1, 5], 1, 10)
    assert result == {"final_floor": 5, "distance": 8, "stops": 3}


def test_noop_and_out_of_range():
    result = solution.simulate_elevator(4, [4, 20, 2], 1, 10)
    assert result == {"final_floor": 2, "distance": 2, "stops": 2}


def test_empty_requests():
    result = solution.simulate_elevator(5, [], 1, 10)
    assert result == {"final_floor": 5, "distance": 0, "stops": 0}


def test_noop_counts_as_stop():
    # A single request equal to the current floor: no movement, one stop.
    result = solution.simulate_elevator(7, [7], 1, 10)
    assert result == {"final_floor": 7, "distance": 0, "stops": 1}


def test_all_out_of_range():
    result = solution.simulate_elevator(3, [0, 11, -5, 99], 1, 10)
    assert result == {"final_floor": 3, "distance": 0, "stops": 0}


def test_below_min_ignored():
    # Boundary just below min_floor is ignored; min_floor itself is valid.
    result = solution.simulate_elevator(5, [0, 1], 1, 10)
    assert result == {"final_floor": 1, "distance": 4, "stops": 1}


def test_negative_floors():
    # Basement floors: min can be negative.
    result = solution.simulate_elevator(-2, [3, -3, 0], -5, 5)
    # -2 -> 3 (dist 5), 3 -> -3 (dist 6), -3 -> 0 (dist 3)
    assert result == {"final_floor": 0, "distance": 14, "stops": 3}


def test_boundary_floors_valid():
    # Exactly min_floor and max_floor are valid requests.
    result = solution.simulate_elevator(5, [1, 10], 1, 10)
    assert result == {"final_floor": 10, "distance": 4 + 9, "stops": 2}


def test_repeated_noops():
    # Repeated requests to the same floor each count as a stop, zero distance.
    result = solution.simulate_elevator(4, [4, 4, 4], 1, 10)
    assert result == {"final_floor": 4, "distance": 0, "stops": 3}


def test_property_stops_never_exceed_requests():
    # Property: over many generated sequences, stops <= len(requests), distance
    # >= 0, and final_floor stays within [min_floor, max_floor] whenever at least
    # one valid request was serviced (otherwise equals start_floor).
    seed = 12345
    for _ in range(300):
        # Simple deterministic LCG; no random module used.
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        n = seed % 8
        reqs = []
        s = seed
        for _ in range(n):
            s = (1103515245 * s + 12345) & 0x7FFFFFFF
            # Values spanning outside [0, 12] to exercise range filtering.
            reqs.append((s % 20) - 3)
        start = (seed % 11)
        res = solution.simulate_elevator(start, reqs, 0, 12)
        assert res["stops"] <= len(reqs)
        assert res["distance"] >= 0
        assert res["stops"] >= 0
        valid_count = sum(1 for r in reqs if 0 <= r <= 12)
        assert res["stops"] == valid_count
        if valid_count == 0:
            assert res["final_floor"] == start
        else:
            assert 0 <= res["final_floor"] <= 12
