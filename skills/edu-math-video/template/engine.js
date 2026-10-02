/* Notebook-style explainer engine. DO NOT put scene code here: scenes live in anim.js.
 * renderFrame(t) must be deterministic (same t -> same pixels): never use Math.random() or Date.now();
 * use hash(n) / noise1(x, seed) and the global NOW (current time in seconds).
 *
 * Canvas is 1920x1080. Subtitle box occupies y ≈ 914..1044, so scene content must stay above y = 860.
 */
const W = 1920, H = 1080;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const TL = window.TIMELINE;

const C = {
  ink: '#2d2a26', paper: '#fbf6ea', red: '#e2553f', blue: '#3b7dd8', yellow: '#eea21f',
  green: '#3c9a5a', purple: '#8a5cc2', gray: '#9a938a', pink: '#f08aa6', sand: '#d9a55a', land: '#f1e6cc',
};
const ZH = "'Kuaile','PingFang SC','Hiragino Sans GB',sans-serif";   // cute Chinese display font
const EN = "'PHand','Kuaile',sans-serif";                              // handwritten English font
const MF = "'PHand','Kuaile','PingFang SC',sans-serif";                // math / formulas on the board
const SUB = "'PingFang SC','Hiragino Sans GB','Heiti SC',sans-serif";  // subtitles
const PI = Math.PI, TAU = PI * 2;

// ---------------------------------------------------------------- math
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const eio = t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);   // ease in-out
const eout = t => 1 - Math.pow(1 - t, 3);                                       // ease out
const back = t => { t = clamp(t); const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); }; // overshoot pop
const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const noise1 = (x, seed) => {
  const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
  const a = hash(i + seed * 57.31), b = hash(i + 1 + seed * 57.31);
  return (a + (b - a) * u) * 2 - 1;
};
const mid = (p, q) => [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2];
const mix2 = (p, q, t) => [lerp(p[0], q[0], t), lerp(p[1], q[1], t)];
let BOIL = 0, NOW = 0;

// ---------------------------------------------------------------- stroke engine
function resample(pts, step = 5) {
  const out = [[pts[0][0], pts[0][1], 0]];
  let acc = 0;
  for (let i = 1; i < pts.length; i++) {
    const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
    const d = Math.hypot(x1 - x0, y1 - y0);
    if (d < 1e-6) continue;
    const n = Math.max(1, Math.ceil(d / step));
    for (let k = 1; k <= n; k++) { acc += d / n; out.push([x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n, acc]); }
  }
  return out;
}

/** Wobbly hand-drawn polyline. o: {p: draw-on progress 0..1, c: color, w: width, a: alpha, dash: [on,off],
 *  rough: wobble amplitude (default 1.7), seed, single: one pass only}. Returns tip {x,y,ang}. */
function draw(pts, o = {}) {
  const p = o.p === undefined ? 1 : clamp(o.p);
  if (p <= 0.001 || pts.length < 2) return null;
  const r = resample(pts, 5);
  const L = r[r.length - 1][2], lim = L * p;
  const amp = o.rough === undefined ? 1.7 : o.rough;
  const seed = (o.seed || 0) + BOIL * 13.7;
  const w = o.w || 4;
  ctx.save();
  ctx.strokeStyle = o.c || C.ink;
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  if (o.a !== undefined) ctx.globalAlpha *= o.a;
  if (o.dash) { ctx.setLineDash(o.dash); ctx.lineDashOffset = o.dashOff || 0; }
  let tip = null;
  const passes = o.single ? 1 : 2;
  for (let pass = 0; pass < passes; pass++) {
    const sd = seed + pass * 91.3;
    ctx.beginPath();
    let n = 0;
    for (let i = 0; i < r.length; i++) {
      let [x, y, s] = r[i];
      if (s > lim) break;
      const j = Math.min(i + 1, r.length - 1), k = Math.max(i - 1, 0);
      let nx = -(r[j][1] - r[k][1]), ny = r[j][0] - r[k][0];
      const nl = Math.hypot(nx, ny) || 1; nx /= nl; ny /= nl;
      const off = noise1(s / 45, sd) * amp + noise1(s / 9, sd + 3) * amp * 0.25 + (pass ? 1.2 : 0);
      x += nx * off; y += ny * off;
      if (n++ === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      if (pass === 0) tip = { i, x, y };
    }
    ctx.lineWidth = pass ? w * 0.55 : w;
    if (pass) ctx.globalAlpha *= 0.35;
    ctx.stroke();
  }
  ctx.restore();
  if (!tip) return null;
  const i0 = Math.max(0, tip.i - 3);
  const ang = Math.atan2(r[tip.i][1] - r[i0][1], r[tip.i][0] - r[i0][0]);
  return { x: tip.x, y: tip.y, ang };
}

function head(x, y, ang, o = {}) {
  const s = o.head || 20, spread = 0.5;
  draw([[x - Math.cos(ang - spread) * s, y - Math.sin(ang - spread) * s], [x, y], [x - Math.cos(ang + spread) * s, y - Math.sin(ang + spread) * s]],
    { c: o.c, w: o.w || 4, rough: 0.6, seed: 5, a: o.a });
}
/** polyline with an arrow head at the end (same options as draw + head: size) */
function arrow(pts, o = {}) {
  const e = draw(pts, o);
  if (e && (o.p === undefined || o.p > 0.02)) head(e.x, e.y, e.ang, o);
  return e;
}
const line = (x1, y1, x2, y2, o) => draw([[x1, y1], [x2, y2]], o);
function ellPts(cx, cy, rx, ry, a0 = 0, a1 = TAU, n = 72) {
  const o = [];
  for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; o.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]); }
  return o;
}
/** hand-drawn circle (slightly overshooting like a real pen) */
function circ(cx, cy, r, o = {}) {
  const a0 = o.start === undefined ? -2.1 : o.start;
  return draw(ellPts(cx, cy, r, r * (o.sq || 1), a0, a0 + TAU + (o.over === undefined ? 0.22 : o.over), 90), o);
}
function quadPts(x0, y0, cx, cy, x1, y1, n = 40) {
  const o = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, u = 1 - t;
    o.push([u * u * x0 + 2 * u * t * cx + t * t * x1, u * u * y0 + 2 * u * t * cy + t * t * y1]);
  }
  return o;
}
/** sample y = f(x) for x in [x0, x1] and map through toScreen([x, y]) -> [px, py] (for function graphs) */
function fnPts(f, x0, x1, toScreen, n = 120) {
  const o = [];
  for (let i = 0; i <= n; i++) { const x = lerp(x0, x1, i / n); o.push(toScreen([x, f(x)])); }
  return o;
}
function fillPts(pts, col, a = 1) {
  ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = col; ctx.beginPath();
  pts.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
  ctx.closePath(); ctx.fill(); ctx.restore();
}
/** point at fraction u (0..1) of the way along a polyline: {x, y, ang} */
function along(pts, u) {
  const r = resample(pts, 4), L = r[r.length - 1][2];
  const s = clamp(u) * L;
  let i = 1;
  while (i < r.length - 1 && r[i][2] < s) i++;
  const a = r[i - 1], b = r[i], f = (s - a[2]) / Math.max(1e-6, b[2] - a[2]);
  return { x: lerp(a[0], b[0], f), y: lerp(a[1], b[1], f), ang: Math.atan2(b[1] - a[1], b[0] - a[0]) };
}
/** moving chevrons along a path (direction of motion) */
function flow(pts, o = {}) {
  const r = resample(pts, 4), L = r[r.length - 1][2];
  const gap = o.gap || 90, sp = o.speed || 110, sz = o.size || 11;
  const upto = L * (o.p === undefined ? 1 : clamp(o.p));
  ctx.save();
  ctx.strokeStyle = o.c || C.ink; ctx.lineWidth = o.w || 3.5; ctx.lineCap = 'round';
  ctx.globalAlpha *= (o.a === undefined ? 0.9 : o.a);
  let idx = 0;
  for (let s = ((NOW * sp) % gap + gap) % gap; s < upto; s += gap) {
    while (idx < r.length - 1 && r[idx][2] < s) idx++;
    const b = r[idx], a = r[Math.max(0, idx - 2)];
    const ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
    ctx.beginPath();
    ctx.moveTo(b[0] - Math.cos(ang - 0.6) * sz, b[1] - Math.sin(ang - 0.6) * sz);
    ctx.lineTo(b[0], b[1]);
    ctx.lineTo(b[0] - Math.cos(ang + 0.6) * sz, b[1] - Math.sin(ang + 0.6) * sz);
    ctx.stroke();
  }
  ctx.restore();
}

// ---------------------------------------------------------------- text
/** text with typewriter reveal. o: {p: 0..1 reveal, size, f: font, c: color, al: 'center'|'left'|'right',
 *  a: alpha, bold, pop: 0..1 overshoot scale-in, rot}. Returns the full width in px. */
function txt(s, x, y, o = {}) {
  const p = o.p === undefined ? 1 : clamp(o.p);
  if (p <= 0) return;
  const chars = [...s];
  const n = Math.ceil(chars.length * p);
  ctx.save();
  if (o.a !== undefined) ctx.globalAlpha *= o.a;
  ctx.font = `${o.bold ? 'bold ' : ''}${o.size || 40}px ${o.f || ZH}`;
  ctx.fillStyle = o.c || C.ink;
  ctx.textBaseline = 'middle';
  const full = ctx.measureText(s).width;
  const al = o.al || 'center';
  let x0 = al === 'center' ? x - full / 2 : al === 'right' ? x - full : x;
  if (o.pop !== undefined) {
    const k = back(o.pop);
    ctx.translate(x, y); ctx.scale(k, k); ctx.translate(-x, -y);
  }
  if (o.rot) { ctx.translate(x, y); ctx.rotate(o.rot); ctx.translate(-x, -y); }
  ctx.textAlign = 'left';
  ctx.fillText(chars.slice(0, n).join(''), x0, y);
  ctx.restore();
  return full;
}
/** bilingual label: Chinese above, English below */
function lb(zh, en, x, y, o = {}) {
  const s = o.s || 40;
  const p = o.p === undefined ? 1 : o.p;
  txt(zh, x, y, { size: s, c: o.c, al: o.al, p: p * 1.6, a: o.a, pop: o.pop });
  txt(en, x, y + s * 0.95, { size: s * 0.62, f: EN, c: o.ec || C.gray, al: o.al, p: p * 1.6 - 0.4, a: o.a, pop: o.pop });
}
/** run fn with extra alpha a */
function grp(a, fn) { if (a <= 0.002) return; ctx.save(); ctx.globalAlpha *= clamp(a); fn(); ctx.restore(); }
/** run fn scaled by k around (x, y) */
function scaleAt(x, y, k, fn) { if (k <= 0.002) return; ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.translate(-x, -y); fn(); ctx.restore(); }

// ---------------------------------------------------------------- props
function dot(x, y, col = C.ink, r = 5.5) { ctx.save(); ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.restore(); }
/** point label: dot at q plus a letter offset by (dx, dy) */
function ptLabel(s, q, dx, dy, p = 1, col = C.ink) {
  if (p <= 0) return;
  dot(q[0], q[1], col, 6 * clamp(p * 2));
  txt(s, q[0] + dx, q[1] + dy, { size: 44, f: MF, p, c: col });
}
/** parallel-mark chevron at the midpoint of segment p-q */
function paraM(p, q, col, pp = 1) {
  const x = (p[0] + q[0]) / 2, y = (p[1] + q[1]) / 2, ang = Math.atan2(q[1] - p[1], q[0] - p[0]);
  draw([[x - Math.cos(ang - 0.6) * 13, y - Math.sin(ang - 0.6) * 13], [x, y], [x - Math.cos(ang + 0.6) * 13, y - Math.sin(ang + 0.6) * 13]], { c: col, w: 4, rough: 0.3, single: true, p: pp });
}
/** equal-length tick marks (n ticks) across the midpoint of segment p-q */
function tickM(p, q, n = 1, col = C.ink, pp = 1) {
  const [x, y] = mid(p, q), ang = Math.atan2(q[1] - p[1], q[0] - p[0]), nx = -Math.sin(ang), ny = Math.cos(ang);
  for (let i = 0; i < n; i++) {
    const o = (i - (n - 1) / 2) * 9, cx = x + Math.cos(ang) * o, cy = y + Math.sin(ang) * o;
    line(cx - nx * 12, cy - ny * 12, cx + nx * 12, cy + ny * 12, { c: col, w: 3.5, rough: 0.3, single: true, p: pp });
  }
}
/** right-angle square at vertex V between rays toward A and B */
function rightM(V, A, B, col = C.ink, s = 26, pp = 1) {
  const u = [A[0] - V[0], A[1] - V[1]], v = [B[0] - V[0], B[1] - V[1]];
  const lu = Math.hypot(...u), lv = Math.hypot(...v);
  const a = [V[0] + u[0] / lu * s, V[1] + u[1] / lu * s], b = [V[0] + v[0] / lv * s, V[1] + v[1] / lv * s];
  draw([a, [a[0] + b[0] - V[0], a[1] + b[1] - V[1]], b], { c: col, w: 3.5, rough: 0.3, single: true, p: pp });
}
/** angle arc at vertex V from ray VA to ray VB (shorter way), radius r */
function angM(V, A, B, col = C.red, r = 40, pp = 1) {
  const a0 = Math.atan2(A[1] - V[1], A[0] - V[0]);
  let d = Math.atan2(B[1] - V[1], B[0] - V[0]) - a0;
  while (d > PI) d -= TAU; while (d < -PI) d += TAU;
  draw(ellPts(V[0], V[1], r, r, a0, a0 + d, 30), { c: col, w: 4, rough: 0.4, p: pp });
}
/** rubber stamp that slams in (use for the final answer). rot in radians. */
function stamp(x, y, str, p, col = C.red, size = 48, rot = -0.12) {
  if (p <= 0) return;
  scaleAt(x, y, back(p) * (1 + 0.6 * (1 - clamp(p * 3))), () => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.translate(-x, -y);
    ctx.font = `${size}px ${ZH}`;
    const w = ctx.measureText(str).width + 44, h = size + 30;
    const pts = [[x - w / 2, y - h / 2], [x + w / 2, y - h / 2], [x + w / 2, y + h / 2], [x - w / 2, y + h / 2], [x - w / 2, y - h / 2]];
    fillPts(pts, 'rgba(255,253,246,0.9)');
    draw(pts, { c: col, w: 5, seed: x });
    txt(str, x, y + 2, { size, c: col });
    ctx.restore();
  });
}
/** round token with one character inside (moving objects: 甲, 乙, P …) */
function token(ch, x, y, col, k = 1) {
  scaleAt(x, y, back(k), () => {
    fillPts(ellPts(x, y, 25, 25), '#fffdf7');
    circ(x, y, 25, { c: col, w: 4, seed: col.length + x * 0.01, rough: 0.6 });
    txt(ch, x, y + 1, { size: 30, c: col });
  });
}

function cloudPts(x, y, sx, sy, bumps = 3.5, ph = 0.3) {
  const pts = [];
  for (let i = 0; i <= 100; i++) {
    const a = i / 100 * TAU;
    const r = 0.84 + 0.17 * Math.abs(Math.sin(a * bumps + ph));
    pts.push([x + Math.cos(a) * r * sx, y + Math.sin(a) * r * sy]);
  }
  return pts;
}

/** mascot "Puff" (小气团). s = scale (0.5 in a corner, 1.3 in the outro). o: {mood: 'happy'|'wow'|'dizzy', look: [dx, dy], wave: bool, a} */
function puff(x, y, s, o = {}) {
  if (s <= 0.01) return;
  const t = NOW + (o.seed || 0), mood = o.mood || 'happy';
  if (!o.nobob && !window.NO_BOIL) y += Math.sin(t * 3.2) * 6 * s;
  const col = C.ink;
  ctx.save();
  if (o.a !== undefined) ctx.globalAlpha *= o.a;
  const pts = cloudPts(x, y, 80 * s, 62 * s);
  fillPts(pts, '#ffffff');
  draw(pts, { c: col, w: Math.max(3, 4.5 * s), seed: 11 });
  const ex = 24 * s, ey = -8 * s;
  const lx = (o.look ? o.look[0] : 0) * 5 * s, ly = (o.look ? o.look[1] : 0) * 4 * s;
  const blink = !window.NO_BOIL && ((t * 1.0) % 3.3) < 0.12;
  ctx.fillStyle = C.ink;
  if (mood === 'dizzy') {
    [-1, 1].forEach(d => {
      const pts2 = [];
      for (let i = 0; i < 30; i++) { const a = i * 0.45 + t * 8, rr = i * 0.38 * s; pts2.push([x + d * ex + Math.cos(a) * rr, y + ey + Math.sin(a) * rr]); }
      draw(pts2, { w: 2.5, rough: 0.2, single: true });
    });
  } else if (blink) {
    [-1, 1].forEach(d => line(x + d * ex - 8 * s, y + ey, x + d * ex + 8 * s, y + ey, { w: 3.5, rough: 0.3 }));
  } else {
    [-1, 1].forEach(d => {
      ctx.beginPath(); ctx.ellipse(x + d * ex + lx, y + ey + ly, 7.5 * s, 10 * s, 0, 0, TAU); ctx.fill();
      ctx.save(); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x + d * ex + lx + 2.5 * s, y + ey + ly - 4 * s, 2.6 * s, 0, TAU); ctx.fill(); ctx.restore();
    });
  }
  if (mood === 'wow' || mood === 'dizzy') draw(ellPts(x, y + 22 * s, 8 * s, 10 * s), { w: 3.5, rough: 0.5 });
  else draw(quadPts(x - 17 * s, y + 14 * s, x, y + 34 * s, x + 17 * s, y + 14 * s), { w: 3.5, rough: 0.6 });
  draw(ellPts(x - 46 * s, y + 12 * s, 10 * s, 5 * s), { c: C.pink, w: 3, single: true });
  draw(ellPts(x + 46 * s, y + 12 * s, 10 * s, 5 * s), { c: C.pink, w: 3, single: true });
  if (o.wave) {
    const a = 0.9 + 0.5 * Math.sin(t * 10);
    const bx = x + 78 * s, by = y + 4 * s;
    draw([[bx, by], [bx + Math.cos(a) * 26 * s, by - Math.sin(a) * 26 * s], [bx + Math.cos(a) * 46 * s, by - Math.sin(a) * 46 * s]], { w: 4, c: col });
  }
  ctx.restore();
}
/** speech bubble with its tail at the lower left */
function bubble(x, y, str, p, o = {}) {
  if (p <= 0) return;
  scaleAt(x, y, back(p), () => {
    ctx.font = `${o.size || 40}px ${o.f || ZH}`;
    const w = ctx.measureText(str).width + 50, h = (o.size || 40) + 36;
    const pts = [[x - w / 2, y - h / 2], [x + w / 2, y - h / 2], [x + w / 2, y + h / 2], [x - w / 2 + 50, y + h / 2], [x - w / 2 + 20, y + h / 2 + 26], [x - w / 2 + 28, y + h / 2], [x - w / 2, y + h / 2], [x - w / 2, y - h / 2]];
    fillPts(pts, '#fffdf7');
    draw(pts, { w: 3.5, seed: 8 });
    txt(str, x, y + 2, { size: o.size || 40, f: o.f, c: o.c });
  });
}

// ---------------------------------------------------------------- background: grid paper
const bgCanvas = document.createElement('canvas');
bgCanvas.width = W; bgCanvas.height = H;
(function paintBg() {
  const b = bgCanvas.getContext('2d');
  b.fillStyle = C.paper; b.fillRect(0, 0, W, H);
  b.strokeStyle = 'rgba(80,130,190,0.09)'; b.lineWidth = 1.5;
  for (let x = 30; x < W; x += 60) { b.beginPath(); b.moveTo(x, 0); b.lineTo(x, H); b.stroke(); }
  for (let y = 30; y < H; y += 60) { b.beginPath(); b.moveTo(0, y); b.lineTo(W, y); b.stroke(); }
  for (let i = 0; i < 9000; i++) {
    const x = hash(i * 1.7) * W, y = hash(i * 2.3 + 9) * H;
    b.fillStyle = `rgba(120,100,70,${0.04 + hash(i) * 0.05})`;
    b.fillRect(x, y, 1.6, 1.6);
  }
  const g = b.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.05);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(90,70,40,0.16)');
  b.fillStyle = g; b.fillRect(0, 0, W, H);
})();

// ---------------------------------------------------------------- lined board (right half): derivation text
// Figure goes in the LEFT half (x 60..900, y 130..860). Board is x 930..1870, y 130..880, 11 rows.
const BX0 = 930, BX1 = 1870, BY0 = 130, BY1 = 880;
function board(p = 1) {
  if (p <= 0) return;
  grp(clamp(p * 2), () => {
    const pts = [[BX0, BY0], [BX1, BY0 + 4], [BX1 + 2, BY1], [BX0 - 2, BY1 - 3], [BX0, BY0]];
    fillPts(pts, '#fffdf7', 0.92);
    for (let y = BY0 + 70; y < BY1 - 10; y += 62) line(BX0 + 20, y + 26, BX1 - 20, y + 26, { c: 'rgba(59,125,216,0.25)', w: 2, rough: 0.6, single: true });
    draw(pts, { w: 4, p });
  });
}
/** screen position of board row i (left edge, vertical centre): target for flyText */
const blPos = (i, dx = 0) => [BX0 + 36 + dx, BY0 + 62 + i * 62];
/** "substitute": a copy of a label flies from the figure (from = [x, y]) to the board (to = [x, y]) along an arc,
 *  e = eased progress. Use it when the narration plugs a known value from the figure into the equation. */
function flyText(str, from, to, e, o = {}) {
  if (e <= 0 || e >= 1) return;
  const pts = quadPts(from[0], from[1], (from[0] + to[0]) / 2, Math.min(from[1], to[1]) - 120, to[0], to[1], 30);
  const q = along(pts, e);
  txt(str, q.x, q.y, { size: (o.size || 40) * (1 + 0.25 * Math.sin(PI * e)), f: MF, c: o.c || C.red, bold: true });
}
/** board line: row i (0..10, fractional ok), typed in starting at scene-local time t.
 *  o: {c, size (default 38; max ~50), x, y0, lh}. Keep each row ≤ ~40 characters at size 38. */
function bl(i, str, t, lt, o = {}) {
  const p = clamp((lt - t) / Math.max(0.5, [...str].length * 0.05));
  const y = (o.y0 || BY0 + 62) + i * (o.lh || 62);
  txt(str, o.x || BX0 + 36, y, { size: o.size || 38, f: MF, c: o.c || C.ink, al: 'left', p });
}

// ---------------------------------------------------------------- scene tag (top-left): TAGS comes from anim.js
function tag(id, lt) {
  const tg = TAGS[id]; if (!tg) return;
  const p = clamp((lt - 0.2) / 0.8);
  txt(tg[0], 70, 70, { size: 44, f: EN, c: C.red, al: 'left', p: p * 2 });
  const w = txt(tg[1], 125, 68, { size: 40, al: 'left', p: p * 2 - 0.3 }) || 0;
  txt(tg[2], 125 + w + 18, 72, { size: 30, f: EN, c: C.gray, al: 'left', p: p * 2 - 0.8 });
  draw([[64, 100], [140 + w + 300, 104]], { c: C.yellow, w: 6, p: p * 1.5 - 0.3, seed: 77, a: 0.8 });
}

// ---------------------------------------------------------------- problem screenshot (PROBLEM comes from anim.js)
// The image is fitted (aspect kept) into the box FRAME below; highlight boxes use SOURCE-IMAGE pixel coordinates.
const PROB_IMG = new Image();
const FRAME = { x0: 150, y0: 240, x1: 1772, y1: 730 };  // area the card may use (image fitted inside, max 2.2x);
                                                       // chips go at y≈790, subtitles start at y≈914
let IMG = null;   // {x, y, w, h, k} = where the image is drawn and its scale
let CARD = null;  // white card around the image
function fitProblem() {
  const pad = 22, bw = FRAME.x1 - FRAME.x0 - 2 * pad, bh = FRAME.y1 - FRAME.y0 - 2 * pad;
  const k = Math.min(bw / PROBLEM.srcW, bh / PROBLEM.srcH, 2.2);
  const w = PROBLEM.srcW * k, h = PROBLEM.srcH * k;
  IMG = { x: (FRAME.x0 + FRAME.x1 - w) / 2, y: (FRAME.y0 + FRAME.y1 - h) / 2, w, h, k };
  CARD = { x0: IMG.x - pad, y0: IMG.y - pad, x1: IMG.x + w + pad, y1: IMG.y + h + pad };
}
/** draw the white card + the problem image. p = fade-in progress */
function problemCard(p) {
  if (p <= 0) return;
  const c = CARD, box = [[c.x0, c.y0], [c.x1, c.y0 + 2], [c.x1, c.y1], [c.x0, c.y1 - 2], [c.x0, c.y0]];
  fillPts(box, '#ffffff', 0.95 * clamp(p * 1.5));
  grp(clamp(p * 1.5 - 0.3), () => { if (PROB_IMG.complete && PROB_IMG.naturalWidth) ctx.drawImage(PROB_IMG, IMG.x, IMG.y, IMG.w, IMG.h); });
  draw(box, { w: 3, p });
}
/** hand-drawn highlight rectangle around source-pixel box [x0, y0, x1, y1] (or a list of boxes, for a phrase
 *  that wraps onto two lines); drawn on over 0.5 s starting at scene-local time t */
function hiBox(b, col, t, lt) {
  if (lt < t) return;
  if (Array.isArray(b[0])) { b.forEach(bb => hiBox(bb, col, t, lt)); return; }
  const k = IMG.k, pad = 4;
  const x0 = IMG.x + b[0] * k - pad, y0 = IMG.y + b[1] * k - pad, x1 = IMG.x + b[2] * k + pad, y1 = IMG.y + b[3] * k + pad;
  fillPts([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], col, 0.12 * clamp((lt - t) / 0.5));
  draw([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]], { c: col, w: 5, p: clamp((lt - t) / 0.5), rough: 0.8 });
}
/** condition chip under the card (y ≈ 790). */
const chip = (s, x, col, p) => stamp(x, 790, s, p, col, 36, 0);

// ---------------------------------------------------------------- explanation helpers (reference/visual-design.md)
// These turn "the narration names X" into something the eye can follow. Use them in every scene.
/** 0 -> 1 -> 0 bump starting at scene-local time t0: flash / pulse an element when the narration names it */
function bump(lt, t0, dur = 1.2) { const x = (lt - t0) / dur; return x <= 0 || x >= 1 ? 0 : Math.sin(PI * x); }
/** highlighter pen: thick translucent stroke UNDER an element (call it before drawing the element). a = 0..1 */
function glow(pts, col = C.yellow, a = 1, w = 22) { if (a > 0.01) draw(pts, { c: col, w, a: 0.45 * a, rough: 0.6, single: true }); }
/** morph between two point lists of equal length */
const tween = (P0, P1, e) => P0.map((p, i) => mix2(p, P1[i], e));
/** a copy of segment a-b travels (translate + rotate + stretch) onto c-d: "these are equal / parallel / correspond".
 *  e = eased progress 0..1 (use eio(P(...))). Leaves the copy on c-d when e = 1. */
function slideSeg(a, b, c, d, e, o = {}) {
  if (e <= 0) return;
  const m = mix2(mid(a, b), mid(c, d), e);
  const a0 = Math.atan2(b[1] - a[1], b[0] - a[0]);
  let da = Math.atan2(d[1] - c[1], d[0] - c[0]) - a0;
  while (da > PI / 2) da -= PI; while (da < -PI / 2) da += PI;   // segments have no direction: shortest turn
  const ang = a0 + da * e, L = lerp(Math.hypot(b[0] - a[0], b[1] - a[1]), Math.hypot(d[0] - c[0], d[1] - c[1]), e) / 2;
  const u = [Math.cos(ang) * L, Math.sin(ang) * L];
  draw([[m[0] - u[0], m[1] - u[1]], [m[0] + u[0], m[1] + u[1]]], { c: o.c || C.red, w: o.w || 7, a: o.a === undefined ? 0.85 : o.a, rough: 0.4, single: true });
}
/** rigid motion of a polygon about its centroid: move by (dx, dy), rotate by rot, scale by k -> new points.
 *  Overlay one triangle on another (congruent: k = 1; similar: k = ratio); flip with k < 0 on one axis via o.flip */
function movePoly(pts, dx, dy, rot = 0, k = 1) {
  const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length, cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
  const cs = Math.cos(rot), sn = Math.sin(rot);
  return pts.map(([x, y]) => { const u = (x - cx) * k, v = (y - cy) * k; return [cx + dx + u * cs - v * sn, cy + dy + u * sn + v * cs]; });
}
/** rotate (and scale by k) a point list about the point c. Rotating an angle's arc by PI about the midpoint of
 *  the transversal shows alternate angles are equal; about a vertex it shows a rotation / congruence. */
function rotAbout(pts, c, ang, k = 1) {
  const cs = Math.cos(ang), sn = Math.sin(ang);
  return pts.map(([x, y]) => { const u = (x - c[0]) * k, v = (y - c[1]) * k; return [c[0] + u * cs - v * sn, c[1] + u * sn + v * cs]; });
}
/** curved dashed arrow from a figure point to (usually) a board row: ties a quantity on the figure to its equation */
function callout(from, to, p, col = C.gray, bend = 0.25) {
  if (p <= 0) return;
  const mx = (from[0] + to[0]) / 2, my = (from[1] + to[1]) / 2, dx = to[0] - from[0], dy = to[1] - from[1];
  arrow(quadPts(from[0], from[1], mx - dy * bend, my + dx * bend, to[0], to[1]), { c: col, w: 3, dash: [10, 8], single: true, rough: 0.3, p, head: 14 });
}
/** number that counts from v0 to v1 as e goes 0..1 (lengths, times, areas growing on screen) */
const countTo = (v0, v1, e, dec = 0) => lerp(v0, v1, clamp(e)).toFixed(dec);
/** blend the 3D camera between two poses, e.g. oblique -> top view: camTween({pitch: 0.52, yaw: 0.2}, {pitch: PI / 2, yaw: 0}, e).
 *  pitch = PI/2 is an exact top view (z is ignored), so the same 3D model turns into the base-plane drawing. */
function camTween(A, B, e) { for (const k of Object.keys(A)) CAM[k] = Array.isArray(A[k]) ? A[k].map((v, i) => lerp(v, B[k][i], e)) : lerp(A[k], B[k], e); }

// ---------------------------------------------------------------- coordinate plane (functions, analytic geometry)
/** Make a coordinate system. o: {ox, oy: screen position of the origin, sx, sy: px per unit,
 *  xr: [xmin, xmax], yr: [ymin, ymax] (math units, the visible range), step: tick spacing (default 1)}.
 *  Returns {S: [x, y] -> [px, py], draw(p, grid)} ; call ax.draw(progress) inside a scene. */
function axes(o) {
  const S = ([x, y]) => [o.ox + x * o.sx, o.oy - y * o.sy];
  const step = o.step || 1;
  function drawAxes(p = 1, grid = false) {
    if (p <= 0) return;
    const [x0, x1] = o.xr, [y0, y1] = o.yr;
    if (grid) grp(0.5 * clamp(p * 2), () => {
      for (let x = Math.ceil(x0 / step) * step; x <= x1; x += step) if (Math.abs(x) > 1e-9) line(...S([x, y0]), ...S([x, y1]), { c: 'rgba(59,125,216,0.25)', w: 1.5, rough: 0, single: true });
      for (let y = Math.ceil(y0 / step) * step; y <= y1; y += step) if (Math.abs(y) > 1e-9) line(...S([x0, y]), ...S([x1, y]), { c: 'rgba(59,125,216,0.25)', w: 1.5, rough: 0, single: true });
    });
    arrow([S([x0, 0]), S([x1 + 0.3 * step, 0])], { w: 3.5, p, head: 14, rough: 0.5 });
    arrow([S([0, y0]), S([0, y1 + 0.3 * step])], { w: 3.5, p, head: 14, rough: 0.5 });
    grp(clamp(p * 2 - 1), () => {
      txt('x', ...S([x1 + 0.3 * step, 0]).map((v, i) => v + (i ? 28 : 0)), { size: 34, f: MF });
      txt('y', ...S([0, y1 + 0.3 * step]).map((v, i) => v + (i ? 4 : 28)), { size: 34, f: MF });
      txt('O', ...S([0, 0]).map((v, i) => v + (i ? 24 : -22)), { size: 30, f: MF });
      if (o.labels !== false) {
        for (let x = Math.ceil(x0 / step) * step; x <= x1; x += step) if (Math.abs(x) > 1e-9) {
          const [px, py] = S([x, 0]); line(px, py - 6, px, py + 6, { w: 2.5, rough: 0, single: true });
          txt(String(+x.toFixed(2)), px, py + 26, { size: 24, f: MF, c: C.gray });
        }
        for (let y = Math.ceil(y0 / step) * step; y <= y1; y += step) if (Math.abs(y) > 1e-9) {
          const [px, py] = S([0, y]); line(px - 6, py, px + 6, py, { w: 2.5, rough: 0, single: true });
          txt(String(+y.toFixed(2)), px - 14, py, { size: 24, f: MF, c: C.gray, al: 'right' });
        }
      }
    });
  }
  return { S, draw: drawAxes };
}

// ---------------------------------------------------------------- 3D (solid geometry): oblique camera
// Use for cones, pyramids, cubes. World coords: x right, y TOWARD the viewer (drawn lower on screen), z up.
// Set CAM.cx/cy (screen centre), CAM.s (px per unit), CAM.target (world point at the centre) in anim.js.
// Edges on the far side (small y, hidden behind faces) must be dashed: L3(a, b, {hidden: true}). Check in a still.
const CAM = { cx: 470, cy: 520, s: 160, pitch: 0.52, yaw: 0.2, target: [0, 0, 0] };
const sub3 = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const mix3 = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
const dot3 = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const norm3 = a => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
/** project a 3D point to screen [x, y] */
function pr(p) {
  const q = sub3(p, CAM.target);
  const cs = Math.cos(CAM.yaw), sn = Math.sin(CAM.yaw);
  const u = q[0] * cs + q[1] * sn, v = -q[0] * sn + q[1] * cs;
  return [CAM.cx + CAM.s * u, CAM.cy + CAM.s * (v * Math.sin(CAM.pitch) - q[2] * Math.cos(CAM.pitch))];
}
/** 3D segment; o.hidden = true draws it dashed (edges behind a face must be dashed, as in textbooks) */
function L3(a, b, o = {}) { return draw([pr(a), pr(b)], { rough: 0.7, w: 4, ...o, dash: o.hidden ? [13, 9] : o.dash }); }
/** 3D angle arc at V between rays V->a and V->b, radius rad (world units): returns screen points for draw() */
function arc3(V, a, b, rad, n = 24) {
  const u = norm3(sub3(a, V)), vb = sub3(b, V);
  const w = norm3(sub3(vb, u.map(x => x * dot3(vb, u))));
  const ang = Math.acos(clamp(dot3(u, norm3(vb)), -1, 1));
  const out = [];
  for (let i = 0; i <= n; i++) {
    const t = ang * i / n;
    out.push(pr([0, 1, 2].map(j => V[j] + rad * (Math.cos(t) * u[j] + Math.sin(t) * w[j]))));
  }
  return out;
}

/** Unroll a cone's lateral surface into its sector. The cone: base circle centre `base3` (3D, on z = const),
 *  radius r, apex `apex3`, slant height l. e = 0 draws the 3D lateral rim (via pr), e = 1 the flat sector with its
 *  centre at `apex2` (screen), slant drawn `Ls` px long, opening toward angle `dir` (PI/2 = downwards).
 *  Sector angle = 2*PI*r/l. Returns {rim, top} screen points so you can label them. */
function unrollCone(e, o) {
  const n = 72, theta = 2 * PI * o.r / o.l, rim3 = [], rim2 = [], dir = o.dir === undefined ? PI / 2 : o.dir;
  for (let i = 0; i <= n; i++) {
    const a = PI + 2 * PI * i / n;                            // start the cut at the generator through (-r, 0)
    rim3.push(pr([o.base3[0] + o.r * Math.cos(a), o.base3[1] + o.r * Math.sin(a), o.base3[2]]));
    const b = dir - theta / 2 + theta * i / n;
    rim2.push([o.apex2[0] + o.Ls * Math.cos(b), o.apex2[1] + o.Ls * Math.sin(b)]);
  }
  const rim = tween(rim3, rim2, e), top = mix2(pr(o.apex3), o.apex2, e), col = o.c || C.blue;
  fillPts([top, ...rim], col, (o.fill === undefined ? 0.16 : o.fill) * clamp(e * 3));
  draw(rim, { c: col, w: 4, rough: 0.5 });
  draw([top, rim[0]], { c: col, w: 4, rough: 0.5 }); draw([top, rim[n]], { c: col, w: 4, rough: 0.5 });
  return { rim, top };
}

// ---------------------------------------------------------------- subtitles (bilingual, bottom box, y 914..1044)
function wrap(str, font, maxW) {
  ctx.font = font;
  if (ctx.measureText(str).width <= maxW) return [str];
  const chars = [...str];
  let best = null;
  const m = chars.length / 2;
  const isZh = /[一-鿿]/.test(str);
  for (let i = 1; i < chars.length; i++) {
    const ok = isZh ? /[，；：、——！？。]/.test(chars[i - 1]) : chars[i - 1] === ' ';
    if (!ok) continue;
    const a = chars.slice(0, i).join('').trim(), b = chars.slice(i).join('').trim();
    const sc = Math.abs(i - m);
    if (ctx.measureText(a).width <= maxW && ctx.measureText(b).width <= maxW && (!best || sc < best.sc)) best = { a, b, sc };
  }
  if (best) return [best.a, best.b];
  const i = Math.round(m);
  return [chars.slice(0, i).join(''), chars.slice(i).join('')];
}
/** H_2O / x^2 markup -> Unicode sub/superscripts on screen */
const SUBS = { 0: '₀', 1: '₁', 2: '₂', 3: '₃', 4: '₄', 5: '₅', 6: '₆', 7: '₇', 8: '₈', 9: '₉', '+': '₊', '-': '₋' };
const SUPS = { 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹', '+': '⁺', '-': '⁻', n: 'ⁿ' };
const plain = s => s.replace(/_(\d)/g, (_, d) => SUBS[d]).replace(/\^([0-9+\-n]+)/g, (_, g) => [...g].map(c => SUPS[c]).join(''));
function subtitles(t) {
  let cur = null;
  for (const sc of TL.scenes) for (const ln of sc.lines) if (t >= ln.start - 0.05 && t < (ln.hold_end ?? ln.end) + 0.3) cur = ln;
  if (!cur) return;
  const a = clamp((t - cur.start + 0.05) / 0.15) * clamp(((cur.hold_end ?? cur.end) + 0.3 - t) / 0.15);
  const zf = `600 44px ${SUB}`, ef = `30px ${EN}`;
  const zl = wrap(plain(cur.zh), zf, 1640), el = wrap(plain(cur.en), ef, 1640);
  ctx.font = zf; let w = Math.max(...zl.map(s => ctx.measureText(s).width));
  ctx.font = ef; w = Math.max(w, ...el.map(s => ctx.measureText(s).width));
  const ZLH = 54, ELH = 38, PT = 14, PB = 18, GAP = 6;
  const h = PT + zl.length * ZLH + GAP + el.length * ELH + PB;
  const yb = 1044, y0 = yb - h, x0 = 960 - w / 2 - 36, x1 = 960 + w / 2 + 36;
  grp(a, () => {
    ctx.save();
    ctx.fillStyle = 'rgba(255,253,246,0.93)';
    ctx.beginPath(); ctx.roundRect(x0, y0, x1 - x0, h, 18); ctx.fill();
    ctx.restore();
    draw([[x0 + 10, y0], [x1 - 10, y0 + 1], [x1, y0 + 12], [x1 - 1, yb - 10], [x1 - 12, yb], [x0 + 10, yb - 1], [x0, yb - 12], [x0 + 1, y0 + 10], [x0 + 10, y0]], { w: 2.5, c: C.ink, a: 0.55, rough: 1, single: true, seed: 1 });
    let y = y0 + PT + ZLH / 2;
    zl.forEach(s => { txt(s, 960, y, { size: 44, f: SUB, c: C.ink, bold: true }); y += ZLH; });
    y += GAP - ZLH / 2 + ELH / 2;
    el.forEach(s => { txt(s, 960, y, { size: 30, f: EN, c: '#4c6f9e' }); y += ELH; });
  });
}

// ---------------------------------------------------------------- main loop
function sceneAt(t) {
  let i = TL.scenes.findIndex(s => t >= s.start && t < s.end);
  if (i < 0) i = t < 0 ? 0 : TL.scenes.length - 1;
  return i;
}
/** Scene helper S passed to every SC.<id>(lt, S):
 *   S.cue(k)       scene-local time when narration line k starts
 *   S.dur(k)       duration of line k
 *   S.at(k, f)     cue(k) + f * dur(k)   (f = 0.5 -> halfway through line k)
 *   S.P(a, dd)     progress 0..1 of an animation starting at scene-local time a, lasting dd seconds (default 0.7)
 *   S.n            number of lines in this scene */
function drawScene(i, lt) {
  const sc = TL.scenes[i];
  const cue = k => sc.lines[k].start - sc.start, dur = k => sc.lines[k].end - sc.lines[k].start;
  const S = { cue, dur, at: (k, f = 0) => cue(k) + dur(k) * f, P: (a, dd = 0.7) => clamp((lt - a) / dd), n: sc.lines.length };
  if (!SC[sc.id]) throw new Error(`anim.js has no SC.${sc.id} (scene id from script.json)`);
  SC[sc.id](lt, S);
  tag(sc.id, lt);
}
function renderFrame(t) {
  NOW = t;
  BOIL = window.NO_BOIL ? 0 : Math.floor(t * 8);  // line "boil": wobble re-seeds 8x per second (off in `render.mjs motion`)
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.drawImage(bgCanvas, 0, 0);
  const i = sceneAt(t);
  const sc = TL.scenes[i];
  const lt = t - sc.start;
  const TR = 0.75;  // cross-fade between scenes
  if (i > 0 && lt < TR) {
    const e = eio(lt / TR);
    const prev = TL.scenes[i - 1];
    grp(1 - e, () => drawScene(i - 1, t - prev.start));
    grp(e, () => drawScene(i, lt));
  } else {
    drawScene(i, lt);
  }
  const fin = clamp(t / 0.6), fout = clamp((TL.duration - t) / 1.2);
  if (fin < 1 || fout < 1) {
    ctx.fillStyle = `rgba(251,246,234,${1 - Math.min(fin, fout)})`;
    ctx.fillRect(0, 0, W, H);
  }
  subtitles(t);
}
window.renderFrame = renderFrame;

/** called from index.html after anim.js has loaded */
function boot() {
  if (typeof PROBLEM !== 'undefined' && PROBLEM) { PROB_IMG.src = PROBLEM.src; fitProblem(); }
  window.ready = (async () => {
    await Promise.all([document.fonts.load("40px Kuaile", '例题精讲'), document.fonts.load('40px PHand', 'Abc')]);
    await document.fonts.ready;
    if (PROB_IMG.src) await new Promise(r => { if (PROB_IMG.complete) r(); else { PROB_IMG.onload = r; PROB_IMG.onerror = r; } });
    renderFrame(0);
    return true;
  })();
  if (!/render=1/.test(location.search)) {  // interactive preview in a browser
    const au = document.getElementById('au'), seek = document.getElementById('seek'), btn = document.getElementById('play');
    btn.onclick = () => { if (au.paused) { au.play(); btn.textContent = '❚❚ 暂停 Pause'; } else { au.pause(); btn.textContent = '▶ 播放 Play'; } };
    seek.oninput = () => { const tt = seek.value / 1000 * TL.duration; au.currentTime = tt; renderFrame(tt); };
    const loop = () => { if (!au.paused) { renderFrame(au.currentTime); seek.value = au.currentTime / TL.duration * 1000; } requestAnimationFrame(loop); };
    window.ready.then(loop);
  } else {
    document.body.classList.add('render');
  }
}
