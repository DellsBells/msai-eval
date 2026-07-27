MAX_RUN = 32767  # 0x7FFF, the largest length a single long token can hold


def _emit_token(out, length, value):
    # length is guaranteed 1..MAX_RUN here.
    if length <= 127:
        out.append(length)
        out.append(value)
    else:
        out.append(0x80 | (length >> 8))
        out.append(length & 0xFF)
        out.append(value)


def encode(data):
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        v = data[i]
        j = i
        while j < n and data[j] == v:
            j += 1
        run = j - i
        # Split runs longer than MAX_RUN into MAX_RUN-sized chunks; the final
        # chunk carries the remainder (never zero).
        while run > MAX_RUN:
            _emit_token(out, MAX_RUN, v)
            run -= MAX_RUN
        _emit_token(out, run, v)
        i = j
    return bytes(out)


def decode(blob):
    out = bytearray()
    i = 0
    n = len(blob)
    while i < n:
        h = blob[i]
        if h < 128:
            length = h
            value = blob[i + 1]
            out.extend(bytes([value]) * length)
            i += 2
        else:
            length = ((h & 0x7F) << 8) | blob[i + 1]
            value = blob[i + 2]
            out.extend(bytes([value]) * length)
            i += 3
    return bytes(out)
