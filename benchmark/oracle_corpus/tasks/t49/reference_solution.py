def positional_divergence(a: str, b: str) -> int:
    n = min(len(a), len(b))
    mismatches = 0
    for i in range(n):
        if a[i] != b[i]:
            mismatches += 1
    mismatches += abs(len(a) - len(b))
    return mismatches
