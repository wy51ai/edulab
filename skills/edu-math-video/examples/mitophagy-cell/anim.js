const PROBLEM = null;
const TAGS = {
  intro: null,
  journey: null,
  outro: null
};
const SC = {};
const BIO_FONT = "'Microsoft YaHei',sans-serif";
const FLAT = window.TIMELINE.scenes.flatMap(s => s.lines);
const mark = (k, fraction = 0) => FLAT[k].start + (FLAT[k].end - FLAT[k].start) * fraction;
const CUES = {
  focus: [mark(1, .1), mark(2, .85)],
  wrap: [mark(3, .08), mark(4, .93)],
  transport: [mark(5, .06), mark(5, .93)],
  fuse: [mark(6, .06), mark(6, .93)],
  digest: [mark(7, .06), mark(7, .95)],
  return: [mark(8, .06), mark(8, .93)]
};
function bioText(text, x, y, size = 30, color = '#d5ebf5', align = 'left') {
  ctx.save(); ctx.font = `500 ${size}px ${BIO_FONT}`; ctx.fillStyle = color;
  ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.fillText(text, x, y); ctx.restore();
}
function bioPanel(x, y, width, height, color = '#0b1b30dd', border = '#456279') {
  ctx.save(); ctx.fillStyle = color; ctx.strokeStyle = border; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.roundRect(x, y, width, height, 16); ctx.fill(); ctx.stroke(); ctx.restore();
}
function bioLabel(text, anchor, x, y, color = '#85e5d3') {
  if (anchor.x < 42 || anchor.x > 1878 || anchor.y < 130 || anchor.y > 859) return;
  ctx.save(); ctx.font = `500 30px ${BIO_FONT}`; const width = ctx.measureText(text).width + 36;
  ctx.strokeStyle = color; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(anchor.x, anchor.y); ctx.lineTo(x + width / 2, y + 40); ctx.stroke();
  bioPanel(x, y, width, 46, '#0b1b30e8', color); bioText(text, x + 18, y + 23, 30, color); ctx.restore();
}
function miniCell(state) {
  if (state.focus * (1 - state.return) < .2) return;
  bioPanel(56, 649, 234, 202, '#0b182ae8', '#41667a');
  bioText('在同一细胞中的位置', 173, 677, 21, '#afc8d7', 'center');
  ctx.save(); ctx.translate(171, 755); ctx.scale(.155, .155);
  ctx.fillStyle = '#13485a'; ctx.strokeStyle = '#7dd7df'; ctx.lineWidth = 9;
  ctx.beginPath(); ctx.ellipse(0, 0, 636, 350, 0, 0, TAU); ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#8767a7'; ctx.beginPath(); ctx.ellipse(-255, 0, 145, 132, 0, 0, TAU); ctx.fill();
  ctx.save(); ctx.globalAlpha *= state.cargoOpacity;
  ctx.fillStyle = '#ffb67c'; ctx.beginPath(); ctx.arc(state.cargo.x, state.cargo.y, 31, 0, TAU); ctx.fill(); ctx.restore();
  ctx.strokeStyle = '#ffc96e'; ctx.lineWidth = 10;
  const w = 1840 / state.camera.zoom, h = 736 / state.camera.zoom;
  ctx.strokeRect(state.camera.x - w / 2, state.camera.y - h / 2, w, h); ctx.restore();
  bioText('黄色框：当前视野', 173, 830, 21, '#efc681', 'center');
}
function renderBiology(time) {
  ctx.save(); ctx.globalAlpha = 1;
  const state = BiologyModel.sample(time, CUES);
  const bg = ctx.createRadialGradient(1050, 445, 40, 980, 475, 1120);
  bg.addColorStop(0, '#17354b'); bg.addColorStop(.5, '#0c2035'); bg.addColorStop(1, '#050c1b');
  ctx.fillStyle = bg; ctx.fillRect(0, 0, 1920, 1080);
  BiologyModel.draw(ctx, state, time);
  bioText('看见细胞的自我清理', 64, 66, 44, '#e7f4f7');
  bioText('动物细胞剖面 · 结构与过程为示意', 1844, 66, 24, '#88acbc', 'right');
  ctx.save(); ctx.strokeStyle = '#2f5065'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(64, 107); ctx.lineTo(1856, 107); ctx.stroke(); ctx.restore();
  const stage = time < mark(2) ? '这颗线粒体坏了，细胞怎么办？' : time < mark(3) ? '先看结构：两层膜与嵴' :
    time < mark(5) ? '隔离膜包裹 → 闭合' : time < mark(6) ? '把受损目标运到溶酶体旁' :
    time < mark(7) ? '外层膜融合，内容物留在内部' : time < mark(8) ? '内部水解酶分解内容物' :
    time < mark(9) ? '清除受损来源，回到整个细胞' : time < mark(10) ? '如果清理被阻，可能发生什么？' : '包裹 → 融合 → 降解';
  bioText(stage, 65, 157, 34, time < mark(2) ? '#ffc994' : '#a8e8de');
  const point = BiologyModel.project(state.cargo, state);
  if (time < mark(3)) {
    bioLabel('受损线粒体', point, Math.min(1500, point.x + 120), Math.max(226, point.y - 176), '#ffbd8e');
    if (state.camera.zoom < 1.5) bioLabel('细胞核', BiologyModel.project({x:-255,y:0}, state), 360, 263, '#c5a8df');
  } else if (time < mark(5)) {
    bioLabel(state.closed ? '自噬体：双膜已闭合' : '隔离膜：保留开放口', {x:point.x-95*state.camera.zoom,y:point.y}, 300, 233, '#d8dd9e');
  } else if (time < mark(8)) {
    const lyso = BiologyModel.project({x:lerp(430,325,state.fuse),y:-100}, state);
    bioLabel(state.fuse > .92 ? '自噬溶酶体' : '溶酶体', {x:lyso.x+80,y:lyso.y-60}, 1440, 228, '#c4adef');
    if (state.fuse > .92 && state.digest < .99) bioLabel(time < mark(7) ? '内层膜与内容物保留' : '内容物在内部降解', point, 398, 233, '#ffe0a2');
  }
  if (time >= mark(2) && time < mark(3)) {
    bioLabel('外膜', BiologyModel.project({x:state.cargo.x-43,y:state.cargo.y-40}, state), 332, 221, '#ffbd8e');
    bioLabel('内膜与嵴', BiologyModel.project({x:state.cargo.x+3,y:state.cargo.y+24}, state), 1180, 711, '#ffe0b4');
  }
  miniCell(state);
  bioText('颗粒与动作时间为示意，不代表实测数量或真实速率', 1845, 879, 22, '#7395a8', 'right');
  if (time >= mark(10)) {
    const p = clamp((time - mark(10)) / Math.max(1, FLAT[10].end - mark(10)));
    const names = ['包裹', '融合', '降解'];
    names.forEach((name, i) => {
      const x = 557 + i * 270;
      bioPanel(x, 787, 210, 63, i / 3 <= p ? '#1b4b50' : '#0c1d30', i / 3 <= p ? '#78d5bb' : '#355166');
      bioText(name, x + 105, 820, 31, '#d9f0e7', 'center');
    });
  }
  ctx.restore();
}
function absoluteScene(id, localTime) {
  renderBiology(window.TIMELINE.scenes.find(s => s.id === id).start + localTime);
}
SC.intro = (lt, S) => absoluteScene('intro', lt);
SC.journey = (lt, S) => absoluteScene('journey', lt);
SC.outro = (lt, S) => absoluteScene('outro', lt);
