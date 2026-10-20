"""Crash graphics mockups: one row of frames per crash type, CGA palette 1/6."""
import sys, os, math, random, contextlib, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import mockship2 as MS
    import mockscene as SC

PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], np.uint8)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
OUT = "/home/claude/gwbasic/build"
FW, FH, GY = 100, 64, 52                       # frame size, ground row
random.seed(7)

def ship_px(collapsed=False, broken=False):
    A, D = MS.A, MS.D
    if not collapsed:
        s = np.zeros((22, 28), np.uint8); s[:10] = A; s[10:] = D; return s
    s = np.zeros((18, 32), np.uint8)
    s[0:10, 2:30] = A
    s[10:15, 2:30] = D[0:5]                    # body only, legs folded flat
    for x, y in ((4, 15), (2, 16), (0, 17), (1, 17), (27, 15), (29, 16), (30, 17), (31, 17)):
        s[y, x] = 3
    if broken: s[16:18, 29:32] = 0; s[14, 30] = 3; s[13, 31] = 3   # snapped leg sticking out
    return s

def rot(sp, ang):
    h, w = sp.shape
    S = int(math.hypot(w, h * 1.2)) + 4
    out = np.zeros((int(S / 1.2) + 4, S), np.uint8)
    cy, cx = (out.shape[0] - 1) / 2, (S - 1) / 2
    a = math.radians(ang)
    for y in range(out.shape[0]):
        for x in range(S):
            dx, dy = x - cx, (y - cy) * 1.2
            sx = dx * math.cos(a) + dy * math.sin(a)
            sy = (-dx * math.sin(a) + dy * math.cos(a)) / 1.2
            ix, iy = int(round(sx + (w - 1) / 2)), int(round(sy + (h - 1) / 2))
            if 0 <= ix < w and 0 <= iy < h: out[y, x] = sp[iy, ix]
    ys, xs = np.nonzero(out)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def frame(slope=0.0):
    f = np.zeros((FH, FW), np.uint8)
    yy, xx = np.mgrid[0:FH, 0:FW]
    g = (GY + slope * (xx[0] - FW / 2)).astype(int)
    ground = yy >= g[None, :]
    f[ground & (0.62 - 0.3 * np.clip((yy - g[None, :]) / 12, 0, 1) > BAYER[yy % 4, xx % 4])] = 3
    f[yy == g[None, :]] = 3
    for _ in range(12):
        sx, sy = random.randrange(FW), random.randrange(2, 30)
        if sy < g[sx] - 4: f[sy, sx] = 1 if random.random() < .3 else 3
    return f, g

def stamp(f, sp, x, y):
    h, w = sp.shape
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(FW, x + w), min(FH, y + h)
    sub = sp[y0 - y:y1 - y, x0 - x:x1 - x]
    f[y0:y1, x0:x1][sub > 0] = sub[sub > 0]

def sit(f, g, sp, cx):
    """drop sprite so its lowest pixel rests on the ground at column cx"""
    h, w = sp.shape
    x = cx - w // 2
    best = 999
    for c in range(w):
        col = np.nonzero(sp[:, c])[0]
        if len(col) and 0 <= x + c < FW: best = min(best, g[x + c] - 1 - col.max())
    stamp(f, sp, x, best)
    return x, best

def dots(f, cx, cy, n, r, cols=(3,), ry=None):
    ry = ry or r
    for _ in range(n):
        a = random.uniform(0, 2 * math.pi); d = random.uniform(0, 1) ** .5
        x, y = int(cx + math.cos(a) * r * d), int(cy + math.sin(a) * ry * d)
        if 0 <= x < FW and 0 <= y < FH: f[y, x] = random.choice(cols)

def dust(f, g, cx, w, h):
    for x in range(cx - w, cx + w):
        if 0 <= x < FW:
            top = g[x] - int(h * (1 - abs(x - cx) / w)) - 1
            for y in range(top, g[x]):
                if (x + y) % 2 == 0 and random.random() < .7: f[y, x] = 3

def fireball(f, cx, cy, r, fade=0.0):
    yy, xx = np.mgrid[0:FH, 0:FW]
    ang = np.arctan2((yy - cy) * 1.2, xx - cx)
    rr = r * (1 + 0.09 * np.sin(5 * ang + r) + 0.06 * np.sin(11 * ang + 2))
    d = np.hypot(xx - cx, (yy - cy) * 1.2) / rr
    th = BAYER[yy % 4, xx % 4]
    keep = th > fade
    f[(d < 1.0) & keep & (th < 0.75)] = 2
    f[(d < 1.0) & keep & (th >= 0.75)] = 0
    f[(d < 0.62) & keep] = 2
    f[(d < 0.38) & keep & ((xx + yy) % 2 == 0)] = 3
    f[(d < 0.22) & keep] = 3

def debris(f, cx, cy, t, n=9, seed=3):
    r = random.Random(seed)
    for i in range(n):
        vx, vy = r.uniform(-14, 14), r.uniform(-16, -4)
        x, y = cx + vx * t, cy + vy * t + 9 * t * t
        if 0 <= int(x) < FW - 1 and 0 <= int(y) < FH - 1:
            c = r.choice((2, 3, 1))
            f[int(y), int(x)] = c; f[int(y), int(x) + 1] = c if i % 2 else f[int(y), int(x) + 1]

def label(f, text, row=0, col=0, c=2):
    for i, ch in enumerate(text):
        gl = SC.FONT.get(ch, SC.FONT[" "])
        for rr in range(8):
            for b in range(8):
                y, x = row * 8 + rr, (col + i) * 8 + b
                if x < FW and gl[rr] >> (7 - b) & 1: f[y, x] = c

rows = []
# ---- 1. hard landing: gear collapse ----
fr = []
f, g = frame(); sit(f, g, ship_px(), 50); dust(f, g, 50, 22, 3); fr.append(f)
f, g = frame(); x, y = sit(f, g, ship_px(True), 50); dust(f, g, 50, 26, 5); dots(f, 50, y + 14, 8, 16, (2, 3), 3); fr.append(f)
f, g = frame(); x, y = sit(f, g, rot(ship_px(True), 7), 50); dust(f, g, 50, 24, 4); dots(f, 62, y + 12, 6, 6, (2,)); fr.append(f)
f, g = frame(); x, y = sit(f, g, rot(ship_px(True, True), 11), 50); dots(f, 56, y - 4, 7, 5, (3,), 3); fr.append(f)
rows.append(("1  HARD LANDING - legs collapse  (vertical 4 to 7)", fr))
# ---- 2. impact: explosion ----
fr = []
f, g = frame(); sit(f, g, ship_px(), 50); dots(f, 50, 44, 40, 20, (3,), 10); fr.append(f)
f, g = frame(); fireball(f, 50, 42, 11); debris(f, 50, 42, .35); fr.append(f)
f, g = frame(); fireball(f, 50, 40, 18); debris(f, 50, 42, .7); fr.append(f)
f, g = frame(); fireball(f, 50, 38, 20, fade=.55); debris(f, 50, 42, 1.05); fr.append(f)
f, g = frame()
for x in range(30, 71):
    d = abs(x - 50) / 20
    for y in range(g[x] - 1, g[x] + int(4 * (1 - d * d)) + 1): f[y, x] = 0
for x in (33, 41, 58, 64, 69): f[g[x] - 2, x] = 2; f[g[x] - 2, x + 1] = 3
dots(f, 50, 34, 10, 8, (3,), 5); fr.append(f)
rows.append(("2  IMPACT - explosion and crater  (vertical over 7)", fr))
# ---- 3. sideways: tip over ----
fr = []
for ang in (15, 40, 68):
    f, g = frame(); x, y = sit(f, g, rot(ship_px(), ang), 46 + ang // 6); dust(f, g, 40, 18, 3 + ang // 20); fr.append(f)
f, g = frame(); x, y = sit(f, g, rot(ship_px(), 90), 58); dust(f, g, 46, 28, 6); dots(f, 70, y + 4, 8, 5, (2, 3)); fr.append(f)
f, g = frame(); x, y = sit(f, g, rot(ship_px(), 90), 58)
for k in range(1, 5): f[y + 4 - k, 58 + 2] = 1 if k > 2 else 3          # pod still puffing
fr.append(f)
rows.append(("3  SIDEWAYS - tips over and rolls  (drift over 2)", fr))
# ---- 4. steep ground: slides into the crater ----
fr = []
for i, (ang, cx) in enumerate(((22, 36), (30, 46), (55, 58), (150, 70))):
    f, g = frame(slope=.32); x, y = sit(f, g, rot(ship_px(), ang), cx)
    if i: dust(f, g, cx - 10, 12, 3)
    fr.append(f)
f, g = frame(slope=.32); x, y = sit(f, g, rot(ship_px(True, True), 180), 74); dust(f, g, 74, 16, 5); dots(f, 74, y - 4, 6, 6, (3,)); fr.append(f)
rows.append(("4  STEEP GROUND - slides and flips  (crater rim, slope)", fr))
# ---- 5. rare: runaway thrusters ----
fr = []
f, g = frame(); x, y = sit(f, g, rot(ship_px(), 20), 44); dots(f, 60, 46, 14, 8, (2, 3)); label(f, "MASTER", 0, 0); label(f, "ALARM", 1, 0); fr.append(f)
def runaway(f, x, y, ang, trail):
    sp = rot(ship_px(True, True), ang); stamp(f, sp, x, y)
    h, w = sp.shape
    for k in range(1, 11):                                          # stuck main engine at full, flame trailing
        yy_, xx_ = min(FH - 1, y + h + k - 3), x + w // 2 - k // 2
        for dx in (-1, 0, 1):
            if 0 <= xx_ + dx < FW: f[yy_, xx_ + dx] = 3 if k < 3 and dx == 0 else 2
    for k in range(1, 10):                                          # stuck side jet pushing it the wrong way
        for dy in (0, 1):
            if 0 <= x - k < FW: f[y + 4 + dy, x - k] = 3 if k < 4 else 1
    for (tx, ty) in trail:                                          # smoke puffs left behind
        for ox, oy in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0)):
            if 0 <= tx + ox < FW and 0 <= ty + oy < FH and (tx + ox + ty + oy) % 2 == 0: f[ty + oy, tx + ox] = 3
f, g = frame(); runaway(f, 40, 20, -15, [(30 + i * 2, 44 - i * 3) for i in range(5)]); label(f, "MASTER", 0, 0); fr.append(f)
f, g = frame(); runaway(f, 62, 6, -30, [(20 + i * 6, 40 - i * 6) for i in range(7)]); label(f, "ALARM", 0, 0); fr.append(f)
f, g = frame(); runaway(f, 66, 30, -70, [(40 + i * 5, 6 + i * 3) for i in range(6)]); fr.append(f)
f, g = frame(); fireball(f, 78, 44, 22); debris(f, 78, 44, .8, n=14, seed=9); label(f, "MAYDAY", 0, 0); fr.append(f)
rows.append(("5  RARE: RUNAWAY THRUSTERS - fast sideways hit with fuel left", fr))

S = 3
fw, fh = FW * S, int(FH * S * 1.2)
sheet = Image.new("RGB", (fw * 5 + 6 * 12, len(rows) * (fh + 46) + 20), (24, 24, 28))
d = ImageDraw.Draw(sheet)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
for r, (title, frames) in enumerate(rows):
    oy = 10 + r * (fh + 46)
    d.text((12, oy), title, font=F, fill=(230, 230, 230))
    for i, f in enumerate(frames):
        im = Image.fromarray(PAL[f]).resize((fw, fh), Image.NEAREST)
        sheet.paste(im, (12 + i * (fw + 12), oy + 32))
sheet.save(f"{OUT}/mock_crashes.png")
print(sheet.size)
