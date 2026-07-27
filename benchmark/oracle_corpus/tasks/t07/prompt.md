# Split a delimited line with quoted fields

Write a function:

```python
def split_fields(line: str, delimiter: str = ",") -> list:
    ...
```

that splits a single line into a list of field strings, honoring
double-quoted fields that may themselves contain the delimiter.

## Behavior

Scan `line` left to right, character by character, building up fields. The
`delimiter` is always a single character (default a comma). Rules:

1. **Unquoted delimiter.** A `delimiter` character encountered outside of
   quotes ends the current field and starts a new one.

2. **Quoting.** A double-quote character `"` toggles "inside quotes" mode.
   While inside quotes, a `delimiter` character is treated as ordinary field
   content, not a separator. The quote characters themselves are **not**
   included in the field's value.

3. **Escaped quote.** Inside a quoted region, two consecutive double-quotes
   (`""`) represent a single literal `"` character in the field value, and do
   **not** end the quoted region. This is the standard CSV escaping
   convention. Example: the field text `"she said ""hi"""` yields the value
   `she said "hi"`.

4. **Fields need not be fully quoted.** Quotes may appear in the middle of an
   otherwise unquoted field, and text may follow a closing quote. Treat quotes
   purely as toggles as you scan; concatenate everything that is not a
   structural quote or an unquoted delimiter. Example: `ab"c,d"ef` is a single
   field with value `abc,def` (the quotes toggle protection around `c,d`).

5. **Empty fields.** Consecutive delimiters produce empty-string fields.
   A trailing delimiter produces a trailing empty field.

6. **The empty line.** `split_fields("")` returns `[""]` (one empty field),
   consistent with the rule that N delimiters always yield N+1 fields.

7. **Whitespace is significant.** Do not trim spaces. Spaces are ordinary
   characters.

You may assume the input is well-formed in the sense that every quoted region
is properly closed (quote toggles come in matching pairs once `""` escapes are
accounted for). You do not need to raise errors for malformed input.

## Examples

```python
split_fields("a,b,c")
# ["a", "b", "c"]

split_fields('foo,"bar,baz",qux')
# ["foo", "bar,baz", "qux"]

split_fields('name,"say ""hi""",done')
# ["name", 'say "hi"', "done"]

split_fields("a;b;c", delimiter=";")
# ["a", "b", "c"]

split_fields(",,")
# ["", "", ""]

split_fields("")
# [""]
```

## Constraints

- `line` is a `str`. `delimiter` is a single-character `str` that is never `"`.
- Return a `list` of `str`.
- Use only the Python standard library. (Do **not** rely on the `csv` module;
  implement the scan yourself so the escaped-quote and mid-field-quote rules
  behave exactly as specified above.)
