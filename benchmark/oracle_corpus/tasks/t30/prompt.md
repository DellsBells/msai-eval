# Factorial-Base (Factoradic) Conversion

The **factorial number system** represents a non-negative integer as a sequence of
digits where the place values are factorials instead of powers of a fixed base.

Reading a factoradic representation from **right to left**, the place values are:

```
0!, 1!, 2!, 3!, 4!, ...   =   1, 1, 2, 6, 24, ...
```

The digit sitting on the place value `i!` must satisfy `0 <= digit <= i`. In other
words, the rightmost digit (place `0!`) is always `0`, the next digit (place `1!`)
is `0` or `1`, the next (place `2!`) is in `0..2`, the next (place `3!`) is in
`0..3`, and so on.

Implement two functions:

```python
def to_factoradic(n: int) -> list[int]:
def from_factoradic(digits: list[int]) -> int:
```

## `to_factoradic(n)`

Convert a non-negative integer `n` into its factoradic digit list.

- Return a list of digits ordered from the **most significant place to the least
  significant place** (i.e. left to right, the natural reading order). The **last**
  element of the list is the `0!` place and is therefore always `0`.
- Use the **minimal** number of digits: do not include extra leading zeros. The
  representation of `0` is exactly `[0]` (just the mandatory `0!` place). The
  representation of any `n >= 1` must have a nonzero most-significant digit.
- For `n >= 1`, find the largest `k` such that `k! <= n`; the result has `k + 1`
  digits (places `k!` down to `0!`).

## `from_factoradic(digits)`

Convert a factoradic digit list (in the same most-significant-first order) back to
an integer.

- `digits[-1]` corresponds to place `0!`, `digits[-2]` to place `1!`, and in
  general the element at index `j` (counting from the right, starting at 0)
  corresponds to place `j!`.
- Return the integer value. `from_factoradic([0])` returns `0`.
- You may assume the input is a valid factoradic list (each digit is within its
  allowed range), except that an **empty list** must return `0`.

## Round-trip guarantee

For every non-negative integer `n`:
`from_factoradic(to_factoradic(n)) == n`.

## Examples

Example 1:
```
to_factoradic(0)   # -> [0]
to_factoradic(1)   # -> [1, 0]     (1 = 1*1! + 0*0!)
to_factoradic(2)   # -> [1, 0, 0]  (2 = 1*2! + 0*1! + 0*0!)
```

Example 2:
```
to_factoradic(349)
# 349 = 2*5! + 4*4! + 2*3! + 0*2! + 1*1! + 0*0!
#     = 2*120 + 4*24 + 2*6 + 0*2 + 1*1 + 0*1
#     = 240 + 96 + 12 + 0 + 1 + 0 = 349
# -> [2, 4, 2, 0, 1, 0]
```

Example 3:
```
from_factoradic([2, 4, 2, 0, 1, 0])   # -> 349
from_factoradic([1, 0])               # -> 1
from_factoradic([])                   # -> 0
```

## Constraints

- Inputs to `to_factoradic` are non-negative integers and may be large.
- Use only the Python standard library.
- Do not read from files, the network, the clock, or the environment.
