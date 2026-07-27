_SEPARATORS = {"_", "-", " "}


def _is_upper(c: str) -> bool:
    return "A" <= c <= "Z"


def _is_lower(c: str) -> bool:
    return "a" <= c <= "z"


def _is_digit(c: str) -> bool:
    return "0" <= c <= "9"


def to_snake(identifier: str) -> str:
    words = []
    current = []

    def flush():
        if current:
            words.append("".join(current))
            current.clear()

    n = len(identifier)
    for i, ch in enumerate(identifier):
        if ch in _SEPARATORS:
            flush()
            continue

        if not current:
            current.append(ch)
            continue

        prev = current[-1]

        # Rule 1: lower/digit followed by uppercase -> boundary before ch
        if _is_upper(ch) and (_is_lower(prev) or _is_digit(prev)):
            flush()
            current.append(ch)
            continue

        # Rule 2: run of >=2 uppercase followed by lowercase ->
        # the last uppercase begins the new word. Detect when the previous char
        # is uppercase, the one before it is uppercase, and the current is lower.
        if _is_lower(ch) and _is_upper(prev) and len(current) >= 2 and _is_upper(current[-2]):
            # move the last uppercase (prev) into a new word, then add ch
            last_upper = current.pop()
            flush()
            current.append(last_upper)
            current.append(ch)
            continue

        current.append(ch)

    flush()
    return "_".join(w.lower() for w in words)
