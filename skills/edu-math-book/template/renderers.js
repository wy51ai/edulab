/* ======================================================================
   renderers.js — pencil-sketch figures for the book
   Three renderers share one set of "marks" (lines, planes, angles, ticks …):
     solid : polyhedra (edges & normals derived from faces) + cylinders / cones / spheres
     plane : 2D coordinate plane or plain plane geometry; in demo mode it stands up like a pop-up card
     none  : no figure; the right page shows a formula board
   ====================================================================== */

const GRAPHITE = '#34322e', PAPER = '#fffdf6';
// counters for scripts/check.mjs: visibility flips (flicker), render errors, frames drawn
const EMB = window.__emb = {flips: 0, errors: 0, frames: 0, lastError: ''};
// a face only changes between front/back once it is clearly past edge-on (cosine), so camera parallax cannot make it flicker
const EDGE_ON = .035;
const rnd = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const f1 = v => (+v).toFixed(1);
const labelSvg = s => String(s).replace(/([A-Za-z])([0-9])/, '$1<tspan dy="6" font-size="66%">$2</tspan>');
const colOf = c => COL[c] || c || GRAPHITE;

/* SVG defs for one figure: a light pencil grain, hatch patterns per colour, blur for shadows.
   The displacement is deliberately small (1.1): stronger grain broke thin and dashed lines apart. */
const sketchDefs = id => `<filter id="${id}-pencil" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="1.1" xChannelSelector="R" yChannelSelector="G"/></filter>` +
  Object.keys(COL).map(c => `<pattern id="${id}-h-${c}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(${c === 'ink' ? 38 : -42})"><line x1="0" y1="0" x2="0" y2="7" stroke="${c === 'ink' ? GRAPHITE : COL[c]}" stroke-width="1"/></pattern>`).join('') +
  `<filter id="${id}-blur"><feGaussianBlur stdDeviation="7"/></filter>`;
const hatch = (gid, c) => `url(#${gid}-h-${COL[c] ? c : 'ink'})`;

/* a pencil stroke: two slightly offset passes that overshoot the ends a little (dashed = one clean pass) */
function sketchLine(A, B, col, w, op, seed, dash) {
  const L = Math.hypot(B[0] - A[0], B[1] - A[1]) || 1, d = [(B[0] - A[0]) / L, (B[1] - A[1]) / L], n = [-d[1], d[0]];
  let o = '';
  for (let k = 0; k < (dash ? 1 : 2); k++) {
    const ov = dash ? 0 : Math.min(L * .06, 1.5 + 4 * rnd(seed * 3 + k)), off = (rnd(seed * 7 + k * 5) - .5) * 1.4;
    const a = [A[0] - d[0] * ov + n[0] * off, A[1] - d[1] * ov + n[1] * off];
    const b = [B[0] + d[0] * ov * .7 - n[0] * off * .6, B[1] + d[1] * ov * .7 - n[1] * off * .6];
    o += `<line x1="${f1(a[0])}" y1="${f1(a[1])}" x2="${f1(b[0])}" y2="${f1(b[1])}" stroke="${col}" stroke-width="${k ? w * .5 : w}" stroke-opacity="${k ? op * .4 : op}" stroke-linecap="round"${dash ? ' stroke-dasharray="6 5"' : ''}/>`;
  }
  return o;
}
// a paper-coloured underlay so a line stays readable where it crosses fills, hatching or other lines
const haloLine = (A, B, w, op = .85) => `<line x1="${f1(A[0])}" y1="${f1(A[1])}" x2="${f1(B[0])}" y2="${f1(B[1])}" stroke="${PAPER}" stroke-width="${f1(w + 3.4)}" stroke-opacity="${op}" stroke-linecap="round"/>`;
const pathD = pts => pts.map((p, i) => (i ? 'L' : 'M') + f1(p[0]) + ' ' + f1(p[1])).join('');
function sketchPath(pts, col, w, op, dash, halo) {
  if (pts.length < 2) return '';
  const d = pathD(pts);
  return (halo ? `<path d="${d}" fill="none" stroke="${PAPER}" stroke-width="${f1(w + 3.4)}" stroke-opacity=".85" stroke-linecap="round" stroke-linejoin="round"/>` : '') +
    `<path d="${d}" fill="none" stroke="${col}" stroke-width="${w}" stroke-opacity="${op}" stroke-linecap="round" stroke-linejoin="round"${dash ? ' stroke-dasharray="6 5"' : ''}/>`;
}
function hull2d(pts) {
  const p = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]), cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = [];
  for (const q of p) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  for (const q of p.reverse()) { while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}
const ptsAttr = pts => pts.map(p => f1(p[0]) + ',' + f1(p[1])).join(' ');
// orthonormal basis of the plane perpendicular to n (3D); in 2D the basis is just x, y
function basisOf(n, dim) {
  if (dim === 2) return [[1, 0], [0, 1]];
  const N = unit(n || [0, 0, 1]), t = Math.abs(N[2]) < .9 ? [0, 0, 1] : [1, 0, 0];
  const e1 = unit(cross(t, N)); return [e1, cross(N, e1)];
}
const circlePts = (c, r, n, from = 0, to = 360, k = 72) => {
  const [e1, e2] = basisOf(n, c.length), out = [];
  for (let i = 0; i <= k; i++) { const t = rad(from + (to - from) * i / k); out.push(add(c, add(mul(e1, r * Math.cos(t)), mul(e2, r * Math.sin(t))))); }
  return out;
};

/* ======================================================================
   shared marks: everything a step can highlight, for any renderer
   ctx: {P, a, pr, R, fade, gid, u, cen, now, t}
   ====================================================================== */
function drawMarks(ctx, sp, base = false) {
  const {pr, R, gid, u, cen, now} = ctx, fade = base ? 1 : ctx.fade;
  let under = '', o = '', lab = '';
  const poly = (pts, attr, tag = 'polygon') => `<${tag} points="${ptsAttr(pts.map(p => pr(R(p))))}" ${attr}/>`;
  const txt = (L, s, c, size = 23, op = fade) => `<text x="${f1(L[0])}" y="${f1(L[1])}" text-anchor="middle" dominant-baseline="middle" font-family="Caveat,'Long Cang',cursive" font-weight="700" font-size="${size}" fill="${colOf(c)}" stroke="${PAPER}" stroke-width="3.5" paint-order="stroke" opacity="${f1(op)}">${labelSvg(s)}</text>`;
  const val = (v) => typeof v === 'function' ? v(ctx.a, ctx.P) : v;

  // filled planes / polygons (hatched)
  (sp.planes || []).forEach(pl => {
    const op = (pl.op ?? 1) * fade;
    under += poly(pl.pts, `fill="${colOf(pl.c)}" fill-opacity="${.08 * op}" stroke="none"`);
    under += poly(pl.pts, `fill="${hatch(gid, pl.c)}" fill-opacity="${.55 * op}" stroke="${colOf(pl.c)}" stroke-opacity="${.6 * op}" stroke-width="1.3" stroke-linejoin="round"`);
  });
  // regions between two curves (plane): {f, g?, x:[a,b], c}
  (sp.regions || []).forEach(rg => {
    const [x0, x1] = val(rg.x), top = [], bot = [], N = 80, g = rg.g || (() => 0);
    for (let i = 0; i <= N; i++) { const x = x0 + (x1 - x0) * i / N; top.push(pr([x, rg.f(x, ctx.a)])); bot.push(pr([x, g(x, ctx.a)])); }
    const pts = top.concat(bot.reverse()), op = (rg.op ?? 1) * fade;
    under += `<polygon points="${ptsAttr(pts)}" fill="${colOf(rg.c)}" fill-opacity="${.1 * op}" stroke="none"/><polygon points="${ptsAttr(pts)}" fill="${hatch(gid, rg.c)}" fill-opacity="${.6 * op}" stroke="none"/>`;
  });
  // bars (statistics): {x, h, w?, c, label?}
  (sp.bars || []).forEach((b, i) => {
    const w = b.w ?? .6, h = val(b.h), q = [[b.x - w / 2, 0], [b.x + w / 2, 0], [b.x + w / 2, h], [b.x - w / 2, h]].map(pr), op = (b.op ?? 1) * fade;
    under += `<polygon points="${ptsAttr(q)}" fill="${hatch(gid, b.c || 'blue')}" fill-opacity="${.7 * op}" stroke="${colOf(b.c || 'blue')}" stroke-width="1.6" stroke-opacity="${op}"/>`;
    if (b.label != null) lab += txt(add(pr([b.x, h]), [0, -14]), val(b.label), b.c || 'blue', 20);
  });
  // circles & arcs: {at, r, n?, from?, to?, c, w, dash}
  (sp.circles || []).forEach((cc, i) => {
    const c = R(cc.at), pts = circlePts(c, val(cc.r), cc.n, cc.from ?? 0, cc.to ?? 360).map(pr);
    if (cc.fill) under += `<polygon points="${ptsAttr(pts)}" fill="${hatch(gid, cc.c)}" fill-opacity="${.45 * fade}" stroke="none"/>`;
    o += sketchPath(pts, colOf(cc.c), (cc.w || 1.8), (cc.op ?? 1) * fade, !!cc.dash, !cc.dash);
  });
  // curves: y = f(x) over x:[a,b]; or parametric {xt, yt, t:[a,b]}; or explicit {pts}
  (sp.curves || []).forEach((cv, i) => o += drawCurve(ctx, cv, fade));
  // segments (and the step animation's moving segments)
  const segs = [...(sp.lines || []), ...(!base && sp.anim ? sp.anim(ctx.t, ctx.P, ctx.a) : [])];
  segs.forEach((sg, i) => {
    let A = R(sg.a), B = R(sg.b);
    if (!A || !B) return;
    if (sg.ext && ctx.clip) [A, B] = ctx.clip(A, B);
    if (sg.grow) B = lerp(A, B, ease(Math.min(1, ctx.t / sg.grow)));
    const op = (sg.op ?? 1) * (sg.ghost ? 1 : fade), col = sg.c && sg.c !== 'ink' ? colOf(sg.c) : GRAPHITE, w = (sg.w || 1.5) * .9;
    const a2 = pr(A), b2 = pr(B);
    if (sg.glow) under += `<line x1="${f1(a2[0])}" y1="${f1(a2[1])}" x2="${f1(b2[0])}" y2="${f1(b2[1])}" stroke="${col}" stroke-width="${f1(w * 3.4)}" stroke-opacity="${f1(.13 * op)}" stroke-linecap="round"/>`;
    if (!sg.dash) o += haloLine(a2, b2, w, .7 * op);
    o += sketchLine(a2, b2, col, w, op, 50 + i, !!sg.dash);
    if (sg.arrow) { const d = unit(sub(b2, a2)), n = [-d[1], d[0]], s = 9; o += `<polygon points="${ptsAttr([b2, add(sub(b2, mul(d, s)), mul(n, s * .45)), sub(sub(b2, mul(d, s)), mul(n, s * .45))])}" fill="${col}" opacity="${f1(op)}"/>`; }
  });
  // equal-length tick marks: [p, q, n]
  (sp.ticks || []).forEach(([p, q, n]) => {
    const A = pr(R(p)), B = pr(R(q)), M = mid(A, B), d = unit(sub(B, A)), nrm = [-d[1], d[0]];
    for (let i = 0; i < n; i++) {
      const c = add(M, mul(d, (i - (n - 1) / 2) * 5));
      o += `<line x1="${f1(c[0] - nrm[0] * 6)}" y1="${f1(c[1] - nrm[1] * 6)}" x2="${f1(c[0] + nrm[0] * 6)}" y2="${f1(c[1] + nrm[1] * 6)}" stroke="${GRAPHITE}" stroke-width="1.6" opacity="${f1(fade)}"/>`;
    }
  });
  // right-angle marks: {v, p, q, c}
  (sp.right || []).forEach(rm => {
    const v = R(rm.v), uu = unit(sub(R(rm.p), v)), w = unit(sub(R(rm.q), v)), r = .2 * u;
    o += poly([add(v, mul(uu, r)), add(add(v, mul(uu, r)), mul(w, r)), add(v, mul(w, r))], `fill="none" stroke="${colOf(rm.c || 'ink')}" stroke-width="1.6" opacity="${f1(fade)}"`, 'polyline');
  });
  // angle arcs: {v, p, q, c, label, r}
  (sp.angles || []).forEach(an => {
    const v = R(an.v), uu = unit(sub(R(an.p), v)), w = unit(sub(R(an.q), v)), r = (an.r || .55) * u, pts = [];
    for (let i = 0; i <= 20; i++) pts.push(add(v, mul(unit(lerp(uu, w, i / 20)), r)));
    under += poly([v, ...pts], `fill="${hatch(gid, an.c)}" fill-opacity="${.8 * fade}" stroke="none"`);
    o += poly(pts, `fill="none" stroke="${colOf(an.c)}" stroke-width="2" opacity="${f1(fade)}"`, 'polyline');
    if (an.label != null) lab += txt(pr(add(v, mul(unit(add(uu, w)), r + .42 * u))), val(an.label), an.c, 25);
  });
  // length labels beside a segment: {a, b, t, c, flip}
  (sp.edgeLabels || []).forEach(el => {
    const A = pr(R(el.a)), B = pr(R(el.b)), M = mid(A, B);
    let nrm = (d => [-d[1], d[0]])(unit(sub(B, A)));
    if ((M[0] - cen[0]) * nrm[0] + (M[1] - cen[1]) * nrm[1] < 0) nrm = mul(nrm, -1);
    if (el.flip) nrm = mul(nrm, -1);
    lab += txt(add(M, mul(nrm, 17)), val(el.t), el.c || 'ink', 23);
  });
  // free text: {at, t, c, size, dx, dy}
  (sp.texts || []).forEach(tx => lab += txt(add(pr(R(tx.at)), [tx.dx || 0, tx.dy || 0]), val(tx.t), tx.c || 'ink', tx.size || 22));
  // pulsing highlighted points: {p, c}
  (sp.pts || []).forEach(p => {
    const q = pr(R(p.p));
    if (!q) return;
    o += `<circle cx="${f1(q[0])}" cy="${f1(q[1])}" r="9" fill="${hatch(gid, p.c)}" stroke="${colOf(p.c)}" stroke-width="1.4"><animate attributeName="r" values="9;11.5;9;6.5;9" dur="1.6s" repeatCount="indefinite"/></circle><circle cx="${f1(q[0])}" cy="${f1(q[1])}" r="3.6" fill="${colOf(p.c)}"/>`;
  });
  return {under, o, lab};
}

/* clip a polyline to the view rectangle (Liang–Barsky per segment); returns the visible runs */
function clipRuns(pts, V) {
  if (!V) return [pts];
  const runs = [];
  let cur = [];
  const clipSeg = (A, B) => {
    const d = sub(B, A); let t0 = 0, t1 = 1;
    for (const [i, lo, hi] of [[0, V.x[0], V.x[1]], [1, V.y[0], V.y[1]]]) {
      if (Math.abs(d[i]) < 1e-12) { if (A[i] < lo || A[i] > hi) return null; continue; }
      let ta = (lo - A[i]) / d[i], tb = (hi - A[i]) / d[i];
      if (ta > tb) [ta, tb] = [tb, ta];
      t0 = Math.max(t0, ta); t1 = Math.min(t1, tb);
      if (t0 > t1) return null;
    }
    return [add(A, mul(d, t0)), add(A, mul(d, t1)), t0 > 0, t1 < 1];
  };
  for (let i = 1; i < pts.length; i++) {
    const A = pts[i - 1], B = pts[i];
    if (!A || !B) { if (cur.length > 1) runs.push(cur); cur = []; continue; }
    const c = clipSeg(A, B);
    if (!c) { if (cur.length > 1) runs.push(cur); cur = []; continue; }
    if (c[2] || !cur.length) { if (cur.length > 1) runs.push(cur); cur = [c[0]]; }
    cur.push(c[1]);
    if (c[3]) { runs.push(cur); cur = []; }
  }
  if (cur.length > 1) runs.push(cur);
  return runs;
}

/* a curve on the plane renderer: clipped to the view, broken at asymptotes */
function drawCurve(ctx, cv, fade) {
  const {a} = ctx, pr = ctx.pr, V = ctx.view, N = cv.n || 240, raw = [];
  const ok = p => p && isFinite(p[0]) && isFinite(p[1]);
  if (cv.pts) cv.pts.forEach(k => raw.push(ctx.R(k)));
  else if (cv.f) {
    const [x0, x1] = typeof cv.x === 'function' ? cv.x(a) : (cv.x || (V ? V.x : [-5, 5]));
    let prev = null;
    for (let i = 0; i <= N; i++) {
      const x = x0 + (x1 - x0) * i / N, y = cv.f(x, a);
      if (prev != null && isFinite(y) && V && Math.abs(y - prev) > (V.y[1] - V.y[0]) * 2) raw.push(null);   // jump across an asymptote
      raw.push(isFinite(y) ? [x, y] : null); prev = isFinite(y) ? y : null;
    }
  } else if (cv.xt) {
    const [t0, t1] = typeof cv.t === 'function' ? cv.t(a) : cv.t;
    for (let i = 0; i <= N; i++) { const t = t0 + (t1 - t0) * i / N, p = [cv.xt(t, a), cv.yt(t, a)]; raw.push(ok(p) ? p : null); }
  }
  const runs = clipRuns(raw.map(p => ok(p) ? p : null), cv.noClip ? null : V);
  const col = colOf(cv.c || 'ink'), w = (cv.w || 2.2), op = (cv.op ?? 1) * fade;
  let o = runs.map(r => sketchPath(r.map(pr), col, w, op, !!cv.dash, !cv.dash)).join('');
  if (cv.label) {
    const lx = cv.label.at ?? (cv.f ? null : 0);
    let p = null;
    if (cv.f && lx != null) p = [lx, cv.f(lx, a)];
    else { const r = runs[runs.length - 1]; if (r) p = r[Math.floor(r.length * .85)]; }
    if (p) { const q = add(pr(p), [cv.label.dx ?? 12, cv.label.dy ?? -14]); o += `<text x="${f1(q[0])}" y="${f1(q[1])}" font-family="'EB Garamond',serif" font-style="italic" font-size="${cv.label.size || 20}" fill="${col}" stroke="${PAPER}" stroke-width="3.5" paint-order="stroke" opacity="${f1(op)}">${cv.label.t}</text>`; }
  }
  return o;
}

/* point labels (vertex names) */
function drawLabels(ctx, keys, labelDir) {
  const {pr, P, cen} = ctx;
  let o = '', lab = '';
  keys.forEach(k => {
    if (!P[k]) return;
    const q = pr(P[k]), away = sub(q, cen), d = (labelDir && labelDir[k]) || (len(away) > 8 ? unit(away) : [.6, -.8]);
    const L = add(q, mul(d, 20));
    lab += `<text x="${f1(L[0])}" y="${f1(L[1])}" text-anchor="middle" dominant-baseline="middle" font-family="Caveat,cursive" font-weight="700" font-size="27" fill="${GRAPHITE}" stroke="${PAPER}" stroke-width="4" paint-order="stroke">${labelSvg(k)}</text>`;
  });
  return {o, lab};
}
const dotAt = (pr, p) => { const q = pr(p); return `<circle cx="${f1(q[0])}" cy="${f1(q[1])}" r="3" fill="${GRAPHITE}"/>`; };

/* ======================================================================
   solid renderer
   figure: {type:'solid', model(a) → {A:[x,y,z]…}, faces:[['A','B','C'],…], verts?, round?:[…], extraEdges?:[['A','C']]}
   ====================================================================== */
const SolidR = {
  init(fig) {
    const faces = fig.faces || [];
    const verts = fig.verts || [...new Set(faces.flat())];
    const map = new Map();
    faces.forEach((f, fi) => f.forEach((k, i) => {
      const q = f[(i + 1) % f.length], key = [k, q].sort().join('|');
      if (!map.has(key)) map.set(key, {a: k, b: q, faces: []});
      map.get(key).faces.push(fi);
    }));
    return {faces, verts, edges: [...map.values()], round: fig.round || [], extra: fig.extraEdges || [], vis: {}};
  },
  // outward normal of face i: the body may change shape with the parameter, so it is computed every frame
  normal(S, P, i) {
    const pts = S.faces[i].map(k => P[k]), n = [0, 0, 0];
    pts.forEach((a, j) => { const b = pts[(j + 1) % pts.length];
      n[0] += (a[1] - b[1]) * (a[2] + b[2]); n[1] += (a[2] - b[2]) * (a[0] + b[0]); n[2] += (a[0] - b[0]) * (a[1] + b[1]); });
    return dot(n, sub(centroidOf(pts), centroidOf(S.verts.map(k => P[k])))) < 0 ? mul(n, -1) : n;
  },
  // front/back per face with hysteresis: near edge-on the previous state is kept
  facing(ctx, S) {
    const P = ctx.P, st = S.vis[ctx.gid] || (S.vis[ctx.gid] = []);
    return S.faces.map((f, i) => {
      const fc = centroidOf(f.map(k => P[k])), c = dot(unit(SolidR.normal(S, P, i)), unit(sub(ctx.eye, fc)));
      const v = Math.abs(c) < EDGE_ON && st[i] != null ? st[i] : c > 0;
      if (st[i] != null && st[i] !== v) EMB.flips++;
      return (st[i] = v);
    });
  },
  hullPts(S, P) {
    const pts = S.verts.map(k => P[k]);
    S.round.forEach(b => { const c = typeof b.at === 'string' ? P[b.at] : b.at; roundBox(b, c).forEach(p => pts.push(p)); });
    return pts;
  },
  draw(ctx, S) {
    const {P, pr, gid} = ctx, front = ctx.front;
    const fFront = SolidR.facing(ctx, S);
    let o = '', lab = '';
    // 1. paper fill on front faces (only for the figure standing on the page)
    if (ctx.solid) S.faces.forEach((f, i) => { if (fFront[i]) o += `<polygon points="${ptsAttr(f.map(k => pr(P[k])))}" fill="${PAPER}" fill-opacity=".34" stroke="none"/>`; });
    const marks = drawMarks(ctx, ctx.sp);
    o += marks.under;
    // 2. hidden edges AFTER the fills, so the paper never washes them out
    S.edges.forEach((e, i) => { const vis = e.faces.some(fi => fFront[fi]); if (!vis) o += sketchLine(pr(P[e.a]), pr(P[e.b]), GRAPHITE, 1.5, .72, i, true); });
    // 3. visible edges, each on a paper halo
    S.edges.forEach((e, i) => { const vis = e.faces.some(fi => fFront[fi]); if (vis) { const A = pr(P[e.a]), B = pr(P[e.b]); o += haloLine(A, B, 2.2, .6) + sketchLine(A, B, GRAPHITE, 2.2, .95, i + 20); } });
    S.extra.forEach(([a, b], i) => o += sketchLine(pr(P[a]), pr(P[b]), GRAPHITE, 2, .9, i + 90));
    // 4. round bodies
    S.round.forEach((b, i) => o += drawRound(ctx, b, i));
    o += marks.o; lab += marks.lab;
    const extra = ctx.sp.labels || [];
    extra.forEach(k => { if (P[k]) o += dotAt(pr, P[k]); });
    const L = drawLabels(ctx, [...S.verts, ...(ctx.fig.labels || []), ...extra], {...(ctx.fig.labelDir || {}), ...(ctx.sp.labelDir || {})});
    return {o: o + L.o, lab: lab + L.lab};
  },
};
/* cylinders, cones, frustums (vertical axis) and spheres */
function roundBox(b, c) {
  const r = Math.max(b.r || 0, b.r1 || 0, b.r2 || 0), h = b.h || 0, pts = [];
  if (b.type === 'sphere') { for (const s of [-1, 1]) { pts.push(add(c, [s * r, 0, 0]), add(c, [0, s * r, 0]), add(c, [0, 0, s * r])); } return pts; }
  for (const z of [0, h]) for (let k = 0; k < 8; k++) { const t = k * Math.PI / 4; pts.push(add(c, [r * Math.cos(t), r * Math.sin(t), z])); }
  return pts;
}
function drawRound(ctx, b, seed) {
  const {pr, front, P} = ctx, c = typeof b.at === 'string' ? P[b.at] : b.at, N = 96;
  const runs = (pts, vis, w) => {           // split a closed/open polyline into visible (solid) and hidden (dashed) runs
    let o = '', cur = [pts[0]], cv = vis[0];
    for (let i = 1; i < pts.length; i++) {
      cur.push(pts[i]);
      if (vis[i] !== cv || i === pts.length - 1) { o += cv ? sketchPath(cur.map(pr), GRAPHITE, w, .95, false, true) : sketchPath(cur.map(pr), GRAPHITE, 1.5, .72, true); cur = [pts[i]]; cv = vis[i]; }
    }
    return o;
  };
  let o = '';
  if (b.type === 'sphere') {
    const r = b.r, toEye = unit(sub(ctx.eye, c)), [e1, e2] = basisOf(toEye, 3), sil = [];
    for (let i = 0; i <= N; i++) { const t = 2 * Math.PI * i / N; sil.push(add(c, add(mul(e1, r * Math.cos(t)), mul(e2, r * Math.sin(t))))); }
    o += sketchPath(sil.map(pr), GRAPHITE, 2.2, .95, false, true);
    if (b.equator !== false) { const eq = circlePts(c, r, [0, 0, 1], 0, 360, N); o += runs(eq, eq.map(p => front(sub(p, c), p)), 1.6); }
    return o;
  }
  const h = b.h, r1 = b.type === 'cone' ? b.r : (b.r1 ?? b.r), r2 = b.type === 'cone' ? 0 : (b.r2 ?? b.r), TAU = 2 * Math.PI;
  // side normal at angle t is (h cos t, h sin t, r1 − r2); it faces the eye E when  A cos t + B sin t > Sv.
  // Solving that exactly (instead of sampling) keeps the outline generators steady while the figure turns.
  const E = sub(ctx.eye, c), A = E[0], B = E[1], Sv = r1 - (r1 - r2) * E[2] / h, rho = Math.hypot(A, B);
  const sideFront = t => A * Math.cos(t) + B * Math.sin(t) > Sv;
  const sil = rho > Math.abs(Sv) + 1e-9 ? (ph => [ph - Math.acos(Sv / rho), ph + Math.acos(Sv / rho)])(Math.atan2(B, A)).map(t => ((t % TAU) + TAU) % TAU).sort((x, y) => x - y) : [];
  const botFront = front([0, 0, -1], c), topFront = front([0, 0, 1], add(c, [0, 0, h]));
  const arc = (r, z, t0, t1) => { const n = Math.max(2, Math.ceil((t1 - t0) / TAU * N)), pts = []; for (let i = 0; i <= n; i++) { const t = t0 + (t1 - t0) * i / n; pts.push(add(c, [r * Math.cos(t), r * Math.sin(t), z])); } return pts; };
  const rimArcs = (r, z, capFront) => {
    const cuts = sil.length ? [sil[0], sil[1], sil[0] + TAU] : [0, TAU];
    let out = '';
    for (let i = 0; i + 1 < cuts.length; i++) {
      const vis = capFront || sideFront((cuts[i] + cuts[i + 1]) / 2), pts = arc(r, z, cuts[i], cuts[i + 1]).map(pr);
      out += vis ? sketchPath(pts, GRAPHITE, 2.2, .95, false, true) : sketchPath(pts, GRAPHITE, 1.5, .72, true);
    }
    return out;
  };
  o += rimArcs(r1, 0, botFront);
  if (r2 > 0) o += rimArcs(r2, h, topFront);
  sil.forEach((t, i) => {
    const P1 = pr(add(c, [r1 * Math.cos(t), r1 * Math.sin(t), 0])), P2 = pr(add(c, [r2 * Math.cos(t), r2 * Math.sin(t), h]));
    o += haloLine(P1, P2, 2.2, .6) + sketchLine(P1, P2, GRAPHITE, 2.2, .95, seed * 13 + i);
  });
  if (b.axis) o += sketchLine(pr(c), pr(add(c, [0, 0, h])), GRAPHITE, 1.3, .7, seed + 7, true);
  return o;
}

/* ======================================================================
   plane renderer
   figure: {type:'plane', view:{x:[x0,x1], y:[y0,y1]}, axes?, grid?, model(a) → {A:[x,y]…}, labels?, base?:{marks}}
   Coordinates are scaled to a standard box so marks (angle radius, right-angle size) look the same at any zoom.
   ====================================================================== */
const PlaneR = {
  init(fig) {
    const V = fig.view || {x: [-5, 5], y: [-4, 4]};
    const k = Math.min(4.6 / (V.x[1] - V.x[0]), 3.9 / (V.y[1] - V.y[0]));
    return {V, k, cx: (V.x[0] + V.x[1]) / 2, cy: (V.y[0] + V.y[1]) / 2, hh: (V.y[1] - V.y[0]) * k / 2};
  },
  std(S, p) { return [(p[0] - S.cx) * S.k, (p[1] - S.cy) * S.k]; },
  // clip an infinite line through A, B to the view rectangle
  clip(S, A, B) {
    const V = S.V, d = sub(B, A); let t0 = -1e9, t1 = 1e9;
    for (const [i, lo, hi] of [[0, V.x[0], V.x[1]], [1, V.y[0], V.y[1]]]) {
      if (Math.abs(d[i]) < 1e-12) continue;
      const ta = (lo - A[i]) / d[i], tb = (hi - A[i]) / d[i];
      t0 = Math.max(t0, Math.min(ta, tb)); t1 = Math.min(t1, Math.max(ta, tb));
    }
    return t0 < t1 ? [add(A, mul(d, t0)), add(A, mul(d, t1))] : [A, B];
  },
  hullPts(S) { const V = S.V; return [[V.x[0], V.y[0]], [V.x[1], V.y[0]], [V.x[1], V.y[1]], [V.x[0], V.y[1]]]; },
  draw(ctx, S) {
    const {pr, fig, P} = ctx, V = S.V;
    let o = '', lab = '';
    if (ctx.solid) o += `<polygon points="${ptsAttr(PlaneR.hullPts(S).map(pr))}" fill="${PAPER}" stroke="#d9cfba" stroke-width="1.2"/>`;   // the pop-up card
    // grid & axes
    if (fig.grid !== false && fig.axes !== false) {
      const st = fig.gridStep || niceStep(V);
      for (let x = Math.ceil(V.x[0] / st) * st; x <= V.x[1] + 1e-9; x += st) o += `<line x1="${f1(pr([x, V.y[0]])[0])}" y1="${f1(pr([x, V.y[0]])[1])}" x2="${f1(pr([x, V.y[1]])[0])}" y2="${f1(pr([x, V.y[1]])[1])}" stroke="#9fb3d6" stroke-opacity=".28" stroke-width=".8"/>`;
      for (let y = Math.ceil(V.y[0] / st) * st; y <= V.y[1] + 1e-9; y += st) o += `<line x1="${f1(pr([V.x[0], y])[0])}" y1="${f1(pr([V.x[0], y])[1])}" x2="${f1(pr([V.x[1], y])[0])}" y2="${f1(pr([V.x[1], y])[1])}" stroke="#9fb3d6" stroke-opacity=".28" stroke-width=".8"/>`;
    }
    if (fig.axes !== false) {
      const ax = (A, B, name, side) => {
        const a2 = pr(A), b2 = pr(B), d = unit(sub(b2, a2)), n = [-d[1], d[0]];
        o += sketchLine(a2, b2, GRAPHITE, 1.4, .85, name === 'x' ? 3 : 4);
        o += `<polygon points="${ptsAttr([b2, add(sub(b2, mul(d, 10)), mul(n, 4.5)), sub(sub(b2, mul(d, 10)), mul(n, 4.5))])}" fill="${GRAPHITE}"/>`;
        lab += `<text x="${f1(b2[0] + side[0])}" y="${f1(b2[1] + side[1])}" font-family="'EB Garamond',serif" font-style="italic" font-size="20" fill="${GRAPHITE}">${name}</text>`;
      };
      const y0 = Math.min(Math.max(0, V.y[0]), V.y[1]), x0 = Math.min(Math.max(0, V.x[0]), V.x[1]);
      ax([V.x[0], y0], [V.x[1], y0], fig.xLabel || 'x', [-6, 20]);
      ax([x0, V.y[0]], [x0, V.y[1]], fig.yLabel || 'y', [10, 6]);
      if (fig.tickLabels !== false) {
        const st = fig.tickStep || niceStep(V), num = v => (Math.abs(v) < 1e-9 ? '' : +v.toFixed(2));
        for (let x = Math.ceil(V.x[0] / st) * st; x <= V.x[1] - st * .5; x += st) if (Math.abs(x - x0) > 1e-9) { const q = pr([x, y0]); lab += `<text x="${f1(q[0])}" y="${f1(q[1] + 16)}" text-anchor="middle" font-family="'EB Garamond',serif" font-size="14" fill="#8a8172">${num(x)}</text><line x1="${f1(q[0])}" y1="${f1(q[1] - 3)}" x2="${f1(q[0])}" y2="${f1(q[1] + 3)}" stroke="${GRAPHITE}" stroke-width="1"/>`; }
        for (let y = Math.ceil(V.y[0] / st) * st; y <= V.y[1] - st * .5; y += st) if (Math.abs(y - y0) > 1e-9) { const q = pr([x0, y]); lab += `<text x="${f1(q[0] - 7)}" y="${f1(q[1] + 5)}" text-anchor="end" font-family="'EB Garamond',serif" font-size="14" fill="#8a8172">${num(y)}</text><line x1="${f1(q[0] - 3)}" y1="${f1(q[1])}" x2="${f1(q[0] + 3)}" y2="${f1(q[1])}" stroke="${GRAPHITE}" stroke-width="1"/>`; }
        const q = pr([x0, y0]); if (V.x[0] < 0 && V.y[0] < 0) lab += `<text x="${f1(q[0] - 8)}" y="${f1(q[1] + 17)}" text-anchor="middle" font-family="'EB Garamond',serif" font-style="italic" font-size="15" fill="#8a8172">O</text>`;
      }
    }
    // the figure's permanent content, then the step's highlights
    const base = drawMarks(ctx, fig.base || {}, true), marks = drawMarks(ctx, ctx.sp);
    o += base.under + marks.under + base.o + marks.o; lab += base.lab + marks.lab;
    // guide drops to the axes: {p, c}
    (ctx.sp.drops || []).forEach(dp => {
      const p = ctx.R(dp.p), c = colOf(dp.c || 'ink'), y0 = Math.min(Math.max(0, V.y[0]), V.y[1]), x0 = Math.min(Math.max(0, V.x[0]), V.x[1]);
      o += sketchLine(pr(p), pr([p[0], y0]), c, 1.3, .8 * ctx.fade, 5, true) + sketchLine(pr(p), pr([x0, p[1]]), c, 1.3, .8 * ctx.fade, 6, true);
    });
    const keys = [...(fig.labels || []), ...(ctx.sp.labels || [])];
    keys.forEach(k => { if (P[k]) o += dotAt(pr, P[k]); });
    const L = drawLabels(ctx, keys, {...(fig.labelDir || {}), ...(ctx.sp.labelDir || {})});
    return {o: o + L.o, lab: lab + L.lab};
  },
};
function niceStep(V) {
  const span = Math.max(V.x[1] - V.x[0], V.y[1] - V.y[0]), raw = span / 9, p = Math.pow(10, Math.floor(Math.log10(raw)));
  return [1, 2, 5, 10].map(m => m * p).find(s => s >= raw) || raw;
}

/* ======================================================================
   figures: shared parameter animation; the flat one printed on the page, the pop one standing in 3D
   ====================================================================== */
const FIG = LESSON.figure || {type: 'none'};
const RD = FIG.type === 'solid' ? SolidR : FIG.type === 'plane' ? PlaneR : null;
const RS = RD ? RD.init(FIG) : null;
const DEF_A = FIG.param ? FIG.param.def : 0;
const modelAt = a => (FIG.model ? FIG.model(a) : {}) || {};
const resolver = (P, a) => k => typeof k === 'string' ? P[k] : typeof k === 'function' ? k(P, a) : k;

// scale so the body fills the page figure the same way the original prism did;
// when the parameter makes the body grow past 105 % of its default size, shrink it back so it stays on the page
const bodyR = P => { const pts = RD.hullPts(RS, P), c = centroidOf(pts); return Math.max(...pts.map(p => dist(p, c))) || 1; };
const R0 = FIG.type === 'solid' ? bodyR(modelAt(DEF_A)) : 1;
const SCALE0 = FIG.type === 'solid' ? Math.min(1.6, 1.85 / R0) * (FIG.scale || 1) : 1;
const scaleAt = P => FIG.type === 'solid' ? SCALE0 * Math.min(1, 1.05 * R0 / bodyR(P)) : 1;

class Figure {
  constructor() { this.a = DEF_A; this.aT = DEF_A; this.spec = {}; this.t0 = 0; this.good = ''; }
  // same spec again (e.g. hovering back and forth on the left page) must not restart the fade-in
  set(spec) { spec = spec || {}; if (spec === this.spec) return; this.spec = spec; this.t0 = performance.now() / 1000; this.aT = spec.a ?? DEF_A; }
  render(...args) {
    try { return (this.good = this._render(...args)); }
    catch (e) {
      EMB.errors++;
      if (EMB.lastError !== e.message) { EMB.lastError = e.message; console.error('[render] ' + e.message + (window.__embStep ? ' @ ' + window.__embStep : '')); }
      return this.good;
    }
  }
  tick() { this.a += (this.aT - this.a) * 0.12; }
  ctx(P, pr, extra) {
    return Object.assign({P, a: this.a, sp: this.spec, pr, R: resolver(P, this.a), t: performance.now() / 1000 - this.t0, fig: FIG, u: 1}, extra);
  }
}

class FlatFigure extends Figure {
  constructor(svg) {
    super();
    Object.assign(this, {svg, W: 560, H: 490, S: 112, oy: -10, yaw: FIG.flatYaw ?? -2.2, pitch: FIG.flatPitch ?? .34});
    svg.setAttribute('viewBox', `0 0 ${this.W} ${this.H}`);
    if (FIG.type !== 'solid') return;
    let drag = null;
    svg.addEventListener('pointerdown', e => { drag = [e.clientX, e.clientY]; svg.setPointerCapture(e.pointerId); svg.classList.add('grab'); });
    svg.addEventListener('pointermove', e => {
      if (!drag) return;
      this.yaw -= (e.clientX - drag[0]) * 0.009;
      this.pitch = Math.max(-.15, Math.min(1.35, this.pitch + (e.clientY - drag[1]) * 0.007));
      drag = [e.clientX, e.clientY];
    });
    const up = () => { drag = null; svg.classList.remove('grab'); };
    svg.addEventListener('pointerup', up); svg.addEventListener('pointercancel', up);
    svg.addEventListener('dblclick', () => { this.yaw = FIG.flatYaw ?? -2.2; this.pitch = FIG.flatPitch ?? .34; });
  }
  _render(now) {
    this.tick();
    if (!RD) return '';
    const a = this.a, P = modelAt(a), {W, H} = this;
    let pr, extra = {now, gid: 'glf', solid: false, mode: 'flat'};
    if (FIG.type === 'solid') {
      const yaw = this.yaw, cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(this.pitch), spn = Math.sin(this.pitch);
      const pts = RD.hullPts(RS, P), lo = pts[0].map((_, i) => Math.min(...pts.map(p => p[i]))), hi = pts[0].map((_, i) => Math.max(...pts.map(p => p[i])));
      const ctr = mid(lo, hi), S = this.S * scaleAt(P);
      pr = p => {
        const x = p[0] - ctr[0], y = p[1] - ctr[1], z = p[2] - ctr[2];
        const x1 = x * cy - y * sy, y1 = x * sy + y * cy;
        const d = y1 * cp - z * spn, u = y1 * spn + z * cp, k = 9 / (9 + d);
        return [W / 2 + x1 * S * k, H / 2 + this.oy - u * S * k];
      };
      const eye = add(ctr, [-9 * cp * sy, -9 * cp * cy, 9 * spn]);       // the camera point that pr() looks from
      extra.eye = eye; extra.front = (n, p) => dot(n, sub(eye, p)) > 0;
    } else {
      pr = p => { const q = RD.std(RS, p); return [W / 2 + q[0] * this.S, H / 2 + this.oy - q[1] * this.S]; };
      extra.u = 1 / RS.k; extra.view = RS.V; extra.clip = (A, B) => RD.clip(RS, A, B);
    }
    const ctx = this.ctx(P, pr, extra);
    ctx.fade = Math.min(1, ctx.t / .6);
    const hp = RD.hullPts(RS, P).map(pr); ctx.cen = centroidOf(hp);
    const d = RD.draw(ctx, RS);
    return `<defs>${sketchDefs('glf')}</defs><g filter="url(#glf-pencil)">${d.o}</g>${d.lab}`;
  }
}

/* The figure standing on the page in true 3D: projected through the same matrices as the CSS scene */
const PAGE_ANCHOR = [165, -160, 16];   // right page, where the printed figure sits (world px; z = page surface)
const UNIT = 120;                       // px per model unit
const CARD_LEAN = rad(18);              // plane figures stand like a pop-up card leaning back a little
class PopFigure extends Figure {
  constructor(svg) {
    super();
    const y0 = FIG.yaw ?? 128;
    Object.assign(this, {svg, yaw: FIG.type === 'solid' ? y0 : 0, yawT: FIG.type === 'solid' ? y0 : 0, g: 0, drag: null});
    if (FIG.type !== 'solid') return;
    svg.addEventListener('pointerdown', e => { if (e.target.classList.contains('hit')) { this.drag = e.clientX; e.preventDefault(); } });
    addEventListener('pointermove', e => { if (this.drag != null) { this.yaw -= (e.clientX - this.drag) * 0.45; this.yawT = this.yaw; this.drag = e.clientX; } });
    addEventListener('pointerup', () => this.drag = null);
  }
  // each step can name the yaw that shows it best; turn there along the shortest way round
  set(spec) { super.set(spec); if (FIG.type === 'solid' && this.spec.view != null) this.yawT = this.yaw + ((((this.spec.view - this.yaw) % 360) + 540) % 360 - 180); }
  // model point → the 3D point that gets projected (plane points are lifted onto the standing card)
  lift(p) {
    if (FIG.type === 'solid') return p;
    const q = RD.std(RS, p), h = q[1] + RS.hh;
    return [q[0], Math.sin(CARD_LEAN) * h, Math.cos(CARD_LEAN) * h];
  }
  _render(now, world) {
    if (this.drag == null) this.yaw += (this.yawT - this.yaw) * .05;
    this.tick();
    if (this.g < .002 || !RD) return '';
    const a = this.a, P = modelAt(a), g = this.g;
    const hp3 = RD.hullPts(RS, P).map(p => this.lift(p));
    const S = FIG.type === 'solid' ? UNIT * .95 * scaleAt(P) : UNIT * .74, c0 = FIG.type === 'solid' ? centroidOf(hp3) : [0, 0, 0];
    const local = new DOMMatrix().translate(...PAGE_ANCHOR).rotate(0, 0, this.yaw)
      .scale(S, -S, S * Math.max(g, .02)).translate(-c0[0], -c0[1], 0);
    const toView = world.view.multiply(local), full = world.persp.multiply(toView);
    const proj = p => { const q = full.transformPoint(new DOMPoint(p[0], p[1], p[2] || 0, 1)); return [q.x / q.w, q.y / q.w]; };
    const pr = p => proj(this.lift(p));
    const eyeP = toView.inverse().transformPoint(new DOMPoint(world.eye[0], world.eye[1], world.eye[2], 1));
    const E = [eyeP.x / eyeP.w, eyeP.y / eyeP.w, eyeP.z / eyeP.w];
    const extra = {now, gid: 'glp', solid: true, mode: 'pop', eye: E, front: (n, p) => dot(n, sub(E, p)) > 0};
    if (FIG.type === 'plane') { extra.u = 1 / RS.k; extra.view = RS.V; extra.clip = (A, B) => RD.clip(RS, A, B); }
    const ctx = this.ctx(P, pr, extra);
    ctx.fade = Math.min(1, ctx.t / .6);
    ctx.cen = centroidOf(hp3.map(proj));

    // contact shadow: fixed light in world space, converted into the model's rotated frame
    const yr = this.yaw * Math.PI / 180, L = [.42, .30];
    const Lm = [L[0] * Math.cos(yr) + L[1] * Math.sin(yr), -(-L[0] * Math.sin(yr) + L[1] * Math.cos(yr))];
    const sh = hp3.map(p => { const h = p[2] * g; return proj([p[0] + h * Lm[0], p[1] + h * Lm[1], 0]); });
    const hull = ptsAttr(hull2d(sh)), hit = ptsAttr(hull2d(hp3.map(proj)));
    const op = clamp01(g * 1.5), d = RD.draw(ctx, RS);
    return `<defs>${sketchDefs('glp')}</defs>
      <g opacity="${op}"><polygon points="${hull}" fill="#2a2418" fill-opacity=".16" filter="url(#glp-blur)"/>
      <g>${d.o}</g>${d.lab}
      ${this.drawHover(P, pr, now)}${this.drawTag(P, a, pr, now, ctx.cen)}</g>
      <polygon class="hit" points="${hit}" fill="transparent"/>`;
  }
  // emphasise the element named by the hovered symbol on the sheet (a point, an edge or a face)
  drawHover(P, pr, now) {
    const hv = this.hover;
    if (!hv) return '';
    const pts = hv.pts.map(k => P[k]).filter(Boolean).map(pr), col = colOf(hv.c) || COL.violet;
    if (!pts.length) return '';
    const xy = ptsAttr(pts), blink = '<animate attributeName="opacity" values="1;.45;1" dur="1.05s" repeatCount="indefinite"/>';
    if (pts.length === 1) return `<circle cx="${f1(pts[0][0])}" cy="${f1(pts[0][1])}" r="14" fill="${col}" fill-opacity=".25" stroke="${col}" stroke-width="2">${blink}</circle>`;
    if (pts.length === 2) return `<g>${blink}<polyline points="${xy}" stroke="${col}" stroke-width="12" stroke-opacity=".22" stroke-linecap="round" fill="none"/><polyline points="${xy}" stroke="${col}" stroke-width="3.5" stroke-linecap="round" fill="none"/></g>`;
    return `<polygon points="${xy}" fill="${hatch('glp', hv.c)}" stroke="${col}" stroke-width="2.5" stroke-linejoin="round">${blink}</polygon>`;
  }
  // a small printed label pinned to the figure by a leader line
  drawTag(P, a, pr, now, cen) {
    const T = this.spec.tag;
    if (!T) return '';
    const op = clamp01((now - this.t0 - .9) / .5);
    if (op <= 0) return '';
    const R = resolver(P, a), at = Array.isArray(T.at) && typeof T.at[0] === 'string' ? mid(R(T.at[0]), R(T.at[1])) : R(T.at);
    if (!at) return '';
    const q = pr(at), raw = typeof T.text === 'function' ? T.text(a) : T.text, col = colOf(T.c || 'ink');
    const txt = raw.replace(/₁/g, '<tspan baseline-shift="sub" font-size="68%" font-style="normal">1</tspan>');
    const side = q[0] >= cen[0] ? 1 : -1, w = [...raw].reduce((s, ch) => s + (/[^\x00-\xff]/.test(ch) ? 20 : 11), 0) + 28, h = 32;
    const bx = q[0] + side * 58 + (side < 0 ? -w : 0), by = q[1] - 80;
    const ex = side > 0 ? bx : bx + w;
    return `<g opacity="${op}">
      <polyline points="${f1(q[0])},${f1(q[1])} ${f1(q[0] + side * 30)},${f1(by + h / 2)} ${f1(ex)},${f1(by + h / 2)}" fill="none" stroke="${col}" stroke-width="1.3"/>
      <circle cx="${f1(q[0])}" cy="${f1(q[1])}" r="3.5" fill="${PAPER}" stroke="${col}" stroke-width="1.6"/>
      <rect x="${f1(bx + 2)}" y="${f1(by + 3)}" width="${w}" height="${h}" rx="2" fill="rgba(40,30,10,.16)"/>
      <rect x="${f1(bx)}" y="${f1(by)}" width="${w}" height="${h}" rx="2" fill="#fffdf7" stroke="${GRAPHITE}" stroke-opacity=".6" stroke-width="1" transform="rotate(-1.5 ${f1(bx)} ${f1(by)})"/>
      <text x="${f1(bx + w / 2)}" y="${f1(by + h / 2 + 1)}" text-anchor="middle" dominant-baseline="middle" font-family="Caveat,'Long Cang',cursive" font-weight="700" font-size="21" fill="${col}">${txt}</text></g>`;
  }
}
