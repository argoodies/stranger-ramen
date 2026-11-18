# Compose the app icon: the game's night sky (sky.mjs), the warm glow by the door (glow.png, added to the sky), and the ramen shop (house.mjs) over it.
# Usage: node house.mjs; node sky.mjs; python3 compose.py  -> /dev/shm/sicon3/shop_icon.png (1024)
from PIL import Image
import numpy as np, os
D = '/dev/shm/sicon3'; HERE = os.path.dirname(os.path.abspath(__file__))
k = 547 / 1039; S = round(3000 * k); ox = round(239 - 980 * k); oy = round(238 - 1011 * k)      # the house's 3000px render scaled so its roof spans x 239..786, apex at y 238, as in the 0.1.0 icon
sky = np.array(Image.open(f'{D}/gsky_nomoon.png').convert('RGB')).astype(float)
glow = np.array(Image.open(f'{HERE}/glow.png').convert('RGB')).astype(float)
bg = Image.fromarray(np.clip(sky + glow, 0, 255).astype(np.uint8)).convert('RGBA')
house = Image.open(f'{D}/house.png').resize((S, S), Image.LANCZOS).crop((-ox, -oy, -ox + 1024, -oy + 1024))
bg.alpha_composite(house); bg.convert('RGB').save(f'{D}/shop_icon.png')
