def encode(data: bytes) -> bytes:
    if not data:
        return b""
    
    result = []
    count = 1
    
    for i in range(1, len(data)):
        if data[i] == data[i - 1]:
            count += 1
        else:
            result.extend([count.to_bytes(1, 'big'), data[i - 1]])
            count = 1
    
    # Add the last run
    result.extend([count.to_bytes(1, 'big'), data[-1]])
    
    return b''.join(result)