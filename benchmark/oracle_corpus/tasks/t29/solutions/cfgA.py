def digit_signature(n: int) -> int:
    digits = [int(d) for d in str(n)]
    signature = sum((i + 1) * d if i % 2 == 0 else -(i + 1) * d for i, d in enumerate(digits))
    return signature