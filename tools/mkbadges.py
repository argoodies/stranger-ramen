#!/usr/bin/env python3
"""Game Center achievement images for Tiny Clocktower, drawn with the /3b game's own canvas code (deploy/3b.html).
One 1024x1024 PNG per achievement into assets/achievements/<id>.png (Game Center shows them in a circle, so each fills a round medallion):
  wins:    a gold star with the count          streaks: a red flame with the count
  days:    the sun in the rosy sky with the day   roles:   that role's token on the island's green
  tricks:  the role's token under the night sky   first:   the purple book and its sparkle
usage: tools/mkbadges.py [id ...]"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'tools', 'mkposter.py'), encoding='utf-8').read().split("subprocess.run([sys.executable")[0].replace("os.path.abspath(__file__)", repr(os.path.join(ROOT, 'tools', 'x')))
exec(src)
book = open(os.path.join(ROOT, 'tools', 'mk3b.py'), encoding='utf-8').read()
i = book.index("      let ox = 0, oy = 0; const W = s * .46"); j = book.index("    } else {", i)
import re
BOOK = re.sub(r"\s//[^\n]*", "", book[i:j]).replace("\n", " ")
JS = """window.requestAnimationFrame = () => 0;
setTimeout(() => { const N = 1024, c2 = document.createElement('canvas'); c2.width = c2.height = N; const real = ctx, keep = [W, H]; ctx = c2.getContext('2d'); W = H = N; starCache = null;
  const KIND = '__K__', NUM = '__N__', ROLE = '__R__', C = N / 2, cream = [244, 232, 208], g0 = glow, e0 = ell;
  const disc = (r, c) => circ(C, C, r, c), num = (t, y, size, col) => { ctx.font = `700 ${size}px ${THINF}`; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; const m = ctx.measureText(t), ty = y + (m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) / 2; ctx.fillStyle = css(col); ctx.fillText(t, C, ty); };
  const tok = (r) => { glow = () => {}; ell = (x, y, a, b, c, al) => { if (al !== .4) e0(x, y, a, b, c, al); }; roleToken(C, C, r, ROLE); glow = g0; ell = e0; };
  if (KIND === 'wins') { disc(N * .5, [214, 168, 92]); disc(N * .45, [64, 50, 104]); const pts = []; for (let k = 0; k < 10; k++) { const a = -Math.PI / 2 + k * Math.PI / 5, r = k % 2 ? N * .17 : N * .38; pts.push([C + Math.cos(a) * r, C + N * .02 + Math.sin(a) * r]); } poly(pts, [236, 196, 132]); num(NUM, C + N * .05, NUM.length > 2 ? N * .16 : N * .2, [64, 50, 104]); }
  else if (KIND === 'streak') { disc(N * .5, [168, 44, 66]); disc(N * .45, [44, 34, 74]); const f = (s, c) => { ctx.beginPath(); ctx.moveTo(C, C - N * .36 * s); ctx.bezierCurveTo(C + N * .1 * s, C - N * .18 * s, C + N * .3 * s, C - N * .1 * s, C + N * .26 * s, C + N * .12 * s); ctx.bezierCurveTo(C + N * .24 * s, C + N * .3 * s, C + N * .1 * s, C + N * .38 * s, C, C + N * .38 * s); ctx.bezierCurveTo(C - N * .1 * s, C + N * .38 * s, C - N * .24 * s, C + N * .3 * s, C - N * .26 * s, C + N * .12 * s); ctx.bezierCurveTo(C - N * .3 * s, C - N * .1 * s, C - N * .1 * s, C - N * .18 * s, C, C - N * .36 * s); ctx.closePath(); ctx.fillStyle = css(c); ctx.fill(); }; ctx.save(); ctx.translate(0, N * .02); f(1, [214, 62, 70]); ctx.translate(C * .32, C * .3); ctx.scale(.68, .68); f(1, [240, 160, 70]); ctx.restore(); num(NUM, C + N * .12, N * .19, [250, 244, 230]); }
  else if (KIND === 'day') { disc(N * .5, [236, 196, 132]); ctx.save(); ctx.beginPath(); ctx.arc(C, C, N * .45, 0, TAU); ctx.clip(); drawSky(SKYD[0], SKYD[1], SKYD[2], 3.7, .1); ctx.restore(); glow(C, C - N * .02, N * .4, [255, 216, 150], .5); disc(N * .27, [255, 216, 150]); num(NUM, C - N * .02, N * .26, [196, 110, 96]); }
  else if (KIND === 'role') { disc(N * .5, [92, 168, 162]); disc(N * .45, [120, 190, 180]); tok(N * .3); }
  else if (KIND === 'trick') { disc(N * .5, [146, 118, 181]); ctx.save(); ctx.beginPath(); ctx.arc(C, C, N * .45, 0, TAU); ctx.clip(); drawSky(SKYN[0], SKYN[1], SKYN[2], 3.7, 1); ctx.restore(); tok(N * .26); const r = N * .045, x = C + N * .24, y = C - N * .24; glow(x, y, r * 4, [255, 236, 170], .7); poly([[x, y - r * 1.3], [x + r, y], [x, y + r * 1.3], [x - r, y]], [255, 236, 170]); }
  else { disc(N * .5, [146, 118, 181]); ctx.save(); ctx.beginPath(); ctx.arc(C, C, N * .45, 0, TAU); ctx.clip(); drawSky(SKYD[0], SKYD[1], SKYD[2], 3.7, .1); ctx.restore(); { const x = N / 2, y = N / 2 + N * .1, s = N * .5, t = 0; __BOOK__ } const r = N * .05, dy = C - N * .2; glow(C, dy, r * 4, [255, 236, 170], .7); poly([[C, dy - r * 1.3], [C + r, dy], [C, dy + r * 1.3], [C - r, dy]], [255, 236, 170]); }
  ctx = real; [W, H] = keep; const ta = document.createElement('textarea'); ta.id = 'png'; ta.textContent = c2.toDataURL('image/png'); document.body.appendChild(ta); document.title = 'ok'; }, 500);"""
IDS = {'first_win': ('first', '', ''), 'win_sailor': ('role', '', 'sailor'), 'win_heretic': ('role', '', 'heretic'), 'win_pukka': ('role', '', 'pukka'),
       'trick_sailor': ('trick', '', 'sailor'), 'trick_heretic': ('trick', '', 'heretic'), 'trick_pukka': ('trick', '', 'pukka')}
for n in (3, 5, 7, 10, 15): IDS[f'streak_{n}'] = ('streak', str(n), '')
for n in (5, 10, 25, 50, 100, 200): IDS[f'wins_{n}'] = ('wins', str(n), '')
for n in (3, 4, 5, 7): IDS[f'day_{n}'] = ('day', str(n), '')
want = sys.argv[1:] or list(IDS)
out = os.path.join(ROOT, 'assets', 'achievements'); os.makedirs(out, exist_ok=True)
for a in want:
    k, n, r = IDS[a]
    render(JS.replace('__K__', k).replace('__N__', n).replace('__R__', r).replace('__BOOK__', BOOK), '390,844', 1, os.path.join(out, a + '.png'))
