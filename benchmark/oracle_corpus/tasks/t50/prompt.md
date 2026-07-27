# Longest Shared Run

Given two strings, a **shared run** is a block of one or more characters that appears
contiguously (with no gaps) in *both* strings at some position. We want to measure the
length of the longest such block, and also report where it starts in the first string.

Implement a single function:

```python
def longest_shared_run(a: str, b: str) -> tuple[int, int]:
```

## Behavior specification

Return a 2-tuple `(length, start)` where:

- `length` is the length of the longest contiguous substring that occurs in **both** `a`
  and `b`.
- `start` is the starting index **in `a`** of that longest shared run.

Rules:

1. Comparison is **case-sensitive** and exact.
2. If there is no shared character at all (the longest shared run has length `0`), return
   `(0, 0)`.
3. If multiple runs tie for the longest length, return the one whose starting index **in
   `a`** is **smallest** (the left-most occurrence within `a`).
4. Overlapping is allowed within a single string in the usual substring sense — you are
   only looking for the maximal contiguous match; you do not need to worry about reusing
   characters.

The run must be contiguous in both strings simultaneously — it is a common **substring**,
not a common subsequence. For example the longest shared run of `"abcxyz"` and `"xyzabc"`
is `"abc"` (length 3) or `"xyz"` (length 3); since both tie at length 3, you return the one
starting earlier in `a`, which is `"abc"` at index `0`.

### Edge cases

- If either string is empty, return `(0, 0)`.
- A single shared character (with nothing longer) yields `length == 1` and the index of its
  left-most occurrence in `a`.
- Identical strings return `(len(a), 0)`.

## Worked examples

```python
longest_shared_run("abcdef", "zzcdezz")   # -> (3, 2)   run "cde" starts at index 2 in a
longest_shared_run("abcxyz", "xyzabc")    # -> (3, 0)   "abc" and "xyz" tie; "abc" starts earlier in a
longest_shared_run("hello", "world")      # -> (1, 2)   "l" is the longest shared run; left-most 'l' in "hello" is index 2
longest_shared_run("same", "same")        # -> (4, 0)
longest_shared_run("abc", "xyz")          # -> (0, 0)   no shared characters
longest_shared_run("", "anything")        # -> (0, 0)
```

For `"hello"` vs `"world"`: the shared characters are `'l'` and `'o'`, but never two in a
row, so the longest shared run has length `1`. Both `'l'` (indices 2 and 3 in `"hello"`)
and `'o'` (index 4) qualify; the left-most start in `a` among all length-1 runs is index
`2` (the first `'l'`), so the answer is `(1, 2)`.

## Constraints

- Input strings contain only printable ASCII characters, length `0` to `2000`.
- Use only the Python standard library.
