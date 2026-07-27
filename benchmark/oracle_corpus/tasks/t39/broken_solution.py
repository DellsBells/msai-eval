FLAG = 0x7E
ESC = 0x7D
ESC_FLAG = 0x5E
ESC_ESC = 0x5D


def stuff(payload):
    out = bytearray()
    for b in payload:
        if b == FLAG:
            out.append(ESC)
            out.append(ESC_FLAG)
        elif b == ESC:
            out.append(ESC)
            out.append(ESC_ESC)
        else:
            out.append(b)
    return bytes(out)


def frame(payload):
    return stuff(payload) + bytes([FLAG])


def _unstuff(body):
    out = bytearray()
    i = 0
    n = len(body)
    while i < n:
        b = body[i]
        if b == ESC:
            nxt = body[i + 1]
            if nxt == ESC_FLAG:
                out.append(FLAG)
            else:  # ESC_ESC
                out.append(ESC)
            i += 2
        else:
            out.append(b)
            i += 1
    return bytes(out)


def deframe(stream):
    payloads = []
    body = bytearray()
    for b in stream:
        if b == FLAG:
            payloads.append(_unstuff(bytes(body)))
            body = bytearray()
        else:
            body.append(b)
    # BUG: a trailing partial frame (bytes after the last FLAG with no
    # terminating FLAG) is appended instead of being discarded.
    if body:
        payloads.append(_unstuff(bytes(body)))
    return payloads
