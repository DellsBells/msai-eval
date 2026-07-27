import solution

import random


def test_empty():
    assert solution.rle_encode("") == ""
    assert solution.rle_decode("") == ""


def test_short_runs_literal():
    # runs of length 1, 2, 3 stay literal
    assert solution.rle_encode("aaab") == "aaab"
    assert solution.rle_encode("ab") == "ab"
    assert solution.rle_encode("a") == "a"


def test_boundary_run_of_four_is_compressed():
    # exactly 4 must compress (this pins the >= 4 threshold)
    assert solution.rle_encode("aaaa") == "#4#a"
    assert solution.rle_encode("aaaab") == "#4#ab"


def test_run_of_three_not_compressed():
    assert solution.rle_encode("aaa") == "aaa"


def test_multi_digit_run():
    assert solution.rle_encode("w" * 10) == "#10#w"
    assert solution.rle_encode("z" * 123) == "#123#z"


def test_hash_escaping_literal():
    # 1..3 hashes are doubled
    assert solution.rle_encode("#") == "##"
    assert solution.rle_encode("##") == "####"
    assert solution.rle_encode("###") == "######"


def test_hash_run_compressed():
    # 4+ hashes compress with '#' as the repeated char
    assert solution.rle_encode("####") == "#4##"
    assert solution.rle_encode("#" * 7) == "#7##"


def test_mixed_worked_example():
    assert solution.rle_encode("xx###yyyy") == "xx#######4#y"


def test_digits_in_input():
    # short runs of digits stay literal
    assert solution.rle_encode("12a34") == "12a34"
    # a long run of a digit compresses; the separator disambiguates the count
    assert solution.rle_encode("5555") == "#4#5"
    # a compressed digit run immediately followed by a literal digit
    assert solution.rle_encode("11117") == "#4#17"


def test_space_run_compressed():
    assert solution.rle_encode(" " * 5) == "#5# "


def test_short_runs_literal_non_alpha_chars():
    # Runs of length 1..3 stay literal regardless of the character class:
    # spaces and digits must NOT be compressed at length 3 or below.
    assert solution.rle_encode(" ") == " "
    assert solution.rle_encode("  ") == "  "
    assert solution.rle_encode("   ") == "   "
    assert solution.rle_encode("2") == "2"
    assert solution.rle_encode("22") == "22"
    assert solution.rle_encode("222") == "222"


def test_decode_basic():
    assert solution.rle_decode("#4#ab") == "aaaab"
    assert solution.rle_decode("aaab") == "aaab"
    assert solution.rle_decode("xx#######4#y") == "xx###yyyy"
    assert solution.rle_decode("#10#w") == "w" * 10
    assert solution.rle_decode("##") == "#"
    assert solution.rle_decode("#4##") == "####"


def test_decode_multi_digit_count():
    # Counts with 3+ decimal digits must be parsed in full (not capped).
    assert solution.rle_decode("#123#z") == "z" * 123
    assert solution.rle_decode("#100#a") == "a" * 100
    assert solution.rle_decode("#250# ") == " " * 250
    # A big count immediately followed by a literal digit.
    assert solution.rle_decode("#123#z7") == "z" * 123 + "7"


def test_roundtrip_long_single_char_run():
    # Long runs force multi-digit (3+) counts through both directions.
    for ch in ("q", "#", " ", "5"):
        for length in (100, 123, 250, 999):
            s = ch * length
            enc = solution.rle_encode(s)
            assert solution.rle_decode(enc) == s


def test_roundtrip_property():
    rng = random.Random(20240704)
    alphabet = "ab#12 x"
    for _ in range(600):
        length = rng.randint(0, 40)
        s = "".join(rng.choice(alphabet) for _ in range(length))
        assert solution.rle_decode(solution.rle_encode(s)) == s
