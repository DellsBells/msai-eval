def positional_divergence(a: str, b: str) -> int:
    score = 0
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            score += 1
    return score

# Example usage:
# print(positional_divergence("abcde", "ace"))  # Output: 2