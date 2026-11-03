// ---- Game Center, in the app only: wins are counted on the device and reported through the native shell; on the web gcPost does nothing
const GCK = 'pocket_gc'; let GCS = { wins: 0, streak: 0, best: 0, ach: {} }; try { GCS = Object.assign(GCS, JSON.parse(localStorage.getItem(GCK) || '{}')); } catch (e) {}
// achievements that no longer exist (role first wins, two earlier role tricks) are dropped, so they are never sent again
const GCA = ['first_win', 'wins_100', 'wins_300', 'wins_1000', 'day_7', 'exec_survive', 'drink_alone', 'self_reverse', 'all_tokens', 'trick_pukka', 'self_poison'];
for (const id of Object.keys(GCS.ach || {})) if (!GCA.includes(id)) delete GCS.ach[id];
function gcPost(m) { try { window.webkit.messageHandlers.gc.postMessage(m); } catch (e) {} if (typeof window.__miniGC === 'function') window.__miniGC(m); }      // the Xiaohongshu build listens here for its leaderboard
function gcAch(id) { GCS.ach[id] = 1; try { localStorage.setItem(GCK, JSON.stringify(GCS)); } catch (e) {} gcPost({ t: 'ach', id: 'pc.' + id }); }
function gcRecord(won, role) {
  if (!won) { GCS.streak = 0; try { localStorage.setItem(GCK, JSON.stringify(GCS)); } catch (e) {} return; }
  GCS.wins++; GCS.streak++; GCS.best = Math.max(GCS.best, GCS.streak); gcAch('first_win'); window.__wonThisSession = true;
  for (const n of [100, 300, 1000]) if (GCS.wins >= n) gcAch('wins_' + n);
  gcPost({ t: 'score', v: GCS.wins });      // the leaderboard ranks total wins
}
window.__gcSync = () => { for (const id of Object.keys(GCS.ach)) gcPost({ t: 'ach', id: 'pc.' + id }); if (GCS.wins) gcPost({ t: 'score', v: GCS.wins }); };      // once signed in: anything earned before sign-in goes up too
// The app's leaderboard capsule: in the Tiny Clocktower app only (the web has none; the Xiaohongshu build has its own),
// top middle of the lobby once the player has won in this session. In Apple's manner: dark frosted glass, the system font in white,
// a filled trophy in system orange and a white chevron. A tap opens Game Center's own Most Wins board (native, see AppDelegate).
(function () {
  const inApp = !!(window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.gc);
  if (!inApp) return;
  const T = { hans: '总胜场榜', hant: '總勝場榜', en: 'Most Wins' };
  const make = () => {
    const st = document.createElement('style');
    st.textContent = '#gccap{position:fixed;left:50%;top:calc(10px + env(safe-area-inset-top));transform:translateX(-50%);z-index:20;display:none;align-items:center;height:36px;padding:0 12.25px 0 11px;border-radius:18px;border:.5px solid rgba(255,255,255,.22);background:rgba(28,22,34,.32);-webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);box-shadow:0 4px 18px rgba(0,0,0,.12);font:600 15px -apple-system,BlinkMacSystemFont,"SF Pro Text","PingFang SC",system-ui,sans-serif;letter-spacing:-.01em;color:#fff;white-space:nowrap;-webkit-tap-highlight-color:transparent;transition:opacity .15s}' +
      '#gccap.on{display:flex}#gccap:active{opacity:.55}#gccap svg{display:block}#gccap .ic{margin-right:7px}#gccap .ch{margin-left:6px}' +
      '#gccap .tx{display:inline-block;transform:translateY(-.092em)}' +      // Chinese sits low in its line box: lifted by the measured amount
      // the language button: a white globe in a round button of the capsule's dark glass; its menu an iOS menu of glass with a blue tick
      '#lang{width:36px!important;height:36px!important;padding:0!important;display:flex;align-items:center;justify-content:center;border:.5px solid rgba(255,255,255,.22)!important;border-radius:18px!important;background:rgba(28,22,34,.32)!important;-webkit-backdrop-filter:saturate(180%) blur(20px)!important;backdrop-filter:saturate(180%) blur(20px)!important;box-shadow:0 4px 18px rgba(0,0,0,.12)!important;color:#fff!important}#lang[style*="block"]{display:flex!important}#lang:active{opacity:.55}' +
      '#langMenu{gap:0!important;padding:6px 0!important;min-width:180px;border-radius:14px!important;border:.5px solid rgba(255,255,255,.55)!important;background:rgba(246,246,248,.72)!important;-webkit-backdrop-filter:saturate(180%) blur(24px)!important;backdrop-filter:saturate(180%) blur(24px)!important;box-shadow:0 10px 36px rgba(0,0,0,.18)}' +
      '#langMenu button{position:relative;border-radius:0!important;padding:11px 44px 11px 18px!important;font:400 16px -apple-system,BlinkMacSystemFont,"SF Pro Text","PingFang SC",system-ui,sans-serif!important;letter-spacing:-.01em!important;color:rgba(0,0,0,.86)!important;background:transparent!important}' +
      '#langMenu button+button{border-top:.5px solid rgba(60,60,67,.18)}#langMenu button:active{background:rgba(0,0,0,.06)!important}' +
      '#langMenu button.on::after{content:"";position:absolute;right:18px;top:50%;width:6px;height:11px;margin-top:-7px;border:solid #007AFF;border-width:0 2.2px 2.2px 0;transform:rotate(45deg)}';
    document.head.appendChild(st);
    // the language button: Apple's globe (as the SF Symbol globe) in white, in the same dark glass as the Most Wins capsule; the menu's tick is system blue
    const lb = document.getElementById('lang');
    if (lb) lb.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9.2"/><ellipse cx="12" cy="12" rx="4" ry="9.2"/><path d="M3.2 9h17.6M3.2 15h17.6"/></svg>';
    const b = document.createElement('button'); b.id = 'gccap'; b.setAttribute('aria-label', 'Game Center');
    const label = () => '<svg class="ic" width="18" height="18" viewBox="0 0 24 24"><path fill="#FF9500" d="M7 3h10v2h3.5a1 1 0 0 1 1 1c0 3.3-2.1 5.9-5 6.6A5.2 5.2 0 0 1 13 15.9V18h3a1 1 0 0 1 1 1v2H7v-2a1 1 0 0 1 1-1h3v-2.1a5.2 5.2 0 0 1-3.5-3.3c-2.9-.7-5-3.3-5-6.6a1 1 0 0 1 1-1H7zm0 4H4.6a5 5 0 0 0 2.6 3.6A7 7 0 0 1 7 9zm10 0v2a7 7 0 0 1-.2 1.6A5 5 0 0 0 19.4 7z"/></svg>' +
      '<span class="tx">' + (T[typeof LANG !== 'undefined' ? LANG : 'hans'] || T.hans) + '</span><svg class="ch" width="7" height="12" viewBox="0 0 7 12" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1.5 1.5L5.5 6l-4 4.5"/></svg>';
    let lastLang = '';
    b.addEventListener('click', e => { e.stopPropagation(); gcPost({ t: 'board' }); });
    document.body.appendChild(b);
    setInterval(() => {
      const on = !!window.__wonThisSession && !!window.__3bLang;
      if (on && lastLang !== LANG) { lastLang = LANG; b.innerHTML = label(); }
      b.classList.toggle('on', on);
    }, 300);
  };
  if (document.body) make(); else document.addEventListener('DOMContentLoaded', make);
})();
// The clock tower's three-player game (水手 / 普卡 / 异端分子), taken out of the main game: only /3b uses it.
// tools/mk3b.py puts this file into deploy/3b.html as a script of its own, after the main game's script (roleToken, sounds, drawing helpers and STR come from there).

// ------------------------------------------------------------ inside the clocktower: a three-player game
// Sailor / Pukka / Heretic, one each. Rules follow the official ability texts:
//   Sailor (Townsfolk): each night choose an alive player: either you or they are drunk until dusk. You can't die.
//   Pukka (Demon): each night choose a player: they are poisoned. The previously poisoned player dies then becomes healthy.
//   Heretic (Outsider): whoever wins, loses & whoever loses, wins, even if you are dead.
const RN = { sailor: '水手', pukka: '普卡', heretic: '异端分子' };
const ABIL = {
  sailor: '每个夜晚，你要选一名存活的玩家：你和他之中，有一人会醉酒到下个黄昏。只要你清醒，你就不会死。',
  pukka: '你是恶魔。每个夜晚，你要选一名玩家：他中毒。上一个因你中毒的人会在这时死去，然后恢复健康。',
  heretic: '只要你没有醉酒或中毒，这一局赢的算输、输的算赢——哪怕你已经死了。',
};
const stN = i => i === 0 ? '你' : i === 1 ? '左边那位' : '右边那位', npcN = (v, i) => i === v ? '我' : i === 0 ? '你' : '他', BLOOK = [{ kind: 'chef', apron: [220, 80, 80] }, { kind: 'ida', hat: [90, 150, 230] }, { kind: 'ida', hat: [240, 190, 110] }];
const BG = { run: 0, auto: false, roles: [], alive: [], drunk: -1, poisoned: -1, night: 0, dark: 0, isNight: false, bubble: null, wait: null, votes: null, reveal: false, over: false, result: null };
const BHIT = {};
function bsay(who, txt) { return new Promise(res => { if (BG.auto) return res(); BG.bubble = { who, text: txt }; BG.wait = { type: 'say', res }; }); }
function bpick(ok, txt, blank) { return new Promise(res => { if (BG.auto) { const c = [0, 1, 2, 'st'].filter(ok); if (blank !== undefined) c.push(blank); return res(pick(c)); } BG.bubble = { who: 'st', text: txt }; BG.wait = { type: 'pick', ok, res, blank }; }); }
function botcTap(x, y) {
  const w = BG.wait; if (!w) return;
  if (w.type === 'say') { BG.wait = null; chime(pick([69, 74, 76]), 0, .07, .6); w.res(); return; }
  let best = null, bd = 1e9; for (const k of [0, 1, 2, 'st']) { const h = BHIT[k]; if (!h) continue; const d = Math.hypot(x - h[0], y - h[1]) / h[2]; if (d < 1.2 && d < bd) { bd = d; best = k; } }
  if (best == null || !w.ok(best)) { if (w.blank !== undefined) { BG.wait = null; chime(57, 0, .1, .8); w.res(w.blank); } else if (best != null) chime(45, 0, .1, .3); return; }
  BG.wait = null; chime(best === 'st' ? 62 : 74, 0, .16, 1.2); if (best !== 'st') BG.pop = { who: best, t: 0 }; w.res(best);
}
async function playBotc() {
  const g = BG, run = ++g.run, ST = 'st', live = () => g.alive.filter(Boolean).length;
  const roles = ['sailor', 'pukka', 'heretic']; for (let i = 2; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0; [roles[i], roles[j]] = [roles[j], roles[i]]; }
  Object.assign(g, { snaps: [], roles, alive: [true, true, true], drunk: -1, poisoned: -1, night: 0, forceGood: false, isNight: false, votes: null, reveal: false, revealT: 0, showMine: false, deathBy: [null, null, null], gonePoison: -1, goneDrunk: -1, deadPoison: -1, over: false, result: null, log: [] });
  const si = roles.indexOf('sailor'), pi = roles.indexOf('pukka'), hi = roles.indexOf('heretic');
  // the Pukka's poison only works while the Pukka is sober. A player the Pukka kills is still poisoned at the time of death
  // (deadPoison), so their ability stays off: a Heretic killed this way does not flip the result.
  const poisonedNow = i => (g.poisoned === i || g.deadPoison === i) && g.alive[pi] && g.drunk !== pi;
  const sailorSafe = () => g.drunk !== si && !poisonedNow(si);
  const win = () => !g.alive[pi] ? 'good' : live() <= 2 ? 'evil' : null;
  // a dead character's tokens leave play: the Pukka's single poison token, the Sailor's drunk token
  const clean = () => { if (!g.alive[pi] && g.poisoned >= 0) { if (g.drunk !== pi) g.gonePoison = g.poisoned; /* a Pukka who dies drunk leaves no token behind: his tokens were already off the table */ g.poisoned = -1; } if (!g.alive[si] && g.drunk >= 0) { g.goneDrunk = g.drunk; g.drunk = -1; } };
  const recap = [], nm = i => stN(i) + '（' + RN[roles[i]] + '）'; g.recap = recap;
  const claim = [null, null, null], lastPick = [null, null, null], bluff = Math.random() < .5 ? 'sailor' : 'heretic';
  await bsay(ST, S().welcome);
  g.showMine = true; if (!g.auto) { chime(74, 0, .16, 1.4); chime(81, .1, .14, 1.4); }

  let raw = null;
  while (run === g.run) {
    // ---- night
    g.night++; g.isNight = true; g.votes = null; g.drunk = -1; let died = -1, rec = '第 ' + g.night + ' 夜。'; const aud = { p0: g.poisoned, sailorPoisoned: g.alive[si] && poisonedNow(si) };
    await bsay(ST, S().night);
    if (g.alive[si]) {
      const works = !poisonedNow(si);
      const tgt = si === 0 ? await bpick(k => k !== ST && g.alive[k], S().pickSailor)
        : (Math.random() < .25 ? si : pick([0, 1, 2].filter(k => k !== si && g.alive[k])));
      lastPick[si] = tgt; if (si === 0 && tgt === 0 && (!g.auto || g.testBadges)) gcAch('drink_alone');      // 一人饮酒: the Sailor picks himself
      if (works) g.drunk = tgt === si ? si : (Math.random() < .5 ? tgt : si);
      rec += works ? nm(si) + '选了' + (tgt === si ? '自己' : nm(tgt)) + '，醉的是' + nm(g.drunk) + '。' : nm(si) + '中着毒，能力没有生效。';
      if (si === 0) await bsay(ST, S().ok);
    }
    if (g.alive[pi]) {
      const tgt = pi === 0 ? await bpick(k => k !== ST && g.alive[k], S().pickPukka)
        : pick([0, 1, 2].filter(k => k !== pi && g.alive[k]));      // a computer Pukka never poisons himself
      lastPick[pi] = tgt; if (pi === 0 && tgt === 0 && (!g.auto || g.testBadges)) gcAch('self_poison');      // 自毒: the Pukka poisons himself
      if (g.drunk !== pi && g.poisoned !== pi) {
        const prev = g.poisoned;
        // poisoning himself still lands, but a Pukka poisoned that night cannot make the last victim die
        if (tgt !== pi && prev >= 0 && g.alive[prev]) { g.alive[prev] = false; g.deathBy[prev] = 'night'; g.deadPoison = prev; died = prev; }
        g.poisoned = tgt; if (tgt === si) g.drunk = -1;
        rec += nm(pi) + '让' + (tgt === pi ? '自己' : nm(tgt)) + '中了毒' + (died >= 0 ? '；上一个中毒的' + nm(died) + '毒发身亡。' : tgt === pi && prev >= 0 && prev !== pi ? '；自己中了毒，上一个中毒的人没有毒发。' : '。'); clean();
        aud.self = tgt === pi; aud.prevAlive = prev >= 0 && prev !== pi;
      }
      else rec += nm(pi) + (g.drunk === pi ? '醉了' : '中着自己的毒') + '，没能下毒，也没有人毒发身亡。';
      if (pi === 0) await bsay(ST, S().ok);
    }

    recap.push(rec); g.snaps.push({ night: true, n: g.night, alive: g.alive.slice(), drunk: g.drunk, poisoned: g.poisoned }); aud.pukkaDrunk = g.alive[pi] && g.drunk === pi; aud.both = g.alive[si] && g.poisoned === si && g.drunk >= 0; aud.p1 = g.poisoned; aud.died = died; aud.drunk = g.drunk; (g.audit = g.audit || []).push(aud);
    // a death in the night ends a three-player game on the spot: the Storyteller announces it and the result while it is still night
    if (died >= 0) { await bsay(ST, S().nightDied(died)); raw = win() || 'evil'; break; }
    g.isNight = false;
    await bsay(ST, S().dawnQuiet);
    if ((raw = win())) break;
    if (g.night >= 7) { raw = 'good'; g.forceGood = true; break; }      // the seventh day dawns: good has outlasted evil and wins outright, whatever the Heretic
    // ---- day: the other two say who they are (the Pukka lies)
    for (const v of [1, 2]) if (g.alive[v]) {
      const r = roles[v] === 'pukka' ? bluff : roles[v]; claim[v] = r;
      const t = roles[v] === 'pukka' ? pick([0, 1, 2].filter(k => k !== v)) : lastPick[v];
      await bsay(v, r === 'sailor' ? S().sailorSay(v, t) : S().hereticSay);
    }
    const other = v => 3 - v, hereticOn = g.drunk !== hi && !poisonedNow(hi);
    const suspect = v => claim[other(v)] === roles[v] ? other(v) : (v + g.night) % 2 ? 0 : other(v);
    const wants = (v, nom) => roles[v] === 'sailor' ? nom === suspect(v) : roles[v] === 'heretic' ? nom !== suspect(v) : (hereticOn ? nom === v : nom !== v);
    // ---- nomination and vote
    // only you may nominate, and you must: tapping empty space does nothing until you pick a player
    let nom = await bpick(k => k !== ST && g.alive[k], S().nomPrompt); const nominator = 0;
    await bsay(0, S().myNom(nom));      // you say it out loud
    if (nom != null) {
      // the count goes round clockwise, starting with the player after the nominee and ending with the nominee;
      // each player's answer shows as it is given. Whoever nominated votes for it automatically, but still says so in turn.
      const votes = [null, null, null]; g.votes = votes; g.voteOrder = [];
      for (const v of [(nom + 1) % 3, (nom + 2) % 3, nom]) if (g.alive[v]) {
        g.voteOrder.push(v);
        if (v === nominator) votes[v] = true;
        else if (v === 0) votes[v] = (await bpick(k => k === nom, S().votePrompt, 'no')) === nom;
        else votes[v] = wants(v, nom);
        await bsay(v, v === 0 ? (votes[v] ? S().myVote : S().myNoVote) : (votes[v] ? S().iVote : S().iDont));
      }
      const yes = votes.filter(x => x === true).length, need = Math.ceil(live() / 2);
      const snap = { night: false, n: g.night, alive: g.alive.slice(), drunk: g.drunk, poisoned: g.poisoned }; g.snaps.push(snap);
      const head = '第 ' + g.night + ' 天。' + nm(nominator) + '提名' + (nom === nominator ? '自己' : nm(nom)) + '，' + yes + ' 票';
      if (yes >= need) {
        if (roles[nom] === 'sailor' && sailorSafe()) { if (nom === 0 && (!g.auto || g.testBadges)) gcAch('exec_survive');      /* 不死之身: you were executed and did not die */ recap.push(head + '通过，可清醒的水手死不了。'); await bsay(ST, S().voteSafe(yes, nom)); }
        else { g.alive[nom] = false; g.deathBy[nom] = 'exec'; snap.alive = g.alive.slice(); snap.exec = nom; recap.push(head + '通过，' + nm(nom) + '被处决。'); clean(); await bsay(ST, S().voteExec(yes, nom)); }
      } else { recap.push(head + '，不够 ' + need + ' 票，没有处决。'); await bsay(ST, S().voteFail(yes, need)); }
      g.votes = null;
      if ((raw = win())) break;
    } else { g.snaps.push({ night: false, n: g.night, alive: g.alive.slice(), drunk: g.drunk, poisoned: g.poisoned }); recap.push('第 ' + g.night + ' 天。没有人被提名。'); await bsay(ST, S().noNom); }
  }
  if (run !== g.run) return null;
  // ---- the end: apply the Heretic
  const hereticOn = !g.forceGood && g.drunk !== hi && !poisonedNow(hi), fin = hereticOn ? (raw === 'good' ? 'evil' : 'good') : raw, mine = roles[0] === 'pukka' ? 'evil' : 'good';
  g.reveal = true; g.revealT = 0; g.pukkaSober = g.alive[pi] && g.drunk !== pi; if (!g.auto) [62, 69, 74].forEach((m, k) => chime(m, k * .15, .16, 1.6));
  g.result = { raw, fin, hereticOn, nights: g.night, won: mine === fin };
  if (!g.auto || g.testBadges) {
    if (roles[0] === 'pukka' && mine === fin && g.alive[pi] && g.drunk !== pi && g.deadPoison >= 0 && g.poisoned >= 0 && g.deadPoison !== g.poisoned) gcAch('trick_pukka');      // won with the Pukka's mark on two different players
    if (roles[0] === 'heretic' && g.deathBy[0] === 'exec' && hereticOn) gcAch('self_reverse');      // 亲手逆转: executed, and your own reversal flipped the result
    const sailorMark = g.drunk === 0 || g.goneDrunk === 0, pukkaMark = ((g.poisoned === 0 || g.deadPoison === 0) && g.pukkaSober) || g.gonePoison === 0;
    if (roles[0] === 'heretic' && g.deathBy[0] === 'exec' && sailorMark && pukkaMark) gcAch('all_tokens');      // 魅魔体质: executed, and the reveal shows both the others' reminders on you
  }
  g.recapLine = recap.map(r => r.replace(/第 (\d+) (夜|天)。/, '第$1$2，').replace(/。$/, '').replace(/。/g, '，')).join('；') + '。';
  if (!g.auto && g.forceGood && mine === 'good') gcAch('day_7');      // 漫长的一周: the game ran to the seventh day and you, on the good side, won the forced settlement
  if (!g.auto) gcRecord(mine === fin, roles[0]);
  g.over = true; if (!g.auto) resultMusic(mine === fin);
  await bsay(ST, g.forceGood ? S().goodForced : fin === 'good' ? S().goodWins : S().evilWins);
  await new Promise(res => { if (g.auto) return res(); g.bubble = null; g.wait = { type: 'say', res }; });
  if (!g.auto && run === g.run && mode === 'tower') leaveTower();
  return g.result;
}

// the shroud that hangs over a dead player's token
function shroud(x, y, r, a = 1) { const w = r * .42, t0 = y - r * 1.3, t1 = y + r * .05; poly([[x - w, t0], [x + w, t0], [x + w, t1], [x, t1 - r * .28], [x - w, t1]], [28, 22, 40], .93 * a); poly([[x - w, t0], [x + w, t0], [x + w, t0 + r * .16], [x - w, t0 + r * .16]], [80, 70, 100], a); }
// small reminder token: 醉 / 毒
function reminder(x, y, r, ch, c, a = 1) { glow(x, y, r * 1.8, c, .5 * a); circ(x, y, r, [40, 30, 64], a); circ(x, y, r * .84, c, a); text(ch, x, y + .5, r * 1.15, [255, 255, 255], a, 'center', true); }
// the tune when the result is announced: bright if you won, wistful if you lost
function resultMusic(won) {
  if (!AC) return;
  if (won) { [62, 66, 69, 74, 78, 81, 86, 90].forEach((m, k) => chime(m, k * .11, .2, 2.2)); pad([50, 57, 62, 66, 69, 74], AC.currentTime + .1, 6); [74, 78, 81].forEach(m => chime(m, 1.1, .16, 3)); bell(293.6, .14); }
  else { [69, 65, 62, 60, 57, 53, 50].forEach((m, k) => chime(m, k * .42, .18, 2.8)); pad([38, 45, 53, 57, 60], AC.currentTime + .1, 7); setTimeout(() => bell(73.4, .2), 2600); }
}

// ---- what follows down to the library is the old three-player table game: nothing leads to it any more
let fadeCv = null;
function fadedDraw(a, fn) {      // draw something made of overlapping pieces at less than full opacity without its pieces showing through one another: drawn whole onto a canvas of its own, then laid over the picture at opacity a
  if (a <= 0) return; if (a >= 1) { ctx.save(); try { fn(); } finally { ctx.restore(); } return; }      // whatever fn changes (opacity, blend) stays inside it
  const real = ctx, oc = fadeCv || (fadeCv = document.createElement('canvas')); if (oc.width !== cv.width || oc.height !== cv.height) { oc.width = cv.width; oc.height = cv.height; }
  ctx = oc.getContext('2d'); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, oc.width, oc.height); ctx.setTransform(DPR, 0, 0, DPR, 0, 0); ctx.globalAlpha = 1;
  ctx.save(); try { fn(); } finally { ctx.restore(); ctx = real; }
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha *= a; ctx.drawImage(oc, 0, 0); ctx.restore(); }
function drawGeese3(t, n) {      // three geese crossing the sky, exactly as over the town in the main game: white by day, a soft grey by night (n: how far into the night)
  for (let i = 0; i < 3; i++) { const x = ((t * 26 + i * 170) % (W + 200)) - 100, y = H * 0.2 + i * 26 + 10 * Math.sin(t * .9 + i), f = 6 * Math.sin(t * 7 + i * 1.7); line([[x - 10, y - f], [x, y], [x + 10, y - f]], mix([255, 255, 255], [200, 190, 220], n), 2, lerp(.95, .7, n)); } }
// the player, a boy with soft full hair, dark top, blue shorts and white sneakers: walks the four diagonals in small quick steps, the back foot flicking up, the body nearly still. ph: the step (null: standing); flip: 1 right, -1 left; away: going up the screen
function drawHero(x, y, k, ph, flip = 1, away = true) {
  const R = [214, 62, 70], RD = [168, 44, 66], SK = [242, 210, 182], SH = [246, 242, 238], D = [246, 242, 238], BL = [40, 36, 46], tone = c => [mix(c, [255, 255, 255], .12), mix(c, [70, 50, 110], .26)], P = poly;
  ctx.save(); ctx.translate(x, y); ctx.scale(flip, 1); ctx.translate(-x, -y); const by = y - (ph == null ? 0 : Math.abs(Math.cos(ph)) * .01 * k), sl = away ? -.5 : .5, tilt = away ? -1 : 1; if (!figNoShadow) ell(x, y, .2 * k, .06 * k, [20, 12, 40], .3);
  const leg = (off, back) => { const hipx = x + (back ? -.035 : .035) * k, hipy = by - .3 * k; let st, up = 0, kx, ky = hipy + .13 * k;
    if (ph == null) { st = back ? -.04 : .04; kx = (hipx + x + st * k) / 2; }
    else { const q = ((ph + off) / TAU % 1 + 1) % 1; if (q < .5) { st = .12 - .48 * q; kx = (hipx + x + st * k) / 2 + .012 * k; } else { const u = (q - .5) / .5, e = Math.sin(u * Math.PI); st = -.12 + .24 * u - .07 * e * (1 - u); up = .08 * e * (1 - u * .55); kx = hipx + (.02 + .045 * e) * k; } }
    const fx = x + st * k, fy = y + st * sl * k - up * k; ctx.strokeStyle = css(back ? mix(SK, [70, 50, 110], .06) : SK); ctx.lineWidth = .062 * k; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.beginPath(); ctx.moveTo(hipx, hipy); ctx.lineTo(kx, ky); ctx.lineTo(fx, fy - .04 * k); ctx.stroke();
    P([[fx - .04 * k, fy - .068 * k], [fx + .03 * k, fy + (-.068 + tilt * .012) * k], [fx + .105 * k, fy + (-.03 + tilt * .02) * k], [fx + .105 * k, fy + (.012 + tilt * .02) * k], [fx - .04 * k, fy + .012 * k]], SH); };
  if (away) { leg(0, false); leg(Math.PI, true); } else { leg(Math.PI, true); leg(0, false); }
  const [pa, pb] = tone(BL), [a, b] = tone(D); P([[x - .15 * k, by - .46 * k], [x, by - .46 * k], [x, by - .29 * k], [x - .17 * k, by - .29 * k]], pa); P([[x, by - .46 * k], [x + .15 * k, by - .46 * k], [x + .17 * k, by - .29 * k], [x, by - .29 * k]], pb);
  P([[x - .1 * k, by - .86 * k], [x, by - .86 * k], [x, by - .42 * k], [x - .19 * k, by - .42 * k]], a); P([[x, by - .86 * k], [x + .1 * k, by - .86 * k], [x + .19 * k, by - .42 * k], [x, by - .42 * k]], b);
  const hx = x, hy = by - 1.03 * k, r = .17 * k;
  const shape = (pts, c) => { ctx.beginPath(); ctx.moveTo(hx + pts[0] * r, hy + pts[1] * r); for (let n = 2; n < pts.length; n += 4) ctx.quadraticCurveTo(hx + pts[n] * r, hy + pts[n + 1] * r, hx + pts[n + 2] * r, hy + pts[n + 3] * r); ctx.closePath(); ctx.fillStyle = css(c); ctx.fill(); };      
  circ(hx, hy, r, SK); for (const m of [-1, 1]) { const pts = [.04, -1.42, -.7, -1.5, -1.08, -.92, -1.26, -.5, -1.2, 0, -1.2, .24, -1.06, .42, -.94, .24, -.8, 0, -.66, .2, -.46, .26, -.34, .08, -.28, -.04, -.14, .14, .04, .18]; shape(pts.map((v, n) => n % 2 ? v : v * m), [28, 26, 34]); }      // the same black hair whichever way he walks: symmetrical, lying close to the head, a few soft locks over the forehead
  ctx.beginPath(); ctx.arc(hx, hy - r * .16, r * 1.36, Math.PI * .98, Math.PI * 2.02); ctx.closePath(); ctx.fillStyle = css(R); ctx.fill(); P([[hx - r * 1.24, hy - r * .22], [hx - r * 2.1, hy - r * .02], [hx - r * 2.06, hy - r * .18], [hx - r * 1.2, hy - r * .46]], RD); circ(hx - r * .03, hy - r * 1.52, r * .13, RD);      // a red cap over the hair, the peak turned backwards
  ctx.restore();
}
function drawBotc(t, dt) {
  const g = BG; g.dark = lerp(g.dark, g.isNight ? 1 : 0, 1 - Math.pow(0.002, dt));
  TINT = [30, 30, 90]; TK = lerp(0.04, 0.34, g.dark); SHADOW = [58, 40, 96];
  moonAt = [W * .8, H * .14]; drawSky(mix(SKYD[0], SKYN[0], g.dark), mix(SKYD[1], SKYN[1], g.dark), mix(SKYD[2], SKYN[2], g.dark), t, .1 + .9 * g.dark); moonAt = null;
  const mx = W * .8, my = H * .14, sc = mix(ORBD, ORBN, g.dark); glow(mx, my, 130, sc, lerp(.45, .1, g.dark)); drawOrb(mx, my, 22, g.dark); drawGeese3(t, g.dark);
  const s = Math.min(W / 11.2, (H - 250) / 8.6), v = new View(W / 2, H * .6, s), P = v.P.bind(v);
  const top = [92, 168, 162], under = [70, 96, 130];
  v.disc(0, 0, -3.6, 1.1, 1.1, under); v.disc(0, 0, -2.5, 2.3, .9, under); v.disc(0, 0, -1.6, 3.4, 1.0, mix(under, top, .3)); v.disc(0, 0, -.6, 4.3, .6, top); v.disc(0, 0, 0, 2.3, 0, [120, 190, 180]);
  for (let i = 0; i < 12; i++) { const q = TAU * i / 12; line([P(3.95 * Math.cos(q), 3.95 * Math.sin(q)), P(4.18 * Math.cos(q), 4.18 * Math.sin(q))], tint(mix(top, [255, 255, 255], .6)), s * .07); }
  const K = s * 1.25, seat = i => { const q = (45 + 120 * i) * Math.PI / 180; return [3.0 * Math.cos(q), 3.0 * Math.sin(q)]; };
  const w = g.wait, canPick = k => w && w.type === 'pick' && w.ok(k), pulse = .5 + .5 * Math.sin(t * 5);
  const items = [0, 1, 2].map(i => ({ k: seat(i)[0] + seat(i)[1], i })); items.push({ k: 0, i: 'st' }); const toks = [];
  if (g.reveal) g.revealT += dt;
  for (const k of [0, 1, 2, 'st']) delete BHIT[k];
  items.sort((a, b) => a.k - b.k).forEach(({ i }) => {
    if (i === 'st') {
      v.disc(0, 0, 0, .95, .3, [240, 220, 190]); const p = P(0, 0, .3);
      if (canPick('st')) { ctx.beginPath(); ctx.ellipse(p[0], p[1], s * .9, s * .45, 0, 0, TAU); ctx.strokeStyle = css([255, 236, 170], .5 + .4 * pulse); ctx.lineWidth = 2.5; ctx.stroke(); }
      glow(p[0], p[1] - K * .8, K * 1.4, [200, 170, 255], .3 + .3 * g.dark); fig(p[0], p[1], K * 1.2, { kind: 'teller', body: [132, 100, 172], hat: [70, 52, 100] });
      BHIT.st = [p[0], p[1] - K * .8, K * .95];
      return;
    }
    const [x, y] = seat(i), p = P(x, y), dead = !g.alive[i], asleep = g.dark > .5 && !g.reveal && !(i === 0 && w && w.type === 'pick');
    if (canPick(i)) { ctx.beginPath(); ctx.ellipse(p[0], p[1], s * .7 * (1 + .06 * pulse), s * .35 * (1 + .06 * pulse), 0, 0, TAU); ctx.strokeStyle = css([255, 236, 170], .5 + .4 * pulse); ctx.lineWidth = 2.5; ctx.stroke(); }
    if (g.pop && g.pop.who === i) { const u = g.pop.t / .45, k2 = 1 + .55 * eout(u); ctx.beginPath(); ctx.ellipse(p[0], p[1], s * .7 * k2, s * .35 * k2, 0, 0, TAU); ctx.strokeStyle = css([255, 236, 170], .95 * (1 - u) * (1 - u)); ctx.lineWidth = 3.5 * (1 - u * .6); ctx.stroke(); g.pop.t += dt; if (g.pop.t >= .45) g.pop = null; }
    if (i === 0) glow(p[0], p[1] - K * .6, K * 1.2, [255, 240, 200], .3);
    const look = dead ? { kind: 'bare', body: [236, 236, 255], head: [236, 236, 255], a: .45 } : Object.assign({}, BLOOK[i], asleep ? { a: .55 } : {});
    fadedDraw(look.a == null ? 1 : look.a, () => fig(p[0], p[1], K, Object.assign({}, look, { a: 1 })));      // asleep or dead: faded as a whole, so the hat never shows the head through it
    if (dead) { ctx.beginPath(); ctx.ellipse(p[0], p[1] - K * 1.33, K * .2, K * .06, 0, 0, TAU); ctx.strokeStyle = css([255, 250, 220], .8); ctx.lineWidth = 2; ctx.stroke(); }
    if (g.votes && g.votes[i] != null) { const vx = p[0] + K * .62, vy = p[1] - K * 1.1; if (g.votes[i]) { glow(vx, vy, 24, [255, 214, 110], .7); poly([[vx, vy - 13], [vx + 9, vy], [vx, vy + 13], [vx - 9, vy]], [255, 214, 110]); } else line([[vx - 7, vy], [vx + 7, vy]], [200, 190, 220], 3, .8); }
    toks.push(i);
    BHIT[i] = [p[0], p[1] - K * .8, K * .8];
  });
  if (g.dark > .02) { ctx.fillStyle = css([10, 10, 40], .3 * g.dark); ctx.fillRect(0, 0, W, H); drawOrb(mx, my, 22, g.dark); }      // the night falls over everything but the moon
  // tokens over heads: your own role all game long; at the end everyone's role, shrouds for the dead, and 醉 / 毒 reminders
  const R = clamp(s * .62, 17, 30);
  for (const i of toks) {
    const [x, y] = seat(i), p = P(x, y), tx = p[0], ty = p[1] - K * 1.72 - R - 4 + 3 * Math.sin(t * 2 + i);
    if (g.reveal) {
      const pp = pop((g.revealT - i * .25) / .45); if (pp <= 0) continue;
      roleToken(tx, ty, R * pp, g.roles[i]);
      if (!g.alive[i]) shroud(tx, ty, R * pp, clamp((g.revealT - 1.0 - i * .2) / .4));
      const ra = clamp((g.revealT - 1.5) / .4), mr = R * .56, my = ty + R * .65; let k = 0, mp = () => [tx + R * 1.2 + k++ * R * 1.2, my];      // reminders: lower right, each further one beside the last
      if (g.drunk === i) roleToken(...mp(), mr, 'sailor', ra);
      // one Pukka token for the poison that killed them, one for tonight's poison: the same player can carry both
      if (g.deadPoison === i && g.pukkaSober) roleToken(...mp(), mr, 'pukka', ra);
      if (g.poisoned === i && g.pukkaSober) roleToken(...mp(), mr, 'pukka', ra);
      if (g.goneDrunk === i) { const [gx, gy] = mp(); roleToken(gx, gy, mr, 'sailor', ra); shroud(gx, gy, mr, ra); }
      if (g.gonePoison === i) { const [gx, gy] = mp(); roleToken(gx, gy, mr, 'pukka', ra); shroud(gx, gy, mr, ra); }
    } else if (i === 0 && g.showMine) roleToken(tx, ty, R, g.roles[0]);
  }
  // what is being said
  const b = g.bubble;
  if (b && BHIT[b.who]) {
    // a speech bubble right beside whoever is talking
    const h = BHIT[b.who], fs = clamp(W * .04, 13.5, 17), maxw = Math.min(W - 60, 300); ctx.font = FONT(fs, true);
    const lines = wrapText(b.text, maxw);
    const lh = fs * 1.45, cw = Math.max(...lines.map(l => ctx.measureText(l).width)) + 26, bh = lines.length * lh + 16;
    const top = b.who === 'st' ? h[1] - K * 1.12 : h[1] - K * .95, bx = clamp(h[0] - cw / 2, 8, W - cw - 8), by = top - bh - 9;
    ctx.fillStyle = css([250, 246, 238], .97); rrect(bx, by, cw, bh, 13); ctx.fill();
    poly([[h[0] - 7, by + bh - 1], [h[0] + 7, by + bh - 1], [h[0], by + bh + 9]], [250, 246, 238], .97);
    lines.forEach((l, k) => text(l, bx + cw / 2, by + 8 + lh * (k + .5), fs, [50, 36, 70], 1, 'center', true));
    if (w && w.type === 'say') text('▾', bx + cw - 11, by + bh - 9 + 2 * Math.sin(t * 5), 11, [150, 130, 170], .9);
  }
}

// tests for the three-player game: open deploy/3b.html with one of these hashes
if (location.hash) {
  if (location.hash === '#botc') setTimeout(async () => { BG.auto = true; const tally = {}; let drunkDeaths = 0, drunkDeathTokens = 0; const chk = () => { const g = BG, pi = g.roles.indexOf('pukka'); if (!g.alive[pi] && g.drunk === pi) { drunkDeaths++; if (g.gonePoison >= 0 || g.poisoned >= 0) drunkDeathTokens++; } }; let n = 0, maxN = 0, nightEnds = 0, killedHeretic = 0, killedHereticFlipped = 0, endedAtNight = 0; for (let k = 0; k < 400; k++) { const r = await playBotc(); n++; chk(); if (BG.deadPoison >= 0) { nightEnds++; if (BG.isNight) endedAtNight++; if (BG.roles[BG.deadPoison] === 'heretic') { killedHeretic++; if (r.hereticOn) killedHereticFlipped++; } } maxN = Math.max(maxN, r.nights); const key = BG.roles[0] + ':' + r.raw + '>' + r.fin + (r.hereticOn ? '(H)' : ''); tally[key] = (tally[key] || 0) + 1; } const A = BG.audit, pd = A.filter(a => a.pukkaDrunk), sp = A.filter(a => a.sailorPoisoned); document.title = 'pukkaDiedDrunk=' + drunkDeaths + ' tokensShown=' + drunkDeathTokens + ' ; nightKills=' + nightEnds + ' endedAtNight=' + endedAtNight + ' killedHeretic=' + killedHeretic + ' flippedAnyway=' + killedHereticFlipped + ' ; nights=' + A.length + ' pukkaDrunk=' + pd.length + ' bad=' + pd.filter(a => a.p1 !== a.p0 || a.died >= 0).length + ' sailorPoisoned=' + sp.length + ' bad=' + sp.filter(a => a.drunk !== -1).length + ' ; games=' + n + ' maxNights=' + maxN + ' selfPoisonNights=' + A.filter(a => a.self).length + ' diedOnSelfPoison=' + A.filter(a => a.self && a.died >= 0).length + ' sailorPoisonedWithDrunkToken=' + A.filter(a => a.both).length + ' ' + JSON.stringify(tally); }, 300);
  if (location.hash === '#botcorder') setTimeout(async () => { BG.auto = true; const log = []; let bad = 0, n = 0; for (let k = 0; k < 300; k++) { BG.voteOrder = null; await playBotc(); } document.title = 'ok'; }, 300);
  if (location.hash === '#botcnightend') setTimeout(async () => { mode = 'tower'; fade = 0; BG.auto = true; for (let k = 0; k < 400; k++) { const r = await playBotc(); if (BG.deadPoison >= 0 && (location.search.includes('her') ? BG.roles[BG.deadPoison] === 'heretic' : true) && (location.search.includes('twice') ? BG.poisoned === BG.deadPoison : true)) { BG.revealT = 5; BG.dark = 1; BG.bubble = { who: 'st', text: r.fin === 'good' ? S().goodWins : S().evilWins }; document.title = 'killed=' + BG.roles[BG.deadPoison] + ' raw=' + r.raw + ' fin=' + r.fin + ' hereticOn=' + r.hereticOn; break; } } }, 300);
  if (location.hash === '#stats') setTimeout(async () => { BG.auto = true; const N = 6000, c = {}; const inc = k => c[k] = (c[k] || 0) + 1;
    for (let k = 0; k < N; k++) { const r = await playBotc(), g = BG, pi = g.roles.indexOf('pukka'), hi = g.roles.indexOf('heretic'), si = g.roles.indexOf('sailor'), me = g.roles[0];
      const end = g.deadPoison >= 0 ? 'night:' + g.roles[g.deadPoison] : !g.alive[pi] ? 'exec:pukka' : 'exec:' + g.roles[g.alive.indexOf(false)];
      inc('end|' + end); inc('raw|' + r.raw); inc('fin|' + r.fin); inc('flip|' + (r.hereticOn ? 'yes' : g.deadPoison === hi ? 'no:killedPoisoned' : g.drunk === hi ? 'no:drunk' : 'no:poisoned')); inc('nights|' + r.nights);
      inc('path|' + end + ' > ' + (r.hereticOn ? 'flip' : 'noflip') + ' > ' + r.fin); inc('me|' + me + ':' + (r.won ? 'win' : 'lose')); inc('endNight' + r.nights + '|' + (g.deadPoison >= 0 ? 'night' : 'day')); }
    document.title = JSON.stringify({ N, c }); }, 300);
  if (location.hash === '#paths') setTimeout(async () => { BG.auto = true; const N = 20000, c = {}, R = { sailor: '水手', pukka: '普卡', heretic: '异端' };
    for (let k = 0; k < N; k++) { const r = await playBotc(), g = BG, pi = g.roles.indexOf('pukka'), rn = i => i < 0 || i == null ? '无' : R[g.roles[i]], sober = g.alive[pi] && g.drunk !== pi;
      const steps = g.snaps.map((sn, j) => sn.night ? '夜' + sn.n + '[醉:' + rn(sn.drunk) + ' 毒:' + rn(sn.poisoned) + (j === g.snaps.length - 1 && g.deadPoison >= 0 ? ' 死:' + rn(g.deadPoison) : '') + ']' : '日' + sn.n + '[' + (sn.exec != null ? '处决' + rn(sn.exec) : '无处决') + ']').join(' ');
      const toks = ['sailor', 'pukka', 'heretic'].map(role => { const i = g.roles.indexOf(role), t = []; if (!g.alive[i]) t.push('幕布'); if (g.drunk === i) t.push('醉'); if (sober && g.deadPoison === i) t.push('毒'); if (sober && g.poisoned === i) t.push('毒'); if (g.goneDrunk === i) t.push('醉(盖幕布)'); if (g.gonePoison === i) t.push('毒(盖幕布)'); return R[role] + ':' + (t.join('+') || '无'); }).join(' ');
      const key = steps + ' => ' + (r.hereticOn ? '颠倒' : '不颠倒') + ' => ' + (r.fin === 'good' ? '善良胜' : '邪恶胜') + ' || ' + toks; c[key] = (c[key] || 0) + 1; }
    const top = Object.entries(c).sort((a, b) => b[1] - a[1]); document.title = JSON.stringify({ N, kinds: top.length, top: top.slice(0, 16) }); }, 300);
}
