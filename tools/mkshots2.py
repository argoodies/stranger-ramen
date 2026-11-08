#!/usr/bin/env python3
"""App Store screenshots (2026-10-24 set), five scenes staged on a copy of the game; index.html itself is not touched.
  1 the ramen shop: the chef lifts a finished bowl of beef noodles while the next noodles turn in the pot; the drunk at the counter orders in a few words
  2 the bar at night: a drink just set down by the chef, not yet drunk; the cat on the left says meow
  3 the library at night: the chef stands in the moonlight from the window, by the shelves, saying nothing
  4 the island at night, zoomed out, the chef before the clock tower; no "tap" hint
  5 the church, round two: the torch just lit, the chef a step in front of it, both whirlwinds there with their health bars
  6 the view from the top of the clock tower at night, the moment the shooting star crosses the sky
  7 ordinary play: the chef on the path in the town at night, close up, as in the game
usage: tools/mkshots2.py [langs] [iphone|ipad|both]     e.g. tools/mkshots2.py hans iphone
out: /dev/shm/botc/shots4/<locale>/iphone_N.png (1290x2796) and ipad_N.png (2048x2732)"""
import os, sys, subprocess
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HS = '/root/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'
OUT = '/dev/shm/botc/shots4'
LOC = {'hans': 'zh-Hans', 'hant': 'zh-Hant', 'en': 'en-US'}
COMMON = "window.requestAnimationFrame = (f) => setTimeout(() => f(performance.now()), 16); window.__noGeese = true;"
SCENES_ALL = {
 1: """setTimeout(() => { enterStall(); fade = 0; const want = { chili: false, cilantro: false, beef: true };      // the drunk orders a plain beef noodle, the shortest way he can say it
      let text = orderText(want); for (let k = 0; k < 80; k++) { const t2 = orderText(want); if (t2.length < text.length) text = t2; }
      stall.seats = [null, { look: { kind: 'drunk', body: [226, 212, 186], hat: [44, 40, 56], name: '酒鬼' }, want, text, state: 'wait', t: 9, wait: 0, say: '', dish: null }, null]; stall.spawn = 999;
      stall.bowl = Object.assign(emptyBowl(), { noodle: true, soup: true, beef: true }); stall.bowlAnim = {};
      Object.assign(stall.owner, { x: 2.44, y: 1.25, tx: 2.44, ty: 1.25, ptx: null, path: null }); setHold('bowl'); stall.pot = 'cooking'; stall.potT = .9; cookT = () => 99; }, 300);""",
 2: """setTimeout(() => { G.n = 1; G.t = HALF + 20; enterBar(); fade = 0; Object.assign(bar, { who: 'sailor', x: 2.5, y: 3.5, path: [] }); Object.assign(bar.cat, { x: .55, y: 2.3, tx: .55, ty: 2.3, sit: 999, face: 1 });
      setTimeout(() => { const k = BARHIT.keeper; if (k) cafeTap(k[0], k[1]); }, 300);
      setInterval(() => { bar.cat.meowT = 1.2; bar.cat.sit = 999; bar.keepSayT = bar.mySayT = bar.whoSayT = 0; }, 50); }, 300);""",
 3: """setTimeout(() => { G.n = 1; G.t = HALF + 20; enterLib(); fade = 0; Object.assign(lib, { x: 1.35, y: 1.75, path: [], say: '', sayT: 0 }); setInterval(() => { lib.sayT = 0; }, 50); }, 300);""",
 4: """setTimeout(() => { G.n = 1; G.t = HALF + 20; mode = 'world'; $('title').style.display = 'none'; zoomOut = zoomTarget = 1; fade = 0; tapHint = () => {}; { const st = document.createElement('style'); st.textContent = '#zoom,#lang,#enter{display:none!important}'; document.head.appendChild(st); } player.x = TDOOR[0] + .5; player.y = TDOOR[1] + 1.5; player.path = []; }, 300);""",
 5: """setTimeout(() => { save.knife = true; save.equip.weapon = 'knife'; enterChurch(); fade = 0; const c = church, p = c.p; c.tier = 2; p.x = p.tx = TORCH[0] + 1.0; p.y = p.ty = TORCH[1] + .35; c.cam = null; churchIgnite();
      setInterval(() => c.foes.forEach(f => { f.app = 0; f.cd = 99; f.wt = 99; f.wind = 0; }), 30); }, 300);""",
 7: """setTimeout(() => { G.n = 1; G.t = HALF + 20; mode = 'world'; $('title').style.display = 'none'; zoomOut = zoomTarget = 0; titleK = 0; fade = 0; tapHint = () => {}; worldHint = 0; player.x = -.5; player.y = 3.5; player.path = []; camX = player.x; camY = player.y; }, 300);""",
 6: """setTimeout(() => { G.n = 1; G.t = HALF + 20; $('title').style.display = 'none'; enterTower(); towerShow(); fade = 0; tapHint = () => {};
      Object.assign(tw.view, { kind: 'meteor', night: true, t: TSTAR + .47 }); updateTower = () => {};
      { const st = document.createElement('style'); st.textContent = '#zoom,#lang,#enter,#leave{display:none!important}'; document.head.appendChild(st); } }, 300);""",
}
# 2026-11-08 set, in store order: the quiet town as the game opens (its title over the island at night) first, the tower-top shooting star dropped
SCENES_ALL[0] = """setTimeout(() => { G.n = 1; G.t = HALF + 20; logoSteam = () => {}; { const st = document.createElement('style'); st.textContent = '#lang{display:none!important}'; document.head.appendChild(st); } }, 300);"""
ORDER = [0, 1, 2, 3, 5]      # scene numbers in the order they appear in the store (the zoomed-out island and the close-up town dropped too; the title without its steam); the files are numbered 1.. in this order
SCENES_ALL = {i + 1: SCENES_ALL[k] for i, k in enumerate(ORDER)}
ONLY = [int(x) for x in os.environ.get("ONLY", "").split(",") if x]
SCENES = {k: v for k, v in SCENES_ALL.items() if not ONLY or k in ONLY}
def page(n, lang):
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    src = src.replace("if (!storyRain) for (let i = 0; i < 3; i++) {", "if (!storyRain && !window.__noGeese) for (let i = 0; i < 3; i++) {", 1)
    src = src.replace("const cookT = () =>", "let cookT = () =>", 1)
    i = src.rfind('</body>'); p = f'/dev/shm/botc/shot{n}.html'
    open(p, 'w', encoding='utf-8').write(src[:i] + '<script>' + COMMON + SCENES_ALL[n] + '</script>' + src[i:]); return p
langs = (sys.argv[1] if len(sys.argv) > 1 else 'hans,hant,en').split(','); dev = sys.argv[2] if len(sys.argv) > 2 else 'both'
for lg in langs:
    d = f'{OUT}/{LOC[lg]}'; os.makedirs(d, exist_ok=True)
    for n in SCENES:
        p = page(n, lg)
        if dev in ('iphone', 'both'):
            subprocess.run([HS, '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--window-size=430,932', '--force-device-scale-factor=3', '--virtual-time-budget=7000', f'--screenshot={d}/iphone_{n}.png', f'file://{p}?lang={lg}'], capture_output=True, timeout=200)
            im = Image.open(f'{d}/iphone_{n}.png').convert('RGB'); assert im.size == (1290, 2796), im.size; im.save(f'{d}/iphone_{n}.png')
        if dev in ('ipad', 'both'):
            subprocess.run([HS, '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--window-size=1024,1366', '--force-device-scale-factor=1', '--virtual-time-budget=7000', f'--screenshot={d}/ipad_s{n}.png', f'file://{p}?lang={lg}'], capture_output=True, timeout=200)
            im = Image.open(f'{d}/ipad_s{n}.png').convert('RGB'); assert im.size == (1024, 1366), im.size; im.resize((2048, 2732), Image.LANCZOS).save(f'{d}/ipad_{n}.png'); os.remove(f'{d}/ipad_s{n}.png')
        print(lg, n, 'ok')
