---
name: edu-chem-reaction
description: >-
  把一个化学反应做成自包含的微观 3D 交互演示网页：左/上为 Three.js 可交互分子动画
  （拖滑块看断键·成键·原子重组，分步高亮），右为 KaTeX 反应方程 + 分步讲解 + 原子守恒计数 +
  可选能量-反应进程曲线。支持三入口——给定文字反应/方程、随机出题、上传图片识别后演示。
  覆盖燃烧、化合/分解/置换/复分解、氧化还原（电子转移可视化）、有机机理（酯化等含催化剂·过渡态）。
  统一由 sympy 精确驱动：自动配平方程、校验原子守恒与原子映射、推导键的断/成，答案与几何同源一致。
  内置两套引擎并自动选择：morph（原子变形，展示原子守恒）与 mechanism（机理关键帧，展示催化/过渡态）。
  混合几何：默认自建 VSEPR 分子库，环境装有 RDKit 则可用其由 SMILES 生成构象（绝不自动安装）。
  其他 agent 也可调用本技能生成此类网页。形态与 edu-solid-geometry / edu-analytic-geometry 平行，
  但用 Three.js + KaTeX 演示分子反应。
  触发词：化学反应, 微观演示, 分子动画, 燃烧, 甲烷燃烧, 氢气燃烧, 电解水, 氧化还原, 电子转移,
  酯化反应, 反应机理, 断键成键, 原子守恒, 质量守恒, 化学方程式配平, 解这个化学反应,
  随机出一个化学反应, 这张图里的化学反应; chemistry reaction, microscopic/molecular animation,
  combustion, electrolysis, redox electron transfer, esterification mechanism, bond breaking and
  forming, atom conservation, balance equation, interactive chemistry reaction page.
---

# 化学反应微观演示 → 交互网页

## 这个技能产出什么
一个可直接用浏览器打开的单页 HTML：一侧是反应对应的 **3D 分子动画**（Three.js，可旋转缩放，
拖动“反应进度”滑块逐帧看 **化学键断裂/生成、原子重新组合**，分步高亮 + 浮动分子标签），
另一侧是 **KaTeX 反应方程 + 分步讲解 + 原子守恒计数器**，并可选 **能量-反应进程曲线**、
火焰、催化剂质子、电子转移等叠加层。形态与 `template/reaction.html` 一致。

## 依赖（重要）
计算核心 `lib/reaction_kernel.py` 依赖 **sympy**（用于配平）。运行脚本前先确认有一个能 import
sympy 的 `python3`：跑 `python3 -c "import sympy"`（本机：`/opt/homebrew/bin/python3.11`）。

**缺库时的处理（重要）**：若 import 报错（sympy 或后续用到的任何库都同理），**先询问用户是否安装**，
同意后再装（`python3 -m pip install <库名>`）或换解释器；**不要未经询问直接装**。
**RDKit 是可选项**：装了则混合几何会用它由 SMILES 生成真实构象，没装就用自建 VSEPR 库——
两种都能跑，**本技能任何时候都不会自动安装 RDKit**。

## 工作流程

### 第 1 步：得到 reaction spec（三入口归一）
把反应整理成结构化 spec（格式见 `references/problem-schema.md`）：反应物/产物、原子映射或显式原子、
条件（点燃/通电/催化/可逆）、所属类别、分步讲解、**语言**。
- **文字反应/方程**：直接抽取反应物与产物，调 kernel 自动配平。
- **图片**：用视觉读图抽取方程，并**把识别到的反应回显给用户确认**（方程/条件/类别/语言）后再继续。
- **随机出题**：从注册表挑一个反应，或在库内物种间组合并用 `balanced_coefficients` 配平、答案规整再用。

> **输出语言跟随提示词语言**：英文提示 → 英文网页，中文 → 中文。spec 里记下 `meta.language`。

### 第 2 步：用 kernel 精确计算（不要心算）
按 `references/conventions.md` 的建模约定，调用 `lib/reaction_kernel.py`：
- `balanced_coefficients(...)` 用 sympy 零空间**自动配平**（方程系数有保证）；
- `assemble_data(spec)` 展开分子实例、**校验原子守恒与原子映射双射**、**推导键的断/成（差集）**、
  算出每个原子在反应物态/产物态的世界坐标，产出注入模板的 `data`。

可先命令行自检：
```bash
python3 lib/reaction_kernel.py     # 配平 + 守恒 + 键差 自检
python3 lib/molecules.py           # 分子库自检
```

### 第 3 步：写 build_* 拼 spec 并注入模板

> 📍 **输出位置（重要）**：成品 HTML 一律写到**用户当前工作目录（`Path.cwd()`）**，除非用户显式指定路径。
> **绝不要**写进技能自身目录（`skills/edu-chem-reaction/output/` 等）——那是技能内部的开发样例目录。

照着 `scripts/generate.py` 里的 `build_*` 改即可，再 `render_html(K.assemble_data(spec), out)`：
```python
from pathlib import Path
out = Path.cwd() / "reaction-<反应简述>.html"   # 落在用户当前目录
render_html(K.assemble_data(spec), out)
```
**范例（直接照抄改）**：
- `build_combustion_ch4`（甲烷燃烧·morph·火焰·能量）——高层 `species + atom_map` 的范本；
- `build_redox_na_cl2`（钠+氯气·氧化还原·电子转移）——叠加 `electrons`；
- `build_esterification`（酯化·mechanism·催化剂·过渡态）——低层 `atoms + fragments + 关键帧` 的范本。

`generate.py` 可直接出已注册反应；**不传路径默认写到 cwd**：
```bash
python3 <技能目录>/scripts/generate.py combustion_ch4 ./reaction.html
python3 <技能目录>/scripts/generate.py list
```

### 第 4 步：自检（对应正确性方案）
- sympy 配平系数 == 方程展示系数 == 各分子实例个数（`assemble_data` 内已断言）。
- 原子映射是反应物↔产物原子的**双射**、元素一致；键端点都存在（kernel 已校验）。
- 原子守恒计数器在反应前后不变（催化剂不计入）。
- 起本地静态服务（服务**输出文件所在目录**）用预览检查：无控制台报错、KaTeX 方程渲染正常、
  拖滑块时断键/成键高亮与分步讲解一致。

> ⚠️ **必须关闭你开过的端口/服务**：预览检查一结束就立即停掉本地服务，**绝不留下占用端口的进程**。
> 用 preview 工具开的：检查完马上 `preview_stop`。交付前确认端口已释放，再告诉用户结果。

### 第 5 步：交付
成品写在**用户当前工作目录（cwd）**，命名形如 `reaction-<反应简述>.html`，把路径告诉用户，可直接浏览器打开。
交付前确认：**(1)** 成品在 cwd、不在技能目录；**(2)** 没有遗留任何由本次预览开启的本地服务/端口。

## 两套引擎与自动选择
模板内置一套统一渲染器、两种逐帧定位（共用键差绘制/标签/叠加层/UI）：
- **morph**（原子变形）：原子各自从反应物态插值到产物态，天然展示**原子守恒/重组**，适配任意反应。
- **mechanism**（机理关键帧）：原子归属刚体片段（fragment），按 K0/K1/K2 关键帧整体位移，
  基团不变形，适配**催化剂/过渡态/离去基团**类有机机理。

`assemble_data` 据 `meta.engine`（`auto`/`morph`/`mechanism`）选择：`auto` 时，类别为 `organic`
或带 `fragments` 走 mechanism，否则走 morph。叠加层均为数据开关（见 schema）：
`flame`（燃烧/强放热）、`catalyst`（催化剂质子+开关）、`transitionGlow`（过渡态能量光）、
`electrons`（氧化还原电子转移）、`energy`（能量-反应进程曲线）、原子守恒计数器（默认开）。

**配色**：整体为亮色（教科书球棍图风：原子带深色描边 + 柔和投影 + 白底面板），各反应用 `meta.accent`
区分强调色（燃烧 amber、酯化 indigo、钠氯 violet…）。

## 扩展
- **加反应**：在 `generate.py` 加一个 `build_*`（高层 `species+atom_map`，或低层 `atoms+fragments`），
  注册进 `REGISTRY`。
- **加分子/离子**：在 `lib/molecules.py` 的 `_LIBRARY_BUILDERS` 加一项（VSEPR 几何 + 显示元数据 + 内部键）。
- **加叠加层**：在 `template/reaction.html` 增一个由 `data` 字段驱动的可选模块。

## 目录
- `template/reaction.html` — 数据驱动模板（统一渲染器 + 双引擎 + 数据岛 `__REACTION_DATA__`）
- `lib/molecules.py` — VSEPR 理想分子几何库（含元素表/配色/半径）
- `lib/reaction_kernel.py` — sympy 配平 + 守恒/映射校验 + 键差 + 场景装配 + 可选 RDKit 探测
- `scripts/generate.py` — 注入模板 + 范例 build_*（含 REGISTRY 与 CLI）
- `references/problem-schema.md` — reaction spec 与 data 的数据格式
- `references/conventions.md` — 建模约定、引擎选择、叠加层、配平与自检
