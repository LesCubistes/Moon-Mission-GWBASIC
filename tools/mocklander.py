"""Design mockups for the Moon Landing mission, in CGA palette 1/6.
Produces: build/mock_landers.png (sprite options) and build/mock_easy.png (Easy level scene).
"""
import numpy as np, random, math
from PIL import Image, ImageDraw, ImageFont

PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], np.uint8)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
OUT = "/home/claude/gwbasic/build"
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
FS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

def grid(rows):
    """sprite from strings: . black  c cyan  r red  g grey"""
    m = {".": 0, "c": 1, "r": 2, "g": 3}
    return np.array([[m[ch] for ch in row] for row in rows], np.uint8)

# ---- lander options ----
LANDERS = {
 "A. Apollo LM (16x14)": grid([
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
  "ggg..........ggg",
 ]),
 "B. Compact LM (12x10)": grid([
  "....gggg....",
  "...gcccсg...".replace("с", "c"),
  "..ggc..cgg..",
  "..gggggggg..",
  ".rrrrrrrrrr.",
  ".r.rrrrrr.r.",
  ".rrrrrrrrrr.",
  "g.g......g.g",
  "g..g....g..g",
  "gg........gg",
 ]),
 "C. Bold LM (14x12)": grid([
  ".....gggg.....",
  "....gccccg....",
  "...gcc..ccg...",
  "..gggccccggg..",
  "..rrrrrrrrrr..",
  ".rrr.rrrr.rrr.",
  ".rrrrrrrrrrrr.",
  "..g..gggg..g..",
  ".g..g....g..g.",
  ".g.g......g.g.",
  "g..g......g..g",
  "gg..........gg",
 ]),
}
FLAME = grid(["..rr..", ".rggr.", "..rr..", "...r.."])

def rot(sp, ang):
    """nearest-neighbour rotate a sprite (for rotation frames)"""
    h, w = sp.shape
    S = int(math.ceil(math.hypot(w, h * 1.2))) + 2
    out = np.zeros((int(S / 1.2) + 2, S), np.uint8)
    cy, cx = (out.shape[0] - 1) / 2, (S - 1) / 2
    a = math.radians(ang)
    for y in range(out.shape[0]):
        for x in range(S):
            dx, dy = x - cx, (y - cy) * 1.2
            sx = dx * math.cos(a) + dy * math.sin(a)
            sy = (-dx * math.sin(a) + dy * math.cos(a)) / 1.2
            ix, iy = int(round(sx + (w - 1) / 2)), int(round(sy + (h - 1) / 2))
            if 0 <= ix < w and 0 <= iy < h: out[y, x] = sp[iy, ix]
    return out

def big(px, s):
    return Image.fromarray(PAL[px]).resize((px.shape[1] * s, int(px.shape[0] * s * 1.2)), Image.NEAREST)

sheet = Image.new("RGB", (1240, 560), (24, 24, 28))
d = ImageDraw.Draw(sheet)
x = 30
for name, sp in LANDERS.items():
    d.text((x, 14), name, font=F, fill=(230, 230, 230))
    withflame = np.zeros((sp.shape[0] + 4, sp.shape[1]), np.uint8); withflame[:sp.shape[0]] = sp
    fx = (sp.shape[1] - 6) // 2; withflame[sp.shape[0]:, fx:fx + 6] = FLAME
    sheet.paste(big(withflame, 12), (x, 50))
    sheet.paste(big(sp, 2), (x + 300, 60))
    d.text((x + 300, 40), "actual size x2", font=FS, fill=(160, 160, 160))
    x += 410
d.text((30, 330), "Rotation frames for A (every 15 degrees, if the lander tilts):", font=F, fill=(230, 230, 230))
x = 30
for ang in (-45, -30, -15, 0, 15, 30, 45):
    sheet.paste(big(rot(LANDERS["A. Apollo LM (16x14)"], ang), 6), (x, 365))
    x += 165
sheet.save(f"{OUT}/mock_landers.png")

# ---- Easy level: Tranquility Base ----
W, H = 320, 200
px = np.zeros((H, W), np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
random.seed(11)
# terrain heights: gentle mare plain with 3 pads and a few craters with steep rims
ground = np.zeros(W)
for x in range(W):
    ground[x] = 168 + 6 * math.sin(x / 41) + 3 * math.sin(x / 13 + 2) + 1.5 * math.sin(x / 5.1)
PADS = [(26, 62, "x2"), (144, 172, "x3"), (254, 276, "x5")]   # wide -> narrow, more points
CRATERS = [(100, 14, 9), (212, 18, 11), (304, 10, 7)]          # center, half-width, depth
for cx, hw, dep in CRATERS:
    for x in range(max(0, cx - hw - 4), min(W, cx + hw + 5)):
        dxn = (x - cx) / hw
        if abs(dxn) <= 1:
            ground[x] += dep * (1 - dxn ** 2) ** 0.7       # bowl
        elif abs(dxn) <= 1.35:
            ground[x] -= 5 * (1 - (abs(dxn) - 1) / 0.35)  # steep raised rim
for a, b, _ in PADS:
    lvl = round(ground[a:b + 1].mean())
    ground[a:b + 1] = lvl
    for i in range(1, 8):                                   # ease terrain into the pad
        t = i / 8
        if a - i >= 0: ground[a - i] = lvl * (1 - t) + ground[a - i] * t
        if b + i < W: ground[b + i] = lvl * (1 - t) + ground[b + i] * t
g = np.round(ground).astype(int)
below = yy >= g[None, :]
depth = np.clip((yy - g[None, :]) / 30, 0, 1)
shade = 0.62 - 0.35 * depth
px[below & (shade > BAYER[yy % 4, xx % 4])] = 3
px[yy == g[None, :]] = 3                                     # solid surface line
# steep slopes (crash zones) shown with red edge in the design view only
steep = np.zeros(W, bool)
steep[1:] = np.abs(np.diff(g)) >= 2
# pads: solid surface, beacon lights at both ends
for a, b, lab in PADS:
    lvl = g[a]
    px[lvl, a:b + 1] = 3; px[lvl + 1, a:b + 1] = 3
    px[lvl - 1, a] = px[lvl - 1, b] = 1
    px[lvl - 2, a] = px[lvl - 2, b] = 1
# stars
for _ in range(60):
    sx, sy = random.randrange(W), random.randrange(18, 140)
    if sy < g[sx] - 10: px[sy, sx] = 1 if random.random() < .3 else 3
# small Earth high in the sky
for y in range(24, 40):
    for x in range(280, 300):
        dx, dy = (x - 289.5) / 9.5, (y - 31.5) / 8
        if dx * dx + dy * dy <= 1 and dx < 0.45:
            px[y, x] = 2 if ((x + y) % 2 and -0.4 < dx < 0.2 and -0.3 < dy < 0.6) else 1
# HUD top band
px[0:16] = 0
px[16, :] = 1
# lander + flame at start position
sp = LANDERS["A. Apollo LM (16x14)"]
lx, ly = 60, 40
px[ly:ly + sp.shape[0], lx:lx + sp.shape[1]][sp > 0] = sp[sp > 0]
px[ly + 14:ly + 18, lx + 5:lx + 11][FLAME > 0] = FLAME[FLAME > 0]

img = big(px, 3)
d = ImageDraw.Draw(img)
mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 21)
d.text((8, 4), "FUEL", font=mono, fill=tuple(PAL[3]))
d.rectangle((70, 9, 70 + 120, 21), outline=tuple(PAL[3]))
d.rectangle((72, 11, 72 + 90, 19), fill=tuple(PAL[1]))
d.text((215, 4), "ALT 0850  H+0.4  V-1.2  T 0:07", font=mono, fill=tuple(PAL[3]))
for a, b, lab in PADS:
    d.text(((a + b) / 2 * 3 - 12, (g[a] + 4) * 3.6), lab, font=mono, fill=tuple(PAL[1]))
d.text((8, 56), "TRANQUILITY BASE", font=mono, fill=tuple(PAL[1]))
img.save(f"{OUT}/mock_easy.png")

# design overlay: same scene with crash zones marked
ov = img.copy(); d2 = ImageDraw.Draw(ov)
for x in range(W):
    if steep[x]:
        d2.rectangle((x * 3, g[x] * 3.6 - 3, x * 3 + 2, g[x] * 3.6 + 3), fill=(255, 60, 60))
for a, b, lab in PADS:
    d2.rectangle((a * 3, g[a] * 3.6 - 5, b * 3 + 2, g[a] * 3.6 + 2), outline=(80, 255, 80), width=2)
d2.text((330, 640), "green = safe pads    red = too steep (crash)", font=F, fill=(255, 255, 255))
ov.save(f"{OUT}/mock_easy_zones.png")
print("pads at y:", [int(g[a]) for a, _, _ in PADS])
