# Roster Ordering

You are given a roster of employees and must produce a deterministic display order.

Implement a single function:

```python
def order_roster(employees):
    ...
```

## Input

`employees` is a list of dictionaries. Each dictionary has exactly these keys:

- `"name"`: a non-empty string (may contain any characters; comparisons are case-sensitive).
- `"dept"`: a non-empty string naming the department.
- `"salary"`: an integer that may be any value (including zero or negative).

Names within the whole roster are **not** guaranteed to be unique. Two different
dictionaries may be fully identical in every field.

## Ordering rules

Return a **new** list containing the same dictionary objects, ordered by applying
these rules in priority order:

1. **Department, ascending** by ordinary string comparison (Python's default `<`
   on `str`, i.e. lexicographic by Unicode code point).
2. If two employees are in the same department, the one with the **higher salary
   comes first** (salary descending).
3. If they are in the same department **and** have the same salary, order by
   **name, ascending** (ordinary string comparison).
4. If department, salary, and name are all equal, preserve the **relative order
   in which those employees appeared in the input** (the earlier one stays
   earlier).

Do not mutate the input list or any of the dictionaries. The returned list must
contain exactly the same objects (by identity) as the input, just reordered.

## Return value

A new list of the same dictionaries in the computed order. For an empty input,
return a new empty list.

## Examples

Example 1:

```python
order_roster([
    {"name": "Ana",   "dept": "Sales",   "salary": 50000},
    {"name": "Bob",   "dept": "Eng",     "salary": 90000},
    {"name": "Cara",  "dept": "Sales",   "salary": 60000},
    {"name": "Dan",   "dept": "Eng",     "salary": 90000},
])
# ->
# [
#   {"name": "Bob",  "dept": "Eng",   "salary": 90000},
#   {"name": "Dan",  "dept": "Eng",   "salary": 90000},
#   {"name": "Cara", "dept": "Sales", "salary": 60000},
#   {"name": "Ana",  "dept": "Sales", "salary": 50000},
# ]
```

(Within "Eng", Bob and Dan both earn 90000, so they are ordered by name: "Bob" <
"Dan". "Eng" < "Sales" so all Eng employees come first.)

Example 2:

```python
order_roster([
    {"name": "Zoe", "dept": "Ops", "salary": -100},
    {"name": "Amy", "dept": "Ops", "salary": -100},
])
# ->
# [
#   {"name": "Amy", "dept": "Ops", "salary": -100},
#   {"name": "Zoe", "dept": "Ops", "salary": -100},
# ]
```

Example 3:

```python
order_roster([])
# -> []
```

## Constraints

- Python 3, standard library only.
- The function must be deterministic.
- Input may contain up to a few thousand entries.
