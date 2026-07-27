"""Reference solution for the Undo/Redo Command Log task."""


def run_editor(commands):
    buffer = ""
    undo_stack = []   # snapshots of buffer state *before* each edit
    redo_stack = []   # snapshots pushed by UNDO, consumed by REDO

    for cmd in commands:
        if cmd == "UNDO":
            if undo_stack:
                prev = undo_stack.pop()
                redo_stack.append(buffer)  # remember current state for REDO
                buffer = prev
            # empty undo stack -> silent no-op, redo untouched
        elif cmd == "REDO":
            if redo_stack:
                nxt = redo_stack.pop()
                undo_stack.append(buffer)  # remember current state for UNDO
                buffer = nxt
            # empty redo stack -> silent no-op, undo untouched
        else:
            # An editing command: record pre-edit state, clear redo, then edit.
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
