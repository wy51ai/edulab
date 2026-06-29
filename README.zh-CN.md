# edulab

**简体中文** · [English](README.md)

教育类技能集合：把学科问题转成**可交互的教学网页**。

## 安装

**推荐** —— 用 [skills](https://github.com/vercel-labs/skills) 一行命令安装：

```bash
npx skills add wy51ai/edulab
```

后续更新到最新版：

```bash
npx skills update
```

> **注意**：`npx skills update` 只会把**已安装**的技能刷新到最新版，**不会**自动拉取仓库新增的技能。当本仓库新增了技能（如新的 `edu-*`）时，再次运行 `npx skills add wy51ai/edulab` 即可装上。

或作为 Claude Code 插件市场使用：

```
/plugin marketplace add wy51ai/edulab
/plugin install edulab
```

安装后，技能会随触发词自动激活，也可以手动调用。

## 技能：edu-solid-geometry

![edu-solid-geometry 演示](edu-solid-geometry.gif)

把一道立体几何题解成一个自包含的交互教学网页。支持三种入口：

| 入口 | 说明 |
|---|---|
| 文字题目 | 直接抽取题面求解 |
| 上传图片 | 视觉读图识别题目，回显确认后求解 |
| 随机出题 | 随机参数求解，答案不规整自动重抽 |

**覆盖题型**：正方体 / 长方体、棱锥 / 棱柱、圆柱 / 圆锥上的——线面角、二面角、异面直线夹角、点到平面距离、体积等。统一用"建系 + 向量法"。

**触发词**：立体几何、线面角、二面角、异面直线、点到平面距离、正四棱锥、解这道几何题、随机出一道立体几何题、这张图里的立体几何题；solid geometry, line-plane angle, dihedral angle, distance to plane, interactive geometry solution page 等。

### 依赖

计算核心 `lib/geometry_kernel.py` 依赖 **sympy**。用任意一个能 import sympy 的 `python3` 即可：

```bash
python3 -m pip install sympy   # 若缺 sympy
```

### 命令行直接生成（不经过 Claude）

```bash
cd skills/edu-solid-geometry
python3 scripts/generate.py cube   ./cube.html     # 正方体·线面角
python3 scripts/generate.py box    ./box.html      # 长方体·体积
python3 scripts/generate.py random 7 ./random.html # 随机出题（seed=7）
python3 lib/geometry_kernel.py                     # kernel 内置样例自检
```

> 不传输出路径时，默认写到**当前工作目录（cwd）**。

## 技能：edu-analytic-geometry

![edu-analytic-geometry 演示](edu-analytic-geometry.gif)

把一道解析几何（圆锥曲线）题解成一个自包含的交互教学网页。三入口与上面一致（文字 / 图片 / 随机）。基于 **2D Canvas 画板 + KaTeX** 的通用数据驱动交互引擎：一个参数滑块驱动派生构造（直线∩曲线、曲线上动点、中心对称、切线…）与实时读数，并配理论范围条或定值指示。

**覆盖题型**：求标准方程、弦长、向量数量积取值范围 / 定值、三角形面积最值、定点、定值（斜率之积）、轨迹、切线、离心率——涵盖椭圆 / 双曲线 / 抛物线 / 圆。统一用"设含参直线 `x=my+c` + 联立 + 韦达 + 换元"。

> kernel 内置的一个正确性细节：区间端点的开 / 闭由"是否有真实直线取到"判定，所以框出的答案始终与交互工具一致（例如椭圆 `MA·MB` 的范围是**闭区间** `[-3, 7/4]`——把 θ 拖到 0° 屏幕上正好读到 −3）。

**触发词**：解析几何、圆锥曲线、椭圆、双曲线、抛物线、焦点弦、向量数量积取值范围、定点问题、定值问题、斜率之积、三角形面积最值、轨迹方程、离心率；analytic geometry, conic sections, ellipse, hyperbola, parabola, chord length, dot product range, fixed point, locus, interactive analytic geometry solution page 等。

### 依赖

计算核心 `lib/analytic_kernel.py` 依赖 **sympy**（同上）。

### 命令行直接生成（不经过 Claude）

```bash
cd skills/edu-analytic-geometry
python3 scripts/generate.py list                          # 列出已注册题型
python3 scripts/generate.py ellipse_dot_range ./sol.html  # 椭圆 · MA·MB 范围 [-3, 7/4]
python3 scripts/generate.py parabola_dot_const ./sol.html # 抛物线焦点弦 · OA·OB ≡ -3
python3 scripts/generate.py all ./out_dir                 # 全部已注册题型
python3 lib/analytic_kernel.py                            # kernel 内置自检
```

> 同上，不传输出路径时默认写到**当前工作目录（cwd）**。

## 技能：edu-chem-reaction

![edu-chem-reaction 演示](edu-chem-reaction.gif)

把一个化学反应做成自包含的**微观 3D 演示**网页：一侧是可交互的 Three.js 分子动画（拖滑块看化学键断裂 / 生成、原子重新组合，分步高亮），另一侧是 KaTeX 反应方程 + 分步讲解 + 原子守恒计数 + 可选能量-反应进程曲线。三入口与上面一致（文字 / 图片 / 随机）。

**双引擎自动选择** —— 一套渲染器、两种逐帧定位，共用键差绘制、标签、叠加层与 UI：

| 引擎 | 适用 | 强调 |
|---|---|---|
| morph | 燃烧、化合 / 分解 / 置换、氧化还原 | 原子各自飞向新搭档——原子守恒与重组 |
| mechanism | 有机机理（酯化…），含催化剂 · 过渡态 · 离去基团 | 分子片段按关键帧刚体位移——反应机理 |

**sympy 驱动的正确性**：自动配平方程（由元素矩阵零空间求整数计量数）、校验原子映射（反应物↔产物原子的双射）与守恒，并由反应前后键的差集推导哪根键断 / 成——方程、几何、计数器同源一致。

**混合几何**：默认用自建 VSEPR 分子库；若环境装有 RDKit 则可由 SMILES 生成构象（绝不自动安装）。

**覆盖反应**：甲烷 / 氢气燃烧、电解水、钠与氯气氧化还原（含电子转移叠加层）、葡萄糖有氧氧化、酯化机理——涵盖初中基础、高中无机氧化还原与有机机理。

**触发词**：化学反应、微观演示、分子动画、燃烧、电解水、氧化还原、电子转移、酯化反应、断键成键、原子守恒、化学方程式配平；chemistry reaction, microscopic/molecular animation, combustion, electrolysis, redox electron transfer, esterification mechanism, atom conservation, interactive chemistry reaction page 等。

### 依赖

计算核心 `lib/reaction_kernel.py` 依赖 **sympy**（同上）。**RDKit 为可选项**——装了才用，绝不自动安装。

### 命令行直接生成（不经过 Claude）

```bash
cd skills/edu-chem-reaction
python3 scripts/generate.py list                            # 列出已注册反应
python3 scripts/generate.py combustion_ch4 ./reaction.html  # 甲烷燃烧（morph · 火焰）
python3 scripts/generate.py esterification ./reaction.html  # 酯化反应（mechanism · 催化剂）
python3 scripts/generate.py random 7 ./random.html          # 随机出题（seed=7）
python3 lib/reaction_kernel.py                              # kernel 内置自检
```

> 同上，不传输出路径时默认写到**当前工作目录（cwd）**。

## 工作原理

1. **得到 problem spec** —— 三入口归一成结构化描述（几何体类型与尺寸、已知条件、所求、语言）。
2. **kernel 精确计算** —— sympy 算出精确坐标、关键向量、法向量、最终答案及各步中间量（LaTeX 字符串），绝不心算。
3. **组装并注入模板** —— 把 `lesson` / `steps` / `model` 数据注入数据驱动模板 `template/lesson.html`，3D 顶点坐标由 `kernel.to_three(...)` 给出，与解题同源。
4. **自检** —— kernel 答案 == 答案卡 == 末步骤展示值；本地静态服务 + 预览检查无报错、公式与高亮正常。
5. **交付** —— 成品写到用户当前工作目录，命名形如 `solution-<题目简述>.html`。

## 目录结构

```
edulab/
├── .claude-plugin/
│   ├── plugin.json              # 插件元信息
│   └── marketplace.json         # 市场清单
├── index.html                   # 成品样例（正四棱锥·线面角）
└── skills/
    ├── edu-solid-geometry/      # 立体几何 — 3D（Three.js）+ MathJax
    │   ├── SKILL.md
    │   ├── template/lesson.html # 数据驱动模板（通用 3D 渲染器 + 数据岛）
    │   ├── lib/
    │   │   ├── geometry_kernel.py  # sympy 精确计算核心
    │   │   └── bodies.py           # 几何体棱拓扑库
    │   ├── scripts/generate.py
    │   ├── output/
    │   └── references/          # problem-schema.md · conventions.md
    ├── edu-analytic-geometry/   # 解析几何 / 圆锥曲线 — 2D（Canvas）+ KaTeX
    │   ├── SKILL.md
    │   ├── template/board.html  # 数据驱动模板（通用 2D 渲染器 + 参数引擎）
    │   ├── lib/
    │   │   ├── analytic_kernel.py  # sympy 精确求解核心（联立·韦达·范围·定值）
    │   │   └── conics.py           # 圆锥曲线定义库
    │   ├── scripts/generate.py
    │   ├── output/
    │   └── references/          # problem-schema.md · conventions.md
    └── edu-chem-reaction/       # 化学反应 — 3D（Three.js）+ KaTeX
        ├── SKILL.md
        ├── template/reaction.html # 数据驱动模板（统一渲染器 + 双引擎 + 数据岛）
        ├── lib/
        │   ├── reaction_kernel.py  # sympy 配平 + 守恒/原子映射校验 + 键差 + 装配
        │   └── molecules.py        # VSEPR 分子几何库
        ├── scripts/generate.py
        ├── output/
        └── references/          # problem-schema.md · conventions.md
```

## 扩展

**edu-solid-geometry**
- **加题型**：在 `geometry_kernel.py` 加求解函数（见 `references/conventions.md` 配方表），在 `generate.py` 加一个 `build_*`。
- **加几何体**：在 `geometry_kernel.py` 加坐标构建函数，在 `bodies.py` 加棱拓扑。

**edu-analytic-geometry**
- **加题型**：在 `analytic_kernel.py` 加目标量函数并复用 `range_over_m` / `is_constant_in_m`，在 `generate.py` 加一个 `build_*`（选交互范式：范围条 / 定值 / 定点 / 轨迹 trace）。
- **加曲线**：椭圆 / 双曲线 / 抛物线 / 圆已内置；新曲线在 `conics.py` 与 `board.html` 引擎各加一份。

**edu-chem-reaction**
- **加反应**：在 `generate.py` 加一个 `build_*`（高层 `species + atom_map`，或低层 `atoms + fragments` 用于机理），注册进 `REGISTRY`。
- **加分子 / 离子**：在 `lib/molecules.py` 加一项（VSEPR 几何 + 显示元数据 + 内部键）。

## License

[Apache-2.0](LICENSE)

## 作者

WY · [@akokoi1](https://x.com/akokoi1)

## Star History

<a href="https://www.star-history.com/?repos=wy51ai%2Fedulab&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&legend=top-left" />
 </picture>
</a>
