"""A plausible but subtly wrong solution for the Bracket Fault Locator task."""

_PAIRS = {")": "(", "]": "[", "}": "{"}
_OPENERS = {"(", "[", "{"}
_CLOSERS = {")", "]", "}"}


def find_fault(s: str) -> int:
    stack = []
    for i, ch in enumerate(s):
        if ch in _OPENERS:
            stack.append((ch, i))
        elif ch in _CLOSERS:
            if not stack:
                return i
            opener_char, _ = stack[-1]
            if _PAIRS[ch] != opener_char:
                return i
            stack.pop()
    if stack:
        # BUG: returns the outermost unclosed opener instead of the innermost.
        return stack[0][1]
    return -1
