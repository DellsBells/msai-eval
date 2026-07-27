def slugify(text: str) -> str:
    out = []
    prev_sep = False
    for ch in text:
        # Step 1: ASCII-only lowercasing (A-Z -> a-z), everything else untouched.
        if "A" <= ch <= "Z":
            ch = chr(ord(ch) + 32)
        # Step 2: word character = ASCII lowercase letter or ASCII digit.
        if ("a" <= ch <= "z") or ("0" <= ch <= "9"):
            out.append(ch)
            prev_sep = False
        else:
            # separator: emit a single hyphen for a maximal run
            if not prev_sep:
                out.append("-")
            prev_sep = True
    result = "".join(out)
    # strip a single leading/trailing hyphen (at most one of each can exist)
    if result.startswith("-"):
        result = result[1:]
    if result.endswith("-"):
        result = result[:-1]
    return result
