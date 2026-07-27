# Validate and measure nested brackets

Write a function:

```python
def check_brackets(text: str) -> tuple:
    ...
```

that scans a string for three kinds of brackets and reports whether they are
balanced, along with the maximum nesting depth reached.

## Brackets

Only these six characters are treated as brackets. Every other character
(letters, digits, spaces, punctuation, etc.) is ignored completely.

| Open | Close |
|------|-------|
| `(`  | `)`   |
| `[`  | `]`   |
| `{`  | `}`   |

## What to return

Return a tuple `(ok, depth, position)`:

- `ok` — a `bool`. `True` if and only if the brackets are perfectly balanced:
  every opening bracket is closed by a matching closing bracket of the same
  kind, in the correct nested order, with nothing left open at the end.
- `depth` — an `int`, the **maximum nesting depth** reached at any point while
  scanning a *valid prefix*. See the depth rules below.
- `position` — an `int`. When `ok` is `True`, this is `-1`. When `ok` is
  `False`, this is the **0-based index into `text`** of the first bracket
  character that makes the string invalid (see error rules).

## Depth rules

Depth starts at 0. Each time you consume an opening bracket, depth increases by
1 *after* which you record it as a candidate maximum; each time you consume a
matching closing bracket, depth decreases by 1. `depth` in the result is the
largest value depth ever reached.

- For a fully valid string, `depth` is the deepest nesting. Example: `([{}])`
  reaches depth 3.
- For an **invalid** string, `depth` is still the maximum depth ever reached
  while scanning, counting every opening bracket consumed **before** the
  scan stops. The error character itself is not counted (a mismatched or
  stray closing bracket does not raise the depth). Example: `(([)` consumes
  three openers `(`, `(`, `[` (depth climbs to 3), then the `)` at index 3
  does not match the `[` at index 2, so it is the error; the reported depth
  is 3.
- Example: `({}` climbs to depth 2 (via `(` then `{`), drops back to 1 when
  `}` closes, and ends with `(` unclosed — reported depth is the maximum
  reached, `2`.
- The maximum can be reached and then *left behind* before the error. The
  running depth may have already dropped when the scan stops; you still report
  the peak, not the depth at the error. Example: `())` — the `(` pushes depth
  to 1, the first `)` closes it (depth back to 0), then the second `)` at
  index 2 is a stray close. The running depth there is `0`, but the maximum
  ever reached was `1`, so the reported depth is `1`, giving `(False, 1, 2)`.
  Example: `(()))` reaches depth 2, returns to 0, then the `)` at index 4 is
  stray → `(False, 2, 4)`.
- The empty string, or a string with no brackets at all, is valid with
  `depth == 0` and `position == -1`.

## Error rules (which character is "first invalid")

Scanning left to right over bracket characters only:

1. A **closing bracket with no open bracket waiting** is invalid. Its index is
   the error position. Example: `a)b` → error at index 1.
2. A **closing bracket that does not match the most recent unclosed opening
   bracket** is invalid. Its index is the error position. Example: `[(])` →
   the `]` at index 2 does not match the `(` opened at index 1, so error at
   index 2.
3. If scanning completes but **one or more opening brackets were never
   closed**, the string is invalid. The error position is the index of the
   **first** (left-most) opening bracket that remained unclosed. Example:
   `({)` is actually rule 2, but `({}` leaves the `(` at index 0 unclosed →
   error at index 0; `foo(bar` leaves the `(` at index 3 unclosed → error at
   index 3.

Rules 1 and 2 are detected as soon as the bad closing bracket is seen, so an
early mismatch is always reported before any later unclosed-open situation.

## Examples

```python
check_brackets("([{}])")     # (True, 3, -1)
check_brackets("a(b)c[d]e")  # (True, 1, -1)
check_brackets("(([)")       # (False, 3, 3)
check_brackets("({}")        # (False, 2, 0)
check_brackets("())")        # (False, 1, 2)
check_brackets("")           # (True, 0, -1)
check_brackets(")")          # (False, 0, 0)
```

## Constraints

- `text` is a `str`, possibly empty.
- Return a 3-tuple `(bool, int, int)` exactly as specified.
- Use only the Python standard library.
