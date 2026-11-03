#!/usr/bin/env python3
"""Game Center achievement images for Tiny Clocktower: only four designs, 1024x1024 PNGs into assets/achievements/<id>.png.
  the three role achievements show that role's token, drawn by the game's own roleToken (index.html), on a transparent ground:
    exec_survive (Undying) the anchor token   self_reverse (Turn the Tables) the cross token   trick_pukka (Double Dose) the arrow token
  every other achievement is the app icon (ios-pocket/.../icon_1024.png)
usage: tools/mkbadges.py      (needs the Playwright chrome-headless-shell)"""
import os, re, json, base64, shutil, subprocess, tempfile
from PIL import Image, ImageDraw, ImageChops
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'achievements')
ICON = os.path.join(ROOT, 'ios-pocket', 'App', 'Assets.xcassets', 'AppIcon.appiconset', 'icon_1024.png')
HS = '/root/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'
ROLES = {'exec_survive': 'sailor', 'self_reverse': 'heretic', 'trick_pukka': 'pukka'}
OTHERS = ['first_win', 'streak_3', 'streak_5', 'day_3', 'day_5', 'day_7'] + [f'wins_{n}' for n in (5, 10, 25, 50, 100, 200, 300, 500, 1000)]
N, R = 1024, 500      # the token fills the round medallion Game Center shows

# ---- the tokens, from the game's own drawing code
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
need = [r'const TAU = .*?\n', r'const clamp = .*?\n', r'const lerp = .*?\n', r'const mix = .*?\n', r'const css = .*?\n',
        r'function circ\(.*?\n', r'function ell\(.*?\n', r'function glow\(.*?\n}\n', r'function roleToken\(.*?\n}\n']
code = ''.join(re.search(p, src, re.S).group(0) for p in need)
page = f"""<html><body><script>let ctx;
{code}
const out = {{}};
for (const role of {json.dumps(sorted(set(ROLES.values())))}) {{ const c = document.createElement('canvas'); c.width = c.height = {N}; ctx = c.getContext('2d'); roleToken({N / 2}, {N / 2}, {R}, role); out[role] = c.toDataURL(); }}
document.body.textContent = '@@' + JSON.stringify(out) + '@@';
</script></body></html>"""
tmp = tempfile.mkdtemp()
open(os.path.join(tmp, 't.html'), 'w', encoding='utf-8').write(page)
r = subprocess.run([HS, '--no-sandbox', '--disable-gpu', '--dump-dom', 'file://' + os.path.join(tmp, 't.html')], capture_output=True, text=True, timeout=120)
m = re.search(r'@@(\{.*?\})@@', r.stdout, re.S)
if not m: raise SystemExit('no tokens came back: ' + '\n'.join(l for l in r.stderr.split('\n') if 'CONSOLE' in l))
shutil.rmtree(tmp)
os.makedirs(OUT, exist_ok=True)
mask = Image.new('L', (N, N), 0); ImageDraw.Draw(mask).ellipse((N / 2 - R, N / 2 - R, N / 2 + R, N / 2 + R), fill=255)      # no glow, no shadow: just the token
tokens = {}
for role, url in json.loads(m.group(1)).items():
    im = Image.open(__import__('io').BytesIO(base64.b64decode(url.split(',')[1]))).convert('RGBA')
    im.putalpha(ImageChops.multiply(im.getchannel('A'), mask)); tokens[role] = im
for a, role in ROLES.items(): tokens[role].save(os.path.join(OUT, a + '.png'), optimize=True); print(a, role)
icon = Image.open(ICON).convert('RGB'); assert icon.size == (N, N)
for a in OTHERS: icon.save(os.path.join(OUT, a + '.png'), optimize=True)
print('app icon:', len(OTHERS))
