"""Preview: the title's earthrise with a rolling moonscape (the ground slides past, near faster than far).

Built the way the machine code would draw it, so the preview is honest:
  - every screen row of ground is a pre-dithered strip that wraps; its length grows toward the
    viewer (L = 256 * (r + R0) / R0), so one world texture lines up across all rows
  - each frame every row is copied at its own offset (moves in 2-pixel steps, so only two
    shifted copies of the strips would be stored)
  - the hilly, curved skyline is a fixed mask; the Earth rises behind it
usage: mkrollmoon.py BUILDDIR OUT.gif   (BUILDDIR holds MOONBG.PIC, EARTH.SPR, TITLE.SPR, CREDIT.SPR)
"""
import sys, os, math, random, struct
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

B, OUTGIF = sys.argv[1], sys.argv[2]
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

# ---------- frames ----------
bg = load_pic(f"{B}/MOONBG.PIC")
sky = bg.copy()
for c in range(W): sky[hz[c]:, c] = 0               # stars only
earth = spr(f"{B}/EARTH.SPR")[:EH]
title = spr(f"{B}/TITLE.SPR"); cred = spr(f"{B}/CREDIT.SPR")
ground_mask = np.zeros((H, W), bool)
for c in range(W): ground_mask[hz[c]:, c] = True

FPS = 12
frames = []
T = 12 * FPS
SPEED = 0.9                                         # world depth per frame (positive: the ground comes toward the viewer, away from the Earth)
for f in range(T):
    px = sky.copy()
    t = f / FPS
    # Earth rises from 1.5 s to 9 s, slowing as it tops out
    k = min(1, max(0, (t - 1.5) / 7.5)); k = 1 - (1 - k) ** 2
    ey = int(round(HT - (HT - EY) * k))
    sub = px[ey:ey + EH, EX:EX + EW]
    e = earth[:sub.shape[0]]
    sub[e > 0] = e[e > 0]
    # ground: each row copies the band texture row for its depth; the ground comes toward us
    sd = f * SPEED
    for r in range(NR):
        y = Y0 + r
        img = bands[band_of[r]]; hb = img.shape[1]
        j = int(((zw(r) + sd) % PZ) * hb / PZ)
        m = ground_mask[y]
        px[y, m] = img[y & 1, j][m]
    for c in range(W): px[hz[c], c] = 3            # the bright lip of the skyline stays put
    if t > 9.5:
        th, tw = title.shape; px[6:6 + th, 24:24 + tw][title > 0] = title[title > 0]
        ch, cw = cred.shape; px[34:34 + ch, 216:216 + cw][cred > 0] = cred[cred > 0]
    frames.append(Image.fromarray(PAL[px]).resize((640, 480), Image.NEAREST))
frames[0].save(OUTGIF, save_all=True, append_images=frames[1:], duration=int(1000 / FPS), loop=0)
frames[-1].save(OUTGIF.replace(".gif", ".png"))
print("frames", len(frames))
