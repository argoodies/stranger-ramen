const { chromium } = require('/tmp/node_modules/playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1600, height: 1600 }, deviceScaleFactor: 3 }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file:///root/clocktower-ramen/index.html?lang=hans#night'); await p.waitForTimeout(600);
  await p.evaluate(() => { player.x = 1; player.y = 6; player.path = []; document.getElementById('top').style.display = 'none'; try { npcs.length = 0; } catch (e) {} });
  await p.waitForTimeout(1500);
  const c = await p.evaluate(() => { const q = wv.P(-4.05, 3.35, .9), z = wv.s * 7.0; return { x: q[0] - z / 2, y: q[1] - z / 2, width: z, height: z, n: typeof npcs }; });
  console.log(JSON.stringify(c)); await p.screenshot({ path: '/dev/shm/rt/icon_world.png', clip: c }); console.log(errs.join('\n') || 'no errors'); await b.close(); })();
