"""Reference solution for the Bounded Session Log with Checkpoints task."""


def replay(capacity, ops):
    log = []          # recency order: front = least recent, back = most recent
    checkpoints = []  # stack of snapshots (each a list copy of the log)

    for op in ops:
        verb, _, arg = op.partition(" ")

        if verb == "TOUCH":
            key = arg
            if key in log:
                # Move existing key to the back (most recent).
                log.remove(key)
                log.append(key)
            else:
                # New key: evict front if at capacity, then insert at back.
                if len(log) >= capacity:
                    log.pop(0)
                log.append(key)
        elif verb == "FORGET":
            key = arg
            if key in log:
                log.remove(key)
        elif verb == "CHECKPOINT":
            # Independent snapshot: copy the current log.
            checkpoints.append(list(log))
        elif verb == "ROLLBACK":
            if checkpoints:
                snapshot = checkpoints.pop()
                log = list(snapshot)  # restore contents and order exactly
        elif verb == "COMMIT":
            if checkpoints:
                checkpoints.pop()
    return log
