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

![edu-math-video demo](edu-math-video.png)

Turns math problems (geometry, algebra, functions, motion problems…) and supported biology mechanisms into **16:9 1920×1080 explainer MP4s**: Chinese narration, bilingual zh + en subtitles (`.srt` too), and Canvas animation driven by the narration timeline. Use GLM-TTS or a supported fallback, including free offline Windows Chinese speech. Input is a problem screenshot or plain text; the biology example also works as a concept lesson.

**The picture explains the step**: every narration line gets a "point → move → keep" action on the figure (equal segments slide onto each other, congruent triangles overlay, the 3D camera tweens to a top view, a cone unrolls into a sector…) — timed by `S.at(k, f)` (a fraction into line *k*), never by hard-coded seconds. A `motion` check flags static segments outside exempt scenes.

**Pipeline** (one folder per video, created in the user's current directory):

```
script.json ──build_audio.py──► timeline.json + mix.wav + <name>.srt   (GLM-TTS + synthesized music)
anim.js + engine.js ──node render.mjs video──► <name>.mp4              (Playwright + ffmpeg, 30 fps)
```

**Guard rails**: open with a visible question, then establish the original conditions before using them. `tts` text must be speakable Chinese (no digits / math symbols); polyphones are pinned (`长[cháng]`, shared `pron.json` lexicon) and `--check` must report 0 before any paid TTS call. Review a free `--preview` and contact sheet before real audio. Optional `--asr` uses online recognition and requires authorization to send the narration; offline lessons can skip it and report the verification scope.

**Trigger words**: math explainer video, biology explainer video, cell animation, walkthrough video, problem-solving video, micro-lesson; 讲解视频、解题视频、例题精讲、生物微课、细胞动画 etc. The skill name remains `edu-math-video`.

### Dependency

- Python 3 with `numpy requests pypinyin pillow`; Node.js 18+ with `playwright` + `ffmpeg-static` (installed once in the workspace — `scripts/new_video.sh` writes the `package.json`); Google Chrome or Playwright Chromium.
- Optional Zhipu **`GLM_API_KEY`**, provided by you, in `~/.config/math-problem-video/.env` (see `reference/glm-tts-setup.md`).
- **No key?** It falls back automatically (`TTS_ENGINE=auto`): [edge-tts](https://github.com/rany2/edge-tts) if installed (free neural voices, needs internet), else macOS `say` (offline, robotic). Windows with an installed Chinese desktop voice uses offline system speech before Edge. Force one with `TTS_ENGINE=glm|windows|edge|say`.

### Run the pipeline by hand (without Claude)

```bash
bash skills/edu-math-video/scripts/new_video.sh "$PWD" my_problem   # scaffold from template/
bash skills/edu-math-video/scripts/setup_check.sh my_problem        # must print ALL OK
cd my_problem
python3 build_audio.py --check                                      # script + pronunciation lint (free)
python3 build_audio.py --preview && node render.mjs motion && node render.mjs stills auto
python3 build_audio.py && node render.mjs video 6                   # real TTS, then render (6 = parallel pages)
```

### Video teaching upgrade (0.2.0)

- Optional `pause_after` gives students thinking time and retains the question in the video and SRT.
- Optional `theorem` records conditions, reasons and a conclusion; `--check` emits a reviewable teaching report. This is a structural check, not mathematical verification.
- Windows can use free offline Chinese desktop speech. PowerShell scaffolding and cross-platform environment checks are included.
- Motion measurements stay in the browser; direct canvas capture and linear-time audio smoothing reduce rendering and mixing overhead.
- The sample now checks theorem conditions and ends with a transfer exercise. Existing scripts keep their original timing.

See [teaching guidance](skills/edu-math-video/reference/teaching-quality.md). Windows: use the full skill path, `SKILL/scripts/new_video.ps1 -Workspace $PWD -Name my_problem`, then `python SKILL/scripts/setup_check.py my_problem`. Keep the user workspace as the working directory.

### Cell mechanism lessons (0.3.0)

![Mitophagy lesson preview](skills/edu-math-video/examples/mitophagy-cell/preview.png)

- A reusable [Canvas cell model](skills/edu-math-video/lib/biology-model.js) keeps the same cell, mitochondrion and lysosome as the camera moves from the whole cell to the local mechanism and back.
- The approximately one-minute [mitophagy-cell example](skills/edu-math-video/examples/mitophagy-cell/) opens with “How does a cell clear a damaged mitochondrion?”, animates wrapping, closure, fusion and internal degradation, then ends with a transfer question. Each narration line explains one visible change.
- Optional `episode.motion_regions` measures motion in the actual model area instead of assuming a left-side figure. Optional `music_level` is a number from `0` to `1`, defaults to `1`, and `0` disables background music while retaining narration and configured sound effects. Existing math projects keep their defaults.
- Review a 45–60 second sample before exporting a full lesson. Scientific diagrams and particle counts are teaching schematics, not experimental measurements; ROS content must not be relabelled as survival rate. The project does not promise views or learning gains.

Create an independent demo project in your lesson workspace (replace the paths):

```bash
python /path/to/edu-math-video/scripts/create_biology_demo.py --workspace /path/to/lessons --name cell-classroom-demo
cd /path/to/lessons/cell-classroom-demo
python build_audio.py --check
python build_audio.py --preview
node render.mjs motion
node render.mjs stills auto
# Review the images, then generate real narration and export:
python build_audio.py
node render.mjs video 6
```

See the [biology visual standards](skills/edu-math-video/reference/biology-visuals.md) for model differences, mechanism order and the visual/cause-and-effect review checklist. The model is a Canvas teaching cutaway, not a reconstructed specimen or an interactive classroom.


### Faster local generation (0.3.1)

Windows offline narration now shares one speech engine across multiple clips and avoids FFmpeg when the clip already has the required PCM format. Identical narration is synthesized once. Video export defaults to x264 `fast` at the existing 1080p, 30 fps and CRF 18 settings, and reuses a completed MP4 when local inputs and the output file still match their content hashes.

On one Windows machine, the same 60-second cell lesson took **93 → 71 seconds for cold narration plus export**; an unchanged repeat export took **0.74 seconds**. These measurements exclude writing the lesson and do not predict every machine's runtime. Use `node render.mjs video 4 --fresh --preset medium` to force a rebuild with the previous compression preset. See [performance details and cache limits](skills/edu-math-video/reference/performance.md), including how to update an existing lesson project.

## How it works

The interactive web lesson skills use the kernel/template workflow below. Videos use the narration and Canvas pipeline above.

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
    └── edu-math-video/          # math and biology explainer videos — narration + Canvas → MP4
        ├── SKILL.md
        ├── template/            # runnable sample project (engine.js · anim.js · build_audio.py · render.mjs)
        ├── shared/              # pron.py + pron.json — shared pronunciation lexicon
        ├── lib/biology-model.js # reusable cell cutaway and mechanism animation
        ├── scripts/             # scaffold · biology demo · environment & contact-sheet tools
        ├── examples/cone-parallel/  # solid-geometry example (camera tween · cone unrolling)
        ├── examples/mitophagy-cell/ # cell mechanism sample (continuous camera · internal degradation)
        └── reference/           # TTS setup · script writing · pronunciation · visual design · animation API
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
- **Biology lesson**: start with `create_biology_demo.py`, reuse `lib/biology-model.js`, and review structure, location, mechanism and evidence using `reference/biology-visuals.md`.
- **Fix a reading**: add the word to `shared/pron.json` (`words` / `ok`) — one lexicon shared by every video.

## License

[Apache-2.0](LICENSE)

## Author

WY · [@akokoi1](https://x.com/akokoi1)

## Star History

<a href="https://www.star-history.com/?repos=wy51ai%2Fedulab&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=wy51ai/edulab&type=date&legend=top-left" />
 </picture>
</a>

## Development checks

Use a Python environment containing `numpy requests pypinyin pillow`, then run `npm install`, `npx playwright install chromium` and `npm test`. On Windows ensure that environment's Python is first on PATH. Checks cover old timings, thinking pauses, theorem metadata, offline audition, FFmpeg discovery, native SAPI (Windows only), Canvas subtitle holds, motion-region configuration and music controls. Tests do not call online TTS or ASR. They supplement visual and scientific review.

CI recipe: copy `ci/math-video-tests.yml` into `.github/workflows/` with an account that has workflow-write permission.
