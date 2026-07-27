def split_fields(line: str, delimiter: str = ",") -> list:
    fields = []
    current = []
    in_quotes = False

    # BUG: treats every '"' as a plain toggle. It never recognizes the
    # doubled-quote ("") escape, so an escaped quote is silently dropped
    # (toggle off then back on) instead of producing a literal '"'.
    for ch in line:
        if ch == '"':
            in_quotes = not in_quotes
            continue
        if ch == delimiter and not in_quotes:
            fields.append("".join(current))
            current = []
            continue
        current.append(ch)

    fields.append("".join(current))
    return fields
