def parse_record(text: str) -> dict:
    _KEY_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
    _TOKEN_CHARS = _KEY_CHARS | set(".+-")

    pos = 0
    n = len(text)

    def skip_ws(i):
        while i < n and text[i] in " \t\r\n":
            i += 1
        return i

    def parse_record_at(i):
        i = skip_ws(i)
        assert text[i] == "{"
        i += 1
        result = {}
        while True:
            i = skip_ws(i)
            if i < n and text[i] == "}":
                i += 1
                return result, i
            key, i = parse_key(i)
            i = skip_ws(i)
            assert text[i] == "="
            i += 1
            i = skip_ws(i)
            value, i = parse_value(i)
            result[key] = value

    def parse_key(i):
        start = i
        while i < n and text[i] in _KEY_CHARS:
            i += 1
        return text[start:i], i

    def parse_value(i):
        ch = text[i]
        if ch == "{":
            return parse_record_at(i)
        if ch == '"':
            return parse_quoted(i)
        return parse_token(i)

    def parse_quoted(i):
        assert text[i] == '"'
        i += 1
        out = []
        while i < n:
            c = text[i]
            if c == "\\":
                nxt = text[i + 1] if i + 1 < n else ""
                if nxt == '"':
                    out.append('"')
                    i += 2
                    continue
                # BUG: does not treat "\\" as an escape for a single backslash.
                # The backslash is emitted and the next char handled normally,
                # so "\\" becomes two backslashes instead of one.
                out.append("\\")
                i += 1
                continue
            if c == '"':
                i += 1
                return "".join(out), i
            out.append(c)
            i += 1
        return "".join(out), i

    def parse_token(i):
        start = i
        while i < n and text[i] in _TOKEN_CHARS:
            i += 1
        return text[start:i], i

    value, pos = parse_record_at(pos)
    return value
