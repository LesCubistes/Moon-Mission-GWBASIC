"""Build Moon Landing terrain for Fra Mauro (Medium) and Hadley Rille (Hard).

For each site writes OUTDIR/<NAME>.PIC (CGA screen BSAVE) and OUTDIR/<NAME>.MAP
(H(0..319) ground row per column, H(320+x) highest ground under the 28 px lander
footprint), plus preview_<name>.png. Same drawing style as the Easy level.
"""
import sys, os, math, random, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import mockscene as SC
from mklevel_io import cga_bytes, bsave

OUT = sys.argv[1]
W, H = 320, 200
yy, xx = np.mgrid[0:H, 0:W]
TH = SC.BAYER[yy % 4, xx % 4]
X = np.arange(W)
FOOT = 28

def bump(g, cx, r, h):                   # smooth hill (h > 0 raises the ground)
    for i in range(max(0, cx - r), min(W, cx + r + 1)):
        g[i] -= h * (1 - ((i - cx) / r) ** 2)

def peak(g, cx, r, h):                   # steep, pointed mountain
    for i in range(max(0, cx - r), min(W, cx + r + 1)):
        u = abs(i - cx) / r
        g[i] -= h * (1 - u) ** 1.4

def crater(g, cx, r, dep, rim):
    for i in range(max(0, cx - int(r * 1.5)), min(W, cx + int(r * 1.5) + 1)):
        u = (i - cx) / r
        if abs(u) <= 1: g[i] += dep * (1 - u * u) ** 0.5
        elif abs(u) <= 1.45: g[i] -= rim * (1 - (abs(u) - 1) / 0.45)

def rille(g, a, b, floor, wall):         # canyon: steep walls from a..a+wall and b-wall..b, flat floor
    for i in range(a, b + 1):
        if i < a + wall: t = (i - a) / wall
        elif i > b - wall: t = (b - i) / wall
        else: t = 1
        g[i] = g[i] * (1 - t) + floor * t

def level_pads(g, pads):
    for a, b, _ in pads:
        lvl = round(g[a:b + 1].mean())
        for i in range(1, 9):
            t = i / 9
            if a - i >= 0: g[a - i] = lvl * (1 - t) + g[a - i] * t
            if b + i < W: g[b + i] = lvl * (1 - t) + g[b + i] * t
        g[a:b + 1] = lvl

def draw(g, far, far_density, pads, shadows, stars, seed):
    random.seed(seed)
    px = np.zeros((H, W), np.uint8)
    farzone = yy >= far[None, :]
    px[farzone & (TH < far_density)] = 3
    px[yy == far[None, :]] = 3
    g = np.round(g).astype(int)
    ground = yy >= g[None, :]
    px[ground] = 0
    dpt = np.clip((yy - g[None, :]) / 26, 0, 1)
    px[ground & ((0.70 - 0.42 * dpt) > TH)] = 3
    for a, b in shadows:                                   # sun from the left: right-facing slopes dark
        for i in range(a, b):
            px[g[i]:g[i] + 4, i] = 0
    px[(yy == g[None, :] - 1) | (yy == g[None, :] - 2)] = 0
    px[(yy == g[None, :]) | (yy == g[None, :] + 1)] = 3
    for a, b, lab in pads:
        L = g[a]
        px[L, a:b + 1] = 1
        if L + 1 < H: px[L + 1, a:b + 1] = 3
        for e in (a, b):
            px[L - 4:L, e] = 3
            px[L - 5:L - 3, e] = 2
    n = 0
    while n < stars:
        sx, sy = random.randrange(W), random.randrange(20, 140)
        if sy < min(far[sx], g[sx]) - 4 and not (22 <= sy <= 33 and 88 <= sx <= 236):
            px[sy, sx] = 1 if random.random() < .3 else 3; n += 1
    import earth as E
    E.EW, E.EH, E._G = 24, 20, None
    ep, ed = E.render(2)
    px[30:50, 276:300][ed] = ep[ed]
    # HUD frame, same as Easy
    px[0:17] = 0
    px[22:34, 88:236] = 0
    px[17, :] = 1
    px[1, 40:122] = 3; px[5, 40:122] = 3; px[1:6, 40] = 3; px[1:6, 121] = 3
    from mklevel_io import pad_patches
    pad_patches(px, g, [(a, b, int(lab[1:])) for a, b, lab in pads])  # shaded patches, no labels
    from mklevel_io import csm_dots
    csm_dots(px, 248, 24)                # command module far overhead
    return px, g

def build(name, g, far, far_density, pads, shadows, stars, seed):
    level_pads(g, pads)
    px, gi = draw(g, far, far_density, pads, shadows, stars, seed)
    bsave(f"{OUT}/{name}.PIC", cga_bytes(px), seg=0xB800)
    Hh = [int(v) for v in gi]
    MN = [min(Hh[x:x + FOOT]) if x + FOOT <= 320 else min(Hh[x:]) for x in range(320)]
    bsave(f"{OUT}/{name}.MAP", struct.pack("<640h", *(Hh + MN)))
    SC.big(px).save(f"{OUT}/preview_{name.lower()}.png")
    print(name, "pads", [(a, b, Hh[a], b - a - 26) for a, b, _ in pads], "min ground", min(Hh), "max", max(Hh))

# ---------------- Fra Mauro (Apollo 14, Medium): hilly highlands, boulders, Cone crater ----------------
g = 158 + 7 * np.sin(X / 23 + .5) + 5 * np.sin(X / 9.5 + 1) + 2.2 * np.sin(X / 4.1)
far = np.round(118 + 9 * np.sin(X / 21 + 2) + 5 * np.sin(X / 8) + 2 * np.sin(X / 3.7)).astype(int)
FM_PADS = [(18, 64, "x3"), (150, 190, "x5"), (270, 304, "x7")]
bump(g, 100, 22, 26)                     # ridge to climb over after the first pad
bump(g, 120, 9, 8)
crater(g, 228, 20, 22, 10)               # Cone crater, between the x5 and x7 pads
crater(g, 82, 8, 7, 4)
for cx, r, h in ((72, 3, 4), (134, 3, 5), (140, 2, 3), (198, 3, 4), (258, 3, 5), (312, 3, 4)):
    bump(g, cx, r, h)                    # boulders
build("MEDIUM", g, far, 0.10, FM_PADS, [(100, 120), (212, 228)], 50, 14)

# ---------------- Hadley Rille (Apollo 15, Hard): Apennine peak, deep winding rille ----------------
g = 166 + 4 * np.sin(X / 19) + 2 * np.sin(X / 7 + 1) + 1.2 * np.sin(X / 3.3)
far = np.round(100 + 22 * np.exp(-((X - 60) / 45) ** 2) + 14 * np.exp(-((X - 250) / 50) ** 2)
               - 0 + 4 * np.sin(X / 9) + 2 * np.sin(X / 3.9)).astype(int)
far = np.minimum(far, 128); far = np.maximum(far, 70)
HR_PADS = [(8, 48, "x4"), (190, 224, "x7"), (282, 313, "x10")]
peak(g, 108, 46, 92)                     # Mount Hadley: towering peak right after the first pad
peak(g, 132, 18, 30)
bump(g, 265, 22, 20)                     # Hadley Delta foothill, the x10 mesa sits beside it
rille(g, 176, 238, 190, 13)              # the rille: steep walls, x7 pad on its floor
for cx, r, h in ((60, 3, 5), (160, 3, 5), (250, 2, 4)):
    bump(g, cx, r, h)
build("HARD", g, far, 0.12, HR_PADS, [(108, 154), (238, 265)], 45, 15)
