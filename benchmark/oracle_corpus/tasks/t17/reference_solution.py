"""Reference solution for the Bracket Fault Locator task."""

_PAIRS = {")": "(", "]": "[", "}": "{"}
_OPENERS = {"(", "[", "{"}
_CLOSERS = {")", "]", "}"}


def find_fault(s: str) -> int:
    # Stack of (opener_char, index_in_s) for currently open groups.
    stack = []
    for i, ch in enumerate(s):
        if ch in _OPENERS:
            stack.append((ch, i))
        elif ch in _CLOSERS:
            if not stack:
                # Stray closer.
                return i
            opener_char, _ = stack[-1]
            if _PAIRS[ch] != opener_char:
                # Mismatched closer.
                return i
            stack.pop()
        # Non-bracket characters are ignored.
    if stack:
        # Innermost (most recently opened) unclosed opener.
        return stack[-1][1]
    return -1
