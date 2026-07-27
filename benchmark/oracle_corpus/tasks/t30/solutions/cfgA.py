def to_factoradic(n: int) -> list[int]:
    if n == 0:
        return [0]
    
    digits = []
    i = 1
    while n > 0:
        n, remainder = divmod(n, i)
        digits.append(remainder)
        i += 1
    
    return digits[::-1]

def from_factoradic(digits: list[int]) -> int:
    if not digits:
        return 0
    
    n = 0
    factorial = 1
    for digit in reversed(digits):
        n += digit * factorial
        factorial *= len(digits) - (digits.index(digit) + 1)
    
    return n