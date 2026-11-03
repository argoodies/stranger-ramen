/* The Xiaohongshu build's leaderboard (mini-tool submitScore / getRankList / getMyRank, client 9.51+, closed beta).
   Board 1, all-time: total wins, the same number the app sends to Game Center. The game posts { t: 'score', v } through
   window.__miniGC after each win and once at launch (__gcSync); a score goes up only when it has grown.
   A trophy pill sits beside the language button in the lobby and opens the top 100 (ten rows at a time, scrolling) and your own rank (under them, only when you are not among them).
   Older clients, a missing API or no nickname authorisation (1005 / 1006): no button, and the game carries on as before.
   Plain ES5 so it passes the Chrome 61 gate as written; loaded by boot.js after the game scripts. */
(function () {
  window.__xhsBuild = true;      // the Xiaohongshu build: its ball speaks only once the leaderboard works (no web one in its place)
  var MIN = 9510, BOARD = 1, CACHE = 45000, sent = 0, pend = 0, ok = false, off = false, cache = null, cacheAt = 0, btn, panel, list;
  function mt() { return window.xhs && window.xhs.miniTool; }
  function has() { var m = mt(); return !!(m && typeof m.submitScore === 'function' && typeof m.getRankList === 'function' && typeof m.getMyRank === 'function'); }
  function lang() { try { return LANG; } catch (e) { return 'hans'; } }
  var T = {
    hans: { title: '排行榜', me: '我的排名', wins: '胜', none: '还没有人上榜', fail: '暂时无法加载，稍后再试', wait: '加载中…', anon: '小红书用户', out: '未上榜', rank: '第 # 名', close: '关闭', meAuth: '授权后显示你的排名', closed: '排行榜暂未开放', you: '我' },
    hant: { title: '排行榜', me: '我的排名', wins: '勝', none: '還沒有人上榜', fail: '暫時無法載入，稍後再試', wait: '載入中…', anon: '小紅書用戶', out: '未上榜', rank: '第 # 名', close: '關閉', meAuth: '授權後顯示你的排名', closed: '排行榜暫未開放', you: '我' },
    en: { title: 'Leaderboard', me: 'My rank', wins: 'wins', none: 'Nobody on the board yet', fail: 'Could not load, try again later', wait: 'Loading…', anon: 'Player', out: 'Not ranked', rank: 'No. #', close: 'Close', meAuth: 'Your rank shows once authorised', closed: 'The leaderboard is not open yet', you: 'Me' }
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
  css.textContent = '#xcap{position:fixed;left:50%;top:calc(8px + var(--safe-area-inset-top, env(safe-area-inset-top, 0px)));-webkit-transform:translateX(-50%);transform:translateX(-50%);z-index:20;display:none;height:32px;padding:0 7.25px 0 8px;border:.5px solid rgba(0,0,0,.08);border-radius:16px;background:rgba(255,255,255,.92);box-shadow:0 2px 10px rgba(0,0,0,.12);color:#333;font:600 13px ' + XF + ';letter-spacing:.02em;white-space:nowrap;-webkit-align-items:center;align-items:center}' +
    '#xcap.on{display:-webkit-flex;display:flex}#xcap:active{opacity:.6}' +
    '#xcap .ic{width:24px;height:24px;margin-right:6px;border-radius:50%;background:#FF2442;display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;-webkit-justify-content:center;justify-content:center}' +
    '#xcap .tx{display:block}' +      // the words are an outline (svgWords): its box is its ink, so centring the box centres the words
    '#xcap .ar{margin-left:5px;display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center}#xcap .ar svg{display:block}' +
    '#xpanel{position:fixed;left:50%;top:50%;-webkit-transform:translate(-50%,-50%);transform:translate(-50%,-50%);z-index:20;display:none;-webkit-flex-direction:column;flex-direction:column;width:300px;max-width:calc(100% - 40px);max-height:66%;padding:6px 0 10px;border-radius:16px;background:#fff;color:#333;font:400 15px ' + XF + ';box-shadow:0 10px 36px rgba(0,0,0,.22)}' +
    '#xpanel.open{display:-webkit-flex;display:flex}' +
    '#xpanel .tt{padding:12px 18px 10px;font-size:17px;font-weight:600;color:#333;border-bottom:1px solid #f2f2f2}' +
    '#xpanel .ls{touch-action:pan-y;overscroll-behavior:contain;height:414px;max-height:calc(66vh - 120px);box-sizing:border-box;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:4px 8px 0}' +
    '#xpanel .row{display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;border-radius:10px;padding:10px 10px}' +
    '#xpanel .rk{width:46px;color:#999;font-weight:600;font-style:italic}#xpanel .rk.t{color:#FF2442}' +
    '#xpanel .nm{-webkit-flex:1;flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;padding-right:8px}#xpanel .sc{white-space:nowrap;color:#999;font-size:14px}' +
    '#xpanel .row.me{background:#FFF0F2}#xpanel .row.me .rk,#xpanel .row.me .nm,#xpanel .row.me .sc{color:#FF2442}#xpanel .row.me .nm{font-weight:600}' +
    '#xpanel .ft{padding:4px 8px 0;border-top:1px solid #f2f2f2;margin-top:4px}#xpanel .ft:empty{display:none}' +
    '#xpanel .msg{padding:26px 12px;text-align:center;color:#999;font-size:14px}' +
    '#xpanel .spin{width:24px;height:24px;margin:0 auto 10px;border-radius:50%;border:3px solid #ffe0e5;border-top-color:#FF2442;-webkit-animation:xspin .8s linear infinite;animation:xspin .8s linear infinite}' +
    '@-webkit-keyframes xspin{to{-webkit-transform:rotate(360deg)}}@keyframes xspin{to{transform:rotate(360deg)}}' +
    '#xpanel .sk i{display:block;height:12px;border-radius:6px;background:#f0f0f0;background:-webkit-linear-gradient(left,#f2f2f2 25%,#e6e6e6 50%,#f2f2f2 75%);background:linear-gradient(90deg,#f2f2f2 25%,#e6e6e6 50%,#f2f2f2 75%);background-size:200% 100%;-webkit-animation:xsh 1.3s linear infinite;animation:xsh 1.3s linear infinite}' +
    '#xpanel .row.blank{height:41px;box-sizing:border-box}' +
    '#xpanel .sk .rk i{width:16px}#xpanel .sk .sc i{width:38px}#xpanel .row.sk{height:41px;box-sizing:border-box}' +      // the height of a real row
    '@-webkit-keyframes xsh{from{background-position:150% 0}to{background-position:-50% 0}}@keyframes xsh{from{background-position:150% 0}to{background-position:-50% 0}}' +
    // the language menu in the same manner as the board: a white card, the chosen language in red (the button is the shared 文A mark, tools/mk3b.py)
    '#langMenu{padding:6px!important;min-width:150px;border:0!important;border-radius:14px!important;background:#fff!important;box-shadow:0 10px 36px rgba(0,0,0,.2)}' +
    '#langMenu button{position:relative;border-radius:10px!important;padding:10px 40px 10px 14px!important;font:400 15px ' + XF + '!important;letter-spacing:0!important;color:#333!important;background:transparent!important}' +
    '#langMenu button+button{margin-top:2px}#langMenu button.on{background:#FFF0F2!important;color:#FF2442!important;font-weight:600!important}' +
    '#langMenu button.on::after{content:"";position:absolute;right:16px;top:50%;width:5px;height:10px;margin-top:-7px;border:solid #FF2442;border-width:0 2px 2px 0;-webkit-transform:rotate(45deg);transform:rotate(45deg)}';      // a red tick on the right of the chosen one
  document.head.appendChild(css);
  btn = document.createElement('button'); btn.id = 'xcap'; btn.setAttribute('aria-label', 'rank');
  var LABELS = /*LABELS*/{"hans":["M182 -840V-638H55V-568H182V-348L42 -311L57 -237L182 -274V-14C182 -1 177 3 164 4C154 4 115 4 74 3C83 22 93 53 96 72C158 72 196 70 221 58C245 47 254 27 254 -14V-295L373 -331L364 -399L254 -368V-568H362V-638H254V-840ZM380 -253V-184H550V79H623V-833H550V-669H401V-601H550V-461H404V-394H550V-253ZM715 -833V80H787V-181H962V-250H787V-394H941V-461H787V-601H950V-669H787V-833Z M1435 -780V-708H1927V-780ZM1267 -841C1216 -768 1119 -679 1035 -622C1048 -608 1069 -579 1079 -562C1169 -626 1272 -724 1339 -811ZM1391 -504V-432H1728V-17C1728 -1 1721 4 1702 5C1684 6 1616 6 1545 3C1556 25 1567 56 1570 77C1668 77 1725 77 1759 66C1792 53 1804 30 1804 -16V-432H1955V-504ZM1307 -626C1238 -512 1128 -396 1025 -322C1040 -307 1067 -274 1078 -259C1115 -289 1154 -325 1192 -364V83H1266V-446C1308 -496 1346 -548 1378 -600Z M2369 -555V-395H2438V-494H2875V-395H2947V-555H2797C2813 -589 2831 -630 2847 -670L2773 -684C2762 -646 2743 -595 2726 -555H2565L2587 -560C2581 -590 2564 -640 2548 -677L2482 -665C2495 -631 2509 -586 2515 -555ZM2608 -837C2617 -809 2625 -775 2631 -746H2382V-684H2928V-746H2705C2699 -777 2688 -815 2677 -846ZM2604 -458C2615 -427 2625 -390 2631 -361H2382V-298H2533C2522 -142 2487 -34 2336 26C2352 39 2372 65 2380 81C2494 32 2551 -41 2580 -141H2804C2795 -46 2785 -6 2771 8C2763 16 2755 16 2739 16C2723 16 2680 16 2635 12C2646 30 2653 56 2655 76C2701 78 2747 79 2770 76C2796 75 2815 69 2831 53C2854 29 2867 -31 2879 -174C2881 -183 2882 -203 2882 -203H2594C2599 -233 2603 -264 2605 -298H2930V-361H2707C2702 -391 2689 -434 2674 -468ZM2177 -840V-647H2047V-577H2167C2141 -441 2084 -281 2027 -197C2040 -179 2057 -145 2066 -124C2108 -190 2147 -297 2177 -409V79H2242V-443C2266 -393 2293 -332 2305 -300L2349 -353C2334 -384 2262 -511 2242 -541V-577H2347V-647H2242V-840Z",42.0,-846.0,2905.0,929.0],"hant":["M310 -199 339 -134 500 -193C476 -107 428 -31 334 31C350 43 375 66 387 81C569 -42 592 -218 592 -418V-840H523V-669H359V-600H523V-460H366V-392H523C522 -347 520 -303 514 -262C438 -237 364 -213 310 -199ZM696 -840V79H767V-173H960V-242H767V-392H933V-460H767V-600H943V-669H767V-840ZM167 -839V-638H42V-568H167V-363L28 -321L47 -249L167 -288V-7C167 7 162 11 150 11C138 12 99 12 56 10C65 31 75 62 77 80C141 81 179 78 203 66C228 55 237 34 237 -7V-311L347 -347L336 -416L237 -385V-568H345V-638H237V-839Z M1435 -780V-708H1927V-780ZM1267 -841C1216 -768 1119 -679 1035 -622C1048 -608 1069 -579 1079 -562C1169 -626 1272 -724 1339 -811ZM1391 -504V-432H1728V-17C1728 -1 1721 4 1702 5C1684 6 1616 6 1545 3C1556 25 1567 56 1570 77C1668 77 1725 77 1759 66C1792 53 1804 30 1804 -16V-432H1955V-504ZM1307 -626C1238 -512 1128 -396 1025 -322C1040 -307 1067 -274 1078 -259C1115 -289 1154 -325 1192 -364V83H1266V-446C1308 -496 1346 -548 1378 -600Z M2369 -555V-395H2438V-494H2875V-395H2947V-555H2797C2813 -589 2831 -630 2847 -670L2773 -684C2762 -646 2743 -595 2726 -555H2565L2587 -560C2581 -590 2564 -640 2548 -677L2482 -665C2495 -631 2509 -586 2515 -555ZM2608 -837C2617 -809 2625 -775 2631 -746H2382V-684H2928V-746H2705C2699 -777 2688 -815 2677 -846ZM2604 -458C2615 -427 2625 -390 2631 -361H2382V-298H2533C2522 -142 2487 -34 2336 26C2352 39 2372 65 2380 81C2494 32 2551 -41 2580 -141H2804C2795 -46 2785 -6 2771 8C2763 16 2755 16 2739 16C2723 16 2680 16 2635 12C2646 30 2653 56 2655 76C2701 78 2747 79 2770 76C2796 75 2815 69 2831 53C2854 29 2867 -31 2879 -174C2881 -183 2882 -203 2882 -203H2594C2599 -233 2603 -264 2605 -298H2930V-361H2707C2702 -391 2689 -434 2674 -468ZM2177 -840V-647H2047V-577H2167C2141 -441 2084 -281 2027 -197C2040 -179 2057 -145 2066 -124C2108 -190 2147 -297 2177 -409V79H2242V-443C2266 -393 2293 -332 2305 -300L2349 -353C2334 -384 2262 -511 2242 -541V-577H2347V-647H2242V-840Z",28.0,-846.0,2919.0,929.0],"en":["M101 0H514V-79H193V-733H101Z M855 13C928 13 986 -11 1033 -42L1001 -103C960 -76 918 -60 865 -60C762 -60 691 -134 685 -250H1051C1053 -264 1055 -282 1055 -302C1055 -457 977 -557 838 -557C714 -557 595 -448 595 -271C595 -92 710 13 855 13ZM684 -315C695 -423 763 -484 840 -484C925 -484 975 -425 975 -315Z M1314 13C1381 13 1442 -22 1494 -65H1497L1505 0H1580V-334C1580 -469 1525 -557 1392 -557C1304 -557 1228 -518 1179 -486L1214 -423C1257 -452 1314 -481 1377 -481C1466 -481 1489 -414 1489 -344C1258 -318 1156 -259 1156 -141C1156 -43 1223 13 1314 13ZM1340 -61C1286 -61 1244 -85 1244 -147C1244 -217 1306 -262 1489 -283V-132C1436 -85 1392 -61 1340 -61Z M1937 13C2002 13 2060 -22 2102 -64H2105L2113 0H2188V-796H2096V-587L2101 -494C2053 -533 2012 -557 1948 -557C1824 -557 1713 -447 1713 -271C1713 -90 1801 13 1937 13ZM1957 -64C1862 -64 1807 -141 1807 -272C1807 -396 1877 -480 1964 -480C2009 -480 2051 -464 2096 -423V-138C2051 -88 2007 -64 1957 -64Z M2592 13C2665 13 2723 -11 2770 -42L2738 -103C2697 -76 2655 -60 2602 -60C2499 -60 2428 -134 2422 -250H2788C2790 -264 2792 -282 2792 -302C2792 -457 2714 -557 2575 -557C2451 -557 2332 -448 2332 -271C2332 -92 2447 13 2592 13ZM2421 -315C2432 -423 2500 -484 2577 -484C2662 -484 2712 -425 2712 -315Z M2926 0H3018V-349C3054 -441 3109 -475 3154 -475C3177 -475 3189 -472 3207 -466L3224 -545C3207 -554 3190 -557 3166 -557C3106 -557 3050 -513 3012 -444H3010L3001 -543H2926Z M3553 13C3677 13 3789 -94 3789 -280C3789 -448 3713 -557 3573 -557C3512 -557 3452 -523 3402 -481L3406 -578V-796H3314V0H3387L3395 -56H3399C3446 -13 3503 13 3553 13ZM3538 -64C3502 -64 3453 -78 3406 -120V-406C3457 -454 3505 -480 3550 -480C3654 -480 3694 -400 3694 -279C3694 -145 3628 -64 3538 -64Z M4143 13C4276 13 4394 -91 4394 -271C4394 -452 4276 -557 4143 -557C4010 -557 3892 -452 3892 -271C3892 -91 4010 13 4143 13ZM4143 -63C4049 -63 3986 -146 3986 -271C3986 -396 4049 -480 4143 -480C4237 -480 4301 -396 4301 -271C4301 -146 4237 -63 4143 -63Z M4663 13C4730 13 4791 -22 4843 -65H4846L4854 0H4929V-334C4929 -469 4874 -557 4741 -557C4653 -557 4577 -518 4528 -486L4563 -423C4606 -452 4663 -481 4726 -481C4815 -481 4838 -414 4838 -344C4607 -318 4505 -259 4505 -141C4505 -43 4572 13 4663 13ZM4689 -61C4635 -61 4593 -85 4593 -147C4593 -217 4655 -262 4838 -283V-132C4785 -85 4741 -61 4689 -61Z M5101 0H5193V-349C5229 -441 5284 -475 5329 -475C5352 -475 5364 -472 5382 -466L5399 -545C5382 -554 5365 -557 5341 -557C5281 -557 5225 -513 5187 -444H5185L5176 -543H5101Z M5674 13C5739 13 5797 -22 5839 -64H5842L5850 0H5925V-796H5833V-587L5838 -494C5790 -533 5749 -557 5685 -557C5561 -557 5450 -447 5450 -271C5450 -90 5538 13 5674 13ZM5694 -64C5599 -64 5544 -141 5544 -272C5544 -396 5614 -480 5701 -480C5746 -480 5788 -464 5833 -423V-138C5788 -88 5744 -64 5694 -64Z",101.0,-796.0,5824.0,809.0]}/*/LABELS*/;
  function svgWords(lang, color, px) {      // the words as their outline (tools/mklabels.py): the svg box is the ink's box
    var L = LABELS[lang] || LABELS.hans, k = px / 1000, P = 60;      // an even margin round the ink (em/1000): the edges' smoothing is not clipped, the centre stays put
    return '<svg width="' + ((L[3] + 2 * P) * k).toFixed(2) + '" height="' + ((L[4] + 2 * P) * k).toFixed(2) + '" viewBox="' + (L[1] - P) + ' ' + (L[2] - P) + ' ' + (L[3] + 2 * P) + ' ' + (L[4] + 2 * P) + '" style="display:block;overflow:visible"><path fill="' + color + '" d="' + L[0] + '"/></svg>';
  }
  function capLabel() { btn.innerHTML = '<span class="ic"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M8.5 20h7M10 17h4"/></svg></span><span class="tx" aria-label="' + esc(t('title')) + '">' + svgWords(lang(), '#333', 13) + '</span><span class="ar"><svg width="8" height="12" viewBox="0 0 8 12" fill="none" stroke="#333" stroke-width=".85" stroke-linecap="round" stroke-linejoin="round"><path d="M2 2l4 4-4 4"/></svg></span>'; }      // a drawn chevron: a text \u203a sits on the font\'s baseline, not in the middle
  // level with the container's own top buttons (getWindowInfo, 9.49+), in the middle of the screen; the safe area otherwise
  function place() {
    var m = mt(); if (!m || typeof m.getWindowInfo !== 'function') return;
    Promise.resolve(m.getWindowInfo()).then(function (w) {
      var b = w && w.menuButtons, r = b && (b.share || b.me || b.back);
      if (r && r.height > 0) { btn.style.top = r.top + 'px'; btn.style.height = r.height + 'px'; btn.style.borderRadius = (r.height / 2) + 'px'; }
    }, function () {});
  }
  panel = document.createElement('div'); panel.id = 'xpanel';
  panel.innerHTML = '<div class="tt"></div><div class="ls" data-scroll></div><div class="ft"></div>';      // data-scroll: the game lets a touch there scroll (index.html)
  document.body.appendChild(btn); document.body.appendChild(panel);
  list = panel.querySelector('.ls'); var foot = panel.querySelector('.ft');
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  // no avatars: the board gives rank, score and nickname only, there is no API for the player's own profile, and the
  // container loads no web images
  var TOP = 100, SEEN = 10;      // the board holds the top 100 in a box ten rows tall that scrolls; under it one more row: your own rank if you are further down, else an empty one
  function row(rk, nm, sc, me) {
    return '<div class="row' + (me ? ' me' : '') + '"><span class="rk' + (typeof rk === 'number' && rk <= 3 ? ' t' : '') + '">' + rk + '</span><span class="nm">' + esc(nm) + '</span><span class="sc">' + sc + '</span></div>';
  }
  function render(r) {
    var L = r[0], M = r[1], h = '';
    foot.innerHTML = '';
    if (L.e) { list.innerHTML = '<div class="msg">' + (unauth(L.e) ? t('closed') : t('fail')) + '</div>'; return; }
    var data = ((L.v && L.v.data) || []).slice(0, TOP), my = M.e ? null : (M.v || {}), mine = my && my.status === 'EXACT' ? my.rank : 0, shown = false;
    for (var i = 0; i < data.length; i++) {      // ranks are unique, so your own row in the top 100 is the one with your rank
      var me = mine && data[i].rank === mine; if (me) shown = true;
      h += row(data[i].rank, me ? t('you') : (data[i].nickname == null ? t('anon') : data[i].nickname), data[i].score + ' ' + t('wins'), me);
    }
    if (!data.length) h = '<div class="msg">' + t('none') + '</div>';
    list.innerHTML = h; list.scrollTop = 0;
    if (shown) { foot.innerHTML = '<div class="row blank"></div>'; var el = list.querySelector('.row.me'); if (el) list.scrollTop = Math.max(0, el.offsetTop - list.offsetTop - (list.clientHeight - el.offsetHeight) / 2); return; }      // in the top 100: highlighted where it is and scrolled to the middle of the box, an empty row underneath so the board keeps its height
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
    // loading: skeleton rows the size of the real ones, so the board opens at its full height and does not jump when the data comes
    var sk = '', W = [62, 48, 70, 54, 44, 66, 58, 50, 68, 46];      // as many as the board shows
    for (var k = 0; k < W.length; k++) sk += '<div class="row sk"><span class="rk"><i></i></span><span class="nm"><i style="width:' + W[k] + '%"></i></span><span class="sc"><i></i></span></div>';
    list.innerHTML = sk; list.scrollTop = 0; foot.innerHTML = '<div class="row sk"><span class="rk"><i></i></span><span class="nm"><i style="width:30%"></i></span><span class="sc"><i></i></span></div>';
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
  // ---- what the ball says: tapped (tools/mk3b.py), it turns once and then tells you, in a speech bubble like everyone else's,
  // how many games you have won and where that puts you among all players
  var SAY = {
    hans: { rank: '你赢了 {w} 局，全网排名第 {r}。', over: '你赢了 {w} 局，全网排名 500 名开外。', none: '你赢了 {w} 局，还没上榜。', fail: '暂时查不到排名，稍后再试。' },
    hant: { rank: '你贏了 {w} 局，全網排名第 {r}。', over: '你贏了 {w} 局，全網排名 500 名開外。', none: '你贏了 {w} 局，還沒上榜。', fail: '暫時查不到排名，稍後再試。' },
    en: { rank: '{w} wins so far, No. {r} worldwide.', over: '{w} wins so far, outside the top 500.', none: '{w} wins so far, not ranked yet.', fail: 'Could not get your rank, try again later.' }
  };
  function say(k, w, r) { var S = SAY[lang()] || SAY.hans; if (window.__markSay) window.__markSay(S[k].replace('{w}', w).replace('{r}', r)); }
  function fill(res) {
    var M = res[1], my = M.e ? null : (M.v || {}), w = Math.max(sent, (my && my.score) || 0);
    if (!my) say('fail'); else if (my.status === 'EXACT') say('rank', w, my.rank); else if (my.status === 'OVER_LIMIT') say('over', w); else say('none', w);
  }
  var busy = false;
  function openMe() {
    if (busy) return; busy = true;      // the bubble comes when the ball has stopped turning (a second), or when the rank does if later
    var t0 = Date.now(), after = function (f) { return function (v) { setTimeout(function () { busy = false; f(v); }, Math.max(0, 1000 - (Date.now() - t0))); }; };
    load().then(after(fill), after(function () { say('fail'); }));
  }
  var lastLang = '';
  // shown first, so the words are drawn to the capsule's real height
  function show(v) { btn.classList.toggle('on', v); if (v && lastLang !== lang()) { lastLang = lang(); capLabel(); } }
  setInterval(function () { show(false); if (ok && !window.__boardMark) window.__boardMark = { open: openMe }; if (!window.__3bLang) close(); }, 300);      // no capsule: once the leaderboard works, the bubbles that replace the book after a win (tools/mk3b.py) open it      // the floating island's lobby, after a win in this session; never hidden for an error

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
