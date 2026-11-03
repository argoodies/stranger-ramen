/* The Xiaohongshu build's leaderboard (mini-tool submitScore / getRankList / getMyRank, client 9.51+, closed beta).
   Board 1, all-time: total wins, the same number the app sends to Game Center. The game posts { t: 'score', v } through
   window.__miniGC after each win and once at launch (__gcSync); a score goes up only when it has grown.
   A trophy pill sits beside the language button in the lobby and opens the top 100 and your own rank.
   Older clients, a missing API or no nickname authorisation (1005 / 1006): no button, and the game carries on as before.
   Plain ES5 so it passes the Chrome 61 gate as written; loaded by boot.js after the game scripts. */
(function () {
  var MIN = 9510, BOARD = 1, CACHE = 45000, sent = 0, pend = 0, ok = false, off = false, cache = null, cacheAt = 0, btn, panel, list, mine;
  function mt() { return window.xhs && window.xhs.miniTool; }
  function has() { var m = mt(); return !!(m && typeof m.submitScore === 'function' && typeof m.getRankList === 'function' && typeof m.getMyRank === 'function'); }
  function lang() { try { return LANG; } catch (e) { return 'hans'; } }
  var T = {
    hans: { title: '总胜场榜', me: '我的排名', wins: '胜', none: '还没有人上榜', fail: '暂时无法加载，稍后再试', wait: '加载中…', anon: '小红书用户', out: '未上榜', close: '关闭' },
    hant: { title: '總勝場榜', me: '我的排名', wins: '勝', none: '還沒有人上榜', fail: '暫時無法載入，稍後再試', wait: '載入中…', anon: '小紅書用戶', out: '未上榜', close: '關閉' },
    en: { title: 'Most Wins', me: 'My rank', wins: 'wins', none: 'Nobody on the board yet', fail: 'Could not load, try again later', wait: 'Loading…', anon: 'Player', out: 'Not ranked', close: 'Close' }
  };
  function t(k) { return (T[lang()] || T.hans)[k]; }
  function code(e) { return e && typeof e.errCode === 'number' ? e.errCode : 0; }
  function unauth(e) { if (window.__rankErr) window.__rankErr(e); var c = code(e); if (c === 1005 || c === 1006 || c === 10003) { off = true; show(false); return true; } return false; }

  // ---- submitting: only a bigger total, never in a loop
  function submit(v) {
    v = Math.floor(Number(v) || 0);
    if (!ok || off || v <= sent || v <= pend || v > 1000000) return;
    pend = v;
    Promise.resolve(mt().submitScore({ board: BOARD, score: v })).then(function (r) { sent = Math.max(sent, (r && r.score) || v); cache = null; }, function (e) { unauth(e); }).then(function () { pend = 0; });
  }
  var queued = [];
  window.__miniGC = function (m) { if (m && m.t === 'score') { if (ok) submit(m.v); else queued.push(m.v); } };

  // ---- reading: cached, with a short back-off while the board warms up (2002)
  function call(fn, args, tries) {
    return Promise.resolve(mt()[fn](args)).catch(function (e) {
      if (code(e) === 2002 && tries < 4) return new Promise(function (res) { setTimeout(res, 500 * Math.pow(2, tries)); }).then(function () { return call(fn, args, tries + 1); });
      throw e;
    });
  }
  function load() {
    if (cache && Date.now() - cacheAt < CACHE) return Promise.resolve(cache);
    return Promise.all([call('getRankList', { board: BOARD, period: 'all' }, 0), call('getMyRank', { board: BOARD, period: 'all' }, 0)]).then(function (r) { cache = r; cacheAt = Date.now(); return r; });
  }

  // ---- the button and the panel
  var css = document.createElement('style');
  css.textContent = '#xrank{position:fixed;left:14px;bottom:calc(16px + var(--safe-area-inset-bottom, env(safe-area-inset-bottom, 0px)));z-index:7;display:none;padding:8px 11px;line-height:0}' +
    '#xpanel{position:fixed;top:0;right:0;bottom:0;left:0;z-index:20;display:none;background:rgba(14,10,34,.55);-webkit-align-items:center;align-items:center;-webkit-justify-content:center;justify-content:center}' +
    '#xpanel .card{width:86%;max-width:360px;max-height:76%;display:-webkit-flex;display:flex;-webkit-flex-direction:column;flex-direction:column;background:rgba(36,28,70,.96);border:1px solid rgba(255,255,255,.18);border-radius:18px;color:#f4ecdc;font:300 15px var(--serif);overflow:hidden}' +
    '#xpanel .hd{display:-webkit-flex;display:flex;-webkit-justify-content:space-between;justify-content:space-between;-webkit-align-items:center;align-items:center;padding:14px 16px 10px;font-weight:400;font-size:17px;letter-spacing:.08em}' +
    '#xpanel .x{background:none;border:0;color:#f4ecdc;font-size:22px;line-height:1;padding:0 4px}' +
    '#xpanel .ls{overflow-y:auto;-webkit-overflow-scrolling:touch;padding:0 12px}' +
    '#xpanel .row{display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;padding:9px 6px;border-top:1px solid rgba(255,255,255,.08)}' +
    '#xpanel .rk{width:38px;color:#ffd48c;font-weight:400}#xpanel .nm{-webkit-flex:1;flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;padding-right:8px}#xpanel .sc{color:#ffd48c}' +
    '#xpanel .msg{padding:22px 6px;text-align:center;opacity:.75}' +
    '#xpanel .me{padding:12px 18px 14px;border-top:1px solid rgba(255,255,255,.18);background:rgba(255,212,140,.08)}';
  document.head.appendChild(css);
  btn = document.createElement('button'); btn.className = 'pill'; btn.id = 'xrank'; btn.setAttribute('aria-label', 'rank');
  btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M8.5 20h7M10 17h4"/></svg>';
  panel = document.createElement('div'); panel.id = 'xpanel';
  panel.innerHTML = '<div class="card"><div class="hd"><span class="tt"></span><button class="x">×</button></div><div class="ls"></div><div class="me"></div></div>';
  document.body.appendChild(btn); document.body.appendChild(panel);
  list = panel.querySelector('.ls'); mine = panel.querySelector('.me');
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function row(rk, nm, sc) { return '<div class="row"><span class="rk">' + rk + '</span><span class="nm">' + esc(nm) + '</span><span class="sc">' + sc + ' ' + t('wins') + '</span></div>'; }
  function render(r) {
    var data = (r[0] && r[0].data) || [], my = r[1] || {}, h = '';
    for (var i = 0; i < data.length; i++) h += row(data[i].rank, data[i].nickname == null ? t('anon') : data[i].nickname, data[i].score);
    list.innerHTML = h || '<div class="msg">' + t('none') + '</div>';
    var mr = my.status === 'EXACT' ? my.rank : my.status === 'OVER_LIMIT' ? '500+' : t('out');
    mine.innerHTML = t('me') + ' · <b style="font-weight:400;color:#ffd48c">' + mr + '</b>' + (my.status === 'EXACT' ? ' · ' + my.score + ' ' + t('wins') : '');
  }
  function open() {
    panel.querySelector('.tt').textContent = t('title'); panel.querySelector('.x').setAttribute('aria-label', t('close'));
    list.innerHTML = '<div class="msg">' + t('wait') + '</div>'; mine.innerHTML = ''; panel.style.display = 'flex';
    load().then(render, function (e) { if (!unauth(e)) list.innerHTML = '<div class="msg">' + t('fail') + '</div>'; else panel.style.display = 'none'; });
  }
  btn.addEventListener('click', open);
  panel.addEventListener('click', function (e) { if (e.target === panel || e.target.className === 'x') panel.style.display = 'none'; });
  function show(v) { btn.style.display = v ? 'block' : 'none'; }
  setInterval(function () { show(ok && !off && !!window.__3bLang && panel.style.display !== 'flex'); }, 300);      // only in the lobby, like the language button

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
        if (typeof window.__gcSync === 'function') window.__gcSync();      // the total so far goes up once at launch
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
