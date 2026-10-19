"""M1 lander, enlarged and split into two sprites (ascent + descent stage) for future cutscenes.
Shows: full ship, exploded stages, landed with hatch open + ladder, liftoff sequence, thruster chart.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], np.uint8)
OUT = "/home/claude/gwbasic/build"
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
FS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
M = {".": 0, "c": 1, "r": 2, "g": 3}

def mirror(half):
    for h in half: assert len(h) == len(half[0]), h
    return np.array([[M[c] for c in h + h[::-1]] for h in half], np.uint8)

# 28 wide. Ascent stage: cabin, docking hatch on top, RCS pods, front hatch (closed).
ASCENT_HALF = [
    "...........ggg",
    ".........ggggg",
    ".ggg....gggggg",
    ".gcgg..ggccccc",
    ".ggggggggccccg",   # window band with centre frame
    ".ggg..gggccccg",
    "......gggggggg",
    "......gggggggg",   # hatch drawn below as an outlined panel
    "......gggggggg",
    ".......ggggggg",
]
# Descent stage: porch, red foil body, bell, splayed legs with foot pads.
DESCENT_HALF = [
    "....rrrrrrgggg",   # porch under the hatch
    "...rrrrrrrrrrr",
    "..rrgrrrrrrrrr",
    "..rrrrrrrrrrrr",
    "...rrrrrrrrrrr",
    "...g.....g.ggg",   # leg struts + engine bell
    "..g......gggg.",
    "..g.......gggg",
    ".g............",
    ".g............",
    "g.............",
    "ggg...........",
]
A = mirror(ASCENT_HALF)
# hatch: open the centre block with a black panel
A[6, 11:17] = 0; A[6:10, 11] = 0; A[6:10, 16] = 0; A[8, 15] = 1   # hatch outline + handle
A[4, 8] = 0; A[4, 19] = 0                                          # notch between cabin and pod arms
D = mirror(DESCENT_HALF)
AH, DH, W = A.shape[0], D.shape[0], A.shape[1]
POD_L, POD_R, POD_Y = 2, W - 3, 4         # pod nozzle centres (in ascent stage coords)
BELL_Y = 7                                # last bell row in descent stage

def canvas(h, w): return np.zeros((h, w), np.uint8)
def stamp(px, sp, x, y): px[y:y + sp.shape[0], x:x + sp.shape[1]][sp > 0] = sp[sp > 0]
def big(px, s): return Image.fromarray(PAL[px]).resize((px.shape[1] * s, int(px.shape[0] * s * 1.2)), Image.NEAREST)

def ship(px, x, y):
    stamp(px, A, x, y); stamp(px, D, x, y + AH)

def main_plume(px, x, y, length=7):
    cx = x + W // 2
    for i in range(length):
        hw = max(0, 2 - i // 2)
        px[y + i, cx - 1 - hw:cx + 1 + hw] = 2
    px[y:y + 3, cx - 1:cx + 1] = 3

JETS = {"side": (-1, 0), "up": (0, -1), "upout": (-1, -1), "downout": (-1, 1)}
KEYS = {9: [(-1, "downout")], 6: [(-1, "side")], 3: [(-1, "upout")], 2: [(-1, "up"), (1, "up")],
        1: [(1, "upout")], 4: [(1, "side")], 7: [(1, "downout")]}
def rcs(px, x, y, key):
    for side, j in KEYS[key]:
        dx, dy = JETS[j]
        if side == 1: dx = -dx
        x0 = x + (POD_L if side == -1 else POD_R); y0 = y + POD_Y
        if j == "side": x0 += 2 * dx
        if j == "up": y0 -= 2
        if j in ("upout", "downout"): x0 += dx; y0 += dy
        for k, col in ((1, 3), (2, 3), (3, 1), (4, 1)):
            px[y0 + dy * k, x0 + dx * k] = col

sheet = Image.new("RGB", (1380, 900), (24, 24, 28)); d = ImageDraw.Draw(sheet)
S = 8
# 1. full ship
p = canvas(AH + DH + 10, W + 4); ship(p, 2, 1); main_plume(p, 2, 1 + AH + BELL_Y + 1)
d.text((30, 14), f"Full lander {W}x{AH + DH}", font=F, fill=(230, 230, 230))
sheet.paste(big(p, S), (30, 44))
q = canvas(AH + DH + 2, W + 2); ship(q, 1, 1)
d.text((30, 400), "actual x2", font=FS, fill=(150, 150, 150)); sheet.paste(big(q, 2), (30, 420))

# 2. exploded: two sprites
d.text((330, 14), "Two sprites", font=F, fill=(230, 230, 230))
pa = canvas(AH + 2, W + 2); stamp(pa, A, 1, 1)
pd = canvas(DH + 2, W + 2); stamp(pd, D, 1, 1)
sheet.paste(big(pa, S), (330, 44)); d.text((330, 44 + AH * S * 1.2 + 24), f"ASCENT {W}x{AH}  (cabin, pods, hatch)", font=FS, fill=(200, 200, 200))
sheet.paste(big(pd, S), (330, 210)); d.text((330, 210 + DH * S * 1.2 + 24), f"DESCENT {W}x{DH}  (porch, legs, bell)", font=FS, fill=(200, 200, 200))

# 3. landed, hatch open, ladder deployed to the ground
GROUND = AH + DH + 1
p = canvas(GROUND + 4, W + 10)
ship(p, 5, 1)
p[1 + 7:1 + 10, 5 + 12:5 + 16] = 0                      # hatch swung open (dark doorway)
lx = 5 + 12                                              # ladder rails under the porch
for yy in range(1 + AH + 1, GROUND):
    p[yy, lx] = 3; p[yy, lx + 3] = 3
    if (yy - AH) % 2 == 0: p[yy, lx:lx + 4] = 3
p[GROUND:, :] = 3
d.text((640, 14), "Landed: hatch open, ladder down", font=F, fill=(230, 230, 230))
sheet.paste(big(p, S), (640, 44))

# 4. liftoff: descent stays, ascent rises on its own engine
d.text((640, 430), "Liftoff: descent stage left behind", font=F, fill=(230, 230, 230))
for i, gap in enumerate((0, 6, 16)):
    p = canvas(AH + DH + 22, W + 4)
    base = 21
    stamp(p, D, 2, base + AH - 1 + 1)
    stamp(p, A, 2, base - gap)
    p[base + AH - 1, :] = np.where(p[base + AH - 1] == 0, 0, p[base + AH - 1])
    if gap:
        cx = 2 + W // 2
        for k in range(min(gap, 6)):                       # ascent engine plume
            hw = 1 if k < 3 else 0
            p[base - gap + AH + k, cx - 1 - hw:cx + 1 + hw] = 2 if k else 3
        if gap < 10:                                       # blast scattering off the porch
            for sx in (-6, -4, 4, 6):
                p[base + AH + 1, cx + sx] = 3
    p[-1, :] = 3
    sheet.paste(big(p, 5), (640 + i * 245, 466))

sheet.save(f"{OUT}/mock_ship_m1l.png")

# 5. keypad chart for M1-L
S2 = 5
cw, ch = (W + 16) * S2 + 20, int((AH + DH + 16) * S2 * 1.2) + 50
chart = Image.new("RGB", (cw * 3 + 20, ch * 3 + 60), (24, 24, 28)); d = ImageDraw.Draw(chart)
d.text((14, 12), "M1-L keypad: 8 main engine, others fire the pod jets (green = push)", font=F, fill=(230, 230, 230))
ARROW = {8: (0, -1), 9: (1, -1), 6: (1, 0), 3: (1, 1), 2: (0, 1), 1: (-1, 1), 4: (-1, 0), 7: (-1, -1)}
for r, row in enumerate([[7, 8, 9], [4, 5, 6], [1, 2, 3]]):
    for c, k in enumerate(row):
        p = canvas(AH + DH + 16, W + 16); ship(p, 8, 7)
        if k == 8: main_plume(p, 8, 7 + AH + BELL_Y + 1)
        elif k in KEYS: rcs(p, 8, 7, k)
        ox, oy = 10 + c * cw, 46 + r * ch
        chart.paste(big(p, S2), (ox, oy + 30))
        d.text((ox, oy + 4), {8: "8 MAIN", 5: "5 none"}.get(k, f"{k} RCS"), font=F, fill=(230, 230, 230))
        if k in ARROW:
            ax, ay = ARROW[k]; cx, cy = ox + cw - 50, oy + 16
            d.line((cx - ax * 11, cy - ay * 11, cx + ax * 11, cy + ay * 11), fill=(90, 255, 90), width=4)
            d.ellipse((cx + ax * 11 - 5, cy + ay * 11 - 5, cx + ax * 11 + 5, cy + ay * 11 + 5), fill=(90, 255, 90))
chart.save(f"{OUT}/mock_thrusters_M1L.png")
print(W, AH, DH)
