def residue_mod(digits: list, base: int, d: int) -> int:
    # Plausible but wrong: applies Horner's method to the digits in
    # least-significant-first order (reversed), which does not reconstruct
    # the same integer.
    r = 0
    b = base % d
    for digit in reversed(digits):
        r = (r * b + (digit % d)) % d
    return r % d
