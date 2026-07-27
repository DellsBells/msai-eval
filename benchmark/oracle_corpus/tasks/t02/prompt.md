# Tag Canonicalizer

You are cleaning up free-form user-entered tags before storing them. Write a function
`canonicalize_tags(raw: list[str]) -> list[str]` that normalizes and deduplicates a list
of tag strings.

## Canonical form of a single tag

For each raw tag string, compute its canonical form by applying these steps in order:

1. **Trim** leading and trailing whitespace (spaces, tabs, newlines).
2. **Lowercase** all ASCII uppercase letters (`A`-`Z`).
3. **Collapse internal whitespace**: replace every maximal run of one or more internal
   whitespace characters with a single space (`' '`).

A tag whose canonical form is the empty string (`""`) is called **blank** and is dropped
entirely — it does not appear in the output.

## Deduplication and ordering

Two raw tags are considered duplicates when their canonical forms are equal. The output
list must contain each distinct non-blank canonical form **exactly once**.

The output is ordered by **first appearance**: a canonical form appears in the output at
the position where its *first* contributing raw tag occurred in the input. In other words,
walk the input left to right; the first time you see a raw tag that produces a given
canonical form, that canonical form takes the next output slot. Later raw tags that map to
an already-seen canonical form are ignored.

## Notes

- Whitespace for trimming/collapsing means the ASCII characters space, tab (`\t`),
  newline (`\n`), carriage return (`\r`), form feed (`\f`), and vertical tab (`\v`).
- Do not remove or alter internal punctuation or digits — only case and whitespace are
  normalized.
- An empty input list produces an empty output list.

## Examples

```
canonicalize_tags(["  Python ", "python", "Data   Science"])
    -> ["python", "data science"]

canonicalize_tags(["C++", "  ", "c++", "\tGo\t"])
    -> ["c++", "go"]

canonicalize_tags(["Hello  World", "hello world", "HELLO WORLD"])
    -> ["hello world"]
```

In the first example, `"  Python "` and `"python"` both canonicalize to `"python"`, so
only the first is kept; `"Data   Science"` collapses its triple space to one space.

## Constraints

- The input list has between 0 and 5000 elements.
- Each raw tag has length between 0 and 200 characters.
- Use only the Python standard library.
