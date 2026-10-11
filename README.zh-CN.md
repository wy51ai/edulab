# edulab

**简体中文** · [English](README.md)

教育类技能集合：把学科问题转成**可交互的教学网页**和**带配音的讲解视频**。

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

## 技能：edu-math-video

![edu-math-video 演示](edu-math-video.jpg)

把一道数学题（几何、代数、函数、行程问题……）做成 **16:9、1920×1080 的讲解视频 MP4**：智谱 **GLM-TTS** 中文配音、中英双语字幕（同时输出 `.srt`）、按旁白时间轴驱动的手绘笔记本风格 canvas 动画。输入可以是题目截图或文字。

**图会"讲题"**：每句旁白在图上都有一个"指 → 动 → 留"的动作（相等线段滑过去重合、全等三角形叠上去、3D 相机转到俯视、圆锥侧面展开成扇形……），用 `S.at(k, f)`（第 k 句开始后 f 比例处）定时，绝不写死秒数；`motion` 检查会拦下静止不动的句子。

**流水线**（每个视频一个文件夹，建在用户当前目录）：

```
script.json ──build_audio.py──► timeline.json + mix.wav + <name>.srt   （GLM-TTS + 合成音乐）
anim.js + engine.js ──node render.mjs video──► <name>.mp4              （Playwright + ffmpeg，30 fps）
```

**护栏**：第一幕展示原题并逐条框出条件；`tts` 字段只能是能念出来的中文（无数字/数学符号）；多音字必须固定读音（`长[cháng]`，共享 `pron.json` 词表），`--check` 为 0 才允许调用付费 TTS；先免费 `--preview` + 截图拼图审查版面，再生成真配音；`--asr` 把配音转回文字核对字母读音。

**触发词**：讲解视频、解题视频、例题精讲、微课、数学题视频；math explainer video、walkthrough video 等。

### 依赖

- Python 3 + `numpy requests pypinyin pillow`；Node.js 18+ + `playwright` + `ffmpeg-static`（在工作目录装一次，`scripts/new_video.sh` 会生成 `package.json`）；Google Chrome 或 Playwright Chromium。
- 由你自己提供的智谱 **`GLM_API_KEY`**，写在 `~/.config/math-problem-video/.env`（见 `reference/glm-tts-setup.md`）。
- **没有 key？** 自动兜底（`TTS_ENGINE=auto`）：装了 [edge-tts](https://github.com/rany2/edge-tts) 就用它（免费神经网络音色，需联网），否则用 macOS 自带的 `say`（离线，机械感明显）。也可用 `TTS_ENGINE=glm|edge|say` 指定。

### 手动跑流水线（不经过 Claude）

```bash
bash skills/edu-math-video/scripts/new_video.sh "$PWD" my_problem   # 从 template/ 建项目
bash skills/edu-math-video/scripts/setup_check.sh my_problem        # 必须输出 ALL OK
cd my_problem
python3 build_audio.py --check                                      # 脚本 + 读音检查（免费）
python3 build_audio.py --preview && node render.mjs motion && node render.mjs stills auto
python3 build_audio.py && node render.mjs video 6                   # 真配音，然后渲染（6 = 并行页数）
```

## 技能：edu-physics-video

![edu-physics-video 演示](edu-physics-video.jpg)

把一道物理题（力学、光学、电磁学……）做成 **16:9、1920×1080 的讲解视频 MP4**：智谱 **GLM-TTS** 中文配音、中英双语字幕（同时输出 `.srt`）、按旁白时间轴驱动的蓝图画布动画。输入可以是题目截图或文字。流水线与 edu-math-video 相同，区别在解题方法和画面。

**画面跟着物理走**：建模，把运动分成几段，画受力，选规律，求解，再验算。力箭头按同一比例从作用点长出，物体位置来自解析解 `x(t)`，经 `simT()` 线性映射到屏幕时间，v–t 图同步生长，摩擦力随相对运动反向而转向。用 `S.at(k, f)` 定时。

**流水线**（每个视频一个文件夹，建在用户当前目录）：

```
script.json ──build_audio.py──► timeline.json + mix.wav + <name>.srt   （GLM-TTS + 合成音乐）
anim.js + phys.js + engine.js ──node render.mjs video──► <name>.mp4    （Playwright + ffmpeg，30 fps）
```

**护栏**：第一幕展示原题并逐条框出条件；`tts` 只能是能念出来的中文（单位要读出来，无数字或数学符号；θ 读作西塔）；多音字必须固定读音，`--check` 为 0 才允许调用付费 TTS；先免费 `--preview` 再拿截图拼图审查版面，然后生成真配音；`--asr` 把配音转回文字核对字母读音。通用物理道具加在 `phys.js`。不要改 `engine.js`。

**触发词**：物理题视频、受力分析、牛顿定律、斜面、平抛、圆周、能量、动量、折射；physics explainer video, force diagram, Newton's laws, projectile, circular motion, refraction 等。

### 依赖

与 edu-math-video 相同：Python 3 + `numpy requests pypinyin pillow`；Node.js 18+ + `playwright` + `ffmpeg-static`；智谱 **`GLM_API_KEY`** 写在 `~/.config/math-problem-video/.env`（三个视频技能共用）。没有 key 时 `TTS_ENGINE=auto` 依次用 edge-tts、macOS `say`。

### 手动跑流水线（不经过 Claude）

```bash
bash skills/edu-physics-video/scripts/new_video.sh "$PWD" my_problem
bash skills/edu-physics-video/scripts/setup_check.sh my_problem        # 必须输出 ALL OK
cd my_problem
python3 build_audio.py --check
python3 build_audio.py --preview && node render.mjs motion && node render.mjs stills auto
python3 build_audio.py && node render.mjs video 6
```

## 技能：edu-chem-video

![edu-chem-video 演示](edu-chem-video.jpg)

把一道化学题（氧化还原配平与双线桥、物质的量、化学平衡与三段式、离子反应、电化学、滴定、工业流程……）做成 **16:9、1920×1080 的讲解视频 MP4**：同样的中文配音和中英双语字幕，画面是**墨绿黑板**。配平后的方程式钉在顶部方程式条，左边演示、右边石板。

**方程式在讲题，守恒被数出来**：化合价在数轴上升降，电子一组组长到相等，系数从电子行飞进方程式，原子计数条打上 ✓，双线桥画出电子流动，分子盒按系数比反应，三段式逐行填写。动笔之前用 `scripts/chem_check.py` 核对配平、原子守恒和电荷守恒。`tts` 里化学式换成名称（`HNO3` → 硝酸，`SO4^{2-}` → 硫酸根离子）；字幕 `zh` 保留化学式并自动排成下标。

**流水线**：结构同上，在 `engine.js` 旁使用 `chem.js`（`equation`、`valence`、`bridge`、`eFlow`、`tally`、`molMap`、`iceTable`、`molecule`、`beaker`、`graph`）。

**护栏**：TTS、预览和 `--asr` 与另外两个视频技能相同，并且 `chem_check.py check` 必须退出码为 0。化合价、系数、双线桥起止、分子数量都与解题卡一致。失电子 / 升价用蓝，得电子 / 降价用红。通用化学道具加在 `chem.js`。不要改 `engine.js`。

**触发词**：化学题视频、氧化还原配平、双线桥、电子守恒、物质的量、化学平衡、三段式、滴定；chemistry explainer video, redox, electron conservation, ICE table, titration 等。

### 依赖

与 edu-math-video 相同（共用 `GLM_API_KEY` 和兜底引擎）。`scripts/chem_check.py` 不需要额外的包，用来核对系数、原子 / 电荷守恒和摩尔质量。

### 手动跑流水线（不经过 Claude）

```bash
bash skills/edu-chem-video/scripts/new_video.sh "$PWD" my_problem
bash skills/edu-chem-video/scripts/setup_check.sh my_problem           # 必须输出 ALL OK
cd my_problem
python3 build_audio.py --check
python3 build_audio.py --preview && node render.mjs motion && node render.mjs stills auto
python3 build_audio.py && node render.mjs video 6
```

## 技能：edu-motion-problems

把一道小学行程问题（追及 / 相遇 / 环形跑道）解成一个自包含、零外部依赖的交互课件：题面 + 道路 / 环形跑道动画 + s-t 图 + 时间滑块驱动实时重算 + 动态读数 + 三态状态条 + 分步讲解。原生 Canvas 2D，无 KaTeX / Three.js / CDN，离线可用、可直嵌小程序 web-view。

**覆盖题型**：追及（同向）、相遇（相向）、环形追及、环形相遇。统一物理模型 `kind ∈ {linear, circular} × direction ∈ {same, opposite}`，s-t 图画「展开弧长（不取模）」，四种题型共用同一渲染器。

**答案先行采样**：追上 / 相遇时间、相遇点、圈数恒为整数，只用标准库 `random` / `math`，无需 sympy / CAS。

**触发词**：行程问题、追及问题、相遇问题、环形跑道；motion problems, pursuit, catch-up, meeting, circular track 等。

### 依赖

无——任意 Python 3 即可；生成的网页不发任何网络请求。

### 命令行直接生成（不经过 Claude）

```bash
cd skills/edu-motion-problems
python3 scripts/generate.py list
python3 scripts/generate.py pursue 42 ./pursue.html
python3 scripts/generate.py all ./out_dir   # 全部题型，各出 2 个随机变体
```

## 技能：edu-primary-applied

小学应用题总入口——**62 类**：追及 / 相遇 / 环形跑道、和差 / 和倍 / 差倍、盈亏、年龄、平均数、鸡兔同笼、植树、工程、周期、归一 / 归总、流水行船、火车过桥、平均速度、分数、百分数、比与比例、比例尺、浓度、折扣、还原、移多补少、爬楼 / 锯木 / 敲钟、牛吃草、抽屉原理、消去法、等差数列、租船最省钱、页码、三数和差倍、方阵、时钟夹角、容斥（韦恩图拖圆）、排列组合搭配（连线图）、逻辑推理（排除法）、烙饼（时间轴）、田忌赛马（拖马配对）、利率利息、天平（拖砝码），以及 8 类几何（等底等高三角形 / 平行四边形、梯形等积变形、平行四边形割补、圆周长 / 面积 / 半圆）。每类都解成一个自包含、零外部依赖的交互课件。

**分派式多渲染器**：`STATE[type]` / `DRAW[scene.kind]` / `DIAGRAM[diagram.kind]` 三张表 + 缓存的动态变量 `evalExpr`。加一个新题型 = 写 generator + build + steps + 一个 `STATE` 分派项；渲染器按家族复用（road / circular / bar-model / interval / progress / sequence / train / swap / venn / link-graph / logic-table / timeline / matchup / balance / geodrag / circle / phalanx / clock）。

**答案先行采样**：答案量恒为整数（纯标准库）。

**触发词**：小学应用题、和差、和倍、差倍、鸡兔同笼、工程、分数、百分数、比与比例、浓度、折扣、追及、相遇、环形跑道；primary applied problem, sum and difference, chicken and rabbit, work rate, fraction, percentage, ratio 等。

### 依赖

无——任意 Python 3 即可；生成的网页不发任何网络请求。

### 命令行直接生成（不经过 Claude）

```bash
cd skills/edu-primary-applied
python3 scripts/generate.py list
python3 scripts/generate.py sum-diff 42 ./sum-diff.html
python3 scripts/generate.py all ./out_dir
```

## 技能：edu-primary-geometry

把一道小学数学「图形与几何」题——**9 类**：面积公式推导（平行四边形 / 三角形 / 梯形 / 圆）、组合图形面积、不规则图形方格估算、三视图、平移旋转轴对称、长方体体积 / 表面积——解成一个自包含、零外部依赖的交互课件，带**可拖拽画布**（顶点吸附整数网格或沿约束线滑动；滑块当「阶段」驱动「剪 → 移 → 拼」动画）。

**可拖拽几何**：共享拖拽层（`geomTransform` 世界坐标 + 指针命中 + `applySnap` 吸附）支撑剪拼推导、方格切分、三视图与对称变换。

**答案先行采样**：底 / 高 / 面积 / 体积恒为整数（纯标准库）。

**触发词**：小学几何、面积、平行四边形、三角形、梯形、圆、组合图形、三视图、平移旋转、轴对称、表面积、体积；geometry, area, parallelogram, triangle, trapezoid, circle, three views, symmetry, cuboid volume 等。

### 依赖

无——任意 Python 3 即可；生成的网页不发任何网络请求。

### 命令行直接生成（不经过 Claude）

```bash
cd skills/edu-primary-geometry
python3 scripts/generate.py list
python3 scripts/generate.py area-parallelogram 42 ./parallelogram.html
python3 scripts/generate.py all ./out_dir
```

## 技能：edu-statistics

把一道小学数学「统计与概率」题——**2 类**：统计图表（条形，拖柱顶补全缺失数据）、可能性（树状图，拖手柄沿数轴数叶子）——解成一个自包含、零外部依赖的交互课件，带可拖拽统计图。

**分派式多渲染器** + 复用 edu-primary-geometry 的拖拽层（`geomTransform` + `applySnap` + `dragAxis` 竖向 / 横向吸附）。统计量 / 概率量恒为整数（纯标准库）。

**触发词**：小学统计、统计图、条形统计图、折线统计图、扇形统计图、可能性、概率、树状图、枚举；statistics, bar chart, line chart, pie chart, probability, tree diagram 等。

### 依赖

无——任意 Python 3 即可；生成的网页不发任何网络请求。

### 命令行直接生成（不经过 Claude）

```bash
cd skills/edu-statistics
python3 scripts/generate.py list
python3 scripts/generate.py stat-chart 42 ./stat-chart.html
python3 scripts/generate.py all ./out_dir
```

## 工作原理

小学技能（edu-motion-problems、edu-primary-applied、edu-primary-geometry、edu-statistics）走一条更轻的流水线——不用 sympy：**答案先行好数采样**（标准库 `random` / `math`）喂给**分派式渲染器**（`STATE[type]` / `DRAW[scene.kind]` / `DIAGRAM[diagram.kind]`），注入零依赖原生 Canvas 2D 模板。下面的中学技能则用 sympy 精确内核。

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
    ├── edu-chem-reaction/       # 化学反应 — 3D（Three.js）+ KaTeX
    │   ├── SKILL.md
    │   ├── template/reaction.html # 数据驱动模板（统一渲染器 + 双引擎 + 数据岛）
    │   ├── lib/
    │   │   ├── reaction_kernel.py  # sympy 配平 + 守恒/原子映射校验 + 键差 + 装配
    │   │   └── molecules.py        # VSEPR 分子几何库
    │   ├── scripts/generate.py
    │   ├── output/
    │   └── references/          # problem-schema.md · conventions.md
    ├── edu-math-video/          # 数学题讲解视频 — GLM-TTS + canvas 动画 → MP4
    │   ├── SKILL.md
    │   ├── template/            # 可直接运行的示例项目（engine.js · anim.js · build_audio.py · render.mjs）
    │   ├── shared/              # pron.py + pron.json —— 共享读音词表
    │   ├── scripts/             # new_video.sh · setup_check.sh · 题目图片与截图拼图工具
    │   ├── examples/cone-parallel/  # 立体几何示例（相机转俯视 · 圆锥展开）
    │   └── reference/           # TTS 配置 · 脚本写法 · 读音 · 画面设计 · 动画 API
    ├── edu-physics-video/       # 物理题讲解视频 — GLM-TTS + 蓝图动画 → MP4
    │   ├── SKILL.md
    │   ├── template/            # 蓝图主题（engine.js · phys.js · anim.js）
    │   ├── shared/
    │   ├── scripts/
    │   ├── examples/laser-curvature/  # 几何光学示例
    │   └── reference/
    ├── edu-chem-video/          # 化学题讲解视频 — GLM-TTS + 黑板动画 → MP4
    │   ├── SKILL.md
    │   ├── template/            # 黑板主题（engine.js · chem.js · anim.js）
    │   ├── shared/
    │   ├── scripts/             # 另有 chem_check.py —— 配平与守恒核对
    │   ├── examples/equilibrium/    # 化学平衡 / 三段式示例
    │   └── reference/
    ├── edu-motion-problems/     # 小学行程问题（追及 / 相遇 / 环形）— 零依赖 Canvas 2D
    │   ├── SKILL.md
    │   ├── template/board.html  # 数据驱动模板（道路 / 环形 + s-t 图 + motionState(t)）
    │   ├── lib/                 # good_numbers.py · builders.py · steps.py
    │   ├── scripts/generate.py
    │   ├── tests/
    │   └── references/
    ├── edu-primary-applied/     # 小学应用题（62 类）— 分派式渲染器，零依赖 Canvas 2D
    │   ├── SKILL.md
    │   ├── template/board.html  # 数据驱动模板（STATE/DRAW/DIAGRAM 分派 + evalExpr）
    │   ├── lib/                 # generators.py · builders.py · steps.py
    │   ├── scripts/generate.py
    │   ├── tests/ · verify.mjs
    │   └── references/
    ├── edu-primary-geometry/    # 小学图形与几何（9 类）— 可拖拽画布，零依赖 Canvas 2D
    │   ├── SKILL.md
    │   ├── template/board.html  # 数据驱动模板（STATE/DRAW 分派 + geomTransform 拖拽层）
    │   ├── lib/                 # generators.py · builders.py · steps.py
    │   ├── scripts/generate.py
    │   ├── tests/ · verify.mjs
    │   └── references/
    └── edu-statistics/          # 小学统计与概率（2 类）— 可拖拽统计图，零依赖 Canvas 2D
        ├── SKILL.md
        ├── template/board.html  # 数据驱动模板（STATE/DRAW 分派 + dragAxis 拖拽层）
        ├── lib/                 # generators.py · builders.py · steps.py
        ├── scripts/generate.py
        ├── tests/ · verify.mjs
        └── references/
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

**edu-math-video**
- **做新题**：不改 `engine.js`；每道题重写 `script.json` / `storyboard.md` / `anim.js`，新图形函数写在 `anim.js` 里。
- **修读音**：把词加进 `shared/pron.json`（`words` / `ok`），所有视频共用一份词表。

**edu-physics-video**
- **做新题**：不改 `engine.js`；每道题重写 `script.json` / `storyboard.md` / `anim.js`。通用物理道具加在 `phys.js`。
- **修读音**：把词加进 `shared/pron.json`。

**edu-chem-video**
- **做新题**：不改 `engine.js`；每道题重写自己的文件。通用化学道具加在 `chem.js`。动笔前用 `scripts/chem_check.py` 核对方程式。
- **修读音**：把词加进 `shared/pron.json`。

**小学技能（edu-motion-problems · edu-primary-applied · edu-primary-geometry · edu-statistics）**
- **加题型**：在 `lib/generators.py` 写答案先行的 `gen_*`（edu-motion-problems 在 `lib/good_numbers.py`），在 `lib/builders.py` 写 `build_*`、`lib/steps.py` 写分步文案，注册进 `scripts/generate.py` 的 `REGISTRY`，再加一个 `STATE[type]` 分派项。若题型 `scene.kind` 落在既有渲染器家族，前端零改动；新家族才在 `template/board.html` 加一个 `DRAW` 渲染器。
- **四者共用同一配方**：「答案先行好数采样 + 分派式渲染器 + 零依赖原生 Canvas 2D」——见各技能 `references/conventions.md` §7。

## License

[Apache-2.0](LICENSE)

## 作者

WY · [@akokoi1](https://x.com/akokoi1)

| 微信公众号 | 小红书 |
|---|---|
| <a href="http://weixin.qq.com/r/mp/kUwUDP3EZKAbrblv9xmD"><img src="qr-wechat.png" alt="微信公众号" width="220"></a> | <a href="http://xhslink.com/m/64K17dDQNvj"><img src="qr-xiaohongshu.png" alt="小红书" width="220"></a> |

## Star History

<a href="https://www.star-history.com/?repos=wy51ai%2Fedulab&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&legend=top-left" />
 </picture>
</a>
