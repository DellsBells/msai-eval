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
    return word[0].upper() + word[1:].lower()


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
