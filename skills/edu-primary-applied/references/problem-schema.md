# 数据格式参考（problem-schema）

三种入口（文字 / 随机 / 给定参数）最终归一成同一份数据，注入模板 `template/board.html`
的数据岛 `<script id="lesson-data" type="application/json">__LESSON_DATA__</script>`。数据是
一个 JSON 对象，顶层 9 键（`type/lesson/scene/answer/diagram/readouts/status/steps/ui`，
另 `seed` 复现用）。区分题型靠 `type` + `scene.kind`，前端只硬编码三张分派表：
`STATE[type]`（t → vars）、`DRAW[scene.kind]`（主画布渲染器）、`DIAGRAM[diagram.kind]`
（副图渲染器，可选）。

## 顶层键

```jsonc
{
  "type": "sum-diff",           // 45 类：行程 pursue/meet/circular-same/circular-opp/midpoint-meet
                                // + 线段图 sum-diff/sum-multiple/diff-multiple/profit-loss/age/average/
                                //   unit/aggregate/boat/avgspeed
                                // + 其它 chicken-rabbit/plant/work/cycle/train
                                // + A组 fraction-part/fraction-whole/fraction-ratio/discount/percent-change/
                                //   ratio-share/ratio-scale/concentration/restore/average-move/stairs
                                // + B组 cows/phalanx/pigeonhole/clock/elimination/arithmetic-seq/optimize/
                                //   page-digit/sum-diff-three
                                // + C组 profit-loss-two-gain/profit-loss-two-loss/plant-one/plant-none/plant-ring
  "seed": 42,                   // 复现用
  "lesson": { "title": "和差问题", "problem": "…", "hint": "拖动滑块…" },
  "scene":  { /* 主画布：kind + param(滑块) + 类型专有数据 */ },
  "answer": { /* 各题型自定键，答案量恒整数 */ },
  "diagram": { /* 可选副图，如 st-graph */ },
  "readouts": [ /* 控制台读数 */ ],
  "status":  { "before": {"text":"…","color":"amber"}, "at": {…green}, "after": {…blue} },
  "steps":   [ { "title": "…", "content": "…" } ],
  "ui":      { "play": "▶ 播放", "pause": "⏸ 暂停", "sliderLabel": "较小数 a" }
}
```

## scene（主画布）

```jsonc
"scene": {
  "kind": "bar-model",          // road | circular | bar-model | swap | interval |
                                // progress | sequence | train | phalanx | clock
  "param": { "min": 1, "max": 39, "step": 1, "value": 1, "label": "较小数 a",
             "answer": 17 },     // 滑块目标（答案量），phase 与 verify 唯一数据源
  // —— road/circular 运动 ——
  "motion": { "kind": "linear", "direction": "same", "span": 96, "lap": null,
              "meetWord": "追上", "afterWord": "超过",
              "carA": {"name":"甲","color":"#e2553f","x0":0,"v":6},
              "carB": {"name":"乙","color":"#3b7dd8","x0":20,"v":4} },
  // —— bar-model 线段图 ——
  "rel":   { "bigOf": "sum-minus-a", "sum": 40 },   // 或 {"bigOf":"n-times-a","n":3}
  "bars":  [ {"name":"较小数","color":"#e2553f","var":"a"},   // var 单变量
             {"name":"较大数","color":"#3b7dd8","var":"b"} ], // 或 expr 复合表达式
  "scale": 40,
  "known": { /* 题型常量，供 STATE 里 expr 求值（如盈亏的 a/c/b/d、工程的 a/b） */ },
  "ref":   { "expr": "A", "label": "平均数" },       // 可选参照虚线
  "diffLabel": "相差"
}
```

`scene.param` 是滑块的 `min/max/step/value/label/answer`；`answer` 是滑块目标（答案量），
STATE 据此算 `phase`，`verify.mjs` 据此做「拨到答案变绿」断言。`step===1` 时前端播放采用
「整数扫动」（每 0.4s +1，精确命中答案），否则按时间连续推进（行程/火车过桥）。

## STATE[type] 语义（滑块值 t → vars）

`vars` 必须含 `t` 与 `phase`（`before`/`at`/`after`），其余键供 readouts 的 `expr` 求值。

| type | t 含义 | 关键变量 | phase 判据 |
| --- | --- | --- | --- |
| pursue / meet / circular-* | 时间（秒） | `ranA, ranB, dist, gapDist, nA, nB, posA, posB, vA, vB, L, span, tMeet` | `t` vs `tMeet` |
| sum-diff | 较小数 a | `a, b(=sum−a), sum, diff` | `a` vs `answer.small` |
| sum-multiple | 较小数 a（乙） | `a, b(=n·a), sum, diff` | `a` vs `answer.small` |
| diff-multiple | 较小数 a（乙） | `a, b(=n·a), sum, diff` | `a` vs `answer.small` |
| profit-loss | 人数 n | `n, first(=a·n+b), second(=c·n−d)` | `n` vs `answer.n` |
| age | 几年后 t | `t, son(=Q+t), dad(=P+t), diff, ratio` | `t` vs `answer.t` |
| average | 丙 z | `z, x, y, avg` | `z` vs `answer.z` |
| chicken-rabbit | 鸡数 c | `c, r(=H−c), heads, legs` | `c` vs `answer.c` |
| plant | 棵树 k | `k, gaps(=k−1), spacing(=D/gaps)` | `k` vs `answer.k` |
| work | 合做天数 t | `t, pctA, pctB, pctTotal` | `t` vs `answer.t` |
| cycle | 第 N 盏 | `N, r, colorName` | `N` vs `answer.N` |
| unit | 单价 u | `u, known(=m·u), wanted(=n·u)` | `u` vs `answer.u` |
| aggregate | 盒数 n | `n, perbox(=w/n), b` | `n` vs `answer.n` |
| boat | 水流 u | `u, v, downV(=v+u), upV(=v−u)` | `u` vs `answer.u` |
| train | 时间 t | `t, dist, remain` | `t` vs `answer.t` |
| avgspeed | 平均速度 v | `v, v1, v2, arith` | `v` vs `answer.avg` |
| fraction-part | 部分 p | `p(=t), W, n, d` | `t` vs `answer.part` |
| fraction-whole | 整体 w | `w(=t), n, d, part` | `t` vs `answer.W` |
| fraction-ratio | 分子 n | `n(=t), d, k, A(=t·k), B(=d·k)` | `t` vs `answer.n` |
| discount | 现价 p | `p(=t), A, d` | `t` vs `answer.price` |
| percent-change | 现价 p | `p(=t), A, x` | `t` vs `answer.price` |
| ratio-share | 每份 k | `k(=t), a, b, total` | `t` vs 每份 k |
| ratio-scale | 实际长度 r | `r(=t), n, d` | `t` vs `answer.real` |
| concentration | 盐 s | `s(=t), g, c` | `t` vs `answer.salt` |
| midpoint-meet | 时间 t | motionState 全套（含 `T, m`） | `t` vs `answer.t` |
| restore | 原来 W | `W(=t), X, r, a, b, c, d` | `t` vs `answer.W` |
| average-move | 给的个数 g | `g(=t), a, b` | `t` vs `answer.give` |
| stairs | 总时间/总长 total | `total(=t), gaps(=n−1), spacing, dots, gapVal, unit` | `t` vs `answer.total` |
| cows | 可吃天数 t | `grass(=G+g·t), eaten(=N·t), remain, g, N, G` | `t` vs `answer.t` |
| phalanx | 每边 n | `n(=t), total(=n²), outer(=4n−4)` | `t` vs `answer.n` |
| pigeonhole | 至少数 t | `m, n, cap(=n·t), short(=m−cap)` | `t` vs `answer.least` |
| clock | 夹角 t | `cur(=t), h, angle` | `t` vs `answer.angle` |
| elimination | 甲 x | `x(=t), y(=S1−t), z(=S3−t), sumBC` | `t` vs `answer.x` |
| arithmetic-seq | 第 n 项 an | `an(=t), a, d, n, inc(=t−a)` | `t` vs `answer.an` |
| optimize | 大船数 k | `k(=t), rest, small, bigCost, smallCost, cost, minCost` | `t` vs `answer.optK` |
| page-digit | 页数 n | `n(=t), one(=9), two(=2(n−9)), total, given` | `t` vs `answer.n` |
| sum-diff-three | 甲 a | `a(=t), b(=a−D), c(=n·a), sum` | `t` vs `answer.a` |
| profit-loss-two-gain / two-loss | 人数 t | `needA(=t·a), needC(=t·c), diff, total` | `t` vs `answer.n` |
| plant-one / plant-none / plant-ring | 棵树 k | plantState（`mode`=one/none/ring 驱动 gaps） | `k` vs `answer.k` |

> phase 一律由 `phaseOf(t, scene.param.answer)` 统一计算（`before`/`at`/`after`），
> STATE 里无需各自写三分支。

## DRAW / DIAGRAM 分派表

| scene.kind | 渲染器 | 覆盖题型 |
| --- | --- | --- |
| `road` | 直线道路 + 两车 + 相距箭头 | 追及 / 相遇 / 中点相遇 |
| `circular` | 环形跑道 + 两圆点 + 圈数 | 环形追及 / 环形相遇 |
| `bar-model` | 1..N 个色块 + 差段高亮 + 参照虚线 + 双箭头 | 和差 / 和倍 / 差倍 / 盈亏 / 年龄 / 平均数 / 归一 / 归总 / 流水行船 / 平均速度 / 分数 / 折扣 / 百分数 / 比例 / 浓度 / 还原 / 移多补少 / 牛吃草 / 抽屉 / 消去法 / 等差数列 / 最优化 / 页码 / 三数和差倍 / 盈亏两盈两亏 |
| `swap` | 点数 = 头数/腿数联动 | 鸡兔同笼 |
| `interval` | 路 + 树（点-段图，`mode` 驱动） | 植树 / 植树变体 / 爬楼 / 锯木 / 敲钟 |
| `progress` | 甲乙双进度条合做 | 工程 |
| `sequence` | 周期色块循环 + 游标 | 周期 |
| `train` | 桥 + 车身滑动 | 火车过桥 |
| `phalanx` | n×n 方阵点阵（外层红框 + 内层蓝点） | 方阵 |
| `clock` | 钟面（红时针 + 蓝分针 + 橙夹角弧） | 时钟夹角 |

| diagram.kind | 渲染器 |
| --- | --- |
| `st-graph` | 路程—时间图（两条直线 + 交点/圈线 + 时间游标） |

## answer（各题型键）

| 题型 | 键 |
| --- | --- |
| pursue | `tMeet, xMeet, gap, dv` |
| meet | `tMeet, xMeet, total, sumV` |
| circular-same | `tMeet, xMeet, gap(=L), dv, sMeet, lapsA, lapsB, lapGain(=1)` |
| circular-opp | `tMeet, xMeet, total(=L), sumV, sMeet` |
| sum-diff / sum-multiple / diff-multiple | `small, big`（`small` = 较小数 = 答案量，滑块目标） |
| profit-loss | `n, total`（人数与总数） |
| age | `t`（几年后） |
| average | `z`（丙） |
| chicken-rabbit | `c, r`（鸡、兔） |
| plant | `k, n`（棵树、间隔数） |
| work | `t`（合做天数） |
| cycle | `N, r, color`（第 N 盏、余数、颜色） |
| unit | `u, ans`（单价、n 件总价） |
| aggregate | `n, b`（盒数、每盒颗数） |
| boat | `u, v`（水流、静水） |
| train | `t`（过桥时间） |
| avgspeed | `avg`（平均速度） |
| fraction-part | `part`（部分） |
| fraction-whole | `W`（整体） |
| fraction-ratio | `n, d`（分子、分母） |
| discount | `price`（现价） |
| percent-change | `price`（现价） |
| ratio-share | `A, B`（甲、乙） |
| ratio-scale | `real`（实际长度） |
| concentration | `salt`（盐） |
| midpoint-meet | `t, m, T`（时间、中点偏移、全程） |
| restore | `W`（原来） |
| average-move | `give`（给的个数） |
| stairs | `total`（总时间/总长） |
| cows | `t, G`（天数、原有草） |
| phalanx | `n, total, outer`（每边、总数、外层） |
| pigeonhole | `least`（至少数） |
| clock | `angle`（夹角） |
| elimination | `x, y, z`（甲、乙、丙） |
| arithmetic-seq | `an`（第 n 项） |
| optimize | `optK, minCost`（最优船数、最低总价） |
| page-digit | `n, total`（页数、数字总数） |
| sum-diff-three | `a, b, c`（甲、乙、丙） |
| profit-loss-two-gain / two-loss | `n, total`（人数、总数） |
| plant-one / plant-none / plant-ring | `k, n`（棵树、间隔数） |

## readouts（控制台读数）

| kind | 必填 | 说明 |
| --- | --- | --- |
| `expr` | `expr`, `label` | 表达式在 `vars` 作用域求值（动态变量键）；`unit`、`decimals`、`color` 可选 |
| `gap` | `label` | 运动专用：动态「相距/还差」读数，前端按 kind×direction×phase 自动换词取值 |
| `laps` | — | circular-same 专用：显示「甲 n 圈 · 乙 n 圈」 |
| `answer` | `value` | 固定答案字符串，**绝不实时浮点重算** |

## 前端动态变量键 evalExpr

```js
function evalExpr(expr, vars) {
  var keys = Object.keys(vars);
  var ck = expr + "|" + keys.join(",");       // 缓存键 = expr + 键名列表
  var fn = _exprCache[ck] || buildFn(expr, keys);   // new Function(...MATH, ...keys, body)
  return fn.apply(null, MATH_vals.concat(keys.map(k => vars[k])));
}
```

变量键不再写死（旧版是固定 `KEY_ORDER`），因此「加一个新题型」只需在 `STATE` 里返回新的
vars 键集合，readouts 的 `expr` 即可引用，无需改求值器。
