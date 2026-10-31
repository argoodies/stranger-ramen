// The app icon: the game's own guardian charm (drawGuard in index.html, the cross-marked shield you win in a fight) on a sky of stars. Writes it at 1024 px into every place the apps keep an icon.
const { chromium } = require('/tmp/node_modules/playwright'), fs = require('fs'), { execFileSync } = require('child_process');
(async () => { const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1024, height: 1024 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file:///root/clocktower-ramen/index.html?lang=hans'); await p.waitForTimeout(800);
  const url = await p.evaluate(() => { const c = document.createElement('canvas'), N = c.width = c.height = 1024, o = c.getContext('2d'), keep = ctx;
    const g = o.createLinearGradient(0, 0, 0, N); g.addColorStop(0, '#191640'); g.addColorStop(1, '#2c1a40'); o.fillStyle = g; o.fillRect(0, 0, N, N);      // the sky of the old noodle-shop icon: dark, with a few small stars
    for (const [x, y, r, a] of [[30, 35, 3, .7], [271, 37, 2.5, .7], [530, 105, 5, .95], [660, 149, 3, .6], [912, 57, 5, .75], [62, 250, 2.5, .55], [301, 261, 2.5, .5], [929, 302, 5, .65], [117, 361, 4, .6], [128, 643, 4.5, .55], [895, 650, 5.5, .7], [800, 930, 3, .5], [210, 905, 3, .5]]) { o.beginPath(); o.arc(x, y, r, 0, TAU); o.fillStyle = `rgba(255,250,235,${a})`; o.fill(); }
    ctx = o; const tk = TK; TK = 0; drawGuard(N / 2, N * .49, N * .32); TK = tk; ctx = keep; return c.toDataURL('image/png'); });
  fs.writeFileSync('/dev/shm/botc/star_icon.png', Buffer.from(url.split(',')[1], 'base64')); console.log(errs.join('\n') || 'icon rendered'); await b.close();
  execFileSync('python3', ['-c', `
from PIL import Image
import glob
src = Image.open('/dev/shm/botc/star_icon.png').convert('RGB'); R = '/root/clocktower-ramen/'
for f in ['deploy/icon.png', 'ios/App/Assets.xcassets/AppIcon.appiconset/icon_1024.png', 'harmony/AppScope/resources/base/media/app_icon.png', 'harmony/entry/src/main/resources/base/media/app_icon.png'] + [x[len(R):] for x in glob.glob(R + 'android/app/src/main/res/mipmap-*/ic_launcher.png')]:
    old = Image.open(R + f); src.resize(old.size, Image.LANCZOS).save(R + f); print(f, old.size)
`], { stdio: 'inherit' }); })();
