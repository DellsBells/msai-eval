import solution

import random


def test_push_only():
    assert solution.execute(["PUSH 1", "PUSH 2", "PUSH 3"]) == [1, 2, 3]


def test_empty_program():
    assert solution.execute([]) == []


def test_add():
    assert solution.execute(["PUSH 2", "PUSH 3", "ADD"]) == [5]


def test_sub_operand_order():
    # a - b where a is below, b is on top: 10 - 4 = 6.
    assert solution.execute(["PUSH 10", "PUSH 4", "SUB"]) == [6]
    # negative result direction matters: 4 - 10 = -6.
    assert solution.execute(["PUSH 4", "PUSH 10", "SUB"]) == [-6]


def test_mul_and_dup():
    assert solution.execute(["PUSH 5", "DUP", "MUL"]) == [25]


def test_neg():
    assert solution.execute(["PUSH 7", "NEG"]) == [-7]
    assert solution.execute(["PUSH -3", "NEG"]) == [3]


def test_swap_then_sub():
    # 7,2 -> SWAP -> 2,7 -> SUB: 2 - 7 = -5
    assert solution.execute(["PUSH 7", "PUSH 2", "SWAP", "SUB"]) == [-5]


def test_pop():
    assert solution.execute(["PUSH 1", "PUSH 2", "POP"]) == [1]


def test_negative_push_literals():
    assert solution.execute(["PUSH -5", "PUSH -2", "SUB"]) == [-3]  # -5 - -2 = -3
    assert solution.execute(["PUSH -4", "PUSH 3", "MUL"]) == [-12]


def test_underflow_binary_halts_and_preserves():
    # ADD needs 2, only 1 present -> halt, stack unchanged.
    assert solution.execute(["PUSH 1", "ADD"]) == [1]
    # SUB underflow on empty stack -> []
    assert solution.execute(["SUB"]) == []


def test_underflow_unary_halts():
    assert solution.execute(["NEG"]) == []
    assert solution.execute(["DUP"]) == []
    assert solution.execute(["POP"]) == []


def test_halt_skips_later_instructions():
    # ADD underflows with a single element; later PUSH must NOT run.
    assert solution.execute(["PUSH 9", "ADD", "PUSH 100"]) == [9]


def test_swap_underflow_with_one_element():
    # SWAP needs 2; with one element it halts and leaves that element.
    assert solution.execute(["PUSH 42", "SWAP"]) == [42]


def test_chained_arithmetic():
    # (2 + 3) * 4 - 1
    prog = ["PUSH 2", "PUSH 3", "ADD", "PUSH 4", "MUL", "PUSH 1", "SUB"]
    # 2+3=5; 5*4=20; 20-1=19
    assert solution.execute(prog) == [19]


def test_dup_swap_interplay():
    # push 3, dup -> [3,3], push 8 -> [3,3,8], swap -> [3,8,3], sub: 8-3=5 -> [3,5]
    prog = ["PUSH 3", "DUP", "PUSH 8", "SWAP", "SUB"]
    assert solution.execute(prog) == [3, 5]


def _model(program):
    # Independent oracle for the property test.
    st = []
    for instr in program:
        p = instr.split(" ")
        op = p[0]
        if op == "PUSH":
            st.append(int(p[1]))
        elif op == "POP":
            if not st:
                break
            st.pop()
        elif op == "DUP":
            if not st:
                break
            st.append(st[-1])
        elif op == "NEG":
            if not st:
                break
            st.append(-st.pop())
        elif op == "SWAP":
            if len(st) < 2:
                break
            st[-1], st[-2] = st[-2], st[-1]
        elif op in ("ADD", "SUB", "MUL"):
            if len(st) < 2:
                break
            b = st.pop()
            a = st.pop()
            st.append(a + b if op == "ADD" else a - b if op == "SUB" else a * b)
    return st


def test_property_random_programs_match_model():
    rng = random.Random(424242)
    ops = ["PUSH", "POP", "DUP", "SWAP", "ADD", "SUB", "MUL", "NEG"]
    for _ in range(500):
        n = rng.randint(0, 12)
        prog = []
        for _ in range(n):
            op = rng.choice(ops)
            if op == "PUSH":
                prog.append("PUSH " + str(rng.randint(-9, 9)))
            else:
                prog.append(op)
        assert solution.execute(prog) == _model(prog)


def test_property_sub_is_left_minus_right():
    # Property: for any two literals, SUB yields a - b (below minus top).
    rng = random.Random(7)
    for _ in range(200):
        a = rng.randint(-50, 50)
        b = rng.randint(-50, 50)
        assert solution.execute([f"PUSH {a}", f"PUSH {b}", "SUB"]) == [a - b]
