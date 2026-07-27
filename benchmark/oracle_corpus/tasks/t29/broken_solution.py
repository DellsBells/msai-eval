def digit_signature(n: int) -> int:
    # Plausible but wrong: weights/signs assigned from the RIGHT
    # (least significant digit first) instead of from the left.
    digits = str(n)
    total = 0
    for i, ch in enumerate(reversed(digits)):
        position = i + 1
        weight = position
        sign = 1 if position % 2 == 1 else -1
        total += sign * weight * int(ch)
    return total
