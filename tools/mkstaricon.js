// The app icon: the game's Guardian Cross (drawGuard in index.html) on a dark, sparsely starred sky. Writes it at 1024 px into every place the apps keep an icon.
const { chromium } = require('/tmp/node_modules/playwright'), fs = require('fs'), { execFileSync } = require('child_process');
(async () => { const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1024, height: 1024 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file:///root/clocktower-ramen/index.html?lang=hans'); await p.waitForTimeout(800);
  const url = await p.evaluate(() => { const c = document.createElement('canvas'), N = c.width = c.height = 1024, o = c.getContext('2d'), keep = ctx;
    const g = o.createLinearGradient(0, 0, 0, N); g.addColorStop(0, css(SKYN[0])); g.addColorStop(.5, css(SKYN[1])); g.addColorStop(1, css(SKYN[2])); o.fillStyle = g; o.fillRect(0, 0, N, N);      // the game's night sky
    // the Milky Way across the top of the sky, as in the game: a slanting band of soft light and a dust of fine stars gathered along it
    { o.save(); o.translate(525, 445); o.rotate(-.5);      // the band passes behind the ring's centre, so sky and cross hang together
      const bw = N * .22, h = o.createLinearGradient(0, -bw, 0, bw); h.addColorStop(0, 'rgba(150,150,220,0)'); h.addColorStop(.5, 'rgba(160,160,230,.2)'); h.addColorStop(1, 'rgba(150,150,220,0)'); o.fillStyle = h; o.fillRect(-N, -bw, N * 2, bw * 2);
      for (let i = 0; i < 240; i++) { const a = Math.sin(i * 12.9898) * 43758.5453, b = Math.sin(i * 78.233) * 12543.123, c = Math.sin(i * 39.346) * 24634.633, d = Math.sin(i * 7.13) * 9182.31, f = q => q - Math.floor(q), v = (f(b) + f(c) + f(d) - 1.5) / 1.5 * N * .15; o.beginPath(); o.arc((f(a) * 2 - 1) * N * .8, v, 1.2 + (i % 3) * .8, 0, TAU); o.fillStyle = `rgba(255,250,230,${.3 + (i % 4) * .14})`; o.fill(); } o.restore(); }
    // the game's own Guardian Cross, the gold ring pendant, in the middle of the sky
    ctx = o; const tk = TK; TK = 0; drawGuard(N / 2 + 2, N / 2 + 20, N * .28); TK = tk; ctx = keep; return c.toDataURL('image/png'); });
  fs.writeFileSync('/dev/shm/botc/star_icon.png', Buffer.from(url.split(',')[1], 'base64')); console.log(errs.join('\n') || 'icon rendered'); await b.close(); if (process.argv[2] === 'preview') return;
  execFileSync('python3', ['-c', `
from PIL import Image
import glob
src = Image.open('/dev/shm/botc/star_icon.png').convert('RGB'); R = '/root/clocktower-ramen/'
for f in ['deploy/icon.png', 'ios/App/Assets.xcassets/AppIcon.appiconset/icon_1024.png', 'harmony/AppScope/resources/base/media/app_icon.png', 'harmony/entry/src/main/resources/base/media/app_icon.png'] + [x[len(R):] for x in glob.glob(R + 'android/app/src/main/res/mipmap-*/ic_launcher.png')]:
    old = Image.open(R + f); src.resize(old.size, Image.LANCZOS).save(R + f); print(f, old.size)
`], { stdio: 'inherit' }); })();
