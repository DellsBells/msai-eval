def pack(fields):
    def escape_field(field):
        return field.replace('\\', '\\\\').replace('|', '\\|')
    
    escaped_fields = map(escape_field, fields)
    return '|'.join(escaped_fields)

def unpack(frame):
    fields = []
    current_field = []
    i = 0
    while i < len(frame):
        if frame[i] == '\\':
            if i + 1 < len(frame):
                current_field.append(frame[i + 1])
                i += 2
        elif frame[i] == '|':
            fields.append(''.join(current_field))
            current_field = []
            i += 1
        else:
            current_field.append(frame[i])
            i += 1
    fields.append(''.join(current_field))
    return fields