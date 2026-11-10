#!/usr/bin/env python3
"""The English title lettering 'Ramen Oddities', in the hand of MELO's 'Ramen Puzzle' (assets/logo/title-en-clean.svg):
'Ramen' and the 'e' are MELO's own strokes; O, d, i, t, s are drawn here in the same angular hand
(22-unit stems and bars, chamfered corners, bars ending on a slant). Writes assets/logo/title-en-clean.svg
(the old one is kept as title-en-puzzle-clean.svg) and prints the <svg> for index.html's LOGO.en."""
import re, os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'assets/logo/title-en-puzzle-clean.svg')
if not os.path.exists(SRC): shutil.copy(os.path.join(ROOT, 'assets/logo/title-en-clean.svg'), SRC)
s = open(SRC).read(); d = re.search(r' d="([^"]+)"', s).group(1)
subs = [x.strip() for x in re.split(r'(?=M)', d) if x.strip()]
OX, OY = 146, 290      # the viewBox origin: glyphs below are in picture coordinates from it
pts = lambda sp: [tuple(map(float, p.split(','))) for p in re.findall(r'-?[\d.]+,-?[\d.]+', sp)]
xmin = lambda sp: min(p[0] for p in pts(sp)) - OX
keep = [sp for sp in subs if xmin(sp) < 760]                                     # R, a, m, e, n
e = [sp for sp in subs if xmin(sp) > 1415]                                       # the e of Puzzle
def shift(sp, dx): return 'M' + ' L'.join(f'{x + dx:g},{y:g}' for x, y in pts(sp)) + ' Z'
def poly(p, x0): return 'M' + ' L'.join(f'{x + x0 + OX:g},{y + OY:g}' for x, y in p) + ' Z'
O = [[(20, 16), (120, 16), (140, 36), (140, 186), (120, 206), (20, 206), (0, 186), (0, 36)],
     [(28, 38), (112, 38), (118, 44), (118, 178), (112, 184), (28, 184), (22, 178), (22, 44)]]          # an angular ring, cap height
D = [[(117, 8), (117, 206), (95, 206), (95, 28)],                                                         # the ascender, cut on a slant like the l
     [(22, 72), (95, 72), (95, 93), (28, 93), (22, 99), (22, 178), (28, 184), (95, 184), (95, 206), (22, 206), (0, 184), (0, 94)]]
I = [[(0, 77), (7, 77), (14, 71), (22, 72), (22, 206), (0, 206)], [(8, 32), (22, 32), (14, 52), (0, 52)]]   # stem as the u starts; a slanted dot
T = [[(30, 40), (52, 24), (52, 184), (82, 184), (82, 206), (48, 206), (30, 188)],                          # stem with a foot to the right
     [(20, 72), (30, 72), (30, 93), (0, 93)], [(52, 72), (84, 72), (66, 93), (52, 93)]]                    # the crossbar either side of it, ends on a slant
S = [[(22, 72), (118, 72), (99, 93), (28, 93), (22, 99), (22, 117), (28, 123), (96, 123), (118, 145), (118, 184), (96, 206), (0, 206),
      (19, 184), (90, 184), (96, 178), (96, 151), (90, 145), (22, 145), (0, 123), (0, 94)]]
out = list(keep); x = 839
for glyph, w, gap in ((O, 140, 28), (D, 117, 28), (D, 117, 30), (I, 22, 26), (T, 84, 20), (I, 22, 28)):
    out += [poly(p, x) for p in glyph]; x += w + gap
out += [shift(sp, x - 1424) for sp in e]; x += 121 + 30
out += [poly(p, x) for p in S]; x += 118
W = x + 8
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="235" viewBox="{OX} {OY} {W} 235"><path fill="#fff" fill-rule="evenodd" d="{" ".join(out)}"/></svg>'
open(os.path.join(ROOT, 'assets/logo/title-en-clean.svg'), 'w').write(svg)
print(svg)
