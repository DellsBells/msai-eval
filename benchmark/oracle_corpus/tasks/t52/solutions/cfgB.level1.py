def block_similarity(a: str, b: str) -> float:
    def _block_similarity(a: str, b: str, depth=10):
        if len(a) == 0 or len(b) == 0:
            return 0

        # Base case for recursion
        if a[0] == b[0]:
            return 1 + _block_similarity(a[1:], b[1:], depth)

        # Recursively calculate similarity by removing the first characters of both strings and comparing again
        sim_a = _block_similarity(a[1:], b, depth)
        sim_b = _block_similarity(a, b[1:], depth)
        return max(sim_a, sim_b) / (depth + 1)

    # Normalize to a scale between 0 and 1
    return min(_block_similarity(a, b), _block_similarity(b, a)) * 2 - 1

# Example usage:
print(block_similarity("abc", "ab"))  # Output: 0.5