"""Build the CGA (320x200, palette 1/6) title art for MOON.BAS.

The moon surface is generated (craters, regolith texture). Earth is rendered from
the Earthrise photo's Earth disc, enlarged.

usage: mkart.py EARTH_PHOTO OUTDIR
Outputs: MOONBG.PIC (BSAVE of video RAM), EARTH.SPR, TITLE.SPR, layout.txt, preview_*.png
"""
import sys, os, struct, random, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]   # SRC unused now (kept for the old photo pipeline)
PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], np.uint8)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
yy, xx = np.mgrid[0:200, 0:320]
TH_ = BAYER[yy % 4, xx % 4]
random.seed(1969)

# ---------------- layout ----------------
EW, EH = 96, 80              # Earth sprite size (EW multiple of 4)
EX = 112                     # left edge of Earth
EY = 33                      # final top of Earth (under the title)
HT = 126                     # horizon line where Earth emerges
MARGIN = 2                   # black rows under Earth erase its trail
SH = EH + MARGIN

# ---------------- moon terrain ----------------
def smooth_noise(w, h, scale, seed):
    r = np.random.default_rng(seed)
    g = r.random((h // scale + 3, w // scale + 3))
    img = Image.fromarray((g * 255).astype(np.uint8)).resize(((w // scale + 3) * scale, (h // scale + 3) * scale), Image.BICUBIC)
    return np.asarray(img).astype(float)[:h, :w] / 255.0

# horizon: gentle hills on a curved limb, dead flat where Earth comes up
x = np.arange(320)
hz = HT - 1 + 3 * np.sin(x / 37.0) + 2 * np.sin(x / 13.0 + 1.3) + 1.5 * np.sin(x / 5.3)
SAG = 10                     # the Moon curves away: the horizon drops this much at the screen edges
limb = HT + SAG * ((x - 159.5) / 160.0) ** 2   # smooth, no hills, under the Earth (never above HT)
hz = hz + limb - HT
lo, hi = EX - 6, EX + EW + 5
for i in range(1, 15):
    t = i / 15
    if lo - i >= 0: hz[lo - i] = limb[lo - i] * (1 - t) + hz[lo - i] * t
    if hi + i < 320: hz[hi + i] = limb[hi + i] * (1 - t) + hz[hi + i] * t
hz[lo:hi + 1] = limb[lo:hi + 1]
hz = np.round(hz).astype(int)
moon = yy >= hz[None, :]

depth = np.clip((yy - hz[None, :]) / (200 - HT), 0, 1)
base = 0.50 + 0.08 * depth
tex = (0.55 * smooth_noise(320, 200, 24, 1) + 0.30 * smooth_noise(320, 200, 9, 2)
       + 0.15 * smooth_noise(320, 200, 3, 3)) - 0.5
shade = base + tex * (0.18 + 0.20 * depth)
shade += 0.18 * np.exp(-((yy - hz[None, :]) / 3.0) ** 2)     # bright lip at the horizon
maria = smooth_noise(320, 200, 64, 7)
shade -= 0.16 * np.clip((maria - 0.55) * 4, 0, 1)            # darker plains
shade += 0.10 * np.clip((0.4 - maria) * 4, 0, 1)             # lighter highlands

def crater(cx, cy, r):
    """sun from the left; ellipse flattens with distance"""
    ry = r * (0.30 + 0.25 * (cy - HT) / (200 - HT))
    for py in range(max(int(cy - 1.4 * ry), 0), min(int(cy + 1.4 * ry) + 1, 200)):
        for px in range(max(int(cx - 1.4 * r), 0), min(int(cx + 1.4 * r) + 1, 320)):
            if not moon[py, px]: continue
            u, v = (px - cx) / r, (py - cy) / ry
            d = math.hypot(u, v)
            if d < 1.0:
                if u < -0.05 and d > 0.25 - 0.3 * u:
                    shade[py, px] = 0.02                   # shadow inside the sunward wall
                elif u > 0.15 and d > 0.62:
                    shade[py, px] = 0.92                   # sunlit far inner wall
                else:
                    shade[py, px] = 0.40 + 0.15 * u        # floor
            elif d < 1.22:
                shade[py, px] = 0.88 if u < 0.1 else 0.22  # rim: lit toward the sun, shaded beyond
            elif d < 1.9 and r > 6:
                shade[py, px] += 0.07 * (1.9 - d)          # ejecta halo

craters = []
for n, ymin, ymax, rmin, rmax in ((3, 168, 192, 16, 26), (6, 145, 175, 8, 14),
                                   (16, 135, 190, 3, 7), (30, 130, 196, 1.5, 3)):
    tries = 0
    while n and tries < 800:
        tries += 1
        cx, cy = random.uniform(5, 315), random.uniform(ymin, ymax)
        r = random.uniform(rmin, rmax) * (0.6 + 0.6 * (cy - HT) / (200 - HT))
        if cy - 0.6 * r < hz[int(cx)] + 2: continue
        if any(math.hypot(cx - a, (cy - b) * 2.5) < (r + c) * 0.95 for a, b, c in craters): continue
        craters.append((cx, cy, r)); n -= 1
for c in sorted(craters, key=lambda c: -c[2]):
    crater(*c)

out = np.zeros((200, 320), np.uint8)
out[moon & (np.clip(shade, 0, 1) > TH_)] = 3

stars = 0
while stars < 50:
    sx_, sy_ = random.randrange(320), random.randrange(0, 120)
    if EX - 4 <= sx_ <= EX + EW + 4: continue
    if 6 <= sy_ <= 30 and 20 <= sx_ <= 300: continue
    if sy_ >= hz[sx_] - 3: continue
    out[sy_, sx_] = 1 if random.random() < 0.3 else 3
    stars += 1
bg = out.copy()

# ---------------- Earth: lit globe centered on the Americas ----------------
sys.path.insert(0, __import__("os").path.dirname(__file__))
import earth as E
STYLE = int(sys.argv[3]) if len(sys.argv) > 3 else 2   # 2 = red-black dither (chosen)
earth, disc = E.render(STYLE)
assert earth.shape == (EH, EW)
stats = {"style": STYLE, "land_px": int(((earth == 2) | (earth == 0) & disc).sum())}

full = bg.copy()
full[EY:EY + EH, EX:EX + EW][disc] = earth[disc]

# ---------------- title ----------------
font = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf", 30)
text, spacing = "MOON MISSION", 3
widths = [font.getbbox(c)[2] - font.getbbox(c)[0] if c != " " else 10 for c in text]
timg = Image.new("L", (sum(widths) + spacing * len(text) + 8, 40), 0)
d = ImageDraw.Draw(timg)
cx = 2
for c, w_ in zip(text, widths):
    if c != " ": d.text((cx - font.getbbox(c)[0], 0), c, font=font, fill=255)
    cx += w_ + spacing
ta = np.asarray(timg) > 110
ys_, xs_ = np.nonzero(ta)
ta = ta[ys_.min():ys_.max() + 1, xs_.min():xs_.max() + 1]
th2 = int(round(ta.shape[0] / 1.2))
ta = np.asarray(Image.fromarray(ta.astype(np.uint8) * 255).resize((ta.shape[1], th2), Image.LANCZOS)) > 110
tp = np.zeros((th2 + 2, ta.shape[1] + 2), np.uint8)
tp[1:-1, 1:-1][ta] = 3
sh = np.zeros_like(tp, bool); sh[2:, 2:] = tp[:-2, :-2] == 3
tp[sh & (tp != 3)] = 2
tp[(tp == 3) & (np.arange(tp.shape[0])[:, None] < tp.shape[0] * 0.38)] = 1
TW = tp.shape[1] + (-tp.shape[1]) % 4
tpad = np.zeros((tp.shape[0], TW), np.uint8); tpad[:, :tp.shape[1]] = tp
# the designer's credit under the title, on the right, the way Alley Cat signs "By Bill Williams"
nf = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "dancing-script-latin-400-normal.woff"), 17)
def script(txt):
    im = Image.new("L", (300, 40), 0); ImageDraw.Draw(im).text((2, 2), txt, font=nf, fill=255)
    a = np.asarray(im)
    a = np.asarray(Image.fromarray(a).resize((300, int(round(40 / 1.2))), Image.LANCZOS)) > 70
    ys_, xs_ = np.nonzero(a)
    return a[:, xs_.min():xs_.max() + 1], ys_.min(), ys_.max()
by, b0, b1 = script("by"); nm, n0, n1 = script("Ryan Barrineau")
top = min(b0, n0)
CW = nm.shape[1] + 2 + (-(nm.shape[1] + 2)) % 4
GAP = b1 - top + 2                                  # the y's tail just clears the R
cred = np.zeros((n1 - top + 1 + GAP + 1, CW), np.uint8)
cred[0:b1 - top + 1, 4:4 + by.shape[1]][by[top:b1 + 1]] = 3
cred[GAP:GAP + n1 - top + 1, 2:2 + nm.shape[1]][nm[top:n1 + 1]] = 3
sh = np.zeros_like(cred, bool); sh[1:, 1:] = cred[:-1, :-1] == 3
cred[sh & (cred != 3)] = 2                          # red drop shadow, like the title
ys_ = np.nonzero(cred.any(1))[0]; cred = cred[ys_.min():ys_.max() + 1]
CX, CY = 316 - CW, 34
TX, TY = (320 - TW) // 2 // 4 * 4, 6

# ---------------- writers ----------------
def cga_bytes(px):
    mem = bytearray(16384)
    for y in range(200):
        o = (y & 1) * 0x2000 + (y >> 1) * 80
        for i in range(80):
            p = px[y, i * 4:i * 4 + 4]
            mem[o + i] = (p[0] << 6) | (p[1] << 4) | (p[2] << 2) | p[3]
    return bytes(mem)

def bsave(path, data, seg=0xB800):
    with open(path, "wb") as f:
        f.write(bytes([0xFD]) + struct.pack("<HHH", seg, 0, len(data)) + data + b"\x1a")

def sprite(px):
    """GW-BASIC GET/PUT array, SCREEN 1: width in bits, rows, packed rows top to bottom"""
    h, w = px.shape
    data = bytearray(struct.pack("<HH", w * 2, h))
    rb = (w * 2 + 7) // 8
    for y in range(h):
        row = list(px[y]) + [0] * (rb * 4 - w)
        for i in range(rb):
            p = row[i * 4:i * 4 + 4]
            data.append((p[0] << 6) | (p[1] << 4) | (p[2] << 2) | p[3])
    if len(data) % 2: data.append(0)
    return bytes(data)

esp = np.zeros((SH, EW), np.uint8); esp[:EH] = earth
bsave(f"{OUT}/MOONBG.PIC", cga_bytes(bg))
bsave(f"{OUT}/EARTH.SPR", sprite(esp), seg=0)
bsave(f"{OUT}/TITLE.SPR", sprite(tpad), seg=0)
bsave(f"{OUT}/CREDIT.SPR", sprite(cred), seg=0)

lay = (f"EX={EX} EY={EY} HT={HT} EW={EW} EH={EH} SH={SH} RISE={HT - EY} "
       f"EARTH_INTS={len(sprite(esp)) // 2} TITLE_INTS={len(sprite(tpad)) // 2} TX={TX} TY={TY} CREDIT_INTS={len(sprite(cred)) // 2} CX={CX} CY={CY} CW={CW} {stats}")
open(f"{OUT}/layout.txt", "w").write(lay + "\n")
print(lay)

def png(px, path, scale=3):
    Image.fromarray(PAL[px]).resize((px.shape[1] * scale, int(px.shape[0] * scale * 1.2)), Image.NEAREST).save(path)

fin = full.copy()
fin[TY:TY + tpad.shape[0], TX:TX + TW][tpad > 0] = tpad[tpad > 0]
fin[CY:CY + cred.shape[0], CX:CX + CW][cred > 0] = cred[cred > 0]
png(bg, f"{OUT}/preview_start.png")
png(fin, f"{OUT}/preview_title.png")
png(earth, f"{OUT}/preview_earth_zoom.png", 5)
