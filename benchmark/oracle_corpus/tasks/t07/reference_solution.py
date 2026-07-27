def split_fields(line: str, delimiter: str = ",") -> list:
    fields = []
    current = []
    in_quotes = False
    i = 0
    n = len(line)

    while i < n:
        ch = line[i]
        if ch == '"':
            if in_quotes and i + 1 < n and line[i + 1] == '"':
                # Escaped quote: emit one literal '"', stay inside quotes.
                current.append('"')
                i += 2
                continue
            # Otherwise toggle quote mode; the quote char is structural.
            in_quotes = not in_quotes
            i += 1
            continue
        if ch == delimiter and not in_quotes:
            fields.append("".join(current))
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1

    fields.append("".join(current))
    return fields
