#!/usr/bin/env python3
"""Build the Xiaohongshu (小红书) mini-tool zip of the three-player game from deploy/3b.html.

The mini-tool container (see .claude/skills/minitool-zip-builder) runs an offline H5 page under a strict CSP and a
Chrome 61 baseline, so the page is rewritten, not just zipped:
  * the inline <script> blocks become package files app1.js, app2.js, app3.js, lowered to ES2017 / Chrome 61 with esbuild
    and then parsed with acorn at ecmaVersion 2017 as a gate;
  * a small boot.js runs first: it loads the saved game, language and achievements from the container's Storage JS API
    (client 9.46+, falling back to localStorage), then loads the three game scripts in order; the game reads and writes
    through window.__kv instead of localStorage;
  * CSS that Chrome 61 cannot parse gets a baseline: inset, flex gap, max(), min(); safe areas use the container's
    --safe-area-inset-* variables with env() behind them;
  * rank.js (tools/xhs_rank.js) adds the total-wins leaderboard on clients 9.51+ (mini-tool submitScore / getRankList /
    getMyRank); without it, or without nickname authorisation, nothing shows;
  * index.html sits at the zip root with only .html and .js beside it.
usage: tools/mkxhs.py [out.zip] [--debug]      (needs node/npx for esbuild and acorn; default out: dist/xhs/sanrenran.zip)"""
import os, re, sys, json, shutil, subprocess, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'deploy', '3b.html')
DEBUG = '--debug' in sys.argv; sys.argv = [x for x in sys.argv if x != '--debug']      # --debug: the leaderboard says on screen why it is or is not shown
OUT_ZIP = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, 'dist', 'xhs', 'sanrenran.zip')
STAGE = os.path.join(os.path.dirname(OUT_ZIP), 'pkg')
ESBUILD, ACORN = 'esbuild@0.25.10', 'acorn@8.15.0'
KEYS = ['ctramen', 'ctramen_lang', 'pocket_gc']      # every localStorage key the game uses

def must(cond, msg):
    if not cond: sys.exit('mkxhs: ' + msg)

html = open(SRC, encoding='utf-8').read()

# ---- scripts out of the page
blocks = list(re.finditer(r'<script>(.*?)</script>', html, re.S))
must(len(blocks) == 3, f'expected 3 inline scripts in 3b.html, found {len(blocks)}')
must('<script src' not in html and 'onclick=' not in html, 'unexpected script references in 3b.html')
scripts = [m.group(1) for m in blocks]
for k, js in enumerate(scripts):      # storage through the boot shim
    n = js.count('localStorage.')
    js = js.replace('localStorage.getItem(', '__kv.getItem(').replace('localStorage.setItem(', '__kv.setItem(')
    must('localStorage' not in js, f'app{k + 1}: a localStorage use the shim does not cover')
    for key in re.findall(r"__kv\.\w+\('([^']+)'", js): must(key in KEYS, f'unknown storage key {key}')
    scripts[k] = js.replace("'inset:0;", "'top:0;right:0;bottom:0;left:0;").replace(';inset:0;', ';top:0;right:0;bottom:0;left:0;')
for i, m in reversed(list(enumerate(blocks))):
    html = html[:m.start()] + ('<script src="./boot.js"></script>' if i == 0 else '') + html[m.end():]

# ---- CSS: a Chrome 61 baseline in front of what it cannot parse
def sub1(old, new):
    global html
    must(html.count(old) >= 1, f'css pattern not found: {old[:60]}')
    html = html.replace(old, new)
sub1('canvas{position:fixed;inset:0;', 'canvas{position:fixed;top:0;right:0;bottom:0;left:0;')
sub1('#title{position:fixed;inset:0;', '#title{position:fixed;top:0;right:0;bottom:0;left:0;')
sub1('top:calc(10px + max(env(safe-area-inset-top), var(--sat, 0px)));', 'top:calc(10px + var(--safe-area-inset-top, env(safe-area-inset-top, 0px)));')
sub1('align-items:center;gap:8px;pointer-events:none;z-index:6}', 'align-items:center;pointer-events:none;z-index:6}')
sub1('grid-template-columns:repeat(4,1fr);gap:8px;', 'grid-template-columns:repeat(4,1fr);grid-gap:8px;')
sub1('font:700 min(11.5vw,72px) var(--serif);', 'font:700 11.5vw var(--serif);')
sub1('flex-direction:column;gap:6px;padding:8px;', 'flex-direction:column;padding:8px;')
sub1('</style>', '#langMenu button+button{margin-top:6px}#top>*+*{margin-left:8px}</style>')
html = re.sub(r'env\(safe-area-inset-(top|right|bottom|left)\)', r'var(--safe-area-inset-\1, env(safe-area-inset-\1, 0px))', html)
for k, js in enumerate(scripts):
    scripts[k] = re.sub(r'env\(safe-area-inset-(top|right|bottom|left)\)', r'var(--safe-area-inset-\1, env(safe-area-inset-\1, 0px))', js)
html = re.sub(r'<html lang="[^"]*">', '<html lang="zh-CN">', html, 1)
must('<meta charset="utf-8">' in html.lower() or '<meta charset="utf-8"' in html.lower(), 'no utf-8 charset')
must('viewport-fit=cover' in html, 'viewport lacks viewport-fit=cover')

# ---- boot.js: storage first, then the game scripts in order
BOOT = r"""/* boot: the saved game comes from the mini-tool Storage JS API when the client has it (9.46+), else from localStorage;
   the game reads and writes through window.__kv; then app1.js, app2.js and app3.js load in order */
(function () {
  var KEYS = %s, APPS = ['./app1.js', './app2.js', './app3.js', './rank.js'], mem = {}, useApi = false, started = false;
  function quiet(fn) { try { return fn(); } catch (e) { return null; } }
  KEYS.forEach(function (k) { var v = quiet(function () { return localStorage.getItem(k); }); if (typeof v === 'string') mem[k] = v; });
  function mt() { return window.xhs && window.xhs.miniTool; }
  function put(k, v) {
    if (useApi) { var p = quiet(function () { return mt().setStorage({ key: k, data: JSON.stringify(v) }); }); if (p && p.then) p.then(null, function () {}); }
    else quiet(function () { localStorage.setItem(k, v); });
  }
  window.__kv = {
    getItem: function (k) { return Object.prototype.hasOwnProperty.call(mem, k) ? mem[k] : null; },
    setItem: function (k, v) { v = String(v); mem[k] = v; put(k, v); }
  };
  function start() {
    if (started) return; started = true; var i = 0;
    (function next() { if (i >= APPS.length) return; var s = document.createElement('script'); s.src = APPS[i++]; s.onload = next; s.onerror = next; document.body.appendChild(s); })();
  }
  function build(lo) { var env = lo && lo.miniToolEnv; return Number(env && env.buildVersion) || 0; }
  function version() {
    var x = window.xhs, v = build(x && x.launchOptions);
    if (v) return Promise.resolve(v);
    var m = mt(); if (!m || typeof m.getLaunchOptions !== 'function') return Promise.resolve(0);
    return Promise.resolve(quiet(function () { return m.getLaunchOptions(); })).then(build, function () { return 0; });
  }
  setTimeout(start, 1500);      /* never let a slow container keep the game from starting */
  var vp = version(); window.__xhsBuild = vp;      /* the leaderboard (rank.js) checks the client version too */
  vp.then(function (v) {
    var m = mt();
    if (Math.floor(v / 1000) < 9460 || !m || typeof m.getStorage !== 'function' || typeof m.setStorage !== 'function') return;
    useApi = true;
    return Promise.all(KEYS.map(function (k) {
      return Promise.resolve(quiet(function () { return m.getStorage({ key: k }); })).then(function (r) {
        var s = r && typeof r.data === 'string' ? quiet(function () { return JSON.parse(r.data); }) : null;
        if (typeof s === 'string') mem[k] = s; else if (Object.prototype.hasOwnProperty.call(mem, k)) put(k, mem[k]);      /* carry an older localStorage value across */
      }, function () { if (Object.prototype.hasOwnProperty.call(mem, k)) put(k, mem[k]); });
    }));
  }).then(start, start);
})();
""" % json.dumps(KEYS)

shutil.rmtree(STAGE, ignore_errors=True); os.makedirs(STAGE)
open(os.path.join(STAGE, 'index.html'), 'w', encoding='utf-8').write(html)
open(os.path.join(STAGE, 'boot.js'), 'w', encoding='utf-8').write(BOOT)
for k, js in enumerate(scripts):
    raw = os.path.join(STAGE, f'.raw{k + 1}.js'); open(raw, 'w', encoding='utf-8').write(js)
    r = subprocess.run(['npx', '--yes', ESBUILD, raw, '--target=es2017,chrome61', '--charset=utf8', '--legal-comments=none', '--minify-whitespace', f'--outfile={os.path.join(STAGE, f"app{k + 1}.js")}'], capture_output=True, text=True)
    must(r.returncode == 0, f'esbuild app{k + 1}: {r.stderr[-800:]}'); os.remove(raw)
rank = open(os.path.join(ROOT, 'tools', 'xhs_rank.js'), encoding='utf-8').read()      # the leaderboard, written in ES5
open(os.path.join(STAGE, 'rank.js'), 'w', encoding='utf-8').write(('window.__xhsRankDebug = true;\n' if DEBUG else '') + rank)
for f in ['boot.js', 'app1.js', 'app2.js', 'app3.js', 'rank.js']:      # the Chrome 61 gate: every script must parse as ES2017
    r = subprocess.run(['npx', '--yes', '-p', ACORN, 'acorn', '--ecma2017', '--silent', os.path.join(STAGE, f)], capture_output=True, text=True)
    must(r.returncode == 0, f'{f} is not ES2017: {r.stderr[-600:] or r.stdout[-600:]}')
    body = open(os.path.join(STAGE, f), encoding='utf-8').read()
    for bad in ['eval(', 'new Function', 'WebAssembly', 'fetch(', 'XMLHttpRequest', 'new Worker', 'window.open', 'localStorage.getItem(\'', 'import(']:
        must(bad not in body or (f == 'boot.js' and bad.startswith('localStorage')), f'{f}: forbidden {bad}')

os.makedirs(os.path.dirname(OUT_ZIP), exist_ok=True)
if os.path.exists(OUT_ZIP): os.remove(OUT_ZIP)
with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:      # the files themselves at the root, not the folder
    for f in ['index.html', 'boot.js', 'app1.js', 'app2.js', 'app3.js', 'rank.js']: z.write(os.path.join(STAGE, f), f)
print(OUT_ZIP, os.path.getsize(OUT_ZIP), 'bytes')
