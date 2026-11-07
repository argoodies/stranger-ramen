// The Starcross Town app icon (2026-11-07): the whole island at night, no moon, birds, chef or townsfolk. Screenshots the game to /dev/shm/sicon/island_night.png; the framed 1024 px result is kept in assets/logo/app_icon_island.png.
import { chromium } from '/tmp/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 512, height: 512 }, deviceScaleFactor: 4 });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto('file:///root/clocktower-ramen/index.html?lang=hans#far'); await p.waitForTimeout(3000);
await p.addStyleTag({ content: 'body > *:not(canvas){display:none!important} #c{display:block!important}' });
await p.evaluate(() => {
  G.n = 1; G.t = HALF + 20;      // night
  const og = glow; glow = function (x, y, r, c, a) { if (Math.abs(x - W * .8) < 1 && Math.abs(y - H * .13) < 1) return; return og.apply(this, arguments); };      // no moon glow
  drawOrb = () => {};      // no moon
  const ol = line; line = function (pts, c, w) { if (pts.length === 3 && w === 2 && c && c[0] === 200 && c[1] === 190 && c[2] === 220) return; return ol.apply(this, arguments); };      // no birds
  if (typeof tapHint === 'function') tapHint = () => {};
  player.x = player.y = 200; player.path = [];      // the chef off the island
  setInterval(() => { npcs.length = 0; G.n = 1; }, 50);      // nobody about, always night
});
await p.waitForTimeout(4000);
await p.screenshot({ path: '/dev/shm/sicon/island_night.png' });
console.log(errs.join(';') || 'ok'); await b.close();
