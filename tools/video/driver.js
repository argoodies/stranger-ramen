<script>
(() => {
  let evs = [], segT = 0;
  const K = () => chv.s * .8;
    const SEG = {
    stall: () => { $('title').style.display = 'none'; enterStall(); const want = { chili: true, cilantro: true, beef: true };      // one fortune teller at the counter wanting everything; the noodles take their real time
      stall.seats = [null, { look: { kind: 'ft', hat: [70, 100, 220], name: '占卜师' }, want, text: orderText(want), state: 'wait', t: 9, wait: 0, say: '', dish: null }, null]; stall.spawn = 99;
      Object.assign(stall.owner, { x: 2.4, y: 1.2, tx: 2.4, ty: 1.2, ptx: null, path: null });
      const tap = k => () => { const h = HIT[k]; if (h) stallTap(h[0], h[1]); else console.log('no hit', k); };      // every step is a tap on the thing itself, as a player would do it
      return [[.6, tap('pot')], [3.6, tap('pot')], [4.3, tap('bowl')], [5.0, tap('soup')], [5.6, tap('bowl')], [6.3, tap('chili')], [6.9, tap('bowl')], [7.6, tap('cilantro')], [8.2, tap('bowl')], [8.9, tap('beef')], [9.5, tap('bowl')], [10.3, tap('bowl')]]; },      // boil, wait, scoop, into the bowl, soup, chili, cilantro, beef, and lift the bowl up
    town: () => { leaveStall(); fade = 0; zoomTarget = zoomOut = 0; const pth = bfs(cellOf(player), BDOOR); player.path = pth ? pth.slice(1) : []; player.enter = false; return []; },      // out of the ramen shop, off towards the coffee house
    bar: () => { enterBar(); Object.assign(bar, { x: 2.3, y: 1.5, path: [] }); bar.cups = [{ y: 1.5, night: G.n > .5, col: [240, 196, 70], full: true, slide: 1, from: 1.5 }]; Object.assign(bar.cat, { x: .7, y: 3.2, tx: .7, ty: 3.2, sit: 999 });
      return [[.4, () => { const h = BARHIT.cup0; if (h) cafeTap(h[0], h[1]); }], [1.3, () => barGo([1, 3], null)], [2.3, () => { const h = BARHIT.cat; if (h) cafeTap(h[0], h[1]); }]]; },      // drinks his cup, then goes over to stroke the cat
    fight: () => { enterChurch(); church.tier = 2; const c = church, p = c.p; p.x = p.tx = TORCH[0] + 2.4; p.y = p.ty = TORCH[1] + 1.2; c.cam = null;      // the chef walks to the torch, lights it, and stands still while the two whirlwinds of the second round fade in
      const calm = () => c.foes.forEach(f => { f.cd = 99; f.wt = 99; }); return [[.5, () => { const q = chv.P(TORCH[0], TORCH[1]); churchTap(q[0], q[1] - K() * .8); }], ...Array.from({ length: 90 }, (_, k) => [.55 + k * .05, calm])]; },
    farewell: () => { enterChurch(); church.story = { i: 13, t: 1.0, dev: true, lit: 0 }; return []; },      // the great whirlwind's farewell
    rain: () => { enterChurch(); church.story = { i: 14, t: 3.6, dev: true, lit: 0 }; return []; },
    title: () => { church.story = null; tw.view = null; tw.msay = null; hideChef = false; window.__noGeese = true; tapHint = () => {}; mode = 'title'; zoomOut = zoomTarget = 1; titleT0 = null;      /* the title fades in from nothing exactly as when the game opens */ $('title').style.display = ''; return []; },
  };
  window.__seg = name => { evs = SEG[name](); segT = 0; fade = 0; };
  window.__step = (dt, black) => { window.__VT += dt * 1000; segT += dt; while (evs.length && evs[0][0] <= segT) evs.shift()[1](); frame(window.__VT);
    if (black > 0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = `rgba(6,4,16,${black})`; ctx.fillRect(0, 0, cv.width, cv.height); ctx.restore(); }
    return $('c').toDataURL('image/jpeg', .9); };
  window.__ready = true;
})();
</script>
