# Warehouse Bin Simulation

You are simulating a single storage bin in a warehouse over a sequence of events.
The bin holds units of one product and has a fixed maximum capacity. Write a
function that replays the events and reports the final state plus some tallies.

## Function to implement

```python
def run_bin(capacity, events):
    ...
```

### Parameters

- `capacity` (int): the maximum number of units the bin can hold. Always `>= 0`.
- `events` (list of tuples): each event is `(kind, amount)` where `kind` is one
  of the strings `"restock"` or `"ship"`, and `amount` is a non-negative int.
  Events are processed strictly in order.

The bin starts **empty** (0 units on hand).

### Event rules

Process each event against the current on-hand quantity `q` (starting at 0):

- **`("restock", amount)`**: add `amount` units, but never exceed `capacity`.
  The new quantity is `min(q + amount, capacity)`. Any units that would exceed
  capacity are **discarded** (they overflow and are lost). Count the number of
  discarded units toward a running `wasted` total.

- **`("ship", amount)`**: remove up to `amount` units to fulfill an order. If
  `q >= amount`, ship all `amount` units and the order is fully filled. If
  `q < amount`, ship all `q` units the bin currently has (possibly 0), and the
  remaining `amount - q` units become a **backorder**. Add the backordered
  quantity to a running `backordered` total. A ship event that can be fully
  filled (including shipping exactly `q == amount`) is a fully-filled order; a
  ship event that cannot be fully filled is a backordered order (even if it
  ships some units).

An `amount` of `0` for either kind is a valid event: a `("restock", 0)` changes
nothing and wastes nothing; a `("ship", 0)` ships nothing and is considered
**fully filled** (it is not a backorder).

### Return value

Return a dictionary with exactly these keys:

- `"on_hand"`: units remaining in the bin at the end (int).
- `"wasted"`: total units discarded to overflow across all restocks (int).
- `"backordered"`: total units that could not be shipped across all ship events
  (int).
- `"filled_orders"`: the number of `"ship"` events that were fully filled (int).
- `"backordered_orders"`: the number of `"ship"` events that were **not** fully
  filled (int).

Note that `filled_orders + backordered_orders` equals the total number of
`"ship"` events; `"restock"` events are never counted as orders.

If `events` is empty, return `on_hand` 0, all tallies 0.

## Examples

```python
run_bin(10, [("restock", 8), ("ship", 3), ("restock", 8), ("ship", 20)])
# start 0
# restock 8 -> q=8, wasted 0
# ship 3   -> q=5, filled order
# restock 8 -> q+8=13, min(10, 13)=10, discarded 3 -> wasted 3
# ship 20  -> ships 10, q=0, backorder 10 -> backordered order
# => {"on_hand": 0, "wasted": 3, "backordered": 10,
#     "filled_orders": 1, "backordered_orders": 1}

run_bin(5, [("ship", 2), ("restock", 10)])
# ship 2 with q=0 -> ships 0, backorder 2 -> backordered order
# restock 10 -> min(5, 10)=5, discarded 5 -> wasted 5
# => {"on_hand": 5, "wasted": 5, "backordered": 2,
#     "filled_orders": 0, "backordered_orders": 1}

run_bin(4, [("ship", 0), ("restock", 0)])
# ship 0 -> fully filled (not a backorder)
# restock 0 -> nothing
# => {"on_hand": 0, "wasted": 0, "backordered": 0,
#     "filled_orders": 1, "backordered_orders": 0}
```

## Constraints

- `capacity`, all `amount` values, and the returned tallies are integers `>= 0`.
- Do not use any randomness, I/O, or external libraries.
