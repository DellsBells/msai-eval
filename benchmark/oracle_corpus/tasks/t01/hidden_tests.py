import solution

import random


def test_basic_sentence():
    assert solution.slugify("Hello, World!") == "hello-world"


def test_collapse_multiple_spaces():
    assert solution.slugify("  Multiple   Spaces ") == "multiple-spaces"


def test_underscore_and_accent_are_separators():
    assert solution.slugify("café_bar 42") == "caf-bar-42"


def test_empty_input():
    assert solution.slugify("") == ""


def test_all_separators():
    assert solution.slugify("___") == ""
    assert solution.slugify("!!! ??? ...") == ""


def test_leading_and_trailing_separators():
    assert solution.slugify("--start and end--") == "start-and-end"
    assert solution.slugify("   padded   ") == "padded"


def test_single_word_char():
    assert solution.slugify("a") == "a"
    assert solution.slugify("_a_") == "a"


def test_digits_preserved():
    assert solution.slugify("Room 101 / Level 2") == "room-101-level-2"


def test_underscore_only_between_words():
    # underscores are separators, so words joined by underscores get split
    assert solution.slugify("foo_bar_baz") == "foo-bar-baz"


def test_ascii_only_lowercasing_kelvin_sign():
    # U+212A KELVIN SIGN is a non-ASCII character. Step 1 lowercases only A-Z,
    # so it must be left unchanged and then treated as a separator (Note 4).
    # A Unicode-aware .lower()/.casefold() would fold it to ASCII 'k' -- that is wrong.
    kelvin = "K"
    assert solution.slugify("a" + kelvin + "b") == "a-b"
    assert solution.slugify(kelvin) == ""
    assert solution.slugify("Kelvin " + kelvin + " unit") == "kelvin-unit"


def test_ascii_only_lowercasing_dotted_capital_i():
    # U+0130 LATIN CAPITAL LETTER I WITH DOT ABOVE is non-ASCII; it is a separator.
    # str.lower()/str.casefold() would produce a string containing ASCII 'i',
    # which would incorrectly leak an 'i' into the slug.
    dotted = "İ"
    assert solution.slugify(dotted) == ""
    assert solution.slugify(dotted + "e") == "e"
    assert solution.slugify("x" + dotted + "y") == "x-y"


def test_no_unicode_case_folding_leaks():
    # A battery of non-ASCII characters that a Unicode-aware lowercasing would
    # (wrongly) turn into ASCII word characters. Each is a separator per the spec,
    # so none of their ASCII "folded" forms may appear in the output.
    # U+212A -> 'k', U+0130 -> 'i̇', U+1E9E -> 'ß'/'ss' under casefold, U+2126 -> 'ω' (kept),
    # U+0049.. we include a few whose fold hits ASCII letters/digits.
    cases = {
        "K": "",          # KELVIN SIGN -> would fold to 'k'
        "İ": "",          # I WITH DOT ABOVE -> would fold to 'i' + combining
        "zKy": "z-y",     # k-fold would give 'zky' (no hyphen); spec gives 'z-y'
        "1İ2": "1-2",     # digits around a folding letter stay split
    }
    for src, expected in cases.items():
        assert solution.slugify(src) == expected


def test_non_ascii_digits_are_separators():
    # Step 2 defines a digit strictly as an ASCII digit U+0030-U+0039. Non-ASCII
    # characters that are Unicode digits/numerics (ch.isdigit()/ch.isnumeric() True)
    # are separators, not word characters, and must NOT appear in the output.
    # An implementation using ch.isdigit() instead of "0" <= ch <= "9" would leak them.
    superscript_two = "²"     # SUPERSCRIPT TWO, isdigit() -> True
    arabic_zero = "٠"         # ARABIC-INDIC DIGIT ZERO, isdigit() -> True
    superscript_five = "⁵"    # SUPERSCRIPT FIVE, isdigit() -> True
    arabic_nine = "٩"         # ARABIC-INDIC DIGIT NINE, isdigit() -> True
    # A lone non-ASCII digit is entirely separators -> empty output.
    assert solution.slugify(superscript_two) == ""
    assert solution.slugify(arabic_zero) == ""
    # Embedded between ASCII word chars: acts as a separator, splitting them.
    assert solution.slugify("a" + superscript_two + "b") == "a-b"
    assert solution.slugify("1" + arabic_zero + "2") == "1-2"
    # A run of non-ASCII digits collapses to a single hyphen.
    assert solution.slugify("x" + superscript_five + arabic_nine + "y") == "x-y"
    # None of the ASCII "values" of these digits (2, 0, 5, 9) may leak in.
    assert solution.slugify(superscript_two + arabic_zero + superscript_five + arabic_nine) == ""


def _spec_slugify(text):
    # Independent, straight-from-the-prompt implementation used only to pin down
    # the exact expected output in the differential property test below.
    # ASCII-only lowercasing (step 1), ASCII word chars only (step 2),
    # collapse separator runs to one hyphen (step 3), trim ends (step 4).
    out = []
    prev_sep = False
    for ch in text:
        if "A" <= ch <= "Z":
            ch = chr(ord(ch) + 32)
        if ("a" <= ch <= "z") or ("0" <= ch <= "9"):
            out.append(ch)
            prev_sep = False
        else:
            if not prev_sep:
                out.append("-")
            prev_sep = True
    return "".join(out).strip("-")


def test_no_consecutive_hyphens_property():
    # Property: the output never contains "--", never starts or ends with "-",
    # and only contains [a-z0-9-]. The alphabet includes non-ASCII characters
    # whose Unicode lowercasing WOULD fold to ASCII word chars (U+212A -> 'k',
    # U+0130 -> 'i...'), so a Unicode-aware .lower() implementation diverges here.
    rng = random.Random(1234)
    # Alphabet mixes ASCII word chars, separators, non-ASCII letters that Unicode
    # lowercasing would fold to ASCII (K/İ), and non-ASCII DIGITS (² ٠ ⁵ ٩) that
    # ch.isdigit() reports True for but which the spec treats as separators.
    alphabet = "abcXYZ 09_!?.,-éñ\t\n#@" + "K" + "İ" + "kK9İ0" + "²٠⁵٩"
    for _ in range(300):
        n = rng.randint(0, 25)
        s = "".join(rng.choice(alphabet) for _ in range(n))
        out = solution.slugify(s)
        assert "--" not in out
        assert not out.startswith("-")
        assert not out.endswith("-")
        assert all(("a" <= c <= "z") or ("0" <= c <= "9") or c == "-" for c in out)


def test_matches_spec_over_generated_inputs_property():
    # Differential property: over randomly generated strings drawn from an
    # alphabet that deliberately mixes ASCII word chars, separators, and
    # non-ASCII characters that Unicode case folding would turn into ASCII
    # word chars, the output must exactly match the ASCII-only specification.
    # This pins the step-1 ASCII-only lowercasing requirement.
    rng = random.Random(20260706)
    # includes U+212A (folds to 'k'), U+0130 (folds to contain 'i'), and non-ASCII
    # digits U+00B2/U+0660 (ch.isdigit() True) that the ASCII-only spec must reject.
    alphabet = "aB0 _-.!Zé" + "K" + "İ" + "²٠"
    for _ in range(400):
        n = rng.randint(0, 30)
        s = "".join(rng.choice(alphabet) for _ in range(n))
        assert solution.slugify(s) == _spec_slugify(s)


def test_idempotent_on_slug_property():
    # Property: slugifying an already-valid slug returns it unchanged.
    rng = random.Random(99)
    for _ in range(100):
        parts = []
        k = rng.randint(1, 5)
        for _ in range(k):
            length = rng.randint(1, 6)
            word = "".join(rng.choice("abcdef0123") for _ in range(length))
            parts.append(word)
        slug = "-".join(parts)
        assert solution.slugify(slug) == slug
