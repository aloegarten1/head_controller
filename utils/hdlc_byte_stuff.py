def byte_stuff(data: bytes):
    ESCAPE = 0x7D
    FLAG = 0x7E
    ESCAPE_XOR = 0x20

    stuffed = bytearray()
    for byte in data:
        if byte in (ESCAPE, FLAG):
            stuffed.append(ESCAPE)
            stuffed.append(byte ^ ESCAPE_XOR)
        else:
            stuffed.append(byte)
    return bytes(stuffed)


def unstuff_bytes(data: bytes) -> bytes:
    result = bytearray()
    i = 0
    while i < len(data):
        if data[i] == 0x7D:
            i += 1
            result.append(data[i] ^ 0x20)
        else:
            result.append(data[i])
        i += 1
    return bytes(result)


def bytes2hdlc(data: bytes):
    stuffed = byte_stuff(data)
    FLAG = 0x7E
    return bytes([FLAG]) + stuffed + bytes([FLAG])
