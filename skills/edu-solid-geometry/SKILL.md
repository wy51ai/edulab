---
name: edu-solid-geometry
description: >-
  把一道立体几何题解成一个自包含的交互教学网页：左侧 MathJax 分步解析，
  右侧 Three.js 可交互 3D 模型（分步高亮 + 镜头切换）。支持三种入口——给定文字题目、
  随机出题、上传题目图片识别后解题。覆盖正方体/长方体、棱锥/棱柱、圆柱/圆锥上的线面角、
  二面角、异面直线夹角、点到平面距离、体积等题型，统一用"建系+向量法"，并由 sympy 精确
  计算驱动（答案、3D 坐标、步骤数值同源一致）。其他 agent 也可调用本技能生成此类网页。
  触发词：立体几何, 线面角, 二面角, 异面直线, 点到平面距离, 正四棱锥, 正方体求角, 解这道几何题,
  随机出一道立体几何题, 这张图里的立体几何题; solid geometry, line-plane angle, dihedral angle,
  angle between skew lines, distance to plane, interactive geometry solution page.
---

# 立体几何解题 → 交互网页

## 这个技能产出什么
一个可直接用浏览器打开的单页 HTML：左侧题面/答案/分步解析（公式用 MathJax），
右侧是题目对应的 3D 模型（Three.js，可旋转缩放，分步高亮关键元素并切换镜头）。
形态与 `template/lesson.html` 一致。

## 依赖（重要）
计算核心 `lib/geometry_kernel.py` 依赖 **sympy**。运行脚本前先确认有一个能 import sympy 的
`python3`：跑 `python3 -c "import sympy"`。

**缺库时的处理（重要）**：若 import 报错（sympy 或后续用到的任何库都同理），**先询问用户是否安装**，
得到同意后再帮忙安装（`python3 -m pip install <库名>`），或换一个已装该库的解释器；**不要未经询问直接装**。
下文命令里的 `python3` 均指这个能跑通依赖的解释器。

## 工作流程

### 第 1 步：得到 problem spec（三入口归一）
把题目整理成结构化 spec（格式见 `references/problem-schema.md`）：几何体类型与尺寸、
已知构造点/条件、所求类型与对象、**语言**。
- **文字题目**：直接抽取。
- **图片**：用视觉读图抽取，并**把识别到的题目回显给用户确认**（题面/几何体/尺寸/所求/语言）后再继续。
- **随机出题**：选定几何体与题型，用 kernel 随机参数求解，答案不规整就重抽。

> **输出语言跟随提示词语言**：英文提示 → 英文网页，中文 → 中文。spec 里记下 `language`。

### 第 2 步：用 kernel 精确计算（不要心算）
按 `references/conventions.md` 的建系约定与解法配方，调用 `lib/geometry_kernel.py`：
得到精确坐标、关键向量、法向量、最终答案，以及各步骤要展示的中间量（均为 LaTeX 字符串）。
顶点的 three.js 坐标用 `kernel.to_three(points, scale)` 得到。

可先在命令行跑 kernel 验证答案，例如：
```bash
python3 lib/geometry_kernel.py    # 内置样例自检
```

### 第 3 步：组装 lesson data 并注入模板

> 📍 **输出位置（重要）**：成品 HTML 一律写到**用户当前工作目录（`Path.cwd()`）**，除非用户显式指定路径。
> **绝不要**写进技能自身目录（`skills/edu-solid-geometry/output/` 等）——那是技能内部的开发样例目录。
> 临时构建脚本也放到 cwd 或临时目录（如 `/tmp`），用完可删。

写一个**临时构建脚本**，导入 kernel、bodies、generate，拼出 `lesson` / `steps` / `model` 数据
（schema 见 `references/problem-schema.md`），再调用 `generate.render_html(data, out)` 注入模板产出 HTML。
`out` 用 **cwd 下的绝对路径**：

```python
from pathlib import Path
out = Path.cwd() / "solution-<题目简述>.html"   # 落在用户当前目录，而非技能目录
generate.render_html(data, out)
```

- `steps[*].content` 里的所有数值**直接引用 kernel 的计算结果**，模型只负责组织讲解文字（按目标语言书写）。
- `model.points` 用 `kernel.to_three(...)` 的结果；`model.spheres`/`edges` 用 `lib/bodies.py` 的拓扑
  （`quad_pyramid` / `tri_pyramid` / `cuboid` / `cube` / `prism`），罕见几何体可手写 edges。
- 每步配 `highlight`（该步可见元素的绝对集合）与 `cameraPos`。
- **题面给出线段长度时**：为对应棱加 `measure` 元素（`label` 用 LaTeX，如 `2\sqrt{2}`），
  并把它放进"建系/列已知条件"那步的 `highlight`，在 3D 图中点处标出长度（见 problem-schema）。
- 英文输出时填 `lesson.ui` 英文文案并设 `lesson.language="en"`。

**可直接参考的范例**：`scripts/generate.py` 里的 `build_data()`（正四棱锥·线面角）、
`build_cube_data()`（正方体·线面角）、`build_box_volume_data()`（长方体·体积）都是完整范本，照着改即可。

`generate.py` 可直接出已注册的题；**不传路径时默认写到当前工作目录（cwd）**，也可显式给 cwd 下的文件名
（用技能目录里的 `scripts/generate.py`，输出落在 cwd）：
```bash
python3 <技能目录>/scripts/generate.py cube ./cube.html
python3 <技能目录>/scripts/generate.py box  ./box.html
```

**随机出题**：`generate.py random <seed> [输出.html]`，内部用 `kernel.is_clean(...)` 判答案规整、不过重抽：
```bash
python3 <技能目录>/scripts/generate.py random 7 ./random.html   # 不给路径则默认 ./random.html(cwd)
```
扩展随机题型时沿用"随机参数 → 求解 → is_clean 不过就重抽"。

### 第 4 步：自检（对应正确性方案）
- kernel 答案 == 答案卡 `answerValue` == 末步骤展示的最终值（generate.py 已有断言示例）。
- 3D 顶点坐标来自 `kernel.to_three`（与解题同源）。
- 起本地静态服务（服务**输出文件所在目录**，即 cwd）用预览检查：无控制台报错、公式渲染正常、分步高亮/镜头符合预期。
  （技能仓库内开发时可用 `.claude/launch.json` 的 `geom-preview`；在别处运行就对 cwd 起一个临时静态服务。）

> ⚠️ **必须关闭你开过的端口/服务**：预览检查一结束就立即停掉本地服务，**绝不留下占用端口的进程**。
> - 用 preview 工具开的：检查完马上 `preview_stop`（传对应 serverId）。
> - 直接起的 `http.server`：用完 `kill` 掉，或核对 `lsof -nP -iTCP:<port> -sTCP:LISTEN` 确认已释放。
> - 交付前确认端口已释放，再告诉用户结果。开了不关 = 未完成自检。

### 第 5 步：交付
成品写在**用户当前工作目录（cwd）**，命名形如 `solution-<题目简述>.html`，把（cwd 下的）路径告诉用户，可直接浏览器打开。
交付前确认：**(1)** 成品在 cwd、不在技能目录；**(2)** 没有遗留任何由本次预览开启的本地服务/端口。

## 扩展
- **加题型**：在 `geometry_kernel.py` 加求解函数（见 conventions 配方表），在 `generate.py` 加一个 `build_*`。
- **加几何体**：在 `geometry_kernel.py` 加坐标构建函数，在 `bodies.py` 加棱拓扑。

## 目录
- `template/lesson.html` — 数据驱动模板（通用 3D 渲染器 + 数据岛 `__LESSON_DATA__`）
- `lib/geometry_kernel.py` — sympy 精确计算核心
- `lib/bodies.py` — 几何体棱拓扑库
- `scripts/generate.py` — 注入模板 + 范例构建函数
- `references/problem-schema.md` — 数据格式
- `references/conventions.md` — 建系约定、解法配方、自检
