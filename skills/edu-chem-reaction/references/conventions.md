# 建模约定 · 引擎选择 · 配平 · 自检

## 坐标与显示约定
- **场景尺度**：键长 ≈ 1.0–1.4 单位，原子半径见 `molecules.ELEMENTS`（C 0.50 / O 0.42 / H 0.25 …）。
  深色主题（slate-950 背景），原子配色用 CPK 习惯（C 灰、O 红、H 白、N 蓝、Cl 绿、Na 紫…）。
- **VSEPR 理想几何**：分子库给标准朝向的局部坐标（四面体 CH₄、线形 CO₂、弯曲 104.5° 的 H₂O…）。
  分子在场景中的平移/旋转由“装配层”负责（高层路径用实例 `pos/rot`；低层路径用片段关键帧）。
- **三阶段时间轴**（固定）：`[0,0.4)` 接近·分子轻微浮动 → `[0.4,0.7]` 过渡·断成键高亮+热抖动+能量峰
  → `(0.7,1]` 分离。键的不透明度据此推：断键相 1→0（暖色辉光）、成键相 0→1（绿色辉光）、保留键恒 1。

## 原子守恒是“微观演示”的教学核心
- 反应前后**原子种类与数目不变**（质量守恒）。高层路径用 `atom_map` 显式给出每个原子的去向，
  kernel 校验其为**双射**且元素一致；低层路径由 `bonds_before/after` 的同一批原子保证。
- 守恒计数器（顶部芯片）显示各元素原子数，反应前后恒等。**催化剂原子不计入**（循环再生，非反应物/产物）。
- 配键变化由 `bonds_before/after` 的**差集**自动得出：`broken=before−after`、`formed=after−before`、
  `kept=交集`。不要手写每根动态键。

## 引擎选择
| 反应类型 | 引擎 | 理由 |
|---|---|---|
| 燃烧、化合/分解/置换/复分解、氧化还原 | `morph` | 原子各自飞向新搭档，凸显“原子打散重组、守恒” |
| 有机机理（酯化/加成/取代/消去，含催化剂·过渡态·离去基团） | `mechanism` | 基团作刚体整体位移、不变形，凸显机理 |
- `meta.engine="auto"`：`category=="organic"` 或带 `fragments` → mechanism，否则 morph。
- 两引擎共用键差绘制、浮动标签、火焰/催化剂/过渡态/电子/能量叠加层与整套 UI；只是逐帧定位不同。

## 解法配方（按类别）
- **燃烧/化合/分解/置换**（morph）：列反应物/产物物种 → `balanced_coefficients` 配平 →
  写 `atom_map`（哪个原子去哪个产物分子）→ 配 `flame`(燃烧) 或 `under:"电解"` 等条件 → 3 步讲解。
- **氧化还原**（morph + 电子转移）：同上，另加 `electrons:[{from,to}]`（用全局 id），
  讲解里点明化合价升降、氧化/还原、得失电子守恒；可加 `transitionGlow`。
- **有机机理**（mechanism，低层）：把分子拆成片段（保留基团 + 离去基团 + 催化剂），
  给每个原子 `frag/flocal` 与片段 `K0/K1/K2` 关键帧（可直接参考 `generate.py` 的酯化范例），
  `bonds_before/after` 写清断哪两根、成哪两根，`catalyst` 片段标 `catalyst:true`。

## 配平（sympy）
`balanced_coefficients(reactant_species, product_species)`：构造“元素×物种”矩阵，
反应物正、产物负，求零空间 → 化为最小正整数。零空间维数≠1（无解/不唯一）会抛错，
此时由作者用 `meta.equation` 显式给方程并保证配平。`assemble_data` 会断言“实例个数==配平系数”。

## 自检清单（交付前逐条过）
1. `python3 lib/molecules.py`、`python3 lib/reaction_kernel.py` 自检通过。
2. sympy 配平系数 == 方程系数 == 各物种实例数（assemble_data 已断言）。
3. atom_map 双射、元素一致；键端点都存在（kernel 已校验，违例会抛错）。
4. 守恒计数器反应前后不变；断键/成键数与化学事实一致。
5. 浏览器预览：无控制台报错（除 Tailwind CDN 生产警告外）、KaTeX 方程正常、
   拖滑块时 morph/mechanism 动画顺、断成键高亮与分步讲解同步、叠加层（火焰/催化剂/电子/能量）正常。
6. 成品在 cwd、不在技能目录；预览端口已 `preview_stop` 释放。

## 常见坑
- **atom_map 漏配/重复**：kernel 会报“未映射/未知/重复引用”。按 slot 表逐一核对。
- **slot 名写错**：见 `problem-schema.md` 的 slot 表；`python3 lib/molecules.py` 打印各物种原子。
- **机理片段抖飞**：`flocal` 必须是“片段内”坐标（相对片段原点），不是世界坐标；
  片段原点即该片段在 K 关键帧里的 pos。
- **accent 不生效**：accent 走 CSS 变量（`--accent`），用 schema 里列出的色名；自定义色名请在模板
  `ACCENTS` 表里加。
