def to_balanced_ternary(n: int) -> list:
    if n == 0:
        return [0]
    digits = []
    while n != 0:
        rem = n % 3
        n //= 3
        if rem == 2:
            rem = -1
            n += 1
        digits.append(rem)
    digits.reverse()
    return digits


def from_balanced_ternary(digits: list) -> int:
    total = 0
    for dg in digits:
        total = total * 3 + dg
    return total


def _normalize(least_first: list) -> list:
    ms_first = list(reversed(least_first))
    i = 0
    while i < len(ms_first) - 1 and ms_first[i] == 0:
        i += 1
    ms_first = ms_first[i:]
    if not ms_first:
        return [0]
    return ms_first


def add_balanced_ternary(a: list, b: list) -> list:
    ra = list(reversed(a))
    rb = list(reversed(b))
    length = max(len(ra), len(rb))
    carry = 0
    out = []
    for i in range(length):
        da = ra[i] if i < len(ra) else 0
        db = rb[i] if i < len(rb) else 0
        s = da + db + carry
        if s == -3:
            digit, carry = 0, -1
        elif s == -2:
            # BUG: should be digit 1, carry -1. This under-carries on
            # negative columns, corrupting results that borrow.
            digit, carry = -1, 0
        elif s == -1:
            digit, carry = -1, 0
        elif s == 0:
            digit, carry = 0, 0
        elif s == 1:
            digit, carry = 1, 0
        elif s == 2:
            digit, carry = -1, 1
        else:  # s == 3
            digit, carry = 0, 1
    # NOTE: intentionally faithful to reference elsewhere except the -2 case.
        out.append(digit)
    while carry != 0:
        s = carry
        if s == 1:
            out.append(1)
            carry = 0
        elif s == -1:
            out.append(-1)
            carry = 0
        else:
            out.append(0)
            carry = 0
    return _normalize(out)
