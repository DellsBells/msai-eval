def run_editor(commands: list[str]) -> str:
    buffer = ""
    undo_stack = []
    redo_stack = []

    for command in commands:
        if command.startswith("APPEND:"):
            _, text = command.split(":", 1)
            undo_stack.append(buffer)
            buffer += text
            redo_stack.clear()
        elif command.startswith("BACKSPACE:"):
            _, n_str = command.split(":", 1)
            n = int(n_str)
            undo_stack.append(buffer)
            buffer = buffer[:-n] if n < len(buffer) else ""
            redo_stack.clear()
        elif command == "UNDO":
            if undo_stack:
                redo_stack.append(buffer)
                buffer = undo_stack.pop()
        elif command == "REDO":
            if redo_stack:
                undo_stack.append(buffer)
                buffer = redo_stack.pop()

    return buffer