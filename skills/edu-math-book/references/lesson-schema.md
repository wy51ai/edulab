# lesson.js 字段说明

`lesson.js` 是一段普通 JS，必须声明 `const LESSON = {...}`。可以在它前面声明辅助常量/函数（复用的线段样式、
数值函数）。`core.js` 的辅助函数可直接使用：`add sub mul dot mid len dist unit lerp cross centroidOf rad deg
SQ2 SQ3 SQ5 SQ6 foot(p,A,B) footPlane(p,A,B,C) angleAt(v,p,q) fix(v,d) slide(...) travel(...) pingpong ease`。

## 文本格式（所有文字字段通用）
| 写法 | 效果 |
|---|---|
| `$AB$`、`$A1B1$`、`$ABC1$` | 几何符号：斜体衬线，数字自动下标。草稿纸上由点名组成的符号会**悬停联动**图形（1 个字母=点，2 个=线段，≥3 个=面） |
| `\( … \)` | KaTeX 公式。字符串里含反斜杠时用 `String.raw\`…\``；手写时整个公式作为一笔写出 |
| `<br>`、`<i>…</i>` | 普通 HTML |
| `₁` | 在草稿纸文字里会变成下标 1 |

## 顶层字段
```js
const LESSON = {
  no: 15,                     // 题号（左页大号红字、图号 Fig. 15）
  score: '13 分',             // 可省
  topic: '立体几何',          // 顶栏 "互动试卷 · 立体几何专题"；页面标题
  topicEn: 'Geometry',        // 闹钟表盘上的小字
  chapter: '第三章 · 空间直线与平面', chapterEn: 'Solid Geometry',   // 页眉
  title: '中点里的直三棱柱',  // 左页大标题（≤ 10 个汉字）
  subtitle: 'A right prism, two midpoints, one hidden parallel.',   // 英文副标题，可省
  stem: '如图，在直三棱柱 $ABC-A1B1C1$ 中，…',                        // 题干（不含设问）
  key: {scribble: '两个中点<br>+ 公共顶点<br>→ 中位线！',            // 手写批注（3 行以内，每行 ≤ 6 字）
        formula: '线 ∥ 线 ⟹ 线 ∥ 面',                                // 关键结论（大字）
        caption: '线面平行的判定定理 —— 本题的钥匙'},
  keywords: [['中位线', '三角形两边中点的连线…'], …],               // 2–3 个，可省
  predict: {                                                          // 先猜再掀，可省
    q: '直线 $DE$ 到平面 $BCC1B1$ 的距离是？',
    options: ['√2⁄2', '1', '√2', '2'], answer: 1,                    // 4 个选项，answer 是下标
    big: '1',                // 纸片下的大号答案，默认 options[answer]；长答案配 bigSize: 30
    explain: '关键：…',      // 一句话点睛
    part: 1,                 // "看完整演示"跳到第几问（下标）
    challenge: '换坐标法再算一遍…',   // 右侧小挑战，可省
    dockMsg: '你的回合：先在左页猜一个距离',
  },
  given: '直棱柱：侧棱 ⊥ 底面<br>…',                                  // 右页"已知"卡片
  legend: [{kind: 'line', c: 'violet', t: '要研究的线 $DE$'}, {kind: 'plane', c: 'blue', t: '平面 $BCC1B1$'}],
  methods: ['综合法', '坐标法'],                                       // 右页方法标签（第一个圈出）
  capMain: '点“看演示”，图形会从纸上立起来。',                          // 可省
  props: {sticky: '第15题<br>先猜，再算 ✓', clock: 'GEOMETRY · 15'},   // 书桌道具上的字，可省
  folio: 30,                                                           // 页码，可省
  intro: {board: [['第15题 · 三棱锥 P−ABC', 18], ['(1) 求证：…', 13], ['提示…', 12, 'rgba(255,214,120,.9)']], duty: '值日：王'},
                             // 写了 intro 就带教室开场；board 是黑板文字 [文本, 字号, 颜色?]，每行 ≤ 22 字，最多 5 行
  figure: {...},             // 见下
  parts: [...],              // 见下
};
```

## figure
```js
figure: {
  type: 'solid' | 'plane' | 'none',
  caption: '直三棱柱 $ABC-A1B1C1$ · 双击复位',
  model(a) { return {A: [x, y, z], …}; },   // 所有命名点；a 是滑块参数（没有滑块也会传 param.def 或 0）
  param: {                    // 可省；有它才能在步骤里用 slider
    def: 2, min: .8, max: 3.6, step: .01,
    snap: .08,                // 拖到 def 附近自动吸附
    label: '拖动改变 $BC$',   // 滑块左侧说明
    show: a => a.toFixed(2),  // 滑块数值显示
    ok: a => a > -2 && a < 2, // 可省；"达成"判定（边框变绿），默认 = 吸附到 def
    read: (a, ok) => '∠$BC1C$ = ' + … ,   // 右侧读数
  },
  labelDir: {D: [0, 1], E: [-1, -.2]},     // 标签方向（屏幕坐标，y 向下），默认背离图形中心
  labels: ['M'],             // 始终显示名字的额外点（solid 的顶点自动显示）
  baseSpec: {...},           // 非演示状态、书页平面图上默认显示的 spec（虚线辅助线、点名）
  // solid 专用
  faces: [['A','B','C'], ['A','C','C1','A1'], …],   // 每个面按顶点顺序列出；边和外法向自动推出
  verts: [...],              // 默认 = faces 里出现的点
  round: [{type: 'cylinder'|'cone'|'frustum'|'sphere', at: 'O', r, h, r1, r2, axis: true}],  // 轴竖直
  extraEdges: [['A','C1']],  // 不属于任何面、但要画实线的棱
  yaw: 128, flatYaw: -2.2, flatPitch: .34, scale: 1,   // 初始视角/缩放微调
  // plane 专用
  view: {x: [-3, 3], y: [-5, 5]}, axes: true, grid: true, tickStep: 1, xLabel: 'x', yLabel: 'y',
  base: {curves: [...], lines: [...], …},   // 图形的常驻内容（每一步都画），写法同 spec
  // none 专用
  board: ['\\(a_n=2^n-1\\)', {t: '…', k: 1 /*红色强调*/}, {t: '…', note: 1 /*手写批注*/}],
}
```

## parts / steps
```js
parts: [
  {q: '证明：$DE$ ∥ 平面 $BCC1B1$',   // 左页设问
   name: '第 (1) 问',                 // 可省
   hover: 2,                          // 左页悬停时预览哪一步的 spec（默认最后一步）
   steps: [
     {h: '连 BC₁，DE 成了中位线',      // 这一步的标题（一句话，≤ 16 字）
      chain: [['在 △$ABC1$ 中，$D$、$E$ 为两边中点', '构造三角形'],   // [推理, 理由]，2–4 条，自动加 ⟹
              ['$DE$ ∥ $BC1$', '中位线定理']],
      cmap: {DE: 'violet', BC1: 'orange', ABC1: 'orange'},           // 符号着色（键 = $…$ 里的内容）
      result: {k: '$d$', v: '1', note: '即所求距离'},               // 可省；红圈结果
      full: '∵ … ∴ …',                                               // 可省；"规范作答"折叠区（每问最后一步写）
      spec: {...}},                                                  // 这一步图上高亮什么，见 renderers.md
   ]},
]
```

## 防闪烁（摘要，详见 SKILL.md 4.5）
`model` / 标签函数 / `read` / `anim` 都要是**纯函数且随参数连续**；面要**共面、凸、闭合**；`spec.view` 别侧对某个面；
引擎每帧都会重算，`model` 里别做重计算。check.mjs 的 `[lesson]` / `[flicker]` / `[render]` 告警必须清零。

## 常见错误
- `model()` 没返回某个在 spec/faces 里用到的点 → check.mjs 会报 `[lesson] point "X" is used but model() does not return it`。
- 用 slider 但没写 `figure.param`。
- KaTeX 字符串忘了 `String.raw`，导致 `\frac` 变成换页符。
- `predict.answer` 写成了答案文本而不是下标。
