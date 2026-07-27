import solution


def test_basic_pairs():
    assert solution.parse_settings("host=localhost;port=8080;debug=true") == {
        "host": "localhost",
        "port": "8080",
        "debug": "true",
    }


def test_empty_input():
    assert solution.parse_settings("") == {}


def test_only_semicolons():
    assert solution.parse_settings(";;;") == {}


def test_value_contains_equals():
    # Only the first '=' splits; the rest belongs to the value.
    assert solution.parse_settings("path=/a=b") == {"path": "/a=b"}
    assert solution.parse_settings("q=a=b=c") == {"q": "a=b=c"}


def test_trimming_spaces_only():
    assert solution.parse_settings("  name = Jake ") == {"name": "Jake"}
    # Tabs and newlines are NOT stripped.
    got = solution.parse_settings("\tk\t=\tv\t")
    assert got == {"\tk\t": "\tv\t"}


def test_skip_empty_and_missing_equals():
    assert solution.parse_settings("a=1;;b=2") == {"a": "1", "b": "2"}
    assert solution.parse_settings("path=/a=b;empty=;justakey;=orphan") == {
        "path": "/a=b",
        "empty": "",
    }


def test_empty_value_allowed():
    assert solution.parse_settings("k=") == {"k": ""}
    assert solution.parse_settings("k=   ") == {"k": ""}


def test_empty_key_skipped():
    assert solution.parse_settings("=value") == {}
    assert solution.parse_settings("   =value") == {}


def test_duplicate_last_wins():
    assert solution.parse_settings("role=admin;role=owner") == {"role": "owner"}
    assert solution.parse_settings("x=1;x=2;x=3") == {"x": "3"}


def test_single_pair():
    assert solution.parse_settings("only=one") == {"only": "one"}


def test_worked_example_two():
    assert solution.parse_settings("  name = Jake ;; role=admin ; role = owner ") == {
        "name": "Jake",
        "role": "owner",
    }


def test_property_roundtrip_no_special_chars():
    # Property: for keys/values built from a safe alphabet (no ';', '=', or
    # leading/trailing spaces), serializing and re-parsing recovers the dict.
    import random

    rng = random.Random(1234)
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOP0123456789"
    for _ in range(200):
        n = rng.randint(1, 6)
        d = {}
        for _ in range(n):
            klen = rng.randint(1, 5)
            vlen = rng.randint(0, 5)
            key = "".join(rng.choice(alphabet) for _ in range(klen))
            val = "".join(rng.choice(alphabet) for _ in range(vlen))
            d[key] = val
        serialized = ";".join(f"{k}={v}" for k, v in d.items())
        assert solution.parse_settings(serialized) == d
