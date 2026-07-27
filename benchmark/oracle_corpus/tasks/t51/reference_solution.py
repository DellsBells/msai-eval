def capped_keystroke_distance(a: str, b: str, cap: int) -> int:
    la, lb = len(a), len(b)

    # Standard edit-distance DP with substitution cost 2, indel cost 1.
    # prev[j] = distance between a[:i] and b[:j].
    prev = list(range(lb + 1))  # a="" vs b[:j] -> j inserts
    for i in range(1, la + 1):
        curr = [i] + [0] * lb  # a[:i] vs b="" -> i deletes
        ai = a[i - 1]
        for j in range(1, lb + 1):
            if ai == b[j - 1]:
                sub = prev[j - 1]  # free match
            else:
                sub = prev[j - 1] + 2  # substitution cost 2
            delete = prev[j] + 1
            insert = curr[j - 1] + 1
            curr[j] = min(sub, delete, insert)
        prev = curr

    d = prev[lb]
    if d > cap:
        return -1
    return d
