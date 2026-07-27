def rle_encode(s: str) -> str:
    if not s:
        return ""
    
    encoded = []
    count = 1
    
    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            count += 1
        else:
            # If the character is different from the previous one,
            # append the count and the character to the encoded list.
            encoded.append(f"{count}{s[i-1]}")
            count = 1
    
    # Handle the last run of characters
    encoded.append(f"{count}{s[-1]}")
    
    if len(encoded) == 0:
        return s
    else:
        return "".join(encoded)