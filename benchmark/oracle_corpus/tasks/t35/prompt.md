# Configurable Multi-Key Sort

Build a small sorting engine that orders a list of records according to a
runtime-supplied list of sort keys, each with its own direction, and with a
precise final tie-break.

Implement a single function:

```python
def multisort(records, keys):
    ...
```

## Inputs

- `records`: a list of dictionaries. All dictionaries contain (at least) every
  field named in `keys`. Field values are comparable to each other within a
  field: for any given field, all values are either all integers or all
  strings (never mixed within one field).
- `keys`: a list of `(field, direction)` tuples describing how to sort, in
  order of decreasing priority. `field` is a string naming a key present in
  every record. `direction` is either the string `"asc"` or the string
  `"desc"`.

`keys` may be empty.

## Behavior

Produce a **new** list of the same record objects ordered as follows:

1. Compare records field-by-field in the order the `keys` are given.
2. For a key with direction `"asc"`, a **smaller** value sorts earlier. For a
   key with direction `"desc"`, a **larger** value sorts earlier. Comparison
   uses Python's natural ordering for the value type (numeric order for
   integers, code-point lexicographic order for strings).
3. The first key on which two records differ decides their order; later keys are
   only consulted to break ties left by earlier keys.
4. **Final tie-break:** if two records compare equal on *every* key in `keys`
   (or if `keys` is empty), they must appear in the **same relative order as in
   the input** (a stable sort by original position). This applies regardless of
   the directions of the keys — the original-order tie-break is always
   ascending by input index.

Do not mutate `records` or any record. Return a new list containing exactly the
same objects.

If `direction` is any string other than `"asc"` or `"desc"`, raise a
`ValueError`.

## Return value

A new ordered list of the input records. For empty `records`, return a new empty
list (even if `keys` is non-empty). For empty `keys`, return the records in
their original order (a stable copy).

## Examples

Example 1:

```python
recs = [
    {"team": "B", "wins": 3, "name": "y"},
    {"team": "A", "wins": 5, "name": "x"},
    {"team": "A", "wins": 5, "name": "w"},
]
multisort(recs, [("team", "asc"), ("wins", "desc")])
# ->
# [
#   {"team": "A", "wins": 5, "name": "x"},   # original index 1, kept before ...
#   {"team": "A", "wins": 5, "name": "w"},   # ... index 2 (tie on team+wins)
#   {"team": "B", "wins": 3, "name": "y"},
# ]
```

The two "A"/5 records tie on both keys, so they keep input order: the one that
appeared first (name "x") stays first.

Example 2:

```python
recs = [
    {"v": 2},
    {"v": 1},
    {"v": 2},
]
multisort(recs, [("v", "desc")])
# ->
# [ {"v": 2}, {"v": 2}, {"v": 1} ]
# The two v==2 records keep their input order (the first-appearing one first),
# even though the sort direction is descending.
```

Example 3:

```python
multisort([{"a": 1}], [])
# -> [ {"a": 1} ]   (empty keys: original order preserved)
```

## Constraints

- Python 3, standard library only.
- The function must be deterministic.
- Up to a few thousand records and a handful of keys.
