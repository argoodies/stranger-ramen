// The app icon: the game's own guardian charm (drawGuard in index.html, the cross-marked shield you win in a fight) on a sky of stars. Writes it at 1024 px into every place the apps keep an icon.
const { chromium } = require('/tmp/node_modules/playwright'), fs = require('fs'), { execFileSync } = require('child_process');
(async () => { const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1024, height: 1024 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file:///root/clocktower-ramen/index.html?lang=hans'); await p.waitForTimeout(800);
  const url = await p.evaluate(() => { const c = document.createElement('canvas'), N = c.width = c.height = 1024, o = c.getContext('2d'), keep = ctx;
    const g = o.createLinearGradient(0, 0, 0, N); g.addColorStop(0, '#22306a'); g.addColorStop(.55, '#2c2466'); g.addColorStop(1, '#171233'); o.fillStyle = g; o.fillRect(0, 0, N, N);
    for (let i = 0; i < 90; i++) { const a = Math.sin(i * 12.9898) * 43758.5453, b = Math.sin(i * 78.233) * 12543.123; o.beginPath(); o.arc((a - Math.floor(a)) * N, (b - Math.floor(b)) * N, 1.5 + (i % 4) * 1.6, 0, TAU); o.fillStyle = `rgba(255,250,230,${.35 + (i % 5) * .13})`; o.fill(); }
    o.globalAlpha = 1; { const gl = o.createRadialGradient(N / 2, N * .5, 0, N / 2, N * .5, N * .46); gl.addColorStop(0, 'rgba(255,236,190,.34)'); gl.addColorStop(1, 'rgba(255,236,190,0)'); o.fillStyle = gl; o.fillRect(0, 0, N, N); } ctx = o; const tk = TK; TK = 0; drawGuard(N / 2, N * .49, N * .32); TK = tk; ctx = keep; return c.toDataURL('image/png'); });
  fs.writeFileSync('/dev/shm/botc/star_icon.png', Buffer.from(url.split(',')[1], 'base64')); console.log(errs.join('\n') || 'icon rendered'); await b.close();
  execFileSync('python3', ['-c', `
from PIL import Image
import glob
src = Image.open('/dev/shm/botc/star_icon.png').convert('RGB'); R = '/root/clocktower-ramen/'
for f in ['deploy/icon.png', 'ios/App/Assets.xcassets/AppIcon.appiconset/icon_1024.png', 'harmony/AppScope/resources/base/media/app_icon.png', 'harmony/entry/src/main/resources/base/media/app_icon.png'] + [x[len(R):] for x in glob.glob(R + 'android/app/src/main/res/mipmap-*/ic_launcher.png')]:
    old = Image.open(R + f); src.resize(old.size, Image.LANCZOS).save(R + f); print(f, old.size)
`], { stdio: 'inherit' }); })();
