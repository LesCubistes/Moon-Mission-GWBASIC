"""Pick stars that twinkle: reads a BSAVE'd CGA screen and prints GW-BASIC DATA lines
(count, then x, y, colour per star) for stars inside the allowed sky boxes.
usage: mkstars.py PIC LINE N x0,y0,x1,y1 [x0,y0,x1,y1 ...]"""
import sys, random
import numpy as np
pic, line, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
boxes = [tuple(map(int, b.split(","))) for b in sys.argv[4:]]
mem = open(pic, "rb").read()[7:7 + 16384]
px = np.zeros((200, 320), np.uint8)
for y in range(200):
    o = (y & 1) * 0x2000 + (y >> 1) * 80
    for x in range(320):
        px[y, x] = (mem[o + x // 4] >> (6 - 2 * (x % 4))) & 3
stars = []
for y in range(1, 199):
    for x in range(1, 319):
        if px[y, x] and not any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in [()] if False):
            if any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in boxes):
                if px[y - 1:y + 2, x - 1:x + 2].sum() == px[y, x]:      # a lone pixel in black sky
                    stars.append((x, y, int(px[y, x])))
random.seed(4); random.shuffle(stars); stars = sorted(stars[:n])
vals = [len(stars)] + [v for s in stars for v in s]
out, cur = [], []
for v in vals:
    cur.append(str(v))
    if len(cur) == 24: out.append(cur); cur = []
if cur: out.append(cur)
for i, c in enumerate(out): print(f"{line + i} DATA {','.join(c)}")
