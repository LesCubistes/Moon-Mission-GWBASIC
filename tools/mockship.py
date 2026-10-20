"""Modern lander designs with corner thruster pods, and the 8-direction firing chart.
Sprites are drawn as a left half and mirrored, so they're always symmetric.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], np.uint8)
OUT = "/home/claude/gwbasic/build"
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
FS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
M = {".": 0, "c": 1, "r": 2, "g": 3}

def mirror(half):
    rows = [h + h[::-1] for h in half]
    return np.array([[M[c] for c in r] for r in rows], np.uint8)

SHIPS = {
 "M1. Modern LM": dict(half=[
    "........gg",
    "......gggg",
    ".gg..gcccc",
    ".gggggcc.c",
    ".gg..ggggg",
    "....rrrrrr",
    "...rrgrrrr",
    "...rrrrrrr",
    "....g...gg",
    "...g...ggg",
    "..g.......",
    ".g........",
    "gg........"], pods=(1, 3), bell=9),
 "M2. Tall crew lander": dict(half=[
    ".........g",
    "........gg",
    ".......gcc",
    ".gg....gc.",
    ".gggg.ggcc",
    ".gg..ggggg",
    ".....grrrr",
    ".....grgrr",
    ".....grrrr",
    "......g.gg",
    "....g...gg",
    "...g......",
    "..g.......",
    ".g........",
    "ggg......."], pods=(1, 4), bell=10),
 "M3. Compact angular": dict(half=[
    "......gg",
    "....gggg",
    "gg.gcccc",
    "ggggc.cc",
    "gg.ggggg",
    "..rrrrrr",
    ".rrgrrrr",
    "..rrrrrr",
    "..g...gg",
    ".g....g.",
    "g.......",
    "gg......"], pods=(0, 3), bell=8),
}

# RCS jets per pod as (dx, dy) steps outward from the pod nozzle; side = -1 left pod, +1 right pod
JET = {"side": (-1, 0), "up": (0, -1), "upout": (-1, -1), "downout": (-1, 1)}
# keypad -> list of (pod side, jet) that fire; push is opposite the exhaust
KEYS = {
    8: "MAIN",
    9: [(-1, "downout")],            # left pod fires down-left  -> push up-right
    6: [(-1, "side")],               # left pod fires left       -> push right
    3: [(-1, "upout")],              # left pod fires up-left    -> push down-right
    2: [(-1, "up"), (1, "up")],      # both pods fire up         -> push down
    1: [(1, "upout")],               # right pod fires up-right  -> push down-left
    4: [(1, "side")],                # right pod fires right     -> push left
    7: [(1, "downout")],             # right pod fires down-right-> push up-left
}
ARROW = {8: (0, -1), 9: (1, -1), 6: (1, 0), 3: (1, 1), 2: (0, 1), 1: (-1, 1), 4: (-1, 0), 7: (-1, -1)}

def frame(ship, key, pad=7):
    sp = mirror(ship["half"]); h, w = sp.shape
    px = np.zeros((h + 2 * pad, w + 2 * pad), np.uint8)
    px[pad:pad + h, pad:pad + w] = sp
    if key == 8:                                  # main engine plume under the bell
        cx = pad + w // 2
        for i, (half_w, col) in enumerate([(2, 3), (2, 2), (1, 2), (1, 2), (0, 2), (0, 2)]):
            px[pad + ship["bell"] + 1 + i, cx - 1 - half_w:cx + 1 + half_w] = col
        px[pad + ship["bell"] + 1, cx - 1:cx + 1] = 3
    elif key in KEYS:
        pxp, pyp = ship["pods"]
        for side, jet in KEYS[key]:
            dx, dy = JET[jet]
            if side == 1: dx = -dx
            x0 = pad + (pxp if side == -1 else w - 1 - pxp)
            y0 = pad + pyp
            for k, col in ((1, 3), (2, 3), (3, 1), (4, 1)):
                px[y0 + dy * k, x0 + dx * k] = col
    return px

def big(px, s):
    return Image.fromarray(PAL[px]).resize((px.shape[1] * s, int(px.shape[0] * s * 1.2)), Image.NEAREST)

# ---- sheet 1: hull designs ----
sheet = Image.new("RGB", (1260, 470), (24, 24, 28)); d = ImageDraw.Draw(sheet)
x = 30
for name, sh in SHIPS.items():
    sp = mirror(sh["half"])
    d.text((x, 14), f"{name} ({sp.shape[1]}x{sp.shape[0]})", font=F, fill=(230, 230, 230))
    sheet.paste(big(frame(sh, 8, pad=6), 9), (x, 50))
    sheet.paste(big(frame(sh, 0, pad=1), 2), (x + 300, 70))
    d.text((x + 300, 48), "actual x2", font=FS, fill=(150, 150, 150))
    x += 420
sheet.save(f"{OUT}/mock_ships.png")

# ---- sheet 2: firing chart (keypad layout) for every hull ----
for tag, (name, sh) in zip(("M1", "M2", "M3"), SHIPS.items()):
    S = 8
    cell = big(frame(sh, 0), S).size
    cw, ch = cell[0] + 30, cell[1] + 60
    chart = Image.new("RGB", (cw * 3 + 20, ch * 3 + 70), (24, 24, 28)); d = ImageDraw.Draw(chart)
    d.text((14, 12), f"{name}: keypad thrusters (arrow = direction the lander is pushed)", font=F, fill=(230, 230, 230))
    layout = [[7, 8, 9], [4, 5, 6], [1, 2, 3]]
    for r, row in enumerate(layout):
        for c, k in enumerate(row):
            ox, oy = 10 + c * cw, 50 + r * ch
            chart.paste(big(frame(sh, k), S), (ox + 15, oy + 40))
            label = {8: "8 MAIN ENGINE", 5: "5 (no thrust)"}.get(k, f"{k} RCS")
            d.text((ox + 15, oy + 8), label, font=F, fill=(230, 230, 230))
            if k in ARROW:
                ax, ay = ARROW[k]
                cx, cy = ox + 15 + cell[0] - 28, oy + 22
                d.line((cx - ax * 12, cy - ay * 12, cx + ax * 12, cy + ay * 12), fill=(90, 255, 90), width=4)
                d.ellipse((cx + ax * 12 - 5, cy + ay * 12 - 5, cx + ax * 12 + 5, cy + ay * 12 + 5), fill=(90, 255, 90))
    chart.save(f"{OUT}/mock_thrusters_{tag}.png")
print("ok")
