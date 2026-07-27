def check_brackets(text: str) -> tuple:
    pairs = {")": "(", "]": "[", "}": "{"}
    opens = set("([{")
    closes = set(")]}")

    # Stack holds tuples of (open_char, index_of_open).
    stack = []
    max_depth = 0

    for i, ch in enumerate(text):
        if ch in opens:
            stack.append((ch, i))
            if len(stack) > max_depth:
                max_depth = len(stack)
        elif ch in closes:
            if not stack:
                # Rule 1: closing bracket with nothing open.
                return (False, max_depth, i)
            top_char, _top_idx = stack[-1]
            if top_char != pairs[ch]:
                # Rule 2: mismatched closing bracket.
                return (False, max_depth, i)
            stack.pop()
        # Non-bracket characters are ignored.

    if stack:
        # Rule 3: something left unclosed. Report the left-most open index.
        first_unclosed_idx = stack[0][1]
        return (False, max_depth, first_unclosed_idx)

    return (True, max_depth, -1)
