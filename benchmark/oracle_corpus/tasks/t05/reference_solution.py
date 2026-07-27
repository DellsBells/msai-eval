def parse_settings(text: str) -> dict:
    result = {}
    for entry in text.split(";"):
        # Skip entries that are empty or only spaces.
        if entry.strip(" ") == "":
            continue
        # Must contain an '=' to be a valid pair.
        if "=" not in entry:
            continue
        key, value = entry.split("=", 1)
        key = key.strip(" ")
        value = value.strip(" ")
        if key == "":
            continue
        result[key] = value
    return result
