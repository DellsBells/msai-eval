import re


def slugify(text: str) -> str:
    # Lowercase, then collapse runs of non-word characters to a hyphen.
    lowered = text.lower()
    # NOTE: uses \w, which (mistakenly) treats underscore and unicode letters as word chars.
    result = re.sub(r"\w+", lambda m: m.group(0), lowered)
    # Replace runs of separators (anything not a word char) with a single hyphen.
    result = re.sub(r"[^\w]+", "-", lowered)
    # Trim leading/trailing hyphens.
    result = result.strip("-")
    return result
