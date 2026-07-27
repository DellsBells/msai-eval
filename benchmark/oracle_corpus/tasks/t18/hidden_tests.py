import solution

import random


def test_basic_append():
    assert solution.run_editor(["APPEND:hello", "APPEND: world"]) == "hello world"


def test_empty_command_list():
    assert solution.run_editor([]) == ""


def test_append_empty_payload():
    assert solution.run_editor(["APPEND:", "APPEND:x"]) == "x"


def test_first_colon_only_splits():
    assert solution.run_editor(["APPEND:hi:there"]) == "hi:there"
    assert solution.run_editor(["APPEND::"]) == ":"


def test_backspace_basic():
    assert solution.run_editor(["APPEND:abcdef", "BACKSPACE:2"]) == "abcd"


def test_backspace_zero_is_noop_edit():
    # BACKSPACE:0 removes nothing but is still an editing command.
    assert solution.run_editor(["APPEND:abc", "BACKSPACE:0"]) == "abc"


def test_backspace_overflow_clears_buffer():
    assert solution.run_editor(["APPEND:ab", "BACKSPACE:9"]) == ""
    # exactly buffer length also clears
    assert solution.run_editor(["APPEND:abc", "BACKSPACE:3"]) == ""


def test_undo_reverts_backspace():
    assert solution.run_editor(["APPEND:abc", "BACKSPACE:2", "UNDO"]) == "abc"


def test_undo_then_redo_restores_edit():
    # This is the case the wrong-snapshot bug fails.
    assert solution.run_editor(["APPEND:a", "APPEND:b", "UNDO", "REDO"]) == "ab"


def test_single_edit_undo_redo_roundtrip():
    assert solution.run_editor(["APPEND:xyz", "UNDO"]) == ""
    assert solution.run_editor(["APPEND:xyz", "UNDO", "REDO"]) == "xyz"


def test_edit_clears_redo():
    # UNDO 'x' -> ""; APPEND 'y' -> "y" and clears redo; REDO is a no-op.
    assert solution.run_editor(["APPEND:x", "UNDO", "APPEND:y", "REDO"]) == "y"


def test_leading_undo_redo_are_noops():
    assert solution.run_editor(["UNDO", "REDO", "APPEND:hi:there"]) == "hi:there"


def test_empty_undo_does_not_touch_redo():
    # Build a redo entry, then issue an UNDO with an empty undo stack; it must
    # NOT clear the redo stack, so the following REDO still works.
    # sequence: APPEND a -> "a"; UNDO -> "" (redo has one entry, undo now empty);
    # UNDO again -> no-op (undo empty), must leave redo intact;
    # REDO -> "a"
    assert solution.run_editor(["APPEND:a", "UNDO", "UNDO", "REDO"]) == "a"


def test_multi_level_undo_redo():
    cmds = ["APPEND:a", "APPEND:b", "APPEND:c", "UNDO", "UNDO", "REDO"]
    # "a","ab","abc"; UNDO->"ab"; UNDO->"a"; REDO->"ab"
    assert solution.run_editor(cmds) == "ab"


def test_redo_chain_after_two_undos():
    cmds = ["APPEND:1", "APPEND:2", "APPEND:3", "UNDO", "UNDO", "REDO", "REDO"]
    # after both redos, back to "123"
    assert solution.run_editor(cmds) == "123"


def _reference_model(commands):
    # Independent, straightforward re-implementation used only as an oracle for
    # the property test below.
    buf = ""
    undo = []
    redo = []
    for cmd in commands:
        if cmd == "UNDO":
            if undo:
                prev = undo.pop()
                redo.append(buf)
                buf = prev
        elif cmd == "REDO":
            if redo:
                nxt = redo.pop()
                undo.append(buf)
                buf = nxt
        else:
            verb, _, payload = cmd.partition(":")
            undo.append(buf)
            redo.clear()
            if verb == "APPEND":
                buf = buf + payload
            else:  # BACKSPACE
                n = int(payload)
                buf = "" if n >= len(buf) else buf[:len(buf) - n]
    return buf


def test_property_matches_model_over_random_logs():
    rng = random.Random(1234567)
    alphabet = "abcXY_"
    for _ in range(400):
        length = rng.randint(0, 14)
        cmds = []
        for _ in range(length):
            choice = rng.random()
            if choice < 0.45:
                payload = "".join(rng.choice(alphabet)
                                  for _ in range(rng.randint(0, 3)))
                cmds.append("APPEND:" + payload)
            elif choice < 0.65:
                cmds.append("BACKSPACE:" + str(rng.randint(0, 4)))
            elif choice < 0.83:
                cmds.append("UNDO")
            else:
                cmds.append("REDO")
        assert solution.run_editor(cmds) == _reference_model(cmds)
