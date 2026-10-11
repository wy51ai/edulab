---
name: edu-primary-geometry
description: >-
  把一道小学数学「图形与几何」题（面积公式推导 / 组合图形面积 / 不规则图形估算 / 观察物体三视图 /
  平移旋转轴对称 / 长方体表面积体积 …）解成一个自包含、零外部依赖的单页交互课件：
  题面 + 可拖拽图形画布（等积变形 / 剪拼阶段步进 / 方格纸吸附）+ 参数滑块驱动实时重算 +
  动态读数 + 三态状态条 + 分步解题讲解。答案先行「好数」采样，几何量恒为整数
  （底/高/面积/体积整数，纯标准库 random + math，无 sympy/CAS）。前端用「分派式多渲染器」
  STATE[type]/DRAW[scene.kind] 两张表 + 共享拖拽层（geomTransform 世界坐标 + 指针命中 +
  applySnap 吸附），加一个新题型 = 写 generator + build + steps + 一个 STATE 分派项 +
  （新家族才加）一个 DRAW 渲染器。支持随机出题与给定种子复现。原生 Canvas 2D + 零外部依赖
  （无 KaTeX/Three.js/CDN），离线可用、可直嵌小程序 web-view。与 edu-primary-applied
  （数代应用题）、edu-statistics（统计概率）平行，同源自「画图法」三法（线段图/示意图/图表法）。
  触发词：小学几何, 面积, 平行四边形面积, 三角形面积, 梯形面积, 圆面积, 面积公式推导,
  组合图形面积, 数方格, 不规则图形估算, 三视图, 观察物体, 平移, 旋转, 轴对称, 对称,
  长方体, 正方体, 表面积, 体积, 剪拼, 等积变形, 方格纸;
  geometry, area, parallelogram, triangle, trapezoid, circle, composite shape,
  grid counting, three views, transformation, symmetry, cuboid volume, primary math.
---

# 小学几何 → 交互课件（自研 · 可拖动 · 好数）

## 这个技能产出什么
一个可直接用浏览器打开的单页 HTML（儿童友好、大字号、亮色）：
- **题面**：一句话几何题（数字都是整数）。
- **可拖拽图形画布**：按题型渲染——剪拼推导（平行四边形/三角形/梯形/圆）、方格纸、三视图、
  平移旋转轴对称、长方体展开图；**图上顶点可拖**（吸附整数网格 / 沿约束线滑）。
- **阶段步进**：滑块当「阶段」用（0 → 结论），播放/暂停驱动「剪 → 移 → 拼」动画。
- **动态读数**：当前量（底/高/面积/体积…）+ 固定答案卡（公式）。
- **状态条**：三态（amber → green → blue），「拼到结论」变绿。
- **分步讲解**：中文解题步骤（全 Unicode − × ÷，无需公式渲染器）。

## 依赖（零依赖，重要）
**无需 sympy / CAS / 任何第三方库**。计算核心 `lib/generators.py` 只用标准库 `random`，
`lib/builders.py` 只用标准库。任意 Python3 均可运行；前端引擎原生 Canvas 2D，**不发任何
网络请求**（无 KaTeX/CDN/字体），离线可用、小程序 web-view 无域名白名单问题。

## 核心范式（分派式多渲染器 + 共享拖拽层）

渲染从 `edu-primary-applied` 的引擎复制起步，保留其 `STATE[type]/DRAW[scene.kind]` 分派表
与 `evalExpr` 动态变量键，新增**几何专属拖拽层**：

- `geomTransform(w, h)`：由 `scene.world` 算 `X(x)/Y(y)/invX/invY`（等比缩放、y 向上、居中）。
  DRAW 与命中检测**共用同一变换**——这是「可拖拽」的关键（此前变换写死在各 DRAW 内部，无法命中）。
- `pts`：可变点集（从 `scene.points` 初始化），拖拽只改 `pts[name]`，位置永远重算、帧率无关。
- `applySnap(point, x, y)`：按 `point.snap`（`grid` 吸附整数 / `half` 半格）+ `constraint`
  （`h-line` 沿水平线 / `v-line` 沿竖直线）+ `min/max` 夹取，返回规整坐标。
- `pointerdown/move/up`：命中检测（距可拖顶点 < 20px）→ 反算世界坐标 → 吸附 → 写回 → 重绘。
- **两路拖法并存**：`snap:"grid"` = 练习（吸附整数网格找答案）；`constraint` = 演示
  （等积变形：顶点沿底边平行线自由滑，面积不变）。

于是「加一个新题型 = 写 generator + build + steps + 一个 STATE 分派项」，只要 `scene.kind`
落在既有家族，前端渲染器零改动。详见 `references/conventions.md`。

## 题型清单（全量 9 类，已全部实现）

| slug | 题型 | scene.kind | 交互 | 状态 |
| --- | --- | --- | --- | --- |
| `area-parallelogram` | 平行四边形面积 | `cut-rearrange` | 拖顶点 D（等积变形）+ 阶段剪拼 | ✅ 已实现 |
| `area-triangle` | 三角形面积 | `cut-rearrange` | 拖顶点 C（等积变形）+ 阶段双拼 | ✅ 已实现 |
| `area-trapezoid` | 梯形面积 | `cut-rearrange` | 拖顶点 D（上底平移）+ 阶段双拼 | ✅ 已实现 |
| `area-circle` | 圆面积 | `cut-rearrange` | 等分数 N 滑块（越细越近长方形） | ✅ 已实现 |
| `composite-area` | 组合图形面积 | `grid-split` | 拖辅助线切分 | ✅ 已实现 |
| `grid-count` | 不规则图形估算 | `grid` | 滑块找面积（满格 + 半格） | ✅ 已实现 |
| `three-view` | 观察物体/三视图 | `solid-views` | 滑块找正面格子数 | ✅ 已实现 |
| `transform-symmetry` | 平移/轴对称 | `grid-transform` | 拖对应点 A'（方格纸） | ✅ 已实现 |
| `cuboid-volume` | 长方体体积/表面积 | `solid-net` | 滑块找体积 + 斜二测图 | ✅ 已实现 |

## 工作流程

### 第 1 步：得到 problem spec（随机 / 给定种子）
- **随机出题**：`generate.py <key>`，让 generators 随机采样（答案自动规整）。
- **复现**：`generate.py <key> <seed>`。

### 第 2 步：好数生成（不要手工凑数）
用 `lib/generators.py` 的**答案先行拒绝采样**，几何量恒为整数（见 conventions.md §1）。
几何好数约定：底/高整数；三角形 `底×高` 偶数；梯形 `(上+下)×高` 偶数；圆 π≈3 或半径取整；
长方体长宽高整数。失败抛 `NoGoodNumbers`（MAX_ATTEMPTS=200）。

### 第 3 步：组装数据并注入模板

> 📍 **输出位置 & 唯一产物（最重要）**：交付给用户的**只有一个 `.html`**，写到**当前工作
> 目录（`Path.cwd()`）**（除非用户显式指定路径）。cwd 里**不要留任何别的文件**——构建脚本
> （`.py`）、`__pycache__`、截图（`.png`）都不是交付物，一律放 `/tmp` 或用完即删。

```python
# /tmp/geo_build.py
import sys; sys.dont_write_bytecode = True
sys.path.insert(0, "<技能目录>/scripts")
import generate
from pathlib import Path
data = generate.build_area_parallelogram(seed=42)
out = Path.cwd() / "pingxing-sibianxing-42.html"   # 唯一产物，落在用户当前目录
generate.render_html(data, out)
```
```bash
python3 -B /tmp/geo_build.py && rm -f /tmp/geo_build.py
```

已注册题直接出（`-B` 不写字节码）：
```bash
python3 -B scripts/generate.py list
python3 -B scripts/generate.py area-parallelogram 42 ./pingxing-sibianxing-42.html
python3 -B scripts/generate.py all ./out_dir      # 全部题型，各出 2 个随机变体
```

### 第 4 步：自检（正确性）
- **答案一致性**：`generators` 答案 == `answer` == `steps` 末步展示值 == 前端
  `STATE(t).phase==="at"`（`tests/` 有 1000 次抽样 + schema 自检）。
- **零依赖铁证**：无头浏览器打开 `file://`，断言 `requestfailed=0`、canvas 非空白。
- **交互断言**：滑块拨到答案/阶段 → 状态条变绿；`click(play)` 后前进、再暂停稳定；
  **拖拽**：拖顶点到答案坐标 → 变绿 + 读数正确；拖到 (3.4, 2.6) → 吸附落点 (3, 3)。
- 自检截图只给自己看，**不存 cwd**；本地静态服务只读不写、用完即关。

### 第 5 步：交付
成品写在**用户当前工作目录（cwd）**，命名形如 `<题型>-<seed>.html`，把路径告诉用户。交付前
确认：**(1)** 成品在 cwd、不在技能目录；**(2)** cwd 里**只新增这一个 `.html`**。

## 扩展
见 `references/conventions.md` §7「加题型五步」。全量 9 类已实现：`area-*` 四类复用
`cut-rearrange` 家族（`variant` 分派 triangle/trapezoid/circle），另新增
`grid-split / grid / solid-views / grid-transform / solid-net` 五个 DRAW。

## 目录
- `template/board.html` — 引擎：STATE/DRAW 分派 + evalExpr + 拖拽层（geomTransform/applySnap/指针）+ 播放/滑块 + 数据岛
- `lib/generators.py` — 答案先行好数采样（几何量恒整数）
- `lib/builders.py` — 题型 → schema（`_base`/`_expr`/`_answer` 复用）
- `lib/steps.py` — 中文分步讲解文案（Unicode − × ÷）
- `scripts/generate.py` — 注入模板 + `build_*` + `render_html` + 批量/单题/种子复现
- `references/problem-schema.md` — 统一 schema（scene.kind + STATE 语义）
- `references/conventions.md` — 几何好数配方、渲染器家族、拖拽层约定、扩展配方
- `tests/test_generators.py` / `tests/test_builders.py` — 1000 次抽样 + schema 自检
- `verify.mjs` — 无头端到端自检（Playwright，含拖拽/等积变形）
