def rle_encode(text):
    if not text:
        return ""
    
    encoded = []
    i = 0
    while i < len(text):
        char = text[i]
        count = 1
        while i + 1 < len(text) and text[i + 1] == char:
            count += 1
            i += 1
        
        if count >= 4:
            encoded.append(f"#{count}#{char}")
        else:
            encoded.append(char * count)
        
        i += 1
    
    return ''.join(encoded)

def rle_decode(code):
    if not code:
        return ""
    
    decoded = []
    i = 0
    while i < len(code):
        char = code[i]
        if char == '#':
            if i + 1 < len(code) and code[i + 1] == '#':
                decoded.append('#')
                i += 2
            else:
                i += 1
                start = i
                while i < len(code) and code[i].isdigit():
                    i += 1
                count = int(code[start:i])
                i += 1  # skip the separator '#'
                char_to_repeat = code[i]
                decoded.append(char_to_repeat * count)
                i += 1
        else:
            decoded.append(char)
            i += 1
    
    return ''.join(decoded)