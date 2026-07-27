def positional_divergence(a: str, b: str) -> int:
    min_len = min(len(a), len(b))
    score = 0
    for i in range(min_len):
        if a[i] != b[i]:
            score += 1
    return score + abs(len(a) - len(b))