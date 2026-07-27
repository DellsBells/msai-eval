# Balanced Ternary Codec and Addition

**Balanced ternary** is a base-3 positional system whose digits are `-1`, `0`, and
`+1` (instead of `0`, `1`, `2`). Every integer — positive, negative, or zero — has a
unique balanced-ternary representation with no leading zeros. Place values are the
usual powers of 3: `..., 27, 9, 3, 1`.

For example:

```
  5 = 1*9 + (-1)*3 + (-1)*1   -> digits [1, -1, -1]
 -4 = (-1)*3 + (-1)*1         -> digits [-1, -1]
  0                           -> digits [0]
```

Implement three functions.

```python
def to_balanced_ternary(n: int) -> list[int]:
def from_balanced_ternary(digits: list[int]) -> int:
def add_balanced_ternary(a: list[int], b: list[int]) -> list[int]:
```

## `to_balanced_ternary(n)`

Convert an integer `n` (which may be negative, zero, or positive) into its balanced
ternary digits.

- Return a list of digits, each in `{-1, 0, 1}`, ordered **most-significant place
  first** (natural reading order). The last element is the `1`s place.
- Use the canonical form: **no leading zeros**. The representation of `0` is exactly
  `[0]`. For any `n != 0`, the first (most-significant) digit is nonzero.

## `from_balanced_ternary(digits)`

Convert a balanced-ternary digit list (same most-significant-first order) back to an
integer.

- Each element of `digits` is one of `-1`, `0`, `1`.
- Return the integer value. `from_balanced_ternary([0])` returns `0`.
- An **empty list** represents `0` and must return `0`.
- The input may contain leading zeros (e.g. `[0, 0, 1]`); they do not change the
  value.

## `add_balanced_ternary(a, b)`

Given two balanced-ternary digit lists `a` and `b` (each most-significant-first,
each a valid list of digits in `{-1, 0, 1}`, possibly with leading zeros, possibly
empty), return the **canonical** balanced-ternary representation of the sum of the
two numbers they represent.

- The returned list must itself be canonical: digits in `{-1, 0, 1}`, most
  significant first, no leading zeros, and `[0]` for a result of zero.
- The result must satisfy
  `from_balanced_ternary(add_balanced_ternary(a, b)) ==
   from_balanced_ternary(a) + from_balanced_ternary(b)`.

## Carry rule (for reference)

When a column sum `s` (a value in `-3..3` after adding a carry) is reduced to a
balanced-ternary digit, use:

```
s = -3 -> digit  0, carry -1
s = -2 -> digit  1, carry -1
s = -1 -> digit -1, carry  0
s =  0 -> digit  0, carry  0
s =  1 -> digit  1, carry  0
s =  2 -> digit -1, carry  1
s =  3 -> digit  0, carry  1
```

## Round-trip guarantee

For every integer `n` (negative, zero, positive):
`from_balanced_ternary(to_balanced_ternary(n)) == n`.

## Examples

Example 1:
```
to_balanced_ternary(5)    # -> [1, -1, -1]
to_balanced_ternary(-4)   # -> [-1, -1]
to_balanced_ternary(0)    # -> [0]
```

Example 2:
```
from_balanced_ternary([1, -1, -1])   # -> 5
from_balanced_ternary([0, 0, 1])     # -> 1
from_balanced_ternary([])            # -> 0
```

Example 3:
```
add_balanced_ternary([1, -1, -1], [-1, -1])   # 5 + (-4) = 1 -> [1]
add_balanced_ternary([0], [0])                # 0 + 0 = 0 -> [0]
add_balanced_ternary([1], [1])                # 1 + 1 = 2 -> [1, -1]  (2 = 1*3 + (-1)*1)
```

## Constraints

- Inputs to `to_balanced_ternary` are integers and may be large (positive or negative).
- Use only the Python standard library.
- Do not read from files, the network, the clock, or the environment.
