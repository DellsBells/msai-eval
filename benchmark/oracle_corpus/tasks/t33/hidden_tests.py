import random

import solution


def names(result):
    return [e["name"] for e in result]


def test_example_1():
    inp = [
        {"name": "Ana", "dept": "Sales", "salary": 50000},
        {"name": "Bob", "dept": "Eng", "salary": 90000},
        {"name": "Cara", "dept": "Sales", "salary": 60000},
        {"name": "Dan", "dept": "Eng", "salary": 90000},
    ]
    out = solution.order_roster(inp)
    assert names(out) == ["Bob", "Dan", "Cara", "Ana"]


def test_example_2_tie_by_name():
    inp = [
        {"name": "Zoe", "dept": "Ops", "salary": -100},
        {"name": "Amy", "dept": "Ops", "salary": -100},
    ]
    out = solution.order_roster(inp)
    assert names(out) == ["Amy", "Zoe"]


def test_empty():
    assert solution.order_roster([]) == []


def test_single_element():
    inp = [{"name": "Sol", "dept": "X", "salary": 10}]
    out = solution.order_roster(inp)
    assert names(out) == ["Sol"]
    assert out is not inp  # new list


def test_salary_descending_within_dept():
    inp = [
        {"name": "Low", "dept": "A", "salary": 1},
        {"name": "High", "dept": "A", "salary": 100},
        {"name": "Mid", "dept": "A", "salary": 50},
    ]
    out = solution.order_roster(inp)
    assert names(out) == ["High", "Mid", "Low"]


def test_dept_ascending_precedes_salary():
    # Higher salary in a later dept must NOT jump ahead of lower salary earlier dept.
    inp = [
        {"name": "P", "dept": "Z", "salary": 999},
        {"name": "Q", "dept": "A", "salary": 1},
    ]
    out = solution.order_roster(inp)
    assert names(out) == ["Q", "P"]


def test_full_duplicate_stable_by_input_order():
    a = {"name": "T", "dept": "D", "salary": 5}
    b = {"name": "T", "dept": "D", "salary": 5}
    inp = [a, b]
    out = solution.order_roster(inp)
    # Identical in all fields -> earlier input stays earlier (identity check).
    assert out[0] is a
    assert out[1] is b


def test_input_not_mutated():
    inp = [
        {"name": "M", "dept": "B", "salary": 3},
        {"name": "N", "dept": "A", "salary": 7},
    ]
    snapshot = list(inp)
    solution.order_roster(inp)
    assert inp == snapshot
    assert inp[0]["name"] == "M" and inp[1]["name"] == "N"


def test_case_sensitive_ordering():
    # Uppercase letters sort before lowercase in code-point order.
    inp = [
        {"name": "alpha", "dept": "T", "salary": 0},
        {"name": "Beta", "dept": "T", "salary": 0},
    ]
    out = solution.order_roster(inp)
    assert names(out) == ["Beta", "alpha"]


def test_case_sensitive_dept_ordering():
    # Department ordering is by Unicode code point, NOT case-insensitive.
    # 'Z' (90) < 'a' (97), so "Zoo" must come before "apple".
    inp = [
        {"name": "P", "dept": "apple", "salary": 10},
        {"name": "Q", "dept": "Zoo", "salary": 10},
    ]
    out = solution.order_roster(inp)
    assert [e["dept"] for e in out] == ["Zoo", "apple"]
    assert names(out) == ["Q", "P"]


def test_case_sensitive_dept_beats_casefold():
    # A case-insensitive (casefolded) dept key would order these as
    # ["apple", "Banana"] since "apple" < "banana"; the correct code-point
    # order is ["Banana", "apple"] because 'B' (66) < 'a' (97).
    inp = [
        {"name": "One", "dept": "apple", "salary": 5},
        {"name": "Two", "dept": "Banana", "salary": 5},
    ]
    out = solution.order_roster(inp)
    assert [e["dept"] for e in out] == ["Banana", "apple"]


def test_property_matches_key_ordering():
    # For random rosters, every adjacent pair must respect the key order:
    # dept asc, then salary desc, then name asc.
    rng = random.Random(20240611)
    # Include depts that differ only by case ("Eng" vs "eng", "A" vs "a",
    # "Zoo" vs "zoo") so a case-insensitive dept key cannot match this order.
    depts = ["Eng", "eng", "Sales", "Ops", "HR", "A", "a", "Z", "Zoo", "zoo"]
    for _ in range(200):
        n = rng.randint(0, 30)
        inp = [
            {
                "name": rng.choice(["Ana", "Bob", "Cara", "amy", "Zed", "Bob"]),
                "dept": rng.choice(depts),
                "salary": rng.randint(-50, 50),
            }
            for _ in range(n)
        ]
        out = solution.order_roster(inp)
        assert len(out) == len(inp)
        for x, y in zip(out, out[1:]):
            kx = (x["dept"], -x["salary"], x["name"])
            ky = (y["dept"], -y["salary"], y["name"])
            assert kx <= ky
