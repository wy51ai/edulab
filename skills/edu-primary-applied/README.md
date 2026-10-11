# edu-primary-applied · 小学应用题交互课件技能

> 一份把「小学应用题」解成**单文件、零依赖、离线可用**交互课件的 Claude Code 技能。
> 全量 **45 类**题型，纯标准库 `random + math`，前端原生 Canvas 2D，不发任何网络请求。

---

## 1. 概述

**edu-primary-applied** 是 PlayFamGo（数学交互资源平台）下的 edulab 技能之一。给定一道
小学应用题，它产出**一个可直接用浏览器打开的 `.html`**：题面 + 场景动画 + 参数滑块 +
动态读数 + 三态状态条 + 分步讲解，儿童友好、大字号、亮色，可直嵌小程序 web-view。

核心设计约束（不可变）：

- **零依赖**：计算核心只用标准库 `random`（生成）+ `math`；前端只用原生 Canvas 2D，
  无 KaTeX / Three.js / CDN / 网络请求。
- **答案恒整数**：所有答案量（时间/路程/人数/棵树/角度…）都是整数，绝不出现分数答案。
- **单一数据源**：题目、动画、副图、步骤的数值严格一致，由「答案先行好数采样」驱动。
- **单文件交付**：成品是一个 `.html`，不留构建脚本 / `__pycache__` / 截图在 cwd。

---

## 2. 实现技术

### 2.1 数据流（生成 → 组装 → 渲染）

```
lib/generators.py   lib/builders.py          scripts/generate.py
    gen_*(seed) ──────► build_*(p)  ──────►  render_html(data, out)
    （答案先行采样）      （组装 schema）        （注入数据岛 → 单 HTML）
                                                        │
                                                        ▼
                                             template/board.html
                                             ├─ STATE[type](t) → vars
                                             ├─ DRAW[scene.kind](ctx, w, h, vars)
                                             └─ DIAGRAM[diagram.kind](...)
```

数据岛注入：模板里放一个占位符，运行时用 JSON 替换：

```html
<script id="lesson-data" type="application/json">__LESSON_DATA__</script>
```

前端 `JSON.parse` 读取后驱动整页。数据是 JSON 对象，顶层键：

```
type / lesson / scene / answer / diagram / readouts / status / steps / ui（+ seed 复现）
```

### 2.2 答案先行「好数」采样（generators）

不「算出答案再判规整」，而是**先挑答案量与关系量，再反推已知量**——答案量天然整数。
每个 `gen_*(rng, spec=None)` 循环尝试，失败抛 `NoGoodNumbers`（`MAX_ATTEMPTS=200`）。

例（和差）：先挑较小数 `a` 与差 `D`，再反推 `b=a+D`、`S=2a+D`；例（盈亏）：先挑人数
`n`、每人少 `a`、两次差 `dd`，再反推 `c=a+dd`、`spread=n·dd`、`total=a·n+b`。

### 2.3 分派式多渲染器（可扩展性关键）

前端只硬编码**三张表**，加题型不写新渲染器，只加一个分派项：

| 表 | 作用 |
| --- | --- |
| `STATE[type](t) → vars` | 把滑块值 t 解析成 readouts 用到的变量（含 `phase`） |
| `DRAW[scene.kind](ctx, vars, w, h)` | 主画布渲染器，**按家族复用** |
| `DIAGRAM[diagram.kind](...)` | 可选副图（如 s-t 图） |

`evalExpr(expr, vars)` 用动态变量键求值：

```js
new Function(...Object.keys(MATH).concat(keys), '"use strict"; return (' + expr + ');')
// 缓存键 = expr + '|' + keys.join(',') —— 不同题型 vars 键不同，天然隔离
```

**10 个渲染器家族**（`scene.kind`）：

| kind | 语义 | 覆盖 |
| --- | --- | --- |
| `road` | 直线道路 + 两车 + 相距箭头 | 追及 / 相遇 / 中点相遇 |
| `circular` | 环形跑道 + 圈数标注 | 环形追及 / 环形相遇 |
| `bar-model` | N 色块 + 差段高亮 + 参照虚线 + 双箭头 | 33 类（和差倍/盈亏/年龄/平均数/归一/归总/分数/比例/浓度/…） |
| `swap` | 点数 = 头数/腿数联动 | 鸡兔同笼 |
| `interval` | 点-段图（`mode`=both/one/none/ring） | 植树 + 四种植树变体 + 爬楼/锯木/敲钟 |
| `progress` | 双进度条合做 | 工程 |
| `sequence` | 周期色块循环 + 游标 | 周期 |
| `train` | 桥 + 车身滑动 | 火车过桥 |
| `phalanx` | n×n 方阵点阵（外层红框 + 内层蓝点） | 方阵 |
| `clock` | 钟面（红时针 + 蓝分针 + 橙夹角弧） | 时钟夹角 |

滑块目标统一为 `scene.param.answer`，`phaseOf(t, target)` 返回 `before/at/after`，驱动
三态状态条（amber→green→blue），也是 `verify.mjs` 的唯一数据源。

### 2.4 关键工程坑（照抄避雷）

- **零依赖**：`evalExpr` 用 `new Function(...names, body)`，**不要**写 `new Function.apply`
  （严格模式下 `Function.apply` 是原型方法而非构造器）。
- **整数滑块扫动**：`param.step===1` 时播放按 0.4s/+1 整数扫动（精确命中答案变绿）。
- **帧率无关**：位置永远 `STATE[type](t)` 解析计算（绝不逐帧累加），`dt=min(…,0.05)` 封顶。
- **JS 负数取模为负**：`mod = (s % L + L) % L`。
- **答案读数固定字符串**：`readouts[kind="answer"].value` 绝不实时浮点重算。
- **线段图色块防溢出**：`bx(val)=min(max(val,0)·ux, maxW)` 封顶。
- **色块恒正**：采样点出现负宽条会误判 verify——盈亏类约束 `d<c` 保蓝条全程正（今天修的一处）。

---

## 3. 题型清单（45 类）

| 分组 | 题型 | scene.kind |
| --- | --- | --- |
| **R1 行程** | 追及 / 相遇 / 环形追及 / 环形相遇 | road / circular |
| **R1 线段图** | 和差 / 和倍 / 差倍 | bar-model |
| **R2** | 盈亏 / 年龄 / 平均数 / 鸡兔同笼 / 植树 | bar-model / swap / interval |
| **R3** | 工程 / 周期 / 归一 / 归总 / 流水行船 / 火车过桥 / 平均速度 | progress / sequence / bar-model / train |
| **A 教材核心** | 求几分之几 / 已知部分求整体 / 甲是乙的几分之几 / 折扣 / 增减百分之几 / 按比例分配 / 比例尺 / 浓度 / 中点相遇 / 还原 / 移多补少 / 爬楼·锯木·敲钟 | bar-model / road / interval |
| **B 奥数拓展** | 牛吃草 / 方阵 / 抽屉原理 / 时钟夹角 / 消去法 / 等差数列 / 租船最省钱 / 页码 / 三数和差倍 | bar-model / phalanx / clock |
| **C 家族变体** | 盈亏·两盈 / 盈亏·两亏 / 植树·一端栽 / 植树·两端不栽 / 植树·环形 | bar-model / interval |

> 时钟问题做了整数化降级：只做「整点时针分针夹角 / 经过整点小时转多少度」，避开
> `180/11` 分这类分数答案，坚守「答案恒整数」不变量。

---

## 4. 使用方法

### 4.1 环境

```bash
# Python（任意 3.x，无需第三方库）
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
PY=/c/Users/Administrator/AppData/Local/Programs/Python/Python312/python.exe
# Node v22 + Playwright（仅 verify 用，与生成无关）
```

### 4.2 出题命令（`scripts/generate.py`）

```bash
$PY scripts/generate.py list                          # 列出 45 类
$PY scripts/generate.py sum-diff                      # 随机出一题，写 output/
$PY scripts/generate.py sum-diff 42                   # 指定种子（可复现）
$PY scripts/generate.py sum-diff 7 ./he-cha-42.html   # 指定输出文件
$PY scripts/generate.py all ./out_dir                 # 全部题型，各出 2 个随机变体（90 个）
```

直接在当前目录交付单文件：

```python
# /tmp/pa_build.py
import sys; sys.dont_write_bytecode = True
sys.path.insert(0, "<技能目录>/scripts")
import generate
from pathlib import Path
data = generate.build_sum_diff(seed=42)      # 或 build_pursue / build_sum_multiple / …
generate.render_html(data, Path.cwd() / "he-cha-42.html")
```

```bash
$PY -B /tmp/pa_build.py && rm -f /tmp/pa_build.py
```

### 4.3 测试与端到端自检

```bash
$PY tests/test_generators.py    # 45 类 × 1000 次抽样
$PY tests/test_builders.py      # 45 题型 schema 自检
node verify.mjs                 # Playwright 无头：requestfailed=0 / canvas 非空白 /
                                # 红蓝实体存在 / 拨到答案变绿 / 播放暂停
```

### 4.4 加一个新题型（五步配方）

1. `lib/generators.py` 加一个答案先行的 `gen_*`（保证答案整数）。
2. `lib/builders.py` 加 `build_*`（复用 `_base` / `_bar_scene` / `_motion_scene`），选既有
   `scene.kind` 或新增家族。
3. `lib/steps.py` 加 `*_steps`。
4. `scripts/generate.py` 的 `REGISTRY` 注册；`template/board.html` 的 `STATE` 加对应
   `type`（若 `scene.kind` 是既有家族，DRAW/DIAGRAM 零改动）。
5. `tests/` 补一条单测；文档（`SKILL.md` / `references/*.md`）题型清单与配方表各加一行。

---

## 5. 目录结构

```
edu-primary-applied/
├── SKILL.md                    # 技能指令（触发词 / 工作流 / 五步配方）
├── README.md                   # 本文档（实现技术 + 使用方法）
├── template/board.html         # 通用引擎：STATE/DRAW/DIAGRAM 分派表 + evalExpr + 数据岛
├── lib/
│   ├── generators.py           # 45 个 gen_*（答案先行好数采样）
│   ├── builders.py             # 45 个 build_*（题型 → schema）
│   └── steps.py                # 45 个 *_steps（中文分步讲解）
├── scripts/generate.py         # 注入模板 + REGISTRY + 批量/单题/种子复现
├── references/
│   ├── conventions.md          # 好数配方表 / 渲染器家族 / 关键坑 / 扩展配方
│   └── problem-schema.md       # 统一 schema / STATE / DRAW / answer 键表
├── tests/
│   ├── test_generators.py      # 45 类 × 1000 抽样
│   └── test_builders.py        # 45 类 schema 自检
└── verify.mjs                  # Playwright 无头端到端自检
```

---

## 6. 今日增量（本会话完成）

在原 **19 类主干**基础上，按「A（教材核心）→ B（奥数拓展）→ C（家族变体）」补齐 **26 类**：

- **A 组 12 类**：分数（3）、百分数（2）、比与比例（2）、浓度（1）、行程扩展（1）、还原（1）、
  移多补少（1）、间隔变体（1）。
- **B 组 9 类**：牛吃草、方阵、抽屉原理、时钟夹角、消去法、等差数列、租船最省钱、页码、
  三数和差倍——多数复用 `bar-model`，仅新增 `phalanx`、`clock` 两个轻量 DRAW。
- **C 组 5 类**：盈亏两盈/两亏、植树一端栽/两端不栽/环形——复用 `bar-model` 与 `interval`
  的 `mode` 泛化。

其中修复一处存量隐患：盈亏的「亏」`d` 未约束导致个别随机种子下蓝条在采样点变负，
现约束 `d < c` 保色块全程恒正。全部 **45 类 × 1000 抽样 + schema 自检 + 90 个 HTML
端到端 verify 均绿**。
