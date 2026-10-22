#!/usr/bin/env python3
"""Build deploy/3b.html: the three-player game from the clock tower, on its own.

It is index.html with a small script added at the end that skips the title and the town,
opens on a quiet lobby at the tower's table (you and the Storyteller; tap to stroll, tap him to
start; the language button top right; 小染书 always in simplified characters), plays the tower's game with its music and sounds, and fades back to the lobby when it ends. Served at /3b.
usage: tools/mk3b.py
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
boot = """<script>
// /3b: only the three-player game in the clock tower. Between games the table is a quiet lobby in daylight: just you and the
// Storyteller; tap the table to stroll about it, tap the Storyteller to talk, and the game begins in the night. When it is over
// the picture fades back to the lobby.
(() => {
  const L3 = { hans: ['我们开始吧。'], hant: ['我們開始吧。'], en: ["Let's begin."] }, say3 = () => (L3[LANG] || L3.hans)[0];
  const me = { x: 3 * Math.cos(Math.PI / 4), y: 3 * Math.sin(Math.PI / 4), tx: 0, ty: 0, hop: 0, talk: false, say: null }; me.tx = me.x; me.ty = me.y;
  let lobby = true, tr = null, last = performance.now(), lv = null;      // tr: a fade to black, then a change of scene
  const view = () => { const s = Math.min(W / 11.2, (H - 250) / 8.6); return new View(W / 2, H * .6, s); };
  const ring = (x, y) => { const r = Math.hypot(x, y) || 1, rr = clamp(r, 1.35, 3.85); return [x / r * rr, y / r * rr]; };      // off the Storyteller's dais, inside the rim
  // ---- 小染书: a red capsule beside the Storyteller in the lobby; tapped, it tells you about the three roles itself in one bubble, a token for each name
  const KIDF = '"HanziPen SC","Hannotate SC","Wawati SC","Yuanti SC","YouYuan","幼圆","Comic Sans MS","Chalkboard SE",' + THINF;      // the most childlike hand the device has
  const RB = {      // ability texts: the wording of MELO's 三人血染 script
    hans: { title: '小染书', btn: '小染书', team: { sailor: '镇民 · 善良', pukka: '恶魔 · 邪恶', heretic: '外来者 · 善良' }, name: { sailor: '水手', pukka: '普卡', heretic: '异端分子' },
      abil: { sailor: '每个夜晚，你要选择一名存活的玩家：你或他之一会醉酒直到下个黄昏。你不会死亡。', heretic: '反转善良邪恶的胜负条件，即使你已死亡。', pukka: '每个夜晚，你要选择一名玩家：他中毒。上个因你的能力中毒的玩家会死亡并恢复健康。' } },
    hant: { title: '小染書', btn: '小染书', team: { sailor: '鎮民 · 善良', pukka: '惡魔 · 邪惡', heretic: '外來者 · 善良' }, name: { sailor: '水手', pukka: '普卡', heretic: '異端分子' },
      abil: { sailor: '每個夜晚，你要選擇一名存活的玩家：你或他之一會醉酒直到下個黃昏。你不會死亡。', heretic: '反轉善良邪惡的勝負條件，即使你已死亡。', pukka: '每個夜晚，你要選擇一名玩家：他中毒。上個因你的能力中毒的玩家會死亡並恢復健康。' } },
    en: { title: 'Rule Book', btn: '小染书', team: { sailor: 'Townsfolk · Good', pukka: 'Demon · Evil', heretic: 'Outsider · Good' }, name: { sailor: 'Sailor', pukka: 'Pukka', heretic: 'Heretic' },
      abil: { sailor: 'Each night, choose an alive player: either you or they are drunk until dusk. You can’t die.', heretic: 'Whoever wins, loses & whoever loses, wins, even if you are dead.', pukka: 'Each night, choose a player: they are poisoned. The previously poisoned player dies then becomes healthy.' } } };
  const rb = () => RB[LANG] || RB.hans;
  let bookAt = null;
  let intro = null;      // 小染书 telling you about the roles, all in one bubble: Sailor, Heretic, Pukka
  const INTRO = ['sailor', 'heretic', 'pukka'];
  function drawBook(t, P, s) {      // a red capsule where the grimoire lies in the game, just right of the Storyteller: 小染书, straight, in white
    const q = P(1.1, -.62, 2.0), w = s * 1.2, h = s * .44, x = q[0], y = q[1] + Math.sin(t * 1.6) * s * .06;
    ctx.fillStyle = css([210, 48, 58]); rrect(x - w / 2, y - h / 2, w, h, h / 2); ctx.fill();
    const T = rb().btn, fs = T.length > 3 ? s * .22 : s * .27; ctx.font = `600 ${fs}px ${KIDF}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#fff';
    ctx.textBaseline = 'alphabetic'; const m = ctx.measureText(T), ty = y + (m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) / 2;      // centred on the ink itself, whatever the font's own metrics
    ctx.lineJoin = 'round'; ctx.lineWidth = fs * .04; ctx.strokeStyle = '#fff'; ctx.strokeText(T, x, ty); ctx.fillText(T, x, ty);
    if (!intro) { const yy = y - h * .5 - s * .32 - Math.abs(Math.sin(t * 3 + 1)) * s * .1, r = s * .1; glow(x, yy, r * 4, [255, 236, 170], .7); poly([[x, yy - r * 1.3], [x + r, yy], [x, yy + r * 1.3], [x - r, yy]], [255, 236, 170]); }      // a bright diamond bobbing over it too, like the one over the Storyteller: tap me
    bookAt = [x, y, x - w * .62, x + w * 1.05, y - h * .5 - s * .8, y + h * .5 + s * .85]; }      // where a tap counts: well past the capsule to the right, up over its diamond and a good way below; on the left only just past its end, so a tap by the Storyteller still reaches him
  function tokenBubble(x, topY, al) {      // one speech bubble with all three roles in turn (Sailor, Heretic, Pukka): each a token where its name would be, then what it does
    const fs = clamp(W * .036, 12.5, 15), R = fs * 1.3, pad = 12, gap = 10, rowGap = 10, cw = Math.min(W - 16, 340), maxw = cw - pad * 2 - R * 2 - gap, lh = fs * 1.38; ctx.font = FONT(fs, true);
    const rows = INTRO.map(id => { const lines = wrapText(rb().abil[id], maxw); return { id, lines, h: Math.max(lines.length * lh, R * 2) }; });
    const bh = pad * 2 + rows.reduce((a, r) => a + r.h, 0) + rowGap * (rows.length - 1), bx = clamp(x - cw / 2, 8, W - cw - 8), by = Math.max(8, topY - bh - 8), tx = clamp(x, bx + 17, bx + cw - 17);
    ctx.fillStyle = css([250, 246, 238], .97 * al); rrect(bx, by, cw, bh, 11); ctx.moveTo(tx + 6, by + bh - 3); ctx.lineTo(tx, by + bh + 8); ctx.lineTo(tx - 6, by + bh - 3); ctx.closePath(); ctx.fill('nonzero');
    let yy = by + pad; for (const r of rows) { ctx.save(); ctx.globalAlpha *= al; roleToken(bx + pad + R, yy + r.h / 2, R, r.id); ctx.restore();
      const ty0 = yy + r.h / 2 - r.lines.length * lh / 2; r.lines.forEach((l, k) => text(l, bx + pad + R * 2 + gap, ty0 + lh * (k + .5), fs, [50, 36, 70], al, 'left', true)); yy += r.h + rowGap; } }
  function drawLobby(t, dt) {
    BG.dark = lerp(BG.dark, 0, 1 - Math.pow(.03, dt)); const g = BG; TINT = [30, 30, 90]; TK = lerp(.04, .34, g.dark); SHADOW = [58, 40, 96];
    drawSky(mix(SKYD[0], SKYN[0], g.dark), mix(SKYD[1], SKYN[1], g.dark), mix(SKYD[2], SKYN[2], g.dark), t, .1 + .9 * g.dark);
    const mx = W * .8, my = H * .14, sc = mix([255, 216, 150], [252, 244, 220], g.dark); glow(mx, my, 130, sc, .45); circ(mx, my, 22, sc);
    const v = lv = view(), s = v.s, P = v.P.bind(v), top = [92, 168, 162], under = [70, 96, 130], K = s * 1.25;
    v.disc(0, 0, -3.6, 1.1, 1.1, under); v.disc(0, 0, -2.5, 2.3, .9, under); v.disc(0, 0, -1.6, 3.4, 1.0, mix(under, top, .3)); v.disc(0, 0, -.6, 4.3, .6, top); v.disc(0, 0, 0, 2.3, 0, [120, 190, 180]);
    for (let i = 0; i < 12; i++) { const q = TAU * i / 12; line([P(3.95 * Math.cos(q), 3.95 * Math.sin(q)), P(4.18 * Math.cos(q), 4.18 * Math.sin(q))], tint(mix(top, [255, 255, 255], .6)), s * .07); }
    // walking: straight to where you tapped, at a stroll, with a little hop
    const dx = me.tx - me.x, dy = me.ty - me.y, d = Math.hypot(dx, dy), moving = d > .03;
    if (moving) { const st = Math.min(d, 2.6 * dt); me.x += dx / d * st; me.y += dy / d * st; { const r = Math.hypot(me.x, me.y); if (r < 1.35) { const q = Math.atan2(me.y, me.x) + Math.sign(dx * me.y - dy * me.x || 1) * -.06; me.x = Math.cos(q) * 1.35; me.y = Math.sin(q) * 1.35; } }      // the Storyteller's dais is solid: pushed out to its edge and a little round it, so a walk across slides round the dais
      me.hop += dt; if ((me.step = (me.step || 0) + dt) > .3) { me.step = 0; chime(pick([62, 65, 69]) + 12, 0, .03, .5); } }
    else if (me.talk) { me.talk = false; me.say = { t: 0 }; chime(74, 0, .16, 1.4); chime(81, .1, .14, 1.4); }
    if (me.say && (me.say.t += dt) > 1.5 && !tr) { tr = { t: 0, to: 'game' }; }
    if (moving && !me.talk) { const q = P(me.tx, me.ty); ell(q[0], q[1], s * .26 * 1.25, s * .13 * 1.25, [255, 240, 200], .4); }      // where you are walking to: a ring on the ground
    const pulse = .5 + .5 * Math.sin(t * 5), drawSt = () => { v.disc(0, 0, 0, .95, .3, [240, 220, 190]); const p = P(0, 0, .3);
        if (!me.say && !me.talk && !intro) { ctx.beginPath(); ctx.ellipse(p[0], p[1], s * .9, s * .45, 0, 0, TAU); ctx.strokeStyle = css([255, 236, 170], .35 + .35 * pulse); ctx.lineWidth = 2.5; ctx.stroke(); }      // he is waiting for you
        glow(p[0], p[1] - K * .8, K * 1.4, [200, 170, 255], .3); fig(p[0], p[1], K * 1.2, { kind: 'teller', body: [132, 100, 172], hat: [70, 52, 100] }); lv.st = [p[0], p[1] - K * .8, K * .95];      // no grimoire beside him while you stroll: the 小染书 capsule lies there instead
        if (!me.say && !me.talk && !intro) { const yy = p[1] - K * 1.2 * 1.75 - Math.abs(Math.sin(t * 3)) * s * .14, r = s * .13; glow(p[0], yy, r * 4, [255, 236, 170], .7); poly([[p[0], yy - r * 1.3], [p[0] + r, yy], [p[0], yy + r * 1.3], [p[0] - r, yy]], [255, 236, 170]); } },      // a bright diamond bobbing over his head: talk to him
      drawMe = () => { const p = P(me.x, me.y), y = p[1] - (moving ? Math.abs(Math.sin(me.hop * 9)) * s * .12 : 0); glow(p[0], y - K * .6, K * 1.2, [255, 240, 200], .3); fig(p[0], y, K, BLOOK[0]); };
    if (me.x + me.y < 0) { drawMe(); drawSt(); } else { drawSt(); drawMe(); }      // whoever is nearer is drawn last
    if (!me.say && !me.talk) drawBook(t, P, s); else bookAt = null;      // 小染书, beside the Storyteller while you stroll
    if (intro && bookAt) { intro.t += dt; tokenBubble(bookAt[0], bookAt[1] - s * .26, clamp(intro.t * 4)); }      // 小染书 itself tells you the roles, all in one bubble, its tail on the capsule
    if (me.say) { const p = P(0, 0, .3); sayBubble(p[0], p[1] - K * 1.6 * 1.2, say3(), clamp(W * .036, 12.5, 15), clamp(me.say.t * 4), W * .62); }
  }
  updateTower = () => {};      // no tower room, no keeper, no view from the top
  drawTowerRoom = T => { const now = performance.now(), dt = Math.min(.05, (now - last) / 1000); last = now;
    window.__3bLang = lobby && !tr;      // the language button, top right, while the lobby is up
    if (lobby) drawLobby(T, dt); else drawBotc(T, dt);
    if (tr) { tr.t += dt; ctx.fillStyle = css([6, 4, 16], clamp(tr.t / .7)); ctx.fillRect(0, 0, W, H);      // down to black, then the other scene
      if (tr.t >= .75) { const to = tr.to; tr = null; fade = 1.2;
        if (to === 'game') { lobby = false; me.say = null; BG.dark = 1; bell(146.8, .12); playBotc(); BG.isNight = true; }      // the night, and everyone at the table: the game begins
        else { lobby = true; BG.bubble = null; BG.wait = null; BG.isNight = false; BG.dark = 1; me.x = me.tx = 3 * Math.cos(Math.PI / 4); me.y = me.ty = 3 * Math.sin(Math.PI / 4); } } } };      // back to the quiet table, at your seat
  towerTap = (x, y) => { if (tr) return; if (!lobby) return botcTap(x, y); if (me.say || me.talk || !lv) return;
    if (intro) { if (intro.t > .25) { intro = null; chime(pick([69, 74, 76]), 0, .07, .6); } return; }      // a tap and he is done
    if (bookAt && x > bookAt[2] && x < bookAt[3] && y > bookAt[4] && y < bookAt[5]) { intro = { i: 0, t: 0 }; chime(74, 0, .12, 1); chime(79, .1, .1, 1); return; }      // 小染书: it tells you about the roles
    const st = lv.st; if (st && Math.hypot(x - st[0], y - st[1]) < st[2]) { const r = Math.hypot(me.x, me.y) || 1; me.tx = me.x / r * 1.45; me.ty = me.y / r * 1.45; me.talk = true; chime(69, 0, .07, .8); return; }      // to the Storyteller, to talk
    const [gx, gy] = lv.inv(x, y), [rx, ry] = ring(gx, gy); me.tx = rx; me.ty = ry; chime(69, 0, .07, .8); };      // a stroll about the table
  leaveTower = () => { if (!tr) tr = { t: 0, to: 'lobby' }; };      // a game over: fade back to the lobby
  const go = () => { $('title').style.display = 'none'; for (const id of ['zoom', 'leave', 'enter']) { const el = $(id); if (el) el.style.display = 'none'; }
    mode = 'tower'; tw.view = null; fade = 1; BG.dark = 0; BG.isNight = false; };
  if (!location.hash) setTimeout(go, 0);
  window.__3b = { me, get lobby() { return lobby; }, get tr() { return tr; }, get book() { return bookAt; }, get intro() { return intro; } };      // for tests
})();
</script>
"""
LANG_SHOW = "const show = mode === 'title' || (mode === 'world' && zoomTarget > .5)"
assert src.count(LANG_SHOW) == 1, 'language-button rule not found in index.html'
src = src.replace(LANG_SHOW, LANG_SHOW + ' || !!window.__3bLang', 1)      # /3b: the language button also shows in its lobby
i = src.rfind('</body>')
out = src[:i] + boot + src[i:] if i >= 0 else src + boot
out = out.replace('<title>', '<title>三人染 · ', 1) if '<title>' in out else out
open(os.path.join(ROOT, 'deploy', '3b.html'), 'w', encoding='utf-8').write(out)
print('deploy/3b.html', len(out), 'bytes')
