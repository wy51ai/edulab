---
name: edu-analytic-geometry
description: >-
  把一道解析几何题解成一个自包含的交互教学网页：左栏题面 + 动态控制台（一个
  可变参数滑块驱动实时重算的几何量 + 理论范围/定值指示），中栏 KaTeX 分步解析，右栏 2D
  Canvas 动态几何画板（椭圆/双曲线/抛物线/圆 + 动直线/动点 + 向量 + 标注 + 画笔涂鸦）。
  支持三入口——给定文字题、随机出题、上传题目图片识别后解题。覆盖求标准方程、弦长、向量
  数量积范围/定值、三角形面积最值、定点、定值（斜率之积）、轨迹、离心率等题型，统一"设含参
  直线 x=my+c + 联立 + 韦达 + 换元/常数分离"，并由 sympy 精确计算驱动（答案、坐标、步骤
  数值、交互引擎的理论范围同源一致）。其它 agent 也可调用本技能生成此类网页。形态与
  edu-solid-geometry 平行，但用 Canvas-2D + KaTeX（非 Three.js）。
  触发词：解析几何, 圆锥曲线, 椭圆, 双曲线, 抛物线, 直线与圆锥曲线, 焦点弦, 弦长, 数量积取值范围,
  向量数量积, 定点问题, 定值问题, 斜率之积, 三角形面积最值, 轨迹方程, 离心率, 解这道解析几何题,
  随机出一道圆锥曲线题, 这张图里的解析几何题; analytic geometry, conic sections, ellipse,
  hyperbola, parabola, chord length, dot product range, fixed point, fixed value, locus,
  eccentricity, interactive analytic geometry solution page.
---

# 解析几何解题 → 交互网页

## 这个技能产出什么
一个可直接用浏览器打开的单页 HTML（三栏）：
- **左栏**：题面 + 动态控制台 —— 一个可变参数滑块（如直线倾斜角 θ / 动点参数 t）驱动实时
  重算的几何量（交点坐标、斜率、数量积、弦长、面积…），以及"理论范围条"或"定值指示"。
- **中栏**：分步解析（公式用 **KaTeX**），可一键收起把空间让给画板。
- **右栏**：2D Canvas 动态几何画板（圆锥曲线 + 动直线/动点 + 向量 + 点标注 + 网格坐标轴），
  叠加画笔涂鸦工具栏。

形态与目标模板 `/Users/wuyi/code/code2026/6/template/code_artifact.html` 一致。

## 依赖（重要）
计算核心 `lib/analytic_kernel.py` 依赖 **sympy**。运行脚本前先确认有能 import sympy 的
解释器：`python3 -c "import sympy"`（本机用 `/opt/homebrew/bin/python3.11`，sympy 1.14）。

**缺库时**：若 import 报错（sympy 或后续任何库），**先询问用户是否安装**，同意后再装
（`python3 -m pip install <库名>`）或换一个已装该库的解释器；**不要未经询问直接装**。
下文 `python3` 均指这个能跑通依赖的解释器。

## 工作流程

### 第 1 步：得到 problem spec（三入口归一）
把题目整理成结构化 spec（曲线类型与参数、已知点/条件、所求类型与对象、语言）。
- **文字题**：直接抽取。
- **图片**：视觉读图抽取，并**把识别到的题目回显给用户确认**（题面/曲线/参数/所求/语言）再继续。
- **随机出题**：选曲线 + 题型，随机参数 → kernel 求解，用 `analytic_kernel.is_clean(...)` 判答案
  是否规整，不规整就重抽。

> **输出语言跟随提示词语言**：英文提示 → 英文网页，中文 → 中文。spec 记下 `language`。

### 第 2 步：用 kernel 精确计算（不要心算）
按 `references/conventions.md` 的解法配方，调用 `lib/analytic_kernel.py` 与 `lib/conics.py`：
- `conics.ellipse/hyperbola/parabola/circle(...)` 得曲线对象（精确 a,b,c、焦点、顶点、准线、
  渐近线、`eq_latex`、以及给前端引擎的 `board` dict）。
- `chord_setup(conic, through)` 联立含参直线 `x=my+c` 得 y 的二次方程 + 韦达量（精确）。
- 目标量：`dot_product_expr` / `chord_len_sq_expr` / `triangle_area_expr` / `slope_product_central` …
- 取值范围：`range_over_m(expr, horizontal_valid=?)` —— **含开闭端点判定**（关键正确性点，见下）。
- 定值：`is_constant_in_m(expr)`。

可命令行自检 kernel：
```bash
python3 lib/analytic_kernel.py      # 旗舰题内置断言自检
```

> ⚠️ **端点开闭 = 正确性命门**：过焦点的弦，水平线（x 轴，θ=0）与竖直线（θ=90）都是合法直线，
> 它们取到的端点要计入。例：椭圆 MA·MB 题，x 轴取到 −3、竖直线取到 7/4，故答案是**闭区间**
> `[-3, 7/4]`（很多教辅误写成开的 `(-3, 7/4]`）。`range_over_m` 已据此判定，且这样答案与交互
> 工具一致——拖滑块到 0° 就读到 −3。抛物线焦点弦的"轴方向"是退化线（只交一点），其极限端点
> 不计入（`horizontal_valid=False` 或限制 param 范围）。

### 第 3 步：组装数据并注入模板

> 📍 **输出位置 & 唯一产物（最重要）**：交付给用户的**只有一个 `.html`**，写到**当前工作目录
> （`Path.cwd()`）**（除非用户显式指定路径）。cwd 里**不要留任何别的文件**——构建脚本（`.py`）、
> `__pycache__`、自检截图（`.png`）、临时文件都**不是交付物**，一律放 `/tmp` 或用完即删。
> 也**绝不要**写进技能自身目录（`skills/edu-analytic-geometry/output/` 是技能内部样例）。

把"组装数据 + 注入模板"的**构建脚本写到临时目录**（如 `/tmp/ag_build.py`），让它**只把 `.html`
写到 cwd**；脚本拼出 `lesson` / `steps` / `board` 数据（schema 见 `references/problem-schema.md`），
调用 `generate.render_html(data, out)` 注入 `template/board.html`，**跑完即删脚本**：

```python
# 构建脚本放 /tmp（不要放 cwd）：/tmp/ag_build.py
import sys; sys.dont_write_bytecode = True            # 不生成 __pycache__
sys.path.insert(0, "<技能目录>/scripts")
import generate
from pathlib import Path
data = {"lesson": {...}, "steps": [...], "board": {...}}
out = Path.cwd() / "solution-<题目简述>.html"   # 唯一产物，落在用户当前目录
generate.render_html(data, out)
```

```bash
python3 -B /tmp/ag_build.py && rm -f /tmp/ag_build.py   # -B 不写字节码；跑完删临时脚本，cwd 只剩 .html
```

- `steps[*].content` 里的数值**直接引用 kernel 结果**（用 `K.tex(...)` 输出 LaTeX），模型只负责
  组织讲解文字（按目标语言）。
- `board` 用 kernel 给的曲线 `board` dict、精确点坐标、`param`、`derived` 构造序列、`readouts`、
  `rangeBar`（范围题）/ `constant`（定值题）/ `answerBand`（**形状参数题**，如离心率范围）。
- **形状参数题（滑块=离心率 e 等）**：自然动态量是曲线本身的形状而非动直线/动点时，让滑块=该参数，
  把曲线 `a/b/c`、焦点、动点坐标写成 `@param` 的**表达式字符串**（引擎每帧重绘曲线/焦点/渐近线），
  配 `status` 读数显示不等式状态、`answerBand` 在参数轴高亮答案区间。见 conventions「形状参数题」。
- **可直接照抄的范本**：`scripts/generate.py` 里 6 个 `build_*` 覆盖各类交互范式：
  `ellipse_dot_range`（范围条）、`ellipse_chord_range`、`ellipse_area_max`、
  `ellipse_slopeprod_const`（定值·中心对称）、`parabola_dot_const`（定值·抛物线）、
  `hyperbola_ecc_range`（**形状参数**：滑块=e，曲线随之重绘 + `status` + `answerBand`）。

已注册题直接出（`-B` 不写字节码；不传路径默认写技能 output，交付给用户时务必改成 cwd 下的 `.html`）：
```bash
python3 -B scripts/generate.py list                      # 列出题型
python3 -B scripts/generate.py ellipse_dot_range ./sol.html
python3 -B scripts/generate.py all ./out_dir             # 全部题型
```

### 第 4 步：自检（正确性方案）
- kernel 答案 == 答案卡 `lesson.answer` == 末步骤展示值 == **JS 标准位/扫段重算值**，四者一致
  （`build_*` 内已加 `assert`）。
- `rangeBar` 端点来自 kernel 的 `range_over_m`；`constant` 值来自 kernel 的定值。
- 起本地静态服务（服务**输出文件所在目录**，即 cwd）用预览检查：无控制台报错、KaTeX 正常、
  滑块实时重算正确、范围条/定值/定点/轨迹行为符合、画笔与收起面板可用。
  （技能仓库内开发时可用 `.claude/launch.json` 的 `ag-preview`，端口 4601；别处运行就对 cwd 起
  一个临时静态服务。）
- **自检截图只给你自己看**：preview 工具直接返回图像，**不要把 `.png` 存到 cwd**；本地静态服务只读不写、
  不产生文件。自检产生的任何临时文件（构建脚本 `.py`、截图 `.png`、`__pycache__` 等）交付前一律清掉。

> ⚠️ **必须关闭你开过的端口/服务**：预览一结束立即停掉，**绝不留占用端口的进程**。
> - preview 工具开的：`preview_stop`（传 serverId）。
> - 直接起的 `http.server`：用完 `kill`，或 `lsof -nP -iTCP:<port> -sTCP:LISTEN` 确认已释放。
> - 交付前确认端口已释放再告诉用户。开了不关 = 未完成自检。

### 第 5 步：交付
成品写在**用户当前工作目录（cwd）**，命名形如 `solution-<题目简述>.html`，把路径告诉用户，
可直接浏览器打开。交付前确认：**(1)** 成品在 cwd、不在技能目录；**(2)** 没有遗留本次预览
开启的本地服务/端口；**(3)** cwd 里**只新增了这一个 `.html`**——没有 `.py` / `.png` /
`__pycache__` / 临时文件（用 `git status` 或 `ls` 核一眼，有就删掉）。

## 扩展
- **加题型**：在 `analytic_kernel.py` 加目标量函数（写成 m 的表达式）+ 复用 `range_over_m` /
  `is_constant_in_m`；在 `generate.py` 加一个 `build_*`，选定交互范式（范围条 / 定值 / 定点 /
  轨迹 trace / 形状参数 answerBand）。见 `references/conventions.md` 配方表。
- **加曲线**：`conics.py` 已有椭圆/双曲线/抛物线/圆；前端 `board.html` 引擎已支持四类渲染、
  渐近线、准线方向。新曲线在两处各加一份即可。
- **加交互构造**：`board.html` 的 `buildScene` switch 是构造库（`line_through_angle`、
  `intersect_line_conic`、`point_on_conic`、`point_reflect`、`tangent_at`、`foot_perp`…），
  按需扩充并在 schema 文档登记。

## 目录
- `template/board.html` — 数据驱动模板（通用 2D 渲染器 + 参数引擎 + 数据岛 `__LESSON_DATA__`）
- `lib/conics.py` — 圆锥曲线 sympy 定义库（特殊点 / LaTeX / board dict）
- `lib/analytic_kernel.py` — sympy 精确求解核心（联立·韦达·范围·定值）
- `scripts/generate.py` — 注入模板 + 5 个 build_* 范本 + 批量/单题出题
- `references/problem-schema.md` — 数据格式（board 引擎 schema）
- `references/conventions.md` — 标准式、解法配方表、韦达/换元套路、端点开闭、自检
