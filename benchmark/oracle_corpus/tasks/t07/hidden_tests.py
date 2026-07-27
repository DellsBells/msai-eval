import solution


def test_simple_split():
    assert solution.split_fields("a,b,c") == ["a", "b", "c"]


def test_quoted_delimiter_protected():
    assert solution.split_fields('foo,"bar,baz",qux') == ["foo", "bar,baz", "qux"]


def test_escaped_quotes():
    assert solution.split_fields('name,"say ""hi""",done') == [
        "name",
        'say "hi"',
        "done",
    ]


def test_escaped_quote_whole_field():
    # A field that is exactly a quoted "" pair -> one literal quote.
    assert solution.split_fields('a,"""",b') == ["a", '"', "b"]


def test_custom_delimiter():
    assert solution.split_fields("a;b;c", delimiter=";") == ["a", "b", "c"]
    assert solution.split_fields('x|"y|z"|w', delimiter="|") == ["x", "y|z", "w"]


def test_empty_line():
    assert solution.split_fields("") == [""]


def test_consecutive_delimiters():
    assert solution.split_fields(",,") == ["", "", ""]
    assert solution.split_fields("a,,b") == ["a", "", "b"]


def test_trailing_and_leading_delimiter():
    assert solution.split_fields("a,") == ["a", ""]
    assert solution.split_fields(",a") == ["", "a"]


def test_mid_field_quotes():
    # Quotes act as toggles even mid-field; content stitches together.
    assert solution.split_fields('ab"c,d"ef') == ["abc,def"]


def test_single_field_no_delimiter():
    assert solution.split_fields("hello world") == ["hello world"]


def test_whitespace_significant():
    assert solution.split_fields(" a , b ") == [" a ", " b "]


def test_delimiter_count_invariant():
    # Property: the number of fields equals (number of unquoted delimiters) + 1.
    import random

    rng = random.Random(2024)
    for _ in range(300):
        # Build a line from plain letters and unquoted commas only, so the
        # count of commas is exactly the count of separators.
        length = rng.randint(0, 12)
        chars = []
        commas = 0
        for _ in range(length):
            c = rng.choice("abc,de")
            if c == ",":
                commas += 1
            chars.append(c)
        line = "".join(chars)
        result = solution.split_fields(line)
        assert len(result) == commas + 1


def test_roundtrip_quote_encoding():
    # Property: encode arbitrary field lists by quoting each field and doubling
    # internal quotes; split_fields must recover the exact original fields.
    import random

    rng = random.Random(555)
    alphabet = 'ab, "xy'  # includes the delimiter and quote chars
    for _ in range(300):
        nfields = rng.randint(1, 5)
        fields = []
        for _ in range(nfields):
            flen = rng.randint(0, 6)
            fields.append("".join(rng.choice(alphabet) for _ in range(flen)))
        encoded = ",".join('"' + f.replace('"', '""') + '"' for f in fields)
        assert solution.split_fields(encoded) == fields
