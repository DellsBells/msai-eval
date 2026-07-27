# Token-Passing Ring

`n` nodes numbered `0, 1, ..., n-1` are arranged in a ring: after node `n-1`
comes node `0` again. A single token starts held by node `0`. The token is
passed around the ring for a number of rounds. Some nodes become **exhausted**
and are skipped when passing. Write a function that simulates the passing and
reports where the token ends up plus a visit tally.

## Function to implement

```python
def pass_token(n, rounds, step, quota):
    ...
```

### Parameters

- `n` (int): number of nodes, `n >= 1`.
- `rounds` (int): how many times the token is passed, `rounds >= 0`.
- `step` (int): how many positions forward to move on each pass, `step >= 1`.
- `quota` (int): the maximum number of times any single node may **hold** the
  token, `quota >= 1`.

### The rules

- The token begins held by node `0`. Holding the token at the start (before any
  passes) counts as node `0`'s first hold.
- Each node keeps a count of how many times it has held the token. When a node's
  hold count reaches `quota`, that node becomes **exhausted**: it can no longer
  receive the token and is skipped over during passing. (A node can be exhausted
  even while it is the current holder — exhaustion is about *future* receipt.)
- To perform one pass with the given `step`: move forward one position at a time
  around the ring, and count a position only if the node there is **not**
  exhausted. Keep advancing (wrapping around past `n-1` to `0`) until you have
  landed on `step` non-exhausted nodes. The node you land on after counting
  `step` non-exhausted nodes becomes the new holder, and its hold count
  increases by one (possibly making it newly exhausted).
- Exhausted nodes are simply passed over without being counted. The current
  holder's own position does not count toward the `step` for its own pass (you
  always start moving *forward* from the holder).
- If **every other node** is exhausted so that a pass cannot find `step`
  distinct non-exhausted landing spots, stop early: the token stays where it is
  and no further rounds happen. (See the "stuck" rule below.)

### The "stuck" rule (early stop)

Before performing a pass, look at the nodes other than the current holder. If
there are **no** non-exhausted nodes to move to (every other node is exhausted),
the token cannot move: stop immediately and return the current state, even if
`rounds` passes have not all been performed. Note that with `n == 1` there is
never anywhere to move, so every pass is stuck.

When a pass *can* start (at least one other non-exhausted node exists), you are
guaranteed to be able to complete it: you may revisit nodes as you wrap around,
counting each non-exhausted landing as one step, until `step` landings are
counted. (Landing on the same non-exhausted node twice within one pass counts as
two steps.)

### Return value

Return a dictionary with exactly these keys:

- `"holder"`: the node currently holding the token at the end (int).
- `"holds"`: a list of length `n` where `holds[i]` is the number of times node
  `i` held the token (int list). This includes node `0`'s initial hold.
- `"exhausted"`: a sorted list of the node indices that are exhausted at the end
  (list of int).
- `"rounds_done"`: the number of passes actually performed (int). This equals
  `rounds` unless the ring got stuck early.

## Examples

```python
pass_token(4, 3, 1, 99)
# holder starts at 0 (holds[0]=1). step 1, quota high so no exhaustion.
# pass 1: 0 -> 1 (holds[1]=1)
# pass 2: 1 -> 2 (holds[2]=1)
# pass 3: 2 -> 3 (holds[3]=1)
# => {"holder": 3, "holds": [1, 1, 1, 1], "exhausted": [],
#     "rounds_done": 3}

pass_token(3, 5, 1, 2)
# start: holder 0, holds=[1,0,0]
# pass 1: 0->1 holds=[1,1,0]
# pass 2: 1->2 holds=[1,1,1]
# pass 3: 2->0 holds=[2,1,1]; node 0 now exhausted
# pass 4: from 0, skip 0 (exhausted), land on 1 -> holds=[2,2,1]; node1 exhausted
# pass 5: from 1, skip exhausted 0 and 1, land on 2 -> holds=[2,2,2]; node2 exhausted
# => {"holder": 2, "holds": [2, 2, 2], "exhausted": [0, 1, 2],
#     "rounds_done": 5}

pass_token(1, 4, 1, 5)
# n == 1: nowhere to move, stuck on the very first pass.
# => {"holder": 0, "holds": [1], "exhausted": [], "rounds_done": 0}
```

## Constraints

- `1 <= n`, `0 <= rounds`, `1 <= step`, `1 <= quota`.
- Do not use any randomness, I/O, or external libraries.
