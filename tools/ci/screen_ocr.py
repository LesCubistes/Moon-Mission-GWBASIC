"""Make BIOS text legible without assuming black backgrounds or white text."""
from PIL import Image, ImageChops, ImageOps


def monochrome(image):
    rgb = image.convert('RGB')
    colors = rgb.getcolors(maxcolors=256)
    if colors is None:
        colors = rgb.quantize(colors=16).convert('RGB').getcolors(maxcolors=256)
    background = max(colors, key=lambda item: item[0])[1]
    difference = ImageChops.difference(rgb, Image.new('RGB', rgb.size, background))
    channels = difference.split()
    contrast = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    mask = contrast.point(lambda value: 0 if value > 32 else 255)
    mask = mask.resize((mask.width * 3, mask.height * 3), Image.Resampling.NEAREST)
    return ImageOps.expand(mask, border=40, fill=255)
