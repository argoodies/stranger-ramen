#!/usr/bin/env node
// A playthrough from a blank save, for looking at the game after each change (MELO 2026-11-18): the real game in a headless
// browser, driven step by step through its core loop (title, town, ramen shop, a customer served, the coin taken, the coffee
// house, the lucky draw, selling, the library, the tower, the church fight), a screenshot after each step, by day and at night.
// Taps go through the canvas like a finger's where the game shows where a thing is; otherwise the game's own entry points.
// Time is stepped by hand (frame()), so every run plays the same.
//
// usage: node tools/playthrough.cjs [outDir=playthrough] [page=index.html]
// writes  <outDir>/NN_step.png, <outDir>/report.json (each step: ok, notes), <outDir>/report.md, <outDir>/errors.txt
// exits 1 if the page threw an error or a step failed. Needs the `playwright` package (PW=<path> to point at another copy).
const path = require('path'), fs = require('fs');
const { chromium } = require(process.env.PW || 'playwright');
const OUT = path.resolve(process.argv[2] || 'playthrough'), PAGE = path.resolve(process.argv[3] || 'index.html');

(async () => {
  fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch({ args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: false });
  const errors = [], steps = []; let n = 0;
  p.on('pageerror', e => errors.push('pageerror: ' + e.message + ' ' + (e.stack || '').split('\n')[1]));
  p.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await p.goto('file://' + PAGE); await p.evaluate(() => { localStorage.clear(); }); await p.reload(); await p.waitForTimeout(1500);
  await p.evaluate(() => { window.requestAnimationFrame = () => 0; });      // the clock is ours from here on

  const js = (f, a) => p.evaluate(f, a);
  const tick = (sec = .5) => js(s => { for (let i = 0; i < Math.round(s * 30); i++) frame(last + 1000 / 30); }, sec);
  const tap = async (x, y) => { await p.mouse.move(x, y); await p.mouse.down(); await p.mouse.up(); await tick(.1); };
  const state = () => js(() => ({ mode, n: +G.n.toFixed(2), coins: save.coins, cards: Object.assign({}, save.cards), say: (stall.ownSayT > 0 && stall.ownSay) || (bar.mySayT > 0 && bar.mySay) || (bar.keepSayT > 0 && bar.keepSay) || (bar.boxSayT > 0 && bar.boxSay) || '' }));
  const step = async (name, fn) => {
    const rec = { n: ++n, name, ok: true, notes: [] }, note = s => rec.notes.push(s);
    try { const r = await fn(note); if (r === false) rec.ok = false; } catch (e) { rec.ok = false; note('threw: ' + e.message); }
    rec.state = await state().catch(() => null);
    const file = `${String(n).padStart(2, '0')}_${name}.png`; await p.screenshot({ path: path.join(OUT, file) }); rec.shot = file;
    steps.push(rec); console.log(`${rec.ok ? 'ok  ' : 'FAIL'} ${file} ${rec.notes.join('; ')}`);
    return rec.ok;
  };
  const until = async (cond, sec, dt = .2) => { for (let t = 0; t < sec; t += dt) { if (await js(cond)) return true; await tick(dt); } return js(cond); };

  await step('title_day', async note => { await js(() => { setLang('hans'); G.n = 0; nWant = () => 0; titleT0 = 5; }); await tick(2); const m = await js(() => mode); note('mode ' + m); return m === 'title'; });
  await step('town', async note => { await tap(195, 600); await tick(2); const m = await js(() => mode); note('after a tap: ' + m); if (m === 'title') { await js(() => { mode = 'world'; $('title').style.display = 'none'; }); note('a tap did not leave the title, forced'); return false; } return true; });

  // the ramen shop: walk to its door, a customer comes, cook and serve their order
  await step('ramen_shop', async note => { await js(() => goDoor('stall')); const ok = await until(() => mode === 'stall', 30); await tick(2); note(ok ? 'walked in' : 'never got in'); return ok; });
  await step('customer_waits', async note => { await js(() => { stall.spawn = 0; }); const ok = await until(() => stall.seats.some(c => c && c.state === 'wait'), 25); note(ok ? 'order: ' + JSON.stringify(await js(() => stall.seats.find(c => c && c.state === 'wait').want)) : 'no customer came'); return ok; });
  await step('cooking', async note => { const ok = await js(() => act('boil')); await until(() => stall.pot === 'done', 30); note('pot ' + await js(() => stall.pot)); return ok; });
  await step('bowl_made', async note => {
    const ok = await js(() => { const i = waiting()[0], w = stall.seats[i].want, r = [act('scoop'), act('put'), act('soup')]; for (const k of MORE) for (let j = 0; j < (w[k] === true ? 1 : +w[k] || 0); j++) r.push(act(k)); return r.every(Boolean); });
    await tick(1); note('bowl ' + JSON.stringify(await js(() => stall.bowl))); return ok; });
  await step('served', async note => { const ok = await js(() => act('serve')); await tick(1.5); note(ok ? 'served' : 'serve refused'); return ok; });
  await step('coin_left', async note => { const ok = await until(() => stall.coins.some(Boolean), 20); await tick(1); note(ok ? 'a coin on the counter' : 'no coin (customer unhappy?)'); return ok; });
  await step('coin_taken', async note => {
    const at = await js(() => { const c = stall.coins.find(c => c && c.at); return c && c.at; }); if (!at) { note('no coin to tap'); return false; }
    const c0 = await js(() => save.coins); await tap(at[0], at[1]); await tick(1.5); const c1 = await js(() => save.coins); note(`coins ${c0} -> ${c1}`); return c1 === c0 + 1; });
  await step('backpack_in_shop', async note => { await js(() => document.getElementById('bag').click()); await tick(.8); const o = await js(() => bag.open); note('open ' + o); await js(() => { bag.open = false; }); return o; });
  await step('ramen_shop_night', async () => { await js(() => { G.n = 1; nWant = () => 1; }); await tick(1.5); });

  // the coffee house: take the iced coffee, a pull of the lucky draw, then the shipping box
  await step('coffee_house', async note => { await js(() => { G.n = 0; nWant = () => 0; G.t = 1; bar.taken = null; save.coffeeTaken = null; leaveStall(); }); await tick(1); await js(() => goDoor('bar')); const ok = await until(() => mode === 'bar', 30); await tick(2); note(ok ? 'walked in' : 'never got in'); return ok; });
  await step('iced_coffee', async note => {
    const h = await js(() => BARHIT.take); if (!h) { note('no coffee out (already taken this half-day?)'); return true; }
    const d0 = await js(() => cardN('coffee')); await tap(h[0], h[1]); await tick(2); const d1 = await js(() => cardN('coffee')); note(`coffee ${d0} -> ${d1}`); return d1 === d0 + 1; });
  await step('lucky_draw', async note => {
    const h = await js(() => BARHIT.slot), c0 = await js(() => save.coins); await tap(h[0], h[1]);
    const went = await until(() => bar.slot.st !== 'idle', 15); await until(() => bar.slot.st === 'idle', 15); await tick(1.5);
    const c1 = await js(() => save.coins), win = await js(() => bar.slot.win); note(`coins ${c0} -> ${c1}, ${win ? 'won ' + win : 'no win'}`); return went && c1 === c0 - 1; });
  await step('sell_mode', async note => { const h = await js(() => BARHIT.ship); await tap(h[0], h[1]); await tick(.5); const said = await js(() => bar.boxSayT > 0 ? bar.boxSay : ''), shut = await js(() => !bag.open); await tap(h[0], h[1]); await tick(1); const s = await js(() => bag.open && bag.sell); note(`the box says: ${said}; still shut after one tap: ${shut}; after a second, selling ${s}`); return shut && s; });
  await step('sell_tap', async note => {
    const has = await js(() => { save.cards.guard = (save.cards.guard || 0) + 1; return true; }); await tick(.3);
    const hit = await js(() => { const c = bag.cell, h = bag.hits.find(h => h[2] === 'guard'); return h && [h[0] + c / 2, h[1] + c / 2]; }); if (!hit) { note('ring not in the backpack'); return false; }
    await tap(hit[0], hit[1]); await tick(.5); const r = await js(() => [bag.sel, bar.boxSayT > 0 || bar.mySayT > 0]); note(`picked ${r[0]}, ${r[1] ? 'a bubble came up' : 'nothing said'}`); return has && r[0] === 'guard' && !r[1]; });
  await step('sold', async note => {
    const hit = await js(() => { const c = bag.cell, h = bag.hits.find(h => h[2] === 'guard'); return h && [h[0] + c / 2, h[1] + c / 2]; }), box = await js(() => BARHIT.ship), c0 = await js(() => save.coins);
    await p.mouse.move(hit[0], hit[1]); await p.mouse.down(); for (let i = 1; i <= 12; i++) { await p.mouse.move(hit[0] + (box[0] - hit[0]) * i / 12, hit[1] + (box[1] + 10 - hit[1]) * i / 12); await tick(.05); }
    await tick(.4); await p.mouse.up(); await tick(2); const c1 = await js(() => save.coins); note(`coins ${c0} -> ${c1}`); return c1 === c0 + 5; });
  await step('backpack', async note => { await js(() => { bag.open = bag.sell = false; }); await tick(.3); await js(() => document.getElementById('bag').click()); await tick(.8); return js(() => bag.open); });

  // the other places
  for (const [name, door, inMode] of [['library', 'lib', 'lib'], ['tower', 'tower', 'tower'], ['church', 'church', 'church']])
    await step(name, async note => { await js(() => { bag.open = bag.sell = false; mode = 'world'; fade = 0; player.path = []; player.enter = false; }); await tick(.5); await js(d => goDoor(d), door); const ok = await until(m => mode === m, 40, .25).catch(() => false) || await js(m => mode === m, inMode); await tick(2); note(ok ? 'in' : 'never got in, mode ' + await js(() => mode)); return ok; });
  await step('church_fight', async note => {
    await js(() => { const c = church; c.p.x = TORCH[0] + .6; c.p.y = TORCH[1]; }); const q = await js(() => chv.P(TORCH[0], TORCH[1], 1)); await tap(q[0], q[1]);
    const ok = await until(() => church.fight, 20); await tick(4); note(ok ? 'fight on, foes ' + await js(() => church.foes.length) : 'the torch did not start a fight'); return ok; });
  await step('town_night', async () => { await js(() => { church.fight = false; church.foes = []; mode = 'world'; fade = 0; G.n = 1; nWant = () => 1; zoomTarget = 1; }); await tick(3); });
  await step('title_night', async () => { await js(() => { mode = 'title'; titleT0 = 5; }); await tick(2); });

  const failed = steps.filter(s => !s.ok);
  fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify({ page: PAGE, when: new Date().toISOString(), steps, errors }, null, 1));
  fs.writeFileSync(path.join(OUT, 'errors.txt'), errors.join('\n') || 'none\n');
  fs.writeFileSync(path.join(OUT, 'report.md'), `# Playthrough\n\n${steps.length - failed.length}/${steps.length} steps ok, ${errors.length} page errors\n\n| # | step | ok | notes |\n|---|---|---|---|\n` + steps.map(s => `| ${s.n} | ${s.name} | ${s.ok ? '✓' : '✗'} | ${s.notes.join('; ').replace(/\|/g, '/')} |`).join('\n') + '\n\n' + (errors.length ? '## Errors\n\n' + errors.map(e => '- ' + e).join('\n') + '\n' : ''));
  console.log(`\n${steps.length - failed.length}/${steps.length} steps ok, ${errors.length} page errors`);
  await b.close(); process.exit(failed.length || errors.length ? 1 : 0);
})();
