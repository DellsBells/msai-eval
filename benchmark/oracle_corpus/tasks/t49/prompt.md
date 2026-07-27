# Positional Divergence Score

Two sequences of characters can be compared position-by-position. When they are the
same length, we simply count how many positions hold different characters. When one is
longer than the other, every extra trailing position of the longer string is also counted
as a difference (since there is nothing to compare it against).

Implement a single function:

```python
def positional_divergence(a: str, b: str) -> int:
```

## Behavior specification

Return the **positional divergence** between strings `a` and `b`, computed as follows:

1. Let `n = min(len(a), len(b))` be the length of the overlapping region.
2. For each index `i` in `0 <= i < n`, count `1` if `a[i] != b[i]`, otherwise `0`.
3. Add `abs(len(a) - len(b))` — one for each unpaired trailing position of the longer
   string.
4. The result is the total from steps 2 and 3.

Comparison is **case-sensitive** and exact: `'A'` and `'a'` are different characters, and
a whitespace character differs from any non-matching character in the usual way.

### Edge cases

- If both strings are empty, the divergence is `0`.
- If exactly one string is empty, the divergence equals the length of the other string.
- If the strings are identical, the divergence is `0`.
- The function never returns a negative number; the minimum possible result is `0`.

## Worked examples

```python
positional_divergence("kitten", "kitten")   # -> 0   (identical)
positional_divergence("kitten", "sitting")  # -> 3
positional_divergence("abc", "abcd")         # -> 1   (overlap identical, 1 extra trailing char)
positional_divergence("", "hello")           # -> 5   (5 unpaired positions)
```

For the second example, comparing `"kitten"` (length 6) and `"sitting"` (length 7),
the overlap is the first 6 characters `"kitten"` vs `"sittin"`. Position by position:

| index | a | b | differ? |
|-------|---|---|---------|
| 0     | k | s | 1       |
| 1     | i | i | 0       |
| 2     | t | t | 0       |
| 3     | t | t | 0       |
| 4     | e | i | 1       |
| 5     | n | n | 0       |

That is **2** mismatches in the overlap. The longer string has one extra trailing
character `'g'`, contributing `abs(6 - 7) = 1`. Total = `2 + 1 = 3`.

## Constraints

- Input strings contain only printable ASCII characters, length `0` to `10000`.
- Use only the Python standard library.
