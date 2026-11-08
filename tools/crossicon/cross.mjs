import { chromium } from '/tmp/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 400, height: 400 } });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto('file:///root/clocktower-ramen/index.html?lang=hans'); await p.waitForTimeout(1500);
const out = await p.evaluate(() => {
  const res = {}, keep = ctx;
  const make = (n, f) => { const c = document.createElement('canvas'); c.width = c.height = 1024; ctx = c.getContext('2d'); f(512); res[n] = c.toDataURL('image/png'); };
  make('b_item', C => drawItem('guard', C, C + 40, 470));
  make('b_up', C => { const r = 330, k = .86 * r; ctx.translate(C, C); ctx.rotate(-.6); drawGuard(-.047 * k, .353 * k, r); });
  make('b_tilt', C => { const r = 320, k = .86 * r; drawGuard(C - .047 * k, C + .353 * k, r); });
  ctx = keep; return res;
});
for (const [k, u] of Object.entries(out)) fs.writeFileSync(`/dev/shm/sicon3/${k}.png`, Buffer.from(u.split(',')[1], 'base64'));
console.log(errs.join(';') || 'ok'); await b.close();
