"""Build deploy/sdc.html: sdc.html with the town's drawing engine lifted out of index.html, so /sdc is drawn exactly like the game.
usage: python3 tools/mksdc.py"""
import re, os
ROOT = os.path.join(os.path.dirname(__file__), '..')
src = open(f'{ROOT}/index.html').read(); tpl = open(f'{ROOT}/sdc.html').read()
def block(head):      # a top-level function or class, by its opening text, up to the closing brace at column 0
    i = src.index('\n' + head) + 1; j = src.index('\n}\n', i) + 3; return src[i:j]
def lines(a, b):      # from the line starting with a up to (not including) the line starting with b
    i = src.index('\n' + a) + 1; return src[i:src.index('\n' + b, i) + 1]
def one(start):       # one whole line
    i = src.index('\n' + start) + 1; return src[i:src.index('\n', i) + 1]
parts = [one('const TAU'), lines('const clamp = ', '// One face everywhere'), lines('let AC = null, bus', '// ------------------------------------------------------------ world'), block('class View'), block('function fig('), one('const PAL = '), one('let CLOTH'),
         lines('const DOOR = [-5, 3]', 'function bfs('), block('function bfs('), block('function tree('), block('function lamp('), block('function drawTower('), block('function drawBarHouse('), block('function drawHouse('),
         one('const SKYD = '), block('function skyNow('), block('function drawSky('), one('const HALF = 180'), one('function gameHour'), one('function clockHands')]
html = tpl.replace('/*ENGINE*/', '\n'.join(parts))
assert '/*ENGINE*/' in tpl
open(f'{ROOT}/deploy/sdc.html', 'w').write(html); print('deploy/sdc.html', len(html), 'bytes')
