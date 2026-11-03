#!/usr/bin/env python3
"""Game Center achievement images for Tiny Clocktower, 1024x1024 PNGs into assets/achievements/<id>.png, all in the role tokens' style.
  the three role achievements show that role's token, drawn by the game's own roleToken (index.html), on a transparent ground:
    exec_survive (Undying) the anchor token   self_reverse (Turn the Tables) the cross token   trick_pukka (Double Dose) the arrow token
  every other achievement is a token of the same disc with a number (tools/badgeart.html), in the game's font:
    wins and first win: a gold laurel wreath   streaks: a red flame, hollow, the number inside   days: the sun's yellow
usage: tools/mkbadges.py      (needs the Playwright chrome-headless-shell)"""
import os, re, json, base64, shutil, subprocess, tempfile
from PIL import Image, ImageDraw, ImageChops
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'achievements')
ART = os.path.join(ROOT, 'tools', 'badgeart.html')
HS = '/root/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'
ROLES = {'exec_survive': 'sailor', 'self_reverse': 'heretic', 'trick_pukka': 'pukka'}
OTHERS = [('first_win', 'wins', '1')] + [(f'wins_{n}', 'wins', str(n)) for n in (5, 10, 25, 50, 100, 200, 300, 500, 1000)] + [(f'streak_{n}', 'streak', str(n)) for n in (3, 5)] + [(f'day_{n}', 'day', str(n)) for n in (3, 5, 7)]
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
import urllib.parse
r = subprocess.run([HS, '--no-sandbox', '--disable-gpu', '--virtual-time-budget=5000', '--dump-dom', 'file://' + ART + '#' + urllib.parse.quote(json.dumps(OTHERS))], capture_output=True, text=True, timeout=120)
m = re.search(r'@@(\{.*?\})@@', r.stdout, re.S)
if not m: raise SystemExit('no number badges came back')
for a, url in json.loads(m.group(1)).items():
    Image.open(__import__('io').BytesIO(base64.b64decode(url.split(',')[1]))).convert('RGBA').save(os.path.join(OUT, a + '.png'), optimize=True)
print('number badges:', len(OTHERS))
