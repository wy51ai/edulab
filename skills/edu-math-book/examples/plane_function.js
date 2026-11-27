// 函数与导数：f(x) = x³ − 3x + a 的单调性、极值与零点个数（plane 渲染器范例）
// sympy 已核：f'(x) = 3(x+1)(x−1)；极大 f(−1) = a+2，极小 f(1) = a−2；三个零点 ⇔ −2 < a < 2
const f = (x, a) => x ** 3 - 3 * x + a;
const fp = x => 3 * x * x - 3;
const F = {f, c: 'ink', w: 2.4, label: {t: 'y = f(x)', at: 1.95, dx: 8, dy: 4}};

const LESSON = {
  no: 21, score: '12 分', topic: '函数与导数', topicEn: 'Calculus',
  chapter: '第五章 · 导数的应用', chapterEn: 'Derivatives',
  title: '一个三次函数的三个零点',
  subtitle: 'Two turning points decide how many times the curve meets the axis.',
  stem: String.raw`已知函数 \(f(x)=x^3-3x+a\)，\(a\in\mathbb{R}\)。`,
  key: {scribble: '零点个数<br>看极值<br>的符号！', formula: String.raw`极大值 \(>0\) 且 极小值 \(<0\)`, caption: '三次函数有三个零点的判定'},
  keywords: [['极值点', String.raw`\(f'(x_0)=0\) 且两侧导数异号的点。`], ['零点', '方程 f(x) = 0 的实根，也是图像与 x 轴的交点。']],
  predict: {
    q: '要让 f(x) 有三个零点，a 的取值范围是？',
    options: ['(−2, 2)', '(−∞, 2)', '[−2, 2]', '(0, 2)'], answer: 0, bigSize: 30,
    explain: '关键：极大值 a+2 > 0，极小值 a−2 < 0。',
    part: 1, challenge: '端点 a = ±2 时<br>有几个零点？',
    dockMsg: '你的回合：先在左页猜一个范围',
  },
  given: String.raw`\(f(x)=x^3-3x+a\)<br>\(a\) 为实数参数`,
  legend: [{kind: 'line', c: 'orange', t: String.raw`导函数 \(f'(x)\)`}, {kind: 'line', c: 'green', t: '递增段'}, {kind: 'line', c: 'pink', t: '递减段'}],
  methods: ['导数法', '数形结合'],

  figure: {
    type: 'plane',
    caption: String.raw`\(y=x^3-3x+a\) 的图像 · 拖滑块改变 \(a\)`,
    view: {x: [-3, 3], y: [-5, 5]},
    model: a => ({M: [-1, a + 2], N: [1, a - 2]}),
    labelDir: {M: [0, -1], N: [0, 1]},
    param: {def: 0, min: -4, max: 4, step: .01, label: '拖动改变 \\(a\\)', show: a => a.toFixed(2),
            ok: a => a > -2 && a < 2,
            read: (a, ok) => `零点 ${ok ? 3 : Math.abs(Math.abs(a) - 2) < .02 ? 2 : 1} 个`},
    base: {curves: [F]},
    baseSpec: {},
  },

  parts: [
    {q: '求 f(x) 的单调区间与极值', steps: [
      {h: '先求导，找导数的零点',
       chain: [[String.raw`\(f'(x)=3x^2-3\)`, '求导'], [String.raw`\(=3(x+1)(x-1)\)`, '因式分解'], [String.raw`\(f'(x)=0\Rightarrow x=\pm1\)`, '两个临界点']],
       spec: {curves: [{f: fp, c: 'orange', w: 2.4, dash: 1, x: [-2.2, 2.2], label: {t: "y = f'(x)", at: 2.05, dx: -60, dy: -6}}],
              pts: [{p: [-1, 0], c: 'orange'}, {p: [1, 0], c: 'orange'}],
              texts: [{at: [-1, 0], t: '−1', c: 'orange', dy: 18}, {at: [1, 0], t: '1', c: 'orange', dy: 18}]}},
      {h: '看导数的符号定单调',
       chain: [[String.raw`\(x<-1\) 或 \(x>1\)：\(f'(x)>0\)`, '递增'], [String.raw`\(-1<x<1\)：\(f'(x)<0\)`, '递减']],
       spec: {curves: [{f, x: [-3, -1], c: 'green', w: 3.6}, {f, x: [-1, 1], c: 'pink', w: 3.6}, {f, x: [1, 3], c: 'green', w: 3.6},
                       {f: fp, c: 'orange', w: 1.4, dash: 1, x: [-2.2, 2.2], op: .6}],
              regions: [{f: fp, x: [-1, 1], c: 'pink', op: .8}]}},
      {h: '极大在 x = −1，极小在 x = 1',
       chain: [[String.raw`极大值 \(f(-1)=a+2\)`, '先增后减'], [String.raw`极小值 \(f(1)=a-2\)`, '先减后增']],
       result: {k: '增区间', v: String.raw`\((-\infty,-1),(1,+\infty)\)`, note: '；减区间 (−1, 1)'},
       full: String.raw`\(f'(x)=3x^2-3=3(x+1)(x-1)\)。<br>当 \(x<-1\) 或 \(x>1\) 时 \(f'(x)>0\)，\(f(x)\) 单调递增；当 \(-1<x<1\) 时 \(f'(x)<0\)，\(f(x)\) 单调递减。<br>∴ 极大值 \(f(-1)=a+2\)，极小值 \(f(1)=a-2\)。`,
       spec: {labels: ['M', 'N'], drops: [{p: 'M', c: 'green'}, {p: 'N', c: 'pink'}],
              pts: [{p: 'M', c: 'green'}, {p: 'N', c: 'pink'}],
              tag: {at: 'M', text: '极大 a+2', c: 'green'}}},
    ]},
    {q: '若 f(x) 有三个零点，求 a 的取值范围', steps: [
      {h: '拖动滑块：曲线上下平移',
       chain: [['a 只让图像上下平移', '形状不变'], ['数一数与 x 轴的交点', '零点个数']],
       spec: {slider: true, a: 3, labels: ['M', 'N'], lines: [{a: [-3, 0], b: [3, 0], c: 'blue', w: 2.6, glow: 1}],
              pts: [{p: 'M', c: 'green'}, {p: 'N', c: 'pink'}]}},
      {h: '三个零点 ⟺ 极大值 > 0 > 极小值',
       chain: [[String.raw`\(f(-1)=a+2>0\)`, '左峰在轴上方'], [String.raw`\(f(1)=a-2<0\)`, '右谷在轴下方'], [String.raw`\(-2<a<2\)`, '两式同时成立']],
       result: {k: 'a', v: String.raw`\((-2,\,2)\)`, note: ''},
       full: String.raw`由 (1)，\(f(x)\) 在 \(x=-1\) 处取极大值 \(a+2\)，在 \(x=1\) 处取极小值 \(a-2\)。<br>\(f(x)\) 有三个零点 \(\Leftrightarrow\) \(\begin{cases}a+2>0\\a-2<0\end{cases}\)，解得 \(-2<a<2\)。`,
       spec: {labels: ['M', 'N'], drops: [{p: 'M', c: 'green'}, {p: 'N', c: 'pink'}], lines: [{a: [-3, 0], b: [3, 0], c: 'blue', w: 2.2}],
              pts: [{p: 'M', c: 'green'}, {p: 'N', c: 'pink'}],
              tag: {at: 'N', text: '−2 < a < 2', c: 'violet'}}},
    ]},
  ],
};
