---
name: edu-motion-problems
description: >-
  把一道小学行程问题（追及 / 相遇 / 环形跑道）解成一个自包含、零外部依赖的单页交互课件：
  题面 + 道路/环形跑道动画 + 路程—时间(s-t)图 + 时间滑块驱动实时重算 + 动态读数 + 三态
  状态条 + 分步解题讲解。答案先行「好数」采样，追上/相遇时间、相遇点、圈数恒为整数（纯标准库
  random + math，无需 sympy/CAS）。支持随机出题与给定参数出题。其它 agent 也可调用本技能
  生成此类网页。形态与 edu-analytic-geometry / edu-solid-geometry 平行，但用原生 Canvas 2D
  + 零外部依赖（无 KaTeX/Three.js/CDN），离线可用、可直嵌小程序 web-view。
  触发词：行程问题, 追及问题, 相遇问题, 环形跑道, 小学行程, 追及, 相遇, 同向追及, 相向相遇,
  环形追及, 环形相遇, 小学行程问题生成器; motion problems, pursuit, catch-up, meeting,
  circular track, primary math, elementary word problems.
---

# 小学行程问题 → 交互课件

## 这个技能产出什么
一个可直接用浏览器打开的单页 HTML（儿童友好、大字号、亮色）：
- **题面**：一句话应用题（甲/乙两车或两人），数字都是整数。
- **场景画布**：直线道路（追及 / 相遇）或环形跑道（同向追及 / 相向相遇），两辆车/两人随
  时间移动，追上前用双箭头标出「相距 / 还差」的实时距离。
- **s-t 图**：路程—时间图（两条直线 + 交点/圈线 + 时间游标），直观展示「追上/相遇」时刻。
- **控制台**：时间滑块 + 播放/暂停，滑块与动画双向同步。
- **动态读数**：当前时间 / 甲已跑 / 乙已跑 / 还差距离（三态语义）/ 圈数 / 答案。
- **状态条**：三态（追上前 amber → 追上/相遇绿 → 超过/错过蓝）。
- **分步讲解**：中文解题步骤（全 Unicode − × ÷，无需公式渲染器）。

## 依赖（零依赖，重要）
**无需 sympy / CAS / 任何第三方库**。计算核心 `lib/good_numbers.py` 只用标准库 `random`，
`lib/builders.py` 只用 `math`。任意 Python3 均可运行，前端引擎用原生 Canvas 2D，**不发任何
网络请求**（无 KaTeX/CDN/字体），离线可用、小程序 web-view 无域名白名单问题。

## 核心范式（统一物理模型）

四类题型归一成 **`kind ∈ {linear, circular}` × `direction ∈ {same, opposite}`** 矩阵，
前端只硬编码一个 `motionState(t)`：

```
same(同向):     sA=vA·t;  sB=x0B+vB·t;  gap=x0B−(vA−vB)·t;  tMeet=x0B/(vA−vB)
opposite(相向): sA=vA·t;  sB=x0B−vB·t;  gap=x0B−(vA+vB)·t;  tMeet=x0B/(vA+vB)
circular 额外(仅主画布):  pos=s mod L;  圈数 n=floor(s/L)
```

**关键洞察**：s-t 图一律画「展开弧长（不取模）」，取模只发生在环形主画布的圆周上。于是
环形同向追及 = 线性追及（两条正斜率直线相交）、环形相向 = 线性相遇（正/负斜率相交），
s-t 图渲染器可完全复用。详见 `references/conventions.md`。

## 工作流程

### 第 1 步：得到 problem spec（三入口归一）
题型归一为 `kind × direction`，spec 记下：题型 key（pursue / meet / circular-same /
circular-opp）、可选的速度/时间/一圈长度参数、语言（默认中文）。
- **文字题**：抽取「同向/相向 + 直线/环形 + 已知速度/路程/一圈长」。
- **随机出题**：直接选题型 key，让 good_numbers 随机采样（推荐，答案自动规整）。
- **给定参数**：用 `generate.py <key> <seed>` 复现，或在 build 时把参数作为 spec 传给
  `good_numbers.gen_*(rng, spec)`。

> **输出语言跟随提示词语言**：英文提示 → 英文网页（需改写 builders/steps 文案），中文 → 中文。

### 第 2 步：好数生成（不要手工凑数）
用 `lib/good_numbers.py` 的**答案先行拒绝采样**，答案量恒为整数：
- `gen_pursue(rng)`：先挑速度差 `dv` 与追上时间 `tMeet`，反推 `gap=dv·tMeet`。
- `gen_meet(rng)`：先挑速度和与 `tMeet`，反推 `total=(vA+vB)·tMeet`。
- `gen_circular_same(rng)`：挑一圈长 `L` 与其因子 `dv`，`tMeet=L//dv`（甲多跑一圈追上）。
- `gen_circular_opp(rng)`：挑 `L` 与 `vA+vB | L`，`tMeet=L//(vA+vB)`（合跑一圈相遇）。

失败抛 `NoGoodNumbers`（MAX_ATTEMPTS=200）。可命令行自检：
```bash
python3 lib/good_numbers.py   # 无内置 self-test 时改跑 scripts/generate.py list 验证 import
```

### 第 3 步：组装数据并注入模板

> 📍 **输出位置 & 唯一产物（最重要）**：交付给用户的**只有一个 `.html`**，写到**当前工作
> 目录（`Path.cwd()`）**（除非用户显式指定路径）。cwd 里**不要留任何别的文件**——构建脚本
> （`.py`）、`__pycache__`、截图（`.png`）都不是交付物，一律放 `/tmp` 或用完即删。

构建脚本放临时目录，`render_html(data, out)` 注入 `template/board.html`，跑完即删：

```python
# /tmp/mp_build.py
import sys; sys.dont_write_bytecode = True
sys.path.insert(0, "<技能目录>/scripts")
import generate
from pathlib import Path
data = generate.build_pursue(seed=42)          # 或 build_meet / build_circular_same / _opp
out = Path.cwd() / "zhui-ji-42.html"           # 唯一产物，落在用户当前目录
generate.render_html(data, out)
```

```bash
python3 -B /tmp/mp_build.py && rm -f /tmp/mp_build.py
```

- 题型 schema 见 `references/problem-schema.md`（顶层 9 键：type / lesson / motion /
  answer / graph / readouts / status / steps / ui）。
- 分步讲解数值直接引用好数采样结果（`steps.py` 内用 Unicode − × ÷，模型只按目标语言组织文字）。

已注册题直接出（`-B` 不写字节码）：
```bash
python3 -B scripts/generate.py list
python3 -B scripts/generate.py pursue 42 ./zhui-42.html
python3 -B scripts/generate.py all ./out_dir      # 全部题型，各出 2 个随机变体
```

### 第 4 步：自检（正确性）
- **答案一致性**：`good_numbers` 的答案 == `answer.tMeet` == `graph.meet.t` == 末步骤展示值
  == 前端 `motionState(tMeet)` 的 `gapDist≈0`（`build_*` 内已加断言，`tests/` 另有 1000 次抽样）。
- **零依赖铁证**：无头浏览器打开 `file://`，断言 `requestfailed=0`、两个 canvas 非空白。
- **交互断言**：`slider.value=tMeet; dispatchEvent(input)` → 状态条变绿、答案卡显示 `tMeet 秒`；
  `click(play)` 后时间前进、再暂停时间稳定。
- 自检截图只给自己看，**不存 cwd**；本地静态服务只读不写、用完即关。

### 第 5 步：交付
成品写在**用户当前工作目录（cwd）**，命名形如 `<题型>-<seed>.html`，把路径告诉用户。交付前
确认：**(1)** 成品在 cwd、不在技能目录；**(2)** cwd 里**只新增这一个 `.html`**（用 `ls` 核一眼）。

## 扩展
- **加题型（同范式）**：在 `lib/good_numbers.py` 加一个答案先行的 `gen_*`（保证答案整数），
  在 `lib/builders.py` 加 `build_*`（复用 `_base` / `_readouts`），在 `lib/steps.py` 加
  `*_steps`，最后注册进 `scripts/generate.py` 的 `REGISTRY`。前端引擎**无需改动**（只要
  `motion.kind/direction` 落在既有四种组合里）。
- **加小学其它专题**（工程问题、植树、鸡兔同笼、浓度…）：新建平行技能或在本技能加
  `build_*`，共用「数据岛 + 参数滑块 + Canvas 重绘」范式，各自写 `motionState` 变体。
- **加英文输出**：`builders.py` / `steps.py` 文案按 `language` 分流，`lesson.problem` 用英文。

## 目录
- `template/board.html` — 零依赖数据驱动模板（道路/环形渲染器 + s-t 图 + `motionState(t)` + 数据岛 `__LESSON_DATA__`）
- `lib/good_numbers.py` — 答案先行好数采样（4 类生成器，恒整数答案）
- `lib/builders.py` — 题型 → 完整 schema（9 键，`_base` / `_readouts` 复用）
- `lib/steps.py` — 中文分步讲解文案（Unicode − × ÷）
- `scripts/generate.py` — 注入模板 + `build_*` + `render_html` + 批量/单题/种子复现
- `references/problem-schema.md` — 数据格式（9 键 schema + motionState 语义）
- `references/conventions.md` — 好数配方表、统一物理模型、s-t 图展开弧长、关键坑
