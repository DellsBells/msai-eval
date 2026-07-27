def _longest_block(a: str, b: str):
    la, lb = len(a), len(b)
    best_k = 0
    best_i = 0
    best_j = 0
    if la == 0 or lb == 0:
        return (0, 0, 0)

    prev = [0] * (lb + 1)
    for ia in range(la):
        curr = [0] * (lb + 1)
        ca = a[ia]
        for jb in range(lb):
            if ca == b[jb]:
                run = prev[jb] + 1
                curr[jb + 1] = run
                if run > best_k:
                    best_k = run
                    best_i = ia - run + 1
                    best_j = jb - run + 1
                elif run == best_k and best_k > 0:
                    cand_i = ia - run + 1
                    cand_j = jb - run + 1
                    if (cand_i, cand_j) < (best_i, best_j):
                        best_i = cand_i
                        best_j = cand_j
        prev = curr
    return (best_k, best_i, best_j)


def _matched(a: str, b: str) -> int:
    k, i, j = _longest_block(a, b)
    if k == 0:
        return 0
    left = _matched(a[:i], b[:j])
    right = _matched(a[i + k:], b[j + k:])
    return k + left + right


def block_similarity(a: str, b: str) -> float:
    la, lb = len(a), len(b)
    if la == 0 and lb == 0:
        return 1.0
    m = _matched(a, b)
    # BUG: normalizes by the longer length instead of the average length,
    # i.e. uses M / max(la, lb) rather than 2*M / (la + lb).
    denom = max(la, lb)
    if denom == 0:
        return 0.0
    return round(m / denom, 4)
