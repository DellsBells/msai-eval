import solution

import random


def test_simple_pack():
    assert solution.pack(["name", "value"]) == "name|value"
    assert solution.pack(["a", "b", "c"]) == "a|b|c"


def test_empty_list_and_empty_field():
    assert solution.pack([]) == ""
    assert solution.pack([""]) == ""
    assert solution.pack(["", ""]) == "|"
    assert solution.pack(["", "x", ""]) == "|x|"


def test_pack_escapes_pipe():
    assert solution.pack(["a|b"]) == "a\\|b"
    assert solution.pack(["a|b", "c"]) == "a\\|b|c"


def test_pack_escapes_backslash():
    assert solution.pack(["c\\d"]) == "c\\\\d"
    # a field that is a lone backslash
    assert solution.pack(["\\"]) == "\\\\"
    # backslash directly before a pipe inside a field
    assert solution.pack(["\\|"]) == "\\\\\\|"


def test_pack_mixed_example():
    assert solution.pack(["a|b", "c\\d"]) == "a\\|b|c\\\\d"


def test_unpack_simple():
    assert solution.unpack("name|value") == ["name", "value"]
    assert solution.unpack("a|b|c") == ["a", "b", "c"]


def test_unpack_empty_and_delims():
    assert solution.unpack("") == []
    assert solution.unpack("|") == ["", ""]
    assert solution.unpack("|x|") == ["", "x", ""]


def test_unpack_escaped():
    assert solution.unpack("a\\|b|c\\\\d") == ["a|b", "c\\d"]
    assert solution.unpack("\\\\") == ["\\"]


def test_unpack_general_escape_yields_next_char():
    # Per the format: a backslash consumes the next character literally, and in
    # general "\x" yields "x" -- for ANY x, not just backslash and pipe. A
    # well-formed frame may contain such sequences (the escape is a general
    # mechanism), so an unpacker must drop the backslash and keep the following
    # character regardless of what it is.
    assert solution.unpack("\\a") == ["a"]
    assert solution.unpack("\\x") == ["x"]
    assert solution.unpack("\\ ") == [" "]
    assert solution.unpack("\\1") == ["1"]
    # Mixed with real delimiters and other content.
    assert solution.unpack("a\\bc|d") == ["abc", "d"]
    assert solution.unpack("\\a|\\b") == ["a", "b"]
    # An escaped character sitting next to an unescaped delimiter.
    assert solution.unpack("x\\y|z") == ["xy", "z"]


def test_single_field_no_delim():
    assert solution.unpack("hello") == ["hello"]
    assert solution.pack(["hello"]) == "hello"


def test_roundtrip_nonempty_lists():
    rng = random.Random(38_38_38)
    alphabet = list("ab|\\ xY") + ["\\|", "||"]
    for _ in range(500):
        k = rng.randint(1, 6)
        fields = []
        for _ in range(k):
            flen = rng.randint(0, 8)
            fields.append("".join(rng.choice(alphabet) for _ in range(flen)))
        # The single-empty-field list [""] deliberately packs to "" and
        # unpacks to [] (documented asymmetry); skip that one collision so the
        # round-trip invariant is exercised on every list that must preserve.
        if fields == [""]:
            continue
        assert solution.unpack(solution.pack(fields)) == fields


def test_single_empty_field_collision():
    # documented behavior: [""] packs to "" and unpacks to []
    assert solution.pack([""]) == ""
    assert solution.unpack(solution.pack([""])) == []


def test_roundtrip_empty_list():
    # the empty list is the canonical thing that packs to "" and must round-trip
    assert solution.unpack(solution.pack([])) == []
