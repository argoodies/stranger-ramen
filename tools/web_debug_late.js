/* Web-only debug, after the game (see tools/web_debug_early.js): a tap on the sun opens a small menu to switch between the
   web, the Xiaohongshu look and the app look (the page reloads with ?mode=), and to fake a win so the capsules show. */
(function () {
  var mode = window.__debugMode || '';
  var LABEL = { '': '网页（默认）', xhs: '小红书模式', app: 'App 模式' };
  var st = document.createElement('style');
  st.textContent = '#dbgsun{position:fixed;left:calc(80% - 30px);top:calc(14% - 30px);width:60px;height:60px;border-radius:50%;z-index:19;background:transparent;border:0;padding:0;cursor:pointer;-webkit-tap-highlight-color:transparent}' +
    '#dbgmenu{position:fixed;right:calc(20% - 40px);top:calc(14% + 32px);z-index:60;display:none;min-width:170px;padding:6px;border-radius:12px;background:rgba(255,255,255,.96);box-shadow:0 8px 28px rgba(0,0,0,.25);font:14px -apple-system,"PingFang SC","Noto Sans CJK SC",sans-serif;color:#222}' +
    '#dbgmenu.open{display:block}#dbgmenu button{display:block;width:100%;text-align:left;border:0;background:transparent;padding:9px 12px;border-radius:8px;font:inherit;color:inherit;cursor:pointer}#dbgmenu button.on{background:#eef3ff;color:#1d5bd8;font-weight:600}#dbgmenu hr{border:0;border-top:1px solid #eee;margin:4px 6px}' +
    '#dbgmenu .tt{padding:6px 12px 4px;font-size:11px;letter-spacing:.08em;color:#999}' +
    '#dbgtag{position:fixed;left:8px;bottom:8px;z-index:60;padding:3px 8px;border-radius:6px;background:rgba(0,0,0,.55);color:#fff;font:11px -apple-system,sans-serif;pointer-events:none}';
  document.head.appendChild(st);
  var sun = document.createElement('button'); sun.id = 'dbgsun'; sun.setAttribute('aria-label', 'debug');
  var menu = document.createElement('div'); menu.id = 'dbgmenu';
  var h = '<div class="tt">调试 · 只在网页</div>';
  ['', 'xhs', 'app'].forEach(function (m) { h += '<button data-m="' + m + '"' + (m === mode ? ' class="on"' : '') + '>' + (m === mode ? '✓ ' : '') + LABEL[m] + '</button>'; });
  h += '<hr><button data-win="1">模拟一胜（书变成小球）</button><button data-lose="1">模拟一负（小球变回书）</button>';
  h += '<hr><button data-conf="1">放礼花</button><button data-night="1">切到黑夜 / 白天</button>';
  menu.innerHTML = h;
  document.body.appendChild(sun); document.body.appendChild(menu);
  if (mode) { var tag = document.createElement('div'); tag.id = 'dbgtag'; tag.textContent = 'DEBUG · ' + LABEL[mode]; document.body.appendChild(tag); }
  sun.addEventListener('click', function (e) { e.stopPropagation(); menu.classList.toggle('open'); });
  menu.addEventListener('pointerdown', function (e) { e.stopPropagation(); });
  document.addEventListener('pointerdown', function (e) { if (menu.classList.contains('open') && !menu.contains(e.target) && e.target !== sun) menu.classList.remove('open'); }, true);
  menu.querySelectorAll('button[data-m]').forEach(function (b) {
    b.addEventListener('click', function () {
      var m = b.getAttribute('data-m'); if (m === mode) { menu.classList.remove('open'); return; }
      var u = new URL(location.href); if (m) u.searchParams.set('mode', m); else u.searchParams.delete('mode'); location.href = u.toString();
    });
  });
  // a faked game, recorded as a real one (botc3.js gcRecord): the count on this browser goes up, the ball or the book shows, the score goes out
  menu.querySelector('button[data-lose]').addEventListener('click', function () { gcRecord(false, 'sailor'); menu.classList.remove('open'); });
  // fireworks over the table, as after a win
  menu.querySelector('button[data-conf]').addEventListener('click', function () { if (window.__confettiGo) window.__confettiGo(); menu.classList.remove('open'); });
  // the lobby's day and night, as if the last game had ended by day or at night (eases over like the real thing)
  menu.querySelector('button[data-night]').addEventListener('click', function () { if (!window.__lobbyNight) return; var n = !window.__lobbyNight(); window.__lobbyNight(n); menu.classList.remove('open'); window.__debugToast('（调试）' + (n ? '已切到黑夜' : '已切到白天')); });
  menu.querySelector('button[data-win]').addEventListener('click', function () { gcRecord(true, 'sailor'); menu.classList.remove('open'); window.__debugToast('（调试）已模拟一胜'); });
})();
