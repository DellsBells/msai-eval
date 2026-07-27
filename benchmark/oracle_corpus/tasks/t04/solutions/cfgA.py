def to_snake(identifier: str) -> str:
    import re
    
    # Step 1: Split into words
    words = []
    for part in re.split(r'[_\-\s]+', identifier):
        if not part:
            continue
        i = 0
        while i < len(part):
            j = i + 1
            if part[i].islower() or part[i].isdigit():
                while j < len(part) and (part[j].isalnum() and not part[j].isupper()):
                    j += 1
            elif part[i].isupper():
                if j < len(part) and part[j].islower():
                    j = i + 1
                else:
                    while j < len(part) and part[j].isupper():
                        j += 1
                    if j < len(part) and part[j].islower():
                        j -= 1
            words.append(part[i:j])
            i = j
    
    # Step 2: Lowercase and join
    snake_case = '_'.join(word.lower() for word in words)
    
    return snake_case