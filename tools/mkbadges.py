#!/usr/bin/env python3
"""Game Center achievement images for Tiny Clocktower, drawn with the /3b game's own canvas code (deploy/3b.html).
One 1024x1024 PNG per achievement into assets/achievements/<id>.png (Game Center shows them in a circle, so each fills a round medallion):
  all in white lines on a transparent ground, inside a white ring:
  wins: a star with the count   streaks: a flame with the count   days: the sun with the day
  roles: that role's emblem   first win: the star with 1
  tricks: the anchor in a lifebuoy (survived the vote), the Pukka with two poison reminders (two poison marks), the Heretic's cross in a laurel (executed, yet won)
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
  if (KIND === 'wins') { const pts = []; for (let k = 0; k < 10; k++) { const a = -Math.PI / 2 + k * Math.PI / 5, r = k % 2 ? N * .15 : N * .33; pts.push([C + Math.cos(a) * r, C + N * .03 + Math.sin(a) * r]); } path(pts); num(NUM, C + N * .03, NUM.length > 3 ? N * .08 : NUM.length > 2 ? N * .1 : N * .13); }      // the count right on the star's own centre
  else if (KIND === 'streak') { const P = (u, v) => [C + u * N, C + v * N]; ctx.beginPath(); ctx.moveTo(...P(0, .34)); ctx.bezierCurveTo(...P(-.17, .34), ...P(-.25, .22), ...P(-.23, .07)); ctx.bezierCurveTo(...P(-.22, -.04), ...P(-.17, -.1), ...P(-.19, -.21)); ctx.bezierCurveTo(...P(-.1, -.15), ...P(-.07, -.08), ...P(-.07, -.02)); ctx.bezierCurveTo(...P(-.1, -.15), ...P(-.04, -.28), ...P(.03, -.38)); ctx.bezierCurveTo(...P(.04, -.26), ...P(.1, -.2), ...P(.15, -.12)); ctx.bezierCurveTo(...P(.16, -.17), ...P(.17, -.2), ...P(.17, -.24)); ctx.bezierCurveTo(...P(.25, -.12), ...P(.26, .02), ...P(.23, .12)); ctx.bezierCurveTo(...P(.2, .26), ...P(.12, .34), ...P(0, .34)); ctx.closePath(); ctx.stroke(); num(NUM, C + N * .14, NUM.length > 1 ? N * .13 : N * .15); }      // a flame with its tongues, the run in it
  else if (KIND === 'day') { ctx.beginPath(); ctx.arc(C, C, N * .19, 0, TAU); ctx.stroke(); for (let k = 0; k < 12; k++) { const a = k * TAU / 12; ctx.beginPath(); ctx.moveTo(C + Math.cos(a) * N * .26, C + Math.sin(a) * N * .26); ctx.lineTo(C + Math.cos(a) * N * .34, C + Math.sin(a) * N * .34); ctx.stroke(); } num(NUM, C, N * .17); }
  else if (KIND === 'role') emblem(C, C, N * .38);
  else if (KIND === 'trick' && ROLE === 'sailor') { emblem(C, C, N * .25); ctx.lineWidth = lw * .8; for (const r of [N * .3, N * .37]) { ctx.beginPath(); ctx.arc(C, C, r, 0, TAU); ctx.stroke(); } for (let k = 0; k < 4; k++) { const a = Math.PI / 4 + k * Math.PI / 2; for (const d of [-.16, .16]) { ctx.beginPath(); ctx.moveTo(C + Math.cos(a + d) * N * .3, C + Math.sin(a + d) * N * .3); ctx.lineTo(C + Math.cos(a + d) * N * .37, C + Math.sin(a + d) * N * .37); ctx.stroke(); } } }      // survived the vote: the anchor inside a lifebuoy
  else if (KIND === 'trick' && ROLE === 'pukka') { const mark = (x, y) => { const r = N * .165; ctx.globalCompositeOperation = 'destination-out'; ctx.beginPath(); ctx.arc(x, y, r + lw * 1.6, 0, TAU); ctx.fill(); ctx.globalCompositeOperation = 'source-over'; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.stroke(); emblem(x - r * .05, y, r * .74); }; mark(C + N * .11, C - N * .1); mark(C - N * .1, C + N * .1); }      // two poison marks at once: two of the Pukka's reminder tokens, one on the other
  else if (KIND === 'trick') { emblem(C, C - N * .01, N * .26); const R = N * .31, cy = C + N * .02; for (const m of [-1, 1]) { const at = a => [C + Math.cos(a) * R, cy + Math.sin(a) * R]; ctx.lineWidth = lw * .7; ctx.beginPath(); for (let k = 0; k <= 30; k++) { const q = at(Math.PI / 2 + m * (.3 + k / 30 * 2.1)); k ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); } ctx.stroke(); for (let k = 0; k < 6; k++) { const a = Math.PI / 2 + m * (.55 + k * .34), q = at(a), b = at(a + m * .05), t = Math.atan2(b[1] - q[1], b[0] - q[0]); for (const side of [-1, 1]) { ctx.save(); ctx.translate(q[0], q[1]); ctx.rotate(t + side * .55); ctx.beginPath(); ctx.ellipse(N * .04, 0, N * .042, N * .016, 0, 0, TAU); ctx.fill(); ctx.restore(); } } } }      // executed and still won: the Heretic's cross in a victor's laurel
  else { const bx = C, by = C + N * .12, w = N * .27, h = N * .2, d = N * .07; path([[bx, by], [bx - w, by - d], [bx - w, by - d - h], [bx, by - h]]); path([[bx, by], [bx + w, by - d], [bx + w, by - d - h], [bx, by - h]]); ctx.beginPath(); ctx.moveTo(bx - w, by - d); ctx.lineTo(bx - w, by - d + N * .05); ctx.lineTo(bx, by + N * .05); ctx.lineTo(bx + w, by - d + N * .05); ctx.lineTo(bx + w, by - d); ctx.stroke(); spark(C, C - N * .2, N * .055); }
  ctx = real; [W, H] = keep; const ta = document.createElement('textarea'); ta.id = 'png'; ta.textContent = c2.toDataURL('image/png'); document.body.appendChild(ta); document.title = 'ok'; }, 500);"""
def renderA(script, size, dsf, out):      # as render(), but keeps the transparency
    page_src = open(os.path.join(ROOT, 'deploy', '3b.html'), encoding='utf-8').read(); i = page_src.rfind('</body>'); page = os.path.join(TMP, 'mkbadge.html')
    open(page, 'w', encoding='utf-8').write(page_src[:i] + '<script>\n' + script + '\n</script>\n' + page_src[i:])
    dom = subprocess.run([HS, '--no-sandbox', '--disable-gpu', f'--window-size={size}', f'--force-device-scale-factor={dsf}', '--virtual-time-budget=40000', '--dump-dom', f'file://{page}?lang=hans'], capture_output=True, text=True, timeout=300).stdout
    m = re.search(r'<textarea id="png">data:image/png;base64,([^<]+)</textarea>', dom)
    if not m: sys.exit(f'{out}: no image came back')
    Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGBA').save(out, optimize=True); print(out)
IDS = {'first_win': ('wins', '1', ''), 
       'trick_pukka': ('trick', '', 'pukka')}
for n in (3, 5): IDS[f'streak_{n}'] = ('streak', str(n), '')
for n in (5, 10, 25, 50, 100, 200, 300, 500, 1000): IDS[f'wins_{n}'] = ('wins', str(n), '')
for n in (3, 5, 7): IDS[f'day_{n}'] = ('day', str(n), '')
want = sys.argv[1:] or list(IDS)
out = os.path.join(ROOT, 'assets', 'achievements'); os.makedirs(out, exist_ok=True)
for a in want:
    k, n, r = IDS[a]
    renderA(JS.replace('__K__', k).replace('__N__', n).replace('__R__', r).replace('__BOOK__', BOOK), '390,844', 1, os.path.join(out, a + '.png'))
