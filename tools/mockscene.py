"""Easy level (Tranquility Base) scene mockup, exactly as CGA 320x200 palette 1/6 would show it.
Text uses the real CGA 8x8 font, placed on the 40x25 text grid like PRINT does.
"""
import numpy as np, random, math, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/gwbasic/tools")

PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], np.uint8)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
OUT = "/home/claude/gwbasic/build"
W, H = 320, 200
yy, xx = np.mgrid[0:H, 0:W]
TH = BAYER[yy % 4, xx % 4]

FONT = {}
for line in open("/usr/local/lib/python3.13/dist-packages/pcbasic/data/fonts/cga_08.hex"):
    k, v = line.strip().split(":")
    if len(k) == 4 and int(k, 16) < 128 and len(v) == 16: FONT[chr(int(k, 16))] = bytes.fromhex(v)

def text(px, row, col, s, c=3):
    """PRINT-style: 8x8 cell, foreground c on black (row/col are 1-based like LOCATE)"""
    for i, ch in enumerate(s):
        g = FONT.get(ch, FONT[" "])
        y0, x0 = (row - 1) * 8, (col - 1 + i) * 8
        for r in range(8):
            for b in range(8):
                px[y0 + r, x0 + b] = c if g[r] >> (7 - b) & 1 else 0

def sprite(rows):
    m = {".": 0, "c": 1, "r": 2, "g": 3}
    return np.array([[m[ch] for ch in r] for r in rows], np.uint8)

LANDER = sprite([
  "......gggg......",
  ".....gccccg.....",
  "....gc.cc.cg....",
  "...gggccccggg...",
  "...g.gggggg.g...",
  "..rrrrrrrrrrrr..",
  "..r.r.rrrr.r.r..",
  "..rrrrrrrrrrrr..",
  "..g...g..g...g..",
  ".g...g....g...g.",
  ".g..g......g..g.",
  "g...g..gg..g...g",
  "g..............g",
  "ggg..........ggg"])
FLAME = sprite(["..rr..", ".rggr.", ".rggr.", "..rr..", "...r.."])

def build(seed=11):
    random.seed(seed)
    px = np.zeros((H, W), np.uint8)
    # --- distant highlands silhouette (no collision, scenery only) ---
    far = 128 + 7 * np.sin(np.arange(W) / 29 + 1) + 4 * np.sin(np.arange(W) / 11) + 2 * np.sin(np.arange(W) / 4.3)
    far = np.round(far).astype(int)
    farzone = yy >= far[None, :]
    px[farzone & (TH < 0.07)] = 3                                   # faint, far away
    px[yy == far[None, :]] = 3
    # --- foreground terrain (the collision map) ---
    x = np.arange(W)
    g = 162 + 4 * np.sin(x / 47) + 2 * np.sin(x / 17 + 2) + 1.2 * np.sin(x / 6.1)
    PADS = [(12, 68, "x2"), (140, 184, "x3"), (256, 292, "x5")]   # lander feet span 28 px
    CRATERS = [(96, 16, 13), (214, 20, 16), (308, 9, 8)]             # center, radius, depth
    for cx, r, dep in CRATERS:
        for i in range(max(0, cx - int(r * 1.5)), min(W, cx + int(r * 1.5) + 1)):
            u = (i - cx) / r
            if abs(u) <= 1: g[i] += dep * (1 - u * u) ** 0.5           # deep bowl, steep walls
            elif abs(u) <= 1.45: g[i] -= 6 * (1 - (abs(u) - 1) / 0.45)  # raised rim
    # a small ridge and boulders between pads
    for cx, r, h in ((122, 7, 7), (238, 4, 4)):
        for i in range(cx - r, cx + r + 1):
            g[i] -= h * (1 - ((i - cx) / r) ** 2)
    for a, b, _ in PADS:
        lvl = round(g[a:b + 1].mean())
        for i in range(1, 9):
            t = i / 9
            if a - i >= 0: g[a - i] = lvl * (1 - t) + g[a - i] * t
            if b + i < W: g[b + i] = lvl * (1 - t) + g[b + i] * t
        g[a:b + 1] = lvl
    g = np.round(g).astype(int)
    ground = yy >= g[None, :]
    px[ground] = 0
    dpt = np.clip((yy - g[None, :]) / 26, 0, 1)
    px[ground & ((0.70 - 0.42 * dpt) > TH)] = 3
    # crater interiors in shadow on the sunward (left) wall
    for cx, r, dep in CRATERS:
        for i in range(cx - r, cx):
            px[g[i]:g[i] + 3, i] = 0
    px[(yy == g[None, :] - 1) | (yy == g[None, :] - 2)] = 0             # dark gap separates near from far
    px[(yy == g[None, :]) | (yy == g[None, :] + 1)] = 3                 # crisp surface edge
    # pads: two solid rows + cyan beacons
    for a, b, lab in PADS:
        L = g[a]
        px[L, a:b + 1] = 1                                   # cyan landing deck
        px[L + 1, a:b + 1] = 3
        for e in (a, b):
            px[L - 4:L, e] = 3
            px[L - 5:L - 3, e] = 2                           # red beacon (will blink)
    # stars
    for _ in range(55):
        sx, sy = random.randrange(W), random.randrange(20, 120)
        if sy < far[sx] - 4: px[sy, sx] = 1 if random.random() < .3 else 3
    # small Earth
    import earth as E
    E.EW, E.EH, E._G = 24, 20, None
    ep, ed = E.render(2)
    ex, ey = 276, 30
    px[ey:ey + 20, ex:ex + 24][ed] = ep[ed]
    return px, g, PADS, CRATERS

px, g, PADS, CRATERS = build()

# HUD: two text rows + divider
text(px, 1, 1, "FUEL")
px[1:6, 40:41] = 3; px[1:6, 120:121] = 3; px[1, 40:121] = 3; px[5, 40:121] = 3
px[2:5, 42:104] = 1
text(px, 1, 17, "SCORE 0000")
text(px, 1, 31, "T 0:07")
text(px, 2, 1, "ALT 0850  HSPD +0.4  VSPD -1.2")
px[17, :] = 1
text(px, 4, 13, "TRANQUILITY BASE", 1)
# pad labels below pads
for a, b, lab in PADS:
    col = (a + b) // 2 // 8 + 1
    row = (g[a] + 12) // 8 + 1
    text(px, row, col, lab, 1)
# lander
import mockship2 as MS
lx, ly = 70, 46
MS.ship(px, lx, ly); MS.main_plume(px, lx, ly + MS.AH + MS.BELL_Y + 1)

def big(p, s=3): return Image.fromarray(PAL[p]).resize((W * s, int(H * s * 1.2)), Image.NEAREST)
big(px).save(f"{OUT}/mock_easy.png")

# design overlay: crash zones (slope >= 2 px per px) and pads
img = big(px); d = ImageDraw.Draw(img)
sx, sy = 3, 3.6
for i in range(1, W):
    if abs(int(g[i]) - int(g[i - 1])) >= 2:
        d.rectangle((i * sx - 2, g[i] * sy - 4, i * sx + 2, g[i] * sy + 2), fill=(255, 70, 70))
for a, b, _ in PADS:
    d.rectangle((a * sx, g[a] * sy - 6, b * sx + 3, g[a] * sy + 4), outline=(90, 255, 90), width=3)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
d.rectangle((0, 676, 960, 720), fill=(20, 20, 24))
d.text((14, 686), "design overlay:  green = safe pads   red = too steep, crash", font=f, fill=(255, 255, 255))
img.save(f"{OUT}/mock_easy_zones.png")
np.save(f"{OUT}/easy_ground.npy", g)
print("pad heights", [(a, b, int(g[a])) for a, b, _ in PADS])
