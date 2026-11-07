"""The title of 星穹十字小镇 in the style of MELO's lettering (assets/logo/title-*-clean.svg): even strokes, 45-degree cut corners and ends, small stencil gaps.
物语/語 and the English a, e, l are MELO's own shapes; the rest is drawn here from strokes. Writes assets/logo/star-<lang>.svg and inlines them. usage: python3 tools/mktitle.py"""
import re, math, os
ROOT = os.path.join(os.path.dirname(__file__), '..')
W = 17
def stroke(pts, w=W, cut=(1, 1)):      # a polyline as a polygon with mitred joins; each end is cut on a slant (cut: which way, 0 = square)
    n = len(pts); nor = []
    for i in range(n - 1):
        x = pts[i + 1][0] - pts[i][0]; y = pts[i + 1][1] - pts[i][1]; l = math.hypot(x, y); nor.append((-y / l, x / l))
    L = []; R = []
    for i, p in enumerate(pts):
        if i == 0: m = nor[0]; k = 1
        elif i == n - 1: m = nor[-1]; k = 1
        else:
            a, b = nor[i - 1], nor[i]; mx, my = a[0] + b[0], a[1] + b[1]; l = math.hypot(mx, my); m = (mx / l, my / l); k = 1 / max(.35, m[0] * a[0] + m[1] * a[1])
        L.append((p[0] + m[0] * w / 2 * k, p[1] + m[1] * w / 2 * k)); R.append((p[0] - m[0] * w / 2 * k, p[1] - m[1] * w / 2 * k))
    def ext(q, d, s): return (q[0] + d[0] * s, q[1] + d[1] * s)
    d0 = (nor[0][1], -nor[0][0]); d1 = (-nor[-1][1], nor[-1][0])
    L[0] = ext(L[0], d0, -cut[0] * w * .0); R[0] = ext(R[0], d0, cut[0] * w); L[-1] = ext(L[-1], d1, cut[1] * w); 
    return L + R[::-1]
def box(x0, y0, x1, y1, c=14, w=W):      # a closed box with its bottom-right and top-left corners cut, as the 口 of the original
    return [stroke([(x0 + c, y0), (x1, y0), (x1, y1 - c), (x1 - c, y1), (x0, y1), (x0, y0 + c), (x0 + c, y0)], w, (0, 0))]
GLYPHS = {
 '十': lambda: [stroke([(0, 108), (230, 108)]), stroke([(115, 0), (115, 231)])],
 '字': lambda: [stroke([(116, 0), (116, 30)]), stroke([(6, 72), (6, 44), (222, 44), (222, 72)], W, (1, 1)), stroke([(58, 88), (172, 88), (122, 132)], W, (1, 0)), stroke([(116, 136), (116, 214), (92, 231)], W, (0, 1)), stroke([(0, 158), (230, 158)])],
 '星': lambda: box(52, 2, 180, 100) + [stroke([(60, 51), (172, 51)], W, (0, 0)), stroke([(70, 112), (34, 150)]), stroke([(46, 137), (204, 137)]), stroke([(116, 118), (116, 222)], W, (1, 0)), stroke([(54, 178), (182, 178)]), stroke([(2, 222), (230, 222)])],
 '小': lambda: [stroke([(116, 0), (116, 212), (90, 231)], W, (1, 1)), stroke([(62, 66), (14, 160)]), stroke([(170, 66), (218, 160)])],
 '镇': lambda: [stroke([(58, 0), (10, 62)]), stroke([(34, 38), (92, 38)]), stroke([(26, 88), (88, 88)]), stroke([(56, 88), (56, 196), (86, 176)], W, (0, 1)), stroke([(104, 22), (230, 22)]), stroke([(166, 0), (166, 42)])] + box(122, 54, 212, 158, 10) + [stroke([(130, 90), (204, 90)], W, (0, 0)), stroke([(130, 124), (204, 124)], W, (0, 0)), stroke([(98, 178), (230, 178)]), stroke([(140, 192), (104, 228)]), stroke([(192, 192), (228, 228)])],
 '鎮': lambda: [stroke([(52, 0), (6, 56)]), stroke([(58, 8), (98, 52)]), stroke([(24, 74), (88, 74)]), stroke([(14, 114), (98, 114)]), stroke([(56, 74), (56, 208)], W, (0, 0)), stroke([(28, 142), (40, 184)]), stroke([(86, 142), (72, 184)]), stroke([(0, 222), (104, 222)]), stroke([(112, 22), (230, 22)]), stroke([(170, 0), (170, 42)])] + box(130, 54, 214, 158, 10) + [stroke([(138, 90), (206, 90)], W, (0, 0)), stroke([(138, 124), (206, 124)], W, (0, 0)), stroke([(108, 178), (230, 178)]), stroke([(146, 192), (114, 228)]), stroke([(194, 192), (228, 228)])],
 '穹': lambda: [stroke([(116, 0), (116, 24)]), stroke([(6, 62), (6, 36), (224, 36), (224, 62)]), stroke([(90, 58), (54, 98)]), stroke([(142, 58), (180, 98)]), stroke([(54, 116), (174, 116), (174, 152), (64, 152), (64, 188), (192, 188), (192, 214), (168, 231)], W, (1, 1))],
}
S = 21      # English: the stroke of MELO's capitals
LAT = {      # x, in a box from cap height 306 to baseline 496, x-height 362
 'S': (120, lambda: [stroke([(120, 316), (22, 316), (10, 330), (10, 386), (22, 398), (108, 398), (120, 410), (120, 472), (108, 486), (0, 486)], S)]),
 't': (88, lambda: [stroke([(34, 322), (34, 472), (48, 486), (86, 486)], S), stroke([(0, 372), (86, 372)], S)]),
 'r': (78, lambda: [stroke([(10, 362), (10, 496)], S), stroke([(21, 396), (46, 372), (78, 372)], S, (0, 1))]),
 'c': (104, lambda: [stroke([(104, 372), (24, 372), (10, 386), (10, 472), (24, 486), (104, 486)], S)]),
 'o': (120, lambda: [stroke([(24, 372), (96, 372), (110, 386), (110, 472), (96, 486), (24, 486), (10, 472), (10, 386), (24, 372)], S, (0, 0))]),
 's': (108, lambda: [stroke([(104, 372), (22, 372), (10, 384), (10, 416), (22, 428), (88, 428), (100, 440), (100, 472), (88, 486), (0, 486)], S)]),
 'w': (124, lambda: [stroke([(0, 362), (26, 486), (62, 392), (98, 486), (124, 362)], S, (1, 1))]),
 'T': (150, lambda: [stroke([(0, 316), (150, 316)], S), stroke([(75, 336), (75, 496)], S)]),
}
def path(polys): return ' '.join('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in p) + ' Z' for p in polys)
def shift(polys, dx, dy=0): return [[(x + dx, y + dy) for x, y in p] for p in polys]
def subs(l):
    s = open(f'{ROOT}/assets/logo/title-{l}-clean.svg').read(); d = re.search(r' d="([^"]*)"', s).group(1); out = []
    for u in re.findall(r'M[^MZ]*Z', d): out.append([tuple(map(float, q)) for q in re.findall(r'(-?[\d.]+),(-?[\d.]+)', u)])
    return out
def pick_x(ps, a, b): return [p for p in ps if min(q[0] for q in p) >= a and max(q[0] for q in p) <= b]
SLOT = [162, 435, 700, 940, 1194, 1441]      # where MELO's six letters stood
def chinese(l):
    mine = []
    for ch, x in zip('星穹十字小' + ('镇' if l == 'hans' else '鎮'), SLOT): mine += shift(GLYPHS[ch](), x, 310)
    return mine, [], (154, 288, 1526, 266)
def english():
    en = subs('en'); keep = []; x = 150; mine = []; GAP = 26
    a, l, n = pick_x(en, 323, 441), pick_x(en, 1521, 1543), pick_x(en, 787, 891)
    def put(ps, x0, x1):
        nonlocal x; keep.extend(shift(ps, x - x0, -7 if ps is n else 0)); x += x1 - x0 + GAP
    for ch in 'Starcross Town':
        if ch == ' ': x += 50; continue
        if ch == 'a': put(a, 323, 441)
        elif ch == 'n': put(n, 787, 891)
        else: w, f = LAT[ch]; mine += shift(f(), x); x += w + GAP
    return mine, keep, (140, 290, x - 140, 235)
html = open(f'{ROOT}/index.html').read()
for l in ('hans', 'hant', 'en'):
    mine, keep, (vx, vy, vw, vh) = english() if l == 'en' else chinese(l)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="{1700 * vh / vw:.0f}" viewBox="{vx} {vy} {vw:.0f} {vh}"><path fill="#fff" d="{path(mine)}"/><path fill="#fff" fill-rule="evenodd" d="{path(keep)}"/></svg>'
    open(f'{ROOT}/assets/logo/star-{l}.svg', 'w').write(svg + '\n')
    m = re.search(l + r': `(<svg[^`]*)`', html)
    if m: html = html[:m.start(1)] + svg + html[m.end(1):]
    print(l, len(svg))
open(f'{ROOT}/index.html', 'w').write(html)
