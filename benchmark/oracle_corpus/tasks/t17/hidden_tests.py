import solution

import random


def test_balanced_simple():
    assert solution.find_fault("()") == -1
    assert solution.find_fault("[]") == -1
    assert solution.find_fault("{}") == -1


def test_empty_string():
    assert solution.find_fault("") == -1


def test_balanced_with_text_ignored():
    assert solution.find_fault("(a[b]c)") == -1
    assert solution.find_fault("{[()]}") == -1
    assert solution.find_fault("hello world") == -1


def test_no_brackets_at_all():
    # A string with zero bracket characters is trivially balanced.
    assert solution.find_fault("the quick brown fox") == -1
    assert solution.find_fault("x") == -1


def test_mismatched_closer():
    # ')' at index 4 mismatches the open '['.
    assert solution.find_fault("(a[b)c]") == 4
    # ']' immediately mismatches the open '('.
    assert solution.find_fault("(]") == 1


def test_stray_closer():
    assert solution.find_fault("ab)cd") == 2
    assert solution.find_fault(")") == 0
    assert solution.find_fault("()]") == 2


def test_unclosed_opener_innermost():
    # '(' at index 1 is the innermost never-closed opener.
    assert solution.find_fault("x(y[z]") == 1
    # single unclosed opener at index 0
    assert solution.find_fault("(") == 0


def test_unclosed_returns_innermost_not_outermost():
    # Two nested unclosed openers: '(' at 0 and '[' at 1. Innermost is '[' at 1.
    assert solution.find_fault("([") == 1
    # Three deep: innermost '{' is at index 2.
    assert solution.find_fault("([{") == 2
    # '(' opens at 0, then '[' opens and closes cleanly, ')' closes '(', then a
    # lone '{' opens at index 5 and stays open. Innermost unclosed is index 5.
    assert solution.find_fault("([])<{") == 5
    # Outer '(' at 0 stays open; inner '[]' closes; another '{' opens at 4.
    # still open at end: '(' idx0, '{' idx4 -> innermost is idx4.
    assert solution.find_fault("([]{") == 3


def test_midscan_fault_beats_end_fault():
    # A stray closer at index 1 is a fault even though an opener would also be
    # left unclosed; the mid-scan fault wins because it occurs earlier in scan.
    assert solution.find_fault("(]") == 1
    # Mismatch at index 3 must be reported, not the unclosed '(' at 0.
    assert solution.find_fault("([)") == 2


def test_duplicate_and_deep_nesting():
    assert solution.find_fault("(((((")==4
    assert solution.find_fault("((((()))))") == -1
    assert solution.find_fault("()()()()") == -1


def test_property_balanced_strings_return_minus_one():
    # Property: a string built by concatenating properly-nested random groups,
    # optionally interleaved with non-bracket filler, is always balanced.
    rng = random.Random(20240717)
    fillers = list("abcdefgXYZ 0123.!")

    def gen_balanced(depth):
        if depth <= 0:
            return "".join(rng.choice(fillers) for _ in range(rng.randint(0, 3)))
        pieces = []
        for _ in range(rng.randint(0, 3)):
            if rng.random() < 0.5:
                o, c = rng.choice([("(", ")"), ("[", "]"), ("{", "}")])
                pieces.append(o + gen_balanced(depth - 1) + c)
            else:
                pieces.append("".join(rng.choice(fillers)
                                      for _ in range(rng.randint(0, 2))))
        return "".join(pieces)

    for _ in range(300):
        s = gen_balanced(4)
        assert solution.find_fault(s) == -1


def test_property_single_stray_closer_is_located():
    # Property: take a balanced string and inject one stray closer at a known
    # position where nothing is open; the fault index must be that position.
    rng = random.Random(99)
    for _ in range(200):
        n = rng.randint(0, 6)
        balanced = "".join(rng.choice(["()", "[]", "{}", "z"]) for _ in range(n))
        stray = rng.choice([")", "]", "}"])
        s = stray + balanced  # stray at index 0, nothing open before it
        assert solution.find_fault(s) == 0
