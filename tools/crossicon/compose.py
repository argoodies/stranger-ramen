# Starcross Town icon: the game's night sky (gsky_nomoon.png, drawSky fitted to a square), the blue crystal Guardian Cross (b_tilt.png,
# the game's drawGuard) with its centre of mass on the icon's centre, and a twinkling four-point star just off its upper-right arm.
from PIL import Image, ImageDraw
import numpy as np, math, os, sys; os.chdir('/dev/shm/sicon3')
S = float(sys.argv[1]) if len(sys.argv) > 1 else .8; OUTF = sys.argv[2] if len(sys.argv) > 2 else 'icon_final.png'
def sparkle(im, x, y, r, col=(240, 250, 255)):
    g = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for k in range(30, 0, -1):
        rr = r * 1.1 * k / 30; d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(190, 225, 255, int(120 * (1 - k / 30) ** 2)))
    s = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(s); w = r * .16
    for ang, L in ((0, r), (math.pi / 2, r), (math.pi / 4, r * .45), (-math.pi / 4, r * .45)):
        c, sn = math.cos(ang), math.sin(ang); ww = w if L == r else w * .7
        d.polygon([(x + c * L, y + sn * L), (x - sn * ww, y + c * ww), (x - c * L, y - sn * L), (x + sn * ww, y - c * ww)], fill=col + (255,))
    d.ellipse([x - w * 1.3, y - w * 1.3, x + w * 1.3, y + w * 1.3], fill=(255, 255, 255, 255))
    return Image.alpha_composite(Image.alpha_composite(im, g), s)
src = Image.open('b_tilt.png'); w = int(1024 * S); src = src.resize((w, w), Image.LANCZOS)
a = np.asarray(src.getchannel('A')).astype(float); ys, xs = np.indices(a.shape); m = a.sum(); cx, cy = (xs * a).sum() / m, (ys * a).sum() / m
im = Image.open('gsky_nomoon.png').convert('RGBA'); im.alpha_composite(src, (int(round(512 - cx)), int(round(512 - cy))))
k = S / .8; im = sparkle(im, 512 + 288 * k, 512 - 192 * k, 66)
im.convert('RGB').save(OUTF); print(OUTF, S)
