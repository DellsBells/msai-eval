# Parse a semicolon-delimited settings string

Write a function:

```python
def parse_settings(text: str) -> dict:
    ...
```

that parses a compact settings string into a dictionary.

## Format

The input is a single string containing zero or more **entries** separated by
semicolons (`;`). Each entry is a `key=value` pair. For example:

```
"host=localhost;port=8080;debug=true"
```

## Rules

Process entries strictly left to right. For each entry:

1. **Splitting a pair.** Split the entry into a key and a value on the **first**
   `=` character. Any `=` characters after the first belong to the value.
   Example: the entry `path=/a=b` has key `path` and value `/a=b`.

2. **Trimming.** Strip leading and trailing ASCII spaces (`' '`, i.e. `U+0020`
   only — do not strip tabs or newlines) from **both** the key and the value
   after splitting. Example: the entry `  name  =  Jake  ` yields key `name`
   and value `Jake`.

3. **Empty entries.** An entry that is empty or contains only spaces (after the
   surrounding text is split on semicolons) is **skipped** entirely and
   contributes nothing to the result. This handles leading, trailing, and
   doubled semicolons gracefully. Example: `a=1;;b=2` produces two keys.

4. **Missing `=`.** A non-empty entry that contains no `=` character is
   **skipped** (it is malformed and contributes nothing). Example: the entry
   `justakey` is dropped.

5. **Empty key after trimming.** If, after trimming, the key is the empty
   string, the entry is **skipped**. Example: the entry `=value` is dropped, and
   so is `   =value`.

6. **Empty value is allowed.** A value may legitimately be empty. The entry
   `k=` (or `k=   `) yields key `k` mapped to the empty string `""`.

7. **Duplicate keys.** If the same key (compared after trimming, case
   sensitively) appears more than once, the **last** occurrence wins.

The returned dictionary maps each surviving key (a `str`) to its value (a
`str`). Key insertion order is not tested; only the key/value contents are.

## Examples

```python
parse_settings("host=localhost;port=8080;debug=true")
# {"host": "localhost", "port": "8080", "debug": "true"}

parse_settings("  name = Jake ;; role=admin ; role = owner ")
# {"name": "Jake", "role": "owner"}

parse_settings("path=/a=b;empty=;justakey;=orphan")
# {"path": "/a=b", "empty": ""}
```

## Constraints

- `text` is a `str` and may be empty (`parse_settings("")` returns `{}`).
- Keys and values contain only printable ASCII plus spaces; no escaping
  mechanism exists.
- Use only the Python standard library.
