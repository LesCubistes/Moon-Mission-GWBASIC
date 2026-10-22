"""The danger screens either side of each landing site: rough ground with nowhere safe to land.

Fly off the left or right edge of a site and LANDER.BAS flips to these. Each ends in a natural
wall on its outer side. Reads the site's own PIC and MAP (from OUTDIR) so the top HUD frame and
the ground height at the seam match.
Writes to OUTDIR, for each of EASY, MEDIUM, HARD:
  <SITE>L.RLE, <SITE>R.RLE   RLE-packed screens (CKPIT.BIN mode 6 unpacks them)
  <SITE>L.MAP, <SITE>R.MAP   collision maps, same layout as the site's MAP
  preview_danger_<site>.png  left | site | right
"""
import sys, os, math, random, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import mockscene as SC
from mklevel_io import cga_bytes, bsave, rle, unrle

OUT = sys.argv[1]
W, H = 320, 200
yy, xx = np.mgrid[0:H, 0:W]
TH = SC.BAYER[yy % 4, xx % 4]
X = np.arange(W)
FOOT = 28

def load_pic(path):
    mem = open(path, "rb").read()[7:7 + 16384]
    px = np.zeros((H, W), np.uint8)
    for y in range(H):
        o = (y & 1) * 0x2000 + (y >> 1) * 80
        for i in range(80):
            b = mem[o + i]
            px[y, i * 4:i * 4 + 4] = (b >> 6 & 3, b >> 4 & 3, b >> 2 & 3, b & 3)
    return px

def load_map(path):
    return list(struct.unpack("<640h", open(path, "rb").read()[7:7 + 1280]))

def bump(g, cx, r, h):
    for i in range(max(0, cx - r), min(W, cx + r + 1)):
        g[i] -= h * (1 - ((i - cx) / r) ** 2)
def peak(g, cx, r, h):
    for i in range(max(0, cx - r), min(W, cx + r + 1)):
        g[i] -= h * (1 - abs(i - cx) / r) ** 1.4
def crater(g, cx, r, dep, rim):
    for i in range(max(0, cx - int(r * 1.5)), min(W, cx + int(r * 1.5) + 1)):
        u = (i - cx) / r
        if abs(u) <= 1: g[i] += dep * (1 - u * u) ** 0.5
        elif abs(u) <= 1.45: g[i] -= rim * (1 - (abs(u) - 1) / 0.45)
def crevasse(g, cx, w, dep):
    for i in range(max(0, cx - w), min(W, cx + w + 1)):
        g[i] += dep * (1 - abs(i - cx) / w) ** 0.6

def terrain(site, side, seam, seed):
    """side -1 = left screen (seam on its right edge), +1 = right screen (seam on its left edge)"""
    rng = np.random.default_rng(seed)
    o = -320 if side < 0 else 320                       # same rolling ground as the site, carried on
    g = seam + 3 * np.sin((X + o) / 13 + seed) + 2 * np.sin((X + o) / 5.3) + 1.5 * np.sin((X + o) / 2.7 + 1)
    s = (lambda d: 319 - d) if side < 0 else (lambda d: d)   # s(distance from the seam) -> column
    # boulders all over: no 28 px stretch is flat
    for d in range(34, 300, 11):
        bump(g, s(d + int(rng.integers(-3, 4))), int(rng.integers(4, 8)), float(rng.uniform(4, 8)))
    if site == "EASY":                                  # mare edge: a crater cluster and a boulder field
        crater(g, s(110), 22, 18, 9); crater(g, s(170), 10, 9, 5); crater(g, s(205), 14, 12, 6)
        crevasse(g, s(70), 7, 22)
        bump(g, s(290), 44, 70)                         # the wall: a big crater's rim
    elif site == "MEDIUM":                              # rough highlands: ridges and a deep crater
        bump(g, s(80), 18, 30); peak(g, s(120), 10, 18)
        crater(g, s(185), 26, 28, 12)
        crevasse(g, s(235), 6, 26)
        peak(g, s(300), 60, 110)                        # the wall: a steep ridge
    else:                                               # HARD: the Apennine front and the rille
        crevasse(g, s(60), 12, 40)
        peak(g, s(130), 22, 46); peak(g, s(160), 12, 24)
        crevasse(g, s(205), 8, 30)
        peak(g, s(300), 90, 140)                        # the wall: Mount Hadley's flank
    # ease back to the site's ground height right at the seam
    for d in range(30):
        t = d / 30
        g[s(d)] = seam * (1 - t) + g[s(d)] * t
    return np.clip(g, 24, 196)

def draw(g, top, seed, far_y):
    random.seed(seed)
    px = np.zeros((H, W), np.uint8)
    far = np.round(far_y + 8 * np.sin(X / 21 + seed) + 5 * np.sin(X / 8) + 2 * np.sin(X / 3.7)).astype(int)
    px[(yy >= far[None, :]) & (TH < 0.08)] = 3
    px[yy == far[None, :]] = 3
    gi = np.round(g).astype(int)
    ground = yy >= gi[None, :]
    px[ground] = 0
    dpt = np.clip((yy - gi[None, :]) / 26, 0, 1)
    px[ground & ((0.66 - 0.40 * dpt) > TH)] = 3
    for i in range(W - 1):                              # sun from the left: slopes falling to the right are dark
        if gi[i + 1] > gi[i]: px[gi[i]:gi[i] + 4, i] = 0
    px[(yy == gi[None, :] - 1) | (yy == gi[None, :] - 2)] = 0
    px[(yy == gi[None, :]) | (yy == gi[None, :] + 1)] = 3
    for i in range(0, W, 7):                            # loose rocks scattered on the surface
        if random.random() < .5:
            y = gi[i] + random.randint(3, 14)
            if y < H - 1: px[y, i:i + 2] = 3; px[y + 1, i:i + 2] = 0
    n = 0
    while n < 45:
        sx, sy = random.randrange(W), random.randrange(20, 150)
        if sy < min(far[sx], gi[sx]) - 4 and not (22 <= sy <= 33 and 88 <= sx <= 236):
            px[sy, sx] = 1 if random.random() < .3 else 3; n += 1
    px[0:18] = top                                      # the HUD frame, exactly as on the site screen
    return px, gi

for k, site in enumerate(("EASY", "MEDIUM", "HARD")):
    cpx = load_pic(f"{OUT}/{site}.PIC")
    cmap = load_map(f"{OUT}/{site}.MAP")
    row = []
    for side, tag in ((-1, "L"), (1, "R")):
        seam = cmap[0] if side < 0 else cmap[319]
        g = terrain(site, side, seam, 31 + 7 * k + (side > 0))
        px, gi = draw(g, cpx[0:18], 50 + 3 * k + (side > 0), 118 - 6 * k)
        packed = rle(cga_bytes(px))
        assert unrle(packed) == cga_bytes(px) and len(packed) < 12288, len(packed)
        bsave(f"{OUT}/{site}{tag}.RLE", packed)
        Hh = [int(v) for v in gi]
        MN = [min(Hh[x:x + FOOT]) if x + FOOT <= 320 else min(Hh[x:]) for x in range(320)]
        bsave(f"{OUT}/{site}{tag}.MAP", struct.pack("<640h", *(Hh + MN)))
        # touching down anywhere here is a crash anyway (LANDER.BAS), this just reports flat spots
        print(site, tag, "packed", len(packed), "flat landing spots:", sum(1 for x in range(292) if Hh[x + 1] == Hh[x + 26] == MN[x]))
        row.append(px)
    pv = np.concatenate([row[0], np.full((H, 2), 2, np.uint8), cpx, np.full((H, 2), 2, np.uint8), row[1]], axis=1)
    SC.big(pv).save(f"{OUT}/preview_danger_{site.lower()}.png")
