import solution

import random
import re


def _canonical_oracle(s):
    # Independent reference for the canonical snake_case form, built with a
    # different strategy than a scanning state machine: insert an explicit
    # boundary marker at each transition, then split/lowercase/join.
    #   rule 1 (lower/digit -> upper): boundary before the uppercase.
    #   rule 2 (>=2 upper run -> lower): boundary before the LAST uppercase of
    #           the run, i.e. between the penultimate uppercase and the final
    #           uppercase that starts the following lowercase word.
    SEP = "\x00"
    # Rule 1: a lowercase letter or digit immediately followed by an uppercase.
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", SEP, s)
    # Rule 2: an uppercase that is (a) preceded by another uppercase [so it is
    # part of a run of >=2] and (b) immediately followed by a lowercase letter.
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", SEP, s)
    # Real separators become the same boundary marker.
    s = re.sub(r"[_\- ]+", SEP, s)
    words = [w for w in s.split(SEP) if w]
    return "_".join(w.lower() for w in words)


def test_camel_with_acronym_run():
    assert solution.to_snake("getHTTPResponseCode") == "get_http_response_code"


def test_kebab_and_upper_collapse_same():
    assert solution.to_snake("Get-HTTP-Response-Code") == "get_http_response_code"


def test_acronym_then_digit_then_word():
    assert solution.to_snake("parseJSON2Value") == "parse_json2_value"


def test_simple_camel():
    assert solution.to_snake("getName") == "get_name"


def test_acronym_to_word_boundary():
    assert solution.to_snake("HTTPResponse") == "http_response"
    assert solution.to_snake("JSONData") == "json_data"
    assert solution.to_snake("APIClient") == "api_client"


def test_no_split_letter_digit():
    assert solution.to_snake("utf8") == "utf8"
    assert solution.to_snake("v2") == "v2"


def test_digit_then_upper_splits():
    assert solution.to_snake("x2Y") == "x2_y"


def test_empty_and_separators_only():
    assert solution.to_snake("") == ""
    assert solution.to_snake("___") == ""
    assert solution.to_snake("  --_ ") == ""


def test_already_snake_case_unchanged():
    assert solution.to_snake("already_snake_case") == "already_snake_case"


def test_single_characters():
    assert solution.to_snake("a") == "a"
    assert solution.to_snake("A") == "a"


def test_trailing_acronym():
    assert solution.to_snake("userID") == "user_id"
    assert solution.to_snake("getURLFromID") == "get_url_from_id"


def test_two_letter_acronym_split():
    assert solution.to_snake("IOStream") == "io_stream"
    assert solution.to_snake("ABCdef") == "ab_cdef"


def test_exactly_two_upper_run_then_lower():
    # The acronym-to-word rule triggers on a run of *exactly two* uppercase
    # letters followed by a lowercase letter, not only on runs of three+.
    # The last uppercase begins the new word.
    assert solution.to_snake("BCd") == "b_cd"
    assert solution.to_snake("aBCd") == "a_b_cd"
    assert solution.to_snake("IDcard") == "i_dcard"
    assert solution.to_snake("EUmember") == "e_umember"
    assert solution.to_snake("XYz") == "x_yz"
    assert solution.to_snake("goURLfetch") == "go_ur_lfetch"
    assert solution.to_snake("parseIObuffer") == "parse_i_obuffer"


def test_all_uppercase_is_one_word():
    assert solution.to_snake("ABC") == "abc"
    assert solution.to_snake("ID") == "id"


def test_leading_trailing_separators_stripped():
    assert solution.to_snake("__getName__") == "get_name"
    assert solution.to_snake("-Get-Name-") == "get_name"


def test_output_shape_property():
    # Property: output is only [a-z0-9_], has no leading/trailing/consecutive
    # underscores.
    rng = random.Random(4242)
    alphabet = "abcABCxyzXYZ012_- "
    for _ in range(400):
        n = rng.randint(0, 20)
        s = "".join(rng.choice(alphabet) for _ in range(n))
        out = solution.to_snake(s)
        assert all(("a" <= c <= "z") or ("0" <= c <= "9") or c == "_" for c in out)
        assert "__" not in out
        assert not out.startswith("_")
        assert not out.endswith("_")


def test_idempotent_property():
    # Property: applying to_snake twice equals applying it once.
    rng = random.Random(31337)
    alphabet = "abcHTMLjsonXY23_- "
    for _ in range(400):
        n = rng.randint(0, 24)
        s = "".join(rng.choice(alphabet) for _ in range(n))
        once = solution.to_snake(s)
        twice = solution.to_snake(once)
        assert once == twice


def test_separator_equivalence_property():
    # Property: replacing separators with any other separator (or swapping
    # underscore/hyphen/space) does not change the canonical form.
    rng = random.Random(2718)
    seps = ["_", "-", " "]
    tokens = ["get", "HTTP", "Name", "JSON", "v2", "API", "id", "url"]
    for _ in range(300):
        k = rng.randint(1, 5)
        chosen = [rng.choice(tokens) for _ in range(k)]
        joined_a = rng.choice(seps).join(chosen)
        joined_b = rng.choice(seps).join(chosen)
        assert solution.to_snake(joined_a) == solution.to_snake(joined_b)
