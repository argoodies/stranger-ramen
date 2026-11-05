// record the game frame by frame: each segment runs on the page's virtual clock, every frame's canvas is saved as a JPEG
import fs from 'node:fs';
const url = process.argv[2], out = process.argv[3], FPS = 30, dt = 1 / FPS;
const PLAN = [['stall', 11.4], ['town', 2.2], ['bar', 3.8], ['fight', 4.2], ['farewell', 3.2], ['rain', 2.2], ['title', 3.0]];
const t = await (await fetch('http://127.0.0.1:9333/json/new?' + encodeURIComponent(url), { method: 'PUT' })).json();
const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise(r => ws.addEventListener('open', r));
let id = 0; const send = (method, params) => new Promise(res => { const my = ++id; const h = m => { const d = JSON.parse(m.data); if (d.id === my) { ws.removeEventListener('message', h); res(d.result); } }; ws.addEventListener('message', h); ws.send(JSON.stringify({ id: my, method, params })); });
const ev = async e => { const r = await send('Runtime.evaluate', { expression: e, returnByValue: true }); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 300)); return r.result.value; };
const wait = ms => new Promise(r => setTimeout(r, ms));
for (let k = 0; k < 50 && !(await ev('!!window.__ready')); k++) await wait(200);
await ev(`document.fonts.load("200 30px 'PingFang SC'", '拉面怪奇物语').then(() => 1)`); await wait(800);
await wait(800);
let n = 0; fs.mkdirSync(out, { recursive: true });
for (const [seg, dur] of PLAN) {
  await ev(`__seg(${JSON.stringify(seg)})`); const F = Math.round(dur * FPS);
  for (let f = 0; f < F; f++) {
    const tt = f / FPS, inA = Math.max(0, 1 - tt / .45), outA = seg === 'rain' ? Math.max(0, (tt - (dur - .7)) / .65) : seg === 'title' ? 0 : Math.max(0, (tt - (dur - .3)) / .3);
    const black = seg === 'title' ? inA : Math.min(1, Math.max(inA, outA));
    const d = await ev(`__step(${dt}, ${black.toFixed(3)})`);
    fs.writeFileSync(`${out}/f${String(n++).padStart(4, '0')}.jpg`, Buffer.from(d.split(',')[1], 'base64'));
  }
  console.log(seg, 'served=', await ev('JSON.stringify(stall.seats.map(c => c && c.state + (c.ok ? ":ok" : "")))'), 'foes=', await ev('(church.foes || []).map(f => f.kind + ":" + (+f.app).toFixed(2)).join(",")'), 'fight=', await ev('church.fight'), 'frames so far', n, 'err=', await ev('document.getElementById("err").textContent'));
}
process.exit(0);
