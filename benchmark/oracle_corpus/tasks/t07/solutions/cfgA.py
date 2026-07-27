def split_fields(line: str, delimiter: str = ",") -> list:
    fields = []
    current_field = []
    in_quotes = False
    i = 0
    while i < len(line):
        char = line[i]
        if char == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                current_field.append('"')
                i += 1  # Skip the next quote as it's escaped
            else:
                in_quotes = not in_quotes
        elif char == delimiter and not in_quotes:
            fields.append(''.join(current_field))
            current_field = []
        else:
            current_field.append(char)
        i += 1
    fields.append(''.join(current_field))
    return fields