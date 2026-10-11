---
name: edu-primary-applied
description: >-
  把一道小学应用题（行程 / 和差 / 和倍 / 差倍 / 盈亏 / 年龄 / 平均数 / 鸡兔同笼 / 植树 / 工程 /
  周期 / 归一 / 归总 / 流水行船 / 火车过桥 / 平均速度 …）解成一个自包含、零外部依赖的单页交互课件：
  题面 + 场景动画（道路 / 环形跑道 / 线段图 / 互换 / 间隔 / 进度 / 序列 / 火车过桥）+ 可选副图（路程—时间图）
  + 参数滑块驱动实时重算 + 动态读数 + 三态状态条 + 分步解题讲解。答案先行「好数」采样，答案量恒为整数
  （纯标准库 random + math，无需 sympy/CAS）。前端用「分派式多渲染器」——STATE[type]/DRAW[scene.kind]/
  DIAGRAM[diagram.kind] 三张表，加一个新题型 = 写一个 generator + build + steps + 一个 STATE
  分派项，渲染器按家族复用。支持随机出题与给定参数出题。形态与 edu-analytic-geometry /
  edu-solid-geometry 平行，原生 Canvas 2D + 零外部依赖（无 KaTeX/Three.js/CDN），离线可用、
  可直嵌小程序 web-view。本技能是 edu-motion-problems（行程问题）的总入口与后继。
  触发词：小学应用题, 行程问题, 追及问题, 相遇问题, 环形跑道, 和差问题, 和倍问题, 差倍问题,
  盈亏问题, 年龄问题, 平均数, 鸡兔同笼, 植树问题, 工程问题, 周期问题, 归一问题, 归总问题,
  流水行船, 火车过桥, 平均速度, 线段图, 分数, 百分数, 比与比例, 比例尺, 浓度, 折扣, 还原,
  移多补少, 爬楼, 锯木, 敲钟, 牛吃草, 方阵, 抽屉原理, 时钟夹角, 消去法, 等差数列, 租船最省钱,
  页码, 植树变体, 容斥, 韦恩图, 排列组合, 搭配, 逻辑推理, 烙饼, 田忌赛马, 利率, 利息, 天平, 解方程,
  小学行程, 追及, 相遇, 同向追及, 相向相遇, 环形追及, 环形相遇;
  motion problems, pursuit, catch-up, meeting, circular track, sum and difference,
  sum and multiple, bar model, fraction, percentage, ratio, proportion, concentration,
  discount, chicken and rabbit, age, average, work rate, unit rate,
  primary math, elementary word problems.
---

# 小学应用题 → 交互课件（通用）

## 这个技能产出什么
一个可直接用浏览器打开的单页 HTML（儿童友好、大字号、亮色）：
- **题面**：一句话应用题（数字都是整数）。
- **场景画布**：按题型渲染——直线道路（追及/相遇）、环形跑道（同向追及/相向相遇）、
  线段图（和差/和倍/差倍/盈亏/年龄/平均数/归一/归总/流水行船/平均速度，色块 + 差段高亮 +
  参照线）、互换（鸡兔同笼）、间隔（植树）、进度（工程）、序列（周期）、火车过桥（桥 + 车身）。
- **副图（可选）**：路程—时间 s-t 图（两条直线 + 交点/圈线 + 时间游标）。
- **控制台**：参数滑块 + 播放/暂停，滑块与动画双向同步。
- **动态读数**：当前量（时间/路程/较小数/较大数/和/差/圈数…）+ 固定答案卡。
- **状态条**：三态（amber → green → blue），「找对了」变绿。
- **分步讲解**：中文解题步骤（全 Unicode − × ÷，无需公式渲染器）。

## 依赖（零依赖，重要）
**无需 sympy / CAS / 任何第三方库**。计算核心 `lib/generators.py` 只用标准库 `random`，
`lib/builders.py` 只用 `math`。任意 Python3 均可运行；前端引擎原生 Canvas 2D，**不发任何
网络请求**（无 KaTeX/CDN/字体），离线可用、小程序 web-view 无域名白名单问题。

## 核心范式（分派式多渲染器，可扩展性关键）

渲染从「单一 motion 硬编码」升级为**三张分派表**（`template/board.html`）：
- `STATE[type](t) -> vars`：每个题型一个状态函数，把滑块值 t 解析成 readouts 用到的变量
  （含 `phase`）。
- `DRAW[scene.kind](ctx, vars, w, h)`：渲染器按**家族**复用，不是按题型各写一套。
- `DIAGRAM[diagram.kind](ctx, vars, w, h)`：可选副图。
- `evalExpr(expr, vars)`：**动态变量键**（按 vars 实际 key 构建函数、按 `expr+keys` 缓存），
  是支持多题型的核心重构点。

于是「加一个新题型 = 写 generator + build + steps + 一个 STATE 分派项」，只要 `scene.kind`
落在既有家族，前端渲染器零改动。详见 `references/conventions.md` §2、§7。

## 题型清单（全量 62 类，已全部实现）

| 轮次 | 题型 | scene.kind | 状态 |
| --- | --- | --- | --- |
| **R1** | 追及 / 相遇 / 环形追及 / 环形相遇 | road / circular | ✅ 已实现 |
| **R1** | 和差 / 和倍 / 差倍 | bar-model | ✅ 已实现 |
| R2 | 盈亏 / 年龄 / 平均数 | bar-model | ✅ 已实现 |
| R2 | 鸡兔同笼 | swap | ✅ 已实现 |
| R2 | 植树 | interval | ✅ 已实现 |
| R3 | 工程 | progress | ✅ 已实现 |
| R3 | 周期 | sequence | ✅ 已实现 |
| R3 | 归一 / 归总 | bar-model | ✅ 已实现 |
| R3 | 流水行船 / 火车过桥 / 平均速度 | bar-model / train | ✅ 已实现 |
| **A** | 求几分之几 / 已知部分求整体 / 求甲是乙的几分之几 | bar-model | ✅ 已实现 |
| **A** | 折扣 / 增减百分之几 / 按比例分配 / 比例尺 | bar-model | ✅ 已实现 |
| **A** | 浓度（盐水） | bar-model | ✅ 已实现 |
| **A** | 中点相遇 | road | ✅ 已实现 |
| **A** | 还原（逆推） / 移多补少 | bar-model | ✅ 已实现 |
| **A** | 爬楼 / 锯木 / 敲钟（间隔变体） | interval | ✅ 已实现 |
| **B** | 牛吃草 / 抽屉原理 / 消去法 / 等差数列 | bar-model | ✅ 已实现 |
| **B** | 租船最省钱 / 页码 / 三数和差倍 | bar-model | ✅ 已实现 |
| **B** | 方阵 | phalanx | ✅ 已实现 |
| **B** | 时钟夹角（整点整数化） | clock | ✅ 已实现 |
| **C** | 盈亏 · 两盈 / 盈亏 · 两亏 | bar-model | ✅ 已实现 |
| **C** | 植树 · 一端栽 / 两端不栽 / 环形 | interval | ✅ 已实现 |
| **D** | 容斥 · 韦恩图（拖圆） | venn | ✅ 已实现 |
| **D** | 排列组合 · 搭配（连线图） | link-graph | ✅ 已实现 |
| **D** | 逻辑推理 · 排除法（拖点） | logic-table | ✅ 已实现 |
| **D** | 烙饼问题（时间轴） | timeline | ✅ 已实现 |
| **D** | 田忌赛马（拖马配对） | matchup | ✅ 已实现 |
| **D** | 分数 · 多/少几分之几 | bar-model | ✅ 已实现 |
| **D** | 百分数 · 利率利息 | bar-model | ✅ 已实现 |
| **D** | 植树 · 两侧都栽 | interval | ✅ 已实现 |
| **D** | 方程 · 天平图（拖砝码） | balance | ✅ 已实现 |
| **E** | 三角形 · 等底等高（拖顶点 · 等积变形） | geodrag | ✅ 已实现 |
| **E** | 平行四边形 · 等底等高（联动顶点 · 割补法拉正） | geodrag | ✅ 已实现 |
| **E** | 三角形 · 已知底求高（v-line 拖顶点变高） | geodrag | ✅ 已实现 |
| **E** | 梯形 · 等积变形（上底平移 · 等腰梯形） | geodrag | ✅ 已实现 |
| **E** | 平行四边形 · 割补法（平移三角形拼长方形） | geodrag | ✅ 已实现 |
| **E** | 圆 · 周长（圆周率取 3，半径滑块驱动直径/周长） | circle | ✅ 已实现 |
| **E** | 圆 · 面积（圆周率取 3，半径滑块驱动面积方格） | circle | ✅ 已实现 |
| **E** | 半圆 · 周长（圆周率取 3，半圆弧 + 直径） | circle | ✅ 已实现 |

> R1 = 行程 4 类（迁移自 edu-motion-problems）+ 线段图 3 类，共 7 类；R2（盈亏/年龄/平均数/
> 鸡兔同笼/植树）与 R3（工程/周期/归一/归总/流水行船/火车过桥/平均速度）共 12 类，合计 19 类主干。
> 其后按「加题型五步」增量追加 **A 组 12 类**（教材核心：分数/百分数/比与比例/浓度/行程扩展/还原/
> 移多补少/间隔变体）、**B 组 9 类**（奥数拓展：牛吃草/方阵/抽屉/时钟/消去/等差数列/最优化/页码/
> 三数和差倍）、**C 组 5 类**（既有家族变体：盈亏两盈两亏、植树一端/两端不栽/环形）、
> **D 组 9 类**（画图法综合实践 + 数代变式：容斥/排列组合/逻辑推理/烙饼/田忌赛马/分数差率/
> 利率/植树两侧/天平），合计 62 类（含 **E 组几何 8 类**：三角形·等底等高、平行四边形·等底等高、
> 三角形·已知底求高、梯形·等积变形、平行四边形·割补法、圆·周长、圆·面积、半圆·周长，
> `geodrag` 拖顶点 + `circle` 圆）。
> 多数 B 组复用 bar-model（3 色块 + 参照线）；方阵与时钟各新增一个轻量 DRAW（`phalanx` 点阵 /
> `clock` 钟面）；间隔变体与植树变体复用 `interval` 的 `mode`（both/one/none/ring/two-sides）。
> D 组新增 6 个可拖拽 DRAW：`venn`（拖圆）、`link-graph`（连线）、`logic-table`（拖点）、
> `timeline`（时间轴）、`matchup`（拖马）、`balance`（拖砝码）；分数差率/利率复用 bar-model、
> 植树两侧复用 interval。
> E 组新增 `geodrag`（整数网格 + 多边形 + 可拖顶点），这是引擎里最早的「几何题通用底座」，
> 已接 5 类：三角形·等底等高（C 沿 h-line 拖，面积恒 `底×高÷2`）、平行四边形·等底等高
> （D 沿 h-line 拖 + `depend` 联动对顶点 C，割补法拉正为长方形）、三角形·已知底求高
> （C 沿 v-line 拖变高，面积公式逆用）、梯形·等积变形（上底沿 h-line 平移，等腰梯形为目标）、
> 平行四边形·割补法（`extra` 多分块 + `hidden` 点，平移三角形拼长方形）。底座核心能力：
> `depend` 联动顶点、`extra` 额外分块、`hidden` 锚点、h-line/v-line 拖动、`dragToT` 双向同步滑块、
> 三态（before/at/after）。
> E 组另新增 `circle` 渲染器（圆 + 半径红线 / 直径蓝虚线 + 周长展开线段 / 面积方格，圆周率取 3，
> 半径滑块驱动直径/周长/面积，答案量恒整数），作为几何底座的圆扩展；`circle` 场景用 `mode`
> 区分「周长」（展开线段 `6r`）、「面积」（3 个 `r×r` 方格 = `3r²`）与「半圆周长」（半圆弧
> `3r` + 直径 `2r` = `5r`，强调别漏掉直径）。

## 工作流程

### 第 1 步：得到 problem spec（三入口归一）
spec 记下：题型 key（见 `REGISTRY`）、可选参数、语言（默认中文）。
- **文字题**：抽取「同向/相向 + 直线/环形」或「和/差/倍数」关系。
- **随机出题**：直接选题型 key，让 generators 随机采样（推荐，答案自动规整）。
- **给定参数**：用 `generate.py <key> <seed>` 复现，或在 build 时传 spec。

> **输出语言跟随提示词语言**：英文提示 → 英文网页（需改写 builders/steps 文案），中文 → 中文。

### 第 2 步：好数生成（不要手工凑数）
用 `lib/generators.py` 的**答案先行拒绝采样**，答案量恒为整数（见 conventions.md §1）。60 个
`gen_*` 分五族：
- 行程：`gen_pursue / gen_meet / gen_circular_same / gen_circular_opp / gen_midpoint_meet`。
- 线段图（和差倍/盈亏/年龄/平均数/归一/归总/流水行船/平均速度）：`gen_sum_diff /
  gen_sum_multiple / gen_diff_multiple / gen_profit_loss / gen_age / gen_average / gen_unit /
  gen_aggregate / gen_boat / gen_avgspeed`。
- A 组（分数/百分数/比与比例/浓度/还原/移多补少）：`gen_fraction_part / gen_fraction_whole /
  gen_fraction_ratio / gen_discount / gen_percent_change / gen_ratio_share / gen_ratio_scale /
  gen_concentration / gen_restore / gen_average_move`。
- B 组（奥数拓展）：`gen_cows / gen_phalanx / gen_pigeonhole / gen_clock / gen_elimination /
  gen_arithmetic_seq / gen_optimize / gen_page_digit / gen_sum_diff_three`。
- C 组（既有家族变体）：`gen_profit_loss_two_gain / gen_profit_loss_two_loss / gen_plant_one /
  gen_plant_none / gen_plant_ring`。
- D 组（画图法综合实践 + 数代变式）：`gen_overlap_venn / gen_match_count / gen_logic_table /
  gen_pancake / gen_tianji / gen_fraction_more_less / gen_interest / gen_plant_two_sides /
  gen_equation_balance`。
- 其它：`gen_chicken_rabbit / gen_plant / gen_work / gen_cycle / gen_train / gen_stairs`。
- E 组（几何底座）：`gen_triangle_equal / gen_para_equal / gen_tri_height / gen_trapezoid /
  gen_recompose / gen_circle / gen_circle_area / gen_semicircle`。

失败抛 `NoGoodNumbers`（MAX_ATTEMPTS=200）。

### 第 3 步：组装数据并注入模板

> 📍 **输出位置 & 唯一产物（最重要）**：交付给用户的**只有一个 `.html`**，写到**当前工作
> 目录（`Path.cwd()`）**（除非用户显式指定路径）。cwd 里**不要留任何别的文件**——构建脚本
> （`.py`）、`__pycache__`、截图（`.png`）都不是交付物，一律放 `/tmp` 或用完即删。

```python
# /tmp/pa_build.py
import sys; sys.dont_write_bytecode = True
sys.path.insert(0, "<技能目录>/scripts")
import generate
from pathlib import Path
data = generate.build_sum_diff(seed=42)   # 或 build_pursue / build_sum_multiple / …
out = Path.cwd() / "he-cha-42.html"       # 唯一产物，落在用户当前目录
generate.render_html(data, out)
```
```bash
python3 -B /tmp/pa_build.py && rm -f /tmp/pa_build.py
```

已注册题直接出（`-B` 不写字节码）：
```bash
python3 -B scripts/generate.py list
python3 -B scripts/generate.py sum-diff 42 ./he-cha-42.html
python3 -B scripts/generate.py all ./out_dir      # 全部题型，各出 2 个随机变体
```

### 第 4 步：自检（正确性）
- **答案一致性**：`generators` 答案 == `answer` == `steps` 末步展示值 == 前端
  `STATE(t)` 的 `phase==="at"`（`tests/` 有 1000 次抽样 + schema 自检）。
- **零依赖铁证**：无头浏览器打开 `file://`，断言 `requestfailed=0`、canvas 非空白、
  红/蓝实体存在（`verify.mjs`）。
- **交互断言**：`slider.value=答案; dispatchEvent(input)` → 状态条变绿；
  `click(play)` 后前进、再暂停稳定。
- 自检截图只给自己看，**不存 cwd**；本地静态服务只读不写、用完即关。

### 第 5 步：交付
成品写在**用户当前工作目录（cwd）**，命名形如 `<题型>-<seed>.html`，把路径告诉用户。交付前
确认：**(1)** 成品在 cwd、不在技能目录；**(2)** cwd 里**只新增这一个 `.html`**（`ls` 核一眼）。

## 扩展
见 `references/conventions.md` §7「加题型五步」。全量 62 类题型已实现；再扩展时沿用同一配方。

## 目录
- `template/board.html` — 通用引擎：STATE/DRAW/DIAGRAM 分派表 + 动态 evalExpr + 通用外壳 + 数据岛
- `lib/generators.py` — 答案先行好数采样（62 个 `gen_*`：行程 5 + 线段图 10 + A组 12 + B组 9 + C组 5 + D组 9 + 其它 4 + E组几何 8）
- `lib/builders.py` — 题型 → schema（`_base`/`_motion_scene`/`_st_diagram`/`_bar_scene` 复用）
- `lib/steps.py` — 中文分步讲解文案（Unicode − × ÷）
- `scripts/generate.py` — 注入模板 + `build_*` + `render_html` + 批量/单题/种子复现
- `references/problem-schema.md` — 统一 schema（8 键 + scene.kind + STATE 语义）
- `references/conventions.md` — 好数配方表、渲染器家族、关键坑、扩展配方
- `tests/test_generators.py` / `tests/test_builders.py` — 1000 次抽样 + schema 自检
- `verify.mjs` — 无头端到端自检（Playwright）
