# Two-Tier Run-Length Codec

Implement a byte-oriented run-length codec with a compact **two-tier** length
field. All data is `bytes`. Implement:

```python
def encode(data):   # data: bytes  -> bytes
def decode(blob):   # blob: bytes  -> bytes
```

## Concept

The encoder splits `data` into maximal runs of identical bytes (a "run" is a run
of the same byte value repeated one or more times) and emits one **token** per
run, left to right. Each token encodes a run length and the repeated byte using
a length field that is either 1 or 2 bytes, chosen by the run length.

## Token format

Let `L` be the run length (`L >= 1`) and `v` be the repeated byte value
(`0 <= v <= 255`). A run can be at most `32767` bytes long; runs longer than that
must be **split** into consecutive tokens (see below).

- **Short token** — used when `1 <= L <= 127`. Two bytes:
  - byte 0: `L` (the high bit is 0, so `L` fits directly since `L <= 127`)
  - byte 1: `v`
- **Long token** — used when `128 <= L <= 32767`. Three bytes:
  - byte 0: `0x80 | (L >> 8)` — the high bit is set, the low 7 bits hold the
    high 7 bits of `L` (since `L <= 32767`, `L >> 8 <= 127`)
  - byte 1: `L & 0xFF` — the low 8 bits of `L`
  - byte 2: `v`

So the high bit of the **first** byte of every token tells the decoder whether
the token is short (bit clear → 2 bytes total) or long (bit set → 3 bytes total).

### Splitting long runs

The encoder must use the **shortest** encoding for each run length:

- A run of length `L` with `L <= 127` is emitted as exactly one short token.
- A run of length `L` with `128 <= L <= 32767` is emitted as exactly one long
  token.
- A run of length `L > 32767` is emitted as consecutive tokens: repeatedly emit
  a long token of length `32767` until the remaining length is `<= 32767`, then
  emit the remaining length as a single token (short if that remainder
  `<= 127`, otherwise long). The remainder is never zero (a run length that is
  an exact multiple of `32767` leaves a final chunk of `32767`, emitted as a
  long token — you never emit a zero-length token).

## `encode(data)`

- `encode(b"")` returns `b""`.
- Otherwise return the concatenation of the tokens for each run, in order.

## `decode(blob)`

`decode` is the inverse of `encode` on any bytes it produces (and on any
concatenation of valid tokens). Read tokens left to right:

- Read the first byte `h`. If `h < 128` it is a short token: the run length is
  `h`, the next byte is the repeated value; output that value `h` times and
  advance 2 bytes.
- If `h >= 128` it is a long token: the run length is
  `((h & 0x7F) << 8) | blob[i+1]`, `blob[i+2]` is the repeated value; output that
  value that many times and advance 3 bytes.
- `decode(b"")` returns `b""`.

You may assume `decode` only receives well-formed input (a whole number of
complete tokens; short tokens never carry a length of 0).

## Round-trip guarantee

For every `data`, `decode(encode(data)) == data`.

Note that `encode` may split a long run into several tokens, so `decode` can see
two adjacent tokens with the **same** byte value; it simply concatenates their
output. `encode` is deterministic and always chooses the shortest length field
per (possibly split) chunk as described.

## Examples

```
encode(b"")                    -> b""
encode(b"AAAB")                -> b"\x03A\x01B"
#   run of 3 'A' (0x41): short token 0x03,0x41
#   run of 1 'B' (0x42): short token 0x01,0x42

encode(b"\x00" * 200)          -> b"\x80\xc8\x00"
#   L = 200 -> long token: 0x80 | (200>>8=0) = 0x80, then 200 & 0xFF = 0xc8, then value 0x00

encode(b"Z" * 127)             -> b"\x7fZ"          # 127 is still a short token
encode(b"Z" * 128)             -> b"\x80\x80Z"      # 128 tips into a long token

decode(b"\x03A\x01B")          -> b"AAAB"
decode(b"\x80\xc8\x00")        -> b"\x00" * 200
```

## Constraints

- Inputs are arbitrary `bytes` (byte values 0..255), any length.
- `encode` and `decode` run in linear time in their output size.
- Return `bytes` objects.
- Standard library only.
