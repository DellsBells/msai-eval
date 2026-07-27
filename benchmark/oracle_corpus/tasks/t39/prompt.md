# Byte-Stuffed Frame Splitter

You are implementing a byte-stuffing framing layer for a serial protocol. The
layer marks frame boundaries with a special flag byte and escapes any occurrence
of the flag (or the escape byte) that appears inside a payload, so the flag byte
is guaranteed to appear only at real boundaries.

All data is `bytes`. Implement three functions:

```python
def frame(payload):          # payload: bytes -> bytes   (one framed frame)
def deframe(stream):         # stream: bytes  -> list[bytes]  (all payloads)
def stuff(payload):          # payload: bytes -> bytes   (body escaping only)
```

## Byte values

- `FLAG = 0x7E` — marks the end of a frame.
- `ESC  = 0x7D` — the escape byte.
- `ESC_FLAG = 0x5E` and `ESC_ESC = 0x5D` — escape substitutes.

## `stuff(payload)` — body escaping

`stuff` transforms a payload into its escaped body (no flag bytes added). Scan
the payload byte by byte:

- A `FLAG` byte (`0x7E`) is replaced by the two bytes `ESC, ESC_FLAG`
  (`0x7D, 0x5E`).
- An `ESC` byte (`0x7D`) is replaced by the two bytes `ESC, ESC_ESC`
  (`0x7D, 0x5D`).
- Every other byte is copied unchanged.

After stuffing, the resulting body contains no `FLAG` bytes.

## `frame(payload)` — one frame

`frame(payload)` returns `stuff(payload)` followed by a single trailing `FLAG`
byte. There is **no** leading flag. Thus every frame ends with exactly one
`0x7E`, and `frame(b"")` returns `b"\x7e"` (just the flag).

## `deframe(stream)` — split a stream into payloads

`deframe` takes a byte stream that is the concatenation of zero or more frames
and returns the list of decoded payloads (with escaping undone).

Rules:

- Split the stream on `FLAG` bytes. Each maximal run of bytes **between** flags
  (and before the first flag) is one frame body; unescape it to recover the
  payload.
- Unescaping reverses `stuff`: the two-byte sequence `ESC, ESC_FLAG` becomes a
  single `FLAG`; `ESC, ESC_ESC` becomes a single `ESC`. (You may assume every
  `ESC` byte in a well-formed body is immediately followed by `ESC_FLAG` or
  `ESC_ESC`.)
- Only **complete** frames count: a frame body is complete when it is terminated
  by a `FLAG` byte. Any trailing bytes after the last `FLAG` (a partial frame
  with no terminating flag) are **discarded**.
- An empty body (two consecutive `FLAG` bytes, or a leading `FLAG`) decodes to
  an empty payload `b""` and **is** included in the result.
- `deframe(b"")` returns `[]`.

## Examples

```
stuff(b"AB")             -> b"AB"
stuff(b"\x7e")           -> b"\x7d\x5e"          # a lone FLAG in the body
stuff(b"\x7d")           -> b"\x7d\x5d"          # a lone ESC in the body

frame(b"AB")             -> b"AB\x7e"
frame(b"")               -> b"\x7e"
frame(b"\x7e\x7d")       -> b"\x7d\x5e\x7d\x5d\x7e"

deframe(b"AB\x7eCD\x7e")             -> [b"AB", b"CD"]
deframe(b"AB\x7e")                   -> [b"AB"]
deframe(b"\x7e\x7e")                 -> [b"", b""]      # two empty frames
deframe(b"AB\x7eCD")                 -> [b"AB"]         # "CD" has no flag -> dropped
deframe(b"")                         -> []
deframe(b"\x7d\x5e\x7e")             -> [b"\x7e"]       # escaped flag in payload
```

## Round-trip guarantee

For any list of payloads `ps`, joining their frames and deframing recovers them:
`deframe(b"".join(frame(p) for p in ps)) == ps`.

## Constraints

- Inputs are arbitrary `bytes` (byte values 0..255).
- All three functions run in linear time in their input size.
- Return `bytes` objects (not `bytearray`) from `frame` and `stuff`, and a list
  of `bytes` from `deframe`.
- Standard library only.
