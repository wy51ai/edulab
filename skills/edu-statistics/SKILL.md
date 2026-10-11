---
name: edu-statistics
description: >-
  把一道小学数学「统计与概率」题（统计图表：条形/折线/扇形、可能性：树状图/枚举）解成一个
  自包含、零外部依赖的单页交互课件：题面 + 可拖拽统计图（拖数据柱顶改数值 / 拖数据点）+
  参数滑块驱动实时重算 + 动态读数 + 三态状态条 + 分步解题讲解。答案先行「好数」采样，
  统计量恒为整数（数据/总数整数，占比角整度数；纯标准库 random + math，无 sympy/CAS）。
  前端用「分派式多渲染器」STATE[type]/DRAW[scene.kind] 两张表 + 共享拖拽层
  （geomTransform 世界坐标 + 指针命中 + applySnap 吸附，含竖向 v-line 约束 + dragAxis），
  加一个新题型 = 写 generator + build + steps + 一个 STATE 分派项 +（新家族才加）一个
  DRAW 渲染器。支持随机出题与给定种子复现。原生 Canvas 2D + 零外部依赖（无 KaTeX/Three.js/
  CDN），离线可用、可直嵌小程序 web-view。与 edu-primary-applied（数代应用题）、
  edu-primary-geometry（图形几何）平行，同源自「画图法」三法（线段图/示意图/图表法）。
  触发词：小学统计, 统计图, 条形统计图, 折线统计图, 扇形统计图, 补全统计图, 看图填空,
  平均数, 总数, 可能性, 概率, 树状图, 枚举;
  statistics, bar chart, line chart, pie chart, probability, tree diagram,
  primary math.
---

# 小学统计 → 交互课件（自研 · 可拖动 · 好数）

## 这个技能产出什么
一个可直接用浏览器打开的单页 HTML（儿童友好、大字号、亮色）：
- **题面**：一句话统计题（数字都是整数）。
- **可拖拽统计图**：条形图（拖柱顶补全缺失数据）、折线图、扇形图（后续），图上柱顶/数据点可拖。
- **参数滑块**：与拖拽双向同步，整数扫动。
- **动态读数**：各数据项 + 合计 + 目标答案卡。
- **状态条**：三态（amber → green → blue），「补全到正确值」变绿。
- **分步讲解**：中文解题步骤（全 Unicode − × ÷，无需公式渲染器）。

## 依赖（零依赖，重要）
**无需 sympy / CAS / 任何第三方库**。计算核心 `lib/generators.py` 只用标准库 `random`，
`lib/builders.py` 只用标准库。任意 Python3 均可运行；前端引擎原生 Canvas 2D，**不发任何
网络请求**（无 KaTeX/CDN/字体），离线可用、小程序 web-view 无域名白名单问题。

## 核心范式（分派式多渲染器 + 共享拖拽层）

渲染引擎从 `edu-primary-geometry` 复制起步（其又从 `edu-primary-applied` 复制），保留
`STATE[type]/DRAW[scene.kind]` 分派表与 `evalExpr` 动态变量键、`geomTransform` 拖拽层：

- `geomTransform(w, h)`：由 `scene.world` 算 `X(x)/Y(y)/invX/invY`（等比缩放、y 向上、居中）。
  DRAW 与命中检测**共用同一变换**——这是「可拖拽」的关键。
- `pts`：可变点集（从 `scene.points` 初始化），拖拽只改 `pts[name]`，位置永远重算、帧率无关。
- `applySnap(point, x, y)`：按 `snap`（`grid`/`half`）+ `constraint`（`v-line` 竖向锁 x /
  `h-line` 横向锁 y）+ `min/max`（x）+ `ymin/ymax`（y）夹取，返回规整坐标。
- `dragToT` + `dragAxis`：可拖点与滑块双向同步（拖动点 ↔ 拨滑块），`dragAxis` 指定同步哪个轴
  （`"x"` 默认 / `"y"` 竖向拖柱顶）。

于是「加一个新题型 = 写 generator + build + steps + 一个 STATE 分派项」，只要 `scene.kind`
落在既有家族，前端渲染器零改动。详见 `references/conventions.md`。

## 题型清单（全量 2 类，已全部实现）

| slug | 题型 | scene.kind | 交互 | 状态 |
| --- | --- | --- | --- | --- |
| `stat-chart` | 统计图表（条形） | `chart` | 拖柱顶补全缺失数据（竖向吸附整数） | ✅ 已实现 |
| `probability-tree` | 可能性（树状图） | `tree` | 拖手柄沿数轴数叶子（横向吸附整数） | ✅ 已实现 |

> 折线图、扇形图为 `chart` 家族的后续变体（同一数据多图型展示，靠 `scene.chartKind` 切换）。

## 工作流程

### 第 1 步：得到 problem spec（随机 / 给定种子）
- **随机出题**：`generate.py <key>`，让 generators 随机采样（答案自动规整）。
- **复现**：`generate.py <key> <seed>`。

### 第 2 步：好数生成（不要手工凑数）
用 `lib/generators.py` 的**答案先行拒绝采样**，统计量恒为整数（见 conventions.md §1）。
统计好数约定：数据取整数、总数整数；扇形占比角整度数；可能性事件数整数。失败抛
`NoGoodNumbers`（MAX_ATTEMPTS=200）。

### 第 3 步：组装数据并注入模板

> 📍 **输出位置 & 唯一产物（最重要）**：交付给用户的**只有一个 `.html`**，写到**当前工作
> 目录（`Path.cwd()`）**（除非用户显式指定路径）。cwd 里**不要留任何别的文件**——构建脚本
> （`.py`）、`__pycache__`、截图（`.png`）都不是交付物，一律放 `/tmp` 或用完即删。

```python
# /tmp/stat_build.py
import sys; sys.dont_write_bytecode = True
sys.path.insert(0, "<技能目录>/scripts")
import generate
from pathlib import Path
data = generate.build_stat_chart(seed=42)
out = Path.cwd() / "tiao-xing-tongji-42.html"   # 唯一产物，落在用户当前目录
generate.render_html(data, out)
```
```bash
python3 -B /tmp/stat_build.py && rm -f /tmp/stat_build.py
```

已注册题直接出（`-B` 不写字节码）：
```bash
python3 -B scripts/generate.py list
python3 -B scripts/generate.py stat-chart 42 ./tiao-xing-tongji-42.html
python3 -B scripts/generate.py all ./out_dir      # 全部题型，各出 2 个随机变体
```

### 第 4 步：自检（正确性）
- **答案一致性**：`generators` 答案 == `answer` == `steps` 末步展示值 == 前端
  `STATE(t).phase==="at"`（`tests/` 有 1000 次抽样 + schema 自检）。
- **零依赖铁证**：无头浏览器打开 `file://`，断言 `requestfailed=0`、canvas 非空白。
- **交互断言**：滑块拨到答案 → 状态条变绿；**拖柱顶**到答案高度 → 读数正确 + 变绿；
  `click(play)` 后前进、再暂停稳定。
- 自检截图只给自己看，**不存 cwd**；本地静态服务只读不写、用完即关。

### 第 5 步：交付
成品写在**用户当前工作目录（cwd）**，命名形如 `<题型>-<seed>.html`，把路径告诉用户。交付前
确认：**(1)** 成品在 cwd、不在技能目录；**(2)** cwd 里**只新增这一个 `.html`**。

## 扩展
见 `references/conventions.md` §7「加题型五步」。全量 2 类已实现：`stat-chart`（`chart` 家族）
与 `probability-tree`（`tree` 家族）。

## 目录
- `template/board.html` — 引擎：STATE/DRAW 分派 + evalExpr + 拖拽层（geomTransform/applySnap/指针/dragAxis）+ 播放/滑块 + 数据岛
- `lib/generators.py` — 答案先行好数采样（统计量恒整数）
- `lib/builders.py` — 题型 → schema（`_base`/`_expr`/`_answer` 复用）
- `lib/steps.py` — 中文分步讲解文案（Unicode − × ÷）
- `scripts/generate.py` — 注入模板 + `build_*` + `render_html` + 批量/单题/种子复现
- `references/problem-schema.md` — 统一 schema（scene.kind + STATE 语义）
- `references/conventions.md` — 统计好数配方、渲染器家族、拖拽层约定、扩展配方
- `tests/test_generators.py` / `tests/test_builders.py` — 1000 次抽样 + schema 自检
- `verify.mjs` — 无头端到端自检（Playwright，含拖柱顶/吸附）
