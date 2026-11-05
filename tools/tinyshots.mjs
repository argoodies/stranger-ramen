import { chromium } from '/tmp/node_modules/playwright/index.mjs';
const OUT = '/dev/shm/botc/tinyshots/en-US';
const b = await chromium.launch();
for (const [dev, vw, vh, dsf] of [['iphone', 430, 932, 3], ['ipad', 1024, 1366, 2]]) {
  const scene = async (n, fn) => {
    const ctx = await b.newContext({ viewport: { width: vw, height: vh }, deviceScaleFactor: dsf, isMobile: dev === 'iphone', hasTouch: true, locale: 'en-US' });
    const p = await ctx.newPage(), errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.addInitScript(() => { window.webkit = { messageHandlers: { gc: { postMessage: () => {} } } }; });
    await p.goto('file:///root/clocktower-ramen/deploy/3b.html?lang=en'); await p.addStyleTag({ content: '#dbgtag{display:none!important}' }); await p.waitForTimeout(7000);
    await fn(p); await p.screenshot({ path: `${OUT}/${dev}_${n}.png` }); console.log(dev, n, errs.join(';') || 'ok'); await ctx.close();
  };
  const start = async p => { await p.evaluate(() => { const v = new View(W / 2, H * .6, Math.min(W / 11.2, (H - 250) / 8.6)), q = v.P(0, 0, .3); $('c').dispatchEvent(new PointerEvent('pointerdown', { clientX: q[0], clientY: q[1] - v.s * 1.25 * .8, bubbles: true, pointerId: 1 })); }); await p.waitForTimeout(4500); };
  await scene(1, async p => {});
  await scene(2, async p => { const bk = await p.evaluate(() => window.__3b.book); await p.mouse.click(bk[0], bk[1]); await p.waitForTimeout(1500); });
  await scene(3, async p => { await start(p); await p.evaluate(() => { BG.roles = ['sailor', 'pukka', 'heretic']; BG.alive = [true, true, true]; BG.showMine = true; BG.reveal = false; BG.isNight = true; BG.drunk = BG.poisoned = BG.deadPoison = -1; BG.votes = null; }); await p.waitForTimeout(2500); await p.evaluate(() => { BG.bubble = { who: 'st', text: S().pickSailor }; }); await p.waitForTimeout(800); });
  await scene(4, async p => { await start(p); await p.evaluate(() => { BG.roles = ['heretic', 'sailor', 'pukka']; BG.alive = [true, true, true]; BG.showMine = true; BG.reveal = false; BG.isNight = false; BG.dark = 0; BG.drunk = BG.poisoned = BG.deadPoison = -1; BG.votes = [true, null, true]; BG.voteOrder = [0, 2]; }); await p.waitForTimeout(1200); await p.evaluate(() => { BG.bubble = { who: 2, text: S().iVote }; }); await p.waitForTimeout(800); });
  await scene(5, async p => { await start(p); await p.evaluate(() => { BG.roles = ['sailor', 'heretic', 'pukka']; BG.alive = [true, true, false]; BG.showMine = true; BG.isNight = false; BG.dark = 0; BG.drunk = 1; BG.poisoned = -1; BG.deadPoison = -1; BG.pukkaSober = false; BG.votes = null; BG.reveal = true; BG.revealT = 9; }); await p.waitForTimeout(1500); await p.evaluate(() => { BG.reveal = true; BG.revealT = 9; BG.bubble = { who: 'st', text: S().goodWins }; }); await p.waitForTimeout(800); });
}
await b.close();
