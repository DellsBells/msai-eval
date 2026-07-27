# Capped Keystroke Distance

We want to measure how far apart two strings are under a specific edit model, but we only
care about the answer when it is small — beyond a cap we don't need the exact number.

The edit model has **three** operations to transform string `a` into string `b`:

- **insert** a single character: cost `1`
- **delete** a single character: cost `1`
- **substitute** one character for a different one: cost `2`

(There is no operation for replacing a character with itself; matching characters are free.)
The **keystroke distance** is the minimum total cost of any sequence of operations that
turns `a` into `b`.

Implement a single function:

```python
def capped_keystroke_distance(a: str, b: str, cap: int) -> int:
```

## Behavior specification

Return the minimum keystroke distance between `a` and `b` under the cost model above,
**but** if that minimum distance would exceed `cap`, return `-1` instead.

Precisely:

1. Let `d` be the true minimum keystroke distance.
2. If `d <= cap`, return `d`.
3. If `d > cap`, return `-1`.

Notes:

- `cap` is a non-negative integer (`cap >= 0`).
- Comparison of characters is **case-sensitive** and exact.
- Because a substitution costs `2` (the same as one delete plus one insert), a substitution
  is never strictly cheaper than delete-then-insert, but it is never more expensive either;
  either way each mismatched aligned character contributes `2` and each length difference
  contributes `1` per unmatched character. Your job is to compute the true minimum under
  this model — do not hard-code a shortcut, since matching characters must remain free.

### Edge cases

- If `a == b`, the distance is `0`, so return `0` whenever `cap >= 0`.
- If one string is empty, the distance is the length of the other (all inserts or all
  deletes, cost `1` each). Return `-1` if that length exceeds `cap`.
- `cap == 0` means: return `0` only if the strings are identical, otherwise `-1`.
- The function is symmetric in the roles of `a` and `b`: swapping them yields the same
  distance.

## Worked examples

```python
capped_keystroke_distance("cat", "cat", 5)    # -> 0
capped_keystroke_distance("cat", "car", 5)    # -> 2   (substitute 't' -> 'r', cost 2)
capped_keystroke_distance("cat", "cats", 5)   # -> 1   (insert 's', cost 1)
capped_keystroke_distance("cat", "dog", 6)    # -> 6   (three substitutions, cost 2 each)
capped_keystroke_distance("cat", "dog", 4)    # -> -1  (true distance 6 exceeds cap 4)
capped_keystroke_distance("abc", "", 2)       # -> -1  (distance 3 exceeds cap 2)
capped_keystroke_distance("abc", "", 3)       # -> 3
```

For `"cat"` -> `"car"`: the aligned third characters differ (`t` vs `r`), so one
substitution at cost `2`; the rest match for free. Total `2`.

For `"cat"` -> `"dog"`: every aligned character differs, three substitutions at cost `2`
each, total `6`. With `cap = 4`, `6 > 4`, so return `-1`.

## Constraints

- Input strings contain only printable ASCII characters, length `0` to `1000`.
- `cap` is an integer with `0 <= cap <= 4000`.
- Use only the Python standard library.
