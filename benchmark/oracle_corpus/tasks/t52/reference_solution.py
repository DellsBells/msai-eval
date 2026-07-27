def _longest_block(a: str, b: str):
    """Return (k, i, j): length and start indices of the longest common
    contiguous substring. Tie-break: smallest i, then smallest j. Returns
    (0, 0, 0) if there is no shared character."""
    la, lb = len(a), len(b)
    best_k = 0
    best_i = 0
    best_j = 0
    if la == 0 or lb == 0:
        return (0, 0, 0)

    # dp over common suffix lengths, rolling by rows of a.
    prev = [0] * (lb + 1)
    for ia in range(la):
        curr = [0] * (lb + 1)
        ca = a[ia]
        for jb in range(lb):
            if ca == b[jb]:
                run = prev[jb] + 1
                curr[jb + 1] = run
                if run > best_k:
                    # block ends at (ia, jb); start indices are back run-1
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
    total = len(a) + len(b)
    if total == 0:
        return 1.0
    m = _matched(a, b)
    return round(2.0 * m / total, 4)
