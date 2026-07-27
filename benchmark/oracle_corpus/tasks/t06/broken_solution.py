def check_brackets(text: str) -> tuple:
    pairs = {")": "(", "]": "[", "}": "{"}
    opens = set("([{")
    closes = set(")]}")

    stack = []
    max_depth = 0

    for i, ch in enumerate(text):
        if ch in opens:
            stack.append((ch, i))
            if len(stack) > max_depth:
                max_depth = len(stack)
        elif ch in closes:
            if not stack:
                # Rule 1: stray close (this path correctly reports the peak).
                return (False, max_depth, i)
            top_char, _top_idx = stack[-1]
            if top_char != pairs[ch]:
                # Rule 2: mismatched close.
                # BUG: reports the CURRENT running depth (len(stack)) at the
                # error instead of the maximum depth ever reached. When the peak
                # was reached earlier and then partially unwound before this
                # mismatch, this under-reports the depth.
                return (False, len(stack), i)
            stack.pop()

    if stack:
        first_unclosed_idx = stack[0][1]
        return (False, max_depth, first_unclosed_idx)

    return (True, max_depth, -1)
