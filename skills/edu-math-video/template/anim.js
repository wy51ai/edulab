/* Scenes for ONE problem. This whole file is problem-specific: rewrite it for every new video.
 * Helpers (draw, txt, board, bl, problemCard, hiBox, stamp, puff, pr/L3 for 3D, ...) come from engine.js.
 *
 * Contract with script.json:
 *   - every "scene" id in script.json needs SC.<id> here and a TAGS entry
 *   - SC.<id>(lt, S): lt = seconds since the scene started. Time every animation from S.cue(k) / S.at(k, f),
 *     the moment narration line k starts, so pictures appear exactly when they are mentioned. Never hardcode
 *     absolute seconds: line lengths change whenever the narration is re-generated.
 * Layout: figure in the left half (x 60..900), board on the right (x 930..1870), everything above y = 860.
 *
 * Example problem (replace): 在Rt△ABC中，∠C=90°，AC=3，BC=4，点D是斜边AB的中点，求线段CD的长。
 */

// ---------------------------------------------------------------- problem image + highlight boxes
// srcW/srcH = real pixel size of problem.png. boxes = source-pixel [x0, y0, x1, y1] (or lists of them),
// from scripts/make_problem_png.py (text) or scripts/problem_boxes.py (screenshot).
const PROBLEM = {
  src: 'problem.png', srcW: 1500, srcH: 240,
  boxes: {
    rightAngle: [[510, 44, 739, 116]],
    AC: [[773, 44, 915, 116]],
    BC: [[949, 44, 1089, 116]],
    mid: [[1123, 44, 1422, 116], [34, 124, 184, 196]],
    ask: [[218, 124, 530, 196]],
  },
};

// ---------------------------------------------------------------- scene tags (top-left): [number, 中文, English]
const TAGS = {
  intro: ['01', '审题 · 读条件', 'Read the problem'],
  figure: ['02', '画图', 'Draw the figure'],
  key: ['03', '关键结论', 'Key fact'],
  solve: ['04', '计算', 'Compute'],
  outro: ['05', '方法小结', 'Recap'],
};

// ---------------------------------------------------------------- the figure (left half)
// Pick a scale so the whole figure fits x 60..900, y 130..860 with room for labels.
const K = 130;                                  // px per unit length
const Cp = [190, 720], Ap = [190, 720 - 3 * K], Bp = [190 + 4 * K, 720];
const Dp = mid(Ap, Bp), Ep = [2 * Dp[0] - Cp[0], 2 * Dp[1] - Cp[1]];   // E: C reflected through D

/** st = per-element progress 0..1 (undefined = hidden). Scenes turn pieces on as the narration reaches them.
 *  st.glow = {AC, BC, AB, CD, CE: 0..1}: highlighter under the segment the narration is talking about right now. */
function fig(st) {
  const tri = st.tri === undefined ? 1 : st.tri, g = st.glow || {};
  glow([Cp, Ap], C.blue, g.AC || 0); glow([Cp, Bp], C.blue, g.BC || 0); glow([Ap, Bp], C.yellow, g.AB || 0);
  glow([Cp, Dp], C.red, g.CD || 0);  glow([Cp, Ep], C.green, g.CE || 0);
  if (st.rect) fillPts([Ap, Cp, Bp, Ep], C.green, 0.10 * st.rect);
  if (st.circle) draw(ellPts(Dp[0], Dp[1], 5 / 2 * K, 5 / 2 * K, PI * 0.75, PI * 0.75 + TAU * st.circle, 120), { c: C.purple, w: 3.5, dash: [10, 8], single: true, rough: 0.4 });
  draw([Cp, Ap], { w: 5, p: clamp(tri * 3), seed: 1 });
  draw([Cp, Bp], { w: 5, p: clamp(tri * 3 - 1), seed: 2 });
  draw([Ap, Bp], { w: 5, p: clamp(tri * 3 - 2), seed: 3 });
  if (st.right) rightM(Cp, Ap, Bp, C.ink, 28, st.right);
  ptLabel('C', Cp, -34, 26, clamp(tri * 3));
  ptLabel('A', Ap, -34, -10, clamp(tri * 3 - 0.5));
  ptLabel('B', Bp, 32, 26, clamp(tri * 3 - 1.5));
  if (st.len) {
    txt('3', Cp[0] - 36, (Cp[1] + Ap[1]) / 2, { size: 42, f: MF, c: C.blue, pop: st.len });
    txt('4', (Cp[0] + Bp[0]) / 2, Cp[1] + 44, { size: 42, f: MF, c: C.blue, pop: clamp(st.len * 2 - 1) });
  }
  if (st.ab) { const q = mix2(Ap, Bp, 0.28); txt(st.ab, q[0] + 30, q[1] - 34, { size: 42, f: MF, c: C.red, al: 'left' }); }
  if (st.seek !== undefined && st.seek < 1) {  // "take the midpoint": a marker slides along AB and stops at D
    const q = mix2(Ap, Dp, eio(st.seek)); dot(q[0], q[1], C.red, 9);
  }
  if (st.D) {
    ptLabel('D', Dp, 30, -22, st.D, C.red);
    tickM(Ap, Dp, 1, C.red, st.D); tickM(Dp, Bp, 1, C.red, st.D);
  }
  if (st.CD) draw([Cp, Dp], { c: C.red, w: 6, p: st.CD, seed: 4 });
  if (st.E) {  // extend CD to E, then the rectangle ACBE
    draw([Dp, Ep], { c: C.green, w: 4, dash: [12, 10], p: st.E, single: true, rough: 0.3 });
    ptLabel('E', Ep, 30, -14, clamp(st.E * 2 - 1), C.green);
  }
  if (st.rect) {
    draw([Ap, Ep], { c: C.green, w: 4, p: st.rect, seed: 5 });
    draw([Bp, Ep], { c: C.green, w: 4, p: st.rect, seed: 6 });
  }
}

// ---------------------------------------------------------------- scenes
// Every narration line: highlight what is named (glow + bump), do ONE motion that shows the reasoning
// (slideSeg / draw-on / moving point / countTo), leave a mark. See storyboard.md for the plan of each line.
const SC = {};

// 01: title, the problem image, and one highlight box per condition AS IT IS READ
SC.intro = (lt, S) => {
  const { P, at } = S;
  txt('直角三角形 · 例题精讲', 960, 150, { size: 62, p: P(0.2, 0.9) });
  txt('Right triangle: the median to the hypotenuse', 960, 202, { size: 34, f: EN, c: C.blue, p: P(0.6, 0.8) });
  problemCard(P(0.4, 0.7));
  const B = PROBLEM.boxes;
  hiBox(B.rightAngle, C.yellow, at(0, 0.6), lt);
  hiBox(B.AC, C.blue, at(1, 0.2), lt);
  hiBox(B.BC, C.blue, at(1, 0.6), lt);
  hiBox(B.mid, C.green, at(2, 0.2), lt);
  hiBox(B.ask, C.red, at(3, 0.1), lt);
  chip('∠C = 90°', 420, C.yellow, P(at(0, 0.8), 0.5));
  chip('AC = 3   BC = 4', 800, C.blue, P(at(1, 0.8), 0.5));
  chip('D 是 AB 中点', 1200, C.green, P(at(2, 0.6), 0.5));
  chip('求 CD', 1540, C.red, P(at(3, 0.5), 0.5));
};

// 02: draw the figure piece by piece; each named side lights up as it is read
SC.figure = (lt, S) => {
  const { P, at } = S;
  fig({ tri: P(0.3, 1.8), right: P(at(0, 0.3), 0.5), len: P(at(0, 0.55), 0.8),
    glow: { AC: bump(lt, at(0, 0.45)), BC: bump(lt, at(0, 0.7)), AB: bump(lt, at(1), 1.4), CD: bump(lt, at(1, 0.7)) },
    seek: P(at(1, 0.1), 1.0), D: P(at(1, 0.45), 0.5), CD: P(at(1, 0.6), 0.8) });
  board(1);
  bl(0, '已知 Given:', 0, lt, { c: C.gray, size: 32 });
  bl(1, '∠C = 90°', at(0, 0.2), lt);
  bl(2, 'AC = 3，BC = 4', at(0, 0.6), lt, { c: C.blue });
  bl(3, 'D 是 AB 中点：AD = DB', at(1, 0.2), lt, { c: C.red });
  bl(5, '求 Find:  CD = ?', at(1, 0.7), lt, { size: 46 });
  puff(1790, 820, 0.5, { look: [-1, -1] });
};

// 03: the key fact, SHOWN: CD swings onto DA and DB (all equal -> a circle), then the rectangle explains why
SC.key = (lt, S) => {
  const { P, at } = S;
  fig({ len: 1, right: eio(P(at(0, 0.1), Math.max(0.8, S.dur(0) * 0.55))), D: 1, CD: 1, circle: eio(P(at(1, 0.7), 1.2)), E: P(at(2, 0.2), 1.0), rect: P(at(3, 0.35), 0.8),
    glow: { CD: bump(lt, at(1), 1.0) + bump(lt, at(4, 0.6)), AB: bump(lt, at(4, 0.1), 1.6), CE: bump(lt, at(4, 0.1), 1.6) } });
  slideSeg(Cp, Dp, Dp, Ap, eio(P(at(1, 0.2), 0.9)), { c: C.red });     // copy of CD lands on DA
  slideSeg(Cp, Dp, Dp, Bp, eio(P(at(1, 0.45), 0.9)), { c: C.red });    // ... and on DB
  if (lt < at(4, 0.9)) slideSeg(Cp, Dp, Dp, Ep, eio(P(at(2, 0.35), 0.9)), { c: C.green, a: 0.7 });  // DE = CD
  slideSeg(Cp, Ep, Ap, Bp, eio(P(at(4, 0.25), 1.2)) * (1 - P(at(4, 0.85), 0.4)), { c: C.green, w: 6 });  // diagonal CE -> AB
  // Check the midpoint condition by sliding a copy of AD onto DB before stating the theorem.
  if (lt < at(1)) slideSeg(Ap, Dp, Dp, Bp, eio(P(at(0, 0.25), Math.max(1, S.dur(0) * 0.55))), { c: C.red, w: 6 });
  board(1);
  bl(0, '条件 Conditions:', 0, lt, { c: C.gray, size: 32 });
  bl(1, '∠C = 90°（已知）', at(0, 0.1), lt);
  bl(2, 'AD = DB（D 是中点）', at(0, 0.5), lt, { c: C.red });
  bl(3, 'CD = ½ AB', at(1, 0.3), lt, { c: C.red, size: 44 });
  bl(4, '延长 CD：DE = CD', at(2, 0.3), lt, { c: C.green });
  bl(5, '对角线互相平分 ⇒ 平行四边形', at(3, 0.15), lt, { c: C.green, size: 30 });
  bl(6, '∠C = 90° ⇒ 矩形', at(3, 0.6), lt);
  bl(7, 'CE = AB ⇒ CD = ½ AB', at(4, 0.6), lt, { size: 42 });
};

// 04: the computation; the figure keeps pointing at the quantity being computed
SC.solve = (lt, S) => {
  const { P, at } = S;
  const grow = P(at(0, 0.5), Math.max(0.8, S.dur(0) * 0.45));   // AB "measured" while the sum is spoken
  fig({ len: 1, right: 1, D: 1, CD: 1,
    glow: { AC: bump(lt, at(0, 0.15)), BC: bump(lt, at(0, 0.3)), AB: grow * (1 - P(at(1), 0.4)), CD: P(at(1, 0.55), 0.4) },
    ab: lt > at(0, 0.5) ? `AB = ${countTo(0, 5, grow, grow < 1 ? 1 : 0)}` : null });
  slideSeg(Dp, Bp, Cp, Dp, eio(P(at(1, 0.2), 1.0)), { c: C.red });     // half of AB lands on CD
  if (lt > at(1, 0.55)) { const q = mid(Cp, Dp); txt(`CD = ${countTo(0, 2.5, P(at(1, 0.55), 0.8), 1)}`, q[0] + 20, q[1] + 40, { size: 40, f: MF, c: C.red, al: 'left' }); }
  board(1);
  bl(0, '计算 Compute:', 0, lt, { c: C.gray, size: 32 });
  bl(1, '勾股定理：AB² = AC² + BC²', at(0, 0.05), lt);
  bl(2, 'AB² = 3² + 4² = 25', at(0, 0.4), lt);
  bl(3, 'AB = 5', at(0, 0.75), lt, { c: C.blue, size: 46 });
  bl(5, 'CD = AB ÷ 2 = 2.5', at(1, 0.2), lt, { c: C.red, size: 50 });
  stamp(1560, 760, '答：CD = 2.5', P(at(1, 0.7), 0.5), C.red, 50);
};

// 05: recap cards, then mascot + answer bubble
SC.outro = (lt, S) => {
  const { P, at } = S;
  const cards = [
    ['直角三角形', '斜边中点', 'midpoint of hypotenuse', C.green, 0.05],
    ['斜边中线', '= 斜边一半', 'median = half of it', C.blue, 0.35],
    ['勾股定理', '求出斜边', 'Pythagoras for AB', C.red, 0.65],
  ];
  grp(1 - P(at(1), 0.5), () => {
    cards.forEach(([top, zh, en, col, f], i) => {
      const x = 400 + i * 560, y = 450, p = P(at(0, f), 0.7);
      if (p <= 0) return;
      scaleAt(x, y, back(p), () => {
        const pts = [[x - 225, y - 225], [x + 225, y - 222], [x + 228, y + 222], [x - 226, y + 226], [x - 225, y - 225]];
        fillPts(pts, '#fffdf7');
        draw(pts, { c: col, w: 5, seed: i });
        txt(top, x, y - 105, { size: 60, c: col });
        arrow([[x, y - 40], [x, y + 20]], { c: C.ink, w: 5, head: 14 });
        txt(zh, x, y + 85, { size: 54 });
        txt(en, x, y + 150, { size: 32, f: EN, c: C.gray });
      });
    });
  });
  grp(P(at(1), 0.5), () => {
    puff(760, 560, 1.3 * back(P(at(1, 0.05), 0.6)), { wave: true });
    bubble(1080, 420, lt < at(2) ? '答案：CD = 2.5' : '迁移：CD = 5', P(at(1, 0.2), 0.5), { size: 50, c: C.red });
    txt(lt < at(2) ? '斜边中线 = 斜边一半' : 'AB = 10 ⇒ CD = 5', 960, 160, { size: 72, pop: P(at(1, 0.4), 0.6) });
    txt('See you next problem!', 960, 238, { size: 40, f: EN, c: C.blue, pop: P(at(1, 0.6), 0.6) });
  });
};
