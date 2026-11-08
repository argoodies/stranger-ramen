import { chromium } from '/tmp/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 400, height: 700 } });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto('file:///root/clocktower-ramen/index.html?lang=hans#night'); await p.waitForTimeout(1500);
const out = await p.evaluate(() => {
  const keep = ctx; G.n = 1; G.t = HALF + 20; TINT = [40, 30, 96]; TK = .2; SHADOW = [58, 40, 96];
  const v = wv, c = document.createElement('canvas'); c.width = c.height = 3000; ctx = c.getContext('2d');
  const s = 330, cx = -4.17, cy = 2.15; v.s = s; v.cx = 1500 - (cx - cy) * s * C30; v.cy = 2000 - (cx + cy) * s * .5;
  drawHouse(v, 3); ctx = keep; return c.toDataURL('image/png');
});
fs.writeFileSync('/dev/shm/sicon3/house.png', Buffer.from(out.split(',')[1], 'base64')); console.log(errs.join(';') || 'ok'); await b.close();
