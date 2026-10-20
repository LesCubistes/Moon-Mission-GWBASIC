"""'The Eagle has landed' picture: our lander, drawn big, standing on the regolith.

Composition follows the Apollo surface photo (sun from the right, shadow falling left,
black sky with the horizon rising to the right, a jettisoned bag by the right leg) but the
lander uses our sprite's look: grey ascent stage, cyan windows, red descent stage.
Three end-of-level pictures share one scene:
  LANDED.PIC  the lander standing (also the surface mission briefing picture)
  WRECK.PIC   all landers lost, last one crashed: tipped over on a snapped leg, debris around it
  CRATER.PIC  all landers lost, last one blew up: fresh crater and scattered wreckage
The sky is kept black down to row ~64 so the program can print the score lines there.
usage: mklanded.py OUTDIR
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mklevel_io import cga_bytes, bsave

OUT = sys.argv[1]
W, H = 320, 200
PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], np.uint8)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
yy, xx = np.mgrid[0:H, 0:W]
TH = BAYER[yy % 4, xx % 4]
rng = np.random.default_rng(5)
px = np.zeros((H, W), np.uint8)
ground_layer = px

def mask_poly(pts):
    m = Image.new("1", (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=1); return np.asarray(m)
def mask_ell(cx, cy, rx, ry):
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
STRIPE = (xx % 2 == 0)
def fill(m, c, density=1.0, alt=0):
    """solid colour c, or a shade of c over colour alt (stripes on the lander so it never
    looks like the dotted regolith)"""
    if density >= 1: px[m] = c; return
    if px is ground_layer: pat = TH < density
    else: pat = STRIPE if density < .75 else ~((xx % 4 == 0) & (yy % 2 == 0))
    px[m & pat] = c; px[m & ~pat] = alt
def line(p0, p1, c, width=1):
    m = Image.new("1", (W, H), 0); ImageDraw.Draw(m).line([p0, p1], fill=1, width=width); px[np.asarray(m)] = c

def smooth(scale, seed):
    r = np.random.default_rng(seed).random((H // scale + 3, W // scale + 3))
    img = Image.fromarray((r * 255).astype(np.uint8)).resize(((W // scale + 3) * scale, (H // scale + 3) * scale), Image.BICUBIC)
    return np.asarray(img).astype(float)[:H, :W] / 255

# ---------------- sky and regolith ----------------
X = np.arange(W)
horizon = (80 - 12 * (X / W) + 2 * np.sin(X / 23) + 1 * np.sin(X / 7.5)).astype(int)     # low, rising to the right
ground = yy >= horizon[None, :]
depth = np.clip((yy - horizon[None, :]) / 120, 0, 1)
dens = 0.15 + 0.13 * depth + 0.12 * (smooth(18, 1) - .5) + 0.05 * (smooth(5, 2) - .5)
px[ground & (TH < dens)] = 3
px[(yy == horizon[None, :])] = 3                                          # crisp far ridge line
px[(yy == horizon[None, :] + 1) & (TH < .6)] = 3
for _ in range(110):                                                      # rocks: lit on the right, shadow left
    x = rng.uniform(0, W); y = rng.uniform(horizon[int(x)] + 4, H)
    r = 0.6 + 2.6 * max(0, (y - 60) / 140) ** 1.5 * rng.uniform(.5, 1.4)
    rx, ry = r, r / 1.2
    rock = mask_ell(x, y, rx, ry)
    px[mask_ell(x - rx * .9, y + ry * .4, rx * 1.1, ry * .7) & ground] = 0
    px[rock] = 3
    px[rock & (xx < x - rx * .2) & (TH < .6)] = 0

# ---------------- the lander (drawn on its own layer, outlined in black when composited) ----------------
CX = 152
DY = 14                                       # whole scene sits lower than the photo for a taller sky
def new_layer():
    global px
    px = np.full((H, W), 255, np.uint8); return px

def lander(legs=(0, 1)):
    """our lander standing upright; legs = which front legs to draw (0 screen-left, 1 screen-right)"""
    new_layer()
    # legs behind the body (rear pair), thinner and partly hidden
    for top, foot in (((104, 120), (68, 150)), ((200, 120), (236, 148))):
        line(top, foot, 3, 2)
        px[mask_ell(foot[0], foot[1] + 1, 7, 2.5)] = 3

    # descent stage: octagonal box, front face lit, left face in shade, right face lit
    front = mask_poly([(110, 110), (194, 110), (192, 142), (112, 142)])
    left = mask_poly([(88, 106), (110, 110), (112, 142), (92, 136)])
    right = mask_poly([(194, 110), (214, 106), (210, 136), (192, 142)])
    fill(left, 2, .5, 0)                       # red foil in shade
    fill(front, 2)                             # red foil
    fill(right, 2, .55, 3)                     # red foil catching the sun
    crinkle = front & (rng.random((H, W)) < .07)
    px[crinkle] = 3                            # foil glints
    px[front & (rng.random((H, W)) < .05)] = 0
    fill(mask_poly([(86, 102), (216, 102), (214, 106), (194, 110), (110, 110), (88, 106)]), 0)   # deck edge in shadow
    line((110, 110), (112, 142), 0); line((194, 110), (192, 142), 0)
    fill(mask_poly([(156, 128), (178, 128), (178, 136), (156, 136)]), 3)                         # placard
    line((158, 131), (176, 131), 0); line((158, 133), (172, 133), 0)
    # porch and ladder on the front-left leg
    fill(mask_poly([(124, 104), (148, 104), (148, 110), (124, 110)]), 3, .5, 0)

    # ascent stage, like our sprite. The lander faces us, so its right side is on the screen's left:
    # that side is widened out to the edge of the red tub (equipment bay + side module).
    fill(mask_poly([(92, 78), (104, 72), (104, 102), (94, 102)]), 3, .55, 0)                     # lander-right equipment bay
    fill(mask_poly([(104, 70), (132, 64), (132, 102), (104, 102)]), 3, .55, 0)                   # lander-right module (shade)
    line((104, 70), (104, 102), 0)
    fill(mask_poly([(172, 64), (196, 69), (198, 102), (172, 102)]), 3, .85, 0)                   # lander-left module (lit)
    fill(mask_poly([(132, 62), (138, 56), (166, 56), (172, 62), (172, 102), (132, 102)]), 3)     # front cabin
    line((132, 62), (132, 102), 0); line((172, 62), (172, 102), 0)
    # bigger windows, running down close to the hatch
    LWIN = [(134, 60), (151, 60), (151, 64), (142, 78), (134, 78)]
    RWIN = [(153, 60), (170, 60), (170, 78), (162, 78), (153, 64)]
    fill(mask_poly(LWIN), 1); fill(mask_poly(RWIN), 1)
    line((152, 60), (152, 78), 3)                                                               # centre window post
    # airlock hatch: square frame, inner door, locking wheel, hinges
    fill(mask_poly([(141, 80), (163, 80), (163, 102), (141, 102)]), 0)
    for x0, y0, x1, y1 in ((142, 81, 162, 101), (145, 84, 159, 99)):
        line((x0, y0), (x1, y0), 3); line((x0, y1), (x1, y1), 3); line((x0, y0), (x0, y1), 3); line((x1, y0), (x1, y1), 3)
    px[mask_ell(152, 91, 3.5, 3) & ~mask_ell(152, 91, 2, 1.6)] = 1                              # locking wheel
    px[91, 149:156] = 1; px[89:94, 152] = 1
    px[85:87, 143] = 3; px[95:97, 143] = 3                                                       # hinges
    fill(mask_poly([(144, 48), (160, 48), (160, 56), (144, 56)]), 3, .7, 0)                       # docking tunnel
    line((144, 48), (160, 48), 3)
    for qx, ax in ((84, 93), (206, 197)):                                                         # RCS pods on arms
        line((ax, 78), (qx, 78), 3)
        fill(mask_poly([(qx - 4, 74), (qx + 4, 74), (qx + 4, 82), (qx - 4, 82)]), 3, .6, 0)
        px[78, qx - 6:qx + 7] = 3; px[71:86, qx] = 3                                              # thruster nozzles
    line((116, 66), (102, 48), 3)                                                                 # antenna boom
    px[mask_ell(100, 45, 6, 4.5)] = 3                                                             # dish
    px[mask_ell(101, 46, 3, 2.2)] = 0
    line((178, 66), (180, 52), 3); fill(mask_poly([(180, 50), (186, 50), (186, 55), (180, 55)]), 3)   # small antenna
    # engine skirt under the stage
    fill(mask_poly([(140, 142), (164, 142), (168, 150), (136, 150)]), 3, .4, 0)

    # front legs: main strut, secondary struts, foot pads
    for top, knee, foot in [l for i, l in enumerate((((112, 128), (98, 150), (90, 166)), ((192, 128), (206, 148), (214, 164)))) if i in legs]:
        line(top, foot, 3, 3)
        line(top, (top[0], top[1] - 1), 3)
        line((top[0] + (8 if top[0] < CX else -8), 142), knee, 3, 1)
        line((top[0], 114), knee, 3, 1)
        pad = mask_ell(foot[0], foot[1] + 1, 10, 3.2)
        px[pad] = 3
        px[pad & (yy > foot[1] + 1)] = 0
        px[mask_ell(foot[0], foot[1] + 1, 10, 3.2) & (yy == foot[1] + 3)] = 3
    # ladder rungs on the front-left strut
    for k in (range(5) if 0 in legs else []):
        t = (k + 1) / 7; x = 112 + (90 - 112) * t; y = 128 + (166 - 128) * t
        line((x - 3, y), (x + 3, y), 3)
    return px

def shadow():
    new_layer()
    # shadow cast to the left across the ground
    fill(mask_poly([(40, 160), (92, 150), (150, 146), (162, 156), (150, 172), (108, 182), (62, 186), (26, 178)]), 0)
    return px

def bag():
    new_layer()
    # the jettisoned bag by the right leg
    px[mask_ell(230, 176, 9, 6.5)] = 3
    px[mask_ell(222, 179, 4, 3) & (TH < .4)] = 0
    fill(mask_poly([(212, 182), (226, 180), (232, 184), (218, 186)]), 0)
    return px

def shifted(layer, dy=DY):
    out = np.full((H, W), 255, np.uint8); out[dy:] = layer[:H - dy]; return out

from PIL import ImageFilter
def composite(base, layers):
    out = base.copy()
    for layer, outline in layers:
        lm = layer != 255
        if outline:
            ring = np.asarray(Image.fromarray(lm.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))) > 0
            out[ring & ~lm] = 0               # black outline separates the lander from the ground
        out[lm] = layer[lm]
    return out
ground_px = ground_layer.copy()
LANDED = composite(ground_px, [(shifted(shadow()), False), (shifted(lander()), True), (shifted(bag()), True)])

# ---------- wreck: snapped screen-right leg, lander tipped over onto that side ----------
body = lander(legs=(0,))
img = Image.fromarray(body, "L").rotate(-10, resample=Image.NEAREST, center=(214, 164), fillcolor=255)
wreck = np.full((H, W), 255, np.uint8); wreck[6:] = np.asarray(img)[:H - 6]    # tipped and sunk a little
px = wreck
line((206, 152), (224, 158), 3, 3)            # the snapped strut, bent under the stage
line((224, 158), (238, 156), 3, 2)
px[mask_ell(246, 168, 10, 3.2)] = 3           # its foot pad, torn off and lying flat
px[mask_ell(246, 169, 10, 3.2) & (yy > 169)] = 0
line((150, 120), (172, 134), 0, 1); line((172, 134), (166, 146), 0, 1)   # crack across the descent stage
debris = new_layer()
for x, y, c, r in ((120, 168, 2, 2.5), (176, 176, 3, 2), (196, 180, 2, 3), (262, 174, 3, 1.8),
                   (100, 172, 3, 1.6), (228, 182, 2, 2.2), (140, 180, 3, 1.4)):
    px[mask_ell(x, y, r * 1.4, r)] = c        # bits of foil and metal on the ground
wshadow = new_layer()
fill(mask_poly([(60, 158), (120, 150), (180, 152), (190, 166), (150, 178), (90, 182), (46, 176)]), 0)
WRECKED = composite(ground_px, [(shifted(wshadow), False), (shifted(wreck), True), (shifted(debris), True), (shifted(bag()), True)])

# ---------- crater: the lander is gone, a scorched crater and scattered wreckage ----------
crater = new_layer()
CXc, CYc, RX, RY = 156, 156, 50, 13
rim = mask_ell(CXc, CYc, RX + 7, RY + 4) & ~mask_ell(CXc, CYc, RX, RY)
px[rim & (TH < .85)] = 3                                       # raised bright rim
bowl = mask_ell(CXc, CYc, RX, RY)
px[bowl] = 0
lit = bowl & ~mask_ell(CXc + 9, CYc + 1, RX * .92, RY * .9)
px[lit & (TH < .8)] = 3                                        # thin sunlit crescent on the inner left wall
for k in range(70):                                            # ejecta thrown out in rays
    ang = rng.uniform(0, 2 * math.pi); d = rng.uniform(1.15, 1.75)
    x = CXc + math.cos(ang) * RX * d; y = CYc + math.sin(ang) * RY * d * 1.4
    if 0 <= x < W and horizon[int(min(max(x, 0), W - 1))] + 3 < y < H: px[int(y), int(x)] = 3 if k % 3 else 0
scorch = mask_ell(CXc, CYc, RX + 22, RY + 11) & ~mask_ell(CXc, CYc, RX + 7, RY + 4)
px[scorch & (rng.random((H, W)) < .25)] = 0                    # scorch marks around the rim
for x, y, c, r in ((100, 150, 2, 3), (206, 148, 2, 2.6), (226, 160, 3, 2), (84, 162, 3, 1.8),
                   (190, 172, 2, 2.2), (118, 172, 3, 1.6), (240, 152, 2, 1.8), (136, 146, 3, 2),
                   (170, 176, 2, 1.6), (96, 168, 2, 1.4), (216, 170, 3, 1.4)):
    px[mask_ell(x, y, r * 1.5, r)] = c                         # foil and metal fragments
    px[mask_ell(x - r, y + r * .7, r * 1.3, r * .5) & (px == 255)] = 0
line((214, 144), (226, 130), 3, 2); line((226, 130), (232, 132), 3, 1)   # a bent leg strut sticking up
px[mask_ell(246, 166, 9, 3)] = 3; px[mask_ell(246, 167, 9, 3) & (yy > 167)] = 0   # a lone foot pad
line((102, 156), (90, 148), 3, 1); line((90, 148), (86, 150), 3, 1)
CRATERED = composite(ground_px, [(shifted(crater), False)])

# ---------- save: three full screens (end-of-level pictures) ----------
for name, im in (("LANDED", LANDED), ("WRECK", WRECKED), ("CRATER", CRATERED)):
    bsave(f"{OUT}/{name}.PIC", cga_bytes(im), seg=0xB800)
    Image.fromarray(PAL[im]).resize((960, 720), Image.NEAREST).save(f"{OUT}/preview_{name.lower()}.png")
print("sky rows at x=0/160/319:", horizon[0], horizon[160], horizon[319])
