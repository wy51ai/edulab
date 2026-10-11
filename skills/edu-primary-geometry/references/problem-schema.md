# 数据格式参考（problem-schema · 几何）

三种入口（随机 / 给定种子）最终归一成同一份数据，注入模板 `template/board.html` 的数据岛
`<script id="lesson-data" type="application/json">__LESSON_DATA__</script>`。数据是一个 JSON
对象，顶层 9 键（`type/lesson/scene/answer/readouts/status/steps/ui`，另 `seed` 复现用）。
区分题型靠 `type` + `scene.kind`，前端只硬编码两张分派表：`STATE[type]`（t, pts → vars）、
`DRAW[scene.kind]`（主画布渲染器）。

## 顶层键

```jsonc
{
  "type": "area-parallelogram",   // 题型 slug（规划 9 类，见 SKILL.md）
  "seed": 42,                     // 复现用
  "lesson": { "title": "平行四边形面积 · 剪拼", "problem": "…", "hint": "拖动绿色顶点 D…" },
  "scene":  { /* 主画布：kind + world(世界坐标) + points(可拖顶点) + param(阶段滑块) + known */ },
  "answer": { /* 各题型自定键，答案量恒整数 */ },
  "readouts": [ /* 控制台读数 */ ],
  "status":  { "before": {"text":"…","color":"amber"}, "at": {…green}, "after": {…blue} },
  "steps":   [ { "title": "…", "content": "…" } ],
  "ui":      { "play": "▶ 播放", "pause": "⏸ 暂停", "sliderLabel": "剪拼进度" }
}
```

## scene（主画布）

```jsonc
"scene": {
  "kind": "cut-rearrange",        // cut-rearrange | grid-split | grid | solid-views |
                                  // grid-transform | solid-net（当前已实现 cut-rearrange）
  "cap":  "平行四边形 → 长方形",
  "world": { "xMax": 8, "yMax": 5, "pad": 34 },   // 世界坐标（整数网格），等比缩放居中
  "points": [
    { "name":"A","x":0,"y":0,"fixed":true,"color":"#e2553f","label":"A" },
    { "name":"B","x":4,"y":0,"fixed":true,"color":"#3b7dd8","label":"B" },
    { "name":"D","x":2,"y":3,"snap":"grid","constraint":"h-line",
      "min":0,"max":3,"color":"#2ecc71","label":"D 拖我" }
  ],
  "known": { "a": 4, "h": 3 },    // 题型常量，供 STATE 求值
  "dragToT": null,                 // 可选：可拖点与滑块双向同步
  "param": { "min": 0, "max": 2, "step": 0.1, "value": 0,
             "label": "剪拼进度", "answer": 2 }    // 阶段滑块（answer = 结论阶段）
}
```

- `world`：整数网格世界坐标；`geomTransform` 由此算 `X/Y/invX/invY`（等比缩放、y 向上、居中）。
- `points`：可拖顶点。`fixed:true` 不可拖；`snap` = `grid`/`half`；`constraint` = `h-line`/
  `v-line`（等积变形沿底边平行线滑）；`min/max` 夹取范围。
- `param`：滑块 `min/max/step/value/label/answer`；面积推导当「阶段」用（`answer` = 结论阶段），
  标量答案题型当「答案量」用。
- `dragToT`：可拖点的 x 与滑块值 t 双向同步（拖点 ↔ 拨滑块）。

## STATE[type] 语义（滑块值 t + 可拖点 pts → vars）

`vars` 必须含 `t` 与 `phase`（`before`/`at`/`after`），其余键供 readouts 的 `expr` 求值。

| type | t 含义 | 关键变量 | phase 判据 |
| --- | --- | --- | --- |
| area-parallelogram | 剪拼阶段（0→2） | `a, h, dx(=P.D.x), S(=a·h)` | `t` vs `param.answer`(2) |

> phase 一律由 `phaseOf(t, scene.param.answer)` 统一计算，STATE 里无需各自写三分支。
> 带可拖点的题型，STATE 第二个参数 `pts` 取当前拖拽后的点坐标（如 `dx = pts.D.x`）。

## DRAW 分派表

| scene.kind | 渲染器 | 覆盖题型（规划） |
| --- | --- | --- |
| `cut-rearrange` | 网格 + 平行四边形/三角形/梯形/圆 + 可拖顶点 + 阶段剪拼插值 | 面积公式推导（平四/三角/梯形/圆） |
| `grid-split` | 方格纸 + 拖辅助线切分/添补 | 组合图形面积 |
| `grid` | 方格纸 + 点选半格着色计数 | 不规则图形估算 |
| `solid-views` | 拖小方块摆立体 + 三视图联动 | 观察物体/三视图 |
| `grid-transform` | 方格纸 + 拖图形/对应点 | 平移/旋转/轴对称 |
| `solid-net` | 长方体展开图 + 拖边长 | 长方体表面积/体积 |

## answer（各题型键）

| 题型 | 键 |
| --- | --- |
| area-parallelogram | `S, a, h`（面积、底、高） |

## readouts（控制台读数）

| kind | 必填 | 说明 |
| --- | --- | --- |
| `expr` | `expr`, `label` | 表达式在 `vars` 作用域求值（动态变量键）；`unit`、`decimals`、`color` 可选 |
| `answer` | `value` | 固定答案字符串（公式），**绝不实时浮点重算** |

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
