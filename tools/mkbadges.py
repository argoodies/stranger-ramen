#!/usr/bin/env python3
"""Game Center achievement images for Tiny Clocktower, drawn with the /3b game's own canvas code (deploy/3b.html).
One 1024x1024 PNG per achievement into assets/achievements/<id>.png (Game Center shows them in a circle, so each fills a round medallion):
  all in white lines on a transparent ground, inside a white ring:
  wins: a star with the count   streaks: a flame with the count   days: the sun with the day
  roles: that role's emblem     tricks: the emblem and a sparkle   first: the open book and its sparkle
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
setTimeout(() => { const N = 1024, c2 = document.createElement('canvas'); c2.width = c2.height = N; const real = ctx, keep = [W, H]; ctx = c2.getContext('2d'); W = H = N;
  const KIND = '__K__', NUM = '__N__', ROLE = '__R__', C = N / 2, WT = [255, 255, 255], lw = N * .034;
  ctx.strokeStyle = css(WT); ctx.fillStyle = css(WT); ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const ring = () => { ctx.beginPath(); ctx.arc(C, C, N * .45, 0, TAU); ctx.stroke(); };
  const num = (t, y, size) => { ctx.font = `700 ${size}px ${THINF}`; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; const m = ctx.measureText(t); ctx.fillText(t, C, y + (m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) / 2); };
  const path = pts => { ctx.beginPath(); pts.forEach((p, k) => k ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); ctx.stroke(); };
  const spark = (x, y, r) => path([[x, y - r * 1.3], [x + r, y], [x, y + r * 1.3], [x - r, y]]);
  const emblem = (x, y, r) => { const o = document.createElement('canvas'); o.width = o.height = N; const me = ctx; ctx = o.getContext('2d'); roleToken(x, y, r, ROLE, 1, WT); const im = ctx.getImageData(0, 0, N, N), d = im.data; for (let q = 0; q < d.length; q += 4) if (d[q + 3]) { const k = Math.max(0, Math.min(1, (d[q] - 128) / 127)); d[q] = d[q + 1] = d[q + 2] = 255; d[q + 3] *= k; } ctx.putImageData(im, 0, 0); ctx = me; ctx.drawImage(o, 0, 0); };      // the role's emblem in white only: the Heretic's inner line becomes a gap
  ring();
  if (KIND === 'wins') { const pts = []; for (let k = 0; k < 10; k++) { const a = -Math.PI / 2 + k * Math.PI / 5, r = k % 2 ? N * .15 : N * .33; pts.push([C + Math.cos(a) * r, C + N * .025 + Math.sin(a) * r]); } path(pts); num(NUM, C + N * .05, NUM.length > 2 ? N * .1 : N * .13); }
  else if (KIND === 'streak') { const s = .95; ctx.beginPath(); ctx.moveTo(C, C - N * .33 * s); ctx.bezierCurveTo(C + N * .09 * s, C - N * .16 * s, C + N * .27 * s, C - N * .08 * s, C + N * .23 * s, C + N * .12 * s); ctx.bezierCurveTo(C + N * .21 * s, C + N * .28 * s, C + N * .09 * s, C + N * .34 * s, C, C + N * .34 * s); ctx.bezierCurveTo(C - N * .09 * s, C + N * .34 * s, C - N * .21 * s, C + N * .28 * s, C - N * .23 * s, C + N * .12 * s); ctx.bezierCurveTo(C - N * .27 * s, C - N * .08 * s, C - N * .09 * s, C - N * .16 * s, C, C - N * .33 * s); ctx.closePath(); ctx.stroke(); num(NUM, C + N * .1, N * .15); }
  else if (KIND === 'day') { ctx.beginPath(); ctx.arc(C, C, N * .19, 0, TAU); ctx.stroke(); for (let k = 0; k < 12; k++) { const a = k * TAU / 12; ctx.beginPath(); ctx.moveTo(C + Math.cos(a) * N * .26, C + Math.sin(a) * N * .26); ctx.lineTo(C + Math.cos(a) * N * .34, C + Math.sin(a) * N * .34); ctx.stroke(); } num(NUM, C, N * .17); }
  else if (KIND === 'role') emblem(C, C, N * .38);
  else if (KIND === 'trick') { emblem(C - N * .02, C + N * .02, N * .32); spark(C + N * .24, C - N * .23, N * .045); }
  else { const bx = C, by = C + N * .12, w = N * .27, h = N * .2, d = N * .07; path([[bx, by], [bx - w, by - d], [bx - w, by - d - h], [bx, by - h]]); path([[bx, by], [bx + w, by - d], [bx + w, by - d - h], [bx, by - h]]); ctx.beginPath(); ctx.moveTo(bx - w, by - d); ctx.lineTo(bx - w, by - d + N * .05); ctx.lineTo(bx, by + N * .05); ctx.lineTo(bx + w, by - d + N * .05); ctx.lineTo(bx + w, by - d); ctx.stroke(); spark(C, C - N * .2, N * .055); }
  ctx = real; [W, H] = keep; const ta = document.createElement('textarea'); ta.id = 'png'; ta.textContent = c2.toDataURL('image/png'); document.body.appendChild(ta); document.title = 'ok'; }, 500);"""
def renderA(script, size, dsf, out):      # as render(), but keeps the transparency
    page_src = open(os.path.join(ROOT, 'deploy', '3b.html'), encoding='utf-8').read(); i = page_src.rfind('</body>'); page = os.path.join(TMP, 'mkbadge.html')
    open(page, 'w', encoding='utf-8').write(page_src[:i] + '<script>\n' + script + '\n</script>\n' + page_src[i:])
    dom = subprocess.run([HS, '--no-sandbox', '--disable-gpu', f'--window-size={size}', f'--force-device-scale-factor={dsf}', '--virtual-time-budget=40000', '--dump-dom', f'file://{page}?lang=hans'], capture_output=True, text=True, timeout=300).stdout
    m = re.search(r'<textarea id="png">data:image/png;base64,([^<]+)</textarea>', dom)
    if not m: sys.exit(f'{out}: no image came back')
    Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGBA').save(out, optimize=True); print(out)
IDS = {'first_win': ('first', '', ''), 'win_sailor': ('role', '', 'sailor'), 'win_heretic': ('role', '', 'heretic'), 'win_pukka': ('role', '', 'pukka'),
       'trick_sailor': ('trick', '', 'sailor'), 'trick_heretic': ('trick', '', 'heretic'), 'trick_pukka': ('trick', '', 'pukka')}
for n in (3, 5, 7, 10, 15): IDS[f'streak_{n}'] = ('streak', str(n), '')
for n in (5, 10, 25, 50, 100, 200): IDS[f'wins_{n}'] = ('wins', str(n), '')
for n in (3, 4, 5, 7): IDS[f'day_{n}'] = ('day', str(n), '')
want = sys.argv[1:] or list(IDS)
out = os.path.join(ROOT, 'assets', 'achievements'); os.makedirs(out, exist_ok=True)
for a in want:
    k, n, r = IDS[a]
    renderA(JS.replace('__K__', k).replace('__N__', n).replace('__R__', r).replace('__BOOK__', BOOK), '390,844', 1, os.path.join(out, a + '.png'))
