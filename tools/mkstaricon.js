// The app icon: the game's Guardian Cross (drawGuard in index.html) on a dark, sparsely starred sky. Writes it at 1024 px into every place the apps keep an icon.
const { chromium } = require('/tmp/node_modules/playwright'), fs = require('fs'), { execFileSync } = require('child_process');
(async () => { const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1024, height: 1024 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file:///root/clocktower-ramen/index.html?lang=hans'); await p.waitForTimeout(800);
  const url = await p.evaluate(() => { const c = document.createElement('canvas'), N = c.width = c.height = 1024, o = c.getContext('2d'), keep = ctx;
    const g = o.createLinearGradient(0, 0, 0, N); g.addColorStop(0, css(SKYN[0])); g.addColorStop(.5, css(SKYN[1])); g.addColorStop(1, css(SKYN[2])); o.fillStyle = g; o.fillRect(0, 0, N, N);      // the game's night sky
    for (let i = 0; i < 60; i++) { const a = Math.sin(i * 12.9898) * 43758.5453, b = Math.sin(i * 78.233) * 12543.123, x = (a - Math.floor(a)) * N, v = b - Math.floor(b), y = v * v * N, f = 1 - y / N; o.beginPath(); o.arc(x, y, 1.2 + (i % 3) * .7, 0, TAU); o.fillStyle = `rgba(255,250,230,${(.16 + (i % 4) * .09) * f})`; o.fill(); }      // the dust of faint stars, thickest overhead
    // the game's own Guardian Cross, the gold ring pendant, in the middle of the sky
    ctx = o; const tk = TK; TK = 0; drawGuard(N / 2 + -63, N / 2 + -22, N * .3); TK = tk; ctx = keep; return c.toDataURL('image/png'); });
  fs.writeFileSync('/dev/shm/botc/star_icon.png', Buffer.from(url.split(',')[1], 'base64')); console.log(errs.join('\n') || 'icon rendered'); await b.close(); if (process.argv[2] === 'preview') return;
  execFileSync('python3', ['-c', `
from PIL import Image
import glob
src = Image.open('/dev/shm/botc/star_icon.png').convert('RGB'); R = '/root/clocktower-ramen/'
for f in ['deploy/icon.png', 'ios/App/Assets.xcassets/AppIcon.appiconset/icon_1024.png', 'harmony/AppScope/resources/base/media/app_icon.png', 'harmony/entry/src/main/resources/base/media/app_icon.png'] + [x[len(R):] for x in glob.glob(R + 'android/app/src/main/res/mipmap-*/ic_launcher.png')]:
    old = Image.open(R + f); src.resize(old.size, Image.LANCZOS).save(R + f); print(f, old.size)
`], { stdio: 'inherit' }); })();
