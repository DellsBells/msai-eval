import solution

import random


def test_stuff_plain():
    assert solution.stuff(b"AB") == b"AB"
    assert solution.stuff(b"") == b""


def test_stuff_escapes():
    assert solution.stuff(b"\x7e") == b"\x7d\x5e"
    assert solution.stuff(b"\x7d") == b"\x7d\x5d"
    assert solution.stuff(b"\x7e\x7d") == b"\x7d\x5e\x7d\x5d"
    # stuffed body never contains a raw FLAG
    assert b"\x7e" not in solution.stuff(b"\x7e\x7e\x7d\x00\x7e")


def test_frame_basic():
    assert solution.frame(b"AB") == b"AB\x7e"
    assert solution.frame(b"") == b"\x7e"
    assert solution.frame(b"\x7e\x7d") == b"\x7d\x5e\x7d\x5d\x7e"


def test_frame_returns_bytes_type():
    assert type(solution.frame(b"AB")) is bytes
    assert type(solution.stuff(b"AB")) is bytes


def test_deframe_returns_bytes_elements():
    # deframe must return a list whose elements are bytes, not bytearray.
    result = solution.deframe(b"AB\x7e\x7d\x5e\x7e\x7e")
    assert type(result) is list
    assert result == [b"AB", b"\x7e", b""]
    for element in result:
        assert type(element) is bytes


def test_deframe_simple():
    assert solution.deframe(b"AB\x7eCD\x7e") == [b"AB", b"CD"]
    assert solution.deframe(b"AB\x7e") == [b"AB"]


def test_deframe_empty_stream():
    assert solution.deframe(b"") == []


def test_deframe_empty_frames():
    assert solution.deframe(b"\x7e") == [b""]
    assert solution.deframe(b"\x7e\x7e") == [b"", b""]
    assert solution.deframe(b"\x7e\x7e\x7e") == [b"", b"", b""]


def test_deframe_drops_partial_trailing():
    # "CD" after the last FLAG has no terminating flag -> dropped
    assert solution.deframe(b"AB\x7eCD") == [b"AB"]
    # a lone partial frame with no flag at all -> empty result
    assert solution.deframe(b"XYZ") == []


def test_deframe_unescapes():
    assert solution.deframe(b"\x7d\x5e\x7e") == [b"\x7e"]
    assert solution.deframe(b"\x7d\x5d\x7e") == [b"\x7d"]
    # an empty frame followed by a payload
    assert solution.deframe(b"\x7eAB\x7e") == [b"", b"AB"]


def test_roundtrip_list_of_payloads():
    rng = random.Random(0x39_39)
    for _ in range(400):
        m = rng.randint(0, 5)
        payloads = []
        for _ in range(m):
            plen = rng.randint(0, 10)
            payloads.append(bytes(rng.randint(0, 255) for _ in range(plen)))
        stream = b"".join(solution.frame(p) for p in payloads)
        assert solution.deframe(stream) == payloads


def test_roundtrip_single_frame_property():
    # a single frame always deframes to exactly its one payload
    rng = random.Random(9999)
    for _ in range(300):
        plen = rng.randint(0, 20)
        p = bytes(rng.randint(0, 255) for _ in range(plen))
        assert solution.deframe(solution.frame(p)) == [p]
