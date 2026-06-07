# 数据格式参考（problem-schema）

三入口（文字 / 图片 / 随机）最终归一成同一份数据，注入模板 `template/board.html` 的数据岛
`<script id="lesson-data">__LESSON_DATA__</script>`。数据是一个 JSON 对象，三段：
`lesson` / `steps` / `board`。

## 1. lesson（题面 / 答案 / 界面文案）

```jsonc
"lesson": {
  "language": "zh-CN",                 // 跟随提示词语言：zh-CN / en
  "title": "椭圆与动态向量积范围",       // 左上标题
  "problem": "<p>……题面 HTML，行内公式 $…$，块公式 $$…$$……</p>",
  "answerLabel": "向量数量积取值范围",   // 答案文字说明（自检用，可不显示）
  "answer": "$\\left[-3,\\ \\dfrac{7}{4}\\right]$",  // 最终答案 LaTeX（自检用）
  "ui": { "solutionTitle": "Solution", "collapse": "Collapse", ... }  // 可选：英文输出时覆盖界面文案
}
```

界面文案默认中文，键见 `board.html` 顶部 `UI`：`consoleTitle / solutionTitle / collapse /
expand / current / theoRange`。英文输出时设 `lesson.language="en"` 并填 `lesson.ui`。

## 2. steps（分步解析）

```jsonc
"steps": [
  { "title": "联立 + 韦达定理", "content": "<p>HTML，公式用 $…$ / $$…$$</p>" },
  ...
]
```
每步自动编号（01、02…）。`content` 里的数值**应来自 kernel**（`analytic_kernel.tex(expr)`），
讲解文字由模型按目标语言书写。

## 3. board（场景 + 交互模型）—— 新核心

```jsonc
"board": {
  "view": { "xRange": [-3.6, 3.6], "yRange": [-2.6, 2.6] },   // 数学坐标视窗，引擎自适应缩放
  "conics": [ { "name":"C", "kind":"ellipse", "a":2, "b":1.732, "center":[0,0],
                "color":"curve", "label":"C: x²/4+y²/3=1" } ],
  "points": { "M": {"xy":[-1,0], "color":"vecA", "label":"M(-1,0)"}, "F":[1,0] },
  "param": { "name":"e", "label":"离心率 $e$", "min":1.05,"max":3,"step":0.01,
             "value":1.5, "unit":"", "standard":1.5, "ticks":["1","2","3"] },
  "scalars": [ { "name":"b", "expr":"sqrt(e*e-1)" } ],                             // 可选：由 @param 派生的命名标量，按序求值
  "derived": [ /* 参数实时驱动的构造序列，见下 */ ],
  "readouts": [ /* 控制台实时数值，见下 */ ],
  "rangeBar": { "of":"dot", "min":-3, "max":1.75, "label":"$[-3,\\ \\frac74]$" },  // 范围/最值题
  "constant": { "of":"kprod", "label":"$-\\dfrac34$" },                            // 定值题
  "answerBand":{ "min":1,"max":3,"lo":1,"hi":2,"label":"$e\\in(1,2]$" },           // 形状参数题：参数轴上高亮答案区间
  "trace":    { "of":"Q", "color":"locus" },                                       // 轨迹题（可选）
  "legend":   [ { "color":"line", "text":"动直线 l" } ]                            // 画板左下图例（可选）
}
```
> `rangeBar` / `constant` / `answerBand` 三者按题型择一。

### 3.1 conics[*]（圆锥曲线）
| kind | 必填参数 | 说明 |
|---|---|---|
| `ellipse` | `a`(x 半轴), `b`(y 半轴), `center` | |
| `hyperbola` | `a`(实半轴), `b`(虚半轴), `center`, `orient`("x"/"y") | `asymptotes:true` 画渐近线 |
| `parabola` | `p`, `center`(顶点), `axis`("x"/"y") | `(y-cy)²=2p(x-cx)` 或 `(x-cx)²=2p(y-cy)` |
| `circle` | `r`, `center` | |

通用可选：`color`、`label`（图例文字）、`dashed`、`hidden`、`legend:false`。
**直接用 `conics.py` 返回对象的 `board` 字段**，再补 `name/color/label` 即可。

> **参数化曲线（形状参数题，如离心率）**：`a/b/c/r/p` 与 `center` 各坐标可写成**表达式字符串**
> （用 `@param` 名或别名 `p`，及 `sqrt/sin/cos/abs/pow/min/max/PI` 与 `+ - * / ^`），引擎每帧按
> 当前滑块值重算并重绘曲线、焦点、渐近线。例：双曲线 `{"a":1,"b":"sqrt(e*e-1)"}` 随 `e` 变形。

### 3.2 points（静态命名点）
值可为 `[x,y]`，或 `{xy:[x,y], color, label, emphasis, hidden}`。`emphasis:true` 画大一圈带白边
（定点用）；`hidden:true` 只参与构造不显示；`label` 省略则用点名。
坐标也可为**表达式字符串**（随 `@param` 变），如 `"xy":["e","0"]`、`"xy":["2/e","sqrt((e*e-1)*(4/(e*e)-1))"]`；
当表达式算出 `NaN`（如根号下为负）时该点**自动隐藏**，依赖它的线段/向量/读数一并消失（天然表达"不存在"）。

### 3.3 param（可变参数，省略=静态图）
`min/max/step/value`，`unit`（显示后缀），`standard`（题目设定值，"重置"按钮归到此），
`label`（可含 LaTeX），`ticks`（滑块下方刻度文字数组）。参数当前值在引擎里记作 `@param`，
在表达式里用**参数名**（须是合法标识符，如 `e`/`t`/`k`）或别名 `p` 引用。

### 3.3b scalars（可选：由参数派生的命名标量）
`[{name, expr}]`，按数组顺序求值（后者可引用前者）；算出的标量加入表达式环境，供 `conics` /
`points` / `readouts` 的表达式引用。例：`[{"name":"c","expr":"e"},{"name":"b","expr":"sqrt(e*e-1)"}]`。

### 3.4 derived（构造序列，按顺序求解，可引用前面的结果）
`type` 一览（引擎构造库，与 `analytic_kernel` 对应）：

| type | 字段 | 产出 |
|---|---|---|
| `line_through_angle` | `name, point, angle`(数或`"@param"`) | 直线（过点、给倾斜角） |
| `line_through_slope` | `name, point, slope` | 直线（过点、给斜率） |
| `line_x_eq_my_c` | `name, m, c` | 直线 `x=my+c` |
| `line_through_points` | `name, a, b`(点名) | 两点连线 |
| `line_through_point_dir` | `name, point, dir:[dx,dy]` | 过点给方向 |
| `point_on_conic` | `name, conic, t`(角度°/参数) | 曲线上参数点 |
| `intersect_line_conic` | `name:[n1,n2], line, conic, colors` | 直线∩曲线（按 t 升序两点；不足则缺省隐藏） |
| `intersect_line_line` | `name, a, b`(线名) | 两线交点 |
| `midpoint` | `name, a, b` | 中点 |
| `point_reflect` | `name, of, center` | 中心对称点 `2·center − of` |
| `foot_perp` | `name, point, line` | 垂足 |
| `reflect` | `name, point, line` | 关于直线的反射 |
| `tangent_at` | `name, conic, point` | 曲线在其上一点的切线 |
| `vector` | `name, from, to`(点名) | 向量箭头 |
| `segment` | `name, a, b, dashed, color` | 线段 |
| `polygon` | `name, pts:[...], color, stroke` | 多边形（半透明填充，三角形面积用） |

构造对象可加 `color`（语义名或 hex）、`label`、`dashed`。

### 3.5 readouts（控制台实时数值）
每项 `{id, label, type, ..., color, highlight}`。`highlight:true` 用青色徽标突出（通常是目标量）。
`id` 供 `rangeBar.of` / `constant.of` 跟踪。

| type | 字段 | 显示 |
|---|---|---|
| `coord` | `of`(点名) | `(x, y)` |
| `length` | `a,b`(点) 或 `of`(向量名) | 长度 |
| `distance` | `a,b`(点) | 两点距离 |
| `dot` | `a,b`(向量名) | 数量积 |
| `slope` | `of`(线名) | 斜率（竖直显示"不存在"） |
| `slope_product` | `a,b`(线名) | 斜率之积 |
| `area_triangle` | `pts:[p,q,r]` | 三角形面积 |
| `distance_point_line` | `point, line` | 点到直线距离 |
| `expr` | `expr`(表达式), `digits` | 表达式数值（可用 `@param`/scalars，如半焦距 `c`） |
| `status` | `expr, op, rhs, okText, badText` | 不等式状态：`expr op rhs`(op∈ `< <= > >= ==`) 成立→绿色"满足"，否则红色"不满足" |

### 3.6 rangeBar / constant / answerBand / trace
- `rangeBar`（范围、最值题）：`of` 跟踪一个**标量** readout 的 `id`，`min/max` 为 kernel 给的
  理论范围浮点，`label` 为区间 LaTeX（带 `$…$`）。指针随当前值在 min–max 间移动。
- `constant`（定值题）：`of` 跟踪一个 readout，`label` 为定值 LaTeX（带 `$…$`），显示"恒为定值 ≡ …"。
- `answerBand`（**形状参数题**，如离心率范围）：在**参数轴**上画 `[min,max]`，高亮答案子区间 `[lo,hi]`，
  指针=当前参数值，`label` 为答案 LaTeX（带 `$…$`）。用于"求 e 的取值范围"这类滑块本身即是答案变量的题。
- `trace`（轨迹题）：`of` 为某个 `derived` 点名；引擎在 param 全程采样描出该点路径（可叠加 kernel
  的轨迹方程作为一条 `conics` 曲线对照）。

### 3.7 颜色语义名（COLORS）
`curve`(金黄·主曲线) · `curve2`(粉·次曲线) · `line`(青·动直线) · `line2`(天蓝) · `aux`(灰辅助) ·
`asymptote` · `directrix` · `ptA`(红) · `ptB`(蓝) · `point`(浅灰) · `given`(紫) · `fixed`(翠绿·定点) ·
`vecA`(红) · `vecB`(蓝) · `vec`(琥珀) · `locus` · `area`(青半透明)。也可直接写 hex。
