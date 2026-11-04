/* The Xiaohongshu build's leaderboard (mini-tool submitScore / getMyRank, client 9.51+, closed beta).
   Board 1, all-time: total wins, the same number the app sends to Game Center. The game posts { t: 'score', v } through
   window.__miniGC after each win and once at launch (__gcSync); a score goes up only when it has grown.
   After a won game the lobby shows Game Center's bubbles in a glass ball where the book was (tools/mk3b.py); tapped, it turns and
   says your wins and, when the leaderboard can tell (client 9.51+, authorised), your rank among all players. It also styles the language menu in Xiaohongshu's manner.
   Plain ES5 so it passes the Chrome 61 gate as written; loaded by boot.js after the game scripts. */
(function () {
  var MIN = 9510, BOARD = 1, CACHE = 45000, sent = 0, pend = 0, ok = false, off = false, cache = null, cacheAt = 0;
  function mt() { return window.xhs && window.xhs.miniTool; }
  function has() { var m = mt(); return !!(m && typeof m.submitScore === 'function' && typeof m.getRankList === 'function' && typeof m.getMyRank === 'function'); }
  function lang() { try { return LANG; } catch (e) { return 'hans'; } }
  function code(e) { return e && typeof e.errCode === 'number' ? e.errCode : 0; }
  function unauth(e) { if (window.__rankErr) window.__rankErr(e); var c = code(e); return c === 1005 || c === 1006 || c === 10003; }      // an authorisation refusal; what to do about it is decided where it happens

  // ---- submitting: only a bigger total, never in a loop
  function submit(v) {
    v = Math.floor(Number(v) || 0);
    if (!ok || off || v <= sent || v <= pend || v > 1000000) return;
    pend = v;
    Promise.resolve(mt().submitScore({ board: BOARD, score: v })).then(function (r) { sent = Math.max(sent, (r && r.score) || v); cache = null; }, function (e) { if (unauth(e)) off = true; }).then(function () { pend = 0; });      // refused or failed: the board can still be looked at
  }
  // scores posted before the leaderboard is found wait in a queue; the launch sync (syncing) sends the total from earlier sessions
  var queued = [], syncing = false;
  window.__miniGC = function (m) { if (!m || m.t !== 'score') return; if (ok) submit(m.v); else queued.push(m.v); };

  // ---- reading: cached, with a short back-off while the board warms up (2002)
  function call(fn, args, tries) {
    return Promise.resolve(mt()[fn](args)).catch(function (e) {
      if (code(e) === 2002 && tries < 4) return new Promise(function (res) { setTimeout(res, 500 * Math.pow(2, tries)); }).then(function () { return call(fn, args, tries + 1); });
      throw e;
    });
  }
  function load() {      // your own rank only (the ball says nothing about anyone else)
    if (cache && Date.now() - cacheAt < CACHE) return Promise.resolve(cache);
    return call('getMyRank', { board: BOARD, period: 'all' }, 0).then(function (v) { cache = v; cacheAt = Date.now(); return v; });
  }

  // ---- the language menu in Xiaohongshu's manner: a white card, the chosen language in red with a tick (the button is the shared 文A mark, tools/mk3b.py)
  var XF = '-apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", "Noto Sans CJK SC", sans-serif';
  var css = document.createElement('style');
  css.textContent =
    '#langMenu{padding:6px!important;min-width:150px;border:0!important;border-radius:14px!important;background:#fff!important;box-shadow:0 10px 36px rgba(0,0,0,.2)}' +
    '#langMenu button{position:relative;border-radius:10px!important;padding:10px 40px 10px 14px!important;font:400 15px ' + XF + '!important;letter-spacing:0!important;color:#333!important;background:transparent!important}' +
    '#langMenu button+button{margin-top:2px}#langMenu button.on{background:#FFF0F2!important;color:#FF2442!important;font-weight:600!important}' +
    '#langMenu button.on::after{content:"";position:absolute;right:16px;top:50%;width:5px;height:10px;margin-top:-7px;border:solid #FF2442;border-width:0 2px 2px 0;-webkit-transform:rotate(45deg);transform:rotate(45deg)}';      // a red tick on the right of the chosen one
  document.head.appendChild(css);

  // ---- what the ball says: tapped (tools/mk3b.py), it turns once and then tells you, in a speech bubble like everyone else's,
  // how many games you have won (counted on this device) and, when the leaderboard can say, where that puts you among all players.
  // No rank to be had (an old client, not authorised, not ranked yet, no network): just the wins.
  var SAY = {
    hans: { rank: '你赢了 {w} 局，全网排名第 {r}。', over: '你赢了 {w} 局，全网排名 500 名开外。', wins: '你赢了 {w} 局。', updating: '你赢了 {w} 局，排名更新中。' },
    hant: { rank: '你贏了 {w} 局，全網排名第 {r}。', over: '你贏了 {w} 局，全網排名 500 名開外。', wins: '你贏了 {w} 局。', updating: '你贏了 {w} 局，排名更新中。' },
    en: { rank: '{w} wins so far, No. {r} worldwide.', over: '{w} wins so far, outside the top 500.', wins: '{w} wins so far.', updating: '{w} wins so far, rank updating.' }
  };
  function wins() { var n = 0; try { n = GCS.wins || 0; } catch (e) {} return n; }      // the wins counted on this device; the rank is the leaderboard's, as it has it
  function say(k, w, r) { if (window.__markSay) window.__markSay(function () { var S = SAY[lang()] || SAY.hans; return S[k].replace('{w}', w).replace('{r}', r).replace(/^1 wins/, '1 win'); }); }      // worked out each frame: a change of language shows at once
  function fill(my) {
    my = my || {};
    var far = typeof my.score === 'number' ? my.score : null;      // the leaderboard's count (none past 500th)
    if (far !== null && far > wins() && window.__gcAdopt) window.__gcAdopt(far);      // the leaderboard is ahead: this device catches up
    var behind = far !== null && far < wins();      // the leaderboard is behind this device: its rank is still the old one
    if (my.status === 'EXACT') say(behind ? 'updating' : 'rank', wins(), my.rank); else if (my.status === 'OVER_LIMIT') say('over', wins()); else say('wins', wins());
  }
  var busy = false;
  function openMe() {
    if (busy) return; busy = true;      // the bubble comes when the ball has stopped turning (a second), or when the rank does if later
    var t0 = Date.now(), after = function (f) { return function (v) { setTimeout(function () { busy = false; f(v); }, Math.max(0, 1000 - (Date.now() - t0))); }; };
    if (!ok || off) return after(fill)(null);      // no leaderboard here: the wins alone
    load().then(after(fill), after(function (e) { if (unauth(e)) off = true; fill(null); }));
  }
  window.__boardMark = { open: openMe };      // the Xiaohongshu build always has the ball after a win

  // ---- switched on only for a client that has it. The container may inject window.xhs a little after the page starts,
  // and the launch options may come late, so look again every half second for a while instead of deciding once.
  var why = 'starting', tries = 0, lastErr = '';
  function build() {
    var x = window.xhs, lo = x && x.launchOptions, v = Number(lo && lo.miniToolEnv && lo.miniToolEnv.buildVersion) || 0;
    if (v) return Promise.resolve(v);
    var m = mt(); if (!m || typeof m.getLaunchOptions !== 'function') return Promise.resolve(Promise.resolve(window.__xhsBuild || 0));
    return Promise.resolve(m.getLaunchOptions()).then(function (o) { return Number(o && o.miniToolEnv && o.miniToolEnv.buildVersion) || 0; }, function () { return 0; });
  }
  function detect() {
    if (ok || off) return;
    tries++;
    build().then(function (b) {
      if (ok || off) return;
      if (!window.xhs) why = 'no window.xhs';
      else if (!b) why = 'no build version';
      else if (Math.floor(b / 1000) < MIN) { why = 'client ' + b + ' < 9.51'; return; }      // an old client will not change: stop looking
      else if (!has()) why = 'no leaderboard API (build ' + b + ')';
      else { why = 'on (build ' + b + ')'; ok = true;
        for (var i = 0; i < queued.length; i++) submit(queued[i]);
        syncing = true; try { if (typeof window.__gcSync === 'function') window.__gcSync(); } finally { syncing = false; }      // the total so far goes up once at launch
        return; }
      if (tries < 40) setTimeout(detect, 500);      // up to twenty seconds
    });
  }
  detect();

  // ---- diagnostic build only (mkxhs --debug): a small line at the foot says why the trophy is or is not shown
  if (window.__xhsRankDebug) {
    var d = document.createElement('div');
    d.style.cssText = 'position:fixed;left:8px;right:8px;bottom:calc(64px + var(--safe-area-inset-bottom, env(safe-area-inset-bottom, 0px)));z-index:30;font:11px monospace;color:#fff;background:rgba(0,0,0,.55);padding:4px 6px;border-radius:6px;pointer-events:none;word-break:break-all';
    document.body.appendChild(d);
    setInterval(function () { d.textContent = 'rank: ' + (off ? 'off (unauthorised) ' : '') + why + ' · lobby ' + !!window.__3bLang + ' · sent ' + sent + (lastErr ? ' · err ' + lastErr : '') + ' · tries ' + tries; }, 500);
  }
  window.__rankErr = function (e) { lastErr = (e && (e.errCode || '') + ' ' + (e.errMsg || '')) || String(e); };
})();
