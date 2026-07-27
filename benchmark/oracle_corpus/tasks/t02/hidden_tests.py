import solution

import random


def test_basic_dedup_and_collapse():
    assert solution.canonicalize_tags(["  Python ", "python", "Data   Science"]) == [
        "python",
        "data science",
    ]


def test_blank_tags_dropped():
    assert solution.canonicalize_tags(["C++", "  ", "c++", "\tGo\t"]) == ["c++", "go"]


def test_all_case_variants_collapse():
    assert solution.canonicalize_tags(["Hello  World", "hello world", "HELLO WORLD"]) == [
        "hello world"
    ]


def test_empty_input_list():
    assert solution.canonicalize_tags([]) == []


def test_all_blank_input():
    assert solution.canonicalize_tags(["", "   ", "\t\n", " \r "]) == []


def test_first_appearance_order_is_preserved():
    # zebra comes first in the input, so it must come first in the output,
    # even though it sorts after "apple".
    out = solution.canonicalize_tags(["Zebra", "apple", "ZEBRA", "Apple"])
    assert out == ["zebra", "apple"]


def test_order_not_alphabetical():
    out = solution.canonicalize_tags(["mango", "banana", "cherry"])
    assert out == ["mango", "banana", "cherry"]


def test_single_element():
    assert solution.canonicalize_tags(["  Solo  Tag  "]) == ["solo tag"]


def test_internal_punctuation_untouched():
    assert solution.canonicalize_tags(["c#/.net", "  C#/.NET "]) == ["c#/.net"]


def test_form_feed_and_vertical_tab_are_trimmed():
    # Leading/trailing form feed (\f) and vertical tab (\v) count as whitespace
    # and must be stripped, so both inputs canonicalize to "python".
    assert solution.canonicalize_tags(["\fPython\f", "\vpython\v"]) == ["python"]


def test_form_feed_and_vertical_tab_collapse_internally():
    # A run made of form feed + vertical tab (mixed with a space) is internal
    # whitespace and collapses to a single ASCII space.
    assert solution.canonicalize_tags(["a\vb", "x\f\v y", "x y"]) == ["a b", "x y"]


def test_vertical_tab_dedups_against_space():
    # "x\vy" collapses to "x y", which is the same canonical form as "x y",
    # so the second input is dropped as a duplicate.
    assert solution.canonicalize_tags(["x\vy", "x y"]) == ["x y"]


def test_lowercasing_is_ascii_only():
    # Only ASCII A-Z fold to a-z. A non-ASCII uppercase letter (here 'E' with an
    # acute accent, U+00C9) is left unchanged, so "MÉTA"-style tags that
    # differ only in that accented capital do NOT merge with an already-lowercase
    # version. The ASCII 'M','T','A' still lowercase.
    out = solution.canonicalize_tags(["MÉTA", "méta"])
    # First canonical form keeps the uppercase accented E; second is fully lower.
    assert out == ["mÉta", "méta"]


def test_ascii_letters_lowercase_around_non_ascii():
    # Non-ASCII characters pass through untouched while surrounding ASCII letters
    # are lowercased; the tag is otherwise unchanged.
    assert solution.canonicalize_tags(["CAÑON Road"]) == ["caÑon road"]


def test_first_contributor_determines_position():
    # "b" first appears at index 0 (from "B"); "a" first appears at index 1.
    # Output order must be b, a -- the position of the FIRST contributing raw tag.
    out = solution.canonicalize_tags(["B", "a", "b", "A"])
    assert out == ["b", "a"]


def test_unicode_whitespace_is_ordinary_character():
    # Whitespace is EXACTLY the six ASCII characters (space, \t, \n, \r, \f, \v).
    # A non-breaking space U+00A0 and EM SPACE U+2003 are Unicode whitespace but
    # NOT in that set, so they are ordinary characters: never trimmed, never
    # collapsed. The common " ".join(s.split()) idiom (Unicode-whitespace-aware)
    # would wrongly strip/collapse them.
    nbsp = " "
    emsp = " "
    # Leading/trailing non-breaking space is NOT trimmed; it stays part of the tag.
    assert solution.canonicalize_tags([nbsp + "python" + nbsp]) == [nbsp + "python" + nbsp]
    # An internal non-breaking space is preserved verbatim (not collapsed to " ").
    assert solution.canonicalize_tags(["a" + nbsp + "b"]) == ["a" + nbsp + "b"]
    # EM SPACE likewise stays as an ordinary character.
    assert solution.canonicalize_tags(["a" + emsp + "b"]) == ["a" + emsp + "b"]
    # "a b" and "a b" are DISTINCT canonical forms (the first has a real
    # non-breaking space, the second an ASCII space) -> both kept, in input order.
    assert solution.canonicalize_tags(["a" + nbsp + "b", "a b"]) == ["a" + nbsp + "b", "a b"]
    # A tag that is ONLY a non-breaking space is non-blank (it survives trimming).
    assert solution.canonicalize_tags([nbsp]) == [nbsp]


def test_no_duplicates_property():
    # Property: output has no duplicate entries and every entry is non-blank
    # and already in canonical form (idempotent under re-canonicalization).
    rng = random.Random(2024)
    words = ["Alpha", "beta ", " Gamma", "delta", "ALPHA", "  beta", "Gamma "]
    for _ in range(200):
        n = rng.randint(0, 12)
        raw = [rng.choice(words) for _ in range(n)]
        out = solution.canonicalize_tags(raw)
        # no duplicates
        assert len(out) == len(set(out))
        # every entry non-blank
        assert all(t != "" for t in out)
        # idempotent: canonicalizing the output yields the same list
        assert solution.canonicalize_tags(out) == out


_WS = " \t\n\r\f\v"


def _ref_canon(tag):
    # Independent reference: strip the full ASCII whitespace set, lowercase ONLY
    # ASCII A-Z, then collapse internal whitespace runs to a single space.
    stripped = tag.strip(_WS)
    lowered = "".join(
        chr(ord(ch) + 32) if "A" <= ch <= "Z" else ch for ch in stripped
    )
    out = []
    in_ws = False
    for ch in lowered:
        if ch in _WS:
            if not in_ws:
                out.append(" ")
            in_ws = True
        else:
            out.append(ch)
            in_ws = False
    return "".join(out)


def test_subset_property_first_appearance():
    # Property: the output, read left to right, matches the order of first
    # appearances of canonical forms in the input. The pool deliberately mixes
    # form feed (\f) and vertical tab (\v) so the whitespace handling is
    # exercised, and an accented capital so the ASCII-only lowercasing is too.
    rng = random.Random(7)
    # Pool mixes ASCII whitespace (\f, \v), accented capitals (ASCII-only lowercasing),
    # and Unicode whitespace that is NOT in the ASCII set: non-breaking space (U+00A0)
    # and EM SPACE (U+2003). Those must be preserved as ordinary characters, so a
    # " ".join(s.split()) implementation diverges from the spec here.
    pool = [
        "X", "y", "Z", "  x ", "Y  ", "z", "\fx\v", "a\vb", "a b", "É", "é",
        "a b", " x ", "p q", " ",
    ]
    for _ in range(300):
        n = rng.randint(0, 10)
        raw = [rng.choice(pool) for _ in range(n)]
        out = solution.canonicalize_tags(raw)
        # reconstruct expected first-appearance order using the spec's rules
        expected = []
        seen = set()
        for tag in raw:
            c = _ref_canon(tag)
            if c and c not in seen:
                seen.add(c)
                expected.append(c)
        assert out == expected
