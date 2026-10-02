/* Deterministic, schematic animal-cell cutaway. No accumulated animation state. */
(function (root) {
  'use strict';
  const PI = Math.PI, TAU = PI * 2;
  const clamp = x => Math.max(0, Math.min(1, x));
  const ease = x => { x = clamp(x); return x * x * (3 - 2 * x); };
  const lerp = (a, b, p) => a + (b - a) * p;
  const stages = ['focus', 'wrap', 'transport', 'fuse', 'digest', 'return'];
  function sample(time, cues) {
    if (!Number.isFinite(time) || time < 0) throw Error('Invalid time');
    let previous = -Infinity;
    const progress = {};
    for (const stage of stages) {
      const interval = cues[stage];
      if (!Array.isArray(interval) || interval.length !== 2 ||
          !interval.every(Number.isFinite) || interval[0] < 0 || interval[1] <= interval[0]) {
        throw Error('Invalid interval for ' + stage);
      }
      if (interval[0] < previous) throw Error('Invalid stage order: ' + stage);
      previous = interval[1];
      progress[stage] = ease((time - interval[0]) / (interval[1] - interval[0]));
    }
    const close = progress.focus * (1 - progress.return);
    return {
      ...progress,
      camera: { x: lerp(235, 325, progress.transport) * close,
                y: lerp(-20, -100, progress.transport) * close, zoom: lerp(1.06, 2.5, close) },
      cargo: { x: lerp(170, 228, progress.transport), y: lerp(-20, -100, progress.transport) },
      closed: progress.wrap === 1,
      cargoOpacity: 1 - progress.digest,
      healthyOpacity: 1,
      // A visual cue for this damaged source; not a measured concentration.
      sourceStrength: 1 - progress.digest,
    };
  }
  function ellipse(ctx, x, y, rx, ry, fill, stroke, width = 2) {
    ctx.beginPath(); ctx.ellipse(x, y, rx, ry, 0, 0, TAU);
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = width; ctx.stroke(); }
  }
  function bean(ctx) {
    ctx.beginPath(); ctx.moveTo(-87, 0);
    ctx.bezierCurveTo(-95, -54, -32, -66, 42, -37);
    ctx.bezierCurveTo(96, -25, 98, 38, 43, 49);
    ctx.bezierCurveTo(-20, 63, -76, 55, -87, 0); ctx.closePath();
  }
  function mitochondrion(ctx, x, y, angle = 0, size = 1, damaged = false, time = 0) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle); ctx.scale(size, size);
    const opacity = ctx.globalAlpha;
    ctx.shadowColor = damaged ? '#f5775966' : '#44dfcf44'; ctx.shadowBlur = 17;
    const body = ctx.createLinearGradient(-70, -55, 80, 54);
    body.addColorStop(0, damaged ? '#ffe0a6' : '#b2ffe3');
    body.addColorStop(.5, damaged ? '#dc7959' : '#35b8b1');
    body.addColorStop(1, damaged ? '#7b3f58' : '#155663');
    bean(ctx); ctx.fillStyle = body; ctx.fill();
    ctx.strokeStyle = damaged ? '#ffb088' : '#86f3d6'; ctx.lineWidth = 3; ctx.stroke();
    ctx.shadowBlur = 0;
    // The same closed inner-membrane contour turns inward to form each crista.
    ctx.beginPath(); ctx.moveTo(-73, 0);
    ctx.bezierCurveTo(-79, -30, -65, -39, -53, -36);
    for (let i = 0; i < 5; i++) {
      const px = -53 + i * 23, py = -36 + i * 3;
      ctx.bezierCurveTo(px + 4, py, px + 3, 22, px + 9, 24);
      ctx.bezierCurveTo(px + 16, 25, px + 14, py + 3, px + 23, py + 3);
    }
    ctx.bezierCurveTo(85, -18, 79, 31, 38, 37);
    ctx.bezierCurveTo(-9, 48, -65, 41, -73, 0); ctx.closePath();
    ctx.fillStyle = damaged ? '#492d4c' : '#124854'; ctx.fill();
    ctx.strokeStyle = damaged ? '#ffbf7b' : '#80e8ce'; ctx.lineWidth = 2.8; ctx.stroke();
    ctx.globalAlpha = opacity * .38;
    ellipse(ctx, -33, -31, 30, 6, '#ffffff', null);
    if (damaged) {
      ctx.globalAlpha = opacity * .9; ctx.strokeStyle = '#ff6e68'; ctx.lineWidth = 4;
      ctx.beginPath(); ctx.moveTo(49, -36); ctx.lineTo(39, -16); ctx.lineTo(54, -4); ctx.stroke();
      for (let i = 0; i < 4; i++) {
        const a = time * .5 + i * 1.5;
        ellipse(ctx, Math.cos(a) * 50, Math.sin(a) * 26, 3, 3, '#ffbf79', null);
      }
    }
    ctx.restore();
  }
  function cellBody(ctx, time) {
    const cytoplasm = ctx.createRadialGradient(-120, -100, 20, 0, 0, 650);
    cytoplasm.addColorStop(0, '#155d6d'); cytoplasm.addColorStop(.6, '#0c3b52'); cytoplasm.addColorStop(1, '#0a1a33');
    ctx.shadowColor = '#42c9ed55'; ctx.shadowBlur = 25;
    ellipse(ctx, 0, 0, 636, 350, cytoplasm, '#66d3e9', 5);
    ctx.shadowBlur = 0;
    ellipse(ctx, 0, 0, 624, 338, null, '#2788ab', 4);
    // Paired phospholipid heads sketch one plasma membrane bilayer.
    for (let i = 0; i < 128; i++) {
      const a = TAU * i / 128;
      ellipse(ctx, Math.cos(a) * 635, Math.sin(a) * 349, 3.8, 3.8, '#7ad4df', null);
      ellipse(ctx, Math.cos(a) * 625, Math.sin(a) * 339, 2.5, 2.5, '#2b9aba', null);
    }
    ctx.save(); ctx.beginPath(); ctx.ellipse(0, 0, 615, 329, 0, 0, TAU); ctx.clip();
    for (let i = 0; i < 130; i++) {
      const x = Math.sin(i * 12.3) * 610 + Math.sin(time * .12 + i) * 5;
      const y = Math.cos(i * 7.8) * 320 + Math.cos(time * .1 + i) * 5;
      ctx.globalAlpha = .18 + (i % 4) * .06;
      ellipse(ctx, x, y, 1.4 + i % 3, 1.4 + i % 3, '#a4e9e4', null);
    }
    ctx.globalAlpha = 1;
    const nucleus = ctx.createRadialGradient(-285, -55, 10, -255, 0, 150);
    nucleus.addColorStop(0, '#cd9ed1'); nucleus.addColorStop(.4, '#71528c'); nucleus.addColorStop(1, '#302c59');
    ellipse(ctx, -255, 0, 147, 132, nucleus, '#b992cf', 4);
    ellipse(ctx, -255, 0, 135, 120, null, '#736baf', 2);
    ellipse(ctx, -274, 27, 39, 34, '#d5a0bb', '#e9b6cf', 2);
    ctx.strokeStyle = '#be9ad3'; ctx.lineWidth = 2; ctx.globalAlpha = .45;
    for (let i = 0; i < 7; i++) {
      ctx.beginPath(); ctx.moveTo(-356 + i * 28, -38);
      ctx.bezierCurveTo(-351 + i * 28, -104, -293 + i * 13, 107, -226 + i * 7, 49); ctx.stroke();
    }
    ctx.globalAlpha = 1;
    mitochondrion(ctx, -115, -221, -.45, .68, false, time);
    mitochondrion(ctx, -155, 225, .42, .76, false, time);
    mitochondrion(ctx, 243, 161, -.36, .77, false, time);
    mitochondrion(ctx, 433, 110, .7, .57, false, time);
    // Vesicles and endoplasmic-reticulum folds supply context, not extra lesson claims.
    for (let i = 0; i < 9; i++) ellipse(ctx, -43 + (i % 3) * 120, -235 + Math.floor(i / 3) * 70, 8, 7, '#598997', '#7dbbc5', 1.5);
    ctx.strokeStyle = '#716b98'; ctx.lineWidth = 7; ctx.globalAlpha = .6;
    for (let i = 0; i < 4; i++) {
      ctx.beginPath(); ctx.moveTo(-448, -115 + i * 42);
      ctx.bezierCurveTo(-560, -125 + i * 40, -476, 100 + i * 33, -392, 116 + i * 27); ctx.stroke();
    }
    ctx.restore();
  }
  function lysosome(ctx, state, time) {
    const p = state.fuse, x = lerp(430, 325, p), y = -100;
    const rx = lerp(92, 228, p), ry = lerp(83, 128, p);
    const fill = ctx.createRadialGradient(x - rx * .28, y - ry * .4, 5, x, y, rx);
    fill.addColorStop(0, '#aa8dea'); fill.addColorStop(.4, '#6852a7'); fill.addColorStop(1, '#302c63');
    ctx.save(); const opacity = ctx.globalAlpha;
    ctx.shadowColor = '#ac91ee55'; ctx.shadowBlur = 22;
    ctx.globalAlpha = opacity * (1 - p);
    ellipse(ctx, 430, y, 92, 83, fill, '#bd9dec', 3);
    if (p > 0) {
      // Contact opens a narrow neck between two compartments; it widens as
      // their outer membranes merge into one autolysosome boundary.
      const neck = 3 + p * 74;
      const base = [
        [170,-53,232,-83,288,-83], [345,-83,380,-neck,406,-neck],
        [420,-neck,452,-83,490,-83], [550,-83,582,-45,582,0],
        [582,45,550,83,490,83], [452,83,420,neck,406,neck],
        [380,neck,345,83,288,83], [232,83,170,53,170,0],
      ];
      const merged = [
        [157,-34,181,-67,224,-90.5], [267,-115,324,-128,385,-128],
        [446,-128,503,-115,546,-90.5], [589,-67,613,-34,613,0],
        [613,34,589,67,546,90.5], [503,115,446,128,385,128],
        [324,128,267,115,224,90.5], [181,67,157,34,157,0],
      ];
      ctx.globalAlpha = opacity * p;
      ctx.beginPath(); ctx.moveTo(lerp(170,157,p)-60,y);
      base.forEach((segment,i) => ctx.bezierCurveTo(...segment.map((v,j) =>
        lerp(v,merged[i][j],p) + (j % 2 ? y : -60))));
      ctx.closePath(); ctx.fillStyle = fill; ctx.fill();
      ctx.strokeStyle = '#bd9dec'; ctx.lineWidth = 3; ctx.stroke();
    }
    ctx.globalAlpha = opacity; ctx.shadowBlur = 0;
    for (let i = 0; i < 20; i++) {
      const a = i * 2.399 + time * .2, r = .34 + .5 * ((i * 7) % 13) / 13;
      ellipse(ctx, x + Math.cos(a) * rx * r, y + Math.sin(a) * ry * r, 3.4, 3.4, '#ffd990', null);
    }
    ctx.restore();
  }
  function cargo(ctx, state, time) {
    const { x, y } = state.cargo;
    const destroyed = state.digest;
    ctx.save(); ctx.globalAlpha = 1 - destroyed;
    mitochondrion(ctx, x, y, -.12, 1, true, time); ctx.restore();
    if (destroyed > 0 && destroyed < 1) {
      const alpha = Math.sin(PI * destroyed);
      for (let i = 0; i < 18; i++) {
        const a = i * 2.399, radius = lerp(22, 88, destroyed);
        ctx.save(); ctx.globalAlpha = alpha * .8;
        ellipse(ctx, x + Math.cos(a) * radius, y + Math.sin(a) * radius * .55,
                lerp(6, 1.5, destroyed), lerp(4, 1, destroyed), '#ffd5a0', null); ctx.restore();
      }
    }
    if (state.wrap > 0 && destroyed < 1) {
      const gap = (1 - state.wrap) * PI * .82;
      ctx.save(); ctx.globalAlpha = 1 - destroyed;
      for (let membrane = 0; membrane < 2; membrane++) {
        // The outer autophagosomal membrane merges; the inner membrane stays as cargo.
        ctx.globalAlpha = (1 - destroyed) * (membrane === 0 ? 1 - state.fuse : 1);
        ctx.beginPath(); ctx.ellipse(x, y, 118 - membrane * 10, 82 - membrane * 9,
                                    0, gap, TAU - gap);
        ctx.lineWidth = 5; ctx.strokeStyle = membrane ? '#e3db91' : '#85dcc6'; ctx.stroke();
      }
      ctx.restore();
    }
    const strength = state.sourceStrength;
    for (let i = 0; i < 10; i++) {
      const a = i * 2.399, r = 97 + 18 * Math.sin(time * .75 + i);
      const px = x + Math.cos(a) * r, py = y + Math.sin(a) * r * .66;
      ctx.save(); ctx.globalAlpha = strength * .75;
      ctx.shadowColor = '#ff865f'; ctx.shadowBlur = 11;
      ellipse(ctx, px, py, 3.5 + i % 3, 3.5 + i % 3, '#ff8c68', null); ctx.restore();
    }
  }
  function draw(ctx, state, time, viewport = { x: 40, y: 130, width: 1840, height: 736 }) {
    ctx.save(); ctx.beginPath(); ctx.rect(viewport.x, viewport.y, viewport.width, viewport.height); ctx.clip();
    ctx.translate(viewport.x + viewport.width / 2, viewport.y + viewport.height / 2);
    ctx.scale(state.camera.zoom, state.camera.zoom); ctx.translate(-state.camera.x, -state.camera.y);
    cellBody(ctx, time); lysosome(ctx, state, time); cargo(ctx, state, time); ctx.restore();
  }
  function project(point, state, viewport = { x: 40, y: 130, width: 1840, height: 736 }) {
    return { x: viewport.x + viewport.width / 2 + (point.x - state.camera.x) * state.camera.zoom,
             y: viewport.y + viewport.height / 2 + (point.y - state.camera.y) * state.camera.zoom };
  }
  root.BiologyModel = Object.freeze({ sample, draw, project, mitochondrion });
})(typeof globalThis === 'object' ? globalThis : window);
