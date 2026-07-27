def to_factoradic(n: int) -> list:
    if n == 0:
        return [0]
    fact = 1
    k = 1
    while fact * (k + 1) <= n:
        k += 1
        fact *= k
    digits = []
    for place in range(k, -1, -1):
        digit = n // fact
        digits.append(digit)
        n -= digit * fact
        if place > 0:
            fact //= place
    return digits


def from_factoradic(digits: list) -> int:
    # Plausible but wrong: the place-value factorial is advanced BEFORE it is
    # used, so the rightmost digit is treated as place 1! instead of 0!.
    if not digits:
        return 0
    total = 0
    fact = 1
    for j, digit in enumerate(reversed(digits)):
        fact *= (j + 1)      # off-by-one: gives 1!, 2!, 3!, ... instead of 0!, 1!, 2!, ...
        total += digit * fact
    return total
