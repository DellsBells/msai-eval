# Slug Normalizer

Write a function `slugify(text: str) -> str` that converts an arbitrary string into a
URL-friendly "slug".

## Behavior

Apply the following steps, in order:

1. Convert every ASCII uppercase letter (`A`-`Z`, code points U+0041 through U+005A) to its
   lowercase equivalent. Leave **every** other character unchanged by this step. This
   lowercasing is ASCII-only: it is defined solely by the `A`-`Z` range, not by Unicode case
   folding. Do not use any locale- or Unicode-aware case conversion here — a non-ASCII
   character must never be turned into an ASCII letter or digit. For example, the KELVIN
   SIGN `K` (U+212A) and the LATIN CAPITAL LETTER I WITH DOT ABOVE `İ` (U+0130) are left
   unchanged by this step (and, being non-ASCII, are separators in step 2).
2. Treat a character as a **word character** if it is an ASCII lowercase letter (`a`-`z`)
   or an ASCII digit (`0`-`9`). Every other character (spaces, punctuation, underscores,
   accented letters, symbols, etc.) is a **separator**.
3. Replace every maximal run of one or more consecutive separators with a single hyphen
   (`-`).
4. Remove a leading hyphen if present, and remove a trailing hyphen if present (there can
   be at most one of each after step 3).

The result contains only lowercase ASCII letters, digits, and hyphens. Hyphens never
appear at the start or end, and never appear consecutively.

## Notes

- An empty input string produces an empty output string.
- An input consisting entirely of separators produces an empty output string.
- The underscore character `_` is a separator, not a word character.
- Non-ASCII letters (e.g. `é`, `ñ`) are separators — they are NOT preserved or transliterated.

## Examples

```
slugify("Hello, World!")        -> "hello-world"
slugify("  Multiple   Spaces ") -> "multiple-spaces"
slugify("café_bar 42")          -> "caf-bar-42"
```

In the third example, `é` and `_` are both separators; the run `é_` between `caf` and
`bar` collapses to a single hyphen, and the space before `42` collapses to another hyphen.

As a fourth example, the string `"a" + "K" + "b"` (the letters `a`, then the KELVIN
SIGN, then `b`) becomes `"a-b"`: the Kelvin sign is non-ASCII, so step 1 leaves it
unchanged and step 2 treats it as a separator, producing a single hyphen between `a` and
`b`. It is **not** lowercased to the ASCII letter `k`.

## Constraints

- Input length is between 0 and 10000 characters.
- Use only the Python standard library.
