"""Build deploy/sdc.html: the game itself (index.html) with the church taken away, the clock tower made the way down to the Demon Cave, keyboard and
gamepad control, and its own save. The cave is tools/sdc_mod.js. usage: python3 tools/mksdc.py"""
import os, re
ROOT = os.path.join(os.path.dirname(__file__), '..')
s = open(f'{ROOT}/index.html').read(); mod = open(f'{ROOT}/tools/sdc_mod.js').read(); css = open(f'{ROOT}/tools/sdc_panels.css').read()
def rep(a, b, n=1):
    global s; assert s.count(a) >= 1, a[:70]; s = s.replace(a, b) if n == 0 else s.replace(a, b, n)
def dropline(start):      # remove the whole line beginning with this text
    global s; i = s.index(start); i = s.rfind('\n', 0, i) + 1; j = s.index('\n', i) + 1; s = s[:i] + s[j:]
rep("'ctramen_lang'", "'ctramen_sdc_lang'", 0); rep("'ctramen'", "'ctramen_sdc'", 0)      # its own save, the real game's stays untouched
for l in ["for (let i = 0; i < 4; i++) v.box(5.09 + i * .352", "v.box(6.5, -2, CDZ - .3", "objs.push({ k: 9.6 + CDX + CDY, d: () => drawChapel(v, t) });", "objs.push({ k: 8.8 + .3 + .5, d: () => { const x = 8.28"]: dropline(l)
i = s.index("    for (const [dz, w, h, c] of [[.18, .3, .34"); s = s[:i] + s[s.index('\n', i) + 1:]      # the second line of the church's potted cypress
rep("const onLand = (i, j) => (i >= -5 && i < 5 && j >= -5 && j < 5) || (j === 0 && (i === 5 || i === 6)) || (i >= 7 && i < 9 && j >= -2 && j < 1) || (j === 3 && i === 5);", "const onLand = (i, j) => (i >= -5 && i < 5 && j >= -5 && j < 5) || (j === 3 && i === 5);")      # no church, no bridge to it
rep("goIn = w => w === 'stall' ? enterStall() : w === 'tower' ? enterTower() :", "goIn = w => w === 'stall' ? enterStall() : w === 'tower' ? SDC.tower() :")
rep("if (!hideChef && !storyHook) objs.push({ k: player.x + player.y + 0.01, d: () => { const p = v.P(wx(player.x, player.y), player.y, wz(player.x, player.y)), hop = player.path.length ?", "SDC.worldObjs(objs, v, s); if (!hideChef && !storyHook) objs.push({ k: player.x + player.y + 0.01, d: () => { const p = v.P(wx(player.x, player.y), player.y, wz(player.x, player.y)), hop = player.path.length || player.moving ?")
rep("  if (mode === 'world' && d && !player.path.length) {", "  if (false && d) {")
rep("  if (mode === 'stall') { updateStall(dt); drawStall(T); }", "  SDC.poll(dt);\n  if (mode === 'cave') SDC.frame(dt, T);\n  else if (mode === 'stall') { updateStall(dt); drawStall(T); }")
rep("  if (fade > 0) { ctx.fillStyle = css([14, 12, 36], clamp(fade));", "  SDC.overlay();\n  if (fade > 0) { ctx.fillStyle = css([14, 12, 36], clamp(fade));")
html = '<div id="sdcHint"></div><div id="sdcRot">这个游戏用键盘或手柄玩<br>请接上手柄，或用电脑打开</div><div id="sdcPanel"><div class="in" id="sdcPin"></div></div>\n'
rep('<div id="err"></div>', '<div id="err"></div>\n' + html)
style = """<style>#lang,#langMenu,#bag,#bspeed,#bfreeze,#bclose,#zoom,#gear,#enter,#title{display:none!important}
#sdcHint{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(36px + env(safe-area-inset-bottom));padding:9px 18px;border-radius:22px;background:rgba(20,16,44,.72);border:1px solid rgba(255,255,255,.3);font-size:14px;color:#fff;display:none;white-space:nowrap;z-index:8}
#sdcRot{position:fixed;inset:0;display:none;align-items:center;justify-content:center;flex-direction:column;background:#1e1a44;color:#fff;font-size:16px;line-height:2;z-index:9;text-align:center}
""" + css + "#sdcPanel{z-index:7;color:#fff}.foc{outline:2px solid #ffe6a8;outline-offset:2px}</style>"
rep('</head>', style + '</head>')
# the game opens in the tavern, with no title screen
i = s.rindex('</script>')
s = s[:i] + mod + """
mode = 'world'; zoomTarget = 0; zoomOut = 0; titleK = 0; titleT0 = 2; enterBar();
if ('ontouchstart' in window && !location.search.includes('manual')) document.getElementById('sdcRot').style.display = 'flex';
addEventListener('keydown', () => { document.getElementById('sdcRot').style.display = 'none'; }, true);
""" + s[i:]
open(f'{ROOT}/deploy/sdc.html', 'w').write(s); print('deploy/sdc.html', len(s), 'bytes')
