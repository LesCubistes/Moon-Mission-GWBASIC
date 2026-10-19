"""Convert the Earthrise photo into CGA (320x200, palette 1/6) assets for MOON.BAS.

Outputs (in build/):
  MOONBG.PIC  - BSAVE image of CGA video RAM: moon + empty starfield (Earth removed)
  EARTH.SPR   - GET/PUT sprite of Earth (with black rows under it so it erases its trail)
  TITLE.SPR   - GET/PUT sprite of the "MOON MISSION" title
  layout.txt  - coordinates MOON.BAS needs
  preview_*.png - what it should look like
"""
import sys, struct, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC = sys.argv[1]
OUT = sys.argv[2]

# palette 1/6 on an RGB monitor: black, cyan, red, light grey
PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], float)

# ---- crop a 4:3 region (CGA 320x200 fills a 4:3 screen) without the poster title ----
im = Image.open(SRC).convert("RGB")
X0, X1 = 8, 1054
Y0 = 330
Y1 = Y0 + int((X1 - X0) * 0.75)
crop = im.crop((X0, Y0, X1, Y1)).resize((320, 200), Image.LANCZOS)
a = np.asarray(crop).astype(float)

# Earth box in screen coords (from photo bbox x446-653, y538-708)
def sx(x): return int(round((x - X0) * 320 / (X1 - X0)))
def sy(y): return int(round((y - Y0) * 200 / (Y1 - Y0)))
ex0, ex1, ey0, ey1 = sx(446) - 2, sx(653) + 3, sy(538) - 1, sy(708) + 1

lum = a.mean(2)
r, g, b = a[..., 0], a[..., 1], a[..., 2]

# horizon: first non-black row per column
horizon = np.array([np.argmax(lum[:, x] > 25) if (lum[:, x] > 25).any() else 199 for x in range(320)])
# Earth columns sit in the sky; recompute horizon there ignoring the Earth itself
left, right = horizon[ex0 - 4], horizon[ex1 + 4]
for x in range(ex0 - 3, ex1 + 4):
    col = lum[ey1 + 8:, x]
    horizon[x] = ey1 + 8 + np.argmax(col > 40)

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5

out = np.zeros((200, 320), np.uint8)
yy, xx = np.mgrid[0:200, 0:320]
thr = BAYER[yy % 4, xx % 4]

# moon: black/grey ordered dither on stretched luminance
moon = yy >= horizon[None, :]
# soften the faint diagonal watermark: light median-ish blur on luminance
from PIL import ImageFilter
lum_s = np.asarray(Image.fromarray(lum.astype(np.uint8)).filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.UnsharpMask(radius=2, percent=50, threshold=4))).astype(float)
t = np.clip((lum_s - 40) / (150 - 40), 0, 1) ** 0.85
out[moon & (t + thr * 0.9 > 0.5)] = 3

# Earth: black / cyan / grey with dithering, inside its box only
earth = np.zeros_like(moon)
earth[ey0:ey1 + 1, ex0:ex1 + 1] = True
earth &= ~moon
e = earth & (lum > 45)
# brightness of clouds vs ocean
bright = np.clip((lum - 40) / 150, 0, 1)
blue_ness = np.clip((b - r) / 90, 0, 1)
for y, x in zip(*np.nonzero(e)):
    v = bright[y, x] + thr[y, x] * 0.6
    if v > 0.70:
        out[y, x] = 3            # cloud / ice
    elif v > 0.05:
        out[y, x] = 1            # ocean / land
    else:
        out[y, x] = 0

# stars, kept out of Earth's rising path and away from the title band
random.seed(1969)
stars = []
while len(stars) < 45:
    x, y = random.randrange(320), random.randrange(0, 115)
    if ex0 - 4 <= x <= ex1 + 4: continue
    if y >= horizon[x] - 3: continue
    stars.append((x, y))
for x, y in stars:
    out[y, x] = 1 if random.random() < 0.3 else 3

full = out.copy()                     # final frame = the photo
bg = out.copy()
bg[earth] = 0                         # Earth removed

# rising geometry
hTop = int(horizon[ex0:ex1 + 1].min())          # flat clip line for Earth
W = ex1 - ex0 + 1
W += (-W) % 4                                    # whole bytes
ex1 = ex0 + W - 1
EH = ey1 - ey0 + 1
MARGIN = 2                                       # black rows under Earth erase the trail
SH = EH + MARGIN

def cga_bytes(px):
    """pack 320x200 2bpp into CGA interleaved video RAM (16384 bytes)"""
    mem = bytearray(16384)
    for y in range(200):
        base = (y & 1) * 0x2000 + (y >> 1) * 80
        row = px[y]
        for i in range(80):
            p = row[i * 4:i * 4 + 4]
            mem[base + i] = (p[0] << 6) | (p[1] << 4) | (p[2] << 2) | p[3]
    return bytes(mem)

def bsave(path, data, seg=0xB800, off=0):
    with open(path, "wb") as f:
        f.write(bytes([0xFD]) + struct.pack("<HHH", seg, off, len(data)) + data + b"\x1a")

def sprite(px):
    """GW-BASIC GET/PUT array for SCREEN 1: width in bits, height, then packed rows"""
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

earth_px = np.zeros((SH, W), np.uint8)
earth_px[:EH] = full[ey0:ey1 + 1, ex0:ex1 + 1]
earth_px[:EH][~earth[ey0:ey1 + 1, ex0:ex1 + 1]] = 0

# ---- title sprite ----
font = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf", 30)
text = "MOON MISSION"
spacing = 3
widths = [font.getbbox(c)[2] - font.getbbox(c)[0] if c != " " else 10 for c in text]
tw = sum(widths) + spacing * (len(text) - 1)
timg = Image.new("L", (tw + 8, 40), 0)
d = ImageDraw.Draw(timg)
x = 2
for c, w_ in zip(text, widths):
    if c != " ":
        d.text((x - font.getbbox(c)[0], 0), c, font=font, fill=255)
    x += w_ + spacing
tarr = np.asarray(timg) > 110
ys_, xs_ = np.nonzero(tarr)
tarr = tarr[ys_.min():ys_.max() + 1, xs_.min():xs_.max() + 1]
# squash vertically for CGA's tall pixels
th = int(round(tarr.shape[0] / 1.2))
tarr = np.asarray(Image.fromarray(tarr.astype(np.uint8) * 255).resize((tarr.shape[1], th), Image.LANCZOS)) > 110
tp = np.zeros((th + 2, tarr.shape[1] + 2), np.uint8)
tp[1:-1, 1:-1][tarr] = 3                          # grey letters
# red drop shadow, then cyan top highlight rows
sh = np.zeros_like(tp, bool); sh[2:, 2:] = tp[:-2, :-2] == 3
body = tp == 3
tp[sh & ~body] = 2
for y in range(tp.shape[0]):
    for x in range(tp.shape[1]):
        if tp[y, x] == 3 and y < tp.shape[0] * 0.38:
            tp[y, x] = 1
TW = tp.shape[1] + (-tp.shape[1]) % 4
tpad = np.zeros((tp.shape[0], TW), np.uint8); tpad[:, :tp.shape[1]] = tp
TX = (320 - TW) // 2 // 4 * 4
TY = 12

bsave(f"{OUT}/MOONBG.PIC", cga_bytes(bg))
bsave(f"{OUT}/EARTH.SPR", sprite(earth_px), seg=0, off=0)
bsave(f"{OUT}/TITLE.SPR", sprite(tpad), seg=0, off=0)

with open(f"{OUT}/layout.txt", "w") as f:
    f.write(f"EX={ex0} EYFINAL={ey0} HTOP={hTop} SH={SH} W={W} RISE={hTop - ey0}\n")
    f.write(f"EARTH.SPR bytes={len(sprite(earth_px))} TITLE.SPR bytes={len(sprite(tpad))} TX={TX} TY={TY} TH={tpad.shape[0]} TW={TW}\n")

def png(px, path, scale=3):
    rgb = PAL[px].astype(np.uint8)
    Image.fromarray(rgb).resize((320 * scale, int(200 * scale * 1.2)), Image.NEAREST).save(path)

fin = full.copy()
fin[TY:TY + tpad.shape[0], TX:TX + TW][tpad > 0] = tpad[tpad > 0]
png(bg, f"{OUT}/preview_start.png")
png(full, f"{OUT}/preview_earth.png")
png(fin, f"{OUT}/preview_title.png")
print(open(f"{OUT}/layout.txt").read())
