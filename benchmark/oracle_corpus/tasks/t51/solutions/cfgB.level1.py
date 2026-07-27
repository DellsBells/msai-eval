def capped_keystroke_distance(a: str, b: str, cap: int) -> int:
    from Levenshtein import distance as levenshtein_distance

    def _capped_distance(s1, s2):
        return min(levenshtein_distance(s1, s2), cap)

    result = 0
    for char_a, char_b in zip(a, b):
        result += _capped_distance(char_a, char_b)
    
    # Handle remaining characters after the shortest string ends
    while a:
        result += _capped_distance(a[0], "")
        a = a[1:]
    while b:
        result += _capped_distance(b[0], "")
        b = b[1:]

    return min(result, cap)

# Example usage:
# print(capped_keystroke_distance("abc", "def", 3)) # Output: 6