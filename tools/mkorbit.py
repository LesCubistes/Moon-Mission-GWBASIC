"""Build the orbit (site selection) screen for Moon Landing phase 1.

Outputs in OUTDIR:
  ORBIT.PIC  BSAVE of CGA video RAM: stars, Earth, command/service module, the Moon's limb
             split into three equal landing zones with names + difficulty above the surface
The lander itself is the game's own sprite (LMSHIP/LMMASK), drawn by LANDER.BAS.
Prints the zone label boxes and limb heights the BASIC program uses.
"""
import sys, os, math, random, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import mockscene as SC
from mklevel_io import cga_bytes, bsave, sprite

OUT = sys.argv[1]
W, H = 320, 200
yy, xx = np.mgrid[0:H, 0:W]
TH = SC.BAYER[yy % 4, xx % 4]
random.seed(7)
rng = np.random.default_rng(7)
px = np.zeros((H, W), np.uint8)

# ---------- the Moon: a huge disc whose top edge (limb) curves across the lower screen ----------
TOP, EDGE = 136, 170                      # limb height at screen centre and at the edges
R = (160 ** 2 + (EDGE - TOP) ** 2) / (2 * (EDGE - TOP))
CY = TOP + R
limb = np.array([CY - math.sqrt(R * R - (x + .5 - 160) ** 2) for x in range(W)])
inside = yy >= limb[None, :]
depth = np.clip((yy - limb[None, :]) / 60, 0, 1)        # 0 at the limb, 1 well onto the disc

def smooth(scale, seed):
    from PIL import Image
    r = np.random.default_rng(seed).random((H // scale + 3, W // scale + 3))
    img = Image.fromarray((r * 255).astype(np.uint8)).resize(((W // scale + 3) * scale, (H // scale + 3) * scale), Image.BICUBIC)
    return np.asarray(img).astype(float)[:H, :W] / 255

# maria (dark seas) and highlands
mare = (0.6 * smooth(40, 3) + 0.4 * smooth(14, 4))
bright = 0.62 - 0.30 * (mare > 0.55) - 0.08 * smooth(6, 5) + 0.10 * depth
px[inside & (bright > TH)] = 3

# craters, squashed by perspective (flatter near the limb)
for _ in range(38):
    cx = rng.uniform(0, W); r = rng.uniform(3, 13)
    cy = rng.uniform(limb[int(cx)] + 6, 200)
    squash = 0.25 + 0.55 * min(1, (cy - limb[int(cx)]) / 70)
    rx, ry = r, r * squash
    m = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    bowl = (m < 1) & inside
    px[bowl] = 0
    px[bowl & (TH < 0.30)] = 3                              # dim floor
    px[bowl & (xx > cx + rx * 0.1) & (TH < 0.70)] = 3      # sunlit far (right) wall
    shadow = bowl & (((xx - cx + rx * .35) / rx) ** 2 + ((yy - cy) / ry) ** 2 > .55) & (xx < cx)
    px[shadow] = 0                                          # shadow crescent on the left wall
    rim = (m >= 1) & (m < 1.6) & inside & (xx > cx - rx * .3)
    px[rim & (TH < 0.8)] = 3

# crisp bright limb with a thin dark gap above it
for x in range(W):
    ly = int(round(limb[x]))
    px[ly:ly + 2, x] = 3
    px[max(0, ly - 1), x] = 0

# ---------- three equal zones ----------
ZONES = [  # name, difficulty, name col, diff col, text row (1-based)
    ("TRANQUILITY", "(EASY)", 2, 5, 16),
    ("FRA MAURO", "(MEDIUM)", 16, 17, 15),
    ("HADLEY RILLE", "(HARD)", 28, 31, 16),
]
DIV = [107, 213]                          # zone dividers: 0-106, 107-212, 213-319
boxes = []
for name, diff, c1, c2, row in ZONES:
    x0 = (min(c1, c2) - 1) * 8 - 3
    x1 = (max(c1 + len(name), c2 + len(diff)) - 1) * 8 + 1
    y0, y1 = (row - 1) * 8 - 3, (row + 1) * 8 + 1
    boxes.append((x0, y0, x1, y1))
    assert y1 < limb[x0] - 2 and y1 < limb[x1] - 2, (name, y1, limb[x0], limb[x1])

# ---------- stars (kept clear of text, boxes, CSM, Earth and dividers) ----------
clear = np.zeros((H, W), bool)
clear[0:26, :] = True                                    # title, hint and message rows
for x0, y0, x1, y1 in boxes: clear[y0 - 2:y1 + 3, x0 - 2:x1 + 3] = True
clear[24:48, 112:210] = True                             # command/service module
clear[16:44, 272:304] = True                             # Earth
for d in DIV: clear[:, d - 2:d + 3] = True
clear[44:112, 138:184] = True                             # where the lander starts
n = 0
while n < 70:
    sx, sy = random.randrange(W), random.randrange(26, 140)
    if sy < limb[sx] - 4 and not clear[sy, sx]:
        px[sy, sx] = 1 if random.random() < .3 else 3; n += 1

# dotted dividers: sky part from under the hint rows to the limb, faint dots on the surface
for d in DIV:
    for y in range(56, H):
        if y < limb[d] - 1:
            if y % 4 == 0 and not 104 <= y <= 142: px[y, d] = 1     # gap beside the labels
        elif y % 3 == 0: px[y, d] = 1

# site markers on the surface below each label
for i, (name, *_ ) in enumerate(ZONES):
    mx = (DIV[0] // 2, (DIV[0] + DIV[1]) // 2, (DIV[1] + W) // 2)[i]
    my = int(limb[mx]) + 10
    px[my - 3:my + 4, mx] = 0; px[my, mx - 4:mx + 5] = 0
    px[my - 2:my + 3, mx] = 1; px[my, mx - 3:mx + 4] = 1

# labels: name in cyan, difficulty in white
for name, diff, c1, c2, row in ZONES:
    SC.text(px, row, c1, name, 1)
    SC.text(px, row + 1, c2, diff, 3)

# ---------- Earth, small and far away ----------
import earth as E
E.EW, E.EH, E._G = 24, 20, None
ep, ed = E.render(2)
px[20:40, 276:300][ed] = ep[ed]

# ---------- command/service module, nose pointing left, docking probe where the LM undocked ----------
CSM = SC.sprite([
    "........ggggggggggggggggggggggggggggg.......",
    "......ggg.gggggggg.c.c.c.c.ggggggggggg......",
    "....gggggggggggggg.c.c.c.c.gggggggggggrr....",
    "..ggggggg.gggggggg.c.c.c.c.ggggggggggg.rrr..",
    "gggggggggggggggggggggggggggggggggggggg.rrrrr",
    "..ggggggg.gggggggg.c.c.c.c.ggggggggggg.rrr..",
    "....gggggggggggggg.c.c.c.c.gggggggggggrr....",
    "......ggg.gggggggg.c.c.c.c.ggggggggggg......",
    "........ggggggggggggggggggggggggggggg.......",
])
# make the cone: blank the top/bottom corners of the first 9 columns to taper the command module
cs = CSM.copy()
for r in range(cs.shape[0]):
    k = abs(r - 4)
    cs[r, :max(0, 2 * k)] = 0
cs[:, 9] = np.where(cs[:, 9] > 0, 2, 0)                  # heat-shield seam between CM and SM
x0, y0 = 160 - cs.shape[1] // 2, 30
SC_mask = cs > 0
px[y0:y0 + cs.shape[0], x0:x0 + cs.shape[1]][SC_mask] = cs[SC_mask]
px[y0 + 9:y0 + 12, x0 + 30] = 3                          # high-gain antenna stalk
px[y0 + 12, x0 + 28:x0 + 33] = 3; px[y0 + 13, x0 + 29:x0 + 32] = 3

# ---------- titles (the program prints messages on row 3) ----------
SC.text(px, 1, 11, "SELECT LANDING SITE", 1)
SC.text(px, 2, 3, "4/6 MOVE  2/ENTER DESCEND  ESC MENU", 3)
bsave(f"{OUT}/ORBIT.PIC", cga_bytes(px), seg=0xB800)

SC.big(px).save(f"{OUT}/preview_orbit.png")
print("limb y at x=0,53,107,160,213,266,319:", [int(limb[x]) for x in (0, 53, 107, 160, 213, 266, 319)])
print("label boxes:", boxes)
