/* ======================================================================
   scene.js — builds the book pages from LESSON and runs the desk scene
   ====================================================================== */
const $ = id => document.getElementById(id);
const L = LESSON, PARTS = L.parts || [];
const INTRO_ON = !!$('introUi');                 // generate.py strips the intro markup when the lesson has intro:false

/* ---------- lesson lint (check.mjs collects every "[lesson]" warning; most of these are flicker causes) ---------- */
(function validateLesson() {
  const warn = m => console.warn('[lesson] ' + m);
  const steps = [];
  PARTS.forEach((p, i) => (p.steps || []).forEach((s, j) => steps.push({s, at: `parts[${i}].steps[${j}]`})));
  ['title', 'stem'].forEach(k => { if (!L[k]) warn(`missing "${k}"`); });
  if (!PARTS.length) warn('no parts');
  PARTS.forEach((p, i) => { if (!p.q) warn(`parts[${i}].q missing`); if (!p.steps || !p.steps.length) warn(`parts[${i}] has no steps`); });
  steps.forEach(({s, at}) => {
    if (!s.h) warn(`${at}.h missing`);
    if (!Array.isArray(s.chain)) warn(`${at}.chain must be an array of [text, reason]`);
    else if (s.chain.length > 5) warn(`${at}.chain has ${s.chain.length} lines — split it into two steps (the sheet gets cramped)`);
    const sp = s.spec || {};
    if (sp.slider && !FIG.param) warn(`${at} uses slider but figure.param is missing`);
    if (sp.a != null && FIG.param && (sp.a < FIG.param.min || sp.a > FIG.param.max)) warn(`${at}.spec.a = ${sp.a} is outside param [${FIG.param.min}, ${FIG.param.max}]`);
    if (sp.anim && typeof sp.anim !== 'function') warn(`${at}.spec.anim must be a function (t, P, a) => [segments]`);
  });
  if (L.predict && !(L.predict.options && L.predict.options[L.predict.answer] != null)) warn('predict.answer must be an index into predict.options');

  // KaTeX syntax: a broken formula renders as red source text
  const texts = [];
  const walk = (v, path) => { if (typeof v === 'string') texts.push([v, path]); else if (Array.isArray(v)) v.forEach((x, i) => walk(x, path + '[' + i + ']')); else if (v && typeof v === 'object') Object.entries(v).forEach(([k, x]) => walk(x, path + '.' + k)); };
  walk(L, 'LESSON');
  if (window.katex) texts.forEach(([t, path]) => { for (const m of t.matchAll(/\\\((.+?)\\\)/g)) { try { katex.renderToString(m[1], {throwOnError: true}); } catch (e) { warn(`KaTeX error in ${path}: ${e.message.split('\n')[0]}`); } } });
  texts.forEach(([t, path]) => { if (/[\f\v\t\r\x08]/.test(t)) warn(`${path} contains a control character — a KaTeX string probably lost its backslashes (use String.raw\`…\`)`); });

  if (FIG.type !== 'solid' && FIG.type !== 'plane') return;
  const dim = FIG.type === 'solid' ? 3 : 2;
  // model(): deterministic, finite, continuous in the parameter, cheap
  let P0;
  try { P0 = modelAt(DEF_A); } catch (e) { warn('model() throws: ' + e.message); return; }
  if (JSON.stringify(P0) !== JSON.stringify(modelAt(DEF_A))) warn('model() returns different points for the same parameter (Math.random / Date?) — the figure will flicker');
  const bad = P => Object.entries(P).filter(([k, v]) => !Array.isArray(v) || v.length !== dim || v.some(x => !isFinite(x))).map(([k]) => k);
  const b0 = bad(P0); if (b0.length) warn(`model() points must be finite ${dim}D arrays: ${b0.join(', ')}`);
  const pts0 = Object.values(P0).filter(v => Array.isArray(v) && v.every(isFinite));
  const size = pts0.length ? Math.max(...pts0.map(p => dist(p, centroidOf(pts0)))) || 1 : 1;
  if (FIG.param) {
    const {min, max} = FIG.param, n = 60;
    let prev = null;
    for (let i = 0; i <= n; i++) {
      const a = min + (max - min) * i / n;
      let P; try { P = modelAt(a); } catch (e) { warn(`model(${fix(a)}) throws: ${e.message}`); break; }
      const bb = bad(P); if (bb.length) { warn(`model(${fix(a)}) gives non-finite points: ${bb.join(', ')} — clamp param.min/max`); break; }
      if (prev) { const jump = Math.max(...Object.keys(P).filter(k => prev[k]).map(k => dist(P[k], prev[k]))); if (jump > size * .5) { warn(`model() jumps between a=${fix(prev.a)} and a=${fix(a)} (a point moves ${fix(jump)}) — the slider will make the figure flash`); break; } }
      prev = Object.assign({}, P, {a});
    }
  }
  const t0 = performance.now(); for (let i = 0; i < 200; i++) modelAt(DEF_A);
  const ms = (performance.now() - t0) / 200; if (ms > .3) warn(`model() takes ${ms.toFixed(2)} ms per call — it runs every frame for two figures; precompute constants outside it`);

  // every named point used anywhere must exist
  const need = new Map(), use = (x, at) => { if (typeof x === 'string') need.set(x, need.get(x) || at); };
  const scan = (sp, at) => { if (!sp) return;
    (sp.lines || []).forEach(l => { use(l.a, at); use(l.b, at); });
    (sp.planes || []).forEach(pl => (pl.pts || []).forEach(x => use(x, at)));
    (sp.angles || []).concat(sp.right || []).forEach(m => ['v', 'p', 'q'].forEach(k => use(m[k], at)));
    (sp.ticks || []).forEach(([p, q]) => { use(p, at); use(q, at); });
    (sp.edgeLabels || []).forEach(m => { use(m.a, at); use(m.b, at); });
    (sp.pts || []).forEach(m => use(m.p, at)); (sp.labels || []).forEach(x => use(x, at));
    (sp.texts || []).concat(sp.circles || []).forEach(m => use(m.at, at)); (sp.drops || []).forEach(m => use(m.p, at));
    if (sp.tag) [].concat(sp.tag.at).forEach(x => use(x, at));
    // functions inside a spec must be deterministic too
    ['angles', 'edgeLabels', 'texts'].forEach(k => (sp[k] || []).forEach(m => { const f = m.label ?? m.t; if (typeof f === 'function' && String(f(DEF_A, P0)) !== String(f(DEF_A, P0))) warn(`${at}.${k}: label function is not deterministic`); }));
  };
  steps.forEach(({s, at}) => scan(s.spec, at)); scan(FIG.baseSpec, 'figure.baseSpec'); scan(FIG.base, 'figure.base');
  (FIG.faces || []).flat().forEach(x => use(x, 'figure.faces')); (FIG.labels || []).forEach(x => use(x, 'figure.labels'));
  (FIG.round || []).forEach(b => use(b.at, 'figure.round'));
  need.forEach((at, k) => { if (!P0[k]) warn(`point "${k}" (used in ${at}) is not returned by model()`); });

  // solid faces: ≥ 3 distinct points, planar, and the body convex (hidden lines rely on it)
  if (FIG.type === 'solid' && FIG.faces) {
    const vs = [...new Set(FIG.faces.flat())].map(k => P0[k]).filter(Boolean);
    FIG.faces.forEach((f, i) => {
      const pts = f.map(k => P0[k]); if (pts.some(x => !x)) return;
      if (new Set(f).size < 3) { warn(`figure.faces[${i}] needs at least 3 different points`); return; }
      const n = [0, 0, 0]; pts.forEach((a, j) => { const b = pts[(j + 1) % pts.length]; n[0] += (a[1] - b[1]) * (a[2] + b[2]); n[1] += (a[2] - b[2]) * (a[0] + b[0]); n[2] += (a[0] - b[0]) * (a[1] + b[1]); });
      if (len(n) < 1e-9 * size * size) { warn(`figure.faces[${i}] (${f.join('')}) is degenerate (collinear points)`); return; }
      const u = unit(n), c = centroidOf(pts);
      const off = Math.max(...pts.map(p => Math.abs(dot(sub(p, c), u))));
      if (off > 1e-3 * size) warn(`figure.faces[${i}] (${f.join('')}) is not planar (off by ${fix(off, 3)}) — split it into triangles`);
      const side = vs.map(p => dot(sub(p, c), u)).filter(d => Math.abs(d) > 1e-3 * size);
      if (side.some(d => d > 0) && side.some(d => d < 0)) warn(`figure.faces[${i}] (${f.join('')}) has body points on both sides — the body is not convex or this is not an outer face; hidden lines will be wrong`);
    });
    const ec = new Map(); FIG.faces.forEach(f => f.forEach((k, i) => { const key = [k, f[(i + 1) % f.length]].sort().join('-'); ec.set(key, (ec.get(key) || 0) + 1); }));
    const open = [...ec].filter(([, n]) => n !== 2).map(([k]) => k);
    if (open.length && !(FIG.round || []).length) warn(`edges ${open.join(', ')} do not belong to exactly two faces — the body is not closed (missing a face?)`);
  }
})();

/* ---------- pages ---------- */
document.title = L.pageTitle || `${L.topic || '数学'} · 第${L.no ?? ''}题`;
$('topbarL').innerHTML = L.topbar || `<b>互动试卷</b> · ${L.topic || '数学'}专题`;
if (FIG.type !== 'solid') $('topbarR').textContent = FIG.param ? '点击题号看演示 · 拖动滑块 · Esc 收起' : '点击题号看演示 · ← → 翻步 · Esc 收起';
document.body.classList.add('fig-' + (FIG.type || 'none'));
const PROPS_TEXT = {clock: L.props?.clock || `${(L.topicEn || 'MATH').toUpperCase()} · ${L.no ?? ''}`, sticky: L.props?.sticky || `第${L.no ?? ''}题<br>先猜，再算 ✓`};

(function buildPages() {
  const pr = L.predict;
  const q = PARTS.map((p, i) => `<div class="q part" data-part="${i}"><span class="n">(${i + 1})</span><span><span class="t">${fmt(p.q)}</span></span><span class="lead"></span><span class="go">看演示 <b>↗</b></span></div>`).join('');
  $('leftPage').innerHTML = `<div class="fit">
    <div class="rh"><span>${L.chapter || ''}</span><span>${L.chapterEn || ''}</span></div>
    <div class="eyebrow">Problem ${L.no ?? ''}${L.score ? ' · ' + L.score : ''}</div>
    <h1>${L.title || ''}</h1>
    ${L.subtitle ? `<div class="sub">${L.subtitle}</div>` : ''}
    <div class="stem"><span class="no">${L.no ?? ''}</span>${fmt(L.stem)}</div>
    ${L.key ? `<div class="keyrow"><div class="scribble">${L.key.scribble || ''}</div><div class="keybox"><div class="f">${fmt(L.key.formula)}</div><div class="c">${fmt(L.key.caption)}</div></div></div>` : ''}
    ${L.keywords && L.keywords.length ? `<div class="lbl">Key words · 关键词</div><dl class="kw">${L.keywords.map(([t, d]) => `<dt>${fmt(t)}</dt><dd>${fmt(d)}</dd>`).join('')}</dl>` : ''}
    <div class="lbl">Questions · 设问</div>${q}
    ${pr ? `<div class="lbl">Predict · 先猜</div><div class="pq">${fmt(pr.q)}</div>
    <div class="opts">${pr.options.map((o, i) => `<button class="opt" data-v="${i}"><i></i><span>${fmt(o)}</span></button>`).join('')}</div>
    <div class="flaprow">
      <div class="flap" id="flap">
        <div class="flap-in"><div class="tagline">Answer</div><span class="big"${pr.bigSize ? ` style="font-size:${pr.bigSize}px"` : ''}>${fmt(pr.big ?? pr.options[pr.answer])}</span>
          <span id="verdict"></span><br>${fmt(pr.explain || '')}<br>
          <button id="flapGo">看完整演示 →</button></div>
        <div class="flap-shadow" id="flapShadow"></div>
        <div class="seg s1" id="seg1">
          <div class="face f"><div class="why">WHY ?</div><div class="ft">掀开纸片看答案</div></div>
          <div class="face b"></div>
          <div class="seg s2">
            <div class="face f"><div class="fs">……最好先做出你的预测，再往上掀</div><div class="corner"></div></div>
            <div class="face b"></div>
          </div>
        </div>
        <div class="tape"></div>
      </div>
      ${pr.challenge ? `<div class="challenge"><div class="lbl">Challenge</div>${fmt(pr.challenge)}</div>` : ''}
    </div>` : ''}
  </div><div class="folio">${L.folio ?? 30}</div>`;

  const lg = (L.legend || []).map(it => it.kind === 'plane'
    ? `<span class="pl" style="background:${colOf(it.c)}33;border-color:${colOf(it.c)}"></span>${fmt(it.t)}`
    : `<span class="sw" style="background:${colOf(it.c)}"></span>${fmt(it.t)}`).join('<br>');
  const methods = L.methods || [];
  $('rightPage').innerHTML = `<div class="spacer"></div>
    <div class="cap"><span><span class="fig">Fig. ${L.no ?? ''}</span><span>${fmt(FIG.caption || '')}</span></span>
      ${methods.length ? `<span class="method">method${methods.map((m, i) => `<span class="${i ? '' : 'on'}">${m}</span>`).join('')}</span>` : ''}</div>
    <div class="cap-main">${fmt(L.capMain || (FIG.type === 'none' ? '点“看演示”，跟着草稿纸一步步推。' : '点“看演示”，图形会从纸上立起来。'))}</div>
    <div class="tags">${L.given ? `<div class="tag"><b>Given · 已知</b>${fmt(L.given)}</div>` : ''}${lg ? `<div class="tag"><b>Legend · 图例</b>${lg}</div>` : ''}</div>
    <div class="folio">${(L.folio ?? 30) + 1}</div>`;

  if (FIG.type === 'none' || !RD) {
    $('flat').style.display = 'none';
    const fb = $('fboard'); fb.hidden = false;
    fb.innerHTML = (FIG.board || []).map(l => typeof l === 'string' ? `<div class="fl">${fmt(l)}</div>` : `<div class="fl${l.k ? ' k' : ''}${l.note ? ' note' : ''}">${fmt(l.t)}</div>`).join('');
  }
  // a long problem is scaled down as a whole rather than spilling off the page
  const fit = () => {
    const el = document.querySelector('#leftPage .fit'), avail = 812 - 26 - 46;
    el.style.transform = ''; el.style.width = '';
    const h = el.scrollHeight;
    if (h > avail) { const s = Math.max(.72, avail / h); el.style.transform = `scale(${s.toFixed(3)})`; el.style.width = (100 / s).toFixed(2) + '%'; }
  };
  fit(); document.fonts && document.fonts.ready.then(fit);
})();

Object.entries({Mug: buildMug, Eraser: buildEraser, Sticky: buildSticky, Clock: buildClock}).forEach(([k, build]) => build($('p' + k)));
buildClipboard($('board'));
buildPen($('penAx'));

/* ---------- the classmate: her keyed video stands on the classroom floor (intro only) ---------- */
const CM = 30, DESK_Z = 75;
const GIRL = {x: -30, y: -62, w: 106, h: 188};            // her video frame; feet sit at 92% of its height
const DESK = {x0: -1800, x1: 1800, y0: -1100, y1: 850};     // the reader's desk top in world px (120 × 65 cm)
const roomToWorld = ([x, y, z]) => [x * CM, y * CM, (z - DESK_Z) * CM - 3];
Object.assign(window, {CM, DESK_Z, GIRL, DESK});      // read by the WebGL classroom module
function plane(parent, o, u, v, w, h, css = '') {
  const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
  return mk(parent, `width:${w}px;height:${h}px;transform:matrix3d(${[...u, 0, ...v, 0, ...n, 0, ...o, 1].join(',')});${css}`);
}
const girlPlane = INTRO_ON ? (host => {
  host.style.transform = `translateZ(${-DESK_Z * CM - 3}px) scale3d(${CM},${CM},${CM})`;
  const g = plane(host, [GIRL.x - GIRL.w / 2, GIRL.y, GIRL.h * .92], [1, 0, 0], [0, 0, -1], GIRL.w, GIRL.h);
  g.className = 'f3 girl3';
  g.innerHTML = '<video id="girlV" playsinline preload="auto"></video>';
  return g;
})($('room')) : null;
const BOARD = window.BOARD = {lines: L.intro?.board || [[`第${L.no ?? ''}题 · ${L.title || ''}`, 18], ...PARTS.slice(0, 3).map((p, i) => [`(${i + 1}) ` + String(p.q).replace(/\\\(|\\\)|\$/g, ''), 12])], duty: L.intro?.duty};

/* ---------- figures ---------- */
const BASE = FIG.baseSpec || {};
const flat = new FlatFigure($('flat'));
const pop = new PopFigure($('pop'));
flat.set(BASE);
const HOVER = PARTS.map(p => (p.steps[p.hover ?? p.steps.length - 1] || {}).spec);
const demo = () => document.body.classList.contains('demo');
document.querySelectorAll('.part').forEach(el => {
  const i = +el.dataset.part;
  el.addEventListener('mouseenter', () => { if (!demo()) flat.set(HOVER[i]); });
  el.addEventListener('mouseleave', () => { if (!demo()) flat.set(BASE); });
  el.addEventListener('click', () => openDemo(i, 0));
});
// a chalk copy of the printed figure for the classroom blackboard
if (INTRO_ON && RD) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 490"><style>line,path,polyline,polygon,circle{stroke:#f4f4ea !important;fill:none !important}text{fill:#f4f4ea !important;stroke:none !important;font-family:cursive}</style>${flat.render(1e9)}</svg>`;
  window.boardImg = new Image();
  boardImg.onload = () => window.boardReady?.();
  boardImg.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
}

/* ---------- demo mode ---------- */
const slider = $('slider'), range = $('range'), PARAM = FIG.param;
if (PARAM) Object.assign(range, {min: PARAM.min, max: PARAM.max, step: PARAM.step ?? (PARAM.max - PARAM.min) / 200, value: PARAM.def});
$('sliderL').innerHTML = PARAM ? `${fmt(PARAM.label || '拖动参数')}：<b id="bcv"></b>` : '';
if (FIG.type === 'none') $('shHint').textContent = '每一步写完后，可以展开“规范作答”';
let cur = {p: 0, s: 0};

/* $AB$ → coloured symbol; symbols made of point names become hover targets on the figure. \(…\) → KaTeX (one glyph for the pen) */
function fmtC(str, cmap = {}) {
  return String(str ?? '').replace(/₁/g, '<sub>1</sub>').replace(MATH_RE, (_, t, x) => {
    if (t != null) { const c = cmap[t.trim()]; return `<span class="kx"${c ? ` style="--c:${colOf(c)}"` : ''} data-len="${t.length}">${tex(t)}</span>`; }
    const key = x.trim(), c = cmap[key];
    const toks = /^([A-Z][0-9]?)+$/.test(key) ? key.match(/[A-Z][0-9]?/g) : null;
    const cls = 'm' + (toks ? ' k' : '') + (toks && toks.length >= 3 && c ? ' pl' : '');
    const attrs = (c ? ` style="--c:${colOf(c)}"` : '') + (toks ? ` data-k="${toks.join(',')}" data-c="${c || 'violet'}"` : '');
    return `<span class="${cls}"${attrs}>${x.replace(/([A-Z])1/g, '$1<sub>1</sub>')}</span>`;
  });
}
/* Hand-writing: each character is revealed left→right in turn while the pen tip follows it */
let writing = null;
function handwrite(root, delay) {
  const chars = [];
  let t = delay, circ = null;
  const walk = node => [...node.childNodes].forEach(c => {
    if (c.nodeType === 3) {
      const frag = document.createDocumentFragment();
      for (const ch of c.textContent) {
        if (/\s/.test(ch)) { frag.append(ch); t += 50; continue; }
        const sp = document.createElement('span'), dur = /[㐀-鿿]/.test(ch) ? 150 : 95;
        sp.className = 'hw'; sp.textContent = ch;
        chars.push({el: sp, t0: t, dur});
        t += dur + 12;
        frag.append(sp);
      }
      c.replaceWith(frag);
    } else if (c.nodeType === 1 && c.classList.contains('kx')) {         // a whole formula is one long stroke
      const dur = Math.min(1600, 160 + 38 * (+c.dataset.len || 6));
      c.classList.add('hw'); chars.push({el: c, t0: t, dur}); t += dur + 20;
    } else if (c.nodeType === 1 && c.tagName !== 'DETAILS') {
      if (c.dataset.pause) t += +c.dataset.pause;
      if (c.classList.contains('sh-res')) circ = {el: c.querySelector('.v'), t: t + 400};
      walk(c);
    }
  });
  walk(root);
  const sheet = $('sheet');
  chars.forEach(c => {          // position of each glyph inside the sheet (layout coords, unaffected by 3D)
    let x = 0, y = 0, el = c.el;
    while (el && el !== sheet) { x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; }
    Object.assign(c, {x, y, w: c.el.offsetWidth, h: c.el.offsetHeight});
  });
  sheet.classList.remove('done');
  writing = {chars, circ, next: 0, start: performance.now()};
}
let penLevel = 0;                                        // 0 = pen lifted, ~1 = scratching hard (drives the scratch sound)
function penTick() {
  const pen = $('pen'), sh = $('penSh');
  let x = 470, y = 640, lift = 26;                       // resting spot, bottom-right of the sheet
  penLevel = 0;
  if (writing) {
    const el = performance.now() - writing.start, cs = writing.chars;
    while (writing.next < cs.length && el >= cs[writing.next].t0 + cs[writing.next].dur) cs[writing.next++].el.style.clipPath = 'none';
    const i = writing.next < cs.length ? writing.next : -1;
    if (i >= 0 && el >= cs[i].t0) cs[i].el.style.clipPath = `inset(-35% ${(105 - 117 * clamp01((el - cs[i].t0) / cs[i].dur)).toFixed(1)}% -35% -8%)`;
    if (writing.circ && el >= writing.circ.t) { writing.circ.el.classList.add('on'); writing.circ = null; }
    if (i < 0) $('sheet').classList.add('done');
    if (i >= 0) {
      const c = cs[i], k = clamp01((el - c.t0) / c.dur);
      x = c.x + c.w * k; y = c.y + c.h * (.72 - .25 * Math.sin(k * Math.PI));
      lift = el < c.t0 ? 10 : 3 + 2 * Math.sin(k * 9);
      if (el >= c.t0) penLevel = (.5 + .5 * Math.abs(Math.sin(k * Math.PI * (c.dur > 120 ? 4 : 2)))) * (.85 + Math.random() * .3);
    }
  }
  pen.style.transform = `translate3d(${x.toFixed(1)}px, ${y.toFixed(1)}px, ${lift.toFixed(1)}px)`;
  sh.style.transform = `translate(${(x + lift * .5).toFixed(1)}px, ${(y + lift * .8).toFixed(1)}px)`;
}

/* ---------- sound (intro build only): looping music, ducked while she talks, and a synthesised pencil scratch ---------- */
const snd = {on: true, ctx: null, gain: null, filt: null, vol: 0};
const bgm = $('bgm'), soundBtn = $('soundBtn');
if (INTRO_ON) {
  try { snd.on = localStorage.getItem('sound') !== 'off'; } catch (e) {}
  const setSoundBtn = () => { soundBtn.textContent = snd.on ? '♪ 声音开' : '♪ 声音关'; soundBtn.classList.toggle('off', !snd.on); };
  setSoundBtn();
  const unlockAudio = () => {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!snd.ctx && AC) {
      const ctx = snd.ctx = new AC(), n = ctx.sampleRate * 2, buf = ctx.createBuffer(1, n, ctx.sampleRate), d = buf.getChannelData(0);
      for (let i = 0, b = 0; i < n; i++) { const w = Math.random() * 2 - 1; b = .6 * b + .4 * w; d[i] = .6 * w + .4 * b; }
      const src = ctx.createBufferSource(); src.buffer = buf; src.loop = true;
      const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 900;
      snd.filt = ctx.createBiquadFilter(); snd.filt.type = 'bandpass'; snd.filt.frequency.value = 3200; snd.filt.Q.value = .9;
      snd.gain = ctx.createGain(); snd.gain.gain.value = 0;
      src.connect(hp).connect(snd.filt).connect(snd.gain).connect(ctx.destination); src.start();
    }
    if (snd.ctx && snd.ctx.state === 'suspended') snd.ctx.resume();
    if (snd.on && bgm.paused) bgm.play().catch(() => {});
  };
  ['pointerdown', 'keydown'].forEach(t => addEventListener(t, unlockAudio, true));
  soundBtn.onclick = () => {
    snd.on = !snd.on; setSoundBtn();
    try { localStorage.setItem('sound', snd.on ? 'on' : 'off'); } catch (e) {}
    if (!snd.on) bgm.pause();
  };
}
const BGM_VOL = .35, BGM_DUCK = .1, SCRATCH_VOL = .35;
function soundTick() {
  if (!INTRO_ON) return;
  const talking = girlV && !girlV.paused && camS.i > 0;
  snd.vol += ((snd.on ? (talking ? BGM_DUCK : BGM_VOL) : 0) - snd.vol) * .06;
  bgm.volume = clamp01(snd.vol);
  if (snd.gain) {
    const t = snd.ctx.currentTime;
    snd.gain.gain.setTargetAtTime(snd.on ? penLevel * SCRATCH_VOL : 0, t, .012);
    if (penLevel) snd.filt.frequency.setTargetAtTime(2600 + Math.random() * 1800, t, .03);
  }
}

$('tabs').innerHTML = PARTS.map((p, i) => `<button data-p="${i}">${p.name || `第 (${i + 1}) 问`}</button>`).join('');
function show(p, s) {
  cur = {p, s};
  window.__embStep = `#demo${p + 1}-${s + 1}`;
  const part = PARTS[p], st = part.steps[s], cm = st.cmap || {}, spec = st.spec || {};
  document.querySelectorAll('.tabs button').forEach(b => b.classList.toggle('on', +b.dataset.p === p));
  const res = st.result == null ? null : typeof st.result === 'object' ? st.result : {k: '答', v: st.result, note: ''};
  const sheet = $('sheet');
  sheet.classList.remove('dense', 'denser');
  $('shIn').innerHTML =
    `<div class="sh-head">${part.name || `第 (${p + 1}) 问`} · Step ${s + 1} / ${part.steps.length}</div>` +
    `<div class="sh-title" data-pause="200">${fmtC(st.h, cm)}</div>` +
    (st.chain || []).map(([e, y], i) =>
      `<div class="r"><span class="e" data-pause="380">${i ? '<span class="to">⟹</span>' : ''}${fmtC(e, cm)}</span>` +
      (y ? `<span class="y" data-pause="120">(${fmtC(y)})</span>` : '') + '</div>').join('') +
    (res ? `<div class="sh-res" data-pause="400"><span class="v">${fmtC(res.k)} = ${fmtC(res.v)}</span>${fmtC(res.note || '')}</div>` : '') +
    (st.full ? `<details class="sh-full"><summary>规范作答（考场写法）</summary>${fmtC(st.full, cm)}</details>` : '');
  // long chains: tighten the ruling until the text fits above the slider / hint
  const room = 700 - (spec.slider ? 170 : 70);
  for (const cls of ['dense', 'denser']) { if ($('shIn').scrollHeight <= room) break; sheet.classList.add(cls); }
  handwrite($('shIn'), camS.d > .9 ? 150 : 1100);
  pop.hover = null;
  $('mDots').innerHTML = part.steps.map((_, i) => `<i class="${i === s ? 'on' : ''}" data-i="${i}"></i>`).join('');
  $('prev').disabled = p === 0 && s === 0;
  const last = s === part.steps.length - 1;
  $('next').textContent = !last ? '下一步 →' : p < PARTS.length - 1 ? `进入第 (${p + 2}) 问 →` : '完成 ✓';
  pop.set(spec);
  slider.classList.toggle('show', !!spec.slider);
  if (spec.slider) range.value = spec.a ?? DEF_A;
}
function openDemo(p, s) { document.body.classList.add('demo'); flat.set(BASE); show(p, s); }
function closeDemo() { document.body.classList.remove('demo'); slider.classList.remove('show'); pop.aT = DEF_A; }
$('next').onclick = () => {
  const n = PARTS[cur.p].steps.length;
  if (cur.s < n - 1) show(cur.p, cur.s + 1);
  else if (cur.p < PARTS.length - 1) show(cur.p + 1, 0);
  else closeDemo();
};
$('prev').onclick = () => {
  if (cur.s > 0) show(cur.p, cur.s - 1);
  else if (cur.p > 0) show(cur.p - 1, PARTS[cur.p - 1].steps.length - 1);
};
$('sheet').addEventListener('mouseover', e => {
  const k = e.target.closest('.k');
  pop.hover = k ? {pts: k.dataset.k.split(','), c: k.dataset.c} : null;
});
$('sheet').addEventListener('mouseleave', () => pop.hover = null);
$('mDots').onclick = e => { if (e.target.dataset.i) show(cur.p, +e.target.dataset.i); };
document.querySelectorAll('.tabs button').forEach(b => b.onclick = () => show(+b.dataset.p, 0));
$('close').onclick = closeDemo;
document.addEventListener('keydown', e => {
  if (!demo()) return;
  if (e.key === 'Escape') closeDemo();
  if (e.key === 'ArrowRight') $('next').click();
  if (e.key === 'ArrowLeft' && !$('prev').disabled) $('prev').click();
});
range.addEventListener('input', () => {
  let v = +range.value;
  if (PARAM && PARAM.snap && Math.abs(v - DEF_A) < PARAM.snap) { v = DEF_A; range.value = DEF_A; }   // snap to the given value
  pop.aT = v;
});

/* ---------- prediction ---------- */
let guessed = null;
const PR = L.predict;
const flapEl = $('flap'), seg1 = $('seg1'), flapShadow = $('flapShadow');
$('dockMsg').textContent = PR ? (PR.dockMsg || '你的回合：先在左页猜一个答案') : '点左页的题号，或直接开始演示';
document.querySelectorAll('.opt').forEach(b => b.onclick = () => {
  if (fl.opened) return;
  document.querySelectorAll('.opt').forEach(x => x.classList.remove('sel'));
  b.classList.add('sel'); guessed = +b.dataset.v;
  $('dockMsg').textContent = '很好！现在把左下角的纸片往上掀';
  setDock(2);
});

/* ---------- the flap: a spring-driven paper hinge you can click or drag ---------- */
const OPEN = 158;
const fl = {a: 0, v: 0, target: 0, drag: null, opened: false};
function setOpen(open) {
  fl.target = open ? OPEN : 0;
  if (open && !fl.opened) reveal();
}
function reveal() {
  fl.opened = true;
  document.querySelectorAll('.opt').forEach(x => { if (+x.dataset.v === PR.answer) x.classList.add('right'); else if (x.classList.contains('sel')) x.classList.add('wrong'); });
  $('verdict').textContent = guessed === null ? '直接看答案啦？' : guessed === PR.answer ? '你猜对了！' : '和你猜的不一样？';
  $('dockMsg').textContent = '答案揭晓 —— 点开演示看每一步';
  setDock(3);
}
if (seg1) {
  seg1.addEventListener('pointerdown', e => {
    fl.drag = {y: e.clientY, a0: fl.a, moved: false};
    seg1.setPointerCapture(e.pointerId); e.stopPropagation();
  });
  seg1.addEventListener('pointermove', e => {
    if (!fl.drag) return;
    const dy = fl.drag.y - e.clientY;
    if (Math.abs(dy) > 4) fl.drag.moved = true;
    fl.a = Math.max(0, Math.min(175, fl.drag.a0 + dy * 1.1)); fl.v = 0;
  });
  seg1.addEventListener('pointerup', () => {
    const d = fl.drag; fl.drag = null;
    if (!d) return;
    if (!d.moved) return setOpen(fl.target < OPEN / 2);
    setOpen(fl.a > 55);
  });
  seg1.addEventListener('mouseenter', () => { if (!fl.drag && fl.target === 0 && fl.a < 2) fl.target = 9; });
  seg1.addEventListener('mouseleave', () => { if (!fl.drag && fl.target === 9) fl.target = 0; });
  $('flapGo').onclick = () => openDemo(PR.part ?? PARTS.length - 1, 0);
}
function flapTick() {
  if (!flapEl) return;
  if (!fl.drag) { fl.v += (fl.target - fl.a) * .07; fl.v *= .82; fl.a += fl.v; }
  const a = Math.max(-4, Math.min(178, fl.a)), r = a * Math.PI / 180;
  const bend = 30 * Math.sin(Math.PI * Math.max(0, Math.min(1, a / OPEN)));   // paper curls mid-lift
  flapEl.style.setProperty('--a1', (a - bend * .35).toFixed(2) + 'deg');
  flapEl.style.setProperty('--a2', bend.toFixed(2) + 'deg');
  flapEl.style.setProperty('--shade', (Math.max(0, Math.sin(r)) * .28).toFixed(3));
  flapShadow.style.opacity = a > 1 ? (.15 + .35 * Math.sin(Math.min(r, Math.PI))).toFixed(3) : 0;
  flapShadow.style.transform = `translateZ(.5px) translateY(${(Math.sin(r) * 6).toFixed(1)}px) scaleY(${Math.cos(r).toFixed(3)})`;
}
$('dockGo').onclick = () => openDemo(0, 0);
function setDock(n) { document.querySelectorAll('#dockDots i').forEach((d, i) => d.classList.toggle('on', i < n)); }
setDock(1);

/* ---------- camera: everything is set here each frame so the 3D overlay matches the CSS scene ---------- */
const world = $('world'), cam = $('cam'), flatfig = $('flatfig'), vp = $('vp');
const PERSP = 1900, PO = [.5, .18], CAM_AT = [.5, .57];
const FOCUS = [560, -60], FOCUS_DY = 90;    // world point the demo camera centres on (between figure and sheet)
const INTRO = {eye: roomToWorld([0, 115, 140]), tilt: 76, po: .5, fov: 1.25};
const camS = {d: 0, i: INTRO_ON ? 1 : 0, px: 0, py: 0, tx: 0, ty: 0};   // i: intro (1 = classroom shot, 0 = looking down at the desk)
const room = $('room');
const intro = {leaving: !INTRO_ON};
let pointerDown = false;
addEventListener('pointerdown', () => pointerDown = true);
addEventListener('pointerup', () => pointerDown = false);
addEventListener('pointermove', e => {
  if (pointerDown) return;
  camS.tx = e.clientX / innerWidth - .5; camS.ty = e.clientY / innerHeight - .5;
});

function updateCamera(dt) {
  const target = demo() ? 1 : 0;
  camS.d += (target - camS.d) * Math.min(1, dt * 2.6);
  camS.px += (camS.tx - camS.px) * Math.min(1, dt * 3);
  camS.py += (camS.ty - camS.py) * Math.min(1, dt * 3);
  if (intro.leaving) camS.i = Math.max(0, camS.i - dt / 2.6);
  else if (camS.i < 1) camS.i = Math.min(1, camS.i + dt / 2.6);    // flying back to the classroom
  if (intro.leaving && camS.i < .3 && document.body.classList.contains('intro')) document.body.classList.remove('intro');
  const vw = innerWidth, vh = innerHeight;
  const d = ease(clamp01(camS.d)), i = ease(camS.i);
  const km = Math.min(vw / 1760, vh / 1120) * (1 + .28 * d);   // close-up in demo mode
  const tilt = 36 + 24 * d;                                    // flatter, lower view in demo mode
  const camT = `rotateX(${(-camS.py * 3).toFixed(3)}deg) rotateY(${(camS.px * 4).toFixed(3)}deg)`;
  let worldT = `translateY(${(FOCUS_DY * d).toFixed(2)}px) scale(${km.toFixed(4)}) rotateX(${tilt.toFixed(3)}deg) translate(${(-FOCUS[0] * d).toFixed(2)}px, ${(-FOCUS[1] * d).toFixed(2)}px)`;
  let P = PERSP, poY = PO[1];
  if (i > 0) {
    // intro: a real camera flight from the aisle down to the desk view
    const mix = (a, b) => a + (b - a) * i, R = Math.PI / 180;
    const rxInv = (v, th) => [v[0], v[1] * Math.cos(th) + v[2] * Math.sin(th), -v[1] * Math.sin(th) + v[2] * Math.cos(th)];
    const Tw = [FOCUS[0] * d, FOCUS[1] * d, 0];
    const Em = add(Tw, rxInv([0, ((PO[1] - CAM_AT[1]) * vh - FOCUS_DY * d) / km, PERSP], tilt * R));
    const Ei = INTRO.eye, Pi = vh * INTRO.fov;
    const elev = E => Math.atan2(E[2] - Tw[2], E[1] - Tw[1]);
    const yOff = mix((CAM_AT[1] - PO[1]) * vh + FOCUS_DY * d, -Pi / Math.tan(elev(Ei) + INTRO.tilt * R));
    const E = Em.map((v, j) => mix(v, Ei[j])), k = mix(km, 1);
    P = mix(PERSP, Pi); poY = mix(PO[1], INTRO.po);
    const th = Math.atan2(k * P, -yOff) - elev(E);
    const F = sub(E, rxInv([0, (poY - CAM_AT[1]) * vh / k, P], th));
    worldT = `scale(${k.toFixed(4)}) rotateX(${(th / R).toFixed(3)}deg) translate3d(${F.map(v => (-v).toFixed(2) + 'px').join(',')})`;
    world.style.setProperty('--tilt', (th / R).toFixed(3) + 'deg');
  }
  vp.style.perspective = P.toFixed(1) + 'px';
  vp.style.perspectiveOrigin = `50% ${(poY * 100).toFixed(3)}%`;
  room.style.display = camS.i > 0 ? '' : 'none';
  cam.style.transform = camT;
  world.style.transform = worldT;
  if (!(i > 0)) world.style.setProperty('--tilt', tilt.toFixed(3) + 'deg');
  world.style.setProperty('--pop', easeOutBack(clamp01((camS.d - .15) / .85)).toFixed(4));
  pop.g = camS.d < .2 ? 0 : easeOutBack(clamp01((camS.d - .2) / .8));
  flatfig.style.opacity = (1 - clamp01(camS.d * 2.2 * (RD ? 1 : 0))).toFixed(3);

  const cw = new DOMMatrix(camT).multiply(new DOMMatrix(worldT));      // world → camera space (the WebGL room uses this too)
  const view = new DOMMatrix().translate(vw * CAM_AT[0], vh * CAM_AT[1]).multiply(cw);
  const P0 = new DOMMatrix(); P0.m34 = -1 / P;
  const persp = new DOMMatrix().translate(vw * .5, vh * poY).multiply(P0).translate(-vw * .5, -vh * poY);
  return {view, persp, eye: [vw * .5, vh * poY, P], cw, P, poY, vw, vh};
}

const popSvg = $('pop');
function sizePop() { popSvg.setAttribute('viewBox', `0 0 ${innerWidth} ${innerHeight}`); }
addEventListener('resize', sizePop); sizePop();

let last = performance.now();
const lastMarkup = {flat: '', pop: '', show: '', read: ''};
const EMB_FRAMES = () => window.__emb.frames++;
function loop(ms) {
  const now = ms / 1000, dt = Math.min(.05, (ms - last) / 1000); last = ms;
  const w = updateCamera(dt);
  window.glFrame?.(w);
  EMB_FRAMES();
  // only touch the DOM when the markup actually changed (idle frames are free, hover/pointer state survives)
  if (+flatfig.style.opacity > 0) { const m = flat.render(now); if (m !== lastMarkup.flat) flat.svg.innerHTML = lastMarkup.flat = m; }
  { const m = pop.render(now, w); if (m !== lastMarkup.pop) popSvg.innerHTML = lastMarkup.pop = m; }
  flapTick();
  penTick();
  soundTick();
  introTick(w);
  dust(now, dt);
  if (PARAM && slider.classList.contains('show')) {
    const a = pop.a, ok = PARAM.ok ? PARAM.ok(a) : Math.abs(a - DEF_A) < (PARAM.snap ? PARAM.snap / 6 : 1e-6);
    const shown = PARAM.show ? String(PARAM.show(a)) : fix(a), read = PARAM.read ? String(PARAM.read(a, ok)) : '';
    if (shown !== lastMarkup.show) $('bcv').textContent = lastMarkup.show = shown;
    if (read !== lastMarkup.read) $('sliderR').innerHTML = fmt(lastMarkup.read = read);     // KaTeX is re-rendered only when the text changes
    slider.classList.toggle('ok', ok);
  }
  requestAnimationFrame(loop);
}

/* ---------- intro: she asks, then the camera drops to the desk ---------- */
const girlV = $('girlV'), say = $('say'), introUi = $('introUi');
const LINES = [[.52, '同学，'], [1.7, '这道题怎么解？']];   // speech onsets in the video (seconds)
let sayChars = [];
if (INTRO_ON) {
  document.body.classList.add('intro');
  say.innerHTML = LINES.map(([t0, s]) => [...s].map((ch, j) => `<span data-t="${(t0 + j * .08).toFixed(2)}">${ch}</span>`).join('')).join('<br>');
  sayChars = [...say.children].filter(el => el.dataset.t);
  // keyed alpha video: VP9/WebM for Chrome & Firefox, HEVC-with-alpha for Safari
  girlV.src = /^((?!chrome|android).)*safari/i.test(navigator.userAgent) ? 'girl.mov' : 'girl.webm';
}
function playIntro() { introUi.classList.remove('ask'); return girlV.play(); }
function leaveIntro() {
  if (intro.leaving) return;
  intro.leaving = true;
  introUi.classList.remove('ask');
  girlV.pause();
  say.classList.add('gone');
}
function introTick(w) {
  if (!INTRO_ON) return;
  if (intro.returning && camS.i >= 1) { intro.returning = false; playIntro().catch(() => introUi.classList.add('ask')); }
  if (camS.i <= 0) return;
  const q = w.persp.multiply(w.view).transformPoint(new DOMPoint(...roomToWorld([GIRL.x + 20, GIRL.y, 158]), 1));
  const x = Math.max(16, Math.min(q.x / q.w, innerWidth - say.offsetWidth - 16));
  const y = Math.max(say.offsetHeight + 16, q.y / q.w);
  say.style.translate = `${x.toFixed(1)}px ${(y - say.offsetHeight).toFixed(1)}px`;
  // she is a CSS plane over the WebGL room, so hide whatever of her the desk's far edge would cover from this eye
  const e = w.cw.inverse().transformPoint(new DOMPoint(0, (w.poY - CAM_AT[1]) * innerHeight, w.P));
  const ey = e.y / CM, ez = (e.z + 3) / CM + DESK_Z, edge = DESK.y0 / CM;
  const zCut = ey > edge && ez > DESK_Z ? ez + (DESK_Z - ez) * (GIRL.y - ey) / (edge - ey) : 0;
  const bottom = GIRL.h * .92 - GIRL.h;
  girlPlane.style.clipPath = `inset(0 0 ${Math.max(0, (zCut - bottom) / GIRL.h * 100).toFixed(2)}% 0)`;
  if (intro.leaving) return;
  const t = girlV.currentTime;
  say.classList.toggle('on', t >= LINES[0][0] - .08);
  sayChars.forEach(el => el.classList.toggle('v', t >= +el.dataset.t));
}
if (INTRO_ON) {
  girlV.addEventListener('ended', () => setTimeout(leaveIntro, 450));
  girlV.addEventListener('error', leaveIntro);
  $('introStart').onclick = () => playIntro().catch(leaveIntro);
  $('toClass').onclick = () => {          // from the desk, fly back up to the classroom and let her ask again
    if (demo()) closeDemo();
    intro.leaving = false; intro.returning = true;
    document.body.classList.add('intro');
    say.classList.remove('on', 'gone'); sayChars.forEach(el => el.classList.remove('v'));
    girlV.currentTime = 0;
  };
  $('introSkip').onclick = leaveIntro;
  addEventListener('keydown', e => { if (!intro.leaving && (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); leaveIntro(); } });
}

const deep = location.hash.match(/^#demo(\d)-(\d+)$/);
if (deep) {
  if (INTRO_ON) { intro.leaving = true; camS.i = 0; document.body.classList.remove('intro'); }
  openDemo(+deep[1] - 1, +deep[2] - 1);
} else if (INTRO_ON) playIntro().catch(() => introUi.classList.add('ask'));   // autoplay with sound is usually blocked until a click
requestAnimationFrame(loop);
