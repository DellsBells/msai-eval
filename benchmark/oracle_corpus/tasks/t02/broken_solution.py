_ASCII_LOWER = {ord(c): ord(c) + 32 for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}


def _canon(tag: str) -> str:
    # Lowercase ASCII uppercase only (A-Z -> a-z), then trim + collapse whitespace.
    lowered = tag.translate(_ASCII_LOWER)
    # BUG: str.split() with no arguments splits on *Unicode* whitespace, so it
    # wrongly trims/collapses characters like the non-breaking space (U+00A0) and
    # EM SPACE (U+2003) that the spec defines as ordinary (non-whitespace) chars.
    return " ".join(lowered.split())


def canonicalize_tags(raw):
    seen = set()
    result = []
    for tag in raw:
        c = _canon(tag)
        if not c:
            continue
        if c in seen:
            continue
        seen.add(c)
        result.append(c)
    return result
