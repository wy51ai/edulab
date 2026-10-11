# 数据格式参考（problem-schema · 统计）

三种入口（随机 / 给定种子）最终归一成同一份数据，注入模板 `template/board.html` 的数据岛
`<script id="lesson-data" type="application/json">__LESSON_DATA__</script>`。数据是一个 JSON
对象，顶层 9 键（`type/lesson/scene/answer/readouts/status/steps/ui`，另 `seed` 复现用）。
区分题型靠 `type` + `scene.kind`，前端只硬编码两张分派表：`STATE[type]`（t, pts → vars）、
`DRAW[scene.kind]`（主画布渲染器）。

## 顶层键

```jsonc
{
  "type": "stat-chart",           // 题型 slug（规划 2 类，见 SKILL.md）
  "seed": 42,                     // 复现用
  "lesson": { "title": "条形统计图 · 补全数据", "problem": "…", "hint": "拖动绿色柱顶…" },
  "scene":  { /* 主画布：kind + world(世界坐标) + cats(数据类别) + points(可拖柱顶) + param */ },
  "answer": { /* 各题型自定键，答案量恒整数 */ },
  "readouts": [ /* 控制台读数 */ ],
  "status":  { "before": {"text":"…","color":"amber"}, "at": {…green}, "after": {…blue} },
  "steps":   [ { "title": "…", "content": "…" } ],
  "ui":      { "play": "▶ 播放", "pause": "⏸ 暂停", "sliderLabel": "跑步人数 d" }
}
```

## scene（主画布）

```jsonc
"scene": {
  "kind": "chart",                // chart | tree（当前已实现 chart 的条形图）
  "cap":  "运动项目统计图（条形图）",
  "world": { "xMax": 6, "yMax": 13, "pad": 40 },   // 世界坐标（x=类别轴，y=数值轴）
  "cats": [
    { "name":"跳绳","color":"#e2553f","val":5,"x":1.0 },
    { "name":"篮球","color":"#3b7dd8","val":7,"x":2.33 },
    { "name":"足球","color":"#f5a623","val":4,"x":3.66 },
    { "name":"跑步","color":"#2ecc71","val":6,"x":5.0,"fill":true }   // fill = 缺省可补柱
  ],
  "points": [
    { "name":"barD","x":5.0,"y":0,"snap":"grid","constraint":"v-line",
      "ymin":0,"ymax":12,"color":"#2ecc71","label":"" }   // 可拖柱顶
  ],
  "known": { "a":5, "b":7, "c":4, "T":22, "maxBar":12 },
  "dragToT": "barD", "dragAxis": "y",      // 柱顶竖向 ↔ 滑块双向同步
  "param": { "min": 0, "max": 12, "step": 1, "value": 0,
             "label": "跑步人数 d", "answer": 6 }        // 滑块目标 = 答案量
}
```

- `world`：`x` 为类别轴、`y` 为数值轴（整数）；`geomTransform` 由此算 `X/Y/invX/invY`。
- `cats`：数据类别，`fill:true` 表示该柱缺省、由学生拖动补全（其 `val` 是答案，DRAW 用
  `v.d` 实时显示当前猜测）。
- `points`：可拖柱顶。`constraint:"v-line"` 竖向锁 x、`snap:"grid"` 吸附整数 y、
  `ymin/ymax` 夹取柱高。
- `dragToT` + `dragAxis`：可拖点与滑块双向同步的轴（`"x"` 默认 / `"y"` 竖向拖柱顶）。
- `param`：滑块 `min/max/step/value/label/answer`；`answer` 是答案量，`phase` 据此判定。

## STATE[type] 语义（滑块值 t + 可拖点 pts → vars）

`vars` 必须含 `t` 与 `phase`（`before`/`at`/`after`），其余键供 readouts 的 `expr` 求值。

| type | t 含义 | 关键变量 | phase 判据 |
| --- | --- | --- | --- |
| stat-chart | 跑步人数 d（柱高） | `a,b,c,d(=round(t)),total(=a+b+c+d),T,maxBar` | `d` vs `param.answer` |

> phase 一律由 `phaseOf(d, scene.param.answer)` 统一计算（注意是 `d` 不是 `t`，因为
> `d=round(t)` 夹取后才是真正答案量）。

## DRAW 分派表

| scene.kind | 渲染器 | 覆盖题型（规划） |
| --- | --- | --- |
| `chart` | 柱/折线/扇形（当前柱）+ 可拖柱顶 | 统计图表 |
| `tree` | 树状图 + 点选分支枚举 | 可能性 |

## answer（各题型键）

| 题型 | 键 |
| --- | --- |
| stat-chart | `d, T`（跑步人数、全班总数） |

## readouts（控制台读数）

| kind | 必填 | 说明 |
| --- | --- | --- |
| `expr` | `expr`, `label` | 表达式在 `vars` 作用域求值（动态变量键）；`unit`、`decimals`、`color` 可选 |
| `answer` | `value` | 固定答案字符串（目标总数等），**绝不实时浮点重算** |

## 前端动态变量键 evalExpr

```js
function evalExpr(expr, vars) {
  var keys = Object.keys(vars);
  var ck = expr + "|" + keys.join(",");       // 缓存键 = expr + 键名列表
  var fn = _exprCache[ck] || buildFn(expr, keys);   // new Function(...MATH, ...keys, body)
  return fn.apply(null, MATH_vals.concat(keys.map(k => vars[k])));
}
```

变量键不写死（按 vars 实际 key 构建），因此「加一个新题型」只需在 `STATE` 返回新的 vars
键集合，readouts 的 `expr` 即可引用，无需改求值器。
