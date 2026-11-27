// 三棱锥 P-ABC：中位线证线面平行 + 二面角定高求体积（原 test-paper/index2.html）
// B 为原点，BA 沿 x，BC 沿 y，z 向上；AB = 2，BC = 2√2，PB = PC = √6 ⇒ PO = 2。
// 参数 a = ∠POF（度）：P 在过 O、垂直 BC 的平面内绕 BC 转动。
const EF = {a: 'E', b: 'F', c: 'violet', w: 3.4, glow: 1};
const PC = {a: 'P', b: 'C', c: 'orange', w: 3.4, glow: 1};
const angLabel = a => a.toFixed(0) + '°';
const volume = a => 4 * SQ2 / 3 * Math.sin(rad(a));       // ⅓ · 2√2 · 2 sin∠POF

const LESSON = {
  no: 15, score: '13 分', topic: '立体几何', topicEn: 'Geometry',
  chapter: '第三章 · 空间直线与平面', chapterEn: 'Solid Geometry',
  title: '中点与二面角里的三棱锥',
  subtitle: 'A tetrahedron, three midpoints, one hidden height.',
  stem: '如图，在三棱锥 $P-ABC$ 中，$AB$ ⊥ $BC$，$AB$ = 2，$BC$ = 2√2，$PB$ = $PC$ = √6，$BP$、$AP$、$BC$ 的中点分别为 $D$、$E$、$O$，点 $F$ 在 $AC$ 上，$BF$ ⊥ $AO$。',
  key: {scribble: '三个中点<br>+ BF⊥AO<br>→ 中位线！', formula: '线 ∥ 线 &nbsp;⟹&nbsp; 线 ∥ 面', caption: '第 (1) 问的钥匙；第 (2) 问靠二面角定高'},
  keywords: [['中位线', '三角形两边中点的连线，平行于第三边且等于它的一半。'], ['二面角', '在棱上一点，两个面内分别作棱的垂线所成的角。']],
  predict: {
    q: '三棱锥 $P-ABC$ 的体积是？',
    options: ['√6⁄3', '2√6⁄3', '√6', '4√2⁄3'], answer: 1, bigSize: 30,
    explain: '关键：∠$POF$ 是二面角，高 = $PO$·sin 60° = √3。',
    part: 1, challenge: '换坐标法再算一遍，<br>看看是不是也得 2√6⁄3。',
    dockMsg: '你的回合：先在左页猜一个体积',
  },
  given: '$AB$ ⊥ $BC$，$AB$ = 2，$BC$ = 2√2<br>$PB$ = $PC$ = √6，$BF$ ⊥ $AO$<br>$D$、$E$、$O$ 为 $BP$、$AP$、$BC$ 中点',
  legend: [{kind: 'line', c: 'violet', t: '要研究的线 $EF$'}, {kind: 'plane', c: 'blue', t: '平面 $ADO$'}, {kind: 'plane', c: 'pink', t: '平面 $POF$'}],
  methods: ['综合法', '坐标法'],
  props: {sticky: '第15题<br>先猜，再算 ✓<br>中位线!'},
  intro: {board: [['第15题 · 三棱锥 P−ABC', 18], ['AB⊥BC，AB=2，BC=2√2，PB=PC=√6', 12], ['(1) 求证：EF ∥ 平面 ADO', 13], ['(2) ∠POF=120°，求 V', 13], ['高 = PO·sin60° = √3 ？', 12, 'rgba(255,214,120,.9)']]},

  figure: {
    type: 'solid',
    caption: '三棱锥 $P-ABC$ · 双击复位',
    model(a) {
      const t = rad(a), P = {B: [0, 0, 0], A: [2, 0, 0], C: [0, 2 * SQ2, 0]};
      P.O = mid(P.B, P.C); P.F = mid(P.A, P.C);                       // BF ⊥ AO puts F at the midpoint of AC
      P.P = add(P.O, [2 * Math.cos(t), 0, 2 * Math.sin(t)]);
      P.D = mid(P.B, P.P); P.E = mid(P.A, P.P);
      P.G = lerp(P.A, P.O, 2 / 3);                                    // foot of B on AO
      P.H = [P.P[0], P.O[1], 0];                                       // foot of the height from P
      return P;
    },
    faces: [['A', 'B', 'C'], ['P', 'A', 'B'], ['P', 'B', 'C'], ['P', 'C', 'A']],
    param: {def: 120, min: 60, max: 170, step: 1, snap: 3, label: '拖动改变 ∠$POF$', show: angLabel,
            read: (a, ok) => '$V$ = ' + volume(a).toFixed(3) + (ok ? ' = 2√6⁄3' : '')},
    labelDir: {O: [.2, 1], F: [.5, 1], G: [.9, -.6], H: [-.6, .8], D: [-1, -.2], E: [.9, -.5]},
    baseSpec: {labels: ['D', 'E', 'O', 'F'], lines: ['DA', 'DO', 'AO', 'BF', 'EF', 'PO'].map(([a, b]) => ({a, b, c: 'ink', w: 1.2, dash: 1}))},
  },

  parts: [
    {q: '证明：$EF$ ∥ 平面 $ADO$', hover: 3, steps: [
      {h: '先把 F 的位置找出来',
       chain: [['tan∠$BAO$ = √2⁄2', 'BO = √2，AB = 2'], ['tan∠$ACB$ = √2⁄2', 'AB = 2，BC = 2√2'], ['∠$FBC$ = ∠$ACB$', 'BF ⊥ AO，同角的余角'], ['$FA$ = $FB$ = $FC$', '等角对等边']],
       cmap: {BAO: 'green', AO: 'green', BF: 'orange', ACB: 'blue', FBC: 'orange', FA: 'violet', FB: 'violet', FC: 'violet'},
       spec: {view: 120, labels: ['O', 'F', 'G'],
         lines: [{a: 'A', b: 'O', c: 'green', w: 3, glow: 1}, {a: 'B', b: 'F', c: 'orange', w: 3, glow: 1}],
         right: [{v: 'G', p: 'A', q: 'B', c: 'orange'}, {v: 'B', p: 'A', q: 'C', c: 'ink'}],
         ticks: [['A', 'F', 1], ['F', 'C', 1], ['B', 'O', 2], ['O', 'C', 2]],
         pts: [{p: 'F', c: 'violet'}],
         tag: {at: 'F', text: 'F 是 AC 中点', c: 'violet'}}},
      {h: 'EF 是 △APC 的中位线',
       chain: [['$E$、$F$ 分别为 $AP$、$AC$ 的中点', '已知 + 上一步'], ['$EF$ ∥ $PC$', '中位线定理']],
       cmap: {E: 'violet', F: 'violet', AP: 'orange', AC: 'orange', EF: 'violet', PC: 'orange', APC: 'orange'},
       spec: {view: 140, labels: ['E', 'F'],
         planes: [{pts: ['A', 'P', 'C'], c: 'orange'}],
         lines: [EF, PC], anim: slide('E', 'F', ['F', 'C']),
         ticks: [['A', 'E', 1], ['E', 'P', 1], ['A', 'F', 2], ['F', 'C', 2]],
         tag: {at: ['P', 'C'], text: 'EF ∥ PC', c: 'orange'}}},
      {h: '同理 DO ∥ PC',
       chain: [['$D$、$O$ 分别为 $BP$、$BC$ 的中点', '已知'], ['$DO$ ∥ $PC$', '△BPC 的中位线'], ['$EF$ ∥ $DO$', '平行于同一直线']],
       cmap: {D: 'blue', O: 'blue', BP: 'blue', BC: 'blue', DO: 'blue', PC: 'orange', EF: 'violet'},
       spec: {view: 160, labels: ['D', 'E', 'O', 'F'],
         planes: [{pts: ['B', 'P', 'C'], c: 'blue', op: .7}],
         lines: [EF, PC, {a: 'D', b: 'O', c: 'blue', w: 3.4, glow: 1}], anim: slide('D', 'O', ['O', 'C'], 'blue'),
         tag: {at: ['D', 'O'], text: 'DO ∥ PC', c: 'blue'}}},
      {h: '线 ∥ 线 ⟹ 线 ∥ 面',
       chain: [['$EF$ ∥ $DO$', '上一步'], ['$DO$ ⊂ 平面 $ADO$', ''], ['$EF$ ⊄ 平面 $ADO$', '这一条别漏写'], ['$EF$ ∥ 平面 $ADO$', '判定定理 ∎']],
       cmap: {EF: 'violet', DO: 'blue', ADO: 'blue'},
       full: '在 Rt△$ABO$ 中 tan∠$BAO$ = √2⁄2，在 Rt△$ABC$ 中 tan∠$ACB$ = √2⁄2，∴ ∠$BAO$ = ∠$ACB$。<br>又 $BF$ ⊥ $AO$，∴ ∠$ABF$ = ∠$BAC$，∠$FBC$ = ∠$ACB$，∴ $FA$ = $FB$ = $FC$，$F$ 为 $AC$ 中点。<br>' +
         '∵ $E$、$F$ 分别为 $AP$、$AC$ 中点，∴ $EF$ ∥ $PC$；同理 $DO$ ∥ $PC$，∴ $EF$ ∥ $DO$。<br>又 $DO$ ⊂ 平面 $ADO$，$EF$ ⊄ 平面 $ADO$，∴ $EF$ ∥ 平面 $ADO$。',
       spec: {view: 70, labels: ['D', 'E', 'O', 'F'],
         planes: [{pts: ['A', 'D', 'O'], c: 'blue'}],
         lines: [EF, {a: 'D', b: 'O', c: 'blue', w: 3.4, glow: 1}, {a: 'A', b: 'D', c: 'blue', w: 1.6}, {a: 'A', b: 'O', c: 'blue', w: 1.6}],
         anim: slide('E', 'F', ['E', 'D']),
         tag: {at: ['E', 'F'], text: 'EF ∥ 面 ADO', c: 'violet'}}},
    ]},
    {q: '若 ∠$POF$ = 120°，求三棱锥 $P-ABC$ 的体积', hover: 1, steps: [
      {h: '∠POF 为什么是二面角',
       chain: [['$PB$ = $PC$ ⟹ $PO$ ⊥ $BC$', '三线合一'], ['$OF$ ∥ $AB$ ⟹ $OF$ ⊥ $BC$', 'AB ⊥ BC'], ['$BC$ ⊥ 平面 $POF$', '线面垂直判定']],
       cmap: {PB: 'orange', PC: 'orange', PO: 'green', BC: 'orange', OF: 'green', AB: 'ink', POF: 'pink'},
       spec: {view: 35, labels: ['O', 'F'],
         planes: [{pts: ['P', 'O', 'F'], c: 'pink'}],
         lines: [{a: 'P', b: 'O', c: 'green', w: 3.4, glow: 1}, {a: 'O', b: 'F', c: 'green', w: 3.4, glow: 1}, {a: 'B', b: 'C', c: 'orange', w: 3, glow: 1}],
         right: [{v: 'O', p: 'P', q: 'C', c: 'green'}, {v: 'O', p: 'F', q: 'C', c: 'green'}],
         angles: [{v: 'O', p: 'P', q: 'F', c: 'pink', label: angLabel}],
         tag: {at: 'O', text: 'BC ⊥ 面 POF', c: 'pink'}}},
      {h: '高在面 POF 里',
       chain: [['$PO$ = √(6 − 2) = 2', 'Rt△POB'], ['作 $PH$ ⊥ 直线 $OF$ 于 $H$', ''], ['$PH$ ⊥ 平面 $ABC$', 'BC ⊥ 面 POF ⟹ BC ⊥ PH'], ['$h$ = 2 sin 60° = √3', '∠POH = 60°']],
       cmap: {PO: 'green', PH: 'violet', OF: 'green', H: 'violet', ABC: 'blue'},
       spec: {view: 25, labels: ['O', 'F', 'H'],
         planes: [{pts: ['A', 'B', 'C'], c: 'blue', op: .6}],
         lines: [{a: 'P', b: 'O', c: 'green', w: 3, glow: 1}, {a: 'O', b: 'F', c: 'green', w: 2.4}, {a: 'O', b: 'H', c: 'green', w: 1.6, dash: 1},
                 {a: 'P', b: 'H', c: 'violet', w: 3.6, glow: 1, grow: 1.2}],
         right: [{v: 'H', p: 'P', q: 'O', c: 'violet'}],
         angles: [{v: 'O', p: 'P', q: 'H', c: 'green', label: '60°', r: .45}],
         edgeLabels: [{a: 'P', b: 'O', t: '2', c: 'green'}],
         tag: {at: ['P', 'H'], text: 'h = √3', c: 'violet'}}},
      {h: '拖动滑块：二面角变，高就变',
       chain: [['$h$ = 2 sin(180° − ∠$POF$)', ''], ['$S$△$ABC$ = ½ · 2 · 2√2 = 2√2', ''], ['$V$ = ⅓ · 2√2 · $h$', '']],
       cmap: {POF: 'pink', ABC: 'blue'},
       spec: {view: 25, a: 150, slider: true, labels: ['O', 'H'],
         planes: [{pts: ['P', 'O', 'F'], c: 'pink'}],
         lines: [{a: 'P', b: 'O', c: 'green', w: 3}, {a: 'O', b: 'F', c: 'green', w: 2.4}, {a: 'O', b: 'H', c: 'green', w: 1.6, dash: 1}, {a: 'P', b: 'H', c: 'violet', w: 3.4, glow: 1}],
         right: [{v: 'H', p: 'P', q: 'O', c: 'violet'}],
         angles: [{v: 'O', p: 'P', q: 'F', c: 'pink', label: angLabel}],
         edgeLabels: [{a: 'P', b: 'H', t: a => 'h=' + (2 * Math.sin(rad(a))).toFixed(2), c: 'violet', flip: 1}]}},
      {h: '底面积 × 高 ÷ 3',
       chain: [['$S$△$ABC$ = ½ · $AB$ · $BC$ = 2√2', 'AB ⊥ BC'], ['$h$ = $PH$ = √3', '上一步'], ['$V$ = ⅓ · 2√2 · √3', '']],
       result: {k: '$V$', v: '2√6⁄3', note: '即三棱锥 P−ABC 的体积'},
       cmap: {ABC: 'blue', AB: 'blue', BC: 'blue', PH: 'violet'},
       full: '∵ $PB$ = $PC$，$O$ 为 $BC$ 中点，∴ $PO$ ⊥ $BC$，$PO$ = √(6 − 2) = 2。<br>由 (1) $OF$ ∥ $AB$，又 $AB$ ⊥ $BC$，∴ $OF$ ⊥ $BC$，∴ $BC$ ⊥ 平面 $POF$。<br>' +
         '过 $P$ 作 $PH$ ⊥ 直线 $OF$ 于 $H$，则 $BC$ ⊥ $PH$，∴ $PH$ ⊥ 平面 $ABC$。<br>∠$POH$ = 180° − 120° = 60°，$PH$ = 2 sin 60° = √3。<br>$V$ = ⅓ × ½ × 2 × 2√2 × √3 = 2√6⁄3。' +
         '<br><i>坐标法：</i>$B$ 为原点，$P$(−1, √2, √3)，高即 √3。',
       spec: {view: 50, labels: ['H'],
         planes: [{pts: ['A', 'B', 'C'], c: 'blue'}],
         lines: [{a: 'P', b: 'H', c: 'violet', w: 3.6, glow: 1}, {a: 'O', b: 'H', c: 'ink', w: 1.2, dash: 1}],
         right: [{v: 'H', p: 'P', q: 'O', c: 'violet'}, {v: 'B', p: 'A', q: 'C', c: 'blue'}],
         edgeLabels: [{a: 'A', b: 'B', t: '2', c: 'blue'}, {a: 'B', b: 'C', t: '2√2', c: 'blue'}],
         tag: {at: ['P', 'H'], text: 'V = 2√6⁄3', c: 'violet'}}},
    ]},
  ],
};
