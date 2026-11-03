/* The Xiaohongshu build's leaderboard (mini-tool submitScore / getRankList / getMyRank, client 9.51+, closed beta).
   Board 1, all-time: total wins, the same number the app sends to Game Center. The game posts { t: 'score', v } through
   window.__miniGC after each win and once at launch (__gcSync); a score goes up only when it has grown.
   A trophy pill sits beside the language button in the lobby and opens the top 100 and your own rank.
   Older clients, a missing API or no nickname authorisation (1005 / 1006): no button, and the game carries on as before.
   Plain ES5 so it passes the Chrome 61 gate as written; loaded by boot.js after the game scripts. */
(function () {
  var MIN = 9510, BOARD = 1, CACHE = 45000, sent = 0, pend = 0, ok = false, off = false, cache = null, cacheAt = 0, btn, panel, list;
  function mt() { return window.xhs && window.xhs.miniTool; }
  function has() { var m = mt(); return !!(m && typeof m.submitScore === 'function' && typeof m.getRankList === 'function' && typeof m.getMyRank === 'function'); }
  function lang() { try { return LANG; } catch (e) { return 'hans'; } }
  var T = {
    hans: { title: '总胜场榜', me: '我的排名', wins: '胜', none: '还没有人上榜', fail: '暂时无法加载，稍后再试', wait: '加载中…', anon: '小红书用户', out: '未上榜', close: '关闭', meAuth: '授权后显示你的排名', closed: '排行榜暂未开放', you: '我' },
    hant: { title: '總勝場榜', me: '我的排名', wins: '勝', none: '還沒有人上榜', fail: '暫時無法載入，稍後再試', wait: '載入中…', anon: '小紅書用戶', out: '未上榜', close: '關閉', meAuth: '授權後顯示你的排名', closed: '排行榜暫未開放', you: '我' },
    en: { title: 'Most Wins', me: 'My rank', wins: 'wins', none: 'Nobody on the board yet', fail: 'Could not load, try again later', wait: 'Loading…', anon: 'Player', out: 'Not ranked', close: 'Close', meAuth: 'Your rank shows once authorised', closed: 'The leaderboard is not open yet', you: 'Me' }
  };
  function t(k) { return (T[lang()] || T.hans)[k]; }
  function code(e) { return e && typeof e.errCode === 'number' ? e.errCode : 0; }
  function unauth(e) { if (window.__rankErr) window.__rankErr(e); var c = code(e); return c === 1005 || c === 1006 || c === 10003; }      // an authorisation refusal; what to do about it is decided where it happens

  // ---- submitting: only a bigger total, never in a loop
  function submit(v) {
    v = Math.floor(Number(v) || 0);
    if (!ok || off || v <= sent || v <= pend || v > 1000000) return;
    pend = v;
    Promise.resolve(mt().submitScore({ board: BOARD, score: v })).then(function (r) { sent = Math.max(sent, (r && r.score) || v); cache = null; }, function (e) { unauth(e); }).then(function () { pend = 0; });      // refused or failed: the board can still be looked at
  }
  // the capsule shows only after a win in this session: every score the game posts is a win, except the ones the launch sync
  // sends (syncing), which carry the total from earlier sessions
  var queued = [], syncing = false, wonNow = false;
  window.__miniGC = function (m) { if (!m || m.t !== 'score') return; if (!syncing) wonNow = true; if (ok) submit(m.v); else queued.push(m.v); };

  // ---- reading: cached, with a short back-off while the board warms up (2002)
  function call(fn, args, tries) {
    return Promise.resolve(mt()[fn](args)).catch(function (e) {
      if (code(e) === 2002 && tries < 4) return new Promise(function (res) { setTimeout(res, 500 * Math.pow(2, tries)); }).then(function () { return call(fn, args, tries + 1); });
      throw e;
    });
  }
  function load() {
    if (cache && Date.now() - cacheAt < CACHE) return Promise.resolve(cache);
    // the list and your own rank are asked for separately: a rank that is not authorised must not take the list down with it
    var settle = function (p) { return p.then(function (v) { return { v: v }; }, function (e) { return { e: e }; }); };
    return Promise.all([settle(call('getRankList', { board: BOARD, period: 'all' }, 0)), settle(call('getMyRank', { board: BOARD, period: 'all' }, 0))]).then(function (r) {
      if (!r[0].e && !r[1].e) { cache = r; cacheAt = Date.now(); }
      return r;
    });
  }

  // ---- the button and the panel
  var css = document.createElement('style');
  // Xiaohongshu's own look: a white card, its red (#FF2442) for the button, the first three and your own highlighted row
  var XF = '-apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", "Noto Sans CJK SC", sans-serif';
  css.textContent = '#xcap{position:fixed;left:50%;top:calc(8px + var(--safe-area-inset-top, env(safe-area-inset-top, 0px)));-webkit-transform:translateX(-50%);transform:translateX(-50%);z-index:20;display:none;height:32px;padding:0 12px 0 4px;border:.5px solid rgba(0,0,0,.08);border-radius:16px;background:rgba(255,255,255,.92);box-shadow:0 2px 10px rgba(0,0,0,.12);color:#333;font:600 13px ' + XF + ';letter-spacing:.02em;white-space:nowrap;-webkit-align-items:center;align-items:center}' +
    '#xcap.on{display:-webkit-flex;display:flex}' +
    '#xcap .ic{width:24px;height:24px;margin-right:6px;border-radius:50%;background:#FF2442;display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;-webkit-justify-content:center;justify-content:center}' +
    '#xcap .ar{margin-left:4px;color:#FF2442;font-weight:400;font-size:16px;line-height:1}' +
    '#xpanel{position:fixed;left:50%;top:50%;-webkit-transform:translate(-50%,-50%);transform:translate(-50%,-50%);z-index:20;display:none;-webkit-flex-direction:column;flex-direction:column;width:300px;max-width:calc(100% - 40px);max-height:66%;padding:6px 0 10px;border-radius:16px;background:#fff;color:#333;font:400 15px ' + XF + ';box-shadow:0 10px 36px rgba(0,0,0,.22)}' +
    '#xpanel.open{display:-webkit-flex;display:flex}' +
    '#xpanel .tt{padding:12px 18px 10px;font-size:17px;font-weight:600;color:#333;border-bottom:1px solid #f2f2f2}' +
    '#xpanel .ls{overflow-y:auto;-webkit-overflow-scrolling:touch;padding:4px 8px 0}' +
    '#xpanel .row{display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;border-radius:10px;padding:10px 10px}' +
    '#xpanel .rk{width:46px;color:#999;font-weight:600;font-style:italic}#xpanel .rk.t{color:#FF2442}' +
    '#xpanel .nm{-webkit-flex:1;flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;padding-right:8px}#xpanel .sc{white-space:nowrap;color:#999;font-size:14px}' +
    '#xpanel .row.me{background:#FFF0F2}#xpanel .row.me .rk,#xpanel .row.me .nm,#xpanel .row.me .sc{color:#FF2442}#xpanel .row.me .nm{font-weight:600}' +
    '#xpanel .ft{padding:4px 8px 0;border-top:1px solid #f2f2f2;margin-top:4px}#xpanel .ft:empty{display:none}' +
    '#xpanel .msg{padding:26px 12px;text-align:center;color:#999;font-size:14px}' +
    '#xpanel .spin{width:24px;height:24px;margin:0 auto 10px;border-radius:50%;border:3px solid #ffe0e5;border-top-color:#FF2442;-webkit-animation:xspin .8s linear infinite;animation:xspin .8s linear infinite}' +
    '@-webkit-keyframes xspin{to{-webkit-transform:rotate(360deg)}}@keyframes xspin{to{transform:rotate(360deg)}}';
  document.head.appendChild(css);
  btn = document.createElement('button'); btn.id = 'xcap'; btn.setAttribute('aria-label', 'rank');
  function capLabel() { btn.innerHTML = '<span class="ic"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M8.5 20h7M10 17h4"/></svg></span><span>' + esc(t('title')) + '</span><span class="ar">›</span>'; }
  // level with the container's own top buttons (getWindowInfo, 9.49+), in the middle of the screen; the safe area otherwise
  function place() {
    var m = mt(); if (!m || typeof m.getWindowInfo !== 'function') return;
    Promise.resolve(m.getWindowInfo()).then(function (w) {
      var b = w && w.menuButtons, r = b && (b.share || b.me || b.back);
      if (r && r.height > 0) { btn.style.top = r.top + 'px'; btn.style.height = r.height + 'px'; btn.style.borderRadius = (r.height / 2) + 'px'; }
    }, function () {});
  }
  panel = document.createElement('div'); panel.id = 'xpanel';
  panel.innerHTML = '<div class="tt"></div><div class="ls"></div><div class="ft"></div>';
  document.body.appendChild(btn); document.body.appendChild(panel);
  list = panel.querySelector('.ls'); var foot = panel.querySelector('.ft');
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  // no avatars: the board gives rank, score and nickname only, there is no API for the player's own profile, and the
  // container loads no web images
  function row(rk, nm, sc, me) {
    return '<div class="row' + (me ? ' me' : '') + '"><span class="rk' + (typeof rk === 'number' && rk <= 3 ? ' t' : '') + '">' + rk + '</span><span class="nm">' + esc(nm) + '</span><span class="sc">' + sc + '</span></div>';
  }
  function render(r) {
    var L = r[0], M = r[1], h = '';
    foot.innerHTML = '';
    if (L.e) { list.innerHTML = '<div class="msg">' + (unauth(L.e) ? t('closed') : t('fail')) + '</div>'; return; }
    var data = (L.v && L.v.data) || [], my = M.e ? null : (M.v || {}), mine = my && my.status === 'EXACT' ? my.rank : 0, shown = false;
    for (var i = 0; i < data.length; i++) {      // ranks are unique, so your own row in the top 100 is the one with your rank
      var me = mine && data[i].rank === mine; if (me) shown = true;
      h += row(data[i].rank, me ? t('you') : (data[i].nickname == null ? t('anon') : data[i].nickname), data[i].score + ' ' + t('wins'), me);
    }
    if (!data.length) h = '<div class="msg">' + t('none') + '</div>';
    list.innerHTML = h; list.scrollTop = 0;
    if (shown) { var el = list.querySelector('.row.me'); if (el) list.scrollTop = Math.max(0, el.offsetTop - list.clientHeight / 2); return; }      // in the list: brought into view
    var rk = '-', sc = '', note = '';      // not in it: the same row, highlighted, pinned under the list
    if (M.e) note = unauth(M.e) ? t('meAuth') : '';
    else if (my.status === 'EXACT') { rk = my.rank; sc = my.score + ' ' + t('wins'); }
    else if (my.status === 'OVER_LIMIT') rk = '500+';
    else note = t('out');
    foot.innerHTML = row(rk, note || t('you'), note ? '' : sc, true);
  }
  function open() {
    panel.querySelector('.tt').textContent = t('title');
    panel.classList.add('open');
    if (cache && Date.now() - cacheAt < CACHE) return render(cache);      // fresh enough: straight to the board, no spinner
    list.innerHTML = '<div class="msg"><div class="spin"></div>' + t('wait') + '</div>'; foot.innerHTML = '';
    var t0 = Date.now(), MINSPIN = 600;      // the spinner stays at least this long, so a quick answer does not flicker
    var after = function (f) { return function (x) { setTimeout(function () { if (panel.classList.contains('open')) f(x); }, Math.max(0, MINSPIN - (Date.now() - t0))); }; };
    load().then(after(render), after(function () { list.innerHTML = '<div class="msg">' + t('fail') + '</div>'; }));
  }
  // the capsule opens and closes it, a tap anywhere else closes it (that tap does nothing in the game); the capsule itself stays
  function close() { panel.classList.remove('open'); }
  btn.addEventListener('click', function (e) { e.stopPropagation(); if (panel.classList.contains('open')) close(); else open(); });
  panel.addEventListener('pointerdown', function (e) { e.stopPropagation(); });      // scrolling the list does not reach the game
  document.addEventListener('pointerdown', function (e) {      // that first tap only closes it and does nothing in the game
    if (!panel.classList.contains('open') || btn.contains(e.target) || panel.contains(e.target)) return;
    close(); e.stopPropagation(); e.preventDefault();
  }, true);
  var lastLang = '';
  function show(v) { if (v && lastLang !== lang()) { lastLang = lang(); capLabel(); } btn.classList.toggle('on', v); }
  setInterval(function () { var v = ok && wonNow && !!window.__3bLang; show(v); if (!v) close(); }, 300);      // the floating island's lobby, after a win in this session; never hidden for an error

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
        place();
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
