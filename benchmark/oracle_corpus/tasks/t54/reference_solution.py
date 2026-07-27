def run_bin(capacity, events):
    q = 0
    wasted = 0
    backordered = 0
    filled_orders = 0
    backordered_orders = 0
    for kind, amount in events:
        if kind == "restock":
            new_q = q + amount
            if new_q > capacity:
                wasted += new_q - capacity
                new_q = capacity
            q = new_q
        elif kind == "ship":
            if q >= amount:
                q -= amount
                filled_orders += 1
            else:
                shortfall = amount - q
                backordered += shortfall
                q = 0
                backordered_orders += 1
    return {
        "on_hand": q,
        "wasted": wasted,
        "backordered": backordered,
        "filled_orders": filled_orders,
        "backordered_orders": backordered_orders,
    }
