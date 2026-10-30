"""Smooth MELO's traced title SVGs: they are polygons traced from pixels, so every slanted edge is a staircase of 1-px
steps. Each ring is simplified with Douglas-Peucker (EPS in SVG units), which turns the stairs into straight slants and
keeps real corners, then the cleaned SVGs are written to assets/logo/title-<lang>-clean.svg and inlined into index.html.
usage: python3 tools/simplify_logo.py [EPS]"""
import re, sys, os
EPS = float(sys.argv[1]) if len(sys.argv) > 1 else 1.6
ROOT = os.path.join(os.path.dirname(__file__), '..')
def rdp(pts, eps):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]; dx, dy = x2 - x1, y2 - y1; n = (dx * dx + dy * dy) ** .5 or 1e-9
    i, dm = 0, -1
    for k in range(1, len(pts) - 1):
        d = abs(dy * pts[k][0] - dx * pts[k][1] + x2 * y1 - y2 * x1) / n if n > 1e-9 else ((pts[k][0] - x1) ** 2 + (pts[k][1] - y1) ** 2) ** .5
        if d > dm: i, dm = k, d
    if dm <= eps: return [pts[0], pts[-1]]
    return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)
def ring(pts, eps):      # a closed ring: split at the point farthest from the first, simplify both halves
    far = max(range(len(pts)), key=lambda k: (pts[k][0] - pts[0][0]) ** 2 + (pts[k][1] - pts[0][1]) ** 2)
    a = rdp(pts[:far + 1], eps); b = rdp(pts[far:] + [pts[0]], eps)
    return a[:-1] + b[:-1]
def clean(svg):
    d = re.search(r' d="([^"]*)"', svg).group(1); out = []; n0 = n1 = 0
    for sub in re.findall(r'M[^MZ]*Z', d):
        pts = [tuple(map(float, p)) for p in re.findall(r'(-?[\d.]+),(-?[\d.]+)', sub)]
        if pts[-1] == pts[0]: pts = pts[:-1]
        r = ring(pts, EPS); n0 += len(pts); n1 += len(r)
        out.append('M' + ' L'.join(f'{x:g},{y:g}' for x, y in r) + ' Z')
    return svg.replace(d, ' '.join(out)), n0, n1
html = open(f'{ROOT}/index.html').read()
for l in ('hans', 'hant', 'en'):
    src = open(f'{ROOT}/assets/logo/title-{l}.svg').read().strip(); new, n0, n1 = clean(src)
    open(f'{ROOT}/assets/logo/title-{l}-clean.svg', 'w').write(new + '\n')
    m = re.search(l + r': `(<svg[^`]*)`', html); assert m, l
    html = html[:m.start(1)] + new + html[m.end(1):]
    print(l, n0, '->', n1, 'points')
open(f'{ROOT}/index.html', 'w').write(html)
