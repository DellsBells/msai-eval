MAX_RUN = 32767


def _emit_token(out, length, value):
    # BUG: the short/long boundary is off by one. A length of exactly 128 is
    # emitted as a "short" token whose length byte is 0x80 -- but 0x80 has its
    # high bit set, so a decoder reads it back as a long token and corrupts
    # the stream.
    if length <= 128:
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
