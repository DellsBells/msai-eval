def execute(program: list[str]) -> list[int]:
    stack = []
    
    for instruction in program:
        parts = instruction.split()
        opcode = parts[0]
        
        if opcode == "PUSH":
            n = int(parts[1])
            stack.append(n)
        elif opcode == "POP":
            if len(stack) < 1:
                break
            stack.pop()
        elif opcode == "DUP":
            if len(stack) < 1:
                break
            stack.append(stack[-1])
        elif opcode == "SWAP":
            if len(stack) < 2:
                break
            stack[-1], stack[-2] = stack[-2], stack[-1]
        elif opcode == "ADD":
            if len(stack) < 2:
                break
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
        elif opcode == "SUB":
            if len(stack) < 2:
                break
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)
        elif opcode == "MUL":
            if len(stack) < 2:
                break
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)
        elif opcode == "NEG":
            if len(stack) < 1:
                break
            n = stack.pop()
            stack.append(-n)
    
    return stack