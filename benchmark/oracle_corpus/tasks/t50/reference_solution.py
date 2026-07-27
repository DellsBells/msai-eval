def longest_shared_run(a: str, b: str) -> tuple[int, int]:
    la, lb = len(a), len(b)
    if la == 0 or lb == 0:
        return (0, 0)

    # dp[j] = length of the longest common suffix of a[:i+1] and b[:j+1]
    # We iterate i from 0..la-1 and update a rolling 1-D array over j.
    best_len = 0
    best_start = 0  # start index in a of the best run

    prev = [0] * (lb + 1)
    for i in range(la):
        curr = [0] * (lb + 1)
        ai = a[i]
        for j in range(lb):
            if ai == b[j]:
                run = prev[j] + 1
                curr[j + 1] = run
                if run > best_len:
                    best_len = run
                    best_start = i - run + 1
                elif run == best_len:
                    cand_start = i - run + 1
                    if cand_start < best_start:
                        best_start = cand_start
        prev = curr

    if best_len == 0:
        return (0, 0)
    return (best_len, best_start)
