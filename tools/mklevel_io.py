"""CGA helpers shared by the art builders: screen BSAVE and GET-array sprites."""
import struct

def cga_bytes(px):
    mem = bytearray(16384)
    for y in range(200):
        o = (y & 1) * 0x2000 + (y >> 1) * 80
        for i in range(80):
            p = px[y, i * 4:i * 4 + 4]
            mem[o + i] = (int(p[0]) << 6) | (int(p[1]) << 4) | (int(p[2]) << 2) | int(p[3])
    return bytes(mem)

def bsave(path, data, seg=0):
    with open(path, "wb") as f:
        f.write(bytes([0xFD]) + struct.pack("<HHH", seg, 0, len(data)) + data + b"\x1a")

def sprite(px):
    h, w = px.shape
    data = bytearray(struct.pack("<HH", w * 2, h))
    rb = (w * 2 + 7) // 8
    for y in range(h):
        row = [int(v) for v in px[y]] + [0] * (rb * 4 - w)
        for i in range(rb):
            p = row[i * 4:i * 4 + 4]
            data.append((p[0] << 6) | (p[1] << 4) | (p[2] << 2) | p[3])
    if len(data) % 2: data.append(0)
    return bytes(data)

