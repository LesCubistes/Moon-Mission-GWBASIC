"""Dust kicked up by the descent engine near the ground.

Writes OUTDIR/DU1.SPR .. DU6.SPR: 72x12 sprites drawn with PUT ... XOR centred under the engine
(sizes small/medium/large, two shimmer variants each). XOR twice restores the screen exactly.
Grains fan out sideways from a clear gap under the bell, lower and sparser further out.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mklevel_io import bsave, sprite

OUT = sys.argv[1]
W, H = 72, 12
C = W // 2
rng = np.random.default_rng(9)
n = 1
for reach, count in ((20, 40), (28, 70), (35, 110)):          # small, medium, large plume
    for variant in range(2):
        s = np.zeros((H, W), np.uint8)
        for _ in range(count):
            side = rng.choice((-1, 1))
            d = rng.uniform(5, reach)                          # distance out from the engine
            top = 1 + (H - 2) * (d / reach) ** 0.7             # plume is taller near the middle
            y = int(rng.uniform(top, H))
            x = int(C + side * d)
            if 0 <= x < W:
                s[y, x] = 3
                if rng.random() < .35 and 0 <= x + side < W: s[y, x + side] = 3   # clumps, streaking outward
        s[H - 1, C - reach:C - 4] = 3 * (np.arange(reach - 4) % 3 != 0)          # a sheet of grit on the surface
        s[H - 1, C + 5:C + reach + 1] = 3 * (np.arange(reach - 4) % 3 != 0)
        s[H - 2, C - reach // 2:C - 4:2] = 3; s[H - 2, C + 5:C + reach // 2:2] = 3
        bsave(f"{OUT}/DU{n}.SPR", sprite(s)); n += 1
print("dust sprite ints:", len(sprite(s)) // 2)
