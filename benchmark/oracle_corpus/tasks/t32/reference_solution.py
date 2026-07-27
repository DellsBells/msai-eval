def to_balanced_ternary(n: int) -> list:
    if n == 0:
        return [0]
    digits = []  # least-significant first while building
    while n != 0:
        rem = n % 3          # 0, 1, or 2 (Python floor mod, n may be negative)
        n //= 3
        if rem == 2:
            rem = -1
            n += 1           # borrow: 2 becomes -1 with a carry into next place
        digits.append(rem)
    digits.reverse()         # most-significant first
    return digits


def from_balanced_ternary(digits: list) -> int:
    total = 0
    for dg in digits:        # most-significant first
        total = total * 3 + dg
    return total


def _normalize(least_first: list) -> list:
    # Given a list of column values (already digits in {-1,0,1}) in
    # least-significant-first order, strip leading zeros and return canonical
    # most-significant-first form.
    ms_first = list(reversed(least_first))
    i = 0
    while i < len(ms_first) - 1 and ms_first[i] == 0:
        i += 1
    ms_first = ms_first[i:]
    if not ms_first:
        return [0]
    return ms_first


def add_balanced_ternary(a: list, b: list) -> list:
    ra = list(reversed(a))   # least-significant first
    rb = list(reversed(b))
    length = max(len(ra), len(rb))
    carry = 0
    out = []                 # least-significant first
    for i in range(length):
        da = ra[i] if i < len(ra) else 0
        db = rb[i] if i < len(rb) else 0
        s = da + db + carry  # in range -3..3
        # reduce to balanced-ternary digit + carry
        if s == -3:
            digit, carry = 0, -1
        elif s == -2:
            digit, carry = 1, -1
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
            # carry magnitude is never > 1 here, but keep it robust
            if s == -3:
                out.append(0); carry = -1
            elif s == -2:
                out.append(1); carry = -1
            elif s == 2:
                out.append(-1); carry = 1
            elif s == 3:
                out.append(0); carry = 1
            else:
                out.append(0); carry = 0
    return _normalize(out)
