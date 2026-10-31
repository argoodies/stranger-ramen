// The app icon: the gold cross from inside the church on a dark, sparsely starred sky. Writes it at 1024 px into every place the apps keep an icon.
const { chromium } = require('/tmp/node_modules/playwright'), fs = require('fs'), { execFileSync } = require('child_process');
(async () => { const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1024, height: 1024 } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file:///root/clocktower-ramen/index.html?lang=hans'); await p.waitForTimeout(800);
  const url = await p.evaluate(() => { const c = document.createElement('canvas'), N = c.width = c.height = 1024, o = c.getContext('2d'), keep = ctx;
    const g = o.createLinearGradient(0, 0, 0, N); g.addColorStop(0, '#191640'); g.addColorStop(1, '#2c1a40'); o.fillStyle = g; o.fillRect(0, 0, N, N);      // the old noodle-shop icon's dark sky
    // stars with room to breathe, in loose knots, drawn in from the edges
    const knots = [[150, 150, 3.2, 7], [120, 215, 2.4, 3], [226, 96, 2.2, 3], [258, 214, 1.8, 2], [870, 118, 5, 9], [930, 196, 2.4, 3], [812, 66, 2, 3], [934, 54, 1.8, 2], [905, 640, 3, 5], [846, 700, 2.2, 2], [952, 716, 2, 2], [110, 760, 4.4, 8], [176, 834, 2.4, 3], [66, 846, 2, 2], [214, 722, 1.8, 2], [760, 905, 2.6, 4], [828, 948, 1.8, 2], [430, 70, 2, 2], [560, 952, 2.2, 3], [62, 470, 2.4, 3], [190, 290, 2, 3], [92, 330, 1.8, 2], [300, 120, 1.8, 2], [338, 48, 2.2, 3], [700, 110, 2, 3], [752, 196, 2.8, 5], [690, 40, 1.8, 2], [850, 300, 1.8, 2], [960, 372, 2.4, 3], [790, 430, 2, 3], [880, 500, 3, 5], [760, 620, 1.8, 2], [960, 570, 1.8, 2], [690, 810, 2, 3], [880, 840, 2.4, 3], [640, 930, 1.8, 2], [300, 900, 2.4, 3], [380, 820, 1.8, 2], [250, 640, 2, 3], [150, 590, 2.6, 4], [44, 640, 1.8, 2], [300, 500, 1.8, 2]];
    for (const [x0, y0, r, q] of knots) { const x = 512 + (x0 - 512) * .84, y = 512 + (y0 - 512) * .85; if (r >= 4) { const h = o.createRadialGradient(x, y, 0, x, y, r * 4); h.addColorStop(0, 'rgba(255,250,235,.22)'); h.addColorStop(1, 'rgba(255,250,235,0)'); o.fillStyle = h; o.beginPath(); o.arc(x, y, r * 4, 0, TAU); o.fill(); } o.beginPath(); o.arc(x, y, r, 0, TAU); o.fillStyle = `rgba(255,250,235,${.5 + q * .05})`; o.fill(); }
    ctx = o; const tk = TK, GOLD_ = [236, 200, 130]; TK = 0;
  // the church's cross, the same two beams, turned so it nearly faces us: about 22 degrees off, from a little above
  const A = 22 * Math.PI / 180, ca = Math.cos(A), sa = Math.sin(A), E = .42, S = 205;
  class TV extends View { P(x, y, z = 0) { return [this.cx + (y * ca - x * sa) * this.s, this.cy + (y * sa + x * ca) * E * this.s - z * this.s]; } sh(c) { const [t, l, r] = super.sh(c); return [t, r, l]; } }
  const v = new TV(N / 2 + .95 * sa * S, N / 2 + 2.22 * S - .95 * ca * E * S, S);
  v.box(.84, -.11, .62, .22, .22, 3.2, GOLD_); v.box(.84, -.8, 2.7, .22, 1.6, .22, GOLD_);
    TK = tk; ctx = keep; return c.toDataURL('image/png'); });
  fs.writeFileSync('/dev/shm/botc/star_icon.png', Buffer.from(url.split(',')[1], 'base64')); console.log(errs.join('\n') || 'icon rendered'); await b.close();
  execFileSync('python3', ['-c', `
from PIL import Image
import glob
src = Image.open('/dev/shm/botc/star_icon.png').convert('RGB'); R = '/root/clocktower-ramen/'
for f in ['deploy/icon.png', 'ios/App/Assets.xcassets/AppIcon.appiconset/icon_1024.png', 'harmony/AppScope/resources/base/media/app_icon.png', 'harmony/entry/src/main/resources/base/media/app_icon.png'] + [x[len(R):] for x in glob.glob(R + 'android/app/src/main/res/mipmap-*/ic_launcher.png')]:
    old = Image.open(R + f); src.resize(old.size, Image.LANCZOS).save(R + f); print(f, old.size)
`], { stdio: 'inherit' }); })();
