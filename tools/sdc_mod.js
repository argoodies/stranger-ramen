// 拉面怪奇物语 · 魔窟: index.html itself, with a way down. tools/mksdc.py patches the game and adds this module.
(() => {
const $ = id => document.getElementById(id);
const rand = (a, b) => a + Math.random() * (b - a), irand = (a, b) => Math.floor(rand(a, b + 1));
const THIN = THINF;
function text(t, x, y, px, c = [255, 255, 255], a = 1, al = 'center', w = 300) { ctx.font = `${w} ${px}px ${THIN}`; ctx.textAlign = al; ctx.textBaseline = 'middle'; ctx.fillStyle = css(c, a); ctx.fillText(t, x, y); }
MUSIC.cave = MUSIC.tower;
const CAT_BLACK = { col: [46, 40, 58], sh: [26, 22, 34], pink: [214, 128, 150], eye: [238, 208, 92], pupil: [26, 20, 30] };
function catFigure(q, k, c, pal) {
  const f = c.face || 1, sit = false, still = c.sit > 0, { col, sh, pink } = pal;
  const tail = (pts, w) => { ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); ctx.quadraticCurveTo(pts[1][0], pts[1][1], pts[2][0], pts[2][1]); ctx.quadraticCurveTo(pts[3][0], pts[3][1], pts[4][0], pts[4][1]); ctx.strokeStyle = css(sh); ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.stroke(); ctx.strokeStyle = css(col); ctx.lineWidth = w * .7; ctx.stroke(); };
      ell(q[0], q[1], k * .42, k * .12, [20, 12, 40], .22);
      let hx, hy;
      if (sit) { const sw = Math.sin(c.t * 1.6) * k * .05;      // sitting up: a soft pear of a body, the tail curled round the paws
        tail([[q[0] - f * k * .22, q[1] - k * .08], [q[0] - f * k * .5, q[1] - k * .02], [q[0] - f * k * .3, q[1] + k * .06 + sw * .3], [q[0] + f * k * .05, q[1] + k * .1], [q[0] + f * k * .22, q[1] + k * .02 + sw * .2]], Math.max(3, k * .13));
        ell(q[0], q[1] - k * .3, k * .3, k * .32, col); ell(q[0] + k * .06, q[1] - k * .26, k * .14, k * .24, sh, .35); for (const dx of [-.1, .1]) ell(q[0] + f * k * .1 + dx * k, q[1] - k * .03, k * .08, k * .05, col);      // body and front paws
        hx = q[0] + f * k * .05; hy = q[1] - k * .76; }
      else { const ph = still ? 0 : c.t * 9, bob = Math.abs(Math.sin(ph)) * k * .03, by = q[1] - k * .3 - bob;      // walking: little legs stepping toward where it goes, tail up and swaying
        tail([[q[0] - f * k * .3, by - k * .02], [q[0] - f * k * .55, by - k * .05], [q[0] - f * k * .52, by - k * .3], [q[0] - f * k * .5, by - k * .55 + Math.sin(c.t * 4) * k * .05], [q[0] - f * k * (.36 + .08 * Math.sin(c.t * 4)), by - k * .6]], Math.max(3, k * .13));
        const legs = [[-.22, 0], [-.1, Math.PI], [.14, Math.PI], [.26, 0]]; for (const [lx, o] of legs) { const sw = still ? 0 : Math.sin(ph + o) * k * .08; line([[q[0] + f * lx * k, by + k * .1], [q[0] + f * lx * k + f * sw, q[1] - k * .02]], o ? sh : col, Math.max(2.5, k * .11)); }      // each foot swings forward, then back
        ell(q[0], by, k * .38, k * .22, col); ell(q[0] - f * k * .04, by + k * .05, k * .3, k * .1, sh, .35);
        hx = q[0] + f * k * .34; hy = by - k * .2; }
      for (const sg of [-1, 1]) { poly([[hx + sg * k * .08, hy - k * .17], [hx + sg * k * .23, hy - k * .08], [hx + sg * k * .2, hy - k * .36]], col); poly([[hx + sg * k * .11, hy - k * .17], [hx + sg * k * .2, hy - k * .12], [hx + sg * k * .19, hy - k * .28]], pink); }      // ears, pink inside
      circ(hx, hy, k * .27, col);      // a big round head
      for (const sg of [-1, 1]) { const ex = hx + sg * k * .1 + f * k * .03; circ(ex, hy - k * .02, k * (pal.pupil ? .06 : .045), pal.eye); if (pal.pupil) ell(ex, hy - k * .02, k * .018, k * .05, pal.pupil); circ(ex + k * .015, hy - k * .035, k * .015, [255, 255, 255]); ell(hx + sg * k * .17 + f * k * .03, hy + k * .07, k * .05, k * .03, pink, .55); }      // eyes with a glint (a black cat's are gold, with slit pupils), rosy cheeks      // eyes with a glint, rosy cheeks
      circ(hx + f * k * .03, hy + k * .05, k * .025, pink);      // a tiny nose
  return [hx, hy];
}
// ---------- save ----------
const KEY = 'ramen_sdc_v1';
const blank = () => ({ gold: 60, stash: [], equip: { bow: null, armor: null, acc: null }, potions: 2, runs: 0, out: 0 });
let save = blank();
try { const s = JSON.parse(localStorage.getItem(KEY) || 'null'); if (s) save = Object.assign(blank(), s); } catch (e) {}
const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(save)); } catch (e) {} };

// ---------- items ----------
const RAR = [{ n: '普通', c: '#d6dbe8', m: 1 }, { n: '优良', c: '#7fe0a8', m: 1.7 }, { n: '稀有', c: '#74b9ff', m: 2.8 }, { n: '史诗', c: '#c493ff', m: 4.6 }, { n: '传说', c: '#ffc866', m: 8 }];
const KIND = { gem: '宝', bow: '弓', armor: '甲', acc: '饰' };
const NAMES = { gem: ['碎晶', '紫水晶', '血玉', '月长石', '星辰石'], bow: ['猎弓', '角弓', '夜莺弓', '钟楼弓', '渡鸦之弓'], armor: ['皮甲', '镶钉甲', '夜行斗篷', '鳞甲', '守夜人之甲'], acc: ['旧铃铛', '鹰眼坠', '疾风戒', '渡鸦羽', '月光护符'] };
function rollRar(depth) { let r = Math.random() * (1 + depth * .6), k = 0; for (const t of [.62, .92, 1.16, 1.34]) if (r > t) k++; return k; }
function makeItem(depth, kind) {
  const k = kind || pick(['gem', 'gem', 'bow', 'armor', 'acc']), r = rollRar(depth), m = RAR[r].m, it = { k, r, name: NAMES[k][r] };
  if (k === 'gem') it.v = Math.round(rand(14, 24) * m);
  if (k === 'bow') { it.dmg = Math.round(rand(7, 10) * Math.sqrt(m) * 1.1); it.v = Math.round(it.dmg * 2.2 * m); }
  if (k === 'armor') { it.hp = Math.round(rand(14, 22) * Math.sqrt(m)); it.v = Math.round(it.hp * 1.3 * m); }
  if (k === 'acc') { it.spd = +(rand(.02, .05) * Math.sqrt(m)).toFixed(3); it.sight = r >= 2 ? 1 : 0; it.v = Math.round(rand(16, 26) * m); }
  return it;
}
const itemStat = it => it.k === 'gem' ? `价值 ${it.v} 金币` : it.k === 'bow' ? `攻击 +${it.dmg}` : it.k === 'armor' ? `生命 +${it.hp}` : `移速 +${Math.round(it.spd * 100)}%${it.sight ? '，视野 +1' : ''}`;
const stats = () => { const e = save.equip; return { dmg: 12 + (e.bow ? e.bow.dmg : 0), hp: 100 + (e.armor ? e.armor.hp : 0), spd: 4.4 * (1 + (e.acc ? e.acc.spd : 0)), sight: 7 + (e.acc ? e.acc.sight : 0) }; };

// ---------- sound ----------
function blip(f, d = .1, type = 'sine', v = .08, slide = 0) { if (!AC || !master) return; const o = AC.createOscillator(), g = AC.createGain(), t = AC.currentTime; o.type = type; o.frequency.setValueAtTime(f, t); if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(30, f + slide), t + d); g.gain.setValueAtTime(v, t); g.gain.exponentialRampToValueAtTime(.0005, t + d); o.connect(g); g.connect(master); o.start(t); o.stop(t + d); }
const sfxS = { shoot: () => blip(520, .12, 'triangle', .07, -300), hit: () => blip(180, .09, 'square', .05, -80), coin: () => { blip(990, .07, 'sine', .06); setTimeout(() => blip(1320, .1, 'sine', .06), 60); }, chest: () => { blip(330, .12, 'triangle', .08); setTimeout(() => blip(494, .14, 'triangle', .08), 90); setTimeout(() => blip(660, .2, 'triangle', .08), 190); }, hurt: () => blip(120, .18, 'sawtooth', .07, -50), out: () => [523, 659, 784, 1047].forEach((f, i) => setTimeout(() => blip(f, .24, 'sine', .07), i * 110)) };

// ---------- state ----------
const P = { x: 4, y: 3.5, face: [1, 0], hp: 100, inv: 0, draw: 0, aim: [1, 0], step: 0, moved: 0, speed: 0, dash: 0, dashCd: 0, dashDir: [1, 0], path: [] };
const cat = { x: 0, y: 0, face: 1, t: 0, sit: 1, tx: 0, ty: 0, meowT: 0 };
let time = 0, modal = false, shake = 0, s = 40, scene = 'world';
const v = new View(0, 0, 40), cam = { x: 4, y: 3.5 };
let run = null;      // the current trip into the cave
const floats = [];
const input = { l: 0, r: 0, u: 0, d: 0, jx: 0, jy: 0, ax: 0, ay: 0, shoot: false, act: false, dash: false, potion: false };
const say = (t, x, y, c = [255, 255, 255]) => floats.push({ s: t, x, y, z: 1.8, c, t: 1.4 });
// screen direction -> world direction on the 2:1 diamond
function screenToWorld(sx, sy) { const a = sx / (2 * C30), b = sy; const x = a + b, y = b - a, n = Math.hypot(x, y) || 1; return [x / n, y / n]; }

const caveSolid = (x, y) => { const i = Math.floor(x), j = Math.floor(y); return i < 0 || j < 0 || i >= CS || j >= CS || run.m[j * CS + i] === 1; };
const R = .24;
function tryMove(e, dx, dy, ok) {
  const free = (x, y) => ok(x - R, y - R) && ok(x + R, y - R) && ok(x - R, y + R) && ok(x + R, y + R);
  if (free(e.x + dx, e.y)) e.x += dx; else e.bump = true;
  if (free(e.x, e.y + dy)) e.y += dy; else e.bump = true;
}
// ---------- the Demon Cave: rooms joined by passages, seen from the same corner as the town ----------
const CS = 112, ROOMS = 6, CELL = 18;      // tiles: 0 floor, 1 rock
function genCave() {
  const m = new Uint8Array(CS * CS).fill(1), seen = new Uint8Array(CS * CS), set = (x, y, t) => { if (x > 1 && y > 1 && x < CS - 2 && y < CS - 2) m[y * CS + x] = t; }, at = (x, y) => (x < 0 || y < 0 || x >= CS || y >= CS) ? 1 : m[y * CS + x];
  const rooms = [];
  for (let gy = 0; gy < ROOMS; gy++) for (let gx = 0; gx < ROOMS; gx++) {
    const w = irand(8, 14), h = irand(8, 14), x = 3 + gx * CELL + irand(0, CELL - w - 3), y = 3 + gy * CELL + irand(0, CELL - h - 3), r = { gx, gy, x, y, w, h, cx: x + (w >> 1), cy: y + (h >> 1) }; rooms.push(r);
    for (let j = y; j < y + h; j++) for (let i = x; i < x + w; i++) set(i, j, 0);
    const corner = 2 + irand(0, 1); for (const [a, b] of [[x, y], [x + w - 1, y], [x, y + h - 1], [x + w - 1, y + h - 1]]) for (let k = 0; k < corner; k++) { set(a + (a === x ? k : -k), b, 1); set(a, b + (b === y ? k : -k), 1); }      // rounded, cave-like corners
  }
  const room = (a, b) => rooms[b * ROOMS + a], nb = r => [[1, 0], [-1, 0], [0, 1], [0, -1]].map(([a, b]) => (r.gx + a >= 0 && r.gx + a < ROOMS && r.gy + b >= 0 && r.gy + b < ROOMS) ? room(r.gx + a, r.gy + b) : null).filter(Boolean);
  const carve = (a, b) => { let x = a.cx, y = a.cy, hw = irand(1, 2); const hfirst = Math.random() < .5; const stepX = () => { while (x !== b.cx) { x += Math.sign(b.cx - x); for (let k = -hw; k <= hw; k++) set(x, y + k, 0); } }, stepY = () => { while (y !== b.cy) { y += Math.sign(b.cy - y); for (let k = -hw; k <= hw; k++) set(x + k, y, 0); } }; if (hfirst) { stepX(); stepY(); } else { stepY(); stepX(); } };
  const start = room(0, ROOMS - 1), vis = new Set([start]), stack = [start];
  while (stack.length) { const r = stack[stack.length - 1], o = nb(r).filter(n => !vis.has(n)); if (!o.length) { stack.pop(); continue; } const n = pick(o); vis.add(n); carve(r, n); stack.push(n); }
  for (let i = 0; i < 10; i++) { const r = pick(rooms); carve(r, pick(nb(r))); }
  const dist = r => Math.hypot(r.cx - start.cx, r.cy - start.cy), byFar = [...rooms].sort((a, b) => dist(b) - dist(a)), far = byFar[0], mid = byFar.find(r => dist(r) > 40 && Math.hypot(r.cx - far.cx, r.cy - far.cy) > 45) || byFar[4], maxD = dist(far);
  const portals = [{ x: start.cx + .5, y: start.cy + .5, name: '入口', t: 0 }, { x: far.cx + .5, y: far.cy + .5, name: '深处撤离点', t: 0, armed: true }, { x: mid.cx + .5, y: mid.cy + .5, name: '撤离点', t: 0, armed: true }];
  const chests = [], mobs = [], torches = [], rocks = [], spot = r => { for (let k = 0; k < 40; k++) { const x = irand(r.x + 2, r.x + r.w - 3), y = irand(r.y + 2, r.y + r.h - 3); if (at(x, y) === 0 && Math.hypot(x - r.cx, y - r.cy) > 1.6) return [x + .5, y + .5]; } return [r.cx + .5, r.cy + 1.5]; };
  for (const r of rooms) {
    for (let k = 0; k < 2; k++) rocks.push(spot(r));
    if (Math.random() < .7) torches.push([r.x + 1.5, r.y + 2.5]);
    if (r === start) continue;
    const depth = dist(r) / maxD, nc = Math.random() < .3 + depth * .3 ? (Math.random() < .15 + depth * .25 ? 2 : 1) : 0;
    for (let i = 0; i < nc; i++) { const [x, y] = spot(r); chests.push({ x, y, depth, open: false, t: 0, gold: depth > .7 && Math.random() < .4 }); }
    const n = irand(0, 1) + Math.round(depth * 1.5);
    for (let i = 0; i < n; i++) { const [x, y] = spot(r); mobs.push(makeMob(Math.random() < .25 ? 'bat' : depth > .3 && Math.random() < .35 ? 'archer' : 'slime', x, y, depth)); }
    if (depth > .55 && Math.random() < .45) { const [x, y] = spot(r); mobs.push(makeMob('golem', x, y, depth)); }
  }
  return { m, seen, rooms, portals, chests, mobs, torches, rocks, drops: [], arrows: [], bolts: [], start, sx: start.cx + 1.8, sy: start.cy + .5 };
}
const MOB = { slime: { hp: 34, sp: 1.5, dmg: 10, r: .34, c: [110, 200, 150] }, bat: { hp: 20, sp: 2.7, dmg: 8, r: .3, c: [150, 110, 210], fly: 1 }, archer: { hp: 42, sp: 1.3, dmg: 11, r: .3, c: [214, 208, 226] }, golem: { hp: 170, sp: 1, dmg: 22, r: .55, c: [120, 110, 150], elite: 1 } };
const makeMob = (k, x, y, depth) => { const d = MOB[k], m = 1 + depth * 1.3; return { k, x, y, hp: d.hp * m, max: d.hp * m, dmg: d.dmg * (1 + depth * .7), sp: d.sp, r: d.r, c: d.c, fly: !!d.fly, elite: !!d.elite, alert: 0, cd: rand(.5, 2), flash: 0, depth, ph: Math.random() * 6, dir: [1, 0], wander: 0 }; };
function enterCave() {
  const st = stats(), c = genCave();
  run = Object.assign(c, { bag: [], gold: 0, potions: save.potions, time: 0, kills: 0, cap: 12 });
  scene = 'cave'; mode = 'cave'; fade = 1; P.x = c.sx; P.y = c.sy; P.hp = st.hp; P.inv = 1; P.path = []; cat.x = P.x - 1; cat.y = P.y + .4; cam.x = P.x; cam.y = P.y; save.runs++; persist();
  say('找到撤离点才算带走', P.x, P.y, [255, 236, 190]);
}
function leaveCave(ok, title) {
  const r = run, lost = r.bag.length, vals = r.bag.reduce((a, b) => a + b.v, 0);
  if (ok) { save.gold += r.gold; save.stash.push(...r.bag); save.out++; save.potions = r.potions; sfxS.out(); } else save.potions = r.potions;
  persist(); run = null; scene = 'world'; enterBar(); panelResult(ok, title, r, lost, vals);
}
// ---------- the update ----------
function update(dt) {
  time += dt;
  for (let i = floats.length - 1; i >= 0; i--) { const f = floats[i]; f.t -= dt; f.z += dt * .8; if (f.t <= 0) floats.splice(i, 1); }
  if (shake > 0) shake -= dt;
  if (modal) return;
  const st = stats(); let mx = (input.r - input.l) + input.jx, my = (input.d - input.u) + input.jy, w = [0, 0];
  const mag = Math.min(1, Math.hypot(mx, my));
  if (mag > .12) { w = screenToWorld(mx, my); P.path = []; }
  else if (P.path.length) { const [ti, tj] = P.path[0], dx = ti + .5 - P.x, dy = tj + .5 - P.y, d = Math.hypot(dx, dy); if (d < .15) P.path.shift(); else w = [dx / d, dy / d]; }
  const canStand = (x, y) => !caveSolid(x, y), moving = w[0] || w[1], kk = (P.draw > 0 ? .5 : 1) * (mag > .12 ? mag : 1);
  P.speed = moving ? st.spd * kk : 0;
  if (moving && P.draw <= 0) P.face = w;
  if (P.dashCd > 0) P.dashCd -= dt;
  if (input.dash && P.dashCd <= 0 && !input.shoot) { P.dash = .2; P.dashCd = .9; P.dashDir = moving ? w : P.face; P.inv = Math.max(P.inv, .24); blip(300, .1, 'triangle', .05, 200); } input.dash = false;
  if (P.dash > 0) { P.dash -= dt; tryMove(P, P.dashDir[0] * 11 * dt, P.dashDir[1] * 11 * dt, canStand); P.step += dt * 14; }
  else if (moving) { P.bump = false; tryMove(P, w[0] * P.speed * dt, w[1] * P.speed * dt, canStand); P.step += dt * P.speed * 2; }
  P.moved = moving ? P.moved + dt : 0;
  if (P.inv > 0) P.inv -= dt;
  const c = run;
  c.time += dt;
  // the bow: hold to draw, let go to loose; the aim is the mouse, or on a touch screen the nearest thing in sight
  const tgt = nearestMob(c, 10);
  if (Math.hypot(input.ax, input.ay) > .4) P.aim = screenToWorld(input.ax, input.ay);
  else if (tgt) { const dx = tgt.x - P.x, dy = tgt.y - P.y, d = Math.hypot(dx, dy) || 1; P.aim = [dx / d, dy / d]; } else P.aim = P.face;
  if (input.shoot) { P.draw = Math.min(.7, P.draw + dt + 1e-4); P.face = P.aim; }
  else if (P.draw > 0) { const k = clamp(P.draw / .7, .35, 1), sp = 11 + 9 * k; c.arrows.push({ x: P.x, y: P.y, vx: P.aim[0] * sp, vy: P.aim[1] * sp, dmg: st.dmg * (.55 + .75 * k), t: 1.6, stuck: false }); P.draw = 0; sfxS.shoot(); }
  if (input.potion) { input.potion = false; if (c.potions > 0 && P.hp < st.hp) { c.potions--; P.hp = Math.min(st.hp, P.hp + 50); say('+50', P.x, P.y, [150, 240, 170]); blip(660, .2, 'sine', .07); } }
  reveal(c, P.x, P.y, st.sight);      // the fog lifts round the chef
  for (let i = c.arrows.length - 1; i >= 0; i--) { const a = c.arrows[i]; a.t -= dt; if (a.t <= 0) { c.arrows.splice(i, 1); continue; } if (a.stuck) continue;
    let gone = false; for (let k = 0; k < 3 && !a.stuck && !gone; k++) { a.x += a.vx * dt / 3; a.y += a.vy * dt / 3; if (caveSolid(a.x, a.y)) { a.stuck = true; a.t = 1; break; } for (const m of c.mobs) if (Math.hypot(a.x - m.x, a.y - m.y) < m.r + .14) { hurtMob(c, m, a.dmg); gone = true; break; } } if (gone) c.arrows.splice(i, 1); }
  for (let i = c.bolts.length - 1; i >= 0; i--) { const b = c.bolts[i]; b.t -= dt; b.x += b.vx * dt; b.y += b.vy * dt; if (b.t <= 0 || caveSolid(b.x, b.y)) { c.bolts.splice(i, 1); continue; } if (Math.hypot(b.x - P.x, b.y - P.y) < .4) { hurtP(b.dmg, b.vx, b.vy); c.bolts.splice(i, 1); if (!run) return; } }
  for (const m of [...c.mobs]) { updateMob(c, m, dt); if (!run) return; }
  for (let i = c.drops.length - 1; i >= 0; i--) { const d = c.drops[i]; d.age += dt; d.vz -= 14 * dt; d.z = Math.max(0, d.z + d.vz * dt); if (d.z === 0) d.vz = 0; const nx = d.x + d.vx * dt, ny = d.y + d.vy * dt; if (!caveSolid(nx, ny)) { d.x = nx; d.y = ny; } d.vx *= Math.pow(.02, dt); d.vy *= Math.pow(.02, dt); if (d.age > .35 && Math.hypot(d.x - P.x, d.y - P.y) < 1.1 && take(c, d)) c.drops.splice(i, 1); }
  let at = null; for (const p of c.portals) { const near = Math.hypot(p.x - P.x, p.y - P.y) < 1, far = Math.hypot(p.x - P.x, p.y - P.y); if (far > 4) p.armed = true; if (far < st.sight + 2) p.found = true; if (near && p.armed) at = p; else p.t = 0; }
  c.at_ = at; if (at) { at.t += dt; if (at.t >= 2) { leaveCave(true, at.name); return; } }
  cam.x = lerp(cam.x, P.x, 1 - Math.pow(.005, dt)); cam.y = lerp(cam.y, P.y, 1 - Math.pow(.005, dt));
  updateCat(dt, !!P.speed); updatePrompt();
}
function nearestMob(c, r) { let b = null, bd = r; for (const m of c.mobs) { const d = Math.hypot(m.x - P.x, m.y - P.y); if (d < bd && losClear(P.x, P.y, m.x, m.y)) { b = m; bd = d; } } return b; }
function reveal(c, x, y, r) { for (let j = Math.floor(y - r); j <= y + r; j++) for (let i = Math.floor(x - r); i <= x + r; i++) if (i >= 0 && j >= 0 && i < CS && j < CS && Math.hypot(i + .5 - x, j + .5 - y) < r) c.seen[j * CS + i] = 1; }
function updateMob(c, m, dt) {
  m.ph += dt * 4; if (m.flash > 0) m.flash -= dt; if (m.cd > 0) m.cd -= dt;
  const dx = P.x - m.x, dy = P.y - m.y, d = Math.hypot(dx, dy) || 1; if (d > 22) return;      // asleep until you come near
  const sees = d < 8.5 && losClear(m.x, m.y, P.x, P.y); if (sees) m.alert = 3; else m.alert -= dt;
  let mx = 0, my = 0, sp = m.sp;
  if (m.alert > 0) { mx = dx / d; my = dy / d; if (m.k === 'archer') { const q = d < 3.5 ? -1 : d > 6 ? 1 : 0; mx *= q; my *= q; if (sees && m.cd <= 0) { m.cd = rand(1.6, 2.6); c.bolts.push({ x: m.x, y: m.y, vx: dx / d * 6, vy: dy / d * 6, dmg: m.dmg, t: 3 }); } } }
  else { m.wander -= dt; if (m.wander <= 0) { m.wander = rand(1, 3); const a = rand(0, TAU); m.dir = Math.random() < .4 ? [0, 0] : [Math.cos(a), Math.sin(a)]; } mx = m.dir[0]; my = m.dir[1]; sp *= .4; }
  const ok = (x, y) => !caveSolid(x, y); m.bump = false; const r0 = m.r; tryMove(m, mx * sp * dt, my * sp * dt, ok);
  for (const o of c.mobs) if (o !== m) { const ax = m.x - o.x, ay = m.y - o.y, q = Math.hypot(ax, ay) || 1; if (q < m.r + o.r) { const nx = m.x + ax / q * dt * 1.5, ny = m.y + ay / q * dt * 1.5; if (ok(nx, ny)) { m.x = nx; m.y = ny; } } }
  if (d < r0 + .34 && m.k !== 'archer') hurtP(m.dmg, dx, dy);
}
function hurtP(n, dx, dy) { if (P.inv > 0) return; P.hp -= n; P.inv = .8; const q = Math.hypot(dx, dy) || 1; tryMove(P, dx / q * .5, dy / q * .5, (x, y) => !caveSolid(x, y)); shake = .25; sfxS.hurt(); say('-' + Math.round(n), P.x, P.y, [255, 140, 140]); if (P.hp <= 0) leaveCave(false, '倒在了魔窟'); }
function hurtMob(c, m, n) {
  m.hp -= n; m.flash = .12; m.alert = 5; sfxS.hit(); say(Math.round(n) + '', m.x, m.y, [255, 236, 190]);
  if (m.hp > 0) return;
  c.mobs.splice(c.mobs.indexOf(m), 1); c.kills++;
  const coins = (m.elite ? 7 : 2) + Math.round(m.depth * 3); for (let i = 0; i < coins; i++) spawnDrop(c, m.x, m.y, { coin: irand(3, 7) + Math.round(m.depth * 6) });
  if (Math.random() < (m.elite ? 1 : .26)) spawnDrop(c, m.x, m.y, { item: makeItem(m.depth + (m.elite ? .5 : 0)) });
  if (Math.random() < .08) spawnDrop(c, m.x, m.y, { potion: 1 });
}
function spawnDrop(c, x, y, o) { const a = rand(0, TAU), sp = rand(1, 3); c.drops.push(Object.assign({ x, y, z: .4, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, vz: rand(3, 5), age: 0 }, o)); }
function take(c, d) {
  if (d.coin) { c.gold += d.coin; sfxS.coin(); return true; }
  if (d.potion) { c.potions++; say('药水', d.x, d.y, [150, 240, 170]); blip(800, .1); return true; }
  if (c.bag.length >= c.cap) { if (!d.warned) { d.warned = 1; say('背包满了', P.x, P.y, [255, 200, 160]); } return false; }
  c.bag.push(d.item); sfxS.coin(); say(d.item.name, d.x, d.y, hexRGB(RAR[d.item.r].c)); return true;
}
const hexRGB = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
// ---------- the chef, with a bow, and the cat ----------
function drawChef(t) {
  const K = s * .72, g = v.P(P.x, P.y, 0), hop = P.speed ? Math.abs(Math.sin(P.step)) * s * .1 : 0, a = P.inv > 0 && Math.floor(t * 18) % 2 ? .5 : 1;
  glow(g[0], g[1] - K * .6, K * 1.3, [255, 240, 200], .35); fig(g[0], g[1] - hop, K, { kind: 'chef', apron: [220, 80, 80], a });
  const ax = P.draw > 0 ? P.aim : P.face, q0 = v.P(P.x, P.y, .55), q1 = v.P(P.x + ax[0], P.y + ax[1], .55), l = Math.hypot(q1[0] - q0[0], q1[1] - q0[1]) || 1, c = [(q1[0] - q0[0]) / l, (q1[1] - q0[1]) / l], hx = q0[0] + c[0] * K * .42, hy = q0[1] - hop + c[1] * K * .42, n = [-c[1], c[0]], pull = P.draw / .7, r = K * .56;
  const ta = [hx + n[0] * r - c[0] * K * .1, hy + n[1] * r - c[1] * K * .1], tb = [hx - n[0] * r - c[0] * K * .1, hy - n[1] * r - c[1] * K * .1], nock = [hx - c[0] * (K * .1 + pull * K * .46), hy - c[1] * (K * .1 + pull * K * .46)];
  ctx.beginPath(); ctx.moveTo(ta[0], ta[1]); ctx.quadraticCurveTo(hx + c[0] * K * .3, hy + c[1] * K * .3, tb[0], tb[1]); ctx.strokeStyle = css([150, 104, 70], a); ctx.lineWidth = K * .08; ctx.lineCap = 'round'; ctx.stroke(); line([ta, nock, tb], [240, 236, 226], 1, a);
  if (P.draw > 0) { line([nock, [hx + c[0] * K * .42, hy + c[1] * K * .42]], [236, 226, 206], 2); if (pull >= 1) glow(hx, hy, K * .6, [255, 236, 170], .6); }
}
function updateCat(dt, moving, fx = P.x, fy = P.y) {      // the black cat pads after the chef, a little slower, and sits down when it has caught up
  cat.t += dt; const dx = fx - cat.x, dy = fy - cat.y, d = Math.hypot(dx, dy);
  if (d > 12) { cat.x = fx - .8; cat.y = fy + .4; return; }
  if (d > .85) { const st = Math.min(d, 3.3 * dt); cat.x += dx / d * st; cat.y += dy / d * st; const sd = dx - dy; if (Math.abs(sd) > .05) cat.face = sd > 0 ? 1 : -1; cat.sit = 0; }
  else cat.sit = Math.max(cat.sit, 1);
}
function drawMob(m, t) {
  const p = v.P(m.x, m.y, 0), k = s * .72, c = m.flash > 0 ? [255, 255, 255] : tint(m.c), x = p[0], y = p[1];
  if (m.k === 'slime') { const q = 1 + Math.sin(m.ph) * .1; ell(x, y, k * .4, k * .13, [20, 12, 40], .3); ell(x, y - k * .28 * q, k * .42 / q, k * .32 * q, c); circ(x - k * .14, y - k * .32, k * .06, [30, 40, 50]); circ(x + k * .14, y - k * .32, k * .06, [30, 40, 50]); }
  else if (m.k === 'bat') { const f = Math.sin(m.ph * 3) * k * .28, z = k * .95 + Math.sin(m.ph) * k * .1; ell(x, y, k * .22, k * .08, [20, 12, 40], .25); circ(x, y - z, k * .2, c); poly([[x, y - z], [x - k * .55, y - z - f], [x - k * .28, y - z + k * .14]], mix(c, [40, 30, 70], .3)); poly([[x, y - z], [x + k * .55, y - z - f], [x + k * .28, y - z + k * .14]], mix(c, [40, 30, 70], .3)); circ(x - k * .07, y - z, k * .04, [255, 90, 90]); circ(x + k * .07, y - z, k * .04, [255, 90, 90]); }
  else if (m.k === 'archer') fig(x, y, k, { kind: 'demon', body: m.flash > 0 ? [255, 255, 255] : [168, 160, 190], hat: [120, 110, 150] });
  else { const b = m.flash > 0 ? [255, 255, 255] : m.c; v.box(m.x - .42, m.y - .42, 0, .84, .84, 1.1, b); v.box(m.x - .3, m.y - .3, 1.1, .6, .6, .5, mix(b, [255, 255, 255], .2)); const e = v.P(m.x + .3, m.y + .3, 1.36); circ(e[0], e[1], k * .08, [255, 110, 110]); }
  if (m.hp < m.max) { const w = k * (m.elite ? 1.4 : .9), yy = y - k * (m.elite ? 2.3 : 1.5); ctx.fillStyle = css([20, 16, 40], .7); ctx.fillRect(x - w / 2, yy, w, 3); ctx.fillStyle = css([255, 110, 110]); ctx.fillRect(x - w / 2, yy, w * clamp(m.hp / m.max), 3); }
}
function drawFloats() { for (const f of floats) { const p = v.P(f.x, f.y, f.z); text(f.s, p[0], p[1], 14, f.c, clamp(f.t * 2), 'center', 400); } }
function drawFloats() { for (const f of floats) { const p = v.P(f.x, f.y, f.z); text(f.s, p[0], p[1], 14, f.c, clamp(f.t * 2), 'center', 400); } }
function camera(zoom) { s = clamp(Math.min(W, H) / zoom, 26, 58); v.s = s; v.cx = W / 2 - (cam.x - cam.y) * s * C30 + (shake > 0 ? rnd(-1, 1) * shake * 16 : 0); v.cy = H * .58 - (cam.x + cam.y) * s * .5 + (shake > 0 ? rnd(-1, 1) * shake * 16 : 0); }
function drawCave(t) {
  const c = run, st = stats(), r = st.sight, fogK = d => lerp(.06, .66, clamp((d - (r - 3)) / 3));
  camera(9); TINT = [14, 10, 34]; SHADOW = [30, 22, 60];
  ctx.fillStyle = css([12, 9, 26]); ctx.fillRect(0, 0, W, H);
  const span = Math.ceil(Math.max(W, H * 2) / (s * 1.6)) + 3, ci = Math.floor(cam.x), cj = Math.floor(cam.y), i0 = Math.max(0, ci - span), i1 = Math.min(CS - 1, ci + span), j0 = Math.max(0, cj - span), j1 = Math.min(CS - 1, cj + span);
  const onScreen = (i, j) => { const q = v.P(i, j); return q[0] > -s * 3 && q[0] < W + s * 3 && q[1] > -s * 3 && q[1] < H + s * 3; }, fl = c.m;
  // the floor first
  for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) { const o = j * CS + i; if (fl[o] || !c.seen[o] || !onScreen(i, j)) continue; TK = fogK(Math.hypot(i + .5 - P.x, j + .5 - P.y)); v.quad(i, j, 0, 1.01, 1.01, tint((i + j) % 2 ? [92, 84, 136] : [84, 76, 128])); if ((i * 7 + j * 13) % 11 === 0) v.quad(i + .2, j + .3, 0, .5, .4, tint([108, 180, 170]), .22); }
  // everything that stands up, back to front, one diagonal at a time
  const things = new Map(), add = (x, y, f) => { const d = Math.floor(x) + Math.floor(y); if (!things.has(d)) things.set(d, []); things.get(d).push(f); };
  const lit = (x, y) => { const o = Math.floor(y) * CS + Math.floor(x); return c.seen[o] && Math.hypot(x - P.x, y - P.y) < r + 1; };
  for (const p of c.portals) if (c.seen[Math.floor(p.y) * CS + Math.floor(p.x)]) add(p.x, p.y, () => { TK = fogK(Math.hypot(p.x - P.x, p.y - P.y)); const q = v.P(p.x, p.y, .9), g = v.P(p.x, p.y, 0); glow(q[0], q[1], s * 3, [120, 220, 255], .55 + .2 * Math.sin(t * 3)); v.disc(p.x, p.y, 0, .85, .1, [70, 60, 120]); ell(g[0], g[1] - s * .1, s * .56, s * .28, [150, 236, 255], .8); for (let i = 0; i < 4; i++) { const u = (t * .5 + i / 4) % 1, a = i * 1.6 + t; circ(g[0] + Math.cos(a) * s * .4, g[1] - s * .1 - u * s * 1.7 + Math.sin(a) * s * .15, 2, [200, 244, 255], 1 - u); } text(p.name, g[0], g[1] - s * 2.2, 13, [220, 244, 255], .9); if (p.t > 0) { ctx.fillStyle = css([20, 16, 40], .8); ctx.fillRect(g[0] - s, g[1] - s * 2.7, s * 2, 5); ctx.fillStyle = css([150, 240, 255]); ctx.fillRect(g[0] - s, g[1] - s * 2.7, s * 2 * p.t / 2, 5); } });
  for (const b of c.chests) if (c.seen[Math.floor(b.y) * CS + Math.floor(b.x)]) add(b.x, b.y, () => { TK = fogK(Math.hypot(b.x - P.x, b.y - P.y)); const col = b.gold ? [230, 180, 90] : [150, 96, 60]; v.box(b.x - .32, b.y - .24, 0, .64, .48, .34, b.open ? mix(col, [40, 30, 60], .5) : col); if (!b.open) { v.box(b.x - .35, b.y - .27, .34, .7, .54, .12, mix(col, [255, 255, 255], .2)); const q = v.P(b.x, b.y, .4); glow(q[0], q[1], s * (b.gold ? 1.5 : 1), [255, 214, 140], .5); } if (b.t > 0) { const q = v.P(b.x, b.y, 1.2); ctx.fillStyle = css([20, 16, 40], .8); ctx.fillRect(q[0] - s * .6, q[1], s * 1.2, 5); ctx.fillStyle = css([255, 236, 170]); ctx.fillRect(q[0] - s * .6, q[1], s * 1.2 * clamp(b.t / SEARCH), 5); } });
  for (const [x, y] of c.rocks) if (c.seen[Math.floor(y) * CS + Math.floor(x)]) add(x, y, () => { TK = fogK(Math.hypot(x - P.x, y - P.y)); v.pyramid(x - .2, y - .2, 0, .4, .6, [110, 100, 150]); });
  for (const [x, y] of c.torches) if (c.seen[Math.floor(y) * CS + Math.floor(x)]) add(x, y, () => { TK = 0; v.box(x - .04, y - .04, 0, .08, .08, 1, [120, 84, 70]); const q = v.P(x, y, 1.1); glow(q[0], q[1], s * 2.4, [255, 170, 100], .5); circ(q[0], q[1] + Math.sin(t * 9), s * .1, [255, 214, 140]); });
  for (const d of c.drops) if (lit(d.x, d.y)) add(d.x, d.y, () => { const q = v.P(d.x, d.y, d.z + .12 + Math.abs(Math.sin(t * 4 + d.x)) * .08); if (d.coin) { circ(q[0], q[1], s * .1, [255, 206, 90]); circ(q[0] - 1, q[1] - 1, s * .05, [255, 236, 170]); } else if (d.potion) { ctx.fillStyle = css([230, 90, 110]); ctx.fillRect(q[0] - s * .08, q[1] - s * .14, s * .16, s * .22); } else { const cc = hexRGB(RAR[d.item.r].c); glow(q[0], q[1], s * .8, cc, .6); text(KIND[d.item.k], q[0], q[1], s * .34, cc, 1, 'center', 400); } });
  for (const m of c.mobs) if (Math.hypot(m.x - P.x, m.y - P.y) < r + .5) add(m.x, m.y, () => { TK = 0; drawMob(m, t); });
  for (const a of c.arrows) add(a.x, a.y, () => { const q = v.P(a.x, a.y, a.stuck ? .4 : .62), e = v.P(a.x - a.vx * .03, a.y - a.vy * .03, a.stuck ? .4 : .62); line([e, q], [240, 232, 214], 2); });
  for (const b of c.bolts) add(b.x, b.y, () => { const q = v.P(b.x, b.y, .7); glow(q[0], q[1], s * .5, [200, 120, 255], .8); circ(q[0], q[1], s * .08, [240, 200, 255]); });
  add(P.x, P.y, () => { TK = 0; const q = v.P(P.x, P.y, .6); glow(q[0], q[1], s * 3.4, [255, 220, 170], .16); drawChef(t); });
  add(cat.x, cat.y, () => { TK = 0; catFigure(v.P(cat.x, cat.y), s * .42, cat, CAT_BLACK); });
  const ds = i0 + j0, de = i1 + j1;
  for (let d = ds; d <= de; d++) {
    for (let i = Math.max(i0, d - j1); i <= Math.min(i1, d - j0); i++) { const j = d - i, o = j * CS + i; if (!fl[o] || !c.seen[o] || !onScreen(i, j)) continue; if (!((j > 0 && !fl[o - CS]) || (i > 0 && !fl[o - 1]) || (j < CS - 1 && !fl[o + CS]) || (i < CS - 1 && !fl[o + 1]))) continue; TK = fogK(Math.hypot(i + .5 - P.x, j + .5 - P.y)); const front = (i + j) > (Math.floor(P.x) + Math.floor(P.y)); v.box(i, j, 0, 1, 1, front ? .3 : .85, [66, 56, 104]); }
    const list = things.get(d); if (list) for (const f of list) f();
  }
  TK = 0; drawFloats();
  // hud
  const bw = Math.min(W * .24, 190), top = 56;
  ctx.fillStyle = css([20, 16, 40], .7); ctx.fillRect(14, top, bw, 9); ctx.fillStyle = css([240, 100, 110]); ctx.fillRect(14, top, bw * clamp(P.hp / st.hp), 9);
  text(`生命 ${Math.ceil(P.hp)} / ${st.hp}`, 14, top + 19, 12, [255, 255, 255], .85, 'left'); text(`金币 ${c.gold}   背包 ${c.bag.length}/${c.cap}   药水 ${c.potions}`, 14, top + 37, 12.5, [255, 236, 190], .95, 'left');
  drawMap(c);
  if (c.at_) text('撤离中，站住别动……', W / 2, H * .2, 15, [200, 244, 255]);
  text(usePad ? '左摇杆走 · 右摇杆瞄准 · Ⓧ/扳机 射 · Ⓑ 翻滚 · Ⓐ 搜 · Ⓨ 药 · Start 背包' : 'WASD 走 · J 射（自动瞄准）· K/空格 翻滚 · E 搜 · Q 药 · B 背包', W / 2, H - 16, 12.5, [255, 255, 255], .62);
}
function drawMap(c) {      // the little map is turned like the world: a diamond
  const k = Math.min(.82, W * .17 / CS), cx = W - CS * k - 14, cy = 14 + CS * k * .5, q = (i, j) => [cx + (i - j) * k * C30, cy + (i + j) * k * .5];
  poly([q(0, 0), q(CS, 0), q(CS, CS), q(0, CS)], [14, 10, 32], .62);
  for (let j = 0; j < CS; j += 2) for (let i = 0; i < CS; i += 2) if (c.seen[j * CS + i] && !c.m[j * CS + i]) { const p = q(i, j); ctx.fillStyle = css([150, 170, 200], .7); ctx.fillRect(p[0], p[1], 1.6, 1.4); }
  for (const p of c.portals) if (p.found) { const o = q(p.x, p.y); circ(o[0], o[1], 3, [120, 230, 255]); }
  const o = q(P.x, P.y); circ(o[0], o[1], 2.6, [255, 236, 170]);
}

// ---------- doing things ----------
const SEARCH = 1.1;      // seconds it takes to go through a chest
let prompt = null;
const NAME = { stall: '进入面馆', lib: '进入图书馆', bar: '进入酒馆', tower: '进入钟楼' };
function updatePrompt() {
  let p = null;
  if (mode === 'world') { const c = cellOf(player); for (const k in NAME) { const d = DOORS[k]; if (Math.abs(c[0] - d[0]) + Math.abs(c[1] - d[1]) <= 1) p = { t: NAME[k], f: () => goIn(k) }; } }
  else if (mode === 'cave' && run) { let b = null; for (const q of run.chests) if (!q.open && Math.hypot(P.x - q.x, P.y - q.y) < 1.05) b = q;
    if (b) { p = { t: b.t > 0 ? '搜索中…' : '搜箱子（按住）', hold: true }; if (input.act) { b.t += dtNow; if (b.t >= SEARCH) { b.open = true; b.t = 0; sfxS.chest(); const n = irand(2, 3) + (b.gold ? 1 : 0); for (let i = 0; i < 2 + irand(0, 3); i++) spawnDrop(run, b.x, b.y, { coin: irand(4, 9) + Math.round(b.depth * 12) }); for (let i = 0; i < n - 1; i++) spawnDrop(run, b.x, b.y, { item: makeItem(b.depth + (b.gold ? .6 : 0)) }); if (Math.random() < .3) spawnDrop(run, b.x, b.y, { potion: 1 }); } } else b.t = Math.max(0, b.t - dtNow); } }
  prompt = p; const el = $('sdcHint'), tx = p && `${usePad ? 'Ⓐ' : 'E'}  ${p.t}`; if (p && !modal) { if (el.textContent !== tx) el.textContent = tx; el.style.display = 'block'; } else el.style.display = 'none';
}
function act() { if (prompt && !prompt.hold) prompt.f(); }
// ---------- panels ----------
function openPanel(html) { $('sdcPin').innerHTML = html; $('sdcPanel').style.display = 'block'; modal = true; input.shoot = false; input.act = false; pickFocus(); }
function closePanel() { $('sdcPanel').style.display = 'none'; modal = false; }
// menus by keys or pad: one thing has the focus; a direction moves it to the nearest thing that way, and it stays put when a panel redraws
let focusKey = null;
const focusable = () => [...$('sdcPin').querySelectorAll('[data-a]:not(:disabled)')], keyOf = e => e.dataset.a + ':' + (e.dataset.i || '');
function setFocus(e) { for (const o of $('sdcPin').querySelectorAll('.foc')) o.classList.remove('foc'); if (!e) return; e.classList.add('foc'); focusKey = keyOf(e); e.scrollIntoView({ block: 'nearest' }); }
function pickFocus() { const l = focusable(); setFocus(l.find(e => keyOf(e) === focusKey) || l.find(e => e.classList.contains('main')) || l[0]); }
function moveFocus(dx, dy) {
  const l = focusable(), cur = $('sdcPin').querySelector('.foc'); if (!cur) return pickFocus();
  const c = cur.getBoundingClientRect(), cx = c.left + c.width / 2, cy = c.top + c.height / 2; let best = null, bs = 1e9;
  for (const e of l) { if (e === cur) continue; const r = e.getBoundingClientRect(), x = r.left + r.width / 2 - cx, y = r.top + r.height / 2 - cy, along = x * dx + y * dy, side = Math.abs(x * dy) + Math.abs(y * dx); if (along < 4) continue; const sc = along + side * 2.5; if (sc < bs) { bs = sc; best = e; } }
  if (best) { setFocus(best); blip(700, .04, 'sine', .03); }
}
const confirmFocus = () => { const e = $('sdcPin').querySelector('.foc'); if (e) e.click(); };
const backPanel = () => { sel = null; focusKey = null; closePanel(); };
$('sdcPin').addEventListener('click', e => { const b = e.target.closest('[data-a]'); if (b && ACT[b.dataset.a]) ACT[b.dataset.a](b.dataset.i); });
const cellHTML = (it, a, i, sel) => it ? `<div class="cell${sel ? ' sel' : ''}" data-a="${a}" data-i="${i}" style="color:${RAR[it.r].c}">${KIND[it.k]}</div>` : `<div class="cell"></div>`;
let sel = null;
function panelBag() {
  const inCave = mode === 'cave' && !!run, list = inCave ? run.bag : save.stash, s = stats(), e = save.equip, it = sel && (sel.eq ? e[sel.eq] : list[sel.i]);
  const slot = (k, n) => e[k] ? `<div class="cell${sel && sel.eq === k ? ' sel' : ''}" data-a="eq" data-i="${k}" style="color:${RAR[e[k].r].c}">${e[k].name}<small>${n}</small></div>` : `<div class="cell"><small>${n}（空）</small></div>`;
  openPanel(`<h2>${inCave ? '背包' : '仓库'}</h2><div class="sub">金币 ${save.gold}${inCave ? ` · 本趟 +${run.gold}` : ''} · 攻击 ${s.dmg} · 生命 ${s.hp}</div>
  <h3>身上</h3><div class="slots">${slot('bow', '武器')}${slot('armor', '装备')}${slot('acc', '饰品')}</div>
  <h3>${inCave ? `这一趟 ${run.bag.length}/${run.cap}（撤离才算带走）` : `仓库 ${list.length} 件`}</h3><div class="grid">${list.map((x, i) => cellHTML(x, 'it', i, sel && !sel.eq && sel.i === i)).join('') || ''}${Array(Math.max(0, 12 - list.length)).fill('<div class="cell"></div>').join('')}</div>
  <div id="detail">${it ? `<span style="color:${RAR[it.r].c}">${RAR[it.r].n} · ${it.name}</span><br>${itemStat(it)} · 售价 ${it.v}` : '选一件东西查看。'}</div>
  <div class="row">${it && !sel.eq && it.k !== 'gem' && !inCave ? '<button class="act main" data-a="wear">装备</button>' : ''}${it && sel.eq && !inCave ? '<button class="act" data-a="off">卸下</button>' : ''}<button class="act" data-a="close">关闭</button></div>`);
}
function panelBar() {
  const sum = save.stash.reduce((a, b) => a + b.v, 0);
  sel = null; focusKey = null; openPanel(`<h2>老板</h2><div class="sub">“又活着回来了。”<br>金币 ${save.gold} · 药水 ${save.potions} · 下过 ${save.runs} 次魔窟，活着出来 ${save.out} 次</div>
  <div class="row"><button class="act main" data-a="potion" ${save.gold < 25 ? 'disabled' : ''}>买药水 · 25 金币</button></div>
  <div class="row"><button class="act" data-a="sellgem" ${save.stash.some(i => i.k === 'gem') ? '' : 'disabled'}>卖掉所有宝石</button><button class="act" data-a="sellall" ${save.stash.length ? '' : 'disabled'}>卖掉全部仓库（${sum}）</button></div>
  <div class="row"><button class="act" data-a="close">走开</button></div>`);
}
function panelTower() { focusKey = null; openPanel(`<h2>钟楼</h2><div class="sub">钟摆后面有一道门，通往魔窟。<br>那里一片迷雾，宝箱和怪物都藏在里面。<br>带出来的才算你的；倒下了，这一趟的东西全部丢掉。</div><div class="row"><button class="act main" data-a="go">传送到魔窟</button><button class="act" data-a="close">算了</button></div>`); }
function panelResult(ok, title, r, n, v) {
  focusKey = null; const names = r.bag.slice(0, 18).map(i => `<span style="color:${RAR[i.r].c}">${i.name}</span>`).join('、');
  openPanel(`<h2>${ok ? '撤离成功' : '没能回来'}</h2><div class="sub">${ok ? `从${title}回到了酒馆` : title}</div><div class="sub">${ok ? `带回金币 ${r.gold}，物品 ${n} 件（价值 ${v}）` : `丢失金币 ${r.gold}，物品 ${n} 件（价值 ${v}）`}<br>${names}<br>击败怪物 ${r.kills} · 用时 ${Math.floor(r.time / 60)} 分 ${Math.floor(r.time % 60)} 秒</div><div class="row"><button class="act main" data-a="close">回到酒馆</button></div>`);
}
const ACT = {
  close: () => { sel = null; closePanel(); }, go: () => { closePanel(); fade = 1; enterCave(); },
  it: i => { sel = { i: +i }; panelBag(); }, eq: k => { sel = { eq: k }; panelBag(); },
  wear: () => { const it = save.stash[sel.i], old = save.equip[it.k]; save.stash.splice(sel.i, 1); save.equip[it.k] = it; if (old) save.stash.push(old); sel = null; persist(); panelBag(); },
  off: () => { const k = sel.eq; save.stash.push(save.equip[k]); save.equip[k] = null; sel = null; persist(); panelBag(); },
  potion: () => { if (save.gold >= 25) { save.gold -= 25; save.potions++; persist(); sfxS.coin(); panelBar(); } },
  sellgem: () => { const g = save.stash.filter(i => i.k === 'gem'); save.gold += g.reduce((a, b) => a + b.v, 0); save.stash = save.stash.filter(i => i.k !== 'gem'); persist(); sfxS.coin(); panelBar(); },
  sellall: () => { save.gold += save.stash.reduce((a, b) => a + b.v, 0); save.stash = []; persist(); sfxS.coin(); panelBar(); },
};

// ---------- input: keyboard or gamepad ----------
const ROOM = { stall: 1, bar: 1, lib: 1, tower: 1 }, MOVE = { KeyA: 'l', ArrowLeft: 'l', KeyD: 'r', ArrowRight: 'r', KeyW: 'u', ArrowUp: 'u', KeyS: 'd', ArrowDown: 'd' }, NAV = { KeyA: [-1, 0], ArrowLeft: [-1, 0], KeyD: [1, 0], ArrowRight: [1, 0], KeyW: [0, -1], ArrowUp: [0, -1], KeyS: [0, 1], ArrowDown: [0, 1] };
let usePad = false; const ptr = { x: 0, y: 0, down: false, seen: false };
const openBag = () => { sel = null; focusKey = null; panelBag(); };
function press(on) {      // in a room, E or Ⓐ is a finger on the cursor, so the room's own play works unchanged
  if (on === ptr.down) return; ptr.down = on; const el = document.elementFromPoint(ptr.x, ptr.y) || cv, o = { clientX: ptr.x, clientY: ptr.y, bubbles: true, pointerId: 77, pointerType: 'touch', isPrimary: true };
  if (el === cv) cv.dispatchEvent(new PointerEvent(on ? 'pointerdown' : 'pointerup', o)); else if (on) el.click();
}
const leaveRoom = () => { if (mode === 'bar') leaveBar(); else if (mode === 'lib') leaveLib(); else if (mode === 'stall') leaveStall(); };
addEventListener('keydown', e => {
  if (['Space', 'Tab', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) e.preventDefault();
  usePad = false; e.stopImmediatePropagation();
  if (modal) { if (NAV[e.code]) moveFocus(...NAV[e.code]); else if (!e.repeat && ['Enter', 'KeyE', 'Space', 'KeyJ'].includes(e.code)) confirmFocus(); else if (!e.repeat && ['Escape', 'KeyB', 'Tab', 'KeyK'].includes(e.code)) backPanel(); return; }
  if (e.repeat) return;
  if (MOVE[e.code]) input[MOVE[e.code]] = 1;
  if (ROOM[mode]) { if (e.code === 'KeyE' || e.code === 'Enter' || e.code === 'Space') press(true); if (e.code === 'Escape' || e.code === 'KeyQ') leaveRoom(); if (mode === 'bar' && e.code === 'KeyT') panelBar(); if (mode === 'bar' && (e.code === 'KeyB' || e.code === 'Tab')) openBag(); return; }
  if (e.code === 'Space' || e.code === 'KeyK') input.dash = true;
  if (e.code === 'KeyE' || e.code === 'Enter') { input.act = true; act(); }
  if (e.code === 'KeyQ') input.potion = true;
  if (e.code === 'KeyB' || e.code === 'Tab') openBag();
  if (e.code === 'KeyJ') input.shoot = true;
}, true);
addEventListener('keyup', e => { if (MOVE[e.code]) input[MOVE[e.code]] = 0; if (e.code === 'KeyE' || e.code === 'Enter' || e.code === 'Space') { input.act = false; press(false); } if (e.code === 'KeyJ') input.shoot = false; }, true);
addEventListener('blur', () => { input.l = input.r = input.u = input.d = 0; input.shoot = input.act = false; press(false); });
// the standard gamepad: left stick or d-pad to move, right stick to aim, Ⓐ use, Ⓧ or the triggers to draw the bow, Ⓑ roll or leave a room, Ⓨ potion or the keeper, Start or Back the backpack
const gp = { prev: [], navT: 0, held: false };
function pollPad(dt) {
  const list = navigator.getGamepads ? [...navigator.getGamepads()].filter(Boolean) : [], g = list[0];
  if (!g) { if (usePad) { input.jx = input.jy = input.ax = input.ay = 0; if (gp.held) { input.shoot = input.act = false; gp.held = false; } } return; }
  const on = i => !!(g.buttons[i] && (g.buttons[i].pressed || g.buttons[i].value > .4)), edge = i => on(i) && !gp.prev[i], dz = v => Math.abs(v) < .2 ? 0 : v;
  const lx = dz(g.axes[0] || 0), ly = dz(g.axes[1] || 0), rx = dz(g.axes[2] || 0), ry = dz(g.axes[3] || 0), dx = (on(15) ? 1 : 0) - (on(14) ? 1 : 0), dy = (on(13) ? 1 : 0) - (on(12) ? 1 : 0);
  if (lx || ly || rx || ry || dx || dy || g.buttons.some(b => b.pressed)) { if (!usePad) usePad = true; wakeAudio(true); }
  if (usePad) {
    if (modal) { input.jx = input.jy = 0; gp.navT -= dt; const nx = dx || (Math.abs(lx) > .5 ? Math.sign(lx) : 0), ny = dy || (Math.abs(ly) > .5 ? Math.sign(ly) : 0); if (nx || ny) { if (gp.navT <= 0) { moveFocus(nx, nx ? 0 : ny); gp.navT = .2; } } else gp.navT = 0; if (edge(0)) confirmFocus(); else if (edge(1) || edge(9) || edge(8)) backPanel(); }
    else if (ROOM[mode]) { input.jx = lx + dx; input.jy = ly + dy; press(on(0)); if (edge(1)) leaveRoom(); if (mode === 'bar' && edge(3)) panelBar(); if (mode === 'bar' && (edge(9) || edge(8))) openBag(); }
    else { input.jx = lx + dx; input.jy = ly + dy; input.ax = rx; input.ay = ry; gp.held = true; input.shoot = on(2) || on(7) || on(6) || on(5); input.act = on(0); if (edge(0)) act(); if (edge(1) || edge(4)) input.dash = true; if (edge(3)) input.potion = true; if (edge(9) || edge(8)) openBag(); }
  }
  gp.prev = g.buttons.map(b => b.pressed || b.value > .4);
}

// ---------- hooks the game calls ----------
let dtNow = 1 / 60;
function tickWorld(dt) {      // the town: the chef walks by keys or stick; the cat follows
  const mx = (input.r - input.l) + input.jx, my = (input.d - input.u) + input.jy, mag = Math.min(1, Math.hypot(mx, my)); player.moving = false;
  if (mag > .12 && !modal) { const w = screenToWorld(mx, my), sp = 3.6 * mag * dt, ok = (x, y) => { const i = Math.floor(x), j = Math.floor(y); return walkable(i, j); }, m = .22, free = (x, y) => ok(x - m, y - m) && ok(x + m, y - m) && ok(x - m, y + m) && ok(x + m, y + m); player.path = []; if (free(player.x + w[0] * sp, player.y)) player.x += w[0] * sp; if (free(player.x, player.y + w[1] * sp)) player.y += w[1] * sp; player.moving = true; }
  updateCat(dt, player.moving, player.x, player.y); updatePrompt();
}
function tickRoom(dt) {      // a room: the cursor is the finger
  if (!ptr.seen) { ptr.x = W / 2; ptr.y = H * .6; ptr.seen = true; }
  const mx = (input.r - input.l) + input.jx, my = (input.d - input.u) + input.jy, sp = 460 * dt; if (modal) return; ptr.x = clamp(ptr.x + mx * sp, 0, W); ptr.y = clamp(ptr.y + my * sp, 0, H);
  if (ptr.down && (mx || my)) { const el = document.elementFromPoint(ptr.x, ptr.y); if (el === cv) cv.dispatchEvent(new PointerEvent('pointermove', { clientX: ptr.x, clientY: ptr.y, bubbles: true, pointerId: 77, pointerType: 'touch' })); }
  $('sdcHint').style.display = 'none';
}
function overlay() {      // drawn over the room or the town
  if (ROOM[mode]) { ctx.setTransform(DPR, 0, 0, DPR, 0, 0); circ(ptr.x, ptr.y, 15, [255, 255, 255], ptr.down ? .34 : .16); ctx.beginPath(); ctx.arc(ptr.x, ptr.y, 15, 0, TAU); ctx.strokeStyle = css([255, 236, 190], .95); ctx.lineWidth = 2; ctx.stroke(); circ(ptr.x, ptr.y, 2.5, [255, 236, 190]); text(mode === 'bar' ? (usePad ? '摇杆移动光标 · Ⓐ 点击 · Ⓨ 老板 · Start 仓库 · Ⓑ 出门' : '方向键移动光标 · E 点击 · T 老板 · B 仓库 · Esc 出门') : (usePad ? '摇杆移动光标 · Ⓐ 点击 · Ⓑ 出门' : '方向键移动光标 · E 点击 · Esc 出门'), W / 2, H - 14, 12.5, [255, 255, 255], .7); }
  else if (mode === 'world') { ctx.setTransform(DPR, 0, 0, DPR, 0, 0); text(usePad ? '左摇杆走路 · Ⓐ 进门 · 去钟楼门口进入魔窟' : 'WASD 走路 · E 进门 · 去钟楼门口进入魔窟', W / 2, H - 14, 12.5, [255, 255, 255], .7); }
}
function frame(dt, T) { dtNow = dt; if (!MANUAL) update(dt); ctx.setTransform(DPR, 0, 0, DPR, 0, 0); drawCave(T); $('sdcRot').style.display = 'none'; }
const MANUAL = location.search.includes('manual');
window.SDC = { tower: panelTower, frame, overlay, poll: dt => { pollPad(dt); dtNow = dt; if (mode === 'world') { if (!MANUAL) tickWorld(dt); } else if (ROOM[mode]) tickRoom(dt); },
  worldObjs: (objs, wv, sc) => objs.push({ k: cat.x + cat.y + .02, d: () => catFigure(wv.P(cat.x, cat.y), sc * .42, cat, CAT_BLACK) }), P, cat, input, save, ptr, get run() { return run; }, enterCave, leaveCave, panelTower, panelBar, panelBag, closePanel, tick: q => { for (let t = 0; t < q; t += 1 / 60) { dtNow = 1 / 60; if (mode === 'cave') update(1 / 60); else if (mode === 'world') tickWorld(1 / 60); else tickRoom(1 / 60); } }, genCave };
})();
