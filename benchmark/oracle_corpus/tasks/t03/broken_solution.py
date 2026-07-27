_SMALL = {
    "a", "an", "and", "as", "at", "but", "by", "for", "if", "in",
    "nor", "of", "on", "or", "the", "to", "via", "vs",
}
_ACRONYMS = {
    "api", "ui", "id", "url", "http", "https", "sql", "html", "css",
    "json", "xml",
}


def _capitalize(word: str) -> str:
    if word == "":
        return word
    # BUG: str.capitalize() TITLECASES the first character and lowercases the rest.
    # The spec requires word[0].upper() + word[1:].lower(). These differ when the
    # first character's uppercase form differs from its titlecase form -- e.g. the
    # 'fi' ligature U+FB01 ('ﬁ'.upper() == 'FI' but str.capitalize() gives 'Fi'->'File')
    # and the dz-with-caron digraph U+01C6 (upper U+01C4 vs titlecase U+01C5).
    return word.capitalize()


def title_case(headline: str) -> str:
    if headline == "":
        return ""
    words = headline.split(" ")
    n = len(words)
    out = []
    for i, word in enumerate(words):
        key = word.lower()
        if key in _ACRONYMS:
            out.append(word.upper())
        elif key in _SMALL and i != 0 and i != n - 1:
            out.append(word.lower())
        else:
            out.append(_capitalize(word))
    return " ".join(out)
