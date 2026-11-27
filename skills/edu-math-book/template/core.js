/* ======================================================================
   core.js — loaded BEFORE the lesson, so everything here can be used inside lesson.js
   ====================================================================== */

/* ---------- colours (lessons refer to them by name) ---------- */
const COL = {violet:'#7c5cff', blue:'#2f7bf5', orange:'#f08a1c', pink:'#e8458b', green:'#10a37f', red:'#d64545', ink:'#2b2a28'};

/* ---------- tiny vector helpers (work for 2D and 3D points alike) ---------- */
const add = (p, q) => p.map((v, i) => v + q[i]);
const sub = (p, q) => p.map((v, i) => v - q[i]);
const mul = (p, k) => p.map(v => v * k);
const dot = (p, q) => p.reduce((s, v, i) => s + v * q[i], 0);
const mid = (p, q) => mul(add(p, q), .5);
const len = p => Math.hypot(...p);
const dist = (p, q) => len(sub(p, q));
const unit = p => mul(p, 1 / (Math.hypot(...p) || 1));
const lerp = (p, q, t) => add(p, mul(sub(q, p), t));
const cross = (u, v) => [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
const centroidOf = pts => mul(pts.reduce((s, p) => add(s, p), pts[0].map(() => 0)), 1 / pts.length);
const clamp01 = t => Math.max(0, Math.min(1, t));
const ease = t => (1 - Math.cos(Math.PI * t)) / 2;
const easeOutBack = t => 1 + 2.2 * Math.pow(t - 1, 3) + 1.2 * Math.pow(t - 1, 2);
const pingpong = (t, period) => ease(Math.min(1, Math.max(0, 1.4 * (0.5 - 0.5 * Math.cos(2 * Math.PI * t / period)) - .2)));
const rad = d => d * Math.PI / 180;
const deg = r => r * 180 / Math.PI;
const SQ2 = Math.SQRT2, SQ3 = Math.sqrt(3), SQ5 = Math.sqrt(5), SQ6 = Math.sqrt(6);
// foot of the perpendicular from p onto line AB (2D or 3D)
const foot = (p, A, B) => { const d = sub(B, A); return add(A, mul(d, dot(sub(p, A), d) / dot(d, d))); };
// foot of the perpendicular from p onto the plane through A, B, C
const footPlane = (p, A, B, C) => { const n = unit(cross(sub(B, A), sub(C, A))); return sub(p, mul(n, dot(sub(p, A), n))); };
// angle at vertex v between rays v→p and v→q, in degrees
const angleAt = (v, p, q) => deg(Math.acos(Math.max(-1, Math.min(1, dot(unit(sub(p, v)), unit(sub(q, v)))))));
const fix = (v, d = 2) => (+v.toFixed(d)).toString();

/* ---------- reusable step animations (spec.anim) ---------- */
// a segment from→to slides back and forth along by[0]→by[1], showing it is parallel to where it lands
const slide = (from, to, by, c = 'violet') => (t, P) => {
  const k = pingpong(t, 3.6), v = mul(sub(P[by[1]], P[by[0]]), k);
  return [{a: add(P[from], v), b: add(P[to], v), c, w: 3, dash: 1, ghost: 1, op: .85}];
};
// a point travels along a polyline of named points (e.g. a moving point P on AB)
const travel = (keys, c = 'violet', period = 4) => (t, P) => {
  const k = pingpong(t, period) * (keys.length - 1), i = Math.min(keys.length - 2, Math.floor(k));
  return [{a: P[keys[0]], b: lerp(P[keys[i]], P[keys[i + 1]], k - i), c, w: 3.2, op: .9}];
};

/* ---------- text formatting ----------
   $AB$      → geometry symbol in italic serif (A1 → A₁); on the scratch sheet it links to the figure on hover
   \( … \)   → KaTeX formula (fractions, roots, logs, sums …) */
const tex = (s, display = false) => {
  try { return window.katex ? katex.renderToString(s, {throwOnError: false, displayMode: display}) : s; } catch (e) { return s; }
};
const geo = x => '<span class="m">' + x.replace(/([A-Z])1/g, '$1<sub>1</sub>') + '</span>';
const MATH_RE = /\\\((.+?)\\\)|\$([^$]+)\$/g;
const fmt = s => String(s ?? '').replace(MATH_RE, (_, t, g) => t != null ? tex(t) : geo(g));
