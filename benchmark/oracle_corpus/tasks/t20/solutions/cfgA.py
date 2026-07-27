def replay(capacity: int, ops: list[str]) -> list[str]:
    log = []
    checkpoint_stack = []

    for op in ops:
        parts = op.split()
        verb = parts[0]
        
        if verb == "TOUCH":
            key = parts[1]
            if key in log:
                log.remove(key)
            log.append(key)
            if len(log) > capacity:
                log.pop(0)
        
        elif verb == "FORGET":
            key = parts[1]
            if key in log:
                log.remove(key)
        
        elif verb == "CHECKPOINT":
            checkpoint_stack.append(log.copy())
        
        elif verb == "ROLLBACK":
            if checkpoint_stack:
                log[:] = checkpoint_stack.pop()
        
        elif verb == "COMMIT":
            if checkpoint_stack:
                checkpoint_stack.pop()

    return log