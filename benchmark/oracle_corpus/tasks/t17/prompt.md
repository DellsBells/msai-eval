# Bracket Fault Locator

You are validating a stream of grouping symbols and need to pinpoint *where* the
first structural fault occurs, not merely whether the stream is balanced.

Implement a single function:

```python
def find_fault(s: str) -> int:
    ...
```

## Grouping symbols

Only these six characters are structural brackets:

- Openers: `(`, `[`, `{`
- Closers: `)`, `]`, `}`

with the obvious pairing: `(` matches `)`, `[` matches `]`, `{` matches `}`.

**Every other character in `s` is ordinary text and must be ignored** (it neither
opens nor closes a group, and it can never be a fault).

## What "balanced" means

Scanning left to right, each opener must be closed later by the matching closer,
and closers must appear in the correct nested order (last opened, first closed).

## Return value

`find_fault` returns a single integer, the **0-based index into `s`** of the first
fault, or `-1` if the whole string is balanced.

A fault is detected at the earliest index where one of these happens:

1. **Mismatched closer** — a closer appears whose type does not match the most
   recent still-open opener. The fault index is the index of that *closer*.
2. **Stray closer** — a closer appears when there is no open opener at all. The
   fault index is the index of that *closer*.
3. **Unclosed opener** — the string ends while one or more openers are still open.
   The fault index is the index of the **most recently opened** (i.e. innermost)
   opener that was never closed.

Rules 1 and 2 are checked as you scan, so a fault detected mid-scan always wins
over an end-of-string unclosed-opener fault (a fault that would occur later in the
scan). If the string is fully balanced, return `-1`.

## Constraints

- `s` may be empty; `find_fault("")` returns `-1`.
- `s` can be up to 100000 characters long; run in linear time.
- `s` contains only printable ASCII, but you must not assume anything about which
  non-bracket characters appear.

## Examples

```python
find_fault("(a[b]c)")        # -> -1   (balanced; letters ignored)
find_fault("(a[b)c]")        # -> 4    ')' at index 4 mismatches the open '['
find_fault("ab)cd")          # -> 2    stray ')' with nothing open
find_fault("x(y[z]")         # -> 1    '(' at index 1 is never closed (innermost unclosed)
find_fault("{[()]}")         # -> -1   fully balanced
```
