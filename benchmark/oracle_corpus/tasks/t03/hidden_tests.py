import solution

import random


def test_all_regular_words():
    assert solution.title_case("the quick brown fox") == "The Quick Brown Fox"


def test_interior_small_words_lowercased():
    assert solution.title_case("a tale of two cities") == "A Tale of Two Cities"


def test_acronyms_uppercased():
    assert solution.title_case("building an api for the web") == "Building an API for the Web"


def test_empty_input():
    assert solution.title_case("") == ""


def test_single_word_small_word_is_capitalized():
    # a lone small word is both first and last -> capitalized
    assert solution.title_case("the") == "The"
    assert solution.title_case("of") == "Of"


def test_last_word_small_is_capitalized():
    # trailing small word must be capitalized, not lowercased
    assert solution.title_case("what to look for") == "What to Look For"
    assert solution.title_case("something to live by") == "Something to Live By"


def test_first_word_small_is_capitalized():
    assert solution.title_case("in the beginning") == "In the Beginning"


def test_acronym_first_and_last():
    # acronyms uppercased even at the ends
    assert solution.title_case("api design") == "API Design"
    assert solution.title_case("learning sql") == "Learning SQL"


def test_acronym_beats_small_word_never_conflicts():
    assert solution.title_case("the ui and the api") == "The UI and the API"


def test_capitalize_lowercases_rest():
    # "iPhone" -> "Iphone", "MACOS" -> "Macos"
    assert solution.title_case("iPhone and MACOS") == "Iphone and Macos"


def test_near_matches_not_treated_specially():
    # "apis" is not "api"; "theory" is not "the"
    assert solution.title_case("apis and theory") == "Apis and Theory"


def test_interior_non_letter_only_first_char_uppercased():
    # Capitalize means: uppercase ONLY the first char, lowercase the rest.
    # This must NOT behave like str.title(), which uppercases every letter-run.
    assert solution.title_case("mother-in-law story") == "Mother-in-law Story"
    assert solution.title_case("o'brien and sons") == "O'brien and Sons"
    assert solution.title_case("file 123abc here") == "File 123abc Here"
    # a single hyphenated word as sole (first+last) word
    assert solution.title_case("well-being") == "Well-being"
    # digit-led word: first char unchanged, letters after lowercased
    assert solution.title_case("3d") == "3d"
    assert solution.title_case("MP3-player rocks") == "Mp3-player Rocks"


def test_capitalize_is_uppercase_first_not_titlecase():
    # The spec defines capitalize as EXACTLY word[0].upper() + word[1:].lower().
    # For a first character whose uppercase form differs from its titlecase form,
    # this diverges from str.capitalize() (which titlecases the first char):
    #   - U+FB01 LATIN SMALL LIGATURE FI: 'ﬁ'.upper() == 'FI' (two chars),
    #     so 'file' spelled with the ligature must become 'FIle', NOT 'File'.
    #   - U+01C6 LATIN SMALL LETTER DZ WITH CARON: .upper() -> U+01C4 'DZ',
    #     but str.capitalize() titlecases it to U+01C5. Spec requires the uppercase.
    ligature_fi = "ﬁ"        # 'fi' ligature; not in any special set
    assert solution.title_case(ligature_fi + "le") == "FIle"
    assert solution.title_case(ligature_fi + "le here") == "FIle Here"
    dz = "ǆ"                 # dz-with-caron digraph
    assert solution.title_case(dz + "abc") == "Ǆ" + "abc"
    assert solution.title_case(dz + "abc word") == "Ǆ" + "abc Word"
    # A ligature that is NOT the first character of its word must be left lowercased
    # (only the first character is ever uppercased). Here "coﬁn" starts with 'c'.
    assert solution.title_case("co" + ligature_fi + "n end") == "Co" + ligature_fi + "n End"


def test_via_and_vs_are_interior_small_words():
    # 'via' and 'vs' are in the small-word set and must be lowercased when interior.
    assert solution.title_case("paris via london by train") == "Paris via London by Train"
    assert solution.title_case("dogs vs cats in court") == "Dogs vs Cats in Court"
    # but capitalized when first or last
    assert solution.title_case("via appia") == "Via Appia"
    assert solution.title_case("cats vs") == "Cats Vs"


def test_all_interior_small_words_lowercased():
    # Exercise every small word as an interior word (padded by capitalized ends)
    # so an incomplete small-word set is caught.
    smalls = [
        "a", "an", "and", "as", "at", "but", "by", "for", "if", "in",
        "nor", "of", "on", "or", "the", "to", "via", "vs",
    ]
    for w in smalls:
        headline = "start " + w + " end"
        expected = "Start " + w + " End"
        assert solution.title_case(headline) == expected


def test_two_word_headline_both_ends_protected():
    # both words are at an end; interior small-word rule cannot apply to either
    assert solution.title_case("of mice") == "Of Mice"
    assert solution.title_case("look up") == "Look Up"


def test_join_and_count_invariant_property():
    # Property: the number of output words equals the number of input words,
    # and output words never contain spaces (round-trip word count is preserved).
    rng = random.Random(555)
    vocab = [
        "the", "quick", "API", "Fox", "of", "url", "cities", "and", "run", "id",
        "via", "vs", "mother-in-law", "o'brien", "123abc", "MP3-player",
    ]
    for _ in range(300):
        n = rng.randint(1, 8)
        words = [rng.choice(vocab) for _ in range(n)]
        headline = " ".join(words)
        out = solution.title_case(headline)
        out_words = out.split(" ")
        assert len(out_words) == n
        assert all(" " not in w for w in out_words)


def _oracle_title_case(headline):
    # Independent reimplementation of the spec, used as a property oracle.
    small = {
        "a", "an", "and", "as", "at", "but", "by", "for", "if", "in",
        "nor", "of", "on", "or", "the", "to", "via", "vs",
    }
    acronyms = {
        "api", "ui", "id", "url", "http", "https", "sql", "html", "css",
        "json", "xml",
    }
    if headline == "":
        return ""
    words = headline.split(" ")
    n = len(words)
    out = []
    for i, w in enumerate(words):
        key = w.lower()
        if key in acronyms:
            out.append(w.upper())
        elif key in small and i != 0 and i != n - 1:
            out.append(w.lower())
        else:
            # capitalize: first char uppercased, remainder lowercased (NOT str.title)
            out.append(w[:1].upper() + w[1:].lower() if w else w)
    return " ".join(out)


def test_matches_spec_oracle_property():
    # Property: output must match an independent spec reimplementation over
    # randomized headlines that include small words, acronyms, and words with
    # interior non-letter characters (hyphens, apostrophes, digits).
    rng = random.Random(1234)
    vocab = [
        "the", "of", "via", "vs", "nor", "and", "if", "as", "at", "but", "or",
        "api", "URL", "Sql", "id",
        "hello", "World", "QUICK", "fox",
        "mother-in-law", "o'brien", "123abc", "well-being", "MP3-player",
        "iPhone", "MACOS", "3d", "a-b-c", "x'y'z",
        # Words whose first character titlecases differently from how it uppercases,
        # so str.capitalize() diverges from the spec's word[0].upper()+word[1:].lower():
        # U+FB01 'fi' ligature (upper -> 'FI') and U+01C6 dz-caron digraph (upper -> U+01C4).
        "ﬁle", "ﬁ", "ǆabc", "ǆ", "wﬁx",
    ]
    for _ in range(400):
        n = rng.randint(1, 9)
        words = [rng.choice(vocab) for _ in range(n)]
        headline = " ".join(words)
        assert solution.title_case(headline) == _oracle_title_case(headline)


def test_case_insensitive_matching_property():
    # Property: the output depends only on each word's lowercase key and its
    # position, not on the input casing of that word.
    rng = random.Random(888)
    words = ["api", "the", "of", "hello", "sql", "world", "and"]
    for _ in range(200):
        n = rng.randint(1, 6)
        base = [rng.choice(words) for _ in range(n)]
        variant = []
        for w in base:
            # randomly upper/lower/mixed each character
            chars = []
            for c in w:
                r = rng.random()
                if r < 0.34:
                    chars.append(c.upper())
                elif r < 0.67:
                    chars.append(c.lower())
                else:
                    chars.append(c)
            variant.append("".join(chars))
        assert solution.title_case(" ".join(base)) == solution.title_case(" ".join(variant))
