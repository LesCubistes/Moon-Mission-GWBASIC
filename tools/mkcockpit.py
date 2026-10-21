"""MOCKUP: the success ending seen from inside the lander (cockpit window view).

Built the way the game would draw it, so the mockup is honest about what an 8088 can do:
  * one full-screen cockpit picture (interior, window frame, helmet visor edge, glove on the
    throttle, a modern glass panel) drawn once
  * out of the window, two strips per site slid upward frame by frame:
      - the RIM strip (black sky + the distant crater rim), moving a little faster than
      - the GROUND strip (regolith from the horizon down), so the rim rises above the horizon
        as you sink into the crater
    each frame = PUT rim, PUT ground (height-clipped), then the window frame mask/overlay
  * engine dust streaking across the bottom of the window near the end, a 2-pixel jolt at
    touchdown, then the results on the centre display
usage: mkcockpit.py OUTDIR   -> cockpit_<site>.gif (descent), cockpit_<site>_result.png
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import mockscene as SC

W, H = 320, 200
PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], np.uint8)
BAYER = SC.BAYER
yy, xx = np.mgrid[0:H, 0:W]
TH = BAYER[yy % 4, xx % 4]

# ---------------- window geometry ----------------
WX0, WY0, WX1, WY1 = 64, 12, 243, 107            # bounding box of the window (180 x 96)
WW, WH = WX1 - WX0 + 1, WY1 - WY0 + 1
# the lander's left cabin window seen from inside: straight top, straight outer edge,
# a short inner edge, then the long diagonal back down to the bottom (same shape as outside)
WIN = [(64, 12), (243, 12), (243, 36), (168, 107), (64, 107)]

def poly(pts, w=W, h=H):
    m = Image.new("1", (w, h), 0); ImageDraw.Draw(m).polygon(pts, fill=1); return np.asarray(m)
def ell(cx, cy, rx, ry): return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
def line(px, p0, p1, c, width=1):
    m = Image.new("1", (W, H), 0); ImageDraw.Draw(m).line([p0, p1], fill=1, width=width); px[np.asarray(m)] = c

window = poly(WIN)

# ---------------- the cockpit picture (drawn once) ----------------
def cockpit():
    px = np.zeros((H, W), np.uint8)
    # interior walls: dark, with a few outlined panels, seams and rivets (not a dither wash)
    for pts in ([(4, 6), (58, 18), (58, 108), (4, 108)], [(262, 18), (316, 6), (316, 108), (262, 108)]):
        m = poly(pts); e = m & ~poly([(p[0] + (2 if i in (0, 3) else -2), p[1] + (2 if i < 2 else -2)) for i, p in enumerate(pts)])
        px[e] = 3
        px[m & ~e & (xx % 6 == 0) & (yy % 2 == 0)] = 3          # faint ribbed surface
    for x, y in ((10, 14), (52, 22), (10, 102), (52, 102), (268, 22), (310, 14), (268, 102), (310, 102)):
        px[y, x] = 1; px[y, x + 1] = 1
    # window frame: solid grey rim, darker inner bevel, cyan bolts
    outer = poly([(57, 5), (250, 5), (250, 39), (171, 114), (57, 114)])
    rim = outer & ~window
    px[rim] = 3
    bevel = poly([(61, 9), (246, 9), (246, 37), (169, 110), (61, 110)]) & ~window
    px[bevel & (xx % 2 == yy % 2)] = 0
    for t in np.linspace(.04, .96, 9):
        for (a, b) in (((57, 6), (250, 6)), ((171, 112), (57, 112)), ((250, 39), (171, 112))):
            x = int(a[0] + (b[0] - a[0]) * t); y = int(a[1] + (b[1] - a[1]) * t)
            px[y:y + 2, x:x + 2] = 1
    px[poly([(251, 5), (262, 5), (262, 114), (251, 114)])] = 3          # centre post between the windows
    px[poly([(251, 5), (262, 5), (262, 114), (251, 114)]) & (xx % 2 == 0) & (yy % 2 == 0)] = 0
    # glare shield over the panel
    px[116:125, :] = 0
    line(px, (0, 116), (319, 116), 3); line(px, (0, 124), (319, 124), 3)
    px[118:123, :][(xx[118:123, :] % 4 == 0)] = 3
    # panel body: black with screw heads
    for x in (2, 56, 262, 316):
        px[128, x] = 3; px[188, x] = 3
    def mfd(x0, y0, x1, y1):
        px[y0:y1 + 1, x0:x1 + 1] = 0
        line(px, (x0, y0), (x1, y0), 1); line(px, (x0, y1), (x1, y1), 1)
        line(px, (x0, y0), (x0, y1), 1); line(px, (x1, y0), (x1, y1), 1)
        for cx, cy, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            line(px, (cx + 2 * dx, cy + 2 * dy), (cx + 8 * dx, cy + 2 * dy), 3)
            line(px, (cx + 2 * dx, cy + 2 * dy), (cx + 2 * dx, cy + 6 * dy), 3)
    mfd(60, 126, 259, 191)            # centre: 24 text columns x 7 rows (text rows 17..23, cols 9..32)
    mfd(6, 126, 52, 191)              # left: altitude tape
    mfd(266, 126, 313, 158)           # right: attitude
    for y in range(132, 188, 6):
        line(px, (10, y), (14 if y % 12 else 17, y), 3)
    line(px, (276, 142), (303, 142), 1); line(px, (289, 133), (289, 151), 3)
    px[141:144, 288:291] = 2
    # throttle: T-handle rising from the panel, gloved hand gripping it, suit cuff to the corner
    line(px, (283, 199), (283, 180), 3, 3)                     # stem
    hand = poly([(268, 168), (276, 162), (296, 162), (302, 168), (300, 178), (272, 178)])
    px[hand] = 3
    for x in (277, 283, 289, 295):                             # fingers wrapped over the bar
        line(px, (x, 163), (x, 177), 0)
    line(px, (268, 168), (272, 178), 0); line(px, (266, 172), (270, 166), 3, 2)   # thumb
    cuff = poly([(286, 178), (302, 172), (319, 186), (319, 199), (296, 199)])
    px[cuff] = 3; px[cuff & (xx % 3 == 0)] = 0                 # ribbed suit cuff
    line(px, (286, 178), (302, 172), 0)
    # helmet visor: the view is framed by the curve of your visor in the upper corners,
    # with a faint reflection streak
    visor = ell(160, 112, 206, 124)
    px[~visor & (yy < 125)] = 0
    ring = visor & ~ell(160, 112, 202, 121) & (yy < 125)
    px[ring] = 3
    for k in range(18):                                        # reflection on the visor, upper left
        x = 20 + k * 3; y = 40 - int(k * 1.6)
        if 0 <= y < H: px[y, x] = 1; px[y, x + 1] = 1
    return px

COCK = cockpit()

# ---------------- outside: two strips per site ----------------
def smooth(w, h, scale, seed):
    r = np.random.default_rng(seed).random((h // scale + 3, w // scale + 3))
    img = Image.fromarray((r * 255).astype(np.uint8)).resize(((w // scale + 3) * scale, (h // scale + 3) * scale), Image.BICUBIC)
    return np.asarray(img).astype(float)[:h, :w] / 255

def rim_strip(profile, seed, h=40):
    """black sky + distant ridges whose top follows profile(x) (rows from strip top)"""
    s = np.zeros((h, WW), np.uint8)
    ys, xs = np.mgrid[0:h, 0:WW]
    th = BAYER[ys % 4, xs % 4]
    top = np.array([profile(x) for x in range(WW)])
    body = ys >= top[None, :]
    lit = 0.55 - 0.35 * np.clip((ys - top[None, :]) / 20, 0, 1) + 0.15 * (smooth(WW, h, 6, seed) - .5)
    slope = np.gradient(top.astype(float))[None, :]               # sun from the right: right-facing slopes lit
    lit = lit + np.where(slope < 0, -0.2, 0.12)
    s[body & (lit > th)] = 3
    s[ys == top[None, :]] = 3
    return s

def ground_strip(seed, features, base=0.55):
    """regolith from the horizon (row 0) down; craters and boulders get bigger toward the bottom"""
    h = 110; ys, xs = np.mgrid[0:h, 0:WW]
    th = BAYER[ys % 4, xs % 4]
    rng = np.random.default_rng(seed)
    d = np.clip(ys / h, 0, 1)
    dens = base - 0.30 * d + 0.18 * (smooth(WW, h, 14, seed) - .5) + 0.08 * (smooth(WW, h, 5, seed + 1) - .5)
    s = np.zeros((h, WW), np.uint8)
    s[dens > th] = 3
    s[0:2, :] = 3                                              # bright horizon line
    for _ in range(26):
        cy = rng.uniform(4, h); cx = rng.uniform(0, WW)
        r = 1 + 2.2 * (cy / h) * rng.uniform(.5, 1.3)
        rx, ry = r, r * (0.25 + 0.5 * cy / h)
        m = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
        s[m < 1] = 0
        s[(m < 1) & (xs > cx + rx * .2) & (th < .5)] = 3          # sunlit far wall
        s[(m >= 1) & (m < 1.6) & (xs > cx - rx * .2)] = 3
    for f in features: f(s, xs, ys, th, rng)
    return s

def mountain(cx, w, hgt):
    def f(s, xs, ys, th, rng): pass
    return f

def hummocks(bands):
    def f(s, xs, ys, th, rng):
        for row, amp, period, phase in bands:                   # low ridges across the ground, lit on top
            top = row + amp * np.sin(xs / period + phase)
            ridge = (ys > top - 3) & (ys < top)
            s[ridge] = 3
            s[(ys >= top) & (ys < top + 3) & (th < .75)] = 0      # shadow just behind each ridge
    return f
def cone_rim(s, xs, ys, th, rng):                                # Fra Mauro: Cone crater's bright rim rising close on the right
    top = 26 - 22 * np.clip((xs - 100) / 80, 0, 1) ** 0.8
    m = (ys < 34) & (ys >= top) & (xs > 96)
    s[m] = 0
    s[m & (th < .7 - (ys - top) / 40)] = 3
    s[(np.abs(ys - top) < 1.2) & (xs > 96)] = 3
def rille(s, xs, ys, th, rng):                                   # Hadley: a dark winding channel across the middle ground
    mid = 46 + 7 * np.sin(xs / 26 + 1) + xs * 0.05
    band = np.abs(ys - mid) < 6 + xs * 0.01
    s[band] = 0
    s[band & (ys < mid - 2) & (th < .5)] = 3                     # sunlit far wall of the rille
    s[np.abs(ys - (mid - 6 - xs * .01)) < 1] = 3                # bright lip

def rim_tranq(x): return int(30 - 3 * math.sin(x / 47) - 1.5 * math.sin(x / 11 + 1))          # long, low, smooth rim
def rim_fra(x):                                                 # rumpled highland skyline + Cone crater's rim close on the right
    far = 30 - 6 * math.exp(-((x - 50) / 24) ** 2) - 3 * math.sin(x / 9) ** 2 - 1.5 * math.sin(x / 4.1)
    cone = 34 - 30 * math.exp(-((x - 158) / 30) ** 2)
    return int(max(3, min(far, cone)))
def rim_hadley(x):                                              # Mount Hadley towering left, Hadley Delta right
    return int(max(3, 58 - 52 * math.exp(-((x - 40) / 30) ** 2) - 24 * math.exp(-((x - 150) / 30) ** 2)
                   - 6 * math.exp(-((x - 95) / 12) ** 2) - 1.5 * math.sin(x / 5)))

SITES = {
    "tranquility": dict(title=("TRANQUILITY BASE HERE.", "THE EAGLE HAS LANDED."),
                        rim=rim_tranq, rimh=56, foot=34, base=0.42, ground=[]),
    "fra_mauro":   dict(title=("FRA MAURO BASE HERE.", "TOUCHDOWN CONFIRMED."),
                        rim=rim_fra, rimh=56, foot=34, base=0.66,
                        ground=[hummocks(((34, 3, 17, 0), (54, 4, 23, 2), (78, 5, 29, 4)))]),
    "hadley":      dict(title=("HADLEY BASE HERE.", "TOUCHDOWN CONFIRMED."),
                        rim=rim_hadley, rimh=82, foot=60, base=0.54, ground=[rille]),
}

import random as _r
def scatter(seed, n, mix):
    g = _r.Random(seed)
    return [(g.choice(mix), g.randrange(0, WW + 40), int(4 + 66 * g.random() ** 1.2)) for _ in range(n)]
SITES["tranquility"]["pieces"] = scatter(1, 13, ("crater",) * 5 + ("boulder",))          # cratered mare, few rocks
SITES["fra_mauro"]["pieces"] = scatter(2, 9, ("boulder",) * 3 + ("crater",))             # boulder field
SITES["hadley"]["pieces"] = scatter(3, 7, ("crater", "boulder"))

def piece(kind, size):
    """a crater or a boulder as a small sprite (255 = transparent), at most 16 px wide"""
    w = (6, 10, 16)[size]; h = (3, 5, 8)[size]
    ys, xs = np.mgrid[0:h, 0:w]
    th = BAYER[ys % 4, xs % 4]
    sp = np.full((h, w), 255, np.uint8)
    cx, cy, rx, ry = (w - 1) / 2, (h - 1) / 2, w / 2, h / 2
    m = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
    if kind == "crater":
        sp[m < 1] = 0
        sp[(m < 1) & (xs > cx + rx * .1) & (th < .55)] = 3       # sunlit far wall
        sp[(m >= .7) & (m < 1) & (xs > cx - rx * .3)] = 3          # bright rim
    else:                                                       # boulder: lit right, shadow trailing left
        sp[(m < 1) & (ys < cy + 1)] = 3
        sp[(m < 1) & (xs < cx) & (th < .5)] = 0
        sp[(ys >= cy + 1) & (xs < cx + 1)] = 0
    return sp
PIECES = {(k, z): piece(k, z) for k in ("crater", "boulder") for z in range(3)}
def place(view, sp, x, y):
    h, w = sp.shape
    for r in range(h):
        for c in range(w):
            v = sp[r, c]
            if v != 255 and 0 <= y + r < WH and 0 <= x + c < WW: view[y + r, x + c] = v

# dust sprites in the window (XOR): grains streaking outward from the centre, bottom of the window
def dust_frame(k, strength):
    d = np.zeros((WH, WW), np.uint8)
    rng = np.random.default_rng(100 + k)
    n = int(80 * strength)
    for _ in range(n):
        side = rng.choice((-1, 1)); y = int(rng.uniform(WH * .62, WH - 2))
        x0 = WW // 2 + side * rng.uniform(4, WW // 2)
        L = int(rng.uniform(2, 7))
        for i in range(L):
            x = int(x0 + side * i)
            if 0 <= x < WW: d[y, x] = 3
    return d

def frame(site, t, panel, dust=0.0, jolt=0, drift=0.0):
    """t: 0 (high) .. 1 (touchdown). Returns the full 320x200 frame."""
    cfg = SITES[site]
    rimS = cfg["_rim"]; grS = cfg["_ground"]
    hz = int(round(WH - 8 - (WH - 8 - 44) * t ** 0.8))         # horizon row in the window: 88 -> 44
    rim_up = int(round(4 + 12 * t))                            # rim stands higher as we sink into the crater
    view = np.zeros((WH, WW), np.uint8)
    ry = hz - cfg["foot"] - rim_up + jolt
    for r in range(rimS.shape[0]):
        y = ry + r
        if 0 <= y < WH: view[y] = rimS[r]
    for r in range(grS.shape[0]):
        y = hz + jolt + r
        if 0 <= y < WH: view[y] = grS[r]
    # craters and boulders ride on the ground strip and slide sideways with the drift:
    # near ones (lower in the window) slide faster, so it reads as depth
    for kind, wx, row in cfg["pieces"]:
        y = hz + jolt + row
        if y >= WH: continue
        depth = row / 70
        z = 0 if row < 20 else (1 if row < 45 else 2)
        x = int(round(wx - drift * (0.6 + 5 * depth))) % (WW + 40) - 20
        place(view, PIECES[(kind, z)], x, y)
    if dust > 0:
        view ^= dust_frame(int(t * 1000), dust)
    px = COCK.copy()
    sub = px[WY0:WY1 + 1, WX0:WX1 + 1]
    m = window[WY0:WY1 + 1, WX0:WX1 + 1]
    sub[m] = view[m]
    # panel text (PRINT-style, grey)
    for row, col, txt in panel:
        SC.text(px, row, col, txt, 3)
    fill = int(54 * min(1, max(0, (1 - t) ** 1.3)))            # the altitude tape, a bar per frame (LINE ... BF)
    if fill: px[186 - fill:186, 22:44] = 1
    return px

def big(px, s=2):
    return Image.fromarray(PAL[px]).resize((W * s, int(H * s * 1.2)), Image.NEAREST)

def main(OUT):
  for site, cfg in SITES.items():
    cfg["_rim"] = rim_strip(cfg["rim"], 3, cfg["rimh"])
    cfg["_ground"] = ground_strip(7 + len(site), cfg["ground"], cfg["base"])
    frames, durs = [], []
    N = 64                                                     # ~8 fps over 8 s of descent
    vx = {"tranquility": 1.6, "fra_mauro": -2.2, "hadley": 1.0}[site]   # heading at touchdown (from the flight)
    for k in range(N):
        t = k / (N - 1)
        alt = int(120 * (1 - t) ** 1.3); vs = -(0.6 + 3.2 * (1 - t) ** 0.7)
        drift = vx * 8 * t * (2 - t) * 4                       # how far we have slid, eased as we slow down
        panel = [(17, 10, "DESCENT"), (19, 10, f"ALT  {alt:4d} M"), (20, 10, f"V/S  {vs:+5.1f} M/S"),
                 (21, 10, f"H/S  {vx:+5.1f} M/S"), (22, 10, "LIGHTS  " + ("CONTACT" if alt < 6 else "       "))]
        dust = 0.0 if alt > 30 else min(1, (30 - alt) / 22)
        frames.append(frame(site, t, panel, dust, 0, drift)); durs.append(125)
    # touchdown jolt, engine stop, dust settles, then results
    for j, (jolt, dust, msg) in enumerate(((2, .9, "CONTACT"), (1, .7, "ENGINE STOP"), (0, .45, "ENGINE STOP"),
                                           (0, .25, "ENGINE STOP"), (0, .1, "ENGINE STOP"), (0, 0, "ENGINE STOP"))):
        panel = [(17, 10, "TOUCHDOWN"), (19, 10, "ALT     0 M"), (20, 10, "V/S  +0.0 M/S"), (22, 10, "LIGHTS  " + msg)]
        frames.append(frame(site, 1, panel, dust, jolt, vx * 8 * 4)); durs.append(160)
    a, b = cfg["title"]
    result = [(17, 9 + (24 - len(a)) // 2, a), (18, 9 + (24 - len(b)) // 2, b),
              (19, 10, "SOFT LANDING      150"), (20, 10, "TIME BONUS       1946"),
              (21, 10, "PAD X3    LANDER 1/3"), (22, 10, "SCORE            6290"), (23, 15, "PRESS ENTER")]
    last = frame(site, 1, result, 0, 0, vx * 8 * 4)
    frames.append(last); durs.append(2500)
    imgs = [big(f) for f in frames]
    imgs[0].save(f"{OUT}/cockpit_{site}.gif", save_all=True, append_images=imgs[1:], duration=durs, loop=0)
    big(last, 3).save(f"{OUT}/cockpit_{site}_result.png")
    big(frames[N // 3], 3).save(f"{OUT}/cockpit_{site}_mid.png")
  print("window", WW, "x", WH, "=", (WW * 2 + 7) // 8 * WH + 4, "bytes per full-window PUT")

if __name__ == "__main__":
    main(sys.argv[1])
