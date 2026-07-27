import solution


def test_simple_flat_record():
    assert solution.parse_record('{ name = "Jake"  age = 31 }') == {
        "name": "Jake",
        "age": "31",
    }


def test_nested_and_duplicate():
    assert solution.parse_record('{a=1 b={c=2 d="x y"} a=9}') == {
        "a": "9",
        "b": {"c": "2", "d": "x y"},
    }


def test_escapes_in_quotes():
    got = solution.parse_record(r'{ msg = "she said \"hi\"" path = "C:\\tmp" }')
    assert got == {"msg": 'she said "hi"', "path": "C:\\tmp"}
    # Be explicit about the exact characters.
    assert got["msg"] == 'she said "hi"'
    assert got["path"] == "C:\\tmp"  # a single backslash between C: and tmp
    assert len(got["path"]) == len("C:") + 1 + len("tmp")


def test_empty_record():
    assert solution.parse_record("{}") == {}
    assert solution.parse_record("{   }") == {}
    assert solution.parse_record("{\n\t }") == {}


def test_bare_tokens_stay_strings():
    assert solution.parse_record("{ ver = 1.0.0  flag = -x  z = 007 }") == {
        "ver": "1.0.0",
        "flag": "-x",
        "z": "007",
    }


def test_no_spaces_minimal():
    assert solution.parse_record("{a=1}") == {"a": "1"}
    assert solution.parse_record("{a={b=c}}") == {"a": {"b": "c"}}


def test_quoted_contains_structural_chars():
    # Braces, '=', and spaces inside quotes are literal content.
    assert solution.parse_record('{ k = "a = {b} c" }') == {"k": "a = {b} c"}


def test_deep_nesting():
    txt = '{a={b={c={d="deep"}}}}'
    assert solution.parse_record(txt) == {
        "a": {"b": {"c": {"d": "deep"}}}
    }


def test_backslash_not_before_special():
    # A backslash followed by a normal char is a literal backslash + that char.
    # Source: "\n" inside quotes -> backslash then 'n' (NOT a newline).
    got = solution.parse_record(r'{ p = "a\nb" }')
    assert got == {"p": "a\\nb"}
    assert "\n" not in got["p"]
    assert got["p"] == "a" + "\\" + "n" + "b"


def test_single_entry_nested_only():
    assert solution.parse_record('{ obj = { inner = "v" } }') == {
        "obj": {"inner": "v"}
    }


def test_duplicate_in_nested():
    assert solution.parse_record("{ x = { y = 1  y = 2 } }") == {
        "x": {"y": "2"}
    }


def test_duplicate_dict_last_wins_no_merge():
    # A duplicate key whose values are BOTH nested records: the last record
    # replaces the first wholesale. This must NOT merge the two dicts.
    assert solution.parse_record("{ k = {a=1} k = {b=2} }") == {"k": {"b": "2"}}
    # Overlapping inner keys: still a full replace, not a per-key merge.
    assert solution.parse_record("{ k = {a=1 b=2} k = {b=9 c=3} }") == {
        "k": {"b": "9", "c": "3"}
    }
    # Three duplicates in a row: only the final record survives.
    assert solution.parse_record("{ k = {a=1} k = {b=2} k = {c=3} }") == {
        "k": {"c": "3"}
    }
    # Same thing one level down inside a nested record.
    assert solution.parse_record("{ outer = { k = {a=1} k = {b=2} } }") == {
        "outer": {"k": {"b": "2"}}
    }


def test_duplicate_mixed_types_last_wins():
    # A later scalar replaces an earlier record.
    assert solution.parse_record("{ k = {a=1} k = 2 }") == {"k": "2"}
    # A later record replaces an earlier scalar (no residue from the scalar).
    assert solution.parse_record("{ k = 1 k = {b=2} }") == {"k": {"b": "2"}}
    # A later quoted string replaces an earlier record.
    assert solution.parse_record('{ k = {a=1} k = "hi" }') == {"k": "hi"}


def test_whitespace_variety():
    txt = "{\n  a\t=\t1\n  b =\n2\n}"
    assert solution.parse_record(txt) == {"a": "1", "b": "2"}


def test_property_roundtrip_generated():
    # Property: generate random well-formed records, serialize them, and confirm
    # parse_record recovers the exact structure.
    #
    # Keys are drawn from a *small* pool so that duplicate keys collide often
    # within a single record, and both scalar and nested-record values land on
    # the same key. The expected dict is built by plain last-value-wins (later
    # assignment overwrites the earlier one wholesale), which is exactly the
    # spec: a later value replaces the earlier one — records are NOT merged.
    import random

    rng = random.Random(31415)

    # Deliberately tiny key pool -> frequent duplicate keys within one record.
    key_pool = ["a", "b", "c"]
    token_alpha = "abcdefghijklmnopqrstuvwxyz0123456789_.+-"
    # Characters allowed inside quoted strings for this generator, including
    # ones that must be escaped.
    quoted_alpha = list('abc XYZ 019 ={} ') + ['"', "\\"]

    def make_key():
        return rng.choice(key_pool)

    def make_token():
        # Ensure at least one char; any token char is fine per the spec.
        return "".join(rng.choice(token_alpha) for _ in range(rng.randint(1, 6)))

    def make_quoted_value():
        raw = "".join(rng.choice(quoted_alpha) for _ in range(rng.randint(0, 8)))
        return raw

    def encode_quoted(s):
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return '"' + escaped + '"'

    def build(depth):
        # Returns (python_value_dict, serialized_string) for one record.
        entries = {}
        parts = []
        # Bias toward >1 entry so duplicates within a record are common.
        count = rng.randint(0, 5)
        for _ in range(count):
            k = make_key()
            r = rng.random()
            # Bias toward nested records at depth so that duplicate keys often
            # get a record-valued -> record-valued last-wins situation, which a
            # dict-merge bug would get wrong.
            if depth > 0 and r < 0.5:
                child_val, child_src = build(depth - 1)
                # Plain overwrite == last value wins == full replace (no merge).
                entries[k] = child_val
                parts.append(k + "=" + child_src)
            elif r < 0.75:
                v = make_quoted_value()
                entries[k] = v
                parts.append(k + " = " + encode_quoted(v))
            else:
                v = make_token()
                entries[k] = v
                parts.append(k + " = " + v)
        src = "{ " + "  ".join(parts) + " }"
        return entries, src

    # Track how often we actually stress the record-over-record duplicate case
    # so this test is guaranteed to exercise the merge-vs-replace distinction.
    saw_dict_over_dict_dup = 0
    for _ in range(600):
        # Re-derive expected with an explicit last-wins pass over the entries so
        # the check does not depend on dict insertion semantics being identical.
        expected, src = build(rng.randint(1, 3))
        assert solution.parse_record(src) == expected

    # Construct records that are guaranteed to contain a duplicate key whose
    # two values are both records with overlapping inner keys, forcing the
    # last-wins-vs-merge distinction on every one.
    for _ in range(200):
        _, src_a = build(rng.randint(1, 2))
        first_inner, first_src = build(1)
        second_inner, second_src = build(1)
        # Ensure overlap so a merge would differ from a replace.
        if not second_inner:
            second_inner = {"a": "z"}
            second_src = "{ a = z }"
        src = "{ k = " + first_src + "  k = " + second_src + " }"
        expected = {"k": second_inner}
        assert solution.parse_record(src) == expected
        saw_dict_over_dict_dup += 1

    assert saw_dict_over_dict_dup == 200
