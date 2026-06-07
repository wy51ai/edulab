# 约定与解法配方（conventions）

## 1. 坐标系与曲线标准式
解析几何直接用**数学平面坐标**（x 右、y 上），无需像立体几何那样做 z↔y 换轴。前端引擎把数学
坐标 `(x,y)` 映射到屏幕：`sx = offX + x·scale`，`sy = offY − y·scale`（y 翻转）。`scale` 由 `view`
视窗自适应，不影响数值。

`conics.py` 的标准建系（中心/顶点默认原点）：
- `ellipse(a, b)` — `x²/a² + y²/b² = 1`，a=x 半轴、b=y 半轴；焦点在长轴上，`c=√|a²−b²|`。
- `hyperbola(a, b, orient)` — `orient='x'`: `x²/a²−y²/b²=1`；`'y'`: `y²/a²−x²/b²=1`。a=实半轴、
  b=虚半轴，`c=√(a²+b²)`，渐近线斜率 `±b/a`（x 向）。
- `parabola(p, axis)` — `axis='x'`: `y²=2px`，焦点 `(p/2,0)`，准线 `x=−p/2`；`'y'`: `x²=2py`。
- `circle(center, r)` — `(x−h)²+(y−k)²=r²`。

## 2. 核心套路：设含参直线 + 联立 + 韦达
**首选 `x = m·y + c`**（而非 `y = kx + b`）：天然包含竖直线（`m=0`），避免"斜率不存在"的讨论；
水平线对应 `m→∞`（前端滑块拖到 θ=0° 即此情形）。过定点 `(x₀,y₀)` 时 `c = x₀ − m·y₀`。

`chord_setup(conic, through)` 把 `x=my+c` 代入曲线，得关于 y 的二次方程，返回精确的
`A,B,C` 系数、`ysum=−B/A`、`yprod=C/A`、判别式 `disc`。由韦达量把目标量写成 m 的表达式：
- `x₁+x₂ = m·ysum + 2c`，`x₁x₂ = m²·yprod + m·c·ysum + c²`。

## 3. 解法配方（query.type → kernel → 交互范式）

| query.type | kernel 函数 / 公式 | 交互范式 |
|---|---|---|
| `standard_equation` 求标准方程 | 由离心率/过点/焦点解 a,b,c（或 h,k,r） | 静态标注 |
| `chord_length` 弦长（范围） | `chord_len_sq_expr`，`|AB|²=(1+m²)[ysum²−4·yprod]` | 转直线 + 范围条 |
| `dot_product` 数量积（范围/定值） | `dot_product_expr` + `range_over_m`/`is_constant_in_m` | 转直线 + 范围条/定值 |
| `triangle_area` 面积（最值） | `triangle_area_expr=½·|AB|·d`，换元求极值 | 转直线 + 范围条 |
| `slope_product` 斜率之积（定值） | `slope_product_central`（中心对称）等 | 转动点 + 定值 |
| `fixed_value` 定值 | 目标写成 m 表达式 → `is_constant_in_m` | 转参数 + 定值 |
| `fixed_point` 定点 | 含参直线令"参数项系数=0"解出定点 | 转参数 + 动直线穿定点(`emphasis`) |
| `locus` 轨迹 | 设动点 `(x,y)`，消参得方程 | 拖驱动点 + `trace` 描路径 + 叠加方程 |
| `tangent` 切线 | 判别式=0 / 点切式（`tangent_at`） | 静态 / 转切点 |
| `eccentricity` 离心率（值/范围） | `e=c/a` + 条件不等式（如 `ecc_range_focal_ratio`） | **滑块=e**·曲线随形 + `status` + `answerBand` |

辅助：`tex(expr)`（LaTeX 输出）、`fnum(expr)`（float）、`is_clean(expr)`（随机出题判规整）、
`interval_latex(lo,hi,lo_closed,hi_closed)`。

### 形状参数题（滑块直接驱动曲线，如离心率范围）
有些题的自然动态量不是"动直线/动点"，而是曲线本身的**形状参数**（最常见是离心率 e）。此时让
**滑块 = 该参数**，把曲线的 `a/b/c`、焦点、动点坐标写成该参数的**表达式字符串**（schema 3.1/3.2/3.3b），
引擎每帧重算重绘曲线、焦点、渐近线。配套套路：
- 固定一个标度（如取 `a=1`，则 `c=e`、`b="sqrt(e*e-1)"`），其余量用表达式表示；
- 用 `status` 读数显示存在性/不等式是否成立（如右支上 P 存在 ⇔ `e≤2`）；表达式算出 `NaN` 的点会
  **自动隐藏**，直观表现"不存在"；
- 用 `answerBand` 在参数轴上高亮答案区间（端点由 kernel 给，如 `ecc_range_focal_ratio(3)` → `e∈(1,2]`）。
范例见 `generate.py` 的 `build_hyperbola_ecc_range`。

## 4. 端点开闭判定（正确性命门）
`range_over_m(expr, horizontal_valid=True)` 在 m∈ℝ 上求范围，并判定端点开/闭：
- 收集驻点值、`m=0`（竖直线，恒合法）、`m→±∞`（水平线）的极限；
- 端点是否"闭" = 是否被某条**真实合法直线**取到。
- `horizontal_valid=True`：水平线也是合法弦（如椭圆过内部点的弦），其极限端点**计入（闭）**。
  例：椭圆 `MA·MB`，x 轴取到 −3、竖直线取到 7/4 → **`[-3, 7/4]`**（勿写成开的 `(-3, 7/4]`）。
- `horizontal_valid=False`：水平/退化线不合法或会使图形退化（如 `△OAB` 共线面积 0、抛物线焦点弦
  的轴方向只交一点），该极限端点**不计入（开）**。例：`△OAB` 面积 `(0, 3/2]`。

**这条同时保证答案与交互工具一致**：滑块能拖到端点对应的 θ 时，读数应正好等于答案端点值。

## 5. 正确性自检（必须）
- kernel 算出的答案 == 答案卡 `lesson.answer` == 末步骤展示值 == **前端 JS 标准位/扫段重算值**，
  四者一致；`scripts/generate.py` 的每个 `build_*` 已内置 `assert`，照此为新题型加断言。
- `rangeBar` 端点来自 `range_over_m`；`constant` 值来自 `is_constant_in_m`/对应 kernel 函数。
- 随机题：与 kernel 生成时的标准答案比对。
- 生成后起本地静态服务用预览检查：无控制台报错、KaTeX 渲染正常、滑块实时重算正确、范围条/
  定值/定点/轨迹行为符合、画笔与收起面板可用。**预览完务必关端口**。

## 6. 视窗（view）经验值
让曲线主体留约 10–15% 边距：椭圆 `xRange≈[-1.8a,1.8a]`；抛物线开口方向多留（如 `y²=4x` 用
`xRange:[-2,7]`）；双曲线含渐近线时视窗别太大以免曲线过扁。`param` 范围要避开退化值（抛物线
焦点弦避开轴方向 θ≈0/180；中心对称斜率积避开动点与定点重合的参数）。
