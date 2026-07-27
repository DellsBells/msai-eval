def residue_mod(digits: list, base: int, d: int) -> int:
    # Horner's method under the modulus:
    # process digits most-significant first, r = (r * base + digit) mod d.
    r = 0
    b = base % d
    for digit in digits:
        r = (r * b + (digit % d)) % d
    return r % d
