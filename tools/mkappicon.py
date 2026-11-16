#!/usr/bin/env python3
"""The Tiny Clocktower app icon (2026-11-04; sky made the game's graded night sky 2026-11-16): the three role tokens in a triangle (the Heretic on top, drawn by the game's own roleToken,
without shadow or glow), on the game's night sky shading from near black above to purple below, with stars and a warm light behind them, and 24 straight streamers in the confetti colours bursting out
all round, starting 200-260 out from the middle (staggered) so they do not meet behind the tokens; the burst sits 35 above the
middle, the one going straight up is 15% shorter, the ones behind the lower tokens reach past them, and all are 30% longer. Writes
ios-pocket/App/Assets.xcassets/AppIcon.appiconset/icon_1024.png.
usage: tools/mkappicon.py      (needs the Playwright chrome-headless-shell)"""
import os, re, json, base64, subprocess, io
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
function drift(rx, ry, n, dy, k, fallMax, tk, reachTR = Infinity, kBR = 1) { const placed = [], KNOT = [[-318, 392], [212, 352], [266, 340], [-208, -352, 2], [238, 398], [292, 410], [-236, 366]]; let knot = 0;
  for (let i = 0; i < n; i++) { const a = rnd() * TAU, u = Math.pow(rnd(), .5), f = Math.pow(rnd(), 1.6) * fallMax;
    let dx = Math.cos(a) * rx * u + Math.sin(f * .02 + i) * 18; dx = (i %% 2 ? 1 : -1) * Math.abs(dx);
    let ddy = dy + Math.sin(a) * ry * u + f; if (ddy < 0) ddy *= tk;
    if (dx > 0 && ddy > 0) { dx *= kBR; ddy *= kBR; }      // the bottom right spread out as far as the bottom left
    if (ddy > 0 && Math.abs(dx) < 150 && Math.hypot(dx, ddy) > 485) { const kk = 450 / Math.hypot(dx, ddy); dx *= kk; ddy *= kk; }      // nothing hanging off the very bottom
    if (ddy > 455 && dx > 60 && dx < 160) { ddy -= 36; dx += 62; }      // the purple one lowest down: up a little, and aside so it does not land on the red one above it
    if (dx > 0 && ddy < 0 && Math.hypot(dx, ddy) > reachTR) { const kk = reachTR / Math.hypot(dx, ddy); dx *= kk; ddy *= kk; }      // the top right no further out than the top left reaches
    let c = CONF[(rnd() * CONF.length) | 0]; const w = (3 + rnd() * 4) * k, h = (6 + rnd() * 6) * k, flip = Math.cos(rnd() * TAU) * (1 - .45 * (f / fallMax) * rnd());
    if (dx > 150 && dx < 310 && ddy > 285 && ddy < 370) { const kn = KNOT[knot++ %% KNOT.length]; dx = kn[0]; ddy = kn[1]; if (kn[2] !== undefined) c = CONF[kn[2]]; }      // the knot of pieces just under the Pukka, laid out into the open space below it, two of them under the Sailor and the big one (made blue) up in the bare patch above and left of the Heretic
    if (ddy > 350 && dx > 0 && dx < 220 && c === CONF[0]) {      // the red ones low on the right do not pile on each other: a later one is nudged clear
      const rr = Math.max(w, h) * .5; for (const q of placed) if (q.c === c) { const vx = dx - q.x, vy = ddy - q.y, d = Math.hypot(vx, vy) || 1, need = (rr + q.r) * 1.05; if (d < need) { dx += vx / d * (need - d); ddy += vy / d * (need - d); } }
      placed.push({ x: dx, y: ddy, r: rr, c }); }
    ctx.save(); ctx.translate(C + dx, C + ddy); ctx.rotate(rnd() * TAU); ctx.scale(1, flip); ctx.fillStyle = css(c); ctx.fillRect(-w / 2, -h / 2, w, h); ctx.restore(); } }

// streamers shot straight out from behind the tokens, gravity already bending them down toward their ends (a parabola), a faint ripple in the ribbon
function ribbons(n, wd, L0, L1, grav, flare, alt, sd) { seed = sd;      // thin streamers bursting out: each widens a little as it flies (flare), long and short in turn (alt), fading in from behind the tokens
  const q0 = rnd() * TAU;
  for (let i = 0; i < n; i++) { const q = q0 + i * TAU / n + (rnd() - .5) * TAU / n * .5, L = (L0 + rnd() * (L1 - L0)) * (alt && i %% 2 ? alt : 1), c = CONF[i %% CONF.length], r0 = 200 + (Math.sin(i * 12.9898 + 7) * 43758.5453 %% 1 + 1) %% 1 * 60;      // each starts 200-260 out, staggered, so they do not meet in the middle
    // the one going straight up is 15%% shorter, and the whole burst sits 35 above the middle; one that runs behind the Sailor or the
    // Pukka reaches 15 past that token's edge, so it shows; then every one 30%% longer
    const P = [], Q = []; for (let t = 0; t <= 1.0001; t += .04) { const behind = [[-200, 150 + 35, 175], [200, 150 + 35, 175]].reduce((m, [tx, ty, tr]) => { const along = Math.cos(q) * tx + Math.sin(q) * ty, off = Math.abs(-Math.sin(q) * tx + Math.cos(q) * ty); return off < tr * .9 ? Math.max(m, along + Math.sqrt(tr * tr - off * off) + 15) : m; }, 0), outer = Math.max(Math.max(40, L + 80 - r0) * (-Math.sin(q) > .97 ? .85 : 1) + r0, behind), outer2 = r0 + (outer - r0) * 1.3, r = r0 + t * (outer2 - r0), w = wd * (1 + flare * t) / 2, sx = C + Math.cos(q) * r, sy = C - 35 + Math.sin(q) * r + grav * t * t, nx = -Math.sin(q), ny = Math.cos(q);
      P.push([sx + nx * w, sy + ny * w]); Q.push([sx - nx * w, sy - ny * w]); }
    ctx.fillStyle = css(c); ctx.beginPath(); P.forEach((p, j) => j ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); for (let j = Q.length - 1; j >= 0; j--) ctx.lineTo(Q[j][0], Q[j][1]); ctx.closePath(); ctx.fill(); } }
const SKYN = [[8, 10, 34], [20, 20, 62], [42, 32, 84]];      // the game's night sky: near black above, deep blue, purple at the horizon
const BG = () => { const g = ctx.createLinearGradient(0, 0, 0, N); g.addColorStop(0, css(SKYN[0])); g.addColorStop(.5, css(SKYN[1])); g.addColorStop(1, css(SKYN[2])); ctx.fillStyle = g; ctx.fillRect(0, 0, N, N); stars(55, .6); glow(C, C, N * .32, [255, 210, 160], .3); };      // the night sky as it shades down to the horizon, with stars (MELO 2026-11-16; was one flat purple, then briefly the rose daytime sky)
const TOKS = () => { token(C - 200, C + 150, 175, 'sailor', -.12); token(C + 200, C + 150, 175, 'pukka', .12); token(C, C - 160, 185, 'heretic', 0); };
function ghost(x, y, r, role, tilt = 0) {      // a see-through token (MELO 2026-11-16): two white rings, the outer one dashed, and the role's own picture inside, no disc
  ctx.save(); ctx.strokeStyle = '#fff'; ctx.lineWidth = r * .045; ctx.beginPath(); ctx.arc(x, y, r * .86, 0, TAU); ctx.stroke();
  ctx.setLineDash([r * .13, r * .09]); ctx.lineCap = 'round'; ctx.lineDashOffset = r * .02; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.stroke(); ctx.restore();
  const keep = [circ, ell, glow]; circ = ell = glow = () => {}; ctx.save(); ctx.translate(x, y); ctx.rotate(tilt); roleToken(0, 0, r, role); ctx.restore(); [circ, ell, glow] = keep; }
const GHOSTS = () => { ghost(C, C, 260, 'heretic', 0); };      // the Heretic alone in the middle (MELO 2026-11-16; the Sailor and the Pukka dropped)
make('A2', () => { BG(); GHOSTS(); });      // no streamers (MELO 2026-11-16); was BG(); ribbons(24, 50, 300, 380, 20, 0, 0, 7); TOKS();
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
