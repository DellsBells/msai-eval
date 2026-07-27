def _escape_field(field):
    out = []
    for ch in field:
        # BUG: only the delimiter is escaped; a literal backslash in the field
        # is emitted unescaped, which corrupts the frame.
        if ch == "|":
            out.append("\\")
        out.append(ch)
    return "".join(out)


def pack(fields):
    if len(fields) == 0:
        return ""
    return "|".join(_escape_field(f) for f in fields)


def unpack(frame):
    if frame == "":
        return []
    fields = []
    current = []
    i = 0
    n = len(frame)
    while i < n:
        ch = frame[i]
        if ch == "\\":
            current.append(frame[i + 1])
            i += 2
        elif ch == "|":
            fields.append("".join(current))
            current = []
            i += 1
        else:
            current.append(ch)
            i += 1
    fields.append("".join(current))
    return fields
