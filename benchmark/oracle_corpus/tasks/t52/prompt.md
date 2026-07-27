# Recursive Block Similarity

We measure how similar two strings are by repeatedly carving out their longest matching
block and recursing on what remains to the left and right of that block, then reporting the
fraction of characters that got matched.

Implement a single function:

```python
def block_similarity(a: str, b: str) -> float:
```

## The matching algorithm

Define the total number of matched characters `M(a, b)` between two strings as follows.

1. **Find the longest matching block**: the longest string `s` that appears as a
   contiguous substring in **both** `a` and `b`. Let its length be `k`, its starting index
   in `a` be `i`, and its starting index in `b` be `j`.

   - Tie-breaking when several blocks share the maximum length `k`: choose the block with
     the smallest `i` (start in `a`); if still tied, choose the smallest `j` (start in
     `b`).

2. **Base case**: if `k == 0` (no shared character at all), then `M(a, b) = 0`.

3. **Recurse**: otherwise the block accounts for `k` matched characters. Recurse on the
   parts strictly to the **left** of the block in each string — `a[:i]` and `b[:j]` — and
   on the parts strictly to the **right** — `a[i+k:]` and `b[j+k:]`. Then:

   ```
   M(a, b) = k + M(a[:i], b[:j]) + M(a[i+k:], b[j+k:])
   ```

The **block similarity** is then:

```
block_similarity(a, b) = 2 * M(a, b) / (len(a) + len(b))
```

rounded to **4 decimal places** (use `round(value, 4)`).

## Special cases

- If **both** strings are empty, define the similarity as `1.0` (they are considered
  identical). Return `1.0`.
- If exactly one string is empty, `M = 0` and the ratio is `0.0`.
- If the strings are identical (and non-empty), the longest block is the whole string, so
  `M = len(a)` and the similarity is `1.0`.
- The result always lies in the closed interval `[0.0, 1.0]`.
- Comparison of characters is **case-sensitive** and exact.

## Worked examples

```python
block_similarity("", "")              # -> 1.0
block_similarity("abc", "abc")        # -> 1.0
block_similarity("abc", "xyz")        # -> 0.0
block_similarity("abcd", "bcde")      # -> 0.75
#   longest block "bcd" (k=3) matched; left parts "a" vs "" (M=0),
#   right parts "" vs "e" (M=0). M=3. ratio = 2*3/(4+4) = 6/8 = 0.75

block_similarity("tortoise", "torso") # -> 0.6154
#   longest block "tor" (k=3): a="tortoise" i=0, b="torso" j=0.
#   left: "" vs "" -> 0. right: "toise" vs "so".
#     in "toise" vs "so": longest block "s" (k=1) at a-index 3, b-index 1;
#     left "toi" vs "s" -> 0 ; right "e" vs "o" -> 0.  So right contributes 1.
#   M = 3 + 0 + 1 = 4. ratio = 2*4/(8+5) = 8/13 = 0.6154 (rounded)
```

## Constraints

- Input strings contain only printable ASCII characters, length `0` to `500`.
- Use only the Python standard library.
- Return a Python `float` rounded to 4 decimal places via `round(..., 4)`.
