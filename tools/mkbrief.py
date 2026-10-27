"""The mission briefing shown once when the Lunar Landing mission starts, before the landing site screen.

Three pages drawn here with the real CGA 8x8 font (so they look like the rest of the game but text
can sit on any pixel row), plus pictures of the lander made from the game's own sprites.
Writes to OUTDIR:
  BRIEF1.RLE .. BRIEF3.RLE   RLE-packed CGA screens (CKPIT.BIN mode 6 unpacks them)
  preview_brief.png          the three pages side by side
usage: mkbrief.py OUTDIR LANDERDIR   (LANDERDIR holds LMSHIP.SPR etc. from mklander)
"""
import sys, os, struct
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import mockscene as SC
from mklevel_io import cga_bytes, bsave, rle, unrle

OUT, LDIR = sys.argv[1], sys.argv[2]
W, H = 320, 200
CY, RD, GY = 1, 2, 3                     # cyan, red, grey

# ---------------- the CGA ROM font ----------------
FONT = {}
import pcbasic
for line in open(os.path.join(os.path.dirname(pcbasic.__file__), "data", "fonts", "cga_08.hex")):
    k, v = line.strip().split(":")
    if len(k) == 4 and int(k, 16) < 128:
        FONT[chr(int(k, 16))] = bytes.fromhex(v)

def text(px, x, y, s, c=GY):
    """draw s at pixel x, y; {1} {2} {3} switch colour"""
    i = 0
    while i < len(s):
        if s[i] == "{":
            c = int(s[i + 1]); i += 3; continue
        g = FONT.get(s[i], FONT["?"])
        for r in range(8):
            for b in range(8):
                if g[r] >> (7 - b) & 1 and 0 <= y + r < H and 0 <= x + b < W:
                    px[y + r, x + b] = c
        x += 8; i += 1
    return x

def centre(px, y, s, c=GY):
    n = len(s) - 3 * s.count("{")
    text(px, (W - 8 * n) // 2, y, s, c)

def box(px, x0, y0, x1, y1, c):
    px[y0, x0:x1 + 1] = c; px[y1, x0:x1 + 1] = c; px[y0:y1 + 1, x0] = c; px[y0:y1 + 1, x1] = c

def heading(px, y, s):
    text(px, 8, y, s, RD)
    px[y + 9, 8:8 + 8 * len(s)] = RD

# ---------------- the game's own lander sprites ----------------
def spr(name):
    d = open(os.path.join(LDIR, name + ".SPR"), "rb").read()[7:]
    wb, h = struct.unpack("<HH", d[:4]); w = wb // 2; rb = (wb + 7) // 8
    a = np.zeros((h, w), np.uint8)
    for y in range(h):
        row = d[4 + y * rb:4 + (y + 1) * rb]
        for x in range(w):
            a[y, x] = row[x // 4] >> (6 - 2 * (x % 4)) & 3
    return a

def lander(px, x, y, *extra):
    s = spr("LMSHIP").copy()
    for e in extra:
        f = spr(e); s[f > 0] = f[f > 0]
    sub = px[y:y + s.shape[0], x:x + s.shape[1]]
    sub[s > 0] = s[s > 0]

def frame(px, page):
    box(px, 0, 0, 319, 199, CY)
    centre(px, 4, "MISSION BRIEFING")
    text(px, 280, 4, f"{page}/3", CY)
    px[13, 1:319] = CY

def footer(px, s):
    px[186, 1:319] = CY
    centre(px, 189, s, CY)

def keycap(px, x, y, s, c):
    box(px, x, y, x + 8 * len(s) + 3, y + 11, CY)
    text(px, x + 2, y + 2, s, c)

pages = []

# ---------------- page 1: the goal and the keyboard ----------------
p = np.zeros((H, W), np.uint8); frame(p, 1)
heading(p, 18, "THE GOAL")
text(p, 8, 32, "Set the lander down gently on flat")
text(p, 8, 41, "ground. Land on a pad for a bonus.")
text(p, 8, 50, "You get {1}3 landers{3} for each mission.")
heading(p, 64, "KEYBOARD (NUMBER PAD)")
KX, KY = 12, 80                                    # a number pad picture, coloured by job
for r, row in enumerate(("789", "456", "123")):
    for c, k in enumerate(row):
        col = RD if k in "85" else (GY if k != "5" else RD)
        keycap(p, KX + 15 * c, KY + 14 * r, k, RD if k in "85" else GY)
keycap(p, KX, KY + 42, "  0  ", CY)
y = 80
for keys, what in (("{2}8 +{3}", "more thrust (+10%)"), ("{2}5 -{3}", "less thrust (-10%)"),
                   ("{1}0 SPACE{3}", "engine off"), ("4 6", "push left / right"),
                   ("7 9", "lift up-left/up-right"), ("1 2 3", "push down"), ("ESC", "back to orbit")):
    text(p, 64, y, keys); text(p, 128, y, what); y += 10
text(p, 8, 154, "Thrust slows your fall and the")
text(p, 8, 163, "side jets steer. Every puff")
text(p, 8, 172, "burns a little fuel.")
lander(p, 272, 148, "FL3")
footer(p, "PRESS A KEY  (ESC SKIPS)")
pages.append(p)

# ---------------- page 2: the gamepad and the gauges ----------------
p = np.zeros((H, W), np.uint8); frame(p, 2)
heading(p, 18, "GAMEPAD  (J ON THE TITLE SCREEN)")
y = 32
for a, b in (("{2}A{3} thrust up", "{1}B{3} thrust down"), ("{3}C{3} engine off", "{1}D{3} back to orbit")):
    text(p, 16, y, a); text(p, 168, y, b); y += 10
text(p, 16, y, "D-pad steers like the number pad."); y += 12
text(p, 16, y, "{2}HOLD A TO BURN{3} (set it in the pad"); y += 9
text(p, 16, y, "setup): the engine fires only while A"); y += 9
text(p, 16, y, "is held. Up/down on the D-pad sets"); y += 9
text(p, 16, y, "how hard it burns.")
heading(p, 106, "READING THE GAUGES")
# a copy of the flight display's top two lines
box(p, 4, 117, 315, 137, CY)
box(p, 44, 119, 125, 125, GY); p[121:124, 46:46 + 52] = CY
text(p, 136, 118, "LANDER 1/3"); text(p, 252, 118, "T 0:08")
text(p, 8, 127, "ALT  120 H +1.5 V -3.2 THR  60")
y = 141
for k, what in (("{1}ALT{3}", "height above the ground"),
                ("{1}H{3}", "drift: +1.5 means moving right"),
                ("{1}V{3}", "fall: -3.2 means moving down"),
                ("{1}THR{3}", "engine power, in percent"),
                ("{1}FUEL{3}", "the bar at the top left")):
    text(p, 16, y, k); text(p, 64, y, what); y += 9
footer(p, "PRESS A KEY  (ESC SKIPS)")
pages.append(p)

# ---------------- page 3: landing, scoring, the three sites ----------------
p = np.zeros((H, W), np.uint8); frame(p, 3)
heading(p, 18, "A SAFE LANDING")
text(p, 8, 31, "{1}V{3} no faster than {2}-4.0{3}, {1}H{3} within {2}2.0{3}")
text(p, 8, 40, "and both feet on level ground.")
heading(p, 52, "SCORING")
y = 65
for a, b in (("SOFT LANDING", "500, less for speed"), ("TIME BONUS", "2000, less 50 a second"),
             ("{2}x PAD{3}", "x2 to x10 (off a pad x1)"), ("{2}x LANDER{3}", "2nd lander 1/2, 3rd 1/4")):
    text(p, 8, y, a); text(p, 120, y, b); y += 9
heading(p, 106, "LANDING SITES")
y = 120
for name, lvl, c, fuel, a in (("TRANQUILITY BASE", "EASY", CY, 800, "Flat sea, slow drift, top pad x5"),
                              ("FRA MAURO", "MEDIUM", GY, 700, "Hills and boulders, top pad x7"),
                              ("HADLEY RILLE", "HARD", RD, 650, "Mountains, fast drift, top pad x10")):
    text(p, 8, y, name); text(p, 160, y, f"FUEL {fuel}", CY); text(p, 312 - 8 * len(lvl), y, lvl, c)
    text(p, 16, y + 9, a)
    y += 21
footer(p, "PRESS A KEY TO CHOOSE A SITE")
pages.append(p)

for i, p in enumerate(pages, 1):
    packed = rle(cga_bytes(p))
    assert unrle(packed) == cga_bytes(p) and len(packed) < 12288, len(packed)
    bsave(f"{OUT}/BRIEF{i}.RLE", packed)
    print(f"BRIEF{i}.RLE", len(packed), "bytes")
gap = np.full((H, 4), 0, np.uint8)
SC.big(np.concatenate([pages[0], gap, pages[1], gap, pages[2]], axis=1)).save(f"{OUT}/preview_brief.png")
for i, p in enumerate(pages, 1):
    SC.big(p).save(f"{OUT}/preview_brief{i}.png")
