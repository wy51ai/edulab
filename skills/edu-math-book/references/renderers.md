# 渲染器与 spec 标记

三个渲染器共用一套"标记"（spec 字段）。点可以写成：点名字符串 `'A'`、坐标数组 `[x, y(, z)]`、
或函数 `(P, a) => 点`。所有颜色写名字：`violet blue orange pink green red ink`。

## 共用标记（solid 和 plane 都能用）
| 字段 | 写法 | 说明 |
|---|---|---|
| `lines` | `{a, b, c, w, dash, glow, grow, op, arrow, ext}` | 线段。`glow` 加宽色晕，`grow: 1.2` 1.2 秒内从 a 长到 b，`dash` 虚线，`ext`（plane）延长成直线 |
| `planes` | `{pts: ['A','B','C'], c, op}` | 斜线填充的面 / 多边形 |
| `angles` | `{v, p, q, c, label, r}` | 角弧，`label` 可为函数 `a => …` |
| `right` | `{v, p, q, c}` | 直角符号 |
| `ticks` | `['A','D',1]` | 等长刻痕（1 或 2 道） |
| `edgeLabels` | `{a, b, t, c, flip}` | 线段旁的长度文字，`t` 可为函数 |
| `pts` | `{p, c}` | 呼吸闪烁的高亮点 |
| `labels` | `['D','E']` | 额外显示点名（带小黑点） |
| `labelDir` | `{D: [0, 1]}` | 这一步的标签方向覆盖 |
| `texts` | `{at, t, c, size, dx, dy}` | 任意位置文字 |
| `circles` | `{at, r, n, from, to, c, dash, fill}` | 圆/弧；solid 里 `n` 是圆所在平面的法向 |
| `anim` | `slide('D','E',['D','B'])` / `travel(['A','B'])` / 自定义 `(t, P, a) => [线段…]` | 动画线段 |
| `tag` | `{at: 'F' 或 ['P','H'], text, c}` | 立体图旁的引线标签（只在演示时显示） |
| `slider` | `true` + `a: 3.2` | 本步显示滑块，并把参数先拨到 3.2 让学生拖回来 |
| `view` | `150` | solid：这一步立体图转到的方位角（度） |

## solid
- 给 `faces`，引擎自动推出所有棱、每帧计算外法向（体可以随参数变形），按视线判断可见性：
  **被挡住的棱画虚线，且画在面填充之后**（不会被纸色盖淡），可见棱 2.2px 并带纸色衬底。
- 只支持凸多面体的自动外法向；非凸体请拆成多个凸体或用 `extraEdges` 补棱。
- 旋转体 `round`：轴沿 z 竖直。圆柱/圆台/圆锥自动画上下底圆（背面半圈虚线）和轮廓母线；球画轮廓圆 + 赤道。
  需要截面、内切球等就再用 `circles`（带法向 `n`）、`planes` 叠加。
- 建系习惯：底面放在 z = 0，竖直向上为 z；单位长度 1–3 之间最合适（图形会自动缩放到页面）。

## plane
- `view` 决定坐标范围；坐标会统一缩放进页面，所以 `angles.r`、直角大小等不随范围变化。
- 额外标记：
  - `curves`: `{f: (x, a) => y, x: [x0, x1], c, w, dash, label: {t, at, dx, dy}}`；参数方程 `{xt, yt, t: [t0, t1]}`；
    折线 `{pts: ['A', [1, 2], …]}`。曲线自动裁剪到坐标区域、在渐近线处断开。圆锥曲线用参数方程最稳。
  - `regions`: `{f, g, x: [a, b], c}` —— 两条曲线之间的阴影（g 省略 = x 轴），用于积分/面积/不等式解集。
  - `bars`: `{x, h, w, c, label}` —— 统计柱状图、频率分布直方图、分布列。
  - `drops`: `{p, c}` —— 从点向两轴作虚线（读坐标、极值）。
- `axes: false` 关掉坐标系，就是纯平面几何（三角形、圆、相似、向量图）。
- 演示时整张坐标纸像立体贺卡一样从书页立起，不旋转。

## none
- 右页变成"公式板"：`figure.board` 列出 3–6 行关键式子（`k: 1` 红色强调，`note: 1` 手写批注）。
- 演示时没有立体图，全部靠草稿纸上的推理链；适合数列、不等式、计数与概率计算、复数、二项式定理。
- 概率统计题如果有分布列/直方图，优先用 plane + `bars`。

## 选型速查
| 题目 | 渲染器 | 要点 |
|---|---|---|
| 线面平行/垂直、线面角、二面角、点面距离、体积 | solid | `faces` + 每步 `planes/lines/right/angles`，参数题加 slider |
| 圆柱/圆锥/球（外接球、内切球） | solid | `round` + `circles` |
| 单调性、极值、零点、恒成立 | plane | `curves` + `drops` + 参数 slider |
| 三角函数图像变换 | plane | 多条 `curves`，`anim` 或 slider 控制平移/伸缩 |
| 椭圆/双曲线/抛物线 | plane | 参数方程 `curves`，焦点 `pts`，弦 `lines` |
| 解三角形、平面几何 | plane + `axes:false` | `lines/angles/right/edgeLabels` |
| 统计图表 | plane | `bars` |
| 数列、不等式、计数、复数 | none | `board` + KaTeX 推理链 |
