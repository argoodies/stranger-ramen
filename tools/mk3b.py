#!/usr/bin/env python3
"""Build deploy/3b.html: the three-player game from the clock tower, on its own.

It is index.html with a small script added at the end that skips the title and the town,
opens on a quiet lobby at the tower's table (you and the Storyteller; tap to stroll, tap him to
start), plays the tower's game with its music and sounds, and fades back to the lobby when it ends. Served at /3b.
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
  // ---- the little red book: floating high over the table in the lobby; tapped, it opens a page with the three roles' rules
  const KIDF = '"HanziPen SC","Hannotate SC","Wawati SC","Yuanti SC","YouYuan","幼圆","Comic Sans MS","Chalkboard SE",' + THINF;      // the most childlike hand the device has
  const RB = {
    hans: { title: '小红本', team: { sailor: '镇民 · 善良', pukka: '恶魔 · 邪恶', heretic: '外来者 · 善良' }, name: { sailor: '水手', pukka: '普卡', heretic: '异端分子' },
      abil: ABIL, how: ['三个人，水手、普卡、异端分子各一名。你只知道自己的角色。', '夜晚：水手先行动，然后是普卡。', '白天：只有你可以提名一个人，大家举手投票，票数够了就处决。', '普卡死了，善良获胜；只剩两个人活着，邪恶获胜。', '异端分子没醉也没中毒时，结果会反过来。'], howT: '怎么玩' },
    hant: { title: '小紅本', team: { sailor: '鎮民 · 善良', pukka: '惡魔 · 邪惡', heretic: '外來者 · 善良' }, name: { sailor: '水手', pukka: '普卡', heretic: '異端分子' },
      abil: { sailor: '每個夜晚，你要選一名存活的玩家：你和他之中，有一人會醉酒到下個黃昏。只要你清醒，你就不會死。', pukka: '你是惡魔。每個夜晚，你要選一名玩家：他中毒。上一個因你中毒的人會在這時死去，然後恢復健康。', heretic: '只要你沒有醉酒或中毒，這一局贏的算輸、輸的算贏——哪怕你已經死了。' },
      how: ['三個人，水手、普卡、異端分子各一名。你只知道自己的角色。', '夜晚：水手先行動，然後是普卡。', '白天：只有你可以提名一個人，大家舉手投票，票數夠了就處決。', '普卡死了，善良獲勝；只剩兩個人活著，邪惡獲勝。', '異端分子沒醉也沒中毒時，結果會反過來。'], howT: '怎麼玩' },
    en: { title: 'Little Red Book', team: { sailor: 'Townsfolk · Good', pukka: 'Demon · Evil', heretic: 'Outsider · Good' }, name: { sailor: 'Sailor', pukka: 'Pukka', heretic: 'Heretic' },
      abil: { sailor: 'Each night, choose an alive player: either you or they are drunk until dusk. You can’t die while you are sober.', pukka: 'You are the Demon. Each night, choose a player: they are poisoned. The previously poisoned player dies, then becomes healthy.', heretic: 'Whoever wins, loses, and whoever loses, wins — even if you are dead (unless you are drunk or poisoned).' },
      how: ['Three players: one Sailor, one Pukka, one Heretic. You only know your own role.', 'At night the Sailor acts first, then the Pukka.', 'By day only you may nominate; everyone votes by raising a hand, and enough votes means an execution.', 'If the Pukka dies, Good wins; if only two players are left alive, Evil wins.', 'While the Heretic is neither drunk nor poisoned, the result is turned around.'], howT: 'How to play' } };
  const rb = () => RB[LANG] || RB.hans;
  let bookAt = null;
  function drawBook(t, P, s) {      // a closed red book standing in the air above the middle of the table, gently bobbing, its title in white
    const q = P(0, 0, 6.4), w = s * 1.5, h = s * 1.95, x = q[0] - w / 2, y = q[1] - h / 2 + Math.sin(t * 1.7) * s * .12, tilt = Math.sin(t * 1.1) * .04;
    ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.rotate(tilt); ctx.translate(-w / 2, -h / 2);
    glow(w / 2, h / 2, w * 1.3, [255, 220, 210], .35);
    ctx.fillStyle = css([246, 238, 226]); rrect(w * .1, h * .05, w * .94, h * .97, s * .08); ctx.fill();      // the pages, peeking out at the side and the foot
    ctx.fillStyle = css([200, 44, 52]); rrect(0, 0, w * .96, h * .96, s * .1); ctx.fill();      // the red cover
    ctx.fillStyle = css([158, 28, 40]); rrect(0, 0, w * .16, h * .96, s * .1); ctx.fill();      // the spine
    ctx.strokeStyle = css([255, 214, 140], .7); ctx.lineWidth = Math.max(1, s * .03); ctx.strokeRect(w * .25, h * .1, w * .62, h * .76);      // a thin gold border
    const chars = [...rb().title], en = chars.length > 3, fs = en ? s * .3 : s * .42;
    ctx.font = `700 ${fs}px ${KIDF}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#fff';
    if (en) { const words = rb().title.split(' '); words.forEach((wd, k) => { ctx.save(); ctx.translate(w * .56, h * (.32 + k * .2)); ctx.rotate((k % 2 ? 1 : -1) * .06); ctx.fillText(wd, 0, 0); ctx.restore(); }); }
    else chars.forEach((ch, k) => { ctx.save(); ctx.translate(w * .56 + (k === 1 ? s * .05 : -s * .03), h * (.27 + k * .22)); ctx.rotate([-.12, .09, -.05][k] || 0); ctx.fillText(ch, 0, 0); ctx.restore(); });      // the three characters stacked down the cover, each a little crooked, as a child writes
    ctx.restore(); bookAt = [q[0], y + h / 2, Math.max(w, h) * .65]; }
  function openBook() {      // the page about the three roles; the cross at the top right closes it
    if (document.getElementById('rb3')) return; const R = rb(), d = document.createElement('div'); d.id = 'rb3';
    d.style.cssText = 'position:fixed;inset:0;z-index:1000;background:rgba(10,8,30,.55);display:flex;align-items:center;justify-content:center;padding:14px';
    const card = document.createElement('div'); card.style.cssText = `position:relative;background:#fbf4e8;color:#3a2a44;border-radius:16px;max-width:380px;width:100%;max-height:86vh;overflow:auto;padding:20px 18px 18px;font:15px/1.55 ${THINF};box-shadow:0 10px 40px rgba(0,0,0,.35)`; d.appendChild(card);
    const x = document.createElement('button'); x.setAttribute('aria-label', 'close'); x.style.cssText = 'position:absolute;top:10px;right:10px;width:34px;height:34px;border-radius:50%;border:0;background:rgba(58,42,68,.1);color:#3a2a44;display:flex;align-items:center;justify-content:center;padding:0';
    x.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 4l8 8M12 4l-8 8"/></svg>'; x.onclick = () => { d.remove(); chime(62, 0, .08, .6); }; card.appendChild(x);
    const h = document.createElement('div'); h.textContent = R.title; h.style.cssText = `font:700 24px ${KIDF};color:#c82c34;margin:0 40px 12px 2px`; card.appendChild(h);
    for (const id of ['sailor', 'pukka', 'heretic']) { const row = document.createElement('div'); row.style.cssText = 'display:flex;gap:12px;align-items:flex-start;margin:10px 0';
      const cv2 = document.createElement('canvas'), RR = 2; cv2.width = cv2.height = 56 * RR; cv2.style.cssText = 'position:static;display:block;width:56px;height:56px;flex:none'; const real = ctx; ctx = cv2.getContext('2d'); ctx.scale(RR, RR); try { roleToken(28, 28, 24, id); } finally { ctx = real; } row.appendChild(cv2);
      const tx = document.createElement('div'); tx.innerHTML = `<div style="font-weight:600;font-size:16px">${R.name[id]} <span style="font-weight:400;font-size:12px;opacity:.6;margin-left:4px">${R.team[id]}</span></div><div>${R.abil[id]}</div>`; row.appendChild(tx); card.appendChild(row); }
    const ht = document.createElement('div'); ht.textContent = R.howT; ht.style.cssText = 'font-weight:600;font-size:16px;margin:16px 0 6px'; card.appendChild(ht);
    const ul = document.createElement('ul'); ul.style.cssText = 'margin:0;padding-left:20px'; for (const line of R.how) { const li = document.createElement('li'); li.textContent = line; li.style.margin = '3px 0'; ul.appendChild(li); } card.appendChild(ul);
    document.body.appendChild(d); chime(74, 0, .12, 1); chime(79, .1, .1, 1); }
  window.__rb3 = openBook;
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
        if (!me.say && !me.talk) { ctx.beginPath(); ctx.ellipse(p[0], p[1], s * .9, s * .45, 0, 0, TAU); ctx.strokeStyle = css([255, 236, 170], .35 + .35 * pulse); ctx.lineWidth = 2.5; ctx.stroke(); }      // he is waiting for you
        glow(p[0], p[1] - K * .8, K * 1.4, [200, 170, 255], .3); fig(p[0], p[1], K * 1.2, { kind: 'teller', body: [132, 100, 172], hat: [70, 52, 100] }); const bz = 1.9 + .08 * Math.sin(t * 1.6); v.box(.75, -.9, bz, .7, .55, .12, [72, 56, 104]); lv.st = [p[0], p[1] - K * .8, K * .95];
        if (!me.say && !me.talk) { const yy = p[1] - K * 1.2 * 1.75 - Math.abs(Math.sin(t * 3)) * s * .14, r = s * .13; glow(p[0], yy, r * 4, [255, 236, 170], .7); poly([[p[0], yy - r * 1.3], [p[0] + r, yy], [p[0], yy + r * 1.3], [p[0] - r, yy]], [255, 236, 170]); } },      // a bright diamond bobbing over his head: talk to him
      drawMe = () => { const p = P(me.x, me.y), y = p[1] - (moving ? Math.abs(Math.sin(me.hop * 9)) * s * .12 : 0); glow(p[0], y - K * .6, K * 1.2, [255, 240, 200], .3); fig(p[0], y, K, BLOOK[0]); };
    if (me.x + me.y < 0) { drawMe(); drawSt(); } else { drawSt(); drawMe(); }      // whoever is nearer is drawn last
    if (!me.say && !me.talk) drawBook(t, P, s); else bookAt = null;      // the little red book, up in the air while you stroll
    if (me.say) { const p = P(0, 0, .3); sayBubble(p[0], p[1] - K * 1.6 * 1.2, say3(), clamp(W * .036, 12.5, 15), clamp(me.say.t * 4), W * .62); }
  }
  updateTower = () => {};      // no tower room, no keeper, no view from the top
  drawTowerRoom = T => { const now = performance.now(), dt = Math.min(.05, (now - last) / 1000); last = now;
    if (lobby) drawLobby(T, dt); else drawBotc(T, dt);
    if (tr) { tr.t += dt; ctx.fillStyle = css([6, 4, 16], clamp(tr.t / .7)); ctx.fillRect(0, 0, W, H);      // down to black, then the other scene
      if (tr.t >= .75) { const to = tr.to; tr = null; fade = 1.2;
        if (to === 'game') { lobby = false; me.say = null; BG.dark = 1; bell(146.8, .12); playBotc(); BG.isNight = true; }      // the night, and everyone at the table: the game begins
        else { lobby = true; BG.bubble = null; BG.wait = null; BG.isNight = false; BG.dark = 1; me.x = me.tx = 3 * Math.cos(Math.PI / 4); me.y = me.ty = 3 * Math.sin(Math.PI / 4); } } } };      // back to the quiet table, at your seat
  towerTap = (x, y) => { if (tr) return; if (!lobby) return botcTap(x, y); if (me.say || me.talk || !lv) return;
    if (bookAt && Math.hypot(x - bookAt[0], y - bookAt[1]) < bookAt[2]) return openBook();      // the little red book
    const st = lv.st; if (st && Math.hypot(x - st[0], y - st[1]) < st[2]) { const r = Math.hypot(me.x, me.y) || 1; me.tx = me.x / r * 1.45; me.ty = me.y / r * 1.45; me.talk = true; chime(69, 0, .07, .8); return; }      // to the Storyteller, to talk
    const [gx, gy] = lv.inv(x, y), [rx, ry] = ring(gx, gy); me.tx = rx; me.ty = ry; chime(69, 0, .07, .8); };      // a stroll about the table
  leaveTower = () => { if (!tr) tr = { t: 0, to: 'lobby' }; };      // a game over: fade back to the lobby
  const go = () => { $('title').style.display = 'none'; for (const id of ['zoom', 'leave', 'enter', 'lang']) { const el = $(id); if (el) el.style.display = 'none'; }
    mode = 'tower'; tw.view = null; fade = 1; BG.dark = 0; BG.isNight = false; };
  if (!location.hash) setTimeout(go, 0);
  window.__3b = { me, get lobby() { return lobby; }, get tr() { return tr; }, get book() { return bookAt; } };      // for tests
})();
</script>
"""
i = src.rfind('</body>')
out = src[:i] + boot + src[i:] if i >= 0 else src + boot
out = out.replace('<title>', '<title>三人染 · ', 1) if '<title>' in out else out
open(os.path.join(ROOT, 'deploy', '3b.html'), 'w', encoding='utf-8').write(out)
print('deploy/3b.html', len(out), 'bytes')
