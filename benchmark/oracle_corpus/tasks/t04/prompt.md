# Identifier Canonicalizer (to snake_case)

Programmers write the same identifier many ways: `getHTTPResponseCode`,
`get_http_response_code`, `Get-HTTP-Response-Code`. Write a function
`to_snake(identifier: str) -> str` that reduces any such identifier to a single canonical
`snake_case` form, so that different spellings of the same identifier collapse to one
string.

## Step 1: Split into words

Scan the input left to right and break it into a list of **words** using these rules. A
character is a **separator** if it is an underscore (`_`), a hyphen (`-`), or a space
(` `). Separators never appear in any word; they only mark boundaries. In addition, word
boundaries are inserted *between* adjacent non-separator characters at these transitions:

1. **lower-to-upper**: a lowercase letter or digit immediately followed by an uppercase
   letter starts a new word. (e.g. `getName` -> `get`, `Name`)
2. **acronym-to-word**: a run of two or more uppercase letters immediately followed by a
   lowercase letter is split so that the *last* uppercase letter begins the new word.
   (e.g. `HTTPResponse` -> `HTTP`, `Response`; `JSONData` -> `JSON`, `Data`)

No boundary is inserted between a letter and a digit, or between two digits, except where
rule 1 applies (a digit followed by an uppercase letter). So `utf8` is one word, `v2` is
one word, and `x2Y` splits into `x2`, `Y`.

Runs of separators, and leading/trailing separators, produce no empty words — empty words
are discarded.

## Step 2: Lowercase and join

Lowercase every word (all letters to lowercase; digits unchanged) and join the resulting
words with single underscores (`_`).

## Result properties

- The output contains only lowercase ASCII letters, digits, and underscores.
- The output has no leading, trailing, or consecutive underscores.
- An input that contains no word characters (empty, or only separators) yields `""`.
- The function is **idempotent**: `to_snake(to_snake(x)) == to_snake(x)` for every input.

## Examples

```
to_snake("getHTTPResponseCode")   -> "get_http_response_code"
to_snake("Get-HTTP-Response-Code") -> "get_http_response_code"
to_snake("parseJSON2Value")        -> "parse_json2_value"
```

For `parseJSON2Value`: `parse` (lower-to-upper before `J`), then `JSON` — the run `JSON2`
is uppercase letters followed by a digit, no split there, but `2` is followed by uppercase
`V`, so rule 1 splits after `2` giving `json2`, then `value`.

## Constraints

- Input length is between 0 and 5000 characters.
- The input consists of ASCII letters, digits, and the separators `_`, `-`, and space.
- Use only the Python standard library.
