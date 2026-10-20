"""Build Moon Landing assets for the Easy level (Tranquility Base).

Outputs in OUTDIR:
  EASY.PIC   BSAVE of CGA video RAM: stars, Earth, highlands, terrain, pads, pad labels, HUD frame
  EASY.MAP   BSAVE of 640 integers: H(0..319) = ground row per column,
             H(320+x) = highest ground (min row) under the lander footprint x..x+27
  LMSHIP.SPR lander sprite on a 36x32 canvas (ship at +4,+3)
  LMMASK.SPR AND-mask for that canvas (3 = keep background, 0 = ship pixel)
  FL1-3.SPR  main engine flame small/medium/large (same canvas)
  RCn.SPR    thruster puff for keypad key n (1,2,3,4,6,7,9)
"""
import sys, struct, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import mockship2 as MS
    import mockscene as SC

OUT = sys.argv[1]
CW, CH, OX, OY = 36, 32, 4, 3          # sprite canvas and ship offset
FOOT = 28

def cga_bytes(px):
    mem = bytearray(16384)
    for y in range(200):
        o = (y & 1) * 0x2000 + (y >> 1) * 80
        for i in range(80):
            p = px[y, i * 4:i * 4 + 4]
            mem[o + i] = (int(p[0]) << 6) | (int(p[1]) << 4) | (int(p[2]) << 2) | int(p[3])
    return bytes(mem)

def bsave(path, data, seg=0):
    with open(path, "wb") as f:
        f.write(bytes([0xFD]) + struct.pack("<HHH", seg, 0, len(data)) + data + b"\x1a")

def sprite(px):
    h, w = px.shape
    data = bytearray(struct.pack("<HH", w * 2, h))
    rb = (w * 2 + 7) // 8
    for y in range(h):
        row = [int(v) for v in px[y]] + [0] * (rb * 4 - w)
        for i in range(rb):
            p = row[i * 4:i * 4 + 4]
            data.append((p[0] << 6) | (p[1] << 4) | (p[2] << 2) | p[3])
    if len(data) % 2: data.append(0)
    return bytes(data)

# ---------- background ----------
px, g, PADS, CRATERS = SC.build()
px[0:17] = 0
px[22:34, 88:236] = 0                  # clear stars behind the site title
px[17, :] = 1                          # HUD divider
px[1, 40:122] = 3; px[5, 40:122] = 3; px[1:6, 40] = 3; px[1:6, 121] = 3   # fuel bar frame
from mklevel_io import pad_patches
pad_patches(px, g, [(a, b, int(lab[1:])) for a, b, lab in PADS])      # shaded patches, no labels
bsave(f"{OUT}/EASY.PIC", cga_bytes(px), seg=0xB800)

# ---------- collision map ----------
H = [int(v) for v in g]
MN = [min(H[x:x + FOOT]) if x + FOOT <= 320 else min(H[x:]) for x in range(320)]
bsave(f"{OUT}/EASY.MAP", struct.pack("<640h", *(H + MN)))

# ---------- lander sprites ----------
ship = np.zeros((CH, CW), np.uint8)
MS.ship(ship, OX, OY)
mask = np.where(ship > 0, 0, 3).astype(np.uint8)
fx = []
for length in (3, 6, 9):
    e = np.zeros((CH, CW), np.uint8)
    MS.main_plume(e, OX, OY + MS.AH + MS.BELL_Y + 1, length)
    e[ship > 0] = 0
    fx.append(e)
for key in (1, 2, 3, 4, 6, 7, 9):
    e = np.zeros((CH, CW), np.uint8)
    MS.rcs(e, OX, OY, key)
    e[ship > 0] = 0
    fx.append(e)
bsave(f"{OUT}/LMSHIP.SPR", sprite(ship))
bsave(f"{OUT}/LMMASK.SPR", sprite(mask))
for i, e in enumerate(fx[:3]): bsave(f"{OUT}/FL{i + 1}.SPR", sprite(e))       # flames small/med/large
for k, e in zip((1, 2, 3, 4, 6, 7, 9), fx[3:]): bsave(f"{OUT}/RC{k}.SPR", sprite(e))   # thruster puffs by key

# preview of the background
SC.big(px).save(f"{OUT}/preview_easy_bg.png")
print("sprite ints:", len(sprite(ship)) // 2, " pads:", [(a, b, H[a]) for a, b, _ in PADS])
print("min MN", min(MN), "max H", max(H))

# ---------- crash poses (40x34 canvas, pose bottom-aligned, centred) ----------
with contextlib.redirect_stdout(io.StringIO()):
    import mockcrash as CR
PW, PH = 40, 34
def pose(sp):
    c = np.zeros((PH, PW), np.uint8)
    h, w = sp.shape
    assert h <= PH and w <= PW, (h, w)
    c[PH - h:, (PW - w) // 2:(PW - w) // 2 + w] = sp
    return c
POSES = {
    1: CR.ship_px(True),                      # COL   legs folded
    2: CR.rot(CR.ship_px(True, True), 11),    # COLT  slumped, leg snapped
    3: CR.rot(CR.ship_px(), 40),              # TR40  tipping right
    4: CR.rot(CR.ship_px(), -40),             # TL40  tipping left
    5: CR.rot(CR.ship_px(), 90),              # TR90  on its side, fell right
    6: CR.rot(CR.ship_px(), -90),             # TL90  on its side, fell left
    7: CR.rot(CR.ship_px(True, True), 180),   # FLIP  upside down
}
for n, sp in POSES.items():
    c = pose(sp)
    bsave(f"{OUT}/CP{n}.SPR", sprite(c))
    bsave(f"{OUT}/CM{n}.SPR", sprite(np.where(c > 0, 0, 3).astype(np.uint8)))
print("pose ints:", len(sprite(pose(POSES[1]))) // 2)
