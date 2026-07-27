# Alternating Digit Weight Signature

Write a function:

```python
def digit_signature(n: int) -> int:
```

that computes a "signature" of a non-negative integer `n` from its base-10 digits.

## Behavior

1. Take the decimal digits of `n`, read **from left to right** (most significant digit first).
2. Assign each digit a weight based on its **position from the left**, starting at position 1:
   - The digit at position 1 (leftmost) is multiplied by 1.
   - The digit at position 2 is multiplied by 2.
   - The digit at position 3 is multiplied by 3.
   - ...and so on, so the digit at position `k` is multiplied by `k`.
3. Give each weighted term a sign that **alternates starting with a plus** for the leftmost digit: position 1 is added, position 2 is subtracted, position 3 is added, position 4 is subtracted, and so on.
4. Return the resulting sum (which may be negative).

Formally, if the digits from left to right are `d_1, d_2, ..., d_m`, the result is:

```
1*d_1 - 2*d_2 + 3*d_3 - 4*d_4 + ...
```

## Edge cases

- `n == 0` is a single digit `0`, so `digit_signature(0)` returns `0`.
- Single-digit inputs `n` (0 through 9) return `n` itself (weight 1, positive sign).
- `n` is guaranteed to be a non-negative integer (it will never be negative). It may be arbitrarily large.
- Leading zeros are never present in the standard decimal representation, so you never process a leading `0` unless `n` is exactly `0`.

## Examples

Example 1:
```
digit_signature(1234)
# digits left-to-right: 1, 2, 3, 4
# 1*1 - 2*2 + 3*3 - 4*4 = 1 - 4 + 9 - 16 = -10
# returns -10
```

Example 2:
```
digit_signature(505)
# digits: 5, 0, 5
# 1*5 - 2*0 + 3*5 = 5 - 0 + 15 = 20
# returns 20
```

Example 3:
```
digit_signature(7)
# single digit: 1*7 = 7
# returns 7
```

## Constraints

- Use only the Python standard library.
- Do not read from files, the network, the clock, or the environment.
