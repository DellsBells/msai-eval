# Headline Title-Caser

Write a function `title_case(headline: str) -> str` that converts a headline into a
consistent "title case" style with special handling for small words and known acronyms.

## Tokenization

Split the input on single spaces. The input is guaranteed to already be collapsed: there
are no leading, trailing, or repeated spaces, and the only whitespace is the space
character. Each maximal run of non-space characters is one **word**. (An empty input string
has zero words.)

## Per-word transformation

Let a word's **lowercase key** be the word with every ASCII uppercase letter lowered. The
following two sets are matched against the lowercase key:

- **Small words** (always fully lowercased unless they are the first or last word):
  `a an and as at but by for if in nor of on or the to via vs`
- **Acronyms** (always fully uppercased, regardless of position):
  `api ui id url http https sql html css json xml`

Apply these rules to each word, using its position (0-based index `i`, with `n` total
words):

1. **Acronym rule** (highest priority): if the word's lowercase key is in the acronym set,
   output the word fully uppercased (`word.upper()`).
2. **Small-word rule**: else if the word's lowercase key is in the small-word set AND the
   word is neither the first (`i == 0`) nor the last (`i == n - 1`) word, output the word
   fully lowercased.
3. **Default (capitalize)**: otherwise, "capitalize" the word — output exactly its first
   character uppercased followed by every remaining character lowercased. Only the very
   first character is ever uppercased; interior characters are **always** lowercased, even
   the letter immediately after a hyphen, apostrophe, digit, or any other non-letter. (If
   the first character is not a letter, uppercasing it leaves it unchanged; the rest are
   still lowercased.) This is **not** the same as Python's `str.title()`, which would
   uppercase the start of every letter-run.

The first word and the last word are **never** treated as small words: they always fall
through to the acronym rule or, failing that, the default capitalize rule. Acronyms are
always uppercased even when they are first or last.

## Notes

- Matching for both sets is case-insensitive (via the lowercase key) but exact: the whole
  word must equal an entry. `"apis"` is not the acronym `api`; `"theory"` is not the small
  word `the`.
- "Capitalize" means: uppercase the first character, lowercase the rest. So `"iPhone"`
  becomes `"Iphone"` and `"MACOS"` becomes `"Macos"` (neither is in the acronym set).
- Because only the first character is uppercased, hyphenated and punctuated words keep the
  rest lowercased: `"mother-in-law"` becomes `"Mother-in-law"` (not `"Mother-In-Law"`),
  `"o'brien"` becomes `"O'brien"` (not `"O'Brien"`), and `"123abc"` becomes `"123abc"`
  (leading digit unchanged, letters lowercased — not `"123Abc"`).
- Words are joined back together with single spaces.

## Examples

```
title_case("the quick brown fox")
    -> "The Quick Brown Fox"          # "the" is first, so it is capitalized

title_case("a tale of two cities")
    -> "A Tale of Two Cities"         # "of" is an interior small word -> lowercase

title_case("building an api for the web")
    -> "Building an API for the Web"  # "api" -> uppercased; "an","for","the" interior small words

title_case("paris via london vs berlin")
    -> "Paris via London vs Berlin"   # "via" and "vs" are interior small words -> lowercase

title_case("mother-in-law visits o'brien")
    -> "Mother-in-law Visits O'brien"  # only the first char of each word is uppercased
```

## Constraints

- Input length is between 0 and 5000 characters.
- Use only the Python standard library.
