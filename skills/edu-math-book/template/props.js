/* ---------- 3D desk props (from the original test-paper page), built from lit div faces ----------
   World axes: x right, y toward the viewer, z up off the desk. Light comes from the upper left. */
const LIGHT3 = unit([-.55, -.6, .95]);
const lum3 = n => Math.max(0, dot(unit(n), LIGHT3));
const mk = (parent, css = '', cls = 'f3') => { const d = document.createElement('div'); d.className = cls; d.style.cssText = css; parent.appendChild(d); return d; };
const grp = (parent, transform = '') => mk(parent, `transform:${transform}`, 'g3');
const shadeLayer = (L, k = .5) => `linear-gradient(rgba(10,6,2,${(k * (1 - L)).toFixed(3)}), rgba(10,6,2,${(k * (1 - L)).toFixed(3)}))`;

// axis-aligned box; f maps face name → CSS background (omit a face to skip it)
function box(parent, w, h, d, f, transform = '') {
  const g = grp(parent, transform);
  const F = (k, W, H, t) => f[k] && mk(g, `width:${W}px;height:${H}px;transform:${t};background:${f[k]}`);
  F('bottom', w, h, 'translateZ(0)');
  F('back', w, d, 'rotateX(90deg)');
  F('left', d, h, 'rotateY(-90deg)');
  F('right', d, h, `translateX(${w}px) rotateY(-90deg)`);
  F('front', w, d, `translateY(${h}px) rotateX(90deg)`);
  F('top', w, h, `translateZ(${d}px)`);
  return g;
}
// vertical cylinder wall around the group origin; bg(L, i) gives each strip's CSS from its lighting
function cyl(parent, r, h, n, bg, z0 = 0, from = 0, to = 360, inward = false) {
  const g = grp(parent), span = to - from, s = 2 * Math.PI * r * span / 360 / n + .9;
  for (let i = 0; i < n; i++) {
    const t = from + (i + .5) * span / n, a = t * Math.PI / 180, nrm = [-Math.sin(a), Math.cos(a), .15];
    mk(g, `width:${s}px;height:${h}px;transform:rotateZ(${t}deg) translate3d(${-s / 2}px,${r}px,${z0}px) rotateX(90deg);background:${bg(lum3(inward ? [-nrm[0], -nrm[1], .15] : nrm), i)}`);
  }
  return g;
}
// n-sided rod along +x (axis through the group origin)
function rod(parent, len, R, n, bg, x0 = 0, nf = v => v) {
  const g = grp(parent), s = 2 * R * Math.sin(Math.PI / n) + .5, a = R * Math.cos(Math.PI / n), faces = [];
  for (let i = 0; i < n; i++) {
    const phi = i * 360 / n, p = phi * Math.PI / 180;
    faces.push(mk(g, `width:${len}px;height:${s}px;transform:rotateX(${phi}deg) translate3d(${x0}px,${-s / 2}px,${a}px);background:${bg(lum3(nf([0, -Math.sin(p), Math.cos(p)])), i)}`));
  }
  return faces;
}
const softShadow = (parent, css) => mk(parent, css, 'sh3');

/* ---- coffee cup on a saucer ---- */
function buildMug(host) {
  const ceramic = (L, top = 97) => `linear-gradient(180deg, hsl(40 12% ${78 + 12 * L}%), hsl(40 16% ${Math.min(top, 76 + 22 * L + 10 * Math.pow(L, 16))}%) 22%, hsl(40 14% ${Math.min(top, 74 + 22 * L)}%))`;
  softShadow(host, 'left:-120px;top:-100px;width:270px;height:250px;border-radius:50%;background:rgba(15,8,2,.5);filter:blur(22px);transform:translate3d(26px,30px,.5px)');
  softShadow(host, 'left:-40px;top:-90px;width:430px;height:180px;border-radius:50%;background:linear-gradient(90deg,rgba(15,8,2,.42),rgba(15,8,2,0));filter:blur(20px);transform-origin:0 50%;transform:translate3d(10px,40px,.4px) rotate(32deg)');
  // saucer
  mk(host, 'left:-132px;top:-132px;width:264px;height:264px;border-radius:50%;transform:translateZ(1px);background:#d9d2c5');
  cyl(host, 132, 9, 56, L => ceramic(L), 1);
  mk(host, `left:-132px;top:-132px;width:264px;height:264px;border-radius:50%;transform:translateZ(10px);
    background:radial-gradient(circle at 42% 40%, rgba(255,255,255,.55), transparent 45%),
      radial-gradient(circle, #ece6db 0 36%, #d8d0c2 41%, #f6f2ea 47%, #efe9df 82%, #fbf9f4 90%, #d9d1c3 100%)`);
  // cup wall, rim, inner wall, coffee
  const H = 140, Z = 10, r = 86;
  mk(host, `left:-${r}px;top:-${r}px;width:${2 * r}px;height:${2 * r}px;border-radius:50%;transform:translateZ(${Z + 1}px);background:#cfc7b8`);
  cyl(host, r, H, 48, L => ceramic(L), Z);
  cyl(host, r - 7, 26, 40, L => `linear-gradient(180deg, hsl(36 12% ${48 + 30 * L}%), hsl(36 16% ${70 + 24 * L}%))`, Z + H - 26, 0, 360, true);
  mk(host, `left:-${r - 6}px;top:-${r - 6}px;width:${2 * r - 12}px;height:${2 * r - 12}px;border-radius:50%;transform:translateZ(${Z + H - 24}px);
    background:radial-gradient(ellipse 30% 18% at 36% 32%, rgba(255,250,240,.55), transparent 70%),
      radial-gradient(circle at 50% 50%, #2a170c 0 30%, #3d2213 55%, #6b4024 80%, #a7744a 92%, #c9976a 100%)`);
  mk(host, `left:-${r}px;top:-${r}px;width:${2 * r}px;height:${2 * r}px;border-radius:50%;transform:translateZ(${Z + H}px);
    -webkit-mask:radial-gradient(circle, transparent ${r - 7.5}px, #000 ${r - 7}px);mask:radial-gradient(circle, transparent ${r - 7.5}px, #000 ${r - 7}px);
    background:conic-gradient(from 200deg, #fbf9f4, #e5ded1 30%, #c9c0b0 50%, #e9e3d8 75%, #fbf9f4)`);
  // handle: several stacked half-rings in the x-z plane make a solid loop
  for (let k = -8; k <= 8; k++) {
    const L = .6 + .25 * Math.cos(k / 8 * Math.PI / 2) - k * .02, inset = 2.2 * (1 - Math.cos(k / 8 * Math.PI / 2.2));
    mk(host, `left:0;top:0;width:${58 - inset}px;height:${92 - 2 * inset}px;box-sizing:border-box;border:${15 - inset * 1.6}px solid hsl(40 14% ${70 + 24 * L}%);border-left:0;border-radius:0 46px 46px 0;transform:translate3d(${r - 12}px,${k * .95}px,${Z + 26 + inset}px) rotateX(90deg)`);
  }
  // steam: a billboard facing the camera
  const st = mk(host, `left:-50px;top:-190px;width:100px;height:190px;transform-origin:50% 100%;transform:translateZ(${Z + H}px) rotateX(calc(-1 * var(--tilt,36deg)))`, 'steam');
  st.innerHTML = '<i></i><i></i><i></i><i></i>';
}

/* ---- white eraser with a paper sleeve ---- */
function buildEraser(host) {
  softShadow(host, 'left:0;top:0;width:124px;height:58px;border-radius:8px;background:rgba(15,8,2,.5);filter:blur(7px);transform:translate3d(9px,8px,.5px)');
  const rubber = L => `${shadeLayer(L, .35)}, linear-gradient(#fbfaf7,#efebe4)`;
  box(host, 120, 56, 22, {top: rubber(.95), front: rubber(.55), back: rubber(.4), left: rubber(.5), right: rubber(.62)});
  const sleeve = L => `${shadeLayer(L, .5)}, linear-gradient(90deg,#1f4f8f,#26599e)`;
  const s = box(host, 66, 58, 24, {top: sleeve(.95), front: sleeve(.6), back: sleeve(.4)}, 'translate3d(48px,-1px,0)');
  s.lastChild.innerHTML = '<span class="slv">SOFT<br>0.5</span>';
}

/* ---- vintage twin-bell alarm clock, showing the real time ---- */
// a camera-facing billboard (works because the camera only tilts about x)
const bill = (parent, css, z = 0, extra = '') => mk(parent, `${css};transform-origin:50% 100%;transform:translateZ(${z}px) rotateX(calc(-1 * var(--tilt,36deg))) ${extra}`, 'bb');
function buildClock(host) {
  const R = 74, Dp = 44, H0 = 16, cz = R + H0;            // body radius, depth, foot height, centre height
  const brass = L => `${shadeLayer(L, .5)}, linear-gradient(90deg,#f1d68a,#c49a3e 40%,#8a6524 60%,#e2c06c)`;
  softShadow(host, `left:-100px;top:-40px;width:220px;height:90px;border-radius:50%;background:rgba(15,8,2,.45);filter:blur(14px);transform:translate3d(16px,10px,.5px)`);
  softShadow(host, `left:-30px;top:-80px;width:420px;height:160px;border-radius:50%;background:linear-gradient(90deg,rgba(15,8,2,.4),rgba(15,8,2,0));filter:blur(18px);transform-origin:0 50%;transform:translate3d(0,20px,.4px) rotate(26deg)`);
  softShadow(host, `left:-70px;top:-14px;width:140px;height:30px;border-radius:50%;background:rgba(10,5,1,.6);filter:blur(5px);transform:translate3d(4px,2px,.6px)`);
  // feet
  [-1, 1].forEach(sx => bill(host, `left:${sx * 48 - 11}px;top:-22px;width:22px;height:22px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff3c4,#d0a44a 40%,#6e4f1a 85%)`, 0));
  // enamel body (cylinder with its axis along y), brass bezel rims front and back
  const body = grp(host, `translateZ(${cz}px) rotateZ(90deg)`), nf = v => [-v[1], v[0], v[2]];
  rod(body, Dp, R, 44, L => `${shadeLayer(L, .55)}, linear-gradient(90deg,#1f3a31,#2f5547 50%,#1f3a31)`, -Dp / 2, nf);
  rod(body, 7, R + 4, 44, brass, Dp / 2 - 1, nf);
  rod(body, 5, R + 2, 44, brass, -Dp / 2 - 3, nf);
  // back plate
  mk(host, `left:${-R - 2}px;top:0;width:${2 * R + 4}px;height:${2 * R + 4}px;border-radius:50%;transform:translate3d(0,${-Dp / 2 - 3}px,${cz + R + 2}px) rotateX(-90deg);background:radial-gradient(circle,#2a4a3e,#16291f)`);
  // dial (facing +y, toward the viewer)
  const face = mk(host, `left:${-R}px;top:0;width:${2 * R}px;height:${2 * R}px;border-radius:50%;transform:translate3d(0,${Dp / 2 + 3}px,${cz + R}px) rotateX(-90deg);
    background:radial-gradient(circle, #fbf3df 0 55%, #f1e4c4 80%, #d9c79c 96%, #b89a5c 100%)`, 'f3 dial');
  mk(face, `left:0;top:0;width:100%;height:100%;border-radius:50%;
    -webkit-mask:radial-gradient(circle, transparent ${R - 9}px, #000 ${R - 8.5}px, #000 ${R - 4}px, transparent ${R - 3.5}px);mask:radial-gradient(circle, transparent ${R - 9}px, #000 ${R - 8.5}px, #000 ${R - 4}px, transparent ${R - 3.5}px);
    background:repeating-conic-gradient(#2a2420 0 .7deg, transparent .7deg 6deg)`, 'f2');
  mk(face, `left:0;top:0;width:100%;height:100%;border-radius:50%;
    -webkit-mask:radial-gradient(circle, transparent ${R - 14}px, #000 ${R - 13.5}px, #000 ${R - 4}px, transparent ${R - 3.5}px);mask:radial-gradient(circle, transparent ${R - 14}px, #000 ${R - 13.5}px, #000 ${R - 4}px, transparent ${R - 3.5}px);
    background:repeating-conic-gradient(from -1deg, #2a2420 0 2deg, transparent 2deg 30deg)`, 'f2');
  ['XII', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI'].forEach((t, i) => {
    const a = i * 30 * Math.PI / 180, rr = R - 27;
    const n = mk(face, `left:${R + Math.sin(a) * rr}px;top:${R - Math.cos(a) * rr - 10}px;transform:rotate(${i * 30}deg)`, 'num');
    n.textContent = t;
  });
  mk(face, `top:${R * .68}px;font-size:6.5px`, 'brand').textContent = PROPS_TEXT.clock;
  mk(face, `top:${R * 1.22}px;font-size:6.5px`, 'brand').textContent = 'ALARM';
  const hand = (w, l, bg, extra = '') => mk(face, `width:${w}px;height:${l}px;margin-left:${-w / 2}px;background:${bg};${extra}`, 'hand');
  const hH = hand(6, R * .48, 'linear-gradient(90deg,#1b1714,#3a322b,#1b1714)', 'clip-path:polygon(50% 0,100% 18%,70% 100%,30% 100%,0 18%)');
  const hM = hand(4.5, R * .72, 'linear-gradient(90deg,#1b1714,#3a322b,#1b1714)', 'clip-path:polygon(50% 0,100% 12%,70% 100%,30% 100%,0 12%)');
  const hS = hand(1.6, R * .86, '#b5322a', 'box-shadow:0 0 0 .3px #b5322a');
  mk(face, `left:${R - 5}px;top:${R - 5}px;width:10px;height:10px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#fff0bd,#b8892f 70%)`, 'f2');
  mk(face, `left:0;top:0;width:100%;height:100%;border-radius:50%;background:radial-gradient(ellipse 60% 40% at 32% 22%, rgba(255,255,255,.55), transparent 60%), radial-gradient(circle, transparent 70%, rgba(0,0,0,.18))`, 'f2');
  let base = null;
  const tick = () => {
    const d = new Date(), sec = d.getHours() * 3600 + d.getMinutes() * 60 + d.getSeconds();
    if (base === null) base = sec;                      // keep angles increasing so hands never sweep backwards
    const t = base + Math.max(0, sec - base);
    hS.style.transform = `rotate(${t * 6}deg)`;
    hM.style.transform = `rotate(${t / 10}deg)`;
    hH.style.transform = `rotate(${t / 120}deg)`;
  };
  tick(); setInterval(tick, 1000);
  // twin bells, striker and carrying handle — billboards hold their shading as the camera tilts
  [-1, 1].forEach(sx => {
    const a = sx * 40, x = Math.sin(a * Math.PI / 180) * (R + 2), z = cz + Math.cos(a * Math.PI / 180) * (R + 2);
    bill(host, `left:${x - 36}px;top:-40px;width:72px;height:40px;border-radius:36px 36px 6px 6px / 38px 38px 6px 6px;
      background:radial-gradient(ellipse 70% 90% at 38% 30%, #fff4cc, #e2bf68 35%, #a57a2e 70%, #6b4c18);box-shadow:inset 0 -4px 0 rgba(90,60,15,.6)`, z - 6, `rotate(${a}deg)`);
    bill(host, `left:${x * .82 - 3}px;top:-20px;width:6px;height:20px;background:linear-gradient(90deg,#8a6524,#e2c06c,#8a6524)`, z - 26, `rotate(${a}deg)`);
  });
  bill(host, `left:-3px;top:-40px;width:6px;height:40px;background:linear-gradient(90deg,#6e4f1a,#e2c06c,#6e4f1a)`, cz + R - 2);
  bill(host, `left:-8px;top:-16px;width:16px;height:16px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff3c4,#c99a3c 50%,#6e4f1a)`, cz + R + 32);
  bill(host, `left:-46px;top:-58px;width:92px;height:58px;box-sizing:border-box;border:7px solid #c79c43;border-bottom:0;border-radius:46px 46px 0 0;
    box-shadow:inset 0 2px 0 rgba(255,240,190,.7), 0 2px 0 rgba(90,60,15,.5)`, cz + R + 8);
}

/* ---- sticky-note pad with a curling top sheet ---- */
function buildSticky(host) {
  const W = 210, H = 200, D = 10;
  softShadow(host, `left:0;top:0;width:${W}px;height:${H}px;background:rgba(15,8,2,.42);filter:blur(10px);transform:translate3d(12px,12px,.5px)`);
  const layers = (dir) => `repeating-linear-gradient(${dir}, #f4dd6a 0 1px, #e3c94f 1px 2px)`;
  box(host, W, H, D, {top: '#f1d95e', front: layers('180deg'), right: layers('90deg'), left: layers('90deg'), back: layers('180deg')});
  const sheet = grp(host, `translateZ(${D + .6}px)`);
  const s1 = mk(sheet, `left:0;top:0;width:${W}px;height:${H * .74}px;background:linear-gradient(160deg,#fff3a2,#fae679);
    font-family:var(--hand);font-size:26px;line-height:1.45;color:#4b4130;padding:20px 22px;box-sizing:border-box`);
  s1.innerHTML = PROPS_TEXT.sticky;
  const s2 = mk(sheet, `left:0;top:${H * .74}px;width:${W}px;height:${H * .26}px;transform-origin:50% 0;transform:rotateX(16deg);
    background:linear-gradient(180deg,#f9e57a,#fff6b8 70%,#f4dc6c);box-shadow:0 6px 8px -4px rgba(0,0,0,.25)`);
}

/* ---- clipboard: board thickness and a chrome clip ---- */
function buildClipboard(board) {
  const edge = 'linear-gradient(180deg,#6d4a2c,#4a311d)';
  box(board, 620, 770, 9, {front: edge, back: edge, left: edge, right: edge}, 'translateZ(-9px)');
  const chrome = L => `${shadeLayer(L, .45)}, linear-gradient(180deg,#fdfdfe 0,#d7dbe1 40%,#9aa1ac 58%,#e9ecf0 100%)`;
  const c = grp(board, 'translate3d(196px,10px,0)');
  box(c, 228, 62, 6, {top: chrome(.95), front: chrome(.6), left: chrome(.7), right: chrome(.5), back: chrome(.4)});
  box(c, 196, 46, 4, {top: chrome(.85), front: chrome(.55), left: chrome(.6), right: chrome(.45)}, 'translate3d(16px,22px,6px) rotateX(-12deg)');
  [[30, 18], [190, 18]].forEach(([x, y]) => mk(c, `left:${x}px;top:${y}px;width:12px;height:12px;border-radius:50%;transform:translateZ(6.5px);background:radial-gradient(circle at 35% 35%,#fff,#8d939c 70%)`));
  mk(c, 'left:84px;top:0;width:60px;height:34px;box-sizing:border-box;border:5px solid #b7bcc4;border-bottom:0;border-radius:30px 30px 0 0;transform:translate3d(0,26px,8px) rotateX(64deg);transform-origin:50% 100%');
}

/* ---- fountain pen inside .ax: nib at the origin, barrel along +x ---- */
function buildPen(ax) {
  const R = 7.5, n = 8;
  rod(ax, 214, R, n, L => `${shadeLayer(L, .55)},
    linear-gradient(180deg, rgba(255,255,255,${(.5 * Math.pow(L, 8)).toFixed(2)}), transparent 55%),
    linear-gradient(90deg, #121418 0 26px, #caa24c 26px 30px, #1b2c52 30px 150px, #e1bd63 150px 155px, #1b2c52 155px 206px, #d2ab52 206px)`, 22);
  const nib = 'linear-gradient(90deg, #8a6a2a 0 6%, #f2dc9a 30%, #c9a14a 70%, #a8823a)';
  mk(ax, `width:26px;height:12px;clip-path:polygon(0 50%,100% 0,100% 100%);transform:translate3d(0,-6px,0);background:${nib}`);
  mk(ax, `width:26px;height:12px;clip-path:polygon(0 50%,100% 0,100% 100%);transform:rotateX(90deg) translate3d(0,-6px,0);background:${nib}`);
  mk(ax, 'width:120px;height:3px;transform:translate3d(150px,-1.5px,8px);background:linear-gradient(90deg,#f0d27e,#b58b38);border-radius:2px');
}


/* ---------- afternoon sun ---------- */
// window panes skewed along the light direction, leaf shadows masked out and swaying
(() => {
  const R = (a, b) => a + Math.random() * (b - a);
  let panes = '';
  for (let i = 0; i < 2; i++) for (let j = 0; j < 3; j++) panes += `<rect x="${j * 410}" y="${i * 330}" width="384" height="304" rx="6"/>`;
  let leaves = '';
  for (let k = 0; k < 26; k++) {
    const x = R(700, 1300), y = R(-60, 260), a = R(-60, 60);
    leaves += `<ellipse cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" rx="${R(38, 70).toFixed(0)}" ry="${R(14, 24).toFixed(0)}" transform="rotate(${a.toFixed(0)} ${x.toFixed(0)} ${y.toFixed(0)})"/>`;
  }
  const svg = id => `<defs>
      <filter id="sunBlur${id}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="16"/></filter>
      <mask id="leafMask${id}"><rect x="-2000" y="-2000" width="8000" height="8000" fill="#fff"/>
        <g fill="#000"><g>${leaves}<path d="M640 -80 C 900 40, 1100 120, 1380 140" stroke="#000" stroke-width="12" fill="none"/>
          <animateTransform attributeName="transform" type="rotate" values="-2.5 640 -80; 2 640 -80; -2.5 640 -80" dur="7s" repeatCount="indefinite"/></g></g></mask>
      <linearGradient id="sunGrad${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="rgb(255,222,160)" stop-opacity=".42"/><stop offset="1" stop-color="rgb(255,190,110)" stop-opacity=".26"/></linearGradient>
    </defs>
    <g filter="url(#sunBlur${id})" mask="url(#leafMask${id})" transform="translate(860 560) matrix(1 .42 -.5 1 0 0)" fill="url(#sunGrad${id})">${panes}</g>`;
  document.getElementById('sun').innerHTML = svg('d');
  document.getElementById('sunPages').innerHTML = svg('p');
})();
// dust motes drifting through the sunlight
const dust = (() => {
  const cv = document.getElementById('dust'), cx = cv.getContext('2d');
  const ps = Array.from({length: 90}, () => ({x: Math.random(), y: Math.random(), r: .35 + Math.random() * 1.1, vx: (Math.random() - .3) * .006, vy: (Math.random() - .6) * .004, ph: Math.random() * 6.28}));
  const size = () => { cv.width = innerWidth * devicePixelRatio; cv.height = innerHeight * devicePixelRatio; };
  addEventListener('resize', size); size();
  return (now, dt) => {
    const W = cv.width, H = cv.height, k = devicePixelRatio;
    cx.clearRect(0, 0, W, H);
    for (const p of ps) {
      p.x += (p.vx + Math.sin(now * .3 + p.ph) * .002) * dt; p.y += (p.vy + Math.cos(now * .23 + p.ph) * .002) * dt;
      if (p.x < -.05) p.x = 1.05; if (p.x > 1.05) p.x = -.05; if (p.y < -.05) p.y = 1.05; if (p.y > 1.05) p.y = -.05;
      const beam = Math.exp(-Math.pow((p.x * .53 + p.y * .85 - .45) / .22, 2));       // brighter inside the sun shafts
      const a = (.15 + .85 * beam) * (.55 + .45 * Math.sin(now * 1.7 + p.ph * 3));
      const x = p.x * W, y = p.y * H, r = p.r * k * (1 + beam);
      const g = cx.createRadialGradient(x, y, 0, x, y, r * 3);
      g.addColorStop(0, `rgba(255,232,190,${(.8 * a).toFixed(3)})`); g.addColorStop(1, 'rgba(255,232,190,0)');
      cx.fillStyle = g; cx.beginPath(); cx.arc(x, y, r * 3, 0, 6.283); cx.fill();
    }
  };
})();
