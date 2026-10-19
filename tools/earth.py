"""Render a sunlit Earth centered on the Americas in CGA palette 1/6, in several land styles.

render(style) -> (px, disc): px is EH x EW of palette indices 0-3, disc is the lit-disc mask.
Palette 1/6: 0 black, 1 cyan, 2 red, 3 grey.
"""
import numpy as np
from PIL import Image
from global_land_mask import globe

EW, EH = 96, 80                 # 96 px wide, 80 rows (CGA pixels are 1.2x tall)
LAT0, LON0 = 12.0, -58.0         # view center: both Americas
SUN = np.array([-0.78, 0.30, 0.55]); SUN /= np.linalg.norm(SUN)   # sun from the left
SS = 4                          # supersampling per pixel side
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

STYLES = {
    1: "Solid red land",
    2: "Red-black dither (dark earth)",
    3: "Red-grey dither (tan desert)",
    4: "Biomes: teal forest, tan desert, white ice",
    5: "Dark continents on cyan ocean",
    6: "Grey land, cyan ocean",
}

def _noise(w, h, scale, seed):
    r = np.random.default_rng(seed)
    g = r.random((h // scale + 3, w // scale + 3))
    img = Image.fromarray((g * 255).astype(np.uint8)).resize(((w // scale + 3) * scale, (h // scale + 3) * scale), Image.BICUBIC)
    return np.asarray(img).astype(float)[:h, :w] / 255.0

# cloud field on a lat/lon grid (2 cells per degree), domain-warped for swirls
_CW, _CH = 720, 360
_w1 = _noise(_CW, _CH, 60, 31) - 0.5
_w2 = _noise(_CW, _CH, 60, 32) - 0.5
_base = 0.5 * _noise(_CW, _CH, 30, 21) + 0.3 * _noise(_CW, _CH, 12, 22) + 0.2 * _noise(_CW, _CH, 5, 23)
_jj, _ii = np.meshgrid(np.arange(_CW), np.arange(_CH))
_si = np.clip((_ii + 70 * _w1).astype(int), 0, _CH - 1)
_sj = ((_jj + 140 * _w2).astype(int)) % _CW
_c = _base[_si, _sj]
_lat_grid = np.linspace(90, -90, _CH)[:, None]
_band = (0.30 * np.exp(-((_lat_grid - 6) / 6) ** 2)               # ITCZ
         + 0.35 * np.exp(-((np.abs(_lat_grid) - 50) / 14) ** 2)    # mid-latitude storms
         - 0.20 * np.exp(-((np.abs(_lat_grid) - 24) / 8) ** 2))    # clear subtropics
CLOUD = np.clip((_c + _band - 0.58) * 3.5, 0, 1)

def _cloud_at(lat, lon):
    i = np.clip(((90 - lat) * 2).astype(int), 0, _CH - 1)
    j = (((lon + 180) % 360) * 2).astype(int) % _CW
    return CLOUD[i, j]

def _desert(lat, lon):
    sw_us = (lat > 24) & (lat < 38) & (lon > -118) & (lon < -103)
    mex = (lat > 20) & (lat < 32) & (lon > -114) & (lon < -100)
    atacama = (lat > -30) & (lat < -15) & (lon > -72) & (lon < -67)
    patag = (lat > -52) & (lat < -38) & (lon > -71) & (lon < -63)
    sahara = (lat > 14) & (lat < 33) & (lon > -18) & (lon < 35)
    brazil_ne = (lat > -12) & (lat < -3) & (lon > -44) & (lon < -36)
    return sw_us | mex | atacama | patag | sahara | brazil_ne

def _ice(lat, lon):
    return (lat > 60) & (lon > -75) & (lon < -10) | (lat < -62)

def _sample():
    """supersampled geometry: returns per-pixel fractions/averages"""
    ys = (np.arange(EH * SS) + 0.5) / (EH * SS) * 2 - 1      # -1..1 top->bottom
    xs = (np.arange(EW * SS) + 0.5) / (EW * SS) * 2 - 1
    X, Y = np.meshgrid(xs, -ys)
    R2 = X ** 2 + Y ** 2
    on = R2 <= 1
    Z = np.sqrt(np.clip(1 - R2, 0, 1))
    # rotate view vector back to globe coords
    la0, lo0 = np.radians(LAT0), np.radians(LON0)
    # orthographic inverse
    rho = np.sqrt(R2); c = np.arcsin(np.clip(rho, 0, 1))
    with np.errstate(invalid="ignore", divide="ignore"):
        lat = np.arcsin(np.cos(c) * np.sin(la0) + np.where(rho > 0, Y * np.sin(c) * np.cos(la0) / rho, 0))
        lon = lo0 + np.arctan2(X * np.sin(c), rho * np.cos(c) * np.cos(la0) - Y * np.sin(c) * np.sin(la0))
    lat = np.degrees(lat); lon = (np.degrees(lon) + 180) % 360 - 180
    light = np.clip(X * SUN[0] + Y * SUN[1] + Z * SUN[2], 0, 1) * on
    land = np.zeros_like(on)
    land[on] = globe.is_land(np.clip(lat[on], -89.9, 89.9), np.clip(lon[on], -179.9, 179.9))
    cloud = np.where(on, _cloud_at(np.nan_to_num(lat), np.nan_to_num(lon)), 0)
    des = on & land & _desert(lat, lon)
    ice = on & land & _ice(lat, lon)
    def avg(a):
        return a.reshape(EH, SS, EW, SS).mean((1, 3))
    return dict(on=avg(on.astype(float)), light=avg(light), land=avg(land.astype(float) * on),
                cloud=avg(cloud), desert=avg(des.astype(float)), ice=avg(ice.astype(float)))

_G = None
def render(style):
    global _G
    if _G is None: _G = _sample()
    g = _G
    yy, xx = np.mgrid[0:EH, 0:EW]
    th = BAYER[yy % 4, xx % 4]
    on, L = g["on"] > 0.5, g["light"]
    disc = on & (L > 0.10)                     # night side is invisible against black sky
    land = g["land"] > 0.5
    lit = np.clip((L - 0.08) * 3.0, 0, 1)      # perceived brightness, sharp terminator
    px = np.zeros((EH, EW), np.uint8)

    # ocean: cyan, fading to black at the terminator
    ocean_c = 1
    px[disc & ~land & (lit > th * 0.9)] = ocean_c

    des = g["desert"] > 0.4
    ice = g["ice"] > 0.4
    checker = ((xx + yy) % 2) == 0
    if style == 1:
        px[disc & land & (lit > th * 0.7)] = 2
    elif style == 2:
        px[disc & land & checker & (lit > th * 0.5)] = 2
    elif style == 3:
        m = disc & land & (lit > th * 0.6)
        px[m & checker] = 2; px[m & ~checker] = 3
        px[disc & land & (lit < 0.45) & ~checker] = 0
    elif style == 4:
        forest = disc & land & ~des & ~ice
        px[forest] = 0
        px[forest & (th < 0.38) & (lit > 0.3)] = 1            # dark teal: cyan over black
        m = disc & des & (lit > th * 0.5)
        px[m & checker] = 2; px[m & ~checker] = 3
        px[disc & ice & (lit > th * 0.4)] = 3
    elif style == 5:
        px[disc & land] = 0
        px[disc & land & (th < 0.12) & (lit > 0.4)] = 1       # faint texture so it isn't a hole
    elif style == 6:
        m = disc & land & (lit > th * 0.9)
        px[m & (th < 0.6 + 0.3 * lit - 0.3)] = 3
        px[disc & land & ~m] = 0

    # clouds over everything, thinner ones dithered
    cl = g["cloud"] * lit
    px[disc & (cl > 0.25 + th * 0.55)] = 3
    # bright sunlit limb
    edge = on & (g["on"] < 1) & (L > 0.25)
    px[edge] = 3
    px[~disc] = 0
    return px, disc

if __name__ == "__main__":
    import sys
    from PIL import ImageDraw, ImageFont
    PAL = np.array([(0, 0, 0), (0, 170, 170), (170, 0, 0), (170, 170, 170)], np.uint8)
    out = sys.argv[1]
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    S = 4
    tiles = []
    for s, name in STYLES.items():
        px, _ = render(s)
        img = Image.fromarray(PAL[px]).resize((EW * S, int(EH * S * 1.2)), Image.NEAREST)
        t = Image.new("RGB", (img.width + 40, img.height + 70), (24, 24, 28))
        t.paste(img, (20, 55))
        ImageDraw.Draw(t).text((20, 15), f"{s}. {name}", font=f, fill=(230, 230, 230))
        tiles.append(t)
    W_, H_ = tiles[0].size
    sheet = Image.new("RGB", (W_ * 3, H_ * 2), (24, 24, 28))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 3) * W_, (i // 3) * H_))
    sheet.save(out)
    print(sheet.size)
