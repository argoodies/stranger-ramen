import { chromium } from '/tmp/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 390, height: 844 } });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto('file:///root/clocktower-ramen/index.html?lang=hans'); await p.waitForTimeout(1500);
const url = await p.evaluate(() => {
  // the game's own night sky (drawSky), the whole of it fitted to a square 390 px wide (the phone's width), drawn at 1024
  const keep = ctx, kw = W, kh = H, kc = starCache, km = moonAt, c = document.createElement('canvas'); c.width = c.height = 1024; ctx = c.getContext('2d');
  ctx.scale(1024 / 390, 1024 / 390); W = H = 390; starCache = null; moonAt = null;
  drawSky(SKYN[0], SKYN[1], SKYN[2], 1.2, 1);
  ctx = keep; W = kw; H = kh; starCache = kc; moonAt = km; return c.toDataURL('image/png');
});
fs.writeFileSync('/dev/shm/sicon3/gsky_nomoon.png', Buffer.from(url.split(',')[1], 'base64')); console.log(errs.join(';') || 'ok'); await b.close();
