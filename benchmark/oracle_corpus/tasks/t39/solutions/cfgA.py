FLAG = 0x7E
ESC = 0x7D
ESC_FLAG = 0x5E
ESC_ESC = 0x5D

def stuff(payload):
    result = bytearray()
    for byte in payload:
        if byte == FLAG:
            result.extend([ESC, ESC_FLAG])
        elif byte == ESC:
            result.extend([ESC, ESC_ESC])
        else:
            result.append(byte)
    return bytes(result)

def frame(payload):
    return stuff(payload) + bytes([FLAG])

def deframe(stream):
    frames = stream.split(bytes([FLAG]))
    payloads = []
    for body in frames[:-1]:  # Exclude the last one if it's partial
        payload = bytearray()
        i = 0
        while i < len(body):
            byte = body[i]
            if byte == ESC:
                next_byte = body[i + 1]
                if next_byte == ESC_FLAG:
                    payload.append(FLAG)
                elif next_byte == ESC_ESC:
                    payload.append(ESC)
                i += 1  # Skip the next byte as it's part of the escape sequence
            else:
                payload.append(byte)
            i += 1
        payloads.append(bytes(payload))
    return payloads