"""The braking burn cutscene between orbit and the landing screen.

Writes to OUTDIR:
  BRAKE.RLE  the scene (RLE-packed CGA screen, unpacked by CKPIT.BIN mode 6): the Moon's limb far
             below, stars, Earth, and the landing site marked on the limb ahead
  BRAKE.SPR  12 sprites of 24x24 (74 integers each) for PUT (x, y), BK(n * 74):
             pose p (0 = on its back, engine pointing ahead, .. 3 = upright) at n = 3p ship,
             3p + 1 AND-mask, 3p + 2 engine flame
  preview_brake.png
"""
import sys, os, math, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import mockscene as SC
    import mockcrash as CR
from mklevel_io import cga_bytes, bsave, sprite, rle, unrle

OUT = sys.argv[1]
W, H = 320, 200
yy, xx = np.mgrid[0:H, 0:W]
TH = SC.BAYER[yy % 4, xx % 4]
rng = np.random.default_rng(21)
random.seed(21)
px = np.zeros((H, W), np.uint8)

# ---------- the Moon, seen from high up: a gentle limb low on the screen ----------
TOP, EDGE = 150, 176
R = (160 ** 2 + (EDGE - TOP) ** 2) / (2 * (EDGE - TOP))
CY = TOP + R
limb = np.array([CY - math.sqrt(R * R - (x + .5 - 160) ** 2) for x in range(W)])
inside = yy >= limb[None, :]
depth = np.clip((yy - limb[None, :]) / 40, 0, 1)
def smooth(scale, seed):
    from PIL import Image
    r = np.random.default_rng(seed).random((H // scale + 3, W // scale + 3))
    img = Image.fromarray((r * 255).astype(np.uint8)).resize(((W // scale + 3) * scale, (H // scale + 3) * scale), Image.BICUBIC)
    return np.asarray(img).astype(float)[:H, :W] / 255
mare = 0.6 * smooth(30, 8) + 0.4 * smooth(10, 9)
bright = 0.60 - 0.30 * (mare > 0.55) - 0.08 * smooth(5, 10) + 0.10 * depth
px[inside & (bright > TH)] = 3
for _ in range(30):
    cx = rng.uniform(0, W); r = rng.uniform(2, 8)
    cy = rng.uniform(limb[int(cx)] + 4, 200)
    sq = 0.2 + 0.5 * min(1, (cy - limb[int(cx)]) / 50)
    m = ((xx - cx) / r) ** 2 + ((yy - cy) / (r * sq)) ** 2
    bowl = (m < 1) & inside
    px[bowl] = 0
    px[bowl & (xx > cx + r * 0.1) & (TH < 0.7)] = 3
    px[(m >= 1) & (m < 1.6) & inside & (xx > cx - r * .3) & (TH < .8)] = 3
for x in range(W):
    ly = int(round(limb[x])); px[ly:ly + 2, x] = 3; px[max(0, ly - 1), x] = 0

# the landing site ahead, on the limb
SX = 262
sy = int(limb[SX]) + 6
px[sy - 3:sy + 4, SX] = 0; px[sy, SX - 4:SX + 5] = 0
px[sy - 2:sy + 3, SX] = 2; px[sy, SX - 3:SX + 4] = 2

# stars, Earth
import earth as E
E.EW, E.EH, E._G = 24, 20, None
ep, ed = E.render(2)
px[22:42, 284:308][ed] = ep[ed]
n = 0
while n < 60:
    x, y = random.randrange(W), random.randrange(26, 150)
    if y < limb[x] - 4 and not (18 <= y <= 46 and 280 <= x <= 312) and px[y, x] == 0:
        px[y, x] = 1 if random.random() < .3 else 3; n += 1
px[0:24] = 0                                        # message rows stay black
packed = rle(cga_bytes(px))
assert unrle(packed) == cga_bytes(px)
assert len(packed) < 12288, len(packed)
bsave(f"{OUT}/BRAKE.RLE", packed)

# ---------- the small lander in four poses, with its braking flame ----------
big = CR.ship_px()                                  # 22 x 28, upright
h, w = big.shape
small = np.zeros((h // 2, w // 2), np.uint8)
for y in range(h // 2):
    for x in range(w // 2):
        b = big[2 * y:2 * y + 2, 2 * x:2 * x + 2].ravel()
        b = b[b > 0]
        if len(b): small[y, x] = np.bincount(b).argmax()
S = 24
canvas = np.zeros((S, S), np.uint8)
oy, ox = 4, (S - small.shape[1]) // 2
canvas[oy:oy + small.shape[0], ox:ox + small.shape[1]] = small
flame = np.zeros((S, S), np.uint8)
fy = oy + small.shape[0] - 2                        # from the engine bell down
cxm = S // 2 - 1
for i, half in enumerate((1, 1, 1, 1, 0, 0, 0, 0)):
    if fy + i < S - 1: flame[fy + i, cxm - half:cxm + half + 2] = 2 if i % 3 != 2 else 3
flame[canvas > 0] = 0

def turn(img, ang):                                 # rotate about the centre, square pixels in, CGA aspect out
    out = np.zeros_like(img)
    c = (S - 1) / 2
    a = math.radians(ang)
    for y in range(S):
        for x in range(S):
            dx, dy = x - c, (y - c) * 1.2
            sx = dx * math.cos(a) + dy * math.sin(a)
            sy = (-dx * math.sin(a) + dy * math.cos(a)) / 1.2
            ix, iy = int(round(sx + c)), int(round(sy + c))
            if 0 <= ix < S and 0 <= iy < S: out[y, x] = img[iy, ix]
    return out

data = b""
sheet = np.zeros((S, S * 4 + 12), np.uint8)
for p, ang in enumerate((-90, -60, -30, 0)):        # engine pointing ahead (right) .. upright
    s = turn(canvas, ang); f = turn(flame, ang)
    f[s > 0] = 0
    for spr in (s, np.where(s > 0, 0, 3).astype(np.uint8), f):
        b = sprite(spr); assert len(b) == 148; data += b
    sheet[:, p * (S + 4):p * (S + 4) + S] = np.maximum(s, f)
bsave(f"{OUT}/BRAKE.SPR", data)
prev = px.copy(); prev[60:84, 40:40 + sheet.shape[1]][sheet > 0] = sheet[sheet > 0]
SC.big(prev).save(f"{OUT}/preview_brake.png")
print("BRAKE.RLE", len(packed), "bytes; BRAKE.SPR", len(data), "bytes; limb", int(limb[0]), int(limb[160]), "site", SX, sy)
