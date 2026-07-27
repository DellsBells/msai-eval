import solution

import random


def test_empty():
    assert solution.encode(b"") == b""
    assert solution.decode(b"") == b""


def test_short_tokens_basic():
    assert solution.encode(b"AAAB") == b"\x03A\x01B"
    assert solution.encode(b"A") == b"\x01A"
    assert solution.encode(b"ABC") == b"\x01A\x01B\x01C"


def test_short_boundary_127():
    assert solution.encode(b"Z" * 127) == b"\x7fZ"


def test_long_boundary_128():
    # 128 must tip into a long token (this is the off-by-one boundary)
    assert solution.encode(b"Z" * 128) == b"\x80\x80Z"


def test_long_token_example():
    assert solution.encode(b"\x00" * 200) == b"\x80\xc8\x00"


def test_long_token_max_single():
    # 32767 is the largest single long token
    enc = solution.encode(b"\x41" * 32767)
    assert enc == b"\xff\xffA"
    assert len(enc) == 3


def test_split_over_max_run():
    # 32768 = 32767 + 1 -> a max long token then a short token of length 1
    enc = solution.encode(b"\x42" * 32768)
    assert enc == b"\xff\xffB" + b"\x01B"


def test_split_exact_multiple():
    # 65534 = 2 * 32767 -> two max long tokens, no zero-length final token
    enc = solution.encode(b"\x43" * (2 * 32767))
    assert enc == b"\xff\xffC" + b"\xff\xffC"


def test_decode_basic():
    assert solution.decode(b"\x03A\x01B") == b"AAAB"
    assert solution.decode(b"\x80\xc8\x00") == b"\x00" * 200
    assert solution.decode(b"\x7fZ") == b"Z" * 127
    assert solution.decode(b"\x80\x80Z") == b"Z" * 128


def test_decode_adjacent_same_value_tokens():
    # two adjacent tokens with the same value simply concatenate
    assert solution.decode(b"\x02A\x03A") == b"AAAAA"


def test_all_byte_values_single():
    # a single occurrence of every byte value 0..255
    data = bytes(range(256))
    assert solution.decode(solution.encode(data)) == data


def test_roundtrip_random_payloads():
    rng = random.Random(0x40_40_40)
    alphabet = [0, 1, 65, 128, 200, 255]
    for _ in range(400):
        length = rng.randint(0, 60)
        # build with runs so we exercise both short and long-ish patterns
        data = bytearray()
        while len(data) < length:
            v = rng.choice(alphabet)
            run = rng.randint(1, 10)
            data.extend([v] * run)
        data = bytes(data[:length])
        assert solution.decode(solution.encode(data)) == data


def test_roundtrip_big_runs():
    rng = random.Random(4004)
    for _ in range(60):
        v = rng.randint(0, 255)
        run = rng.randint(1, 70000)  # exercises splitting across MAX_RUN
        data = bytes([v]) * run
        assert solution.decode(solution.encode(data)) == data
