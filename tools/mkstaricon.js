// The app icon: the gold cross from inside the church on a dark, sparsely starred sky. Writes it at 1024 px into every place the apps keep an icon.
const { chromium } = require('/tmp/node_modules/playwright'), fs = require('fs'), { execFileSync } = require('child_process');
(async () => { const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1024, height: 1024 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file:///root/clocktower-ramen/index.html?lang=hans'); await p.waitForTimeout(800);
  const url = await p.evaluate(() => { const c = document.createElement('canvas'), N = c.width = c.height = 1024, o = c.getContext('2d'), keep = ctx;
    const g = o.createLinearGradient(0, 0, 0, N); g.addColorStop(0, '#191640'); g.addColorStop(1, '#2c1a40'); o.fillStyle = g; o.fillRect(0, 0, N, N);      // the old noodle-shop icon's dark sky
    // a dozen stars, fairly large, with room to breathe and clear edges
    const knots = [[170, 170, 7, 9], [262, 112, 4, 5], [128, 268, 4, 4], [852, 138, 9, 9], [908, 240, 4.4, 5], [772, 92, 3.6, 4], [880, 640, 6, 7], [812, 742, 4, 5], [146, 744, 8, 8], [226, 846, 4.4, 5], [96, 500, 4.6, 5], [742, 884, 5, 6]];
    for (const [x, y, r, q] of knots) { if (r >= 7) { const h = o.createRadialGradient(x, y, 0, x, y, r * 4); h.addColorStop(0, 'rgba(255,250,235,.22)'); h.addColorStop(1, 'rgba(255,250,235,0)'); o.fillStyle = h; o.beginPath(); o.arc(x, y, r * 4, 0, TAU); o.fill(); } o.beginPath(); o.arc(x, y, r, 0, TAU); o.fillStyle = `rgba(255,250,235,${.5 + q * .05})`; o.fill(); }
    // the cross exactly as it stands in the church: the same two beams, the same gold, the church's mirrored view
    ctx = o; const tk = TK, GOLD_ = [236, 200, 130], S = 205, v = new MView(N / 2 + .95 * S * C30, N * .5 + 1.9 * S - .95 * S * .5 + 66, S), my = 0; TK = 0; v.box(.84, my - .11, .62, .22, .22, 3.2, GOLD_); v.box(.84, my - .8, 2.7, .22, 1.6, .22, GOLD_); TK = tk; ctx = keep; return c.toDataURL('image/png'); });
  fs.writeFileSync('/dev/shm/botc/star_icon.png', Buffer.from(url.split(',')[1], 'base64')); console.log(errs.join('\n') || 'icon rendered'); await b.close();
  execFileSync('python3', ['-c', `
from PIL import Image
import glob
src = Image.open('/dev/shm/botc/star_icon.png').convert('RGB'); R = '/root/clocktower-ramen/'
for f in ['deploy/icon.png', 'ios/App/Assets.xcassets/AppIcon.appiconset/icon_1024.png', 'harmony/AppScope/resources/base/media/app_icon.png', 'harmony/entry/src/main/resources/base/media/app_icon.png'] + [x[len(R):] for x in glob.glob(R + 'android/app/src/main/res/mipmap-*/ic_launcher.png')]:
    old = Image.open(R + f); src.resize(old.size, Image.LANCZOS).save(R + f); print(f, old.size)
`], { stdio: 'inherit' }); })();
