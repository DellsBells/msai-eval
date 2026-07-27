def rle_encode(text):
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        j = i
        while j < n and text[j] == c:
            j += 1
        run = j - i
        if run >= 4:
            out.append("#")
            out.append(str(run))
            out.append("#")
            out.append(c)
        else:
            if c == "#":
                out.append("##" * run)
            else:
                out.append(c * run)
        i = j
    return "".join(out)


def rle_decode(code):
    out = []
    i = 0
    n = len(code)
    while i < n:
        c = code[i]
        if c == "#":
            # Escaped literal '#' if the next char is also '#'.
            if i + 1 < n and code[i + 1] == "#":
                out.append("#")
                i += 2
                continue
            # Compressed token: #<count>#<char>
            j = i + 1
            digits = []
            while j < n and code[j].isdigit():
                digits.append(code[j])
                j += 1
            count = int("".join(digits))
            # code[j] is the separator '#'; code[j+1] is the repeated char.
            repeated = code[j + 1]
            out.append(repeated * count)
            i = j + 2
        else:
            out.append(c)
            i += 1
    return "".join(out)
