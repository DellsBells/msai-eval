"""A plausible but subtly wrong solution for the Undo/Redo Command Log task."""


def run_editor(commands):
    buffer = ""
    undo_stack = []
    redo_stack = []

    for cmd in commands:
        if cmd == "UNDO":
            if undo_stack:
                prev = undo_stack.pop()
                # BUG: pushes the state we are restoring TO (prev) onto redo,
                # instead of the state we are leaving (the current buffer). A
                # later REDO then restores the pre-edit state, not the redone one.
                redo_stack.append(prev)
                buffer = prev
        elif cmd == "REDO":
            if redo_stack:
                nxt = redo_stack.pop()
                undo_stack.append(buffer)
                buffer = nxt
        else:
            verb, _, payload = cmd.partition(":")
            undo_stack.append(buffer)
            redo_stack.clear()
            if verb == "APPEND":
                buffer = buffer + payload
            elif verb == "BACKSPACE":
                n = int(payload)
                if n >= len(buffer):
                    buffer = ""
                else:
                    buffer = buffer[:len(buffer) - n]
    return buffer
