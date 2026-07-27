"""A plausible but subtly wrong solution for the Bounded Session Log task."""


def replay(capacity, ops):
    log = []
    checkpoints = []

    for op in ops:
        verb, _, arg = op.partition(" ")

        if verb == "TOUCH":
            key = arg
            if key in log:
                log.remove(key)
                log.append(key)
            else:
                if len(log) >= capacity:
                    log.pop(0)
                log.append(key)
        elif verb == "FORGET":
            key = arg
            if key in log:
                log.remove(key)
        elif verb == "CHECKPOINT":
            # BUG: stores a reference to the live list instead of a copy. Later
            # mutations to `log` bleed into the snapshot, and because ROLLBACK
            # rebinds `log` to a fresh list, subsequent edits after a rollback
            # can corrupt snapshots that alias the same underlying list.
            checkpoints.append(log)
        elif verb == "ROLLBACK":
            if checkpoints:
                snapshot = checkpoints.pop()
                log = snapshot
        elif verb == "COMMIT":
            if checkpoints:
                checkpoints.pop()
    return log
