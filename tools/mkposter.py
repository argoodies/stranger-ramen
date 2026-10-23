#!/usr/bin/env python3
"""Render the /3b promotional images and the three-token icon from the real game, into assets/.

  assets/posters/night_9x16.png   1080x1920  the table at night, each player's role token over their head, no text
  assets/posters/night_2x3.png    1200x1800  the same at 2:3, the moon in the sky
  assets/posters/lobby_2x3.png    1200x1800  the opening screen (daytime lobby: Storyteller, you, 小染书), the sun in the sky
  assets/role-icons/trio.png      1024x1024  the three tokens overlapping on the night sky, no coloured glow

Each image is the game's own canvas, exported from inside the page once the scene is set (deploy/3b.html is
built first with tools/mk3b.py). The geese are left out so nothing crosses the sky.
usage: tools/mkposter.py   (needs the Playwright headless Chromium below)
"""
import base64, io, os, re, subprocess, sys, tempfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HS = '/root/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'
TMP = '/dev/shm' if os.path.isdir('/dev/shm') else tempfile.gettempdir()

EXPORT = "const ta = document.createElement('textarea'); ta.id = 'png'; ta.textContent = $('c').toDataURL('image/png'); document.body.appendChild(ta); document.title = 'ok';"
PRE = """window.requestAnimationFrame = () => 0; drawGeese3 = () => {};
const tk = sec => new Promise(res => { const end = performance.now() + sec * 1000; const f = () => { frame(performance.now()); if (performance.now() < end) setTimeout(f, 16); else res(); }; f(); });
const tap = (x, y) => $('c').dispatchEvent(new PointerEvent('pointerdown', { clientX: x, clientY: y, bubbles: true, pointerId: 1 }));"""
NIGHT = PRE + """
setTimeout(async () => { await tk(3.7); const v = new View(W / 2, H * .6, Math.min(W / 11.2, (H - 250) / 8.6)), p = v.P(0, 0, .3); tap(p[0], p[1] - v.s * 1.25 * .8); await tk(4);
  BG.roles = ['sailor', 'heretic', 'pukka']; BG.alive = [true, true, true]; BG.drunk = BG.poisoned = BG.deadPoison = -1; BG.wait = null; BG.bubble = null; BG.votes = null;
  BG.isNight = true; BG.reveal = true; BG.revealT = 9; await tk(3); BG.bubble = null; BG.wait = null; frame(performance.now()); """ + EXPORT + """ }, 0);"""
LOBBY = PRE + """
setTimeout(async () => { await tk(4.2); frame(performance.now()); """ + EXPORT + """ }, 0);"""
TRIO = """window.requestAnimationFrame = () => 0;
setTimeout(() => { const N = 1024, c2 = document.createElement('canvas'); c2.width = c2.height = N; const real = ctx, keep = [W, H]; ctx = c2.getContext('2d'); W = H = N;
  drawSky(SKYN[0], SKYN[1], SKYN[2], 3.7, 1);
  const r = N * .17, cy = N * .5, d = r * .8 / N, g0 = glow; glow = () => {};
  try { [['sailor', .5 - d], ['heretic', .5], ['pukka', .5 + d]].forEach(([id, fx]) => roleToken(N * fx, cy, r, id)); } finally { glow = g0; }
  ctx = real; [W, H] = keep; const ta = document.createElement('textarea'); ta.id = 'png'; ta.textContent = c2.toDataURL('image/png'); document.body.appendChild(ta); document.title = 'ok'; }, 500);"""

def render(script, size, dsf, out, resize=None):
    src = open(os.path.join(ROOT, 'deploy', '3b.html'), encoding='utf-8').read()
    i = src.rfind('</body>'); page = os.path.join(TMP, 'mkposter.html')
    open(page, 'w', encoding='utf-8').write(src[:i] + '<script>\n' + script + '\n</script>\n' + src[i:])
    dom = subprocess.run([HS, '--no-sandbox', '--disable-gpu', f'--window-size={size}', f'--force-device-scale-factor={dsf}', '--virtual-time-budget=40000',
                          '--dump-dom', f'file://{page}?lang=hans'], capture_output=True, text=True, timeout=300).stdout
    m = re.search(r'<textarea id="png">data:image/png;base64,([^<]+)</textarea>', dom)
    if not m: sys.exit(f'{out}: no image came back')
    im = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGB')
    if resize: im = im.resize(resize, Image.LANCZOS)
    os.makedirs(os.path.dirname(out), exist_ok=True); im.save(out, optimize=True); print(out, im.size)

subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'mk3b.py')], check=True)
P = lambda *a: os.path.join(ROOT, 'assets', *a)
render(NIGHT, '432,768', 2, P('posters', 'night_9x16.png'), (1080, 1920))
render(NIGHT, '600,900', 2, P('posters', 'night_2x3.png'))
render(LOBBY, '600,900', 2, P('posters', 'lobby_2x3.png'))
render(TRIO, '390,844', 1, P('role-icons', 'trio.png'))
