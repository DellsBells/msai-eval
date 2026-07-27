def positional_divergence(a: str, b: str) -> int:
    # Compares only the overlapping region, forgetting that the extra
    # trailing characters of the longer string also count as differences.
    n = min(len(a), len(b))
    mismatches = 0
    for i in range(n):
        if a[i] != b[i]:
            mismatches += 1
    return mismatches
