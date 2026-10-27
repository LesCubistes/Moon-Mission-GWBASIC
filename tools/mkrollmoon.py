"""The title's earthrise over a rolling moonscape: the ground rolls toward the viewer, away from the Earth.

The ground is one world texture that repeats every PZ in depth, pre-drawn (and pre-dithered, once for
even and once for odd screen rows) in 10 depth bands, each at its own width scale. Every frame each
screen row copies the texture row for its depth plus the distance travelled. The hilly, curved skyline
is fixed: the rows with sky in them are combined through masks, so the stars and the rising Earth stay.
Writes BUILDDIR/ROLL.DAT and ROLL.BIN (asm/roll.asm, assembled here with nasm) for MOON.BAS, and given OUT.gif a
preview drawn by a Python copy of the machine code.
usage: mkrollmoon.py BUILDDIR [OUT.gif]   (BUILDDIR holds MOONBG.PIC, EARTH.SPR, TITLE.SPR, CREDIT.SPR)
"""
import sys, os, math, random, struct
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

B = sys.argv[1]
OUTGIF = sys.argv[2] if len(sys.argv) > 2 else ""
PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], np.uint8)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
W, H = 320, 200
EX, EY, HT, EW, EH = 112, 33, 126, 96, 80

def load_pic(path):
    mem = open(path, "rb").read()[7:7 + 16384]
    px = np.zeros((H, W), np.uint8)
    for y in range(H):
        o = (y & 1) * 0x2000 + (y >> 1) * 80
        for i in range(80):
            b = mem[o + i]
            px[y, i * 4:i * 4 + 4] = (b >> 6 & 3, b >> 4 & 3, b >> 2 & 3, b & 3)
    return px

def spr(path):
    d = open(path, "rb").read()[7:]
    wb, h = struct.unpack("<HH", d[:4]); w = wb // 2; rb = (wb + 7) // 8
    a = np.zeros((h, w), np.uint8)
    for y in range(h):
        row = d[4 + y * rb:4 + (y + 1) * rb]
        for x in range(w):
            a[y, x] = row[x // 4] >> (6 - 2 * (x % 4)) & 3
    return a

# ---------- the fixed skyline: the same curved, hilly horizon as MOONBG.PIC ----------
x = np.arange(W)
hz = HT - 1 + 3 * np.sin(x / 37.0) + 2 * np.sin(x / 13.0 + 1.3) + 1.5 * np.sin(x / 5.3)
SAG = 10
limb = HT + SAG * ((x - 159.5) / 160.0) ** 2
hz = hz + limb - HT
lo, hi = EX - 6, EX + EW + 5
for i in range(1, 15):
    t = i / 15
    if lo - i >= 0: hz[lo - i] = limb[lo - i] * (1 - t) + hz[lo - i] * t
    if hi + i < 320: hz[hi + i] = limb[hi + i] * (1 - t) + hz[hi + i] * t
hz[lo:hi + 1] = limb[lo:hi + 1]
hz = np.round(hz).astype(int)
Y0 = int(hz.min())                       # first screen row with any ground
NR = H - Y0                              # ground rows
R0 = 20                                  # perspective: near rows slide (NR + R0) / R0 times faster than the skyline

# ---------- one world texture, repeating every PZ in depth, sampled into depth bands ----------
PZ = 64                                  # world depth period (the loop)
F = 300.0                                # focal length in pixels
rng = random.Random(1969)
craters = []
for n, rr in ((6, (5, 9)), (22, (2.2, 5)), (50, (0.9, 2.2))):
    for _ in range(n):
        craters.append((rng.uniform(-180, 180), rng.uniform(0, PZ), rng.uniform(*rr)))
craters.sort(key=lambda c: c[2])                   # small first: bigger craters paint over them
def zw(r): return F * R0 / (r + R0)                # world depth of row r (row 0 = skyline)
TZ = 2 * math.pi / PZ
ph = [rng.uniform(0, 6.3) for _ in range(8)]

def shade_row(X, Z):
    mare = np.sin(X / 37 + Z * TZ * 1 + ph[0]) + 0.7 * np.sin(X / 13 + Z * TZ * 2 + ph[1]) + 0.5 * np.sin(-X / 23 + Z * TZ * 3 + ph[2])
    s = 0.58 - 0.26 * np.clip((mare - 0.3) * 1.2, 0, 1) + 0.12 * np.clip((-0.6 - mare), 0, 1)
    s = s + 0.05 * np.sin(X / 4.1 + Z * TZ * 5 + ph[3])
    for cx, cz, cr in craters:
        dz = (Z - cz + PZ / 2) % PZ - PZ / 2
        v = dz / cr
        if abs(v) > 1.9: continue
        u = (X - cx) / cr
        d = np.hypot(u, v)
        s = np.where(d < 1.9, s + 0.07 * (1.9 - d) * (cr > 4), s)
        s = np.where(d < 1.22, np.where(u < 0.1, 0.88, 0.22), s)
        val = np.where((u < -0.05) & (d > 0.25 - 0.3 * u), 0.02, np.where((u > 0.15) & (d > 0.62), 0.92, 0.40 + 0.15 * u))
        s = np.where(d < 1.0, val, s)
    return s

D42 = np.array([[0, 4, 2, 6], [5, 1, 7, 3]]) / 8.0 + 1 / 16   # 4x2 ordered dither: only two row phases
NB = 10                                  # depth bands: each has its own horizontal scale
edges = [int(round((R0 * (NR + R0) / R0) ** (i / NB) * R0 ** (1 - i / NB))) - R0 for i in range(NB + 1)]
edges[0], edges[-1] = 0, NR
band_of = np.zeros(NR, int); bands = []
xs = np.arange(W)
for b in range(NB):
    ra, rb = edges[b], edges[b + 1]
    rc = (ra + rb - 1) / 2
    zc = zw(rc); dens = (rc + R0) ** 2 / (F * R0)
    hb = max(1, int(round(PZ * dens)))
    img = np.zeros((2, hb, W), np.uint8)               # two copies: dithered for even and for odd screen rows
    X = (xs - 160) * zc / F
    for j in range(hb):
        sh = shade_row(X, j * PZ / hb)
        for k in range(2): img[k, j] = np.where(sh > D42[k, xs % 4], 3, 0)
    bands.append(img); band_of[ra:rb] = b
mem = sum(b.shape[1] for b in bands) * 80 * 2
print("ground rows", NR, "from y", Y0, "; bands", edges, "; texture bytes:", mem)

# ---------- ROLL.DAT: the layout asm/roll.asm reads ----------
SPEED = 0.6                                         # world depth per step (one step per clock tick, 18.2 a second)
NM = int(hz.max()) - Y0 + 1                         # rows with some sky in them
assert Y0 + NM <= 146, "part-sky rows must stay above the menu box"
NB = len(bands)
data = bytearray(0x1800)
struct.pack_into("<4H", data, 0, NR, Y0, NM, NB)
tex = bytearray(); taddr = []
def pack(row):
    b = (row[0::4] << 6) | (row[1::4] << 4) | (row[2::4] << 2) | row[3::4]
    return b.astype(np.uint8).tobytes()
for b, img in enumerate(bands):
    hb = img.shape[1]
    struct.pack_into("<3H", data, 0x40 + 8 * b, 0, int(round(SPEED * hb / PZ * 256)), hb * 256)
    addr = []
    for k in range(2):
        addr.append(0x1800 + len(tex))
        for j in range(hb): tex += pack(img[k, j])
    taddr.append(addr)
for r in range(NR):
    b = band_of[r]; hb = bands[b].shape[1]
    A = int(round(zw(r) * hb / PZ * 256)) % (hb * 256)
    struct.pack_into("<4H", data, 0x100 + 8 * r, taddr[b][0], taddr[b][1], 0x40 + 8 * b, A)
assert 0x100 + 8 * NR <= 0x400 and 0x400 + 240 * NM <= 0x1800
for r in range(NM):
    y = Y0 + r
    sky_ = np.where(y < hz, 3, 0).astype(np.uint8)
    gnd = np.where(y > hz, 3, 0).astype(np.uint8)
    lip = np.where(y == hz, 3, 0).astype(np.uint8)
    data[0x400 + 240 * r:0x400 + 240 * r + 240] = pack(sky_) + pack(gnd) + pack(lip)
data += tex
earth_spr = spr(f"{B}/EARTH.SPR")              # 82 rows: the Earth and two black rows that wipe its trail
assert earth_spr.shape == (82, 96)
struct.pack_into("<H", data, 0x3E, len(data))
for row in earth_spr: data += pack(row)
assert len(data) <= 65536 - 16, len(data)
with open(f"{B}/ROLL.DAT", "wb") as fh:
    fh.write(bytes([0xFD]) + struct.pack("<HHH", 0, 0, len(data)) + bytes(data) + b"\x1a")
print("ROLL.DAT", len(data), "bytes; part-sky rows", NM)
import subprocess, tempfile
with tempfile.TemporaryDirectory() as td:            # assemble asm/roll.asm (needs nasm)
    subprocess.run(["nasm", "-f", "bin", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "asm", "roll.asm"),
                    "-o", f"{td}/roll.bin"], check=True)
    code = open(f"{td}/roll.bin", "rb").read()
assert len(code) <= 500, "ROLL.BIN must fit in RC(249) in MOON.BAS"
code += b"\0" * (len(code) & 1)
with open(f"{B}/ROLL.BIN", "wb") as fh:
    fh.write(bytes([0xFD]) + struct.pack("<HHH", 0, 0, len(code)) + code + b"\x1a")

# ---------- a Python copy of the machine code, frame by frame ----------
def unpack(bs):
    a = np.frombuffer(bytes(bs), np.uint8)
    return np.stack([a >> 6 & 3, a >> 4 & 3, a >> 2 & 3, a & 3], 1).ravel()

def step(mem, scr, boxes, ey=-1, n=1):
    """mem: bytearray ROLL.DAT image; scr: 200x320 pixels, changed in place"""
    nr, y0, nm, nb = struct.unpack_from("<4H", mem, 0)
    if ey >= 0:
        ea = struct.unpack_from("<H", mem, 0x3E)[0]
        for i in range(min(82, 126 - ey)):
            scr[ey + i, 112:208] = unpack(mem[ea + 24 * i:ea + 24 * i + 24])
    for b in [b for _ in range(n) for b in range(nb)]:
        ph, st, top = struct.unpack_from("<3H", mem, 0x40 + 8 * b)
        ph += st
        if ph >= top: ph -= top
        struct.pack_into("<H", mem, 0x40 + 8 * b, ph)
    for r in range(nr):
        y = y0 + r
        c0, c1, bo, A = struct.unpack_from("<4H", mem, 0x100 + 8 * r)
        ph, st, top = struct.unpack_from("<3H", mem, bo)
        j = A + ph
        if j >= top: j -= top
        src = (c1 if y & 1 else c0) + (j >> 8) * 80
        row = unpack(mem[src:src + 80])
        if r < nm:
            m = 0x400 + 240 * r
            sk, gn, lp = (unpack(mem[m + 80 * i:m + 80 * i + 80]) for i in range(3))
            scr[y] = (scr[y] & sk) | (row & gn) | lp
        else:
            keep = np.zeros(W, bool)
            for (ya, yb, ba, bb) in boxes:
                if ya <= y <= yb: keep[4 * ba:4 * bb] = True
            scr[y, ~keep] = row[~keep]

if OUTGIF:
    bg = load_pic(f"{B}/MOONBG.PIC")
    earth = spr(f"{B}/EARTH.SPR")[:EH]
    title = spr(f"{B}/TITLE.SPR"); cred = spr(f"{B}/CREDIT.SPR")
    mem = bytearray(data)
    px = bg.copy()
    FPS = 18
    frames = []
    for f in range(12 * FPS):
        t = f / FPS
        k = min(1, max(0, (t - 1.5) / 7.5)); k = 1 - (1 - k) ** 2
        ey = int(round(HT - (HT - EY) * k))
        step(mem, px, [], ey if ey < HT else -1)
        out = px.copy()
        if t > 9.5:
            th, tw = title.shape; out[6:6 + th, 24:24 + tw][title > 0] = title[title > 0]
            ch, cw = cred.shape; out[34:34 + ch, 216:216 + cw][cred > 0] = cred[cred > 0]
        if f % 3 == 0: frames.append(Image.fromarray(PAL[out]).resize((640, 480), Image.NEAREST))
    frames[0].save(OUTGIF, save_all=True, append_images=frames[1:], duration=int(3000 / FPS), loop=0)
    frames[-1].save(OUTGIF.replace(".gif", ".png"))
    print("frames", len(frames))
