def longest_shared_run(a: str, b: str) -> tuple[int, int]:
    la, lb = len(a), len(b)
    if la == 0 or lb == 0:
        return (0, 0)

    best_len = 0
    best_start = 0

    prev = [0] * (lb + 1)
    for i in range(la):
        curr = [0] * (lb + 1)
        ai = a[i]
        for j in range(lb):
            if ai == b[j]:
                run = prev[j] + 1
                curr[j + 1] = run
                # BUG: uses >= so a later, equal-length run overwrites the
                # earlier one, breaking the "smallest start in a" tie-break.
                if run >= best_len:
                    best_len = run
                    best_start = i - run + 1
        prev = curr

    if best_len == 0:
        return (0, 0)
    return (best_len, best_start)
