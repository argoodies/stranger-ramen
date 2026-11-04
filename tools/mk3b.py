#!/usr/bin/env python3
"""Build deploy/3b.html (web, with a debug switch behind the sun) and deploy/3b-embed.html (the app and the Xiaohongshu package):
the three-player game from the clock tower, on its own.

It is index.html with tools/botc3.js (the three-player game, which the main game no longer has) and a small script added at the end that skips the title and the town,
opens on a quiet lobby at the tower's table (you and the Storyteller; tap to stroll, tap him to
start; the language button top right; 小染书 always in simplified characters), plays the tower's game with its music and sounds, and fades back to the lobby when it ends. Served at /3b.
usage: tools/mk3b.py
"""
import os
import re
def check_comments(code, where):      # a '//' comment runs to the end of its line: code put after one on the same line is silently lost (it has broken the game several times)
    for n, line in enumerate(code.split('\n'), 1):
        m = re.search(r'\S\s{2,}//', line)      # a comment after code on the same line (a whole-line comment is prose)
        if m and re.search(r'(\bif \(|\breturn\b|\bconst |\blet |\bfor \(|[a-zA-Z_]\w*\([^)]*\);\s*\S|\b[a-zA-Z_][\w.]*(?:\[[^\]]*\])?\s*(?:[-+*/]?=)\s*[^=;\n]+;)', line[m.end():]):      # also an assignment: x = ...; / x += ...;
            raise SystemExit(f'{where}:{n}: code after a // comment would be lost:\n  {line.strip()[:200]}')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
boot = """<script>
// /3b: only the three-player game in the clock tower. Between games the table is a quiet lobby in daylight: just you and the
// Storyteller; tap the table to stroll about it, tap the Storyteller to talk, and the game begins in the night. When it is over
// the picture fades back to the lobby.
(() => {
  // the language button on every platform (web, app, Xiaohongshu): Xiaohongshu's translate mark in a small black see-through circle,
  // two white rounded squares overlapping corner to corner, 文 upper left and A lower right drawn as strokes in see-through black
  // (centred whatever font the device has); a cut-out gap (a mask) keeps the squares apart. Each platform styles the menu itself.
  const MARK = '<svg width="14" height="14" viewBox="0 0 24 24"><defs><mask id="xlm"><rect width="24" height="24" fill="#fff"/><rect x="9.8" y="9.8" width="14.2" height="14.2" rx="3.6" fill="#000"/></mask></defs>' +
    '<rect x="1" y="1" width="12" height="12" rx="2.8" fill="#fff" mask="url(#xlm)"/><g fill="none" stroke="rgba(0,0,0,.55)" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3.5v1M3.9 5.2h6.2M9.2 5.5Q8.2 8.8 4 10.5M4.9 5.5Q6.2 8.8 10.2 10.5"/></g>' +
    '<rect x="11" y="11" width="12" height="12" rx="2.8" fill="#fff"/><g fill="none" stroke="rgba(0,0,0,.55)" stroke-width="1.05" stroke-linecap="round" stroke-linejoin="round"><path d="M14.3 20.2L17 13.8l2.7 6.4M15.35 18.1h3.3"/></g></svg>';
  const MARK_CSS = '#lang{position:relative;z-index:0;width:40px!important;height:40px!important;padding:0!important;border:0!important;border-radius:50%!important;background:transparent!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important;box-shadow:none!important;color:#fff!important;line-height:0}' +
    '#lang svg{display:block;margin:0 auto}#lang:active{opacity:.6}#lang::before{content:"";position:absolute;left:50%;top:50%;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;background:rgba(0,0,0,.35);z-index:-1}';
  const L3 = { hans: ['我们开始吧。'], hant: ['我們開始吧。'], en: ["Let's begin."] }, say3 = () => (L3[LANG] || L3.hans)[0];
  const me = { x: 3 * Math.cos(Math.PI / 4), y: 3 * Math.sin(Math.PI / 4), tx: 0, ty: 0, hop: 0, talk: false, say: null }; me.tx = me.x; me.ty = me.y;
  // a new language: the menu closes and you say so yourself, in the new language
  const SWITCHED = { hans: { hans: '已切换为简体中文', hant: '已切换为繁体中文', en: '已切换为英语', auto: '已切换为跟随系统' },
    hant: { hans: '已切換為簡體中文', hant: '已切換為繁體中文', en: '已切換為英語', auto: '已切換為跟隨系統' },
    en: { hans: 'Switched to Simplified Chinese', hant: 'Switched to Traditional Chinese', en: 'Switched to English', auto: 'Now following the system' } };
  document.getElementById('langMenu').querySelectorAll('button').forEach(b => b.addEventListener('click', () => { if (lobby && !tr) me.line = { text: (SWITCHED[LANG] || SWITCHED.en)[b.dataset.l], t: 0 }; }));
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
  let bookAt = null, markAt = null;
  // ---- your side has won: as the Storyteller says so, fireworks burst at the top of the picture and confetti drifts down over the table
  const CONF = [[226, 64, 78], [255, 196, 64], [86, 156, 236], [150, 104, 210], [250, 246, 238], [96, 196, 160]];
  let confetti = null, landed = [];      // landed: pieces lying on the table, [gx, gy, angle, colour, w, h], until the next game begins
  const tableView = () => { const s = Math.min(W / 11.2, (H - 250) / 8.6); return new View(W / 2, H * .6, s); };      // the lobby's and the game's own view of the table
  window.__confettiGo = () => {
    const parts = [], bursts = [];
    for (let b = 0; b < 1; b++) {      // one burst at the top middle of the picture
      const bx = W * .5 + (Math.random() - .5) * W * .06, by = H * .12 + (Math.random() - .5) * H * .02, at = b * .28, c = CONF[(b * 2) % CONF.length];
      bursts.push({ x: bx, y: by, at, c });
      const tv = tableView(), REACH = .181;      // how far the pop carries a piece sideways: its speed times this, with the air below
      for (let k = 0; k < 140; k++) {
        const q = Math.random() * TAU, rr = 1.15 + Math.sqrt(Math.random()) * 1.05, land = [Math.cos(q) * rr, Math.sin(q) * rr];      // its own spot on the light inner ring, off the Storyteller's dais
        const a = Math.random() * TAU, v = (.35 + Math.random() * .65) * Math.min(W, H) * 1.6;
        const vx = (tv.P(land[0], land[1])[0] - bx) / REACH;      // aimed: the pop leaves it right over its spot, so it only has to fall (no pull along the way)
        parts.push({ x: bx, y: by, vx, vy: Math.sin(a) * v * .85, at, c: pick(CONF), w: 3 + Math.random() * 4, h: 6 + Math.random() * 6, r: Math.random() * TAU, vr: (Math.random() - .5) * 12, ph: Math.random() * TAU, fall: .035 + Math.random() * .085, land }); }
    }
    confetti = { t: 0, parts, bursts }; landed = [];      // silent: the win music is playing
  };
  // drawn in depth with the people: each piece belongs to the spot on the table it is falling to (depth gx + gy, the same measure the
  // scene sorts its people by), so a piece behind someone goes behind them, in the air and on the table
  function stepConfetti(dt) {
    if (!confetti) return;
    const C = confetti; C.t += dt;
    const g = Math.min(W, H) * .45, tv = tableView();
    for (const p of C.parts) { if (C.t < p.at || p.done || p.gone) continue;
      const drag = Math.pow(C.t - p.at < .25 ? .0004 : .2, dt); p.vx *= drag;      // a sharp pop, stopped short by the air
      p.vy = Math.min(p.vy * drag + g * dt, Math.min(W, H) * p.fall);      // then a slow fall
      const to = tv.P(p.land[0], p.land[1]);
      p.ph += dt * 2.2; p.x += (p.vx + Math.sin(p.ph) * 16) * dt; p.y += p.vy * dt; p.r += p.vr * .6 * dt;      // swaying as it falls
      if (p.vy > 0 && p.y >= to[1]) { p.done = true; const gnd = tv.inv(p.x, p.y); landed.push([gnd[0], gnd[1], p.r, p.c, p.w, p.h]); continue; }      // it lies exactly where it came down (no jump)      // down on the table: it stays there
      if (p.y > H + 20) p.gone = true; }
    if (C.parts.every(p => p.done || p.gone) && C.t > 1) confetti = null;
  }
  window.__confLayer = (lo, hi) => {      // the pieces whose spot is in [lo, hi) of depth: lying on the table, then those still falling
    const tv = tableView(), inLayer = (gx, gy) => gx + gy >= lo && gx + gy < hi;
    for (const [gx, gy, a, c, w, h] of landed) { if (!inLayer(gx, gy)) continue; const q = tv.P(gx, gy); ctx.save(); ctx.translate(q[0], q[1]); ctx.scale(1, .5); ctx.rotate(a); ctx.fillStyle = css(c); ctx.fillRect(-w / 2, -h / 2, w, h); ctx.restore(); }      // lying flat: squashed like the table top, as bright as in the air
    if (!confetti) return;
    for (const p of confetti.parts) { if (confetti.t < p.at || p.done || p.gone || !inLayer(p.land[0], p.land[1])) continue;
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r); ctx.scale(1, Math.cos(p.ph * 1.3));      // turning over: it narrows and widens
      ctx.fillStyle = css(p.c); ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h); ctx.restore(); }
  };
  // when the last game was a win, where the platform has a scoreboard (window.__boardMark = { open }: the app's, with your Game Center rank, set in botc3.js;
  // the Xiaohongshu build, xhs_rank.js; on the web your own count), the book beside the Storyteller gives way to a small ball of frosted glass holding Game Center's
  // bubbles, floating in its place; a tap opens the scores.
  const BUBBLES = [[9, 13, 7.2, [142, 91, 234], .92], [14.5, 8.5, 5.6, [255, 59, 107], .9], [8, 6, 3.6, [255, 194, 26], .95], [16, 16, 4.6, [43, 196, 240], .9]];      // Game Center's mark, on a 24 grid
  // the bubbles' spin: a tap turns them once round in a second, fast at first and slowing gently back to where they started
  const spin = { tw: 0 }, SPIN = .8, LAG = .07;      // each bubble turns once in SPIN seconds, each starting LAG after the one before
  // the web has no scoreboard: its ball turns and says how many games you have won on this device (botc3.js keeps the count)
  const WEBSAY = { hans: '你赢了 {w} 局。', hant: '你贏了 {w} 局。', en: '{w} wins so far.' };
  const webMark = { open: () => setTimeout(() => window.__markSay(() => (WEBSAY[LANG] || WEBSAY.hans).replace('{w}', GCS.wins).replace(/^1 wins/, '1 win')), 1000) };
  let markLine = null;      // what the ball says (the Xiaohongshu build: your wins and rank), in a speech bubble over it for a few seconds
  window.__markSay = text => { markLine = { text, t: 0 }; };      // text: a string, or () => the words in the language of the moment
  window.__spinMark = () => { if (!spin.tw) spin.tw = 1e-6; };      // all four done in SPIN + 3 LAG, about a second
  function turn(dt) { if (!spin.tw) return; spin.tw += dt; if (spin.tw >= SPIN + 3 * LAG) spin.tw = 0; }
  const TURNS = [2, 1, 2, 1];      // two of the four go round twice
  const angleOf = i => { if (!spin.tw) return 0; const u = clamp((spin.tw - i * LAG) / SPIN); return TAU * TURNS[i] * (1 - Math.pow(1 - u, 3)); };      // fast, then slowing back to its place
  function drawMark(t, dt, P, s, bm) {      // small, floating where the book lay, in a ball of frosted glass: the table shows through it, blurred
    const a0 = ctx.globalAlpha; ctx.globalAlpha = a0 * ap(3);      // it comes in with the opening, when the book does
    const q = P(1.1, -.62, 2.0), R = Math.max(10, s * .3), x = q[0], y = q[1] - s * .12 + Math.sin(t * 1.6) * s * .03, k = R * 1.5 / 24;      // bobbing with the book's own beat
    const m = ctx.getTransform(), dx = m.a * x + m.e, dy = m.d * y + m.f, dr = m.a * R;      // in the canvas's own pixels
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.beginPath(); ctx.arc(dx, dy, dr, 0, TAU); ctx.clip();
    if ('filter' in ctx) { const pd = dr * 1.6; ctx.filter = 'blur(' + (dr * .22).toFixed(1) + 'px)'; ctx.drawImage(ctx.canvas, dx - pd, dy - pd, pd * 2, pd * 2, dx - pd, dy - pd, pd * 2, pd * 2); ctx.filter = 'none'; }      // what is behind it, blurred
    ctx.fillStyle = 'rgba(255,255,255,.38)'; ctx.fillRect(dx - dr, dy - dr, dr * 2, dr * 2); ctx.restore();      // a milky white over it
    ctx.beginPath(); ctx.arc(x, y, R - .5, 0, TAU); ctx.strokeStyle = 'rgba(255,255,255,.75)'; ctx.lineWidth = 1; ctx.stroke();      // its rim catching the light
    turn(dt);
    BUBBLES.forEach(([cx, cy, r, c, a], i) => {      // each bubble on its own: it drifts a little in the glass, out of step with the others, and turns round the middle in its own time
      const fx = Math.sin(t * (1.3 + i * .23) + i * 1.9) * .7, fy = Math.cos(t * (1.1 + i * .31) + i * 2.6) * .7;      // on the 24 grid
      const g = angleOf(i), cs = Math.cos(g), sn = Math.sin(g), u = (cx - 11.2 + fx) * k, v = (cy - 11.5 + fy) * k;
      const grow = 1 + .1 * Math.sin(t * (.7 + i * .17) + i * 3.1) + .06 * Math.sin(t * (1.9 + i * .29) + i * 1.3);      // swelling and shrinking slowly, unevenly, each to its own rhythm
      ctx.beginPath(); ctx.arc(x + u * cs - v * sn, y + u * sn + v * cs, r * k * grow, 0, TAU); ctx.fillStyle = css(c, a); ctx.fill(); });
    ctx.globalAlpha = a0; markAt = [x, y, Math.max(24, R * 2), bm, R]; bookAt = null;
    if (markLine && (markLine.t += dt) < 4) sayBubble(x, q[1] - s * .12 - R - s * .08, typeof markLine.text === 'function' ? markLine.text() : markLine.text, clamp(W * .036, 12.5, 15), clamp(markLine.t * 4) * clamp((4 - markLine.t) * 3), W * .82); else markLine = null;      // a finger-sized place to tap, bigger than the ball
  }
  let seenBook = false;
  let appear = { t: 0, said: 0 }, tableCv = null;      // the first entry: the table, the Storyteller, you, 小染书 and its sparkle fade in one after another, each with a sound; null once done
  // the opening's sounds, over the background music and nothing else, as in the Monument Valley 血染钟楼 video's opening (botc-video/make.py):
  // 咚 — a chime that climbs with each thing that appears (table 62, Storyteller 66, you 69); then 丁零定 for 小染书 — a quick, higher three-note bell
  // (74 78 81, 0.12 s apart, the video's sparkle); its diamond comes in silently
  const dong = m => () => chime(m, 0, .22, 1.6), dingLingDing = () => [74, 78, 81].forEach((m, j) => chime(m, .12 * j, .14, 1.6));
  const APPEAR = [[.5, dong(62)], [1.1, dong(66)], [1.7, dong(69)], [2.3, dingLingDing], [2.9, () => {}]], APPEAR_END = 3.5, APPEAR_TAP = 3.1;      // half a second of empty sky first
  const ap = k => appear ? clamp((appear.t - APPEAR[k][0]) / .55) : 1;      // how far in the k-th thing has faded      // this visit: until 小染书 has been read only it sparkles; after that the Storyteller does
  let intro = null;      // 小染书 telling you about the roles, all in one bubble: Sailor, Heretic, Pukka
  const INTRO = ['sailor', 'heretic', 'pukka'];
  function drawBook(t, P, s) {      // a red capsule where the grimoire lies in the game, just right of the Storyteller: 小染书, straight, in white
    const px = v => Math.round(v * DPR) / DPR, q = P(1.1, -.62, 2.0), w = s * 1.38, h = s * .5, x = px(q[0]), y = px(q[1]);      // still (no bob), on whole device pixels: the lettering stays crisp
    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.gc) {      // wherever Game Center is there (the app), in every language, no label: a stiff open book hanging in the air, a true 3D model seen square on from a little above; on the web always the red label
      let ox = 0, oy = 0; const W = s * .46, L = s * .56, T = s * .13, C = s * .07, Sp = s * .055, al = .42, yaw = 0, pit = .62, paper = [250, 246, 238], leafEdge = [222, 214, 214], board = [146, 118, 181], boardD = [120, 94, 156], ca = Math.cos(al), sa = Math.sin(al),
        P3 = (X, Y, Z) => { const x1 = X * Math.cos(yaw) + Z * Math.sin(yaw), z1 = Z * Math.cos(yaw); return [ox + x1, oy - (Y * Math.cos(pit) + z1 * Math.sin(pit))]; },      // X across, Y up, Z away from you; isometric like the rest of the game: no perspective, near and far edges the same length
        pt = (sg, u, h, z) => P3(sg * (Sp + u * ca - h * sa), u * sa + h * ca, z), u0 = (T * sa - Sp) / ca, ln = L * .44, lc = L * .5, wp = W * .87;
      { const qs = []; for (const sg of [-1, 1]) for (const z of [-lc, lc]) qs.push(pt(sg, W, 0, z), pt(sg, W, -C, z), pt(sg, wp, T, z), pt(sg, u0, T, z), pt(sg, 0, -C, z)); const ys = qs.map(q => q[1]); ox = x - pt(1, u0, T, ln)[0]; oy = y + Math.sin(t * 1.6) * s * .03 - (Math.min(...ys) + Math.max(...ys)) / 2; }      // up and down centred on the red label's spot; across, the top of the V sits right under the sparkle
      for (const sg of [-1, 1]) { poly([pt(sg, W, 0, -lc), pt(sg, W, 0, lc), pt(sg, W, -C, lc), pt(sg, W, -C, -lc)], boardD); poly([pt(sg, 0, 0, -lc), pt(sg, W, 0, -lc), pt(sg, W, 0, lc), pt(sg, 0, 0, lc)], board); poly([pt(sg, 0, 0, -lc), pt(sg, W, 0, -lc), pt(sg, W, -C, -lc), pt(sg, 0, -C, -lc)], boardD); }      // the covers, their near edges a shade darker
      poly([P3(-Sp, 0, -lc), P3(Sp, 0, -lc), P3(Sp, 0, lc), P3(-Sp, 0, lc)], board); poly([P3(-Sp, 0, -lc), P3(Sp, 0, -lc), P3(Sp + C * sa, -C * ca, -lc), P3(-Sp - C * sa, -C * ca, -lc)], boardD);      // the spine
      for (const sg of [-1, 1]) { poly([P3(0, 0, -ln), pt(sg, 0, 0, -ln), pt(sg, wp, 0, -ln), pt(sg, wp, T, -ln), pt(sg, u0, T, -ln)], leafEdge); poly([pt(sg, wp, 0, -ln), pt(sg, wp, 0, ln), pt(sg, wp, T, ln), pt(sg, wp, T, -ln)], leafEdge); }      // the pages' thickness
      for (const sg of [-1, 1]) poly([pt(sg, u0, T, -ln), pt(sg, wp, T, -ln), pt(sg, wp, T, ln), pt(sg, u0, T, ln)], paper);      // and their faces, one solid white
    } else {
      ctx.fillStyle = css([210, 48, 58]); rrect(x - w / 2, y - h / 2, w, h, h / 2); ctx.fill();
      const T = rb().btn, fs = T.length > 3 ? s * .25 : s * .31; ctx.font = `600 ${fs}px ${KIDF}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#fff';
      ctx.textBaseline = 'alphabetic'; const m = ctx.measureText(T), ty = px(y + (m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) / 2);      // centred on the ink itself, whatever the font's own metrics
      ctx.lineJoin = 'round'; ctx.lineWidth = fs * .04; ctx.strokeStyle = '#fff'; ctx.strokeText(T, x, ty); ctx.fillText(T, x, ty);
    }
    if (!intro && !seenBook && ap(4) > 0) { ctx.globalAlpha *= ap(4); const yy = y - h * .5 - s * .32 - Math.abs(Math.sin(t * 3 + 1)) * s * .1, r = s * .1; glow(x, yy, r * 4, [255, 236, 170], .7); poly([[x, yy - r * 1.3], [x + r, yy], [x, yy + r * 1.3], [x - r, yy]], [255, 236, 170]); }      // a bright diamond bobbing over it too, like the one over the Storyteller: tap me
    bookAt = [x, y, x - w * .62, x + w * 1.05, y - h * .5 - s * .8, y + h * .5 + s * .85, q[1]]; }      // [6]: where it rests, without the bob      // where a tap counts: well past the capsule to the right, up over its diamond and a good way below; on the left only just past its end, so a tap by the Storyteller still reaches him
  function tokenBubble(x, topY, al) {      // one speech bubble with all three roles in turn (Sailor, Heretic, Pukka): each a token where its name would be, then what it does
    const fs = clamp(W * .036, 12.5, 15), R = fs * 1.3, pad = 12, gap = 10, rowGap = 10, cw = Math.min(W - 16, 340), maxw = cw - pad * 2 - R * 2 - gap, lh = fs * 1.38; ctx.font = FONT(fs, true);
    const rows = INTRO.map(id => { const lines = wrapText(rb().abil[id], maxw); return { id, lines, h: Math.max(lines.length * lh, R * 2) }; });
    const bh = pad * 2 + rows.reduce((a, r) => a + r.h, 0) + rowGap * (rows.length - 1), bx = clamp(x - cw / 2, 8, W - cw - 8), by = Math.max(8, topY - bh - 8), tx = clamp(x, bx + 17, bx + cw - 17);
    ctx.fillStyle = css([250, 246, 238], .97 * al); rrect(bx, by, cw, bh, 11); ctx.moveTo(tx + 6, by + bh - 3); ctx.lineTo(tx, by + bh + 8); ctx.lineTo(tx - 6, by + bh - 3); ctx.closePath(); ctx.fill('nonzero');
    let yy = by + pad; for (const r of rows) { ctx.save(); ctx.globalAlpha *= al; roleToken(bx + pad + R, yy + r.h / 2, R, r.id); ctx.restore();
      const ty0 = yy + r.h / 2 - r.lines.length * lh / 2; r.lines.forEach((l, k) => text(l, bx + pad + R * 2 + gap, ty0 + lh * (k + .5), fs, [50, 36, 70], al, 'left', true)); yy += r.h + rowGap; } }
  function drawLobby(t, dt) {
    BG.dark = lerp(BG.dark, 0, 1 - Math.pow(.002, dt)); const g = BG; TINT = [30, 30, 90]; TK = lerp(.04, .34, g.dark); SHADOW = [58, 40, 96];
    moonAt = [W * .8, H * .14]; drawSky(mix(SKYD[0], SKYN[0], g.dark), mix(SKYD[1], SKYN[1], g.dark), mix(SKYD[2], SKYN[2], g.dark), t, .1 + .9 * g.dark); moonAt = null;
    const mx = W * .8, my = H * .14, sc = mix(ORBD, ORBN, g.dark); glow(mx, my, 130, sc, lerp(.45, .1, g.dark)); drawOrb(mx, my, 22, g.dark); drawGeese3(t, g.dark);
    if (appear) { appear.t += dt; while (appear.said < APPEAR.length && appear.t >= APPEAR[appear.said][0]) APPEAR[appear.said++][1](); if (appear.t >= APPEAR_END) appear = null; }
    const fadeT = ap(0) < 1, realCtx = ctx; let tc = null;      // while it fades in, the table is drawn whole onto a canvas of its own and laid over the sky, so its layers don't show through one another
    if (fadeT) { tc = tableCv || (tableCv = document.createElement('canvas')); if (tc.width !== cv.width || tc.height !== cv.height) { tc.width = cv.width; tc.height = cv.height; } ctx = tc.getContext('2d'); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, tc.width, tc.height); ctx.setTransform(DPR, 0, 0, DPR, 0, 0); }
    const v = lv = view(), s = v.s, P = v.P.bind(v), top = [92, 168, 162], under = [70, 96, 130], K = s * 1.25;
    v.disc(0, 0, -3.6, 1.1, 1.1, under); v.disc(0, 0, -2.5, 2.3, .9, under); v.disc(0, 0, -1.6, 3.4, 1.0, mix(under, top, .3)); v.disc(0, 0, -.6, 4.3, .6, top); v.disc(0, 0, 0, 2.3, 0, [120, 190, 180]);
    for (let i = 0; i < 12; i++) { const q = TAU * i / 12; line([P(3.95 * Math.cos(q), 3.95 * Math.sin(q)), P(4.18 * Math.cos(q), 4.18 * Math.sin(q))], tint(mix(top, [255, 255, 255], .6)), s * .07); }
    if (fadeT) { ctx = realCtx; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = ap(0); ctx.drawImage(tc, 0, 0); ctx.restore(); }
    // walking: straight to where you tapped, at a stroll, with a little hop
    const dx = me.tx - me.x, dy = me.ty - me.y, d = Math.hypot(dx, dy), moving = d > .03;
    if (moving) { const st = Math.min(d, 2.6 * dt); me.x += dx / d * st; me.y += dy / d * st; { const r = Math.hypot(me.x, me.y); if (r < 1.35) { const q = Math.atan2(me.y, me.x) + Math.sign(dx * me.y - dy * me.x || 1) * -.06; me.x = Math.cos(q) * 1.35; me.y = Math.sin(q) * 1.35; } }      // the Storyteller's dais is solid: pushed out to its edge and a little round it, so a walk across slides round the dais
      me.hop += dt; if ((me.step = (me.step || 0) + dt) > .3) { me.step = 0; chime(pick([62, 65, 69]) + 12, 0, .03, .5); } }
    else if (me.talk) { me.talk = false; me.say = { t: 0 }; chime(74, 0, .16, 1.4); chime(81, .1, .14, 1.4); }
    if (me.say && (me.say.t += dt) > 1.5 && !tr) { tr = { t: 0, to: 'game' }; }
    if (moving && !me.talk) { const q = P(me.tx, me.ty); ell(q[0], q[1], s * .26 * 1.25, s * .13 * 1.25, [255, 240, 200], .4); }      // where you are walking to: a ring on the ground
    const pulse = .5 + .5 * Math.sin(t * 5), drawSt = () => { const p = P(0, 0, .3); fadedDraw(ap(1), () => { v.disc(0, 0, 0, .95, .3, [240, 220, 190]);
        glow(p[0], p[1] - K * .8, K * 1.4, [200, 170, 255], .3); fig(p[0], p[1], K * 1.2, { kind: 'teller', body: [132, 100, 172], hat: [70, 52, 100] }); }); lv.st = [p[0], p[1] - K * .8, K * .95];      // no grimoire beside him while you stroll: the 小染书 capsule lies there instead
        if (!me.say && !me.talk && !intro && seenBook) { const yy = p[1] - K * 1.2 * 1.75 - Math.abs(Math.sin(t * 3)) * s * .14, r = s * .13; glow(p[0], yy, r * 4, [255, 236, 170], .7); poly([[p[0], yy - r * 1.3], [p[0] + r, yy], [p[0], yy + r * 1.3], [p[0] - r, yy]], [255, 236, 170]); } },      // a bright diamond bobbing over his head: talk to him
      drawMe = () => { const p = P(me.x, me.y), y = p[1] - (moving ? Math.abs(Math.sin(me.hop * 9)) * s * .12 : 0); fadedDraw(ap(2), () => { glow(p[0], y - K * .6, K * 1.2, [255, 240, 200], .3); fig(p[0], y, K, BLOOK[0]); }); };
    { const ents = [[0, drawSt], [me.x + me.y, drawMe]].sort((a, b) => a[0] - b[0]); let lo = -Infinity;      // whoever is nearer is drawn last, and the confetti in between
      for (const [k, f] of ents) { window.__confLayer(lo, k); f(); lo = k; } window.__confLayer(lo, Infinity); }
    const bm = window.__lastWon && (window.__boardMark || webMark); markAt = null;      // the app and the Xiaohongshu build bring their own      // the last game won: the ball; lost (or none yet): the book
    if (bm) drawMark(t, dt, P, s, bm); else fadedDraw(ap(3), () => drawBook(t, P, s));      // the book, or after a win the scores' ball in its place (drawn straight onto the picture: its glass blurs what is behind it)      // the book, or after a win the scores' bubbles in its place      // 小染书, beside the Storyteller while you stroll
    if (intro && bookAt) { intro.t += dt; tokenBubble(bookAt[0], bookAt[6] - s * .26 - s * .06, clamp(intro.t * 4)); }      // anchored where the capsule rests, so the bubble stays still while the capsule bobs      // 小染书 itself tells you the roles, all in one bubble, its tail on the capsule
    if (me.say) { const p = P(0, 0, .3); sayBubble(p[0], p[1] - K * 1.6 * 1.2, say3(), clamp(W * .036, 12.5, 15), clamp(me.say.t * 4), W * .62); }
    if (me.line && (me.line.t += dt) < 2.4) { const p = P(me.x, me.y); sayBubble(p[0], p[1] - K * 1.6, me.line.text, clamp(W * .036, 12.5, 15), clamp(me.line.t * 4) * clamp((2.4 - me.line.t) * 3), W * .62); } else me.line = null;      // what you just said (a new language)
  }
  updateTower = () => {};      // no tower room, no keeper, no view from the top
  drawTowerRoom = T => { const now = performance.now(), dt = Math.min(.05, (now - last) / 1000); last = now;
    stepConfetti(dt);
    window.__3bLang = lobby && !tr;      // the language button, top right, while the lobby is up
    if (lobby) drawLobby(T, dt); else drawBotc(T, dt);
    if (tr) { tr.t += dt; ctx.fillStyle = css([6, 4, 16], clamp(tr.t / .7)); ctx.fillRect(0, 0, W, H);      // down to black, then the other scene
      if (tr.t >= .75) { const to = tr.to; tr = null; fade = 1.2;
        if (to === 'game') { confetti = null; landed = []; lobby = false;      /* into the game's scene: the confetti is not there */ me.say = null; BG.dark = 1; bell(146.8, .12); playBotc(); BG.isNight = true; }      // the night, and everyone at the table: the game begins
        else { lobby = true; BG.bubble = null; BG.wait = null; BG.isNight = false; BG.dark = 1; me.x = me.tx = 3 * Math.cos(Math.PI / 4); me.y = me.ty = 3 * Math.sin(Math.PI / 4); } } } };      // back to the quiet table, at your seat
  towerTap = (x, y) => { if (tr || (appear && appear.t < APPEAR_TAP)) return; if (!lobby) return botcTap(x, y); if (me.say || me.talk || !lv) return;      // nothing to tap until everything has appeared; in the game, taps are the game's
    if (intro) { if (intro.t > .25) { intro = null; seenBook = true; chime(pick([69, 74, 76]), 0, .07, .6); } return; }      // a tap and it is done; now the Storyteller sparkles instead
    if (markAt && Math.hypot(x - markAt[0], y - markAt[1]) < markAt[2]) { chime(74, 0, .12, 1); chime(79, .1, .1, 1); window.__spinMark(); markAt[3].open(markAt[0], markAt[1] - markAt[4]); return; }      // (x, top of the ball): where a bubble can point      // the bubbles: the scores
    if (bookAt && x > bookAt[2] && x < bookAt[3] && y > bookAt[4] && y < bookAt[5]) { intro = { i: 0, t: 0 }; chime(74, 0, .12, 1); chime(79, .1, .1, 1); return; }      // 小染书: it tells you about the roles
    const st = lv.st; if (st && Math.hypot(x - st[0], y - st[1]) < st[2]) { me.tx = me.x; me.ty = me.y; me.talk = true; markLine = null; me.line = null; intro = null; return; }      /* the Storyteller's word to begin outranks every other bubble: the ball's, yours, 小染书's */      // the Storyteller answers from where you stand: no walking over
    const [gx, gy] = lv.inv(x, y), [rx, ry] = ring(gx, gy); me.tx = rx; me.ty = ry; chime(69, 0, .07, .8); };      // a stroll about the table
  leaveTower = () => { if (!tr) tr = { t: 0, to: 'lobby' }; };      // a game over: fade back to the lobby
  const go = () => { $('title').style.display = 'none'; for (const id of ['zoom', 'leave', 'enter']) { const el = $(id); if (el) el.style.display = 'none'; }
    mode = 'tower'; tw.view = null; fade = 0; BG.dark = 0; BG.isNight = false;
    const box = document.createElement('div'); box.style.cssText = 'position:fixed;right:calc(12px + env(safe-area-inset-right));bottom:calc(14px + env(safe-area-inset-bottom));z-index:20';      // the language button in the bottom-right corner, its menu opening upward
    const lbn = $('lang'); lbn.innerHTML = MARK; box.appendChild(lbn); const m = $('langMenu'); m.style.top = 'auto'; m.style.bottom = '46px'; m.style.left = 'auto'; m.style.right = '0'; for (const l of ['auto', 'en', 'hans', 'hant']) m.append(m.querySelector(`[data-l=${l}]`)); box.appendChild(m);      /* one fixed order: the system's, then English, 简体, 繁體 */ { const st = document.createElement('style'); st.textContent = MARK_CSS; document.head.appendChild(st); } document.body.appendChild(box); { const st = document.createElement('style'); st.textContent = '#bag,#bspeed,#bfreeze,#bclose{display:none!important}'; document.head.appendChild(st); }      /* /3b has no backpack */ };
  window.__3bQuietMs = performance.now() + (APPEAR_END + .1) * 1000;      // no melody notes from the music until the opening is over
  if (!location.hash) go();      // at once, before the first frame: straight onto the table in the air, no fade, no title, no town
  requestAnimationFrame(frame);      // only now do the frames begin
  window.__3b = { me, get lobby() { return lobby; }, get tr() { return tr; }, get book() { return bookAt; }, get intro() { return intro; } };      // for tests
})();
</script>
"""
LANG_SHOW = "const show = mode === 'title' || (mode === 'world' && zoomTarget > .5)"
assert src.count(LANG_SHOW) == 1, 'language-button rule not found in index.html'
src = src.replace(LANG_SHOW, LANG_SHOW + ' || !!window.__3bLang', 1)      # /3b: the language button also shows in its lobby
botc3 = open(os.path.join(ROOT, 'tools', 'botc3.js'), encoding='utf-8').read()      # the three-player game itself: no longer in index.html
check_comments(boot, 'mk3b boot script')
check_comments(botc3, 'tools/botc3.js')
boot = '<script>\n' + botc3 + '\n</script>\n' + boot
KICK = "\nrequestAnimationFrame(frame);\n</script>"
assert src.count(KICK) == 1, 'frame kick-off not found in index.html'
src = src.replace(KICK, "\n</script>", 1)      # /3b: the main game must not draw a frame (its title over the town) before /3b has taken over; the boot script starts the frames
src = src.replace('</head>', '<style>html,body{background:linear-gradient(rgb(226,150,130),rgb(214,166,156) 50%,rgb(204,150,148))}#title{display:none!important}</style>\n</head>', 1)      # the lobby's daytime sky behind the page, never the night navy, and never the title
MEL = "const t = nextBar + i * 0.6 - AC.currentTime; chime(sc[melIdx], Math.max(0, t), rnd(0.05, 0.09), 2.2);"
assert src.count(MEL) == 1, 'music melody line not found in index.html'
src = src.replace(MEL, "const t = nextBar + i * 0.6 - AC.currentTime; if (window.__3bQuietMs && performance.now() + t * 1000 < window.__3bQuietMs) continue; chime(sc[melIdx], Math.max(0, t), rnd(0.05, 0.09), 2.2);", 1)      # /3b: the music's little melody notes keep out of the opening's 咚 咚 咚 丁零定 (the chord underneath plays on)
i = src.rfind('</body>')
out = src[:i] + boot + src[i:] if i >= 0 else src + boot
import re as _re; out = _re.sub(r'<title>[^<]*</title>', '<title>三人染</title>', out, count=1)      # its own name, not the main game's
# two outputs: deploy/3b-embed.html for the app and the Xiaohongshu package (no debug), and deploy/3b.html for the web, which also
# gets the debug switch behind the sun (tools/web_debug_*.js; the Xiaohongshu leaderboard, tools/xhs_rank.js, only runs in its mode)
open(os.path.join(ROOT, 'deploy', '3b-embed.html'), 'w', encoding='utf-8').write(out)
rd = lambda f: open(os.path.join(ROOT, 'tools', f), encoding='utf-8').read()
assert out.count('<head>') == 1 and out.count('</body>') == 1
web = out.replace('<head>', '<head>\n<script>' + rd('web_debug_early.js') + '</script>', 1)
web = web.replace('</body>', '<script>if (window.__debugMode === "xhs") {\n' + rd('xhs_rank.js') + '\n}\n' + rd('web_debug_late.js') + '</script>\n</body>', 1)
open(os.path.join(ROOT, 'deploy', '3b.html'), 'w', encoding='utf-8').write(web)
print('deploy/3b.html', len(web), 'bytes (web, with the debug switch); deploy/3b-embed.html', len(out), 'bytes (app and Xiaohongshu)')
