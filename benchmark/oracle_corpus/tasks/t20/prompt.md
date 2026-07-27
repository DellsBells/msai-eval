# Bounded Session Log with Checkpoints

You are implementing the state machine behind a session recorder that keeps a
**bounded, ordered log of the most-recently-touched keys** and also supports
**checkpoint / rollback** of that log via a checkpoint stack.

Implement a single function:

```python
def replay(capacity: int, ops: list[str]) -> list[str]:
    ...
```

- `capacity` is a positive integer: the maximum number of distinct keys the log may
  hold at once.
- `ops` is a list of operation strings, applied in order.
- Return the final log as a list of keys ordered **from least-recently-touched
  (front) to most-recently-touched (back)**.

## The log

The log is an ordered collection of **distinct** keys. "Order" is recency order:
the front is the least-recently-touched key, the back is the most-recently-touched.
A key appears at most once. The log starts empty.

## Operations

Each op string has a verb and, for some verbs, a single space-separated argument.

1. `TOUCH <key>` — mark `<key>` as most-recently-used.
   - If `<key>` is already in the log, move it to the back (most-recent). The log
     size does not change.
   - If `<key>` is **not** in the log, insert it at the back. If this would exceed
     `capacity`, first **evict the least-recently-touched key** (the current front)
     to make room, then insert. (With `capacity == 0` never occurring — capacity is
     always >= 1.)
   - `<key>` is any non-empty token with no spaces.

2. `FORGET <key>` — remove `<key>` from the log if present; if absent, do nothing.

3. `CHECKPOINT` — push a snapshot of the **current log** (its exact contents and
   order) onto the checkpoint stack. Does not change the log.

4. `ROLLBACK` — pop the top snapshot off the checkpoint stack and replace the entire
   current log with it (restoring both contents and recency order exactly). If the
   checkpoint stack is empty, `ROLLBACK` does nothing.

5. `COMMIT` — pop and discard the top snapshot off the checkpoint stack (the current
   log is kept as-is). If the checkpoint stack is empty, `COMMIT` does nothing.

## Important interaction rules

- Eviction only happens on a `TOUCH` that inserts a **new** key into a **full**
  log. Re-touching an existing key never evicts anything.
- A snapshot taken by `CHECKPOINT` is independent: later `TOUCH`/`FORGET` operations
  must not mutate an already-taken snapshot, and restoring via `ROLLBACK` must not
  be affected by operations that happened after the checkpoint was taken.
- After a `ROLLBACK`, the restored log behaves exactly as if it had that content and
  recency order all along (subsequent `TOUCH` of an existing restored key moves it
  to the back, etc.).
- `capacity` bounds the live log. A snapshot always has at most `capacity` keys
  (because the log never exceeds capacity), so restoring one can never overflow.

You may assume every op string is well-formed.

## Return value

Return the final log as `list[str]`, front (least-recent) first, back (most-recent)
last. An empty log returns `[]`.

## Examples

```python
replay(2, ["TOUCH a", "TOUCH b", "TOUCH c"])
# a,b then TOUCH c: full (cap 2), evict front 'a', insert 'c' -> [b, c]
# -> ["b", "c"]

replay(3, ["TOUCH a", "TOUCH b", "TOUCH a"])
# a,b ; TOUCH a moves a to back -> [b, a]
# -> ["b", "a"]

replay(2, ["TOUCH a", "TOUCH b", "CHECKPOINT", "TOUCH c", "ROLLBACK"])
# log [a,b]; checkpoint saves [a,b]; TOUCH c evicts a -> [b,c];
# ROLLBACK restores [a,b]
# -> ["a", "b"]

replay(3, ["TOUCH x", "FORGET x", "FORGET y"])
# TOUCH x -> [x]; FORGET x -> []; FORGET y absent -> []
# -> []

replay(2, ["TOUCH a", "CHECKPOINT", "TOUCH b", "COMMIT", "ROLLBACK"])
# [a]; checkpoint [a]; TOUCH b -> [a,b]; COMMIT discards snapshot;
# ROLLBACK now has empty stack -> no-op -> [a,b]
# -> ["a", "b"]
```
