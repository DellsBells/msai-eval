import re

_SEP_RE = re.compile(r"[_\- ]+")


def to_snake(identifier: str) -> str:
    # Insert an underscore at every lower/digit -> upper transition (rule 1),
    # then split on separators, lowercase, and join.
    #
    # NOTE: this handles the lower-to-upper boundary but does NOT split an
    # acronym run from the following word (rule 2 is missing).
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", identifier)
    parts = _SEP_RE.split(spaced)
    words = [p for p in parts if p]
    return "_".join(w.lower() for w in words)
