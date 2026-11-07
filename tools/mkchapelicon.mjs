// The Starcross Town app icon (2026-11-07): the church alone, without its slab, rendered by the game's own drawChapel at night (b_chapel.png);
// it was then centred at 780 px on the night sky with stars and a warm glow in a 1024 px square: assets/logo/app_icon_chapel.png. The other buildings were the alternatives.
import { chromium } from '/tmp/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 400, height: 700 } });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto('file:///root/clocktower-ramen/index.html?lang=hans'); await p.waitForTimeout(1500);
const out = await p.evaluate(() => {
  const res = {}, keep = ctx; G.n = 1; G.t = HALF + 20;
  TINT = [40, 30, 96]; TK = .2; SHADOW = [58, 40, 96];
  const v = wv, t = 3;
  const make = (name, cx, cy, s, f) => { try { const c = document.createElement('canvas'); c.width = c.height = 3200; ctx = c.getContext('2d'); v.s = s; v.cx = 1600 - (cx - cy) * s * C30; v.cy = 2200 - (cx + cy) * s * .5; f(); res[name] = c.toDataURL('image/png'); } catch (e) { res[name + '_ERR'] = e.message + e.stack; } };
  const tile = (x, y, w, d, z = 0) => { v.box(x, y, z - .5, w, d, .5, PAL.isl); };
  make('b_tower', 0, 0, 150, () => { tile(-2, -2, 4, 4); drawTower(v, t); });
  make('b_house', -4.17, 2.15, 330, () => { tile(-5.3, 1.0, 2.3, 2.3); drawHouse(v, t); });
  make('b_bar', 6.65, 3.5, 330, () => { drawBarHouse(v, t); });
  make('b_chapel', 10 + CDX, CDY, 260, () => { drawChapel(v, t); });
  make('b_obs', 2.85, -3.75, 300, () => { tile(1.8, -4.8, 2.1, 2.1); const s = v.s; v.box(2.2, -4.4, 0, 1.3, 1.3, 2.4, PAL.stone); { const dp = v.F('L', [2.85, -3.1, 0], 0, .4); glow(dp[0], dp[1], v.s, [255, 214, 140], .7); } v.arch('L', [2.85, -3.1, 0], .4, .56, [255, 214, 140]); const c = v.P(2.85, -3.75, 2.4), R = .6 * s * 1.2247, [, cl, cr] = v.sh(PAL.roof); ell(c[0], c[1], R, R * .577, cr); ctx.beginPath(); ctx.arc(c[0], c[1], R, Math.PI, TAU); ctx.fillStyle = css(cr); ctx.fill(); ctx.beginPath(); ctx.moveTo(c[0], c[1]); ctx.arc(c[0], c[1], R, Math.PI, Math.PI * 1.58); ctx.closePath(); ctx.fillStyle = css(cl); ctx.fill(); });
  ctx = keep; return res;
});
for (const [k, u] of Object.entries(out)) { if (k.endsWith('_ERR')) { console.log(k, u); continue; } fs.writeFileSync(`/dev/shm/sicon2/${k}.png`, Buffer.from(u.split(',')[1], 'base64')); }
console.log(Object.keys(out).join(' '), errs.join(';') || 'ok'); await b.close();
