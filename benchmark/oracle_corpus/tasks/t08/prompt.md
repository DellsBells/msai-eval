# Parse a nested brace-record mini-format

Write a function:

```python
def parse_record(text: str) -> dict:
    ...
```

that parses a small nested key-value record language into nested Python
dictionaries.

## The language

A **record** is a brace-delimited list of entries:

```
{ key = value  key = value  ... }
```

- The whole input is exactly one record. The outermost `{ ... }` is present.
- Inside a record, each entry is `key = value`.
- Entries are separated by whitespace (spaces, tabs, newlines). There is **no**
  comma between entries. Whitespace around `{`, `}`, `=`, and between entries
  is insignificant and may be any amount (including none where the grammar
  still parses, e.g. `{a=1}`).

### Keys

A **key** is a run of one or more characters from `[A-Za-z0-9_]` (letters,
digits, underscore). Keys are used verbatim as dictionary keys.

### Values

A value is exactly one of three things:

1. **A nested record** — another `{ ... }`, parsed recursively into a nested
   `dict`.

2. **A quoted string** — text enclosed in double quotes `"..."`. Inside a
   quoted string, a backslash escape is supported: `\"` denotes a literal
   double quote and `\\` denotes a literal backslash. No other escapes exist;
   a backslash followed by any other character is a literal backslash followed
   by that character (so `\n` inside quotes is the two characters backslash and
   `n`, **not** a newline). The result value is a Python `str` with the quotes
   removed and escapes resolved. A quoted string may contain spaces, `=`, `{`,
   `}`, and other characters with no special meaning.

3. **A bare token** — a run of one or more characters from `[A-Za-z0-9_.+-]`
   (letters, digits, underscore, dot, plus, minus). A bare token's value is
   returned as a `str` exactly as written (no numeric conversion — `007` stays
   `"007"`, `1.5` stays `"1.5"`).

### Duplicate keys

If the same key appears more than once **within the same record**, the **last**
value wins — the earlier value is discarded entirely and the key maps to
exactly the last value, regardless of the types involved.

This is a plain replacement, **not** a merge. In particular, when two duplicate
entries for the same key are both nested records, the later record **replaces**
the earlier one wholesale; their keys are **not** combined. For example, in
`{ k={a=1} k={b=2} }` the key `k` maps to `{"b": "2"}` only — the `a` entry from
the first record is gone, and the result is **not** `{"a": "1", "b": "2"}`.
Likewise a later scalar replaces an earlier record and a later record replaces
an earlier scalar.

### Empty record

`{}` (with optional inner whitespace, e.g. `{   }`) parses to an empty dict
`{}`.

## Return value

A `dict` mapping each key (`str`) to its value, where a value is either a `str`
(from a quoted string or bare token) or a nested `dict` (from a nested record).

## Worked examples

```python
parse_record('{ name = "Jake"  age = 31 }')
# {"name": "Jake", "age": "31"}

parse_record('{a=1 b={c=2 d="x y"} a=9}')
# {"a": "9", "b": {"c": "2", "d": "x y"}}

parse_record(r'{ msg = "she said \"hi\"" path = "C:\\tmp" }')
# {"msg": 'she said "hi"', "path": "C:\\tmp"}
#   i.e. msg  -> she said "hi"
#        path -> C:\tmp

parse_record('{}')
# {}

parse_record('{ ver = 1.0.0  flag = -x }')
# {"ver": "1.0.0", "flag": "-x"}

parse_record('{ k = {a=1}  k = {b=2} }')
# {"k": {"b": "2"}}
#   last value wins: the second record replaces the first, NOT a merge.
#   It is NOT {"k": {"a": "1", "b": "2"}}.
```

(The last example note: in `path = "C:\\tmp"` the source has two backslashes
inside the quotes, which resolve to a single backslash, so the value is the
string `C:\tmp`.)

## Guarantees about input

You may assume the input is **well-formed**: it is exactly one record, braces
are balanced, every entry has the shape `key = value`, quoted strings are
properly terminated, and there is no trailing junk after the final `}`. You do
**not** need to detect or report syntax errors.

## Constraints

- `text` is a `str`.
- Use only the Python standard library.
- Values are never numerically converted; all leaf values are `str`.
