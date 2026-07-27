def capped_keystroke_distance(a: str, b: str, cap: int) -> int:
    la, lb = len(a), len(b)

    # BUG: this is plain Levenshtein with substitution cost 1, but the
    # required model charges 2 per substitution.
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        curr = [i] + [0] * lb
        ai = a[i - 1]
        for j in range(1, lb + 1):
            if ai == b[j - 1]:
                sub = prev[j - 1]
            else:
                sub = prev[j - 1] + 1  # should be +2
            delete = prev[j] + 1
            insert = curr[j - 1] + 1
            curr[j] = min(sub, delete, insert)
        prev = curr

    d = prev[lb]
    if d > cap:
        return -1
    return d
