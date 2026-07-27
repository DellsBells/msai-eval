# Positional Residue Divisibility

You are given the digits of a non-negative integer written in some base `b`, and a
positive divisor `d`. Your job is to compute the remainder of that integer modulo
`d` using **positional residues** — that is, by combining each digit with the
residue of its place value `b^i` modulo `d`, never by reconstructing the full
integer as a single number first.

Implement:

```python
def residue_mod(digits: list[int], base: int, d: int) -> int:
```

## Meaning of the input

- `digits` is a list of integer digits in **most-significant-first** order (natural
  reading order). For example, in base 10 the number 405 is given as `[4, 0, 5]`.
- `base` (`b`) is the radix, an integer with `b >= 2`. Every element of `digits`
  satisfies `0 <= digit < b`.
- `d` is the divisor, an integer with `d >= 1`.

## What to return

Return the value

```
( sum over positions i of  digit_i * (b^i mod d) )  mod d
```

where position `i` is counted **from the right**, starting at `i = 0` for the last
(least-significant) element of `digits`. The returned value is always in the range
`0 <= result < d`.

The result must equal `N mod d`, where `N` is the integer whose base-`b` digits are
`digits`. You must produce the same answer without ever materializing `N` as one
big integer — reduce modulo `d` as you go so that all intermediate values stay
below roughly `d * base`. (Your function will only be checked on its return value,
but the intended technique is Horner's method carried out under the modulus.)

## Edge cases

- **Empty `digits`** represents the integer `0`, so return `0`.
- A list of all zeros, e.g. `[0, 0, 0]`, also represents `0`; return `0`.
- When `d == 1`, every integer is divisible by 1, so the result is always `0`.
- Leading zeros in `digits` are allowed and do not change the value (e.g. `[0, 4, 0, 5]`
  is the same number as `[4, 0, 5]`).
- A single-digit list `[x]` (with `0 <= x < b`) returns `x mod d`.

## Examples

Example 1:
```
residue_mod([4, 0, 5], 10, 7)
# The number is 405. 405 mod 7 = 405 - 57*7 = 405 - 399 = 6
# returns 6
```

Example 2:
```
residue_mod([1, 0, 1, 1], 2, 3)
# Binary 1011 = 11 (decimal). 11 mod 3 = 2
# returns 2
```

Example 3:
```
residue_mod([], 10, 9)        # returns 0
residue_mod([0, 0], 5, 4)     # returns 0
residue_mod([7], 16, 5)       # 7 mod 5 = 2 -> returns 2
```

## Constraints

- Use only the Python standard library.
- Do not read from files, the network, the clock, or the environment.
