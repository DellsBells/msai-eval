import solution


def test_example_one():
    result = solution.run_bin(
        10, [("restock", 8), ("ship", 3), ("restock", 8), ("ship", 20)]
    )
    assert result == {
        "on_hand": 0,
        "wasted": 3,
        "backordered": 10,
        "filled_orders": 1,
        "backordered_orders": 1,
    }


def test_example_two():
    result = solution.run_bin(5, [("ship", 2), ("restock", 10)])
    assert result == {
        "on_hand": 5,
        "wasted": 5,
        "backordered": 2,
        "filled_orders": 0,
        "backordered_orders": 1,
    }


def test_zero_amount_events():
    result = solution.run_bin(4, [("ship", 0), ("restock", 0)])
    assert result == {
        "on_hand": 0,
        "wasted": 0,
        "backordered": 0,
        "filled_orders": 1,
        "backordered_orders": 0,
    }


def test_empty_events():
    result = solution.run_bin(100, [])
    assert result == {
        "on_hand": 0,
        "wasted": 0,
        "backordered": 0,
        "filled_orders": 0,
        "backordered_orders": 0,
    }


def test_exact_match_ship_is_filled():
    # Shipping exactly what is on hand fully fills the order, leaves bin empty.
    result = solution.run_bin(10, [("restock", 5), ("ship", 5)])
    assert result["on_hand"] == 0
    assert result["filled_orders"] == 1
    assert result["backordered_orders"] == 0
    assert result["backordered"] == 0


def test_ship_zero_when_empty_is_filled():
    # ("ship", 0) with an empty bin is fully filled, not a backorder.
    result = solution.run_bin(10, [("ship", 0)])
    assert result["filled_orders"] == 1
    assert result["backordered_orders"] == 0
    assert result["backordered"] == 0


def test_overflow_discards_excess():
    # Restocking beyond capacity discards the excess and never exceeds capacity.
    result = solution.run_bin(3, [("restock", 3), ("restock", 3)])
    assert result["on_hand"] == 3
    assert result["wasted"] == 3


def test_partial_ship_is_backorder():
    # A ship that ships some units but not all is a backordered order.
    result = solution.run_bin(10, [("restock", 4), ("ship", 7)])
    assert result["on_hand"] == 0
    assert result["backordered"] == 3
    assert result["filled_orders"] == 0
    assert result["backordered_orders"] == 1


def test_zero_capacity_bin():
    # Capacity 0: every restock is fully wasted, nothing can ship.
    result = solution.run_bin(0, [("restock", 5), ("ship", 2)])
    assert result["on_hand"] == 0
    assert result["wasted"] == 5
    assert result["backordered"] == 2
    assert result["filled_orders"] == 0
    assert result["backordered_orders"] == 1


def test_wasted_accumulates_across_overflows():
    # Two separate overflowing restocks with DIFFERING overflow amounts.
    # restock 5 -> q=3, overflow 2 (wasted 2)
    # restock 5 -> q=3, overflow 5 (wasted 5), running total 7
    # ship 3    -> q=0, filled
    # restock 5 -> q=3, overflow 2 (wasted 2), running total 9
    result = solution.run_bin(
        3, [("restock", 5), ("restock", 5), ("ship", 3), ("restock", 5)]
    )
    assert result["on_hand"] == 3
    assert result["wasted"] == 9
    assert result["filled_orders"] == 1
    assert result["backordered_orders"] == 0


def test_backordered_accumulates_across_ships():
    # Two separate backordering ships with DIFFERING shortfalls, bin empty.
    # ship 4 with q=0 -> shortfall 4 (backordered 4)
    # ship 6 with q=0 -> shortfall 6 (backordered 6), running total 10
    result = solution.run_bin(10, [("ship", 4), ("ship", 6)])
    assert result["on_hand"] == 0
    assert result["backordered"] == 10
    assert result["filled_orders"] == 0
    assert result["backordered_orders"] == 2


def test_mixed_multiple_overflows_and_backorders():
    # Interleaved overflows and backorders, each with differing amounts,
    # verifying both running totals accumulate independently.
    # restock 10 -> q=4, overflow 6 (wasted 6)
    # ship 7     -> ships 4, q=0, shortfall 3 (backordered 3), backorder order
    # restock 6  -> q=4, overflow 2 (wasted 8 total)
    # ship 1     -> q=3, filled
    # ship 9     -> ships 3, q=0, shortfall 6 (backordered 9 total), backorder
    result = solution.run_bin(
        4,
        [
            ("restock", 10),
            ("ship", 7),
            ("restock", 6),
            ("ship", 1),
            ("ship", 9),
        ],
    )
    assert result["on_hand"] == 0
    assert result["wasted"] == 8
    assert result["backordered"] == 9
    assert result["filled_orders"] == 1
    assert result["backordered_orders"] == 2


def test_orders_partition():
    # Property test over many deterministic event streams. An independent
    # re-simulation computes the exact expected running totals so that
    # accumulate-vs-overwrite defects (and off-by-one tie-breaks) are caught,
    # not merely non-negativity/partition invariants.
    seed = 999
    for _ in range(300):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        cap = seed % 7
        n = seed % 10
        events = []
        s = seed
        for _ in range(n):
            s = (1103515245 * s + 12345) & 0x7FFFFFFF
            kind = "restock" if (s & 1) == 0 else "ship"
            amount = (s >> 3) % 9
            events.append((kind, amount))

        # Reference re-simulation.
        q = 0
        exp_wasted = 0
        exp_backordered = 0
        exp_filled = 0
        exp_backorders = 0
        for kind, amount in events:
            if kind == "restock":
                new_q = q + amount
                if new_q > cap:
                    exp_wasted += new_q - cap
                    new_q = cap
                q = new_q
            else:  # ship
                if q >= amount:
                    q -= amount
                    exp_filled += 1
                else:
                    exp_backordered += amount - q
                    q = 0
                    exp_backorders += 1

        res = solution.run_bin(cap, events)
        assert res["on_hand"] == q
        assert res["wasted"] == exp_wasted
        assert res["backordered"] == exp_backordered
        assert res["filled_orders"] == exp_filled
        assert res["backordered_orders"] == exp_backorders
        # Invariants that must hold for any correct implementation.
        assert res["filled_orders"] + res["backordered_orders"] == (
            exp_filled + exp_backorders
        )
        assert 0 <= res["on_hand"] <= cap
