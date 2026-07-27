_WS = " \t\n\r\f\v"

# Fixed translation table: only ASCII A-Z fold to a-z; every other code point
# (including non-ASCII uppercase like 'É' or 'Ç') is left untouched.
_ASCII_LOWER = {ord(c): ord(c) + 32 for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}


def _canon(tag: str) -> str:
    # 1. trim leading/trailing ASCII whitespace
    stripped = tag.strip(_WS)
    # 2. lowercase ASCII uppercase letters only (A-Z -> a-z)
    lowered = stripped.translate(_ASCII_LOWER)
    # 3. collapse internal whitespace runs to a single space
    out = []
    in_ws = False
    for ch in lowered:
        if ch in _WS:
            if not in_ws:
                out.append(" ")
            in_ws = True
        else:
            out.append(ch)
            in_ws = False
    return "".join(out)


def canonicalize_tags(raw):
    seen = set()
    result = []
    for tag in raw:
        c = _canon(tag)
        if c == "":
            continue
        if c in seen:
            continue
        seen.add(c)
        result.append(c)
    return result
