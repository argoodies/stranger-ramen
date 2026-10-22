#!/usr/bin/env python3
"""Build deploy/3b.html: the three-player game from the clock tower, on its own.

It is index.html with a small script added at the end that skips the title and the town,
goes straight into the tower's game (its music and sounds as they are), and starts a
new game whenever one ends instead of leaving the tower. Served at /3b.
usage: tools/mk3b.py
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
boot = """<script>
// /3b: only the three-player game in the clock tower, round after round
(() => {
  let last = performance.now();
  updateTower = () => {};      // no tower room, no keeper, no view from the top
  drawTowerRoom = T => { const now = performance.now(), dt = Math.min(.05, (now - last) / 1000); last = now; drawBotc(T, dt); };      // the tower is the game table
  towerTap = (x, y) => botcTap(x, y);
  leaveTower = () => { fade = 1; BG.dark = 0; bell(146.8, .12); playBotc(); };      // a game over: straight into the next one
  const go = () => { $('title').style.display = 'none'; for (const id of ['zoom', 'leave', 'enter', 'lang']) { const el = $(id); if (el) el.style.display = 'none'; }
    mode = 'tower'; tw.view = null; fade = 1; BG.dark = 0; playBotc(); };
  if (!location.hash) setTimeout(go, 0);
})();
</script>
"""
i = src.rfind('</body>')
out = src[:i] + boot + src[i:] if i >= 0 else src + boot
out = out.replace('<title>', '<title>三人染 · ', 1) if '<title>' in out else out
open(os.path.join(ROOT, 'deploy', '3b.html'), 'w', encoding='utf-8').write(out)
print('deploy/3b.html', len(out), 'bytes')
