# Contest Standings

You are scoring a contest and must assign a **rank** to every contestant.

Implement a single function:

```python
def rank_contestants(contestants):
    ...
```

## Input

`contestants` is a list of dictionaries. Each dictionary has exactly these keys:

- `"id"`: a string, unique across the list, identifying the contestant.
- `"score"`: an integer (higher is better; may be negative).
- `"penalty"`: an integer (lower is better; always `>= 0`).

## What determines standing

A contestant is *strictly better* than another when they have a higher `score`.
If two contestants have the **same** `score`, the one with the **lower**
`penalty` is strictly better. Two contestants who share both the same `score`
**and** the same `penalty` are considered **tied** — there is no further
distinction between them for ranking purposes.

## Ranking rule (standard competition ranking, "1224")

Sort contestants from best to worst. Assign ranks as follows:

- The best contestant(s) get rank `1`.
- **All tied contestants receive the same rank.**
- After a group of `k` tied contestants at some rank `r`, the next (worse) group
  starts at rank `r + k` (ranks are *skipped* for the tied positions).

For example, if two contestants tie for the best position, they are both rank
`1`, and the next contestant is rank `3` (rank `2` is skipped).

## Output order and tie-breaking within equal ranks

Return a list of `(id, rank)` tuples. The list must be ordered from best to
worst (rank ascending). **Among contestants that are tied (same rank), order
them by `id` ascending** using ordinary string comparison. Contestants with
different ranks always appear in rank order regardless of `id`.

Do not mutate the input.

## Return value

A list of `(id, rank)` two-tuples. Every input contestant appears exactly once.
For empty input, return an empty list.

## Examples

Example 1:

```python
rank_contestants([
    {"id": "c1", "score": 100, "penalty": 5},
    {"id": "c2", "score": 100, "penalty": 5},
    {"id": "c3", "score": 90,  "penalty": 0},
])
# ->
# [("c1", 1), ("c2", 1), ("c3", 3)]
```

(c1 and c2 tie — same score and penalty — so both are rank 1; c3 is rank 3
because rank 2 is skipped.)

Example 2:

```python
rank_contestants([
    {"id": "x", "score": 50, "penalty": 10},
    {"id": "y", "score": 50, "penalty": 3},
    {"id": "z", "score": 50, "penalty": 3},
])
# ->
# [("y", 1), ("z", 1), ("x", 3)]
```

(y and z share score 50 and penalty 3, so both are rank 1; x has a higher
penalty, so it is worse and gets rank 3. Within the tied pair, "y" < "z".)

Example 3:

```python
rank_contestants([])
# -> []
```

## Constraints

- Python 3, standard library only.
- The function must be deterministic.
- Up to a few thousand contestants.
