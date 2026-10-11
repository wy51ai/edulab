# edulab

[简体中文](README.zh-CN.md) · **English**

A collection of education skills that turn academic problems into **interactive lesson web pages** and **narrated explainer videos**.

## Install

**Recommended** — install with [skills](https://github.com/vercel-labs/skills) in one command:

```bash
npx skills add wy51ai/edulab
```

To update to the latest version later:

```bash
npx skills update
```

> **Note:** `npx skills update` only refreshes skills you've **already** installed — it does **not** pull in skills newly added to the repo. When this repo gains a new skill (e.g. a new `edu-*`), run `npx skills add wy51ai/edulab` again to install it.

Or use it as a Claude Code plugin marketplace:

```
/plugin marketplace add wy51ai/edulab
/plugin install edulab
```

Once installed, the skills activate on their trigger words, and can also be invoked manually.

## Skill: edu-solid-geometry

![edu-solid-geometry demo](edu-solid-geometry.gif)

Solves one solid geometry problem into a self-contained interactive lesson page. Three entry points:

| Entry point | What it does |
|---|---|
| Text problem | Extracts the statement and solves directly |
| Image upload | Reads the problem from the image via vision, echoes it back for confirmation, then solves |
| Random problem | Solves with random parameters; re-rolls if the answer isn't clean |

**Problem types covered**: line-plane angle, dihedral angle, angle between skew lines, point-to-plane distance, volume, and more — on cubes / cuboids, pyramids / prisms, cylinders / cones. All solved uniformly via the "coordinate system + vector method."

**Trigger words**: solid geometry, line-plane angle, dihedral angle, angle between skew lines, distance to plane, interactive geometry solution page; 立体几何、线面角、二面角、异面直线、点到平面距离、正四棱锥、解这道几何题、随机出一道立体几何题、这张图里的立体几何题, etc.

### Dependency

The compute core `lib/geometry_kernel.py` depends on **sympy**. Use any `python3` that can import sympy:

```bash
python3 -m pip install sympy   # if sympy is missing
```

### Generate from the command line (without Claude)

```bash
cd skills/edu-solid-geometry
python3 scripts/generate.py cube   ./cube.html     # cube · line-plane angle
python3 scripts/generate.py box    ./box.html      # cuboid · volume
python3 scripts/generate.py random 7 ./random.html # random problem (seed=7)
python3 lib/geometry_kernel.py                     # kernel built-in self-check
```

> If you don't pass an output path, it writes to the **current working directory (cwd)**.

## Skill: edu-analytic-geometry

![edu-analytic-geometry demo](edu-analytic-geometry.gif)

Solves one analytic geometry (conic sections) problem into a self-contained interactive lesson page. Same three entry points as above (text / image / random). Built on a **2D Canvas board + KaTeX** with a generic, data-driven interactive engine: a parameter slider drives derived constructions (line∩conic, point-on-conic, central reflection, tangent…) and live readouts, with a theoretical-range bar or a fixed-value indicator.

**Problem types covered**: standard equation, chord length, dot-product range / fixed value, triangle-area extremum, fixed point, fixed value (slope product), locus, tangent, eccentricity — on ellipses / hyperbolas / parabolas / circles. All solved uniformly via "parametrized line `x = my + c` + system + Vieta's formulas + substitution."

> A correctness note baked into the kernel: open/closed interval endpoints are decided by whether a *real* line attains them, so the boxed answer always matches what the interactive tool shows (e.g. the ellipse `MA·MB` range is the **closed** `[-3, 7/4]` — slide θ to 0° and you read exactly −3).

**Trigger words**: analytic geometry, conic sections, ellipse, hyperbola, parabola, chord length, dot product range, fixed point, fixed value, locus, eccentricity, interactive analytic geometry solution page; 解析几何、圆锥曲线、椭圆、双曲线、抛物线、焦点弦、向量数量积取值范围、定点问题、定值问题、斜率之积、三角形面积最值、轨迹方程、离心率, etc.

### Dependency

The compute core `lib/analytic_kernel.py` depends on **sympy** (same as above).

### Generate from the command line (without Claude)

```bash
cd skills/edu-analytic-geometry
python3 scripts/generate.py list                          # list registered problem types
python3 scripts/generate.py ellipse_dot_range ./sol.html  # ellipse · MA·MB range [-3, 7/4]
python3 scripts/generate.py parabola_dot_const ./sol.html # parabola focal chord · OA·OB ≡ -3
python3 scripts/generate.py all ./out_dir                 # all registered types
python3 lib/analytic_kernel.py                            # kernel built-in self-check
```

> Like above, no output path → writes to the **current working directory (cwd)**.

## Skill: edu-chem-reaction

![edu-chem-reaction demo](edu-chem-reaction.gif)

Turns one chemical reaction into a self-contained **microscopic 3D demonstration** page: an interactive Three.js molecular animation (drag the slider to watch bonds break / form and atoms recombine, with step highlighting) next to the KaTeX equation, step-by-step narration, an atom-conservation counter, and an optional energy–reaction-coordinate curve. Same three entry points (text / image / random).

**Two engines, auto-selected** — one renderer with two per-frame position resolvers, sharing the bond-diff drawing, labels, overlays and UI:

| Engine | For | Emphasizes |
|---|---|---|
| morph | combustion, combination / decomposition / displacement, redox | atoms fly to new partners — atom conservation & recombination |
| mechanism | organic mechanisms (esterification…) with catalyst · transition state · leaving groups | rigid fragments move through keyframes — the mechanism |

**sympy-driven correctness**: auto-balances the equation (integer coefficients from the matrix null space), validates the atom map (a bijection between reactant and product atoms) and conservation, and derives which bonds break / form from the before↔after difference — equation, geometry and counters all share one source.

**Hybrid geometry**: a built-in VSEPR molecule library by default; if RDKit is installed it can build conformers from SMILES (never installs it automatically).

**Reactions covered**: methane / hydrogen combustion, water electrolysis, Na + Cl₂ redox (with an electron-transfer overlay), glucose aerobic oxidation, and the esterification mechanism — spanning junior-high basics, senior inorganic redox, and organic mechanisms.

**Trigger words**: chemistry reaction, microscopic / molecular animation, combustion, electrolysis, redox electron transfer, esterification mechanism, bond breaking and forming, atom conservation, balance equation, interactive chemistry reaction page; 化学反应、微观演示、分子动画、燃烧、电解水、氧化还原、电子转移、酯化反应、断键成键、原子守恒、化学方程式配平 etc.

### Dependency

The compute core `lib/reaction_kernel.py` depends on **sympy** (same as above). **RDKit is optional** — used only if already installed, never installed automatically.

### Generate from the command line (without Claude)

```bash
cd skills/edu-chem-reaction
python3 scripts/generate.py list                            # list registered reactions
python3 scripts/generate.py combustion_ch4 ./reaction.html  # methane combustion (morph · flame)
python3 scripts/generate.py esterification ./reaction.html  # esterification (mechanism · catalyst)
python3 scripts/generate.py random 7 ./random.html          # random reaction (seed=7)
python3 lib/reaction_kernel.py                              # kernel built-in self-check
```

> Like above, no output path → writes to the **current working directory (cwd)**.

## Skill: edu-math-video

![edu-math-video demo](edu-math-video.jpg)

Turns one math problem (geometry, algebra, functions, motion problems…) into a **16:9 1920×1080 explainer MP4**: Chinese voice-over (Zhipu **GLM-TTS**), bilingual zh + en subtitles (`.srt` too), and hand-drawn notebook-style canvas animation driven by the narration timeline. Input is a problem screenshot or plain text.

**The picture explains the step**: every narration line gets a "point → move → keep" action on the figure (equal segments slide onto each other, congruent triangles overlay, the 3D camera tweens to a top view, a cone unrolls into a sector…) — timed by `S.at(k, f)` (a fraction into line *k*), never by hard-coded seconds. A `motion` check rejects static lines.

**Pipeline** (one folder per video, created in the user's current directory):

```
script.json ──build_audio.py──► timeline.json + mix.wav + <name>.srt   (GLM-TTS + synthesized music)
anim.js + engine.js ──node render.mjs video──► <name>.mp4              (Playwright + ffmpeg, 30 fps)
```

**Guard rails**: the first scene shows the original problem with each condition boxed as it is read; `tts` text must be speakable Chinese (no digits / math symbols); polyphones are pinned (`长[cháng]`, shared `pron.json` lexicon) and `--check` must report 0 before any paid TTS call; a free `--preview` + contact-sheet review comes before real audio; `--asr` transcribes the audio back to catch misread letters.

**Trigger words**: math explainer video, walkthrough video, problem-solving video, micro-lesson; 讲解视频、解题视频、例题精讲、微课 etc.

### Dependency

- Python 3 with `numpy requests pypinyin pillow`; Node.js 18+ with `playwright` + `ffmpeg-static` (installed once in the workspace — `scripts/new_video.sh` writes the `package.json`); Google Chrome or Playwright Chromium.
- A Zhipu **`GLM_API_KEY`** provided by you, in `~/.config/math-problem-video/.env` (see `reference/glm-tts-setup.md`).
- **No key?** It falls back automatically (`TTS_ENGINE=auto`): [edge-tts](https://github.com/rany2/edge-tts) if installed (free neural voices, needs internet), else macOS `say` (offline, robotic). Force one with `TTS_ENGINE=glm|edge|say`.

### Run the pipeline by hand (without Claude)

```bash
bash skills/edu-math-video/scripts/new_video.sh "$PWD" my_problem   # scaffold from template/
bash skills/edu-math-video/scripts/setup_check.sh my_problem        # must print ALL OK
cd my_problem
python3 build_audio.py --check                                      # script + pronunciation lint (free)
python3 build_audio.py --preview && node render.mjs motion && node render.mjs stills auto
python3 build_audio.py && node render.mjs video 6                   # real TTS, then render (6 = parallel pages)
```

## Skill: edu-physics-video

![edu-physics-video demo](edu-physics-video.jpg)

Turns one physics problem (mechanics, optics, electromagnetism…) into a **16:9 1920×1080 explainer MP4**: Chinese voice-over (Zhipu **GLM-TTS**), bilingual zh + en subtitles (`.srt` too), and blueprint-style canvas animation driven by the narration timeline. Input is a problem screenshot or plain text. Same pipeline as edu-math-video; what changes is the solving method and the picture.

**The picture follows the physics**: model the object, split the motion into segments, draw the forces, pick a law, solve, then check. Force arrows grow from the point of application on one scale, the object moves on the analytic solution `x(t)` through a linear `simT()` map, the v–t graph grows in sync, and friction reverses when the relative motion does. Timed by `S.at(k, f)`.

**Pipeline** (one folder per video, created in the user's current directory):

```
script.json ──build_audio.py──► timeline.json + mix.wav + <name>.srt   (GLM-TTS + synthesized music)
anim.js + phys.js + engine.js ──node render.mjs video──► <name>.mp4    (Playwright + ffmpeg, 30 fps)
```

**Guard rails**: the first scene shows the original problem with each condition boxed as it is read; `tts` text must be speakable Chinese (units read aloud; no digits or math symbols; θ is 西塔); polyphones are pinned and `--check` must report 0 before any paid TTS call; a free `--preview` plus a contact-sheet review comes before real audio; `--asr` transcribes the audio back to catch misread letters. Shared physics props go in `phys.js`. Leave `engine.js` unchanged.

**Trigger words**: physics explainer video, force diagram, Newton's laws, incline, projectile, circular motion, energy, momentum, refraction; 物理题视频、受力分析、牛顿定律、斜面、平抛、圆周、能量、动量、折射 etc.

### Dependency

Same as edu-math-video: Python 3 with `numpy requests pypinyin pillow`, Node.js 18+ with `playwright` + `ffmpeg-static`, and a Zhipu **`GLM_API_KEY`** in `~/.config/math-problem-video/.env` (shared by all three video skills). No key → `TTS_ENGINE=auto` falls back to [edge-tts](https://github.com/rany2/edge-tts), then macOS `say`.

### Run the pipeline by hand (without Claude)

```bash
bash skills/edu-physics-video/scripts/new_video.sh "$PWD" my_problem
bash skills/edu-physics-video/scripts/setup_check.sh my_problem        # must print ALL OK
cd my_problem
python3 build_audio.py --check
python3 build_audio.py --preview && node render.mjs motion && node render.mjs stills auto
python3 build_audio.py && node render.mjs video 6
```

## Skill: edu-chem-video

![edu-chem-video demo](edu-chem-video.jpg)

Turns one chemistry problem (redox balancing and the double-line bridge, amount of substance, equilibrium and the ICE table, ionic reactions, electrochemistry, titration, industrial processes…) into a **16:9 1920×1080 explainer MP4** with the same voice-over and bilingual subtitles, drawn on a **green chalkboard**. The balanced equation stays pinned in a strip at the top; the demo sits on the left and the slate on the right.

**The equation does the explaining, and conservation is counted on screen**: oxidation numbers rise and fall on a number line, electrons group until the counts match, coefficients fly from the electron row into the equation, atom tallies check off, the double-line bridge shows electron flow, molecule boxes react in the coefficient ratio, and the ICE table fills row by row. `scripts/chem_check.py` checks the balance and atom / charge conservation before any drawing. In `tts`, formulas become names (`HNO3` → 硝酸, `SO4^{2-}` → 硫酸根离子); the `zh` subtitle keeps the formula and renders subscripts.

**Pipeline**: same shape as above, with `chem.js` next to `engine.js` (`equation`, `valence`, `bridge`, `eFlow`, `tally`, `molMap`, `iceTable`, `molecule`, `beaker`, `graph`).

**Guard rails**: the same TTS, preview, and `--asr` rules as the other video skills, and `chem_check.py check` must exit 0. Oxidation states, coefficients, bridge endpoints, and molecule counts match the solution card. Lost electrons / oxidation are blue; gained electrons / reduction are red. Shared chemistry props go in `chem.js`. Leave `engine.js` unchanged.

**Trigger words**: chemistry explainer video, redox, electron conservation, double-line bridge, amount of substance, chemical equilibrium, ICE table, titration; 化学题视频、氧化还原配平、双线桥、电子守恒、物质的量、化学平衡、三段式、滴定 etc.

### Dependency

Same as edu-math-video (shared `GLM_API_KEY` and the same fallback). `scripts/chem_check.py` needs no extra packages — it checks coefficients, atom / charge conservation, and molar mass.

### Run the pipeline by hand (without Claude)

```bash
bash skills/edu-chem-video/scripts/new_video.sh "$PWD" my_problem
bash skills/edu-chem-video/scripts/setup_check.sh my_problem           # must print ALL OK
cd my_problem
python3 build_audio.py --check
python3 build_audio.py --preview && node render.mjs motion && node render.mjs stills auto
python3 build_audio.py && node render.mjs video 6
```

## Skill: edu-motion-problems

Solves one primary-school motion problem (pursuit / meeting / circular track) into a self-contained, zero-dependency interactive lesson page: the problem statement, a road / circular-track animation, an s–t graph, a time slider that drives live recomputation, dynamic readouts, a three-state status bar, and step-by-step narration. Built on native Canvas 2D — no KaTeX / Three.js / CDN — so it works fully offline and embeds directly in a mini-program web-view.

**Problem types covered**: pursuit (same direction), meeting (opposite direction), circular-track pursuit, circular-track meeting. One unified physical model — `kind ∈ {linear, circular} × direction ∈ {same, opposite}` — with an "unfolded arc-length" s–t graph so the same renderer serves all four.

**Answer-first sampling**: the meet time, meeting point and lap count are always integers, sampled with the stdlib `random` / `math` only — no sympy / CAS.

**Trigger words**: motion problems, pursuit, catch-up, meeting, circular track, primary math; 行程问题、追及问题、相遇问题、环形跑道 etc.

### Dependency

None — any Python 3; the generated page makes zero network requests.

### Generate from the command line (without Claude)

```bash
cd skills/edu-motion-problems
python3 scripts/generate.py list
python3 scripts/generate.py pursue 42 ./pursue.html
python3 scripts/generate.py all ./out_dir   # every type, 2 random variants each
```

## Skill: edu-primary-applied

The general entry point for primary-school applied (word) problems — **62 types**: pursuit / meeting / circular track, sum-difference / sum-multiple / difference-multiple, profit-loss, age, average, chicken-rabbit, planting, work-rate, cycle, unit rate / aggregate, boat-current, train-bridge, average speed, fractions, percentages, ratio & proportion, map scale, concentration, discount, restore, average-move, stairs / sawing / clock-chime, cow-grazing, pigeonhole, elimination, arithmetic sequence, boat-charter optimization, page-digit, three-number sum/difference/multiple, phalanx, clock angle, Venn (draggable circles), permutations & matchings, logic-table, pancake, Tian Ji horse-racing, interest, balance-equation, and 8 geometry types (equal-base triangle/parallelogram, trapezoid, recomposition, circle circumference/area, semicircle). Each becomes a self-contained, zero-dependency interactive page.

**Dispatch-table renderer**: `STATE[type]` / `DRAW[scene.kind]` / `DIAGRAM[diagram.kind]` plus a cached dynamic-variable `evalExpr`. Adding a new type = a generator + build + steps + one `STATE` entry; renderers are reused by family (road / circular / bar-model / interval / progress / sequence / train / swap / venn / link-graph / logic-table / timeline / matchup / balance / geodrag / circle / phalanx / clock).

**Answer-first sampling**: every answer is an integer (stdlib only).

**Trigger words**: primary applied problem, sum and difference, chicken and rabbit, work rate, fraction, percentage, ratio, concentration, discount, age, average, planting, pursuit, meeting, circular track; 小学应用题、和差、和倍、差倍、鸡兔同笼、工程、分数、百分数、比与比例、浓度、折扣 etc.

### Dependency

None — any Python 3; the generated page makes zero network requests.

### Generate from the command line (without Claude)

```bash
cd skills/edu-primary-applied
python3 scripts/generate.py list
python3 scripts/generate.py sum-diff 42 ./sum-diff.html
python3 scripts/generate.py all ./out_dir
```

## Skill: edu-primary-geometry

Solves one primary-school "shape & measure" problem — **9 types**: area derivation (parallelogram / triangle / trapezoid / circle), composite-shape area, irregular-shape grid estimation, three views, translation / rotation / symmetry, cuboid volume / surface area — into a self-contained, zero-dependency interactive page with a **draggable canvas** (vertices snap to an integer grid or slide along a constraint line; a stage slider steps the "cut → move → paste" animation).

**Draggable geometry**: a shared drag layer (`geomTransform` world coordinates + pointer hit-testing + `applySnap`) powers cut-rearrange derivations, grid-split, solid views and transform symmetry. The "cut → move → paste" stage is the slider.

**Answer-first sampling**: base / height / area / volume are always integers (stdlib only).

**Trigger words**: geometry, area, parallelogram, triangle, trapezoid, circle, composite shape, three views, symmetry, cuboid volume; 小学几何、面积、平行四边形、三角形、梯形、圆、组合图形、三视图、平移旋转、轴对称、表面积、体积 etc.

### Dependency

None — any Python 3; the generated page makes zero network requests.

### Generate from the command line (without Claude)

```bash
cd skills/edu-primary-geometry
python3 scripts/generate.py list
python3 scripts/generate.py area-parallelogram 42 ./parallelogram.html
python3 scripts/generate.py all ./out_dir
```

## Skill: edu-statistics

Solves one primary-school "statistics & probability" problem — **2 types**: bar-chart completion (drag a bar top to fill in the missing value) and probability tree diagrams (drag a handle along a number line to count leaves) — into a self-contained, zero-dependency interactive page with a draggable chart.

**Dispatch-table renderer** with the shared drag layer from edu-primary-geometry (`geomTransform` + `applySnap` + `dragAxis` for vertical/horizontal snapping). Statistics and probability quantities are always integers (stdlib only).

**Trigger words**: statistics, bar chart, line chart, pie chart, probability, tree diagram; 小学统计、统计图、条形统计图、折线统计图、扇形统计图、可能性、概率、树状图、枚举 etc.

### Dependency

None — any Python 3; the generated page makes zero network requests.

### Generate from the command line (without Claude)

```bash
cd skills/edu-statistics
python3 scripts/generate.py list
python3 scripts/generate.py stat-chart 42 ./stat-chart.html
python3 scripts/generate.py all ./out_dir
```

## How it works

The elementary skills (edu-motion-problems, edu-primary-applied, edu-primary-geometry, edu-statistics) run a lighter pipeline — no sympy: **answer-first good-number sampling** (stdlib `random` / `math`) feeds a **dispatch-table renderer** (`STATE[type]` / `DRAW[scene.kind]` / `DIAGRAM[diagram.kind]`) into a zero-dependency native Canvas 2D template. The secondary skills below use exact sympy kernels.

1. **Get a problem spec** — normalize all three entry points into a structured description (body type and dimensions, given conditions, the quantity asked, language).
2. **Exact kernel computation** — sympy computes exact coordinates, key vectors, normals, the final answer, and every intermediate value (as LaTeX strings). Never by hand.
3. **Assemble and inject the template** — feed the `lesson` / `steps` / `model` data into the data-driven template `template/lesson.html`; 3D vertex coordinates come from `kernel.to_three(...)`, sharing the same source as the solution.
4. **Self-check** — kernel answer == answer card == final value shown in the last step; a local static server + preview check confirms no console errors and correct formula/highlight rendering.
5. **Deliver** — the finished page is written to the user's current working directory, named like `solution-<short-description>.html`.

## Project structure

```
edulab/
├── .claude-plugin/
│   ├── plugin.json              # plugin metadata
│   └── marketplace.json         # marketplace manifest
├── index.html                   # finished sample (quad pyramid · line-plane angle)
└── skills/
    ├── edu-solid-geometry/      # solid geometry — 3D (Three.js) + MathJax
    │   ├── SKILL.md
    │   ├── template/lesson.html # data-driven template (generic 3D renderer + data island)
    │   ├── lib/
    │   │   ├── geometry_kernel.py  # sympy exact-computation core
    │   │   └── bodies.py           # edge-topology library for solids
    │   ├── scripts/generate.py
    │   ├── output/
    │   └── references/          # problem-schema.md · conventions.md
    ├── edu-analytic-geometry/   # analytic geometry / conics — 2D (Canvas) + KaTeX
    │   ├── SKILL.md
    │   ├── template/board.html  # data-driven template (generic 2D renderer + param engine)
    │   ├── lib/
    │   │   ├── analytic_kernel.py  # sympy exact-solver core (system · Vieta · range · fixed value)
    │   │   └── conics.py           # conic-section definition library
    │   ├── scripts/generate.py
    │   ├── output/
    │   └── references/          # problem-schema.md · conventions.md
    ├── edu-chem-reaction/       # chemistry reactions — 3D (Three.js) + KaTeX
    │   ├── SKILL.md
    │   ├── template/reaction.html # data-driven template (unified renderer + dual engine + data island)
    │   ├── lib/
    │   │   ├── reaction_kernel.py  # sympy balancing + conservation/atom-map check + bond-diff + assembly
    │   │   └── molecules.py        # VSEPR molecule-geometry library
    │   ├── scripts/generate.py
    │   ├── output/
    │   └── references/          # problem-schema.md · conventions.md
    ├── edu-math-video/          # math explainer videos — GLM-TTS + canvas animation → MP4
    │   ├── SKILL.md
    │   ├── template/            # runnable sample project (engine.js · anim.js · build_audio.py · render.mjs)
    │   ├── shared/              # pron.py + pron.json — shared pronunciation lexicon
    │   ├── scripts/             # new_video.sh · setup_check.sh · problem image & contact-sheet tools
    │   ├── examples/cone-parallel/  # solid-geometry example (camera tween · cone unrolling)
    │   └── reference/           # TTS setup · script writing · pronunciation · visual design · animation API
    ├── edu-physics-video/       # physics explainer videos — GLM-TTS + blueprint canvas → MP4
    │   ├── SKILL.md
    │   ├── template/            # blueprint theme (engine.js · phys.js · anim.js)
    │   ├── shared/
    │   ├── scripts/
    │   ├── examples/laser-curvature/  # geometric-optics example
    │   └── reference/
    ├── edu-chem-video/          # chemistry explainer videos — GLM-TTS + chalkboard canvas → MP4
    │   ├── SKILL.md
    │   ├── template/            # chalkboard theme (engine.js · chem.js · anim.js)
    │   ├── shared/
    │   ├── scripts/             # plus chem_check.py — balance and conservation check
    │   ├── examples/equilibrium/    # ICE-table / equilibrium example
    │   └── reference/
    ├── edu-motion-problems/     # primary motion problems (pursuit / meeting / circular) — zero-dep Canvas 2D
    │   ├── SKILL.md
    │   ├── template/board.html  # data-driven template (road / circular + s-t graph + motionState(t))
    │   ├── lib/                 # good_numbers.py · builders.py · steps.py
    │   ├── scripts/generate.py
    │   ├── tests/
    │   └── references/
    ├── edu-primary-applied/     # primary word problems (62 types) — dispatch-table renderer, zero-dep Canvas 2D
    │   ├── SKILL.md
    │   ├── template/board.html  # data-driven template (STATE/DRAW/DIAGRAM dispatch + evalExpr)
    │   ├── lib/                 # generators.py · builders.py · steps.py
    │   ├── scripts/generate.py
    │   ├── tests/ · verify.mjs
    │   └── references/
    ├── edu-primary-geometry/    # primary shape & measure (9 types) — draggable canvas, zero-dep Canvas 2D
    │   ├── SKILL.md
    │   ├── template/board.html  # data-driven template (STATE/DRAW dispatch + geomTransform drag layer)
    │   ├── lib/                 # generators.py · builders.py · steps.py
    │   ├── scripts/generate.py
    │   ├── tests/ · verify.mjs
    │   └── references/
    └── edu-statistics/          # primary statistics & probability (2 types) — draggable chart, zero-dep Canvas 2D
        ├── SKILL.md
        ├── template/board.html  # data-driven template (STATE/DRAW dispatch + dragAxis drag layer)
        ├── lib/                 # generators.py · builders.py · steps.py
        ├── scripts/generate.py
        ├── tests/ · verify.mjs
        └── references/
```

## Extending

**edu-solid-geometry**
- **Add a problem type**: add a solver function in `geometry_kernel.py` (see the recipe table in `references/conventions.md`), then add a `build_*` in `generate.py`.
- **Add a solid**: add a coordinate-construction function in `geometry_kernel.py`, then add its edge topology in `bodies.py`.

**edu-analytic-geometry**
- **Add a problem type**: add a target-quantity function in `analytic_kernel.py` and reuse `range_over_m` / `is_constant_in_m`, then add a `build_*` in `generate.py` (pick an interaction: range bar / fixed value / fixed point / locus trace).
- **Add a curve**: ellipse / hyperbola / parabola / circle are built in; new curves go in `conics.py` and the `board.html` engine.

**edu-chem-reaction**
- **Add a reaction**: add a `build_*` in `generate.py` (high-level `species + atom_map`, or low-level `atoms + fragments` for mechanisms) and register it in `REGISTRY`.
- **Add a molecule / ion**: add an entry in `lib/molecules.py` (VSEPR geometry + display metadata + internal bonds).

**edu-math-video**
- **New problem**: never edit `engine.js`; write the per-problem `script.json` / `storyboard.md` / `anim.js`, and add new figure helpers inside `anim.js`.
- **Fix a reading**: add the word to `shared/pron.json` (`words` / `ok`) — one lexicon shared by every video.

**edu-physics-video**
- **New problem**: leave `engine.js` unchanged; write the per-problem `script.json` / `storyboard.md` / `anim.js`. Shared physics props go in `phys.js`.
- **Fix a reading**: add the word to `shared/pron.json`.

**edu-chem-video**
- **New problem**: leave `engine.js` unchanged; write the per-problem files. Shared chemistry props go in `chem.js`. Run `scripts/chem_check.py` on the equation before drawing.
- **Fix a reading**: add the word to `shared/pron.json`.

**Elementary skills (edu-motion-problems · edu-primary-applied · edu-primary-geometry · edu-statistics)**
- **Add a problem type**: write an answer-first `gen_*` in `lib/generators.py` (or `lib/good_numbers.py` for edu-motion-problems), a `build_*` in `lib/builders.py`, step text in `lib/steps.py`, register it in `scripts/generate.py`'s `REGISTRY`, and add a `STATE[type]` dispatch entry. If the type's `scene.kind` falls in an existing renderer family, the front-end needs no changes; a new family adds one `DRAW` renderer in `template/board.html`.
- **One shared recipe** across all four: "answer-first good-number sampling + dispatch-table renderer + zero-dependency native Canvas 2D" — see each skill's `references/conventions.md` §7.

## License

[Apache-2.0](LICENSE)

## Author

WY · [@akokoi1](https://x.com/akokoi1)

| WeChat | Xiaohongshu |
|---|---|
| <a href="http://weixin.qq.com/r/mp/kUwUDP3EZKAbrblv9xmD"><img src="qr-wechat.png" alt="WeChat official account" width="220"></a> | <a href="http://xhslink.com/m/64K17dDQNvj"><img src="qr-xiaohongshu.png" alt="Xiaohongshu" width="220"></a> |

## Star History

<a href="https://www.star-history.com/?repos=wy51ai%2Fedulab&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&legend=top-left" />
 </picture>
</a>
