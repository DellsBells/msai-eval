def pack(fields):
    return "|".join(field.replace("|", "\\\\").replace("\\", "\\\\\\\\") for field in fields)