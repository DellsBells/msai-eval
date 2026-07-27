# Escaped Field Framing

You are implementing a tiny wire format that packs a list of string *fields*
into one flat string and unpacks it back. Fields may contain **any** characters,
including the delimiter and the escape character, so the format uses escaping to
stay unambiguous.

Implement two functions:

```python
def pack(fields):    # fields: list[str]  -> str
def unpack(frame):   # frame: str         -> list[str]
```

## The format

- The **delimiter** between fields is the pipe character `|`.
- The **escape** character is the backslash `\`.
- Inside a field, when writing it out, every backslash is written as `\\`
  (two characters) and every pipe is written as `\|` (two characters). All other
  characters are written unchanged.
- `pack` joins the escaped fields with a single unescaped `|` between
  consecutive fields.

So `pack(["a", "b"])` is `"a|b"`, and a field that itself contains a pipe, like
`"a|b"`, is escaped to `"a\|b"` before joining.

## `pack` details

- `pack([])` returns the empty string `""`.
- `pack([""])` (a list with one empty field) returns `""` as well — a single
  empty field packs to the empty string.
- `pack(["", ""])` (two empty fields) returns `"|"` — the delimiter with empty
  fields on both sides.
- Fields are never `None`; they are always strings (possibly empty).

## `unpack` details

`unpack` is the inverse of `pack` on every well-formed frame. Scan the frame
left to right:

- A backslash consumes the **next** character literally: `\\` yields a single
  `\`, `\|` yields a single `|`, and in general `\x` yields `x`. (You may assume
  a backslash is always followed by another character in well-formed frames.)
- An **unescaped** `|` ends the current field and starts a new one.
- Every other character is appended to the current field.

Special cases that mirror `pack`:

- `unpack("")` returns `[]` (the empty list), **not** `[""]`.
- `unpack("|")` returns `["", ""]`.
- A frame that is a single non-empty field with no unescaped delimiter unpacks
  to a one-element list.

## Round-trip guarantee

For every list of strings `fields`, `unpack(pack(fields)) == fields`.
(Note the asymmetry at the empty boundary: `pack([]) == pack([""]) == ""`, and
`unpack("") == []`. This is intentional — the round-trip holds because the only
list that packs to `""` and must round-trip is `[]`; a caller who packs `[""]`
and unpacks gets `[]`. Your `unpack` must return `[]` for the empty frame.)

## Examples

```
pack(["name", "value"])        -> "name|value"
pack(["a|b", "c\\d"])          -> "a\\|b|c\\\\d"
#   field "a|b"  -> "a\|b"
#   field "c\d"  -> "c\\d"
#   joined       -> "a\|b|c\\d"   (shown above with Python string escaping)
pack(["", "x", ""])            -> "|x|"
pack([])                       -> ""

unpack("name|value")           -> ["name", "value"]
unpack("a\\|b|c\\\\d")         -> ["a|b", "c\\d"]
unpack("|x|")                  -> ["", "x", ""]
unpack("")                     -> []
```

## Constraints

- Fields contain arbitrary characters (any Unicode code points).
- `pack` and `unpack` run in linear time in their total input size.
- Use only the Python standard library.
