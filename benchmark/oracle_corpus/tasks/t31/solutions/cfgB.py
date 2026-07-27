def residue_mod(digits: list[int], base: int, d: int) -> int:
    """
    Calculate the remainder when the number represented by digits is divided by d.

    Parameters:
    - digits: A list of integers representing a number in base 'base'.
    - base: The base of the number system.
    - d: The divisor for finding the residue modulo operation.

    Returns:
    - An integer, the remainder of the division of the number represented by digits
      by d.
    """
    # Convert the list of digits to a number in base 'base'
    num = int(''.join(map(str, digits)), base)
    
    # Calculate the residue modulo 'd'
    return num % d

# Example usage:
print(residue_mod([4, 0, 5], 10, 7))  # Output: 2