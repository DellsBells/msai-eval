def to_factoradic(n: int) -> list:
    if n == 0:
        return [0]
    # Determine the largest k with k! <= n.
    fact = 1
    k = 1
    # fact currently == k! for k=1 (1! = 1)
    while fact * (k + 1) <= n:
        k += 1
        fact *= k
    # Now fact == k! is the largest factorial <= n.
    digits = []
    for place in range(k, -1, -1):
        # place-value is place! ; we have fact == place! at the top of the loop.
        digit = n // fact
        digits.append(digit)
        n -= digit * fact
        if place > 0:
            fact //= place  # go from place! down to (place-1)!
    return digits


def from_factoradic(digits: list) -> int:
    if not digits:
        return 0
    total = 0
    fact = 1  # will hold j! for the current place j (from the right)
    # Iterate from least significant (rightmost) to most significant.
    for j, digit in enumerate(reversed(digits)):
        if j == 0:
            fact = 1  # 0! = 1
        else:
            fact *= j  # j! = (j-1)! * j
        total += digit * fact
    return total
