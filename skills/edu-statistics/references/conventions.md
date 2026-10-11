# 统计解法配方与约定（conventions）

## 1. 好数配方表（答案先行拒绝采样）

核心思想：**先挑答案量与关系量，再反推已知量**——答案量天然整数，永不「算出答案再判规整」。

| 生成器 | 先挑 | 反推 | 约束 | 答案关系 |
| --- | --- | --- | --- | --- |
| `gen_stat_chart` | 跳绳 `a∈[3,8]`、篮球 `b∈[4,9]`、足球 `c∈[3,8]`、跑步 `d∈[3,10]`（答案量） | 全班 `T=a+b+c+d`、`maxBar=max(a,b,c,d)+2` | `d≤maxBar` | `d=T−a−b−c` |
| `gen_probability_tree` | 转盘 A `m∈{2,3}`、B `n∈{2,3}`、条件规则 `rule` | `total=m·n`、符合条件 `fav` | 规则恒整数 | `fav` 见下表 |

树状图条件规则 → 符合条件数（`fav` 恒整数、≥2，避免答案=初值）：

| rule | 条件 | fav |
| --- | --- | --- |
| `first` | 转盘 A 停红色 | `n` |
| `atleast` | 至少一个转盘停红色 | `m+n−1` |
| `same` | 两个转盘同色（`m==n`） | `m` |
| `different` | 两个转盘不同色（`m==n`） | `m·(m−1)` |

**统计好数约定（后续题型统一沿用）**：
- 数据样本取整数，总数为整数（必要时整十/整百）。
- 扇形占比角 = 整度数（挑 `占比 × 360° ∈ Z` 的数据）。
- 可能性（树状图）等可能事件数为整数，枚举不漏不重。

`MAX_ATTEMPTS=200`，失败抛 `NoGoodNumbers`。

## 2. 拖拽层约定（统计技能核心基建）

`scene` 里每个可拖点描述（`points[]` 项）：

```jsonc
{ "name": "barD", "x": 5.0, "y": 0,                   // 初始世界坐标
  "snap": "grid",                                     // grid=整数吸附 / half=半格
  "constraint": "v-line",                             // 竖向锁 x（拖柱顶）/ h-line 横向锁 y
  "ymin": 0, "ymax": 12,                              // 竖向夹取范围（世界坐标 y）
  "color": "#2ecc71", "label": "" }
```

- `fixed: true` = 不可拖。
- **命中检测与绘制共用同一 `geomTransform`**：DRAW 画柱必须走 `X(x)/Y(y)`，命中检测用
  `invX/invY` 反算，二者不得各写各的坐标换算。
- **竖向拖柱**：`constraint:"v-line"` 锁 x，`snap:"grid"` 四舍五入 y（柱高=整数），
  `ymin/ymax` 夹取柱高范围。
- **双向同步**：`dragToT` 指定可拖点，`dragAxis` 指定同步轴（`"x"` 默认 / `"y"` 竖向）。
  拖动点 ↔ 拨滑块，二者写同一值，无反馈环（程序写 `slider.value` 不触发 `input`）。
- 拖拽命中半径 20px；`pointerdown/move/up`（含触屏，兼容小程序 web-view）。

## 3. 渲染器家族（一个渲染器吃一类题型）

| scene.kind | 语义 | 吃进 |
| --- | --- | --- |
| `chart` | 柱/折线/扇形（当前柱），可拖柱顶补全缺失数据 | 统计图表（条形/折线/扇形） |
| `tree` | 树状图 + 拖数轴手柄数符合条件叶子 | 可能性 |

**关键**：渲染器按 `scene.kind` 复用，不是按题型各写一套。`chart`（条形图）与 `tree` 均已实现。

## 4. 关键坑（照抄即可避雷）

1. **零依赖**：`evalExpr` 用 `new Function(...names, body)`（**不要**写 `new Function.apply`
   ——严格模式下 `Function.apply` 是原型方法而非构造器）。
2. **动态变量键**：缓存键 `expr + '|' + Object.keys(vars).join(',')`；不同题型 vars 键不同，
   天然隔离。
3. **播放/滑块同步**：程序写 `slider.value=t` 不触发 `input`，无反馈环；`input` 里
   `playing=false`。
4. **帧率无关**：位置永远 `STATE[type](t, pts)` 解析计算（绝不逐帧累加），`dt=min(…,0.05)` 封顶。
5. **竖向吸附夹取**：`applySnap` 里先约束线（v-line 锁 x）、再 `snap` 吸附（四舍五入 y）、
   再 `ymin/ymax` 夹取，顺序不可颠倒。
6. **世界坐标 y 向上**：`Y(y) = oy + (yMax - y)·u`，命中反算 `invY = (yMax - (py - oy)/u)`。
7. **柱顶手柄画在 `T.Y(v.d)`**（用 STATE 夹取后的值），与 `pts.barD.y` 同步一致。
8. **答案读数用固定字符串** `readouts[kind="answer"].value`，绝不实时浮点重算。

## 5. 自检断言要点

- **答案一致**：`generators` 答案 == `answer` == `steps` 末步 == 前端 `STATE(t).phase==="at"`。
- **零依赖铁证**：无头打开 `file://` 断言 `requestfailed=0`、canvas 非空白。
- **拖柱顶**：拖到答案高度 → 读数正确 + 变绿；拖到非整数高度 → 吸附为整数。
- **双向同步**：拨滑块与拖柱顶写同一值，读数一致。
- 参考 `tests/test_generators.py`（1000 次抽样）与 `tests/test_builders.py`（schema 自检）。

## 6. 扩展配方（加题型五步）

1. `lib/generators.py` 加一个答案先行的 `gen_*`（保证统计量整数）。
2. `lib/builders.py` 加 `build_*`（复用 `_base`/`_expr`/`_answer`），选一个既有 `scene.kind`
   （`chart`/…）或新增家族。
3. `lib/steps.py` 加 `*_steps`。
4. `scripts/generate.py` 的 `REGISTRY` 注册；`template/board.html` 的 `STATE` 加对应
   `type`（若 scene.kind 是既有家族，DRAW 无需改动；否则加 DRAW 渲染器）。
5. `tests/` 补一条单测；`SKILL.md` 题型清单 + 本文件配方表各加一行。
