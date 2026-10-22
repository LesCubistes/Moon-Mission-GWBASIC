"""Game assets for the success ending: the view out of the commander's window.

Writes to OUTDIR:
  COCKPIT.PIC   the cockpit (window frame, visor edge, glove on the throttle, glass panels), window black
  CKPIT.BIN     the machine-code helper that draws the window view (asm/ckpit.asm, BSAVE'd)
  CKCOM.DAT     shared part of the scenery segment (black row, window rows, slide speeds, dust)  -> offset 3100h
  CK1.DAT .. CK3.DAT   per-site scenery: ground strip, rim strip, horizon tables              -> offset 0
  preview_ckpit_<site>.gif   with --preview: a descent drawn by a Python copy of the machine code
Usage: mkckpit.py OUTDIR [ckpit.bin] [--preview]
"""
import sys, os, math, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcockpit as M
from mklevel_io import cga_bytes, bsave

PREVIEW = "--preview" in sys.argv
ARGS = [a for a in sys.argv[1:] if a != "--preview"]
OUT = ARGS[0]
BIN = ARGS[1] if len(ARGS) > 1 else os.path.join(os.path.dirname(__file__), "..", "asm", "ckpit.bin")
SW = 256                     # strips are 256 px wide and wrap, so the land can slide any distance
GR, RR = 64, 128             # ground rows, rim rows
BAYER = M.BAYER
ZM = 40                      # altitude (game px) where the descent view starts high
T = 2 * math.pi / SW

def smooth_p(h, scale, seed):
    """smooth noise that wraps left/right over SW"""
    from PIL import Image
    gw = SW // scale; gh = h // scale + 3
    r = np.random.default_rng(seed).random((gh, gw))
    r3 = np.concatenate([r, r, r], axis=1)
    img = Image.fromarray((r3 * 255).astype(np.uint8)).resize((gw * 3 * scale, gh * scale), Image.BICUBIC)
    a = np.asarray(img).astype(float) / 255
    return a[:h, SW:2 * SW]

def wrapd(a, b):                                   # signed wrapped distance
    d = (a - b) % SW
    return np.where(d > SW / 2, d - SW, d)

# ---------------- per-site strips ----------------
def rim_profile(fn):
    top = np.array([fn(x) for x in range(180)], float)
    top = np.convolve(np.pad(top, 3, mode="edge"), np.ones(7) / 7, "valid")        # smooth the 1-px steps
    p = np.zeros(SW)
    p[:180] = top
    for x in range(180, SW):                        # ease from the right edge back round to the left edge
        u = (x - 179) / (SW - 179)
        w = (1 - math.cos(math.pi * u)) / 2
        p[x] = top[179] * (1 - w) + top[0] * w
    return p

def rim_strip(fn, seed):
    topf = rim_profile(fn); top = np.round(topf).astype(int)
    ys, xs = np.mgrid[0:RR, 0:SW]
    th = BAYER[ys % 4, xs % 4]
    body = ys >= top[None, :]
    lit = 0.55 - 0.35 * np.clip((ys - top[None, :]) / 20, 0, 1) + 0.15 * (smooth_p(RR, 8, seed) - .5)
    slope = np.gradient(topf)[None, :]
    lit = lit + np.where(slope < 0, -0.2, 0.12)
    s = np.zeros((RR, SW), np.uint8)
    s[body & (lit > th)] = 3
    s[ys == top[None, :]] = 3
    return s

def hummocks(bands):
    def f(s, xs, ys, th, rng):
        for row, amp, k, phase in bands:
            top = row + amp * np.sin(xs * T * k + phase)
            s[(ys > top - 3) & (ys < top)] = 3
            s[(ys >= top) & (ys < top + 3) & (th < .75)] = 0
    return f

def rille(s, xs, ys, th, rng):                      # Hadley: the dark winding rille across the middle ground
    mid = 40 + 6 * np.sin(xs * T * 2 + 1) + 3 * np.sin(xs * T + 2)
    half = 5 + 1.5 * np.sin(xs * T * 3)
    band = np.abs(ys - mid) < half
    s[band] = 0
    s[band & (ys < mid - 1) & (th < .5)] = 3
    s[np.abs(ys - (mid - half)) < 1] = 3

def ground_strip(seed, features, base, pieces):
    ys, xs = np.mgrid[0:GR, 0:SW]
    th = BAYER[ys % 4, xs % 4]
    rng = np.random.default_rng(seed)
    d = np.clip(ys / 110, 0, 1)
    dens = base - 0.30 * d + 0.18 * (smooth_p(GR, 16, seed) - .5) + 0.08 * (smooth_p(GR, 4, seed + 1) - .5)
    s = np.zeros((GR, SW), np.uint8)
    s[dens > th] = 3
    s[0:2, :] = 3
    for _ in range(18):                                 # small pits
        cy = rng.uniform(4, GR); cx = rng.uniform(0, SW)
        r = 1 + 2.2 * (cy / 110) * rng.uniform(.5, 1.3)
        rx, ry = r, r * (0.25 + 0.5 * cy / 110)
        dx = wrapd(xs, cx)
        m = (dx / rx) ** 2 + ((ys - cy) / ry) ** 2
        s[m < 1] = 0
        s[(m < 1) & (dx > rx * .2) & (th < .5)] = 3
        s[(m >= 1) & (m < 1.6) & (dx > -rx * .2)] = 3
    for f in features: f(s, xs, ys, th, rng)
    for kind, wx, row in pieces:                        # the bigger craters and boulders
        if row >= GR: continue
        z = 0 if row < 14 else (1 if row < 30 else 2)
        sp = M.PIECES[(kind, z)]
        h, w = sp.shape
        for r in range(h):
            for c in range(w):
                v = sp[r, c]
                if v != 255 and row + r < GR: s[row + r, (wx + c) % SW] = v
    return s

import random as _r
def scatter(seed, n, mix):
    g = _r.Random(seed)
    return [(g.choice(mix), g.randrange(0, SW), int(4 + 46 * g.random() ** 1.2)) for _ in range(n)]

SITES = [
    ("tranquility", M.rim_tranq, 34, 0.42, [], scatter(1, 16, ("crater",) * 5 + ("boulder",))),
    ("fra_mauro", M.rim_fra, 34, 0.66, [hummocks(((22, 3, 2, 0), (40, 4, 1, 2)))], scatter(2, 12, ("boulder",) * 3 + ("crater",))),
    ("hadley", M.rim_hadley, 60, 0.54, [rille], scatter(3, 9, ("crater", "boulder"))),
]

def tables(foot):
    hz = np.zeros(128, np.uint8); ro = np.zeros(128, np.uint8)
    for z in range(128):
        t = 1 - (min(z, ZM) / ZM) ** 0.7                # 0 high .. 1 touchdown
        h = int(round(88 - 44 * t ** 0.8))
        hz[z] = h; ro[z] = foot + int(round(4 + 12 * t))
    return hz, ro

def pack(strip):                                        # 2bpp, 4 px per byte, high bits = left pixel
    s = strip.astype(np.uint8)
    b = (s[:, 0::4] << 6) | (s[:, 1::4] << 4) | (s[:, 2::4] << 2) | s[:, 3::4]
    return b.astype(np.uint8).tobytes()

# ---------------- shared data ----------------
win = M.window
WT = bytearray()
for y in range(12, 108):
    xs_ = np.nonzero(win[y])[0]
    assert xs_[0] == 64 and len(xs_) == xs_[-1] - 63, y
    n = len(xs_); nb = (n + 3) // 4; p = n - 4 * (nb - 1)
    WT += bytes([nb, (0xFF << (8 - 2 * p)) & 0xFF])
GFT = bytes(int(round(8 + 20 * j / 52)) if j < 52 else 28 for j in range(GR))   # 0.5x far .. 1.75x near
RIMF = 4                                                                        # the far rim barely slides

def dust(level):
    a = np.zeros((32, 448), np.uint8)
    rng = np.random.default_rng(200 + level)
    for _ in range(int(260 * (0.35, 0.65, 1.0)[level])):
        y = int(31 * rng.random() ** 0.6)
        y = 31 - y if rng.random() < .8 else y
        x0 = rng.uniform(0, 448); side = rng.choice((-1, 1)); L = int(rng.uniform(2, 7))
        for i in range(L):
            a[y, int(x0 + side * i) % 448] = 3
    return a

common = bytearray(0x5D00 - 0x3100)
common[0x3140 - 0x3100:0x3140 - 0x3100 + len(WT)] = WT
common[0x3200 - 0x3100:0x3200 - 0x3100 + GR] = GFT
common[0x3240 - 0x3100] = RIMF
DU = [dust(k) for k in range(3)]
for k in range(3):
    o = 0x3300 - 0x3100 + k * 32 * 112
    common[o:o + 32 * 112] = pack(DU[k])
bsave(f"{OUT}/CKCOM.DAT", bytes(common))

cock = M.COCK.copy()
cock[M.window] = 0
bsave(f"{OUT}/COCKPIT.PIC", cga_bytes(cock), seg=0xB800)
code = open(BIN, "rb").read()
assert len(code) <= 800, "CKPIT.BIN must fit in MC(399) in LANDER.BAS"
bsave(f"{OUT}/CKPIT.BIN", code + b"\0" * (len(code) & 1))

# ---------------- Python copy of the machine code (for previews) ----------------
def draw(px, ground, rim, hz_t, ro_t, z, drift, dl, jolt, phase):
    z = max(0, min(127, z))
    hz = int(hz_t[z]) + jolt; ry = hz - int(ro_t[z])
    for r in range(96):
        if r >= hz:
            j = min(r - hz, 63); src = ground[j]; f = GFT[j]
        elif r >= ry:
            src = rim[r - ry]; f = RIMF
        else:
            src = np.zeros(SW, np.uint8); f = 0
        off = ((drift * f) & 0xFFFF) >> 4 & 255
        nb, mask = WT[2 * r], WT[2 * r + 1]
        n = sum(1 for k in range(4) if mask >> (6 - 2 * k) & 3) + 4 * (nb - 1)
        row = src[(off + np.arange(n)) % SW].copy()
        if dl and r >= 64:
            row ^= DU[dl - 1][r - 64, phase * 4:phase * 4 + n]
        px[12 + r, 64:64 + n] = row

for i, (name, fn, foot, base, feats, pieces) in enumerate(SITES, 1):
    g = ground_strip(7 + len(name), feats, base, pieces)
    rm = rim_strip(fn, 3)
    hz_t, ro_t = tables(foot)
    data = pack(g) + pack(rm) + hz_t.tobytes() + ro_t.tobytes()
    assert len(data) == 0x3100
    bsave(f"{OUT}/CK{i}.DAT", data)
    if not PREVIEW: continue
    # preview: a made-up 10 s descent drifting right, 8 frames a second
    frames = []; ph = 0
    for k in range(80):
        t = k / 79
        z = int(60 * (1 - t) ** 1.2); x = 30 * t * (2 - t)
        dl = 0 if z >= 30 else (1 if z >= 20 else (2 if z >= 10 else 3))
        ph = (ph + 23) & 63
        px = cock.copy(); draw(px, g, rm, hz_t, ro_t, z, int(round((x - 30) * 4)), dl, 0, ph)
        frames.append(M.big(px))
    frames[0].save(f"{OUT}/preview_ckpit_{name}.gif", save_all=True, append_images=frames[1:], duration=125, loop=0)
    frames[-1].save(f"{OUT}/preview_ckpit_{name}.png")
print("CKPIT.BIN", len(code), "bytes; CK?.DAT", 0x3100, "bytes each; CKCOM.DAT", len(common))
