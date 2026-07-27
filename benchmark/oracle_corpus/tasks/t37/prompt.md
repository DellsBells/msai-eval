# Threshold Run-Length Encoding

Implement two functions, `rle_encode(text)` and `rle_decode(code)`, that
compress and decompress ASCII strings using a **thresholded** run-length scheme.

## Encoding rules

A "run" is a maximal sequence of one or more identical characters. Scan the
input left to right and process each run as follows:

- If the run has length **4 or greater**, emit a *compressed token* with the
  shape `#<count>#<char>`: the marker character `#`, then the run length written
  in decimal, then a second `#` separator, then the single repeated character.
  For example a run of 5 `a`s becomes `#5#a`, and a run of 12 spaces becomes
  `#12# ` (the last character is the space).
- If the run has length **1, 2, or 3**, emit the characters *literally* (just
  the character repeated that many times), **except** that a literal `#` must be
  escaped by doubling it (each `#` becomes `##`). Any character other than `#`
  is emitted as-is even if it is a digit.

The input may contain any printable ASCII characters including digits and `#`.
A `#` participates in runs like any other character: a run of four or more `#`s
compresses the same way (four `#`s become `#4##` — marker, count `4`, separator
`#`, repeated char `#`), and a run of one/two/three `#`s is escaped by doubling
each one.

`rle_encode("")` returns `""`.

## Decoding rules

`rle_decode(code)` is the exact inverse of `rle_encode`. Scan left to right:

- A `#` immediately followed by another `#` is an escaped literal `#`
  (consume both characters, output one `#`).
- Otherwise a `#` begins a compressed token `#<count>#<char>`: read the decimal
  digits following the marker as the count (always at least one digit, and the
  count is always 4 or greater), then consume the separator `#`, then read the
  single character `<char>` after the separator and output it `count` times.
- Any other character is output literally.

`rle_decode("")` returns `""`.

You may assume `rle_decode` only ever receives strings produced by
`rle_encode` (well-formed input).

## Guarantee

For every input string `s`, `rle_decode(rle_encode(s)) == s`.

## Examples

```
rle_encode("aaaab")        -> "#4#ab"        # run of 4 a's -> "#4#a", then "b"
rle_encode("aaab")         -> "aaab"          # run of 3 stays literal
rle_encode("wwwwwwwwww")   -> "#10#w"         # length 10, multi-digit count

# worked-out mixed example:
rle_encode("xx###yyyy")    -> "xx#######4#y"
#   run "xx"   (len 2) -> "xx"
#   run "###"  (len 3) -> "######"   (each # doubled -> six '#')
#   run "yyyy" (len 4) -> "#4#y"
# result: "xx" + "######" + "#4#y" = "xx#######4#y"
#         (the six escaped '#' and the token's leading '#' sit adjacent,
#          giving seven consecutive '#' characters)
```

Round-trip:
```
rle_decode("#4#ab")       -> "aaaab"
rle_decode("aaab")        -> "aaab"
rle_decode("xx#######4#y") -> "xx###yyyy"
rle_decode("#10#w")       -> "wwwwwwwwww"
rle_decode("#4##")        -> "####"
```

## Constraints

- Input strings contain only printable ASCII (code points 32..126).
- Run lengths fit in a normal Python `int`.
- Both functions run in linear time in the size of their input.
