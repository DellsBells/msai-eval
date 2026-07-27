def digit_signature(n: int) -> int:
    digits = str(n)
    total = 0
    for i, ch in enumerate(digits):
        position = i + 1          # 1-based position from the left
        weight = position
        sign = 1 if position % 2 == 1 else -1
        total += sign * weight * int(ch)
    return total
