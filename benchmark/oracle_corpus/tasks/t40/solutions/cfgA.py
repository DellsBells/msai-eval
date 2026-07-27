def encode(data):
    if not data:
        return b""
    
    encoded = []
    i = 0
    while i < len(data):
        start = i
        byte_value = data[i]
        while i < len(data) and data[i] == byte_value:
            i += 1
        run_length = i - start
        
        if run_length <= 127:
            encoded.append(bytes([run_length, byte_value]))
        else:
            while run_length > 32767:
                encoded.append(b'\x80\x7f' + bytes([byte_value]))
                run_length -= 32767
            if run_length <= 127:
                encoded.append(bytes([run_length, byte_value]))
            else:
                encoded.append(bytes([0x80 | (run_length >> 8), run_length & 0xFF, byte_value]))
    
    return b"".join(encoded)

def decode(blob):
    if not blob:
        return b""
    
    decoded = []
    i = 0
    while i < len(blob):
        first_byte = blob[i]
        if first_byte < 128:
            run_length = first_byte
            byte_value = blob[i + 1]
            decoded.append(byte_value * run_length)
            i += 2
        else:
            run_length = ((first_byte & 0x7F) << 8) | blob[i + 1]
            byte_value = blob[i + 2]
            decoded.append(byte_value * run_length)
            i += 3
    
    return b"".join(decoded)