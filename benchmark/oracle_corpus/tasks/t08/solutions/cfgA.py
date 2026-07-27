def parse_record(text: str) -> dict:
    def parse_value(s):
        if s.startswith('{'):
            return parse_record(s[1:-1])
        elif s.startswith('"'):
            result = []
            escape = False
            for char in s[1:-1]:
                if escape:
                    result.append(char)
                    escape = False
                elif char == '\\':
                    escape = True
                else:
                    result.append(char)
            return ''.join(result)
        else:
            return s

    def parse_entries(s):
        entries = {}
        key = None
        value_start = None
        brace_level = 0
        quote_open = False
        for i, char in enumerate(s):
            if char == '=' and not quote_open and brace_level == 0:
                key = s[:i].strip()
                value_start = i + 1
            elif char == '{' and not quote_open:
                if brace_level == 0:
                    value_start = i
                brace_level += 1
            elif char == '}' and not quote_open:
                brace_level -= 1
                if brace_level == 0:
                    entries[key] = parse_value(s[value_start:i+1].strip())
                    key = None
            elif char == '"' and brace_level == 0:
                if not quote_open:
                    value_start = i
                quote_open = not quote_open
            elif char.isspace() and brace_level == 0 and key is not None and value_start is not None:
                entries[key] = parse_value(s[value_start:i].strip())
                key = None
        if key is not None and value_start is not None:
            entries[key] = parse_value(s[value_start:].strip())
        return entries

    text = text.strip()
    if text.startswith('{') and text.endswith('}'):
        return parse_entries(text[1:-1])
    return {}