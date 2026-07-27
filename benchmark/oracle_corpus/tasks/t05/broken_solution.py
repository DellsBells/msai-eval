def parse_settings(text: str) -> dict:
    result = {}
    for entry in text.split(";"):
        if entry.strip(" ") == "":
            continue
        if "=" not in entry:
            continue
        # BUG: splits on every '=', so values containing '=' are truncated,
        # and the extra pieces are silently discarded.
        parts = entry.split("=")
        key = parts[0].strip(" ")
        value = parts[1].strip(" ")
        if key == "":
            continue
        result[key] = value
    return result
