import solution

import random


def test_basic_eviction():
    assert solution.replay(2, ["TOUCH a", "TOUCH b", "TOUCH c"]) == ["b", "c"]


def test_empty_ops():
    assert solution.replay(3, []) == []


def test_retouch_moves_to_back():
    assert solution.replay(3, ["TOUCH a", "TOUCH b", "TOUCH a"]) == ["b", "a"]


def test_retouch_no_eviction_when_full():
    # Full log, re-touch existing key: size stays, nothing evicted.
    ops = ["TOUCH a", "TOUCH b", "TOUCH a"]  # cap 2, full
    assert solution.replay(2, ops) == ["b", "a"]
    # And a following new key evicts the now-front 'b'.
    ops2 = ["TOUCH a", "TOUCH b", "TOUCH a", "TOUCH c"]
    assert solution.replay(2, ops2) == ["a", "c"]


def test_capacity_one():
    assert solution.replay(1, ["TOUCH a", "TOUCH b", "TOUCH c"]) == ["c"]
    assert solution.replay(1, ["TOUCH a", "TOUCH a"]) == ["a"]


def test_forget_present_and_absent():
    assert solution.replay(3, ["TOUCH x", "FORGET x", "FORGET y"]) == []
    assert solution.replay(3, ["TOUCH a", "TOUCH b", "FORGET a"]) == ["b"]


def test_forget_then_reinsert_goes_to_back():
    ops = ["TOUCH a", "TOUCH b", "FORGET a", "TOUCH a"]
    # [a,b]; forget a -> [b]; touch a -> [b,a]
    assert solution.replay(3, ops) == ["b", "a"]


def test_checkpoint_rollback_independence():
    # The snapshot must be immune to the later TOUCH c eviction.
    ops = ["TOUCH a", "TOUCH b", "CHECKPOINT", "TOUCH c", "ROLLBACK"]
    assert solution.replay(2, ops) == ["a", "b"]


def test_rollback_empty_stack_is_noop():
    assert solution.replay(2, ["TOUCH a", "ROLLBACK"]) == ["a"]


def test_commit_discards_snapshot():
    ops = ["TOUCH a", "CHECKPOINT", "TOUCH b", "COMMIT", "ROLLBACK"]
    # commit removes the only snapshot; rollback then is a no-op -> [a,b]
    assert solution.replay(2, ops) == ["a", "b"]


def test_nested_checkpoints():
    ops = [
        "TOUCH a",              # [a]
        "CHECKPOINT",           # snap1 = [a]
        "TOUCH b",              # [a,b]
        "CHECKPOINT",           # snap2 = [a,b]
        "TOUCH c",              # cap 3 -> [a,b,c]
        "ROLLBACK",             # restore snap2 -> [a,b]
        "ROLLBACK",             # restore snap1 -> [a]
    ]
    assert solution.replay(3, ops) == ["a"]


def test_snapshot_not_mutated_by_later_ops():
    # Take a checkpoint, then heavily mutate, then rollback: must equal the
    # exact snapshot regardless of intervening evictions/forgets/touches.
    ops = [
        "TOUCH a", "TOUCH b", "TOUCH c",   # [a,b,c] cap 3
        "CHECKPOINT",                       # snap = [a,b,c]
        "TOUCH d",                          # evict a -> [b,c,d]
        "FORGET b",                         # [c,d]
        "TOUCH a",                          # [c,d,a]
        "ROLLBACK",                         # -> [a,b,c]
    ]
    assert solution.replay(3, ops) == ["a", "b", "c"]


def test_touch_after_rollback_behaves_normally():
    ops = [
        "TOUCH a", "TOUCH b",   # [a,b]
        "CHECKPOINT",           # snap [a,b]
        "TOUCH c",              # evict a -> [b,c]
        "ROLLBACK",             # -> [a,b]
        "TOUCH a",              # existing -> move to back -> [b,a]
    ]
    assert solution.replay(2, ops) == ["b", "a"]


def test_rollback_then_new_ops_do_not_corrupt_other_snapshots():
    # Two checkpoints of the same-ish list; ensure aliasing between the live log
    # and a popped snapshot does not corrupt a still-held snapshot.
    ops = [
        "TOUCH a",              # [a]
        "CHECKPOINT",           # snapA = [a]
        "CHECKPOINT",           # snapB = [a]
        "ROLLBACK",             # pop snapB, log becomes [a]
        "TOUCH b",              # [a,b]  (must NOT alter snapA)
        "ROLLBACK",             # pop snapA -> [a]
    ]
    assert solution.replay(3, ops) == ["a"]


def _model(capacity, ops):
    # Independent oracle using an explicit copy discipline.
    from collections import deque
    log = deque()
    stack = []
    for op in ops:
        verb, _, arg = op.partition(" ")
        if verb == "TOUCH":
            if arg in log:
                log.remove(arg)
                log.append(arg)
            else:
                if len(log) >= capacity:
                    log.popleft()
                log.append(arg)
        elif verb == "FORGET":
            if arg in log:
                log.remove(arg)
        elif verb == "CHECKPOINT":
            stack.append(list(log))
        elif verb == "ROLLBACK":
            if stack:
                log = deque(stack.pop())
        elif verb == "COMMIT":
            if stack:
                stack.pop()
    return list(log)


def test_property_matches_model():
    rng = random.Random(555)
    keys = ["a", "b", "c", "d", "e"]
    for _ in range(400):
        cap = rng.randint(1, 4)
        n = rng.randint(0, 16)
        ops = []
        for _ in range(n):
            r = rng.random()
            if r < 0.45:
                ops.append("TOUCH " + rng.choice(keys))
            elif r < 0.6:
                ops.append("FORGET " + rng.choice(keys))
            elif r < 0.75:
                ops.append("CHECKPOINT")
            elif r < 0.9:
                ops.append("ROLLBACK")
            else:
                ops.append("COMMIT")
        assert solution.replay(cap, ops) == _model(cap, ops)


def test_property_size_never_exceeds_capacity():
    # Invariant: after any prefix of ops, the log length never exceeds capacity.
    rng = random.Random(9090)
    keys = ["k1", "k2", "k3", "k4", "k5", "k6"]
    for _ in range(200):
        cap = rng.randint(1, 3)
        n = rng.randint(0, 20)
        ops = []
        for _ in range(n):
            r = rng.random()
            if r < 0.6:
                ops.append("TOUCH " + rng.choice(keys))
            elif r < 0.75:
                ops.append("FORGET " + rng.choice(keys))
            elif r < 0.85:
                ops.append("CHECKPOINT")
            elif r < 0.95:
                ops.append("ROLLBACK")
            else:
                ops.append("COMMIT")
        # Check the invariant on every prefix.
        for i in range(len(ops) + 1):
            result = solution.replay(cap, ops[:i])
            assert len(result) <= cap
            # distinctness invariant
            assert len(set(result)) == len(result)
