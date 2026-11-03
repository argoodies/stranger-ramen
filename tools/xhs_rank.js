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
  css.textContent = '#xcap{position:fixed;left:50%;top:calc(8px + var(--safe-area-inset-top, env(safe-area-inset-top, 0px)));-webkit-transform:translateX(-50%);transform:translateX(-50%);z-index:20;display:none;height:32px;padding:0 7.25px 0 8px;border:.5px solid rgba(0,0,0,.08);border-radius:16px;background:rgba(255,255,255,.92);box-shadow:0 2px 10px rgba(0,0,0,.12);color:#333;font:600 13px ' + XF + ';letter-spacing:.02em;white-space:nowrap;-webkit-align-items:center;align-items:center}' +
    '#xcap.on{display:-webkit-flex;display:flex}' +
    '#xcap .ic{width:24px;height:24px;margin-right:6px;border-radius:50%;background:#FF2442;display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center;-webkit-justify-content:center;justify-content:center}' +
    '#xcap .tx{display:block}' +      // the words are an outline (svgWords): its box is its ink, so centring the box centres the words
    '#xcap .ar{margin-left:5px;display:-webkit-flex;display:flex;-webkit-align-items:center;align-items:center}#xcap .ar svg{display:block}' +
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
    '@-webkit-keyframes xspin{to{-webkit-transform:rotate(360deg)}}@keyframes xspin{to{transform:rotate(360deg)}}' +
    '#xpanel .sk i{display:block;height:12px;border-radius:6px;background:#f0f0f0;background:-webkit-linear-gradient(left,#f2f2f2 25%,#e6e6e6 50%,#f2f2f2 75%);background:linear-gradient(90deg,#f2f2f2 25%,#e6e6e6 50%,#f2f2f2 75%);background-size:200% 100%;-webkit-animation:xsh 1.3s linear infinite;animation:xsh 1.3s linear infinite}' +
    '#xpanel .sk .rk i{width:16px}#xpanel .sk .sc i{width:38px}#xpanel .row.sk{height:41px;box-sizing:border-box}' +      // the height of a real row
    '@-webkit-keyframes xsh{from{background-position:150% 0}to{background-position:-50% 0}}@keyframes xsh{from{background-position:150% 0}to{background-position:-50% 0}}' +
    // the language button and its menu in the same manner as the board: a white circle, a white card, the chosen language in red
    // a small black see-through circle (26px, in a 40px tap area) holding the mark; no shadow, no grey edge
    '#lang{width:40px!important;height:40px!important;padding:0!important;border:0!important;border-radius:50%!important;background:transparent!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important;box-shadow:none!important;color:#fff!important}#lang svg{display:block;margin:0 auto}#lang::before{content:"";position:absolute;left:50%;top:50%;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;background:rgba(0,0,0,.35);z-index:-1}#lang{position:relative;z-index:0}' +
    '#langMenu{padding:6px!important;min-width:150px;border:0!important;border-radius:14px!important;background:#fff!important;box-shadow:0 10px 36px rgba(0,0,0,.2)}' +
    '#langMenu button{border-radius:10px!important;padding:10px 14px!important;font:400 15px ' + XF + '!important;letter-spacing:0!important;color:#333!important;background:transparent!important}' +
    '#langMenu button+button{margin-top:2px}#langMenu button.on{background:#FFF0F2!important;color:#FF2442!important;font-weight:600!important}';
  document.head.appendChild(css);
  btn = document.createElement('button'); btn.id = 'xcap'; btn.setAttribute('aria-label', 'rank');
  var LABELS = /*LABELS*/{"hans":["M744 -213C801 -143 858 -47 876 17L977 -42C956 -108 896 -198 837 -266ZM266 -250V-65C266 46 304 80 452 80C482 80 615 80 647 80C760 80 796 49 811 -76C777 -83 724 -101 698 -119C692 -42 683 -29 637 -29C602 -29 491 -29 464 -29C404 -29 394 -34 394 -66V-250ZM113 -237C99 -156 69 -64 31 -13L143 38C186 -28 216 -128 228 -216ZM298 -544H704V-418H298ZM167 -656V-306H489L419 -250C479 -209 550 -143 585 -96L672 -173C640 -212 579 -267 520 -306H840V-656H699L785 -800L660 -852C639 -792 604 -715 569 -656H383L440 -683C424 -732 380 -799 338 -849L235 -800C268 -757 302 -700 320 -656Z M1409 -48V65H1969V-48H1749V-236H1930V-347H1749V-522H1944V-636H1749V-837H1632V-636H1559C1571 -682 1581 -730 1589 -778L1476 -798C1459 -681 1429 -561 1385 -478V-815H1076V-450C1076 -304 1072 -101 1018 36C1045 46 1094 73 1115 90C1152 -1 1169 -124 1177 -242H1275V-46C1275 -34 1272 -30 1261 -30C1251 -30 1219 -30 1189 -31C1203 -1 1216 53 1219 84C1279 84 1318 81 1348 61C1378 42 1385 8 1385 -44V-437C1412 -422 1448 -400 1466 -386C1488 -424 1508 -470 1525 -522H1632V-347H1451V-236H1632V-48ZM1183 -706H1275V-586H1183ZM1183 -478H1275V-353H1182L1183 -451Z M2421 -409C2430 -418 2471 -424 2511 -424H2520C2488 -337 2435 -262 2366 -209L2354 -263L2261 -230V-497H2360V-611H2261V-836H2149V-611H2040V-497H2149V-190C2103 -175 2061 -161 2026 -151L2065 -28C2157 -64 2272 -110 2378 -154L2374 -170C2395 -156 2417 -139 2429 -128C2517 -195 2591 -298 2632 -424H2689C2636 -231 2538 -75 2391 17C2417 32 2463 64 2482 82C2630 -27 2738 -201 2799 -424H2833C2818 -169 2799 -65 2776 -40C2766 -27 2756 -23 2740 -23C2722 -23 2687 -24 2648 -28C2667 3 2680 51 2681 85C2728 86 2771 85 2799 80C2832 76 2857 65 2880 34C2916 -10 2936 -140 2956 -485C2958 -499 2959 -536 2959 -536H2612C2699 -594 2792 -666 2879 -746L2794 -814L2768 -804H2374V-691H2640C2571 -633 2503 -588 2477 -571C2439 -546 2402 -525 2372 -520C2388 -491 2413 -434 2421 -409Z M3576 -667H3750C3744 -638 3734 -602 3723 -570H3605C3600 -598 3587 -636 3576 -667ZM3593 -841C3599 -817 3605 -788 3609 -762H3386V-667H3552L3469 -652C3478 -627 3486 -596 3491 -570H3370V-394H3478V-477H3844V-396H3957V-570H3834L3869 -655L3786 -667H3938V-762H3728C3722 -792 3713 -827 3703 -856ZM3594 -443C3602 -420 3608 -391 3612 -367H3387V-269H3521C3509 -142 3476 -52 3334 3C3358 24 3389 66 3400 92C3512 47 3570 -19 3602 -105H3783C3778 -53 3771 -28 3762 -18C3754 -10 3746 -9 3731 -9C3715 -9 3679 -9 3641 -14C3657 13 3668 55 3670 86C3718 88 3762 87 3787 84C3816 81 3839 74 3859 52C3883 26 3895 -34 3903 -161C3905 -175 3906 -202 3906 -202H3626C3630 -223 3632 -246 3634 -269H3938V-367H3734C3730 -394 3719 -431 3707 -460ZM3155 -850V-663H3038V-552H3147C3122 -431 3072 -290 3017 -212C3035 -180 3060 -125 3070 -91C3102 -142 3131 -216 3155 -297V89H3256V-366C3273 -326 3289 -286 3298 -258L3363 -339C3348 -368 3280 -485 3256 -520V-552H3350V-663H3256V-850Z",31.0,-856.0,3926.0,948.0],"hant":["M179 -177C189 -110 200 -23 201 35L283 14C280 -43 269 -128 257 -196ZM80 -189C71 -107 58 -20 32 40C53 46 94 58 113 68C136 7 154 -87 164 -175ZM810 -181C838 -112 873 -21 890 38L973 0C955 -57 920 -145 890 -213ZM67 -220C89 -232 122 -243 314 -282L324 -230L408 -258C400 -308 375 -391 352 -453L273 -431L293 -366L193 -348C268 -438 340 -547 396 -653L302 -705C282 -659 257 -612 232 -568L164 -563C214 -636 263 -725 298 -810L194 -853C161 -747 100 -635 79 -607C60 -576 43 -557 24 -552C36 -524 53 -474 59 -452C74 -460 96 -466 174 -475C146 -432 122 -400 109 -385C78 -348 57 -323 32 -317C45 -290 61 -240 67 -220ZM426 -205C418 -161 405 -109 388 -63C382 -106 365 -169 350 -219L275 -197C289 -145 305 -78 310 -33L386 -57C377 -30 366 -6 355 15L439 54C470 -7 492 -103 508 -176ZM623 -232C653 -182 693 -113 711 -73L768 -102C764 -25 759 -12 734 -12C717 -12 658 -12 645 -12C616 -12 611 -16 611 -41V-202H512V-40C512 44 535 71 631 71C650 71 725 71 744 71C818 71 844 42 853 -70C828 -76 791 -89 770 -103L793 -115C773 -153 733 -216 703 -264H925V-758H687L729 -839L608 -858C602 -829 591 -790 579 -758H425V-264H691ZM528 -662H817V-584L753 -595C743 -578 730 -560 714 -542L690 -568C711 -592 729 -618 744 -644L672 -657C664 -643 654 -629 642 -615L603 -650L544 -611L592 -566C573 -550 552 -536 528 -522ZM638 -517 661 -490C629 -463 591 -437 546 -415C561 -404 581 -379 590 -362C633 -385 670 -411 703 -439C723 -413 740 -389 752 -368L815 -414C801 -437 781 -464 758 -492C781 -517 800 -543 817 -570V-360H528V-509C541 -497 556 -479 564 -466C591 -482 616 -499 638 -517Z M1836 -835C1813 -796 1776 -746 1740 -714C1753 -705 1771 -692 1788 -678H1710C1719 -729 1726 -784 1731 -843L1621 -849C1617 -787 1611 -730 1601 -678H1517L1586 -723C1567 -756 1527 -802 1489 -836L1406 -787C1439 -756 1475 -711 1494 -678H1416V-580H1576C1569 -560 1561 -540 1553 -522H1385V-424H1490C1456 -385 1415 -353 1365 -327V-804H1082V-441C1082 -296 1078 -96 1026 42C1052 52 1099 76 1119 93C1157 -7 1173 -144 1179 -271H1260V-37C1260 -26 1257 -22 1246 -22C1236 -22 1206 -22 1177 -23C1191 6 1204 58 1206 87C1263 88 1301 85 1329 66C1359 47 1365 15 1365 -35V-282C1383 -262 1402 -240 1411 -228C1427 -237 1443 -246 1458 -256V-181H1562C1537 -102 1487 -42 1380 -2C1404 19 1434 62 1447 89C1587 30 1647 -61 1675 -181H1771C1764 -79 1756 -36 1745 -22C1737 -14 1728 -12 1715 -12C1699 -12 1667 -13 1632 -16C1648 11 1659 52 1661 83C1705 85 1748 84 1772 81C1800 77 1821 69 1840 46C1864 17 1875 -59 1884 -237L1886 -260L1914 -244C1930 -268 1963 -307 1985 -326C1933 -347 1881 -383 1841 -424H1962V-522H1667C1674 -541 1681 -560 1687 -580H1926V-678H1845C1875 -713 1905 -757 1930 -804ZM1589 -370C1587 -338 1585 -308 1582 -279H1491C1544 -319 1587 -367 1621 -424H1721C1756 -370 1805 -318 1858 -279H1691C1694 -308 1696 -338 1698 -370ZM1183 -695H1260V-581H1183ZM1183 -476H1260V-374H1182L1183 -442Z M2532 -615H2790V-567H2532ZM2532 -741H2790V-694H2532ZM2425 -824V-484H2901V-824ZM2022 -195 2067 -74C2129 -104 2201 -139 2274 -176C2298 -160 2335 -124 2352 -105C2392 -131 2431 -165 2467 -203H2527C2473 -129 2397 -60 2323 -22C2351 -4 2382 25 2401 49C2488 -7 2583 -107 2636 -203H2695C2652 -111 2584 -21 2508 27C2538 43 2574 71 2594 94C2675 30 2754 -91 2795 -203H2833C2822 -83 2810 -31 2796 -16C2788 -7 2780 -5 2767 -5C2753 -5 2727 -5 2695 -8C2710 17 2720 58 2722 86C2763 88 2800 87 2823 84C2849 80 2871 73 2890 50C2917 20 2933 -61 2947 -256C2949 -270 2950 -298 2950 -298H2541C2551 -313 2560 -329 2569 -345H2970V-446H2337V-345H2450C2426 -306 2394 -270 2359 -239L2337 -325L2258 -290V-526H2350V-639H2258V-837H2146V-639H2045V-526H2146V-243C2099 -224 2056 -207 2022 -195Z M3576 -667H3750C3744 -638 3734 -602 3723 -570H3605C3600 -598 3587 -636 3576 -667ZM3593 -841C3599 -817 3605 -788 3609 -762H3386V-667H3552L3469 -652C3478 -627 3486 -596 3491 -570H3370V-394H3478V-477H3844V-396H3957V-570H3834L3869 -655L3786 -667H3938V-762H3728C3722 -792 3713 -827 3703 -856ZM3594 -443C3602 -420 3608 -391 3612 -367H3387V-269H3521C3509 -142 3476 -52 3334 3C3358 24 3389 66 3400 92C3512 47 3570 -19 3602 -105H3783C3778 -53 3771 -28 3762 -18C3754 -10 3746 -9 3731 -9C3715 -9 3679 -9 3641 -14C3657 13 3668 55 3670 86C3718 88 3762 87 3787 84C3816 81 3839 74 3859 52C3883 26 3895 -34 3903 -161C3905 -175 3906 -202 3906 -202H3626C3630 -223 3632 -246 3634 -269H3938V-367H3734C3730 -394 3719 -431 3707 -460ZM3155 -850V-663H3038V-552H3147C3122 -431 3072 -290 3017 -212C3035 -180 3060 -125 3070 -91C3102 -142 3131 -216 3155 -297V89H3256V-366C3273 -326 3289 -286 3298 -258L3363 -339C3348 -368 3280 -485 3256 -520V-552H3350V-663H3256V-850Z",24.0,-858.0,3933.0,952.0],"en":["M91 0H224V-309C224 -380 212 -482 205 -552H209L268 -378L383 -67H468L582 -378L642 -552H647C639 -482 628 -380 628 -309V0H763V-741H599L475 -393C460 -348 447 -299 431 -252H426C411 -299 397 -348 381 -393L255 -741H91Z M1166 14C1306 14 1435 -94 1435 -280C1435 -466 1306 -574 1166 -574C1025 -574 897 -466 897 -280C897 -94 1025 14 1166 14ZM1166 -106C1089 -106 1047 -174 1047 -280C1047 -385 1089 -454 1166 -454C1242 -454 1285 -385 1285 -280C1285 -174 1242 -106 1166 -106Z M1718 14C1863 14 1941 -64 1941 -163C1941 -266 1859 -304 1785 -332C1725 -354 1674 -369 1674 -410C1674 -442 1698 -464 1749 -464C1790 -464 1829 -444 1869 -416L1935 -505C1889 -541 1826 -574 1745 -574C1617 -574 1536 -503 1536 -403C1536 -309 1615 -266 1686 -239C1745 -216 1803 -197 1803 -155C1803 -120 1778 -96 1722 -96C1669 -96 1622 -119 1572 -157L1505 -64C1561 -18 1643 14 1718 14Z M2258 14C2307 14 2346 2 2377 -7L2352 -114C2337 -108 2315 -102 2297 -102C2247 -102 2220 -132 2220 -196V-444H2359V-560H2220V-711H2099L2082 -560L1995 -553V-444H2074V-195C2074 -71 2125 14 2258 14Z  M2783 0H2964L3045 -367C3056 -424 3067 -481 3078 -537H3082C3090 -481 3101 -424 3113 -367L3196 0H3380L3517 -741H3377L3318 -379C3307 -302 3296 -223 3285 -143H3280C3264 -223 3250 -303 3233 -379L3147 -741H3020L2935 -379C2919 -302 2903 -223 2888 -143H2884C2873 -223 2861 -301 2849 -379L2792 -741H2641Z M3616 0H3763V-560H3616ZM3690 -651C3740 -651 3775 -682 3775 -731C3775 -779 3740 -811 3690 -811C3638 -811 3605 -779 3605 -731C3605 -682 3638 -651 3690 -651Z M3920 0H4067V-385C4108 -426 4138 -448 4183 -448C4238 -448 4262 -418 4262 -331V0H4409V-349C4409 -490 4357 -574 4236 -574C4160 -574 4103 -534 4054 -486H4051L4040 -560H3920Z M4721 14C4866 14 4944 -64 4944 -163C4944 -266 4862 -304 4788 -332C4728 -354 4677 -369 4677 -410C4677 -442 4701 -464 4752 -464C4793 -464 4832 -444 4872 -416L4938 -505C4892 -541 4829 -574 4748 -574C4620 -574 4539 -503 4539 -403C4539 -309 4618 -266 4689 -239C4748 -216 4806 -197 4806 -155C4806 -120 4781 -96 4725 -96C4672 -96 4625 -119 4575 -157L4508 -64C4564 -18 4646 14 4721 14Z",91.0,-811.0,4853.0,825.0]}/*/LABELS*/;
  function svgWords(lang, color, px) {      // the words as their outline (tools/mklabels.py): the svg box is the ink's box
    var L = LABELS[lang] || LABELS.hans, k = px / 1000, P = 60;      // an even margin round the ink (em/1000): the edges' smoothing is not clipped, the centre stays put
    return '<svg width="' + ((L[3] + 2 * P) * k).toFixed(2) + '" height="' + ((L[4] + 2 * P) * k).toFixed(2) + '" viewBox="' + (L[1] - P) + ' ' + (L[2] - P) + ' ' + (L[3] + 2 * P) + ' ' + (L[4] + 2 * P) + '" style="display:block;overflow:visible"><path fill="' + color + '" d="' + L[0] + '"/></svg>';
  }
  function capLabel() { btn.innerHTML = '<span class="ic"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M8.5 20h7M10 17h4"/></svg></span><span class="tx" aria-label="' + esc(t('title')) + '">' + svgWords(lang(), '#333', 13) + '</span><span class="ar"><svg width="8" height="12" viewBox="0 0 8 12" fill="none" stroke="#FF2442" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 2l4 4-4 4"/></svg></span>'; }      // a drawn chevron: a text \u203a sits on the font\'s baseline, not in the middle
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
  // the language button: Xiaohongshu's translate mark in a black see-through circle, two white rounded squares overlapping corner to corner,
  // 文 on the upper left one, A on the lower right one, drawn as strokes (centred whatever font the phone has) in see-through black;
  // a cut-out gap keeps the squares apart
  var lb = document.getElementById('lang');
  if (lb) lb.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24"><defs><mask id="xlm"><rect width="24" height="24" fill="#fff"/><rect x="9.8" y="9.8" width="14.2" height="14.2" rx="3.6" fill="#000"/></mask></defs>' +
    '<rect x="1" y="1" width="12" height="12" rx="2.8" fill="#fff" mask="url(#xlm)"/><g fill="none" stroke="rgba(0,0,0,.55)" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3.5v1M3.9 5.2h6.2M9.2 5.5Q8.2 8.8 4 10.5M4.9 5.5Q6.2 8.8 10.2 10.5"/></g>' +
    '<rect x="11" y="11" width="12" height="12" rx="2.8" fill="#fff"/><g fill="none" stroke="rgba(0,0,0,.55)" stroke-width="1.05" stroke-linecap="round" stroke-linejoin="round"><path d="M14.3 20.2L17 13.8l2.7 6.4M15.35 18.1h3.3"/></g></svg>';      // the gap between the squares is cut out (a mask): the circle shows through it
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
    // loading: skeleton rows the size of the real ones, so the board opens at its full height and does not jump when the data comes
    var sk = '', W = [62, 48, 70, 54, 44, 66, 58, 50, 68, 46, 60, 52];
    for (var k = 0; k < W.length; k++) sk += '<div class="row sk"><span class="rk"><i></i></span><span class="nm"><i style="width:' + W[k] + '%"></i></span><span class="sc"><i></i></span></div>';
    list.innerHTML = sk; list.scrollTop = 0; foot.innerHTML = '<div class="row sk me"><span class="rk"><i></i></span><span class="nm"><i style="width:30%"></i></span><span class="sc"><i></i></span></div>';
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
  // shown first, so the words are drawn to the capsule's real height
  function show(v) { btn.classList.toggle('on', v); if (v && lastLang !== lang()) { lastLang = lang(); capLabel(); } }
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
