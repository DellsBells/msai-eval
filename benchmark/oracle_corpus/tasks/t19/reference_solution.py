"""Reference solution for the Tiny Stack Machine task."""


def execute(program):
    stack = []
    for instr in program:
        parts = instr.split(" ")
        op = parts[0]

        if op == "PUSH":
            stack.append(int(parts[1]))
        elif op == "POP":
            if len(stack) < 1:
                break
            stack.pop()
        elif op == "DUP":
            if len(stack) < 1:
                break
            stack.append(stack[-1])
        elif op == "NEG":
            if len(stack) < 1:
                break
            stack.append(-stack.pop())
        elif op == "SWAP":
            if len(stack) < 2:
                break
            stack[-1], stack[-2] = stack[-2], stack[-1]
        elif op in ("ADD", "SUB", "MUL"):
            if len(stack) < 2:
                break
            b = stack.pop()
            a = stack.pop()
            if op == "ADD":
                stack.append(a + b)
            elif op == "SUB":
                stack.append(a - b)
            else:  # MUL
                stack.append(a * b)
    return stack
