# 几何解法配方与约定（conventions）

## 1. 好数配方表（答案先行拒绝采样）

核心思想：**先挑答案量（面积/体积）与关系量，再反推已知量**——答案量天然整数，永不
「算出答案再判规整」。

| 生成器 | 先挑 | 反推 | 约束 | 答案关系 |
| --- | --- | --- | --- | --- |
| `gen_area_parallelogram` | 底 `a∈[4,8]`、高 `h∈[3,5]`、初始歪斜 `dx0∈[1,2]` | `S=a·h`、可拖范围 `dxMax` | `0≤dx0≤dxMax` | `S=底×高` |
| `gen_area_triangle` | 底 `a∈{4,6,8}`(偶)、高 `h∈[3,5]`、顶点 `cx0∈[2,a-1]` | `S=a·h÷2`、顶点范围 `[1,a-1]` | `a·h` 偶 | `S=底×高÷2` |
| `gen_area_trapezoid` | 上底 `a∈[2,4]`、下底 `b∈[5,8]`、高 `h∈[3,5]` | `S=(a+b)·h÷2`、上底右端 `dx∈[a,b]` | `(a+b)·h` 偶 | `S=(上+下)×高÷2` |
| `gen_area_circle` | 半径 `r∈[3,6]` | `S=3r²`、等分数 `N∈[4,16]` | π≈3 | `S=πr²≈3r²` |
| `gen_composite_area` | 竖矩形 `a∈[2,5]×H∈[4,7]`、横矩形 `b∈[3,6]×h∈[2,3]` | `S=a·H+b·h`、切线 `x=a` | `h<H` | `S=两矩形和` |
| `gen_grid_count` | 方格纸 `G∈[6,8]`、半格行 `rows∈{2,4}`、每行满格 `widths[i]∈[2,G-1]` | `f=Σwidths`、`hb=rows`、`S=f+hb÷2` | `rows` 偶 | `S=满格+半格÷2` |
| `gen_three_view` | 列数 `cols∈{3,4}`、各列高 `heights[i]∈[1,3]` | `front=Σheights`、`top=cols`、`side=max` | — | `正面=Σ列高` |
| `gen_transform_symmetry` | 模式 `translate/reflect`、三角 `A(1,1)B(4,1)C(1,4)` | 平移 `dx∈[3,5],dy∈[1,3]` / 对称轴 `x=6` | 对应点 `(ax,ay)` 整数 | `A'=(ax,ay)` |
| `gen_cuboid_volume` | 长宽高 `a,b,c∈[2,5]` | `V=a·b·c`、`S=2(ab+bc+ca)` | 全整数 | `V=长×宽×高` |

**几何好数约定（后续题型统一沿用）**：
- 底/高取整数 → 平行四边形/长方形面积 `底×高` 恒整数。
- 三角形保证 `底×高` 为**偶数**（`÷2` 得整数）。
- 梯形保证 `(上底+下底)×高` 为**偶数**。
- 圆面积 `π≈3` 或半径取整（`S=πr²` 得整数/整倍 π）。
- 长方体长宽高整数 → 体积/表面积整数。
- 统计（另一 skill）：整数数据、总整十/整百、占比角 = 整度数。

`MAX_ATTEMPTS=200`，失败抛 `NoGoodNumbers`。

## 2. 拖拽层约定（几何技能核心基建）

`scene` 里每个可拖点描述（`points[]` 项）：

```jsonc
{ "name": "D", "x": 2, "y": 4,                    // 初始世界坐标
  "snap": "grid",                                  // grid=整数吸附 / half=半格
  "constraint": "h-line",                          // 沿水平线滑（等积变形）/ v-line / 无
  "min": 0, "max": 3,                              // 拖拽夹取范围（世界坐标）
  "color": "#2ecc71", "label": "D 拖我" }
```

- `fixed: true` = 不可拖（底/高基准点）。
- **命中检测与绘制共用同一 `geomTransform`**：DRAW 画点必须走 `X(x)/Y(y)`，命中检测用
  `invX/invY` 反算，二者不得各写各的坐标换算——这是 Phase 0 立住的铁律。
- **两路拖法并存**：`snap:"grid"` = 练习（吸附整数网格找答案）；`constraint:"h-line"` =
  演示（等积变形：顶点沿底边平行线自由滑，面积不变）。二者靠 `point.snap`/`point.constraint`
  区分。
- 拖拽命中半径 20px；`pointerdown/move/up`（含触屏，兼容小程序 web-view）。
- `dragToT`：可拖点与滑块双向同步（拖动点 ↔ 拨滑块），用于「拖圆/拖点 = 答案量」的题型。

## 3. 阶段步进（剪拼过程）

面积推导的「剪 → 移 → 拼」复用**现有滑块 + 播放**，无需新机制：
- `scene.param` 当「阶段」用（`min:0`、`max:N`、`step:0.1`、`value:0`、`answer:N`）。
- `DRAW` 按 `t`（阶段号）渲染并**线性插值**中间帧（剪下的三角从原位滑到新位）。
- 结论阶段（`t==answer`）展示公式，`phase==="at"` 变绿。

## 4. 渲染器家族（一个渲染器吃一类题型）

| scene.kind | 语义 | 吃进 |
| --- | --- | --- |
| `cut-rearrange` | 网格 + 图形 + 可拖顶点（等积变形）+ 阶段剪拼插值（`variant` 分派） | 面积公式推导（平四/三角/梯形/圆） |
| `grid-split` | 方格纸 + 拖辅助线切分 | 组合图形面积 |
| `grid` | 方格纸 + 满格/半格着色计数 | 不规则图形估算 |
| `solid-views` | 正面视图方块柱状 | 观察物体/三视图 |
| `grid-transform` | 方格纸 + 拖对应点（平移/对称） | 平移/轴对称 |
| `solid-net` | 长方体斜二测投影 | 长方体表面积/体积 |

**关键**：渲染器按 `scene.kind` 复用，不是按题型各写一套。6 个家族已全部实现。

## 5. 关键坑（照抄即可避雷）

1. **零依赖**：`evalExpr` 用 `new Function(...names, body)`（**不要**写 `new Function.apply`
   ——严格模式下 `Function.apply` 是原型方法而非构造器）。
2. **动态变量键**：缓存键 `expr + '|' + Object.keys(vars).join(',')`；不同题型 vars 键不同，
   天然隔离。
3. **播放/滑块同步**：程序写 `slider.value=t` 不触发 `input`，无反馈环；`input` 里
   `playing=false`。
4. **帧率无关**：位置永远 `STATE[type](t, pts)` 解析计算（绝不逐帧累加），`dt=min(…,0.05)` 封顶。
5. **等积变形**：拖 D 顶点沿水平线走，`S=a·h` 只依赖底和高，不依赖 `dx`——面积读数保持不变。
6. **吸附夹取**：`applySnap` 里先约束线、再吸附、再 `min/max` 夹取，顺序不可颠倒。
7. **世界坐标 y 向上**：`Y(y) = oy + (yMax - y)·u`，命中反算 `invY = (yMax - (py - oy)/u)`。
8. **答案读数用固定字符串** `readouts[kind="answer"].value`，绝不实时浮点重算。

## 6. 自检断言要点

- **答案一致**：`generators` 答案 == `answer` == `steps` 末步 == 前端 `STATE(t).phase==="at"`。
- **零依赖铁证**：无头打开 `file://` 断言 `requestfailed=0`、canvas 非空白。
- **等积变形**：拖 D 顶点前后，面积读数（第三个读数卡）保持一致。
- **阶段步进**：播放后阶段号递增、暂停稳定、末阶段展示公式。
- **拖拽吸附**：拖到非整数坐标（如 3.4, 2.6）落点应为整数（3, 3）。
- 参考 `tests/test_generators.py`（1000 次抽样）与 `tests/test_builders.py`（schema 自检）。

## 7. 扩展配方（加题型五步）

1. `lib/generators.py` 加一个答案先行的 `gen_*`（保证几何量整数）。
2. `lib/builders.py` 加 `build_*`（复用 `_base`/`_expr`/`_answer`），选一个既有 `scene.kind`
   （`cut-rearrange`/…）或新增家族。
3. `lib/steps.py` 加 `*_steps`。
4. `scripts/generate.py` 的 `REGISTRY` 注册；`template/board.html` 的 `STATE` 加对应
   `type`（若 scene.kind 是既有家族，DRAW 无需改动；否则加 DRAW 渲染器）。
5. `tests/` 补一条单测；`SKILL.md` 题型清单 + 本文件配方表各加一行。
