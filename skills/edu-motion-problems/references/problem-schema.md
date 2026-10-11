# 数据格式参考（problem-schema）

三种入口（文字 / 随机 / 给定参数）最终归一成同一份数据，注入模板 `template/board.html` 的
数据岛 `<script id="lesson-data" type="application/json">__LESSON_DATA__</script>`。数据是一个
JSON 对象，顶层 9 键。区分题型只靠 `motion.kind` + `motion.direction`，前端只硬编码一个
`motionState(t)`。

## 顶层键

```jsonc
{
  "type": "pursue",            // pursue | meet | circular-same | circular-opp（机器用）
  "seed": 42,                  // 复现用，人类可不关心
  "lesson": { "title": "追及问题", "problem": "甲、乙…同向…乙在前 20 米…", "hint": "拖动时间滑块…" },
  "motion": { /* 运动模型：kind/direction/carA/carB/span/lap/tMax，见下 */ },
  "answer": { "tMeet": 10, "xMeet": 60, /* 各题型额外键见下 */ },
  "graph":  { /* s-t 图：xMax/yMax/xStep/yStep/lines/meet/laps */ },
  "readouts": [ /* 控制台读数，见下 */ ],
  "status":  { "before": {"text":"…","color":"amber"}, "at": {…green}, "after": {…blue} },
  "steps":   [ { "title": "求速度差", "content": "6 − 4 = 2（米）" } ],
  "ui":      { "play": "▶ 播放", "pause": "⏸ 暂停", "sliderLabel": "时间 t（秒）" }
}
```

## motion（运动模型）

```jsonc
"motion": {
  "kind": "linear",        // linear | circular
  "direction": "same",     // same(同向) | opposite(相向)
  "tMax": 15,              // tMeet + 5，动画/滑块上限
  "span": 96,              // linear：道路全长(米)；circular：一圈长(米)
  "lap": null,             // circular：一圈长 L；linear：null
  "meetWord": "追上",      // 追上 | 相遇
  "carA": { "name": "甲", "color": "#e2553f", "x0": 0,  "v": 6 },
  "carB": { "name": "乙", "color": "#3b7dd8", "x0": 20, "v": 4 }
}
```

`carB.x0` 语义（四种题型）：
- pursue：`x0 = gap`（乙在甲前方 gap 米）
- meet：`x0 = total`（两地相距 total）
- circular-same：`x0 = 0`（同点同向出发）
- circular-opp：`x0 = L`（同点相向出发，sB=L−vB·t 使初始 arc=0）

## answer（各题型额外键）

| 题型 | 键 |
| --- | --- |
| pursue | `tMeet, xMeet, gap, dv` |
| meet | `tMeet, xMeet, total, sumV` |
| circular-same | `tMeet, xMeet(=sMeet), gap(=L), dv, sMeet, lapsA, lapsB, lapGain(=1)` |
| circular-opp | `tMeet, xMeet(=sMeet), total(=L), sumV, sMeet` |

## graph（s-t 图）

```jsonc
"graph": {
  "xMax": 15, "yMax": 90, "xStep": 2, "yStep": 10,   // 轴范围与刻度（Python 已 ceil10，前端不自适应）
  "lines": [ {"name":"甲","color":"#e2553f","b":0,"k":6},
             {"name":"乙","color":"#3b7dd8","b":20,"k":4} ],   // y = b + k·x，x∈[0,xMax]
  "meet":  { "t": 10, "s": 60, "label": "追上", "mode": "cross" },  // mode: cross(直线相交) | lap(圈线)
  "laps": null            // circular-same 时为 [L, 2L, …]，画水平圈线；其余 null
}
```

乙线斜率：同向 `k = vB`（正），相向 `k = -vB`（负）。交点即追上/相遇点。`mode:"lap"` 时两线
同过原点不相交，追上点标在甲线上，垂直虚线标出「一圈 L 米」。

## readouts（控制台读数）

| kind | 必填 | 说明 |
| --- | --- | --- |
| `expr` | `expr`, `label` | 表达式在 `varsFor(st)` 作用域求值（`t/ranA/ranB/dist/nA/nB/vA/vB/L/gapDist/tMeet/span/…`）；`unit`、`decimals`、`color` 可选 |
| `gap` | `label` | 动态「相距/还差」读数，前端按 kind×direction×phase 自动换词与取值 |
| `laps` | — | circular-same 专用：显示「甲 n 圈 · 乙 n 圈」 |
| `answer` | `value` | 固定答案字符串，**绝不实时浮点重算**（避免「9.9 秒追上」假象） |

## 前端唯一硬编码：motionState(t)

```js
dirSign = direction==="same" ? 1 : -1
sA = vA·t;  sB = x0B + dirSign·vB·t
rate = direction==="same" ? vA−vB : vA+vB
initGap = kind==="circular" ? lap : x0B
gapDist = initGap − rate·t                    // 追上/相遇前为正，后为负
phase = t < tMeet−ε ? before : t ≤ tMeet+ε ? at : after
circular: posA = sA mod L; posB = sB mod L; nA = floor(sA/L); nB = floor(sB/L)
```
