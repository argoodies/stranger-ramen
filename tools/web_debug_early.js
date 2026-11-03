/* Web-only debug (tools/mk3b.py puts this into deploy/3b.html only; the app and the Xiaohongshu package are built from
   deploy/3b-embed.html, which has none of it). Runs before the game: ?mode=app pretends to be the app's Game Center bridge,
   ?mode=xhs pretends to be the Xiaohongshu container with a leaderboard, so the web can show either look.
   The sun opens the switch (tools/web_debug_late.js). */
(function () {
  var mode = (location.search.match(/[?&]mode=(\w+)/) || [])[1] || '';
  if (mode !== 'app' && mode !== 'xhs') mode = '';
  window.__debugMode = mode;
  window.__debugToast = function (text) { console.log('[debug]', text); };      // no toasts in the project: the console only
  if (mode === 'app') {      // the app's bridge: messages go to the console; achievements and scores are only logged
    window.webkit = { messageHandlers: { gc: { postMessage: function (m) { console.log('[debug · app] Game Center', m); } } } };
  }
  if (mode === 'xhs') {      // the Xiaohongshu container: a made-up board around your own total on this browser
    var names = ['小鱼干', '钟楼守夜人', null, 'Mira', '三人染爱好者', '夜猫子', '今天也赢了', '说书人的学徒', '阿锚', 'Pukka 粉', '红茶', '一分钟玩家'];
    var best = 0;
    var mine = function () { try { return Math.max(best, JSON.parse(localStorage.getItem('pocket_gc') || '{}').wins || 0); } catch (e) { return best; } };
    var board = function () {
      var rows = [], my = mine();
      for (var i = 0; i < 150; i++) rows.push({ score: Math.max(1, 300 - i * 2 - (i % 2)), nickname: names[i % names.length], me: false });      // more than the board's 100, so 'not in it' can be seen too
      if (my > 0) rows.push({ score: my, nickname: null, me: true });
      rows.sort(function (a, b) { return b.score - a.score || (a.me ? 1 : -1); });
      rows.forEach(function (r, i) { r.rank = i + 1; });
      return rows;
    };
    var later = function (v) { return new Promise(function (res) { setTimeout(function () { res(v); }, 350); }); };
    window.xhs = {
      launchOptions: { miniToolEnv: { buildVersion: 9530000 } },
      miniTool: {
        getLaunchOptions: function () { return Promise.resolve(window.xhs.launchOptions); },
        getWindowInfo: function () { return Promise.resolve({ windowWidth: innerWidth, windowHeight: innerHeight, safeArea: { top: 0 }, menuButtons: { back: null, me: null, share: { left: innerWidth - 90, top: 10, right: innerWidth - 10, bottom: 42, width: 80, height: 32 } } }); },
        submitScore: function (o) { best = Math.max(best, o.score); console.log('[debug · xhs] submitScore', o); return later({ score: best }); },
        getRankList: function () { return later({ data: board().slice(0, 100).map(function (r) { return { rank: r.rank, score: r.score, nickname: r.me ? '小红薯3C7A' : r.nickname }; }) }); },
        getMyRank: function () { var me = board().filter(function (r) { return r.me; })[0]; return later(me ? { status: me.rank <= 500 ? 'EXACT' : 'OVER_LIMIT', rank: me.rank, score: me.score } : { status: 'NOT_PARTICIPATING', rank: null, score: null }); }
      }
    };
  }
})();
