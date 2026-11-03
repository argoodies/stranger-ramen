#!/usr/bin/env python3
"""The capsules' words as SVG outlines, so they sit exactly in the middle on any device: no font is drawn at run time.
Each language's words are laid out from Noto Sans CJK Bold (SC for 简体 and English, TC for 繁體), turned into one path and
cropped to their ink, then written between the LABELS markers in tools/botc3.js and tools/xhs_rank.js as
  { hans: [d, width, height], hant: [...], en: [...] }   (units: em / 1000, y down; the box is the ink's own box)
A capsule draws it as <svg viewBox="0 0 w h" height="h/1000 * font-size">: centring the box centres the ink.
usage: tools/mklabels.py"""
import os, re, json
from fontTools.ttLib import TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
WORDS = {'hans': ('总胜场榜', 2), 'hant': ('總勝場榜', 3), 'en': ('Most Wins', 2)}      # text, face in the collection (2 SC, 3 TC)
fonts = TTCollection(FONT).fonts

def outline(text, face):
    f = fonts[face]; gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm; hmtx = f['hmtx']
    k = 1000 / upm; x = 0; parts = []
    bounds = BoundsPen(gs)
    for ch in text:
        g = cmap[ord(ch)]
        for pen_target in (bounds,):
            gs[g].draw(TransformPen(pen_target, (k, 0, 0, -k, x, 0)))      # y down, em = 1000
        sp = SVGPathPen(gs, ntos=lambda v: ('%.1f' % v).rstrip('0').rstrip('.'))
        gs[g].draw(TransformPen(sp, (k, 0, 0, -k, x, 0)))
        parts.append(sp.getCommands())
        x += hmtx[g][0] * k
    x0, y0, x1, y1 = bounds.bounds
    return ' '.join(parts), (x0, y0, x1, y1)

out = {}
for lang, (text, face) in WORDS.items():
    d, (x0, y0, x1, y1) = outline(text, face)
    # move the ink's box to the origin: the path is redrawn with an offset in the viewBox instead of rewriting every number
    out[lang] = [d, round(x0, 1), round(y0, 1), round(x1 - x0, 1), round(y1 - y0, 1)]
    print(lang, text, 'ink box', round(x1 - x0), 'x', round(y1 - y0), 'em/1000;', len(d), 'chars of path')

blob = '/*LABELS*/' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '/*/LABELS*/'
for f in ('tools/botc3.js', 'tools/xhs_rank.js'):
    p = os.path.join(ROOT, f); s = open(p, encoding='utf-8').read()
    s2, n = re.subn(r'/\*LABELS\*/.*?/\*/LABELS\*/', lambda m: blob, s, flags=re.S)
    if n != 1: raise SystemExit(f'{f}: no LABELS marker')
    open(p, 'w', encoding='utf-8').write(s2); print(f, 'updated')
