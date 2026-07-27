# Tiny Stack Machine

Implement an interpreter for a minimal stack-based bytecode. The machine holds a
stack of integers (empty at start) and executes a program of instructions in order.

Implement a single function:

```python
def execute(program: list[str]) -> list[int]:
    ...
```

`program` is a list of instruction strings. Execute them left to right against an
initially empty integer stack, then **return the final stack contents as a list,
bottom element first, top element last** (i.e. the list in the order values were
stacked, so `stack[-1]` in your return list is the top of the stack).

## Instruction set

Each instruction is a single string. Tokens within an instruction are separated by
exactly one space.

| Instruction | Effect |
|---|---|
| `PUSH <n>` | Push integer `<n>` (a base-10 integer, possibly negative) onto the stack. |
| `POP` | Remove and discard the top element. |
| `DUP` | Duplicate the top element (push a copy of it). |
| `SWAP` | Exchange the top two elements. |
| `ADD` | Pop two elements, push their sum. |
| `SUB` | Pop two elements; push (second-from-top) minus (top). |
| `MUL` | Pop two elements, push their product. |
| `NEG` | Pop one element, push its arithmetic negation. |

### Binary operator operand order

For `ADD`, `SUB`, `MUL`: let `b` be the top element and `a` be the element just
below it. Pop both (`b` first, then `a`) and push the result of applying the
operator as `a OP b`. So for a stack `[..., a, b]` (b on top):

- `ADD` pushes `a + b`
- `SUB` pushes `a - b`
- `MUL` pushes `a * b`

## Error handling

If an instruction cannot execute because the stack does not hold enough operands
(underflow), the machine **halts immediately** and returns the stack **as it was
just before** the failing instruction was attempted — no partial effect from the
failing instruction. Specifically:

- `POP`, `DUP`, `NEG` need at least 1 element.
- `SWAP`, `ADD`, `SUB`, `MUL` need at least 2 elements.

An instruction that would underflow does not modify the stack at all; execution
stops and whatever is on the stack at that moment is the result. Instructions after
the halting point are not executed.

You may assume every instruction string is syntactically valid (a known opcode,
and `PUSH` always followed by a valid integer).

## Return value

Return the stack as a `list[int]`, bottom first. An empty stack returns `[]`.

## Examples

```python
execute(["PUSH 2", "PUSH 3", "ADD"])
# 2, 3 on stack; ADD -> 5
# -> [5]

execute(["PUSH 10", "PUSH 4", "SUB"])
# a=10, b=4 -> a-b = 6
# -> [6]

execute(["PUSH 5", "DUP", "MUL"])
# 5, 5 -> 25
# -> [25]

execute(["PUSH 1", "ADD"])
# ADD needs 2 elements but only 1 present -> halt, return stack as-is
# -> [1]

execute(["PUSH 7", "PUSH 2", "SWAP", "SUB"])
# stack 7,2 -> SWAP -> 2,7 -> SUB: a=2,b=7 -> 2-7 = -5
# -> [-5]
```
