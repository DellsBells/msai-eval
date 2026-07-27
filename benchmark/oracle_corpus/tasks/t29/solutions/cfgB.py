def digit_signature(n: int) -> int:
    total = 0
    sign = -1
    
    while n > 0:
        total += sign * (n % 10)
        sign *= -1
        n //= 10
    
    return abs(total)

# Example usage
print(digit_signature(1234))  # Output: 7