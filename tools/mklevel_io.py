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


def pad_patches(px, g, pads):
    """Mark landing pads as flat shaded patches instead of decks, beacons and labels.
    pads: [(left x, right x, multiplier)]. Lowest multiplier (easiest) = black,
    middle = dark grey (25% dots), highest (hardest) = solid grey."""
    order = sorted(pads, key=lambda p: p[2])
    shades = {order[0][2]: 0, order[len(order) // 2][2]: 1, order[-1][2]: 2}
    for a, b, m in pads:
        L = int(g[a])
        for e in (a, b):                         # clear the old beacon posts back to sky
            px[max(0, L - 6):L - 2, e] = 0
        px[L, a:b + 1] = 3                       # keep the surface line
        s = shades[m]
        for y in range(L + 1, min(L + 8, 200)):
            for x in range(a, b + 1):
                if s == 0: v = 0
                elif s == 1: v = 3 if (x % 2 == 0 and y % 2 == 0) else 0   # 25% dark grey
                else: v = 3
                px[y, x] = v
        px[L + 1:min(L + 8, 200), a] = 3; px[L + 1:min(L + 8, 200), b] = 3   # crisp patch edges

def csm_dots(px, x, y):
    """The command/service module far overhead: a few dots (hull, nose, cyan glint)."""
    px[y, x + 1] = 3
    px[y + 1, x:x + 3] = 3
    px[y + 1, x + 3] = 1

def rle(b):
    """Pack a screen for CKPIT.BIN mode 6: FEh n v = n copies of v (n = 0 means 256), other bytes as is."""
    out = bytearray(); i = 0
    while i < len(b):
        j = i
        while j < len(b) and b[j] == b[i] and j - i < 256: j += 1
        n = j - i
        if n >= 4 or b[i] == 0xFE: out += bytes([0xFE, n & 255, b[i]]); i = j
        else: out.append(b[i]); i += 1
    return bytes(out)

def unrle(p):
    out = bytearray(); i = 0
    while len(out) < 16384:
        if p[i] == 0xFE: n = p[i + 1] or 256; out += bytes([p[i + 2]]) * n; i += 3
        else: out.append(p[i]); i += 1
    return bytes(out)
