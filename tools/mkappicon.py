#!/usr/bin/env python3
"""The Tiny Clocktower app icon (2026-11-04): the three role tokens in a triangle, the Heretic on top, drawn by the game's own roleToken,
in front of confetti drifting down from a burst, on a deep purple with a warm light behind them. Writes ios-pocket/App/Assets.xcassets/AppIcon.appiconset/icon_1024.png.
usage: tools/mkappicon.py      (needs the Playwright chrome-headless-shell)"""
import os, re, json, base64, subprocess, io
from PIL import Image
ROOT = '/root/clocktower-ramen'
HS = '/root/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
need = [r'const TAU = .*?\n', r'const clamp = .*?\n', r'const lerp = .*?\n', r'const mix = .*?\n', r'const css = .*?\n',
        r'function circ\(.*?\n', r'function ell\(.*?\n', r'function glow\(.*?\n}\n', r'function roleToken\(.*?\n}\n']
code = ''.join(re.search(p, src, re.S).group(0) for p in need)
page = """<html><body><script>let ctx;
%s
const N = 1024, C = N / 2;
let seed = 7; const rnd = () => (seed = (seed * 16807) %% 2147483647) / 2147483647;
const CONF = [[226, 64, 78], [255, 196, 64], [86, 156, 236], [150, 104, 210], [250, 246, 238], [96, 196, 160]];
const BUB = [[9, 13, 7.2, [142, 91, 234]], [14.5, 8.5, 5.6, [255, 59, 107]], [8, 6, 3.6, [255, 194, 26]], [16, 16, 4.6, [43, 196, 240]]];
function bg(c0, c1) { const g = ctx.createRadialGradient(C, C * .8, 40, C, C, N * .75); g.addColorStop(0, css(c0)); g.addColorStop(1, css(c1)); ctx.fillStyle = g; ctx.fillRect(0, 0, N, N); }
function stars(n, a) { for (let i = 0; i < n; i++) { ctx.beginPath(); ctx.arc(rnd() * N, rnd() * N, .8 + rnd() * 2.2, 0, TAU); ctx.fillStyle = css([255, 255, 255], a * (.3 + rnd() * .7)); ctx.fill(); } }
function piece(x, y, w, h, r, c, a = 1) { ctx.save(); ctx.translate(x, y); ctx.rotate(r); ctx.fillStyle = css(c, a); ctx.fillRect(-w / 2, -h / 2, w, h); ctx.restore(); }
function confetti(cx, cy, n, r0, r1, sz, a = 1) { for (let i = 0; i < n; i++) { const q = rnd() * TAU, rr = r0 + Math.pow(rnd(), .7) * (r1 - r0); piece(cx + Math.cos(q) * rr, cy + Math.sin(q) * rr, sz * (.5 + rnd() * .5), sz * (1 + rnd()), rnd() * TAU, CONF[(rnd() * CONF.length) | 0], a); } }
function rays(cx, cy, n, len, c, a) { for (let i = 0; i < n; i++) { const q = i * TAU / n + .1; ctx.beginPath(); ctx.moveTo(cx, cy); ctx.arc(cx, cy, len, q - .06, q + .06); ctx.closePath(); ctx.fillStyle = css(c, a); ctx.fill(); } }
function ball(cx, cy, R, glass) {      // the Game Center bubbles, in a glass ball or bare
  if (glass) { const g = ctx.createRadialGradient(cx - R * .35, cy - R * .4, R * .1, cx, cy, R); g.addColorStop(0, 'rgba(255,255,255,.55)'); g.addColorStop(.6, 'rgba(255,255,255,.18)'); g.addColorStop(1, 'rgba(255,255,255,.32)'); ctx.beginPath(); ctx.arc(cx, cy, R, 0, TAU); ctx.fillStyle = g; ctx.fill(); ctx.lineWidth = R * .03; ctx.strokeStyle = 'rgba(255,255,255,.85)'; ctx.stroke(); }
  const k = R * (glass ? 1.45 : 2) / 24; for (const [x, y, r, c] of BUB) { ctx.beginPath(); ctx.arc(cx + (x - 11.2) * k, cy + (y - 11.5) * k, r * k, 0, TAU); ctx.fillStyle = css(c, .93); ctx.fill(); }
  if (glass) { ctx.beginPath(); ctx.ellipse(cx - R * .38, cy - R * .5, R * .22, R * .1, -.6, 0, TAU); ctx.fillStyle = 'rgba(255,255,255,.7)'; ctx.fill(); }
}
function token(x, y, r, role, tilt = 0) {      // the token alone: no shadow under it and no glow round it (roleToken draws both in the game; here only its disc is kept)
  const S = Math.ceil(r * 4), off = document.createElement('canvas'); off.width = off.height = S; const keep = ctx; ctx = off.getContext('2d'); roleToken(S / 2, S / 2, r, role); ctx = keep;
  ctx.save(); ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.clip(); ctx.translate(x, y); ctx.rotate(tilt); ctx.drawImage(off, -S / 2, -S / 2); ctx.restore(); }
const out = {};
function make(name, f) { const c = document.createElement('canvas'); c.width = c.height = N; ctx = c.getContext('2d'); seed = 7; f(); out[name] = c.toDataURL(); }

// burst confetti, pieces bigger near the middle and thinning out, mostly behind the tokens
function burst(cx, cy, n, r0, r1, sz) { for (let i = 0; i < n; i++) { const q = rnd() * TAU, u = Math.pow(rnd(), .8), rr = r0 + u * (r1 - r0); piece(cx + Math.cos(q) * rr, cy + Math.sin(q) * rr * .92, sz * (1.1 - u * .5) * (.55 + rnd() * .45), sz * (1.1 - u * .5) * (1.1 + rnd() * .9), q + (rnd() - .5) * 1.2, CONF[(rnd() * CONF.length) | 0], .55 + .45 * (1 - u)); } }
function sky(top, bot) { const g = ctx.createRadialGradient(C, C * .95, 30, C, C, N * .78); g.addColorStop(0, css(top)); g.addColorStop(1, css(bot)); ctx.fillStyle = g; ctx.fillRect(0, 0, N, N); }
// A2: a triangle — the Heretic on top, the other two below, the burst from their middle
// the confetti drifting down from a burst behind the tokens, drawn as the game draws it (any angle, turned over by cos): each piece has
// fallen its own way below where the pop left it, so the cloud thins downward and the lower ones flutter (turned over more).
// Every other piece goes to the other side, so there is as much on the left as on the right; the top is stretched (tk) to reach as far as the sides.
function drift(rx, ry, n, dy, k, fallMax, tk, reachTR = Infinity, kBR = 1) { const placed = [], KNOT = [[-318, 392], [212, 352], [266, 340], [-208, -352], [238, 398], [292, 410], [-236, 366]]; let knot = 0;
  for (let i = 0; i < n; i++) { const a = rnd() * TAU, u = Math.pow(rnd(), .5), f = Math.pow(rnd(), 1.6) * fallMax;
    let dx = Math.cos(a) * rx * u + Math.sin(f * .02 + i) * 18; dx = (i %% 2 ? 1 : -1) * Math.abs(dx);
    let ddy = dy + Math.sin(a) * ry * u + f; if (ddy < 0) ddy *= tk;
    if (dx > 0 && ddy > 0) { dx *= kBR; ddy *= kBR; }      // the bottom right spread out as far as the bottom left
    if (ddy > 0 && Math.abs(dx) < 150 && Math.hypot(dx, ddy) > 485) { const kk = 450 / Math.hypot(dx, ddy); dx *= kk; ddy *= kk; }      // nothing hanging off the very bottom
    if (ddy > 455 && dx > 60 && dx < 160) { ddy -= 36; dx += 62; }      // the purple one lowest down: up a little, and aside so it does not land on the red one above it
    if (dx > 0 && ddy < 0 && Math.hypot(dx, ddy) > reachTR) { const kk = reachTR / Math.hypot(dx, ddy); dx *= kk; ddy *= kk; }      // the top right no further out than the top left reaches
    const c = CONF[(rnd() * CONF.length) | 0], w = (3 + rnd() * 4) * k, h = (6 + rnd() * 6) * k, flip = Math.cos(rnd() * TAU) * (1 - .45 * (f / fallMax) * rnd());
    if (dx > 150 && dx < 310 && ddy > 285 && ddy < 370) { [dx, ddy] = KNOT[knot++ %% KNOT.length]; }      // the knot of pieces just under the Pukka, laid out into the open space below it, two of them under the Sailor and the big green one up in the bare patch above and left of the Heretic
    if (ddy > 350 && dx > 0 && dx < 220 && c === CONF[0]) {      // the red ones low on the right do not pile on each other: a later one is nudged clear
      const rr = Math.max(w, h) * .5; for (const q of placed) if (q.c === c) { const vx = dx - q.x, vy = ddy - q.y, d = Math.hypot(vx, vy) || 1, need = (rr + q.r) * 1.05; if (d < need) { dx += vx / d * (need - d); ddy += vy / d * (need - d); } }
      placed.push({ x: dx, y: ddy, r: rr, c }); }
    ctx.save(); ctx.translate(C + dx, C + ddy); ctx.rotate(rnd() * TAU); ctx.scale(1, flip); ctx.fillStyle = css(c); ctx.fillRect(-w / 2, -h / 2, w, h); ctx.restore(); } }
make('A2', () => { seed = 2026;      // the draw MELO picked (2026-11-04, "c1", then "h7")
  ctx.fillStyle = css([40, 22, 80]); ctx.fillRect(0, 0, N, N); stars(55, .6); glow(C, C, N * .32, [255, 210, 160], .3);      // a deep, even purple, warm light behind the tokens only
  drift(440, 330, 260, -60, 5.6, 230, 1.3, 465, 1.06);      // "h7": the big pieces drifting a little further down
  { const keep = seed; seed = 61; for (const [x, y] of [[722, 178], [770, 232], [716, 262], [758, 318], [705, 335], [792, 162], [806, 262], [884, 318], [900, 392]]) {      // a few more where the right side was bare: between the top-right corner and the lower-right token, and out to the right of the Heretic (as full as its left)
      const c = CONF[(rnd() * CONF.length) | 0], w = (3 + rnd() * 4) * 5.6, h = (6 + rnd() * 6) * 5.6;
      ctx.save(); ctx.translate(x + (rnd() - .5) * 20, y + (rnd() - .5) * 20); ctx.rotate(rnd() * TAU); ctx.scale(1, Math.cos(rnd() * TAU)); ctx.fillStyle = css(c); ctx.fillRect(-w / 2, -h / 2, w, h); ctx.restore(); }
    seed = keep; }
  token(C - 200, C + 150, 175, 'sailor', -.12); token(C + 200, C + 150, 175, 'pukka', .12); token(C, C - 160, 185, 'heretic', 0); });
document.body.textContent = '@@' + JSON.stringify(out) + '@@';
</script></body></html>""" % code
open('/tmp/mkappicon.html', 'w', encoding='utf-8').write(page)
r = subprocess.run([HS, '--no-sandbox', '--disable-gpu', '--virtual-time-budget=4000', '--dump-dom', 'file:///tmp/mkappicon.html'], capture_output=True, text=True, timeout=120)
m = re.search(r'@@(\{.*?\})@@', r.stdout, re.S)
if not m: raise SystemExit(r.stderr[-2000:])
url = json.loads(m.group(1))['A2']
out = os.path.join(ROOT, 'ios-pocket', 'App', 'Assets.xcassets', 'AppIcon.appiconset', 'icon_1024.png')
Image.open(io.BytesIO(base64.b64decode(url.split(',')[1]))).convert('RGB').save(out, optimize=True)      # no alpha: the App Store refuses an icon with one
print('icon:', out)
