# edulab

[简体中文](README.zh-CN.md) · **English**

A collection of education skills that turn academic problems into **interactive lesson web pages**.

edulab is a [Claude Code](https://claude.com/claude-code) plugin (plugin + marketplace). The goal: give it a problem, get back a single self-contained HTML page you can open in any browser — complete with a worked explanation and a visualization, turning "I read it" into "I can rotate it and actually see it."

The original skill, **edu-solid-geometry**, solves solid geometry problems using the "coordinate system + vector method," driven by exact [sympy](https://www.sympy.org) computation. It outputs a lesson page with step-by-step analysis (MathJax) on the left and an interactive 3D model (Three.js) on the right.

The newer **edu-higher-math** skill extends the same exact-computation pattern to higher mathematics: double integrals, polar integrals, surface flux, and first-order differential equations. It outputs a MathJax lesson with SVG-based interactive domain, surface, and slope-field visualizations.

The **edu-signals-control** skill adds the same pattern for introductory signals and control-system feedback problems: single-loop negative feedback, closed-loop transfer functions, and high loop-gain limits such as `H(s)=kA/(1+kAF(s)) -> 1/F(s)`.

## Preview

![edulab demo — line-plane angle lesson page](demo1.png)

[index.html](index.html) in the project root is a finished sample (regular quadrilateral pyramid · line-plane angle). Open it directly in a browser:

- **Left**: problem statement / answer / step-by-step analysis, formulas rendered with MathJax
- **Right**: the matching 3D model — rotate and zoom, with key elements highlighted per step and the camera moving along
- The answer, the 3D coordinates, and every intermediate value are **consistent at the source** (all derived from one sympy computation)

You can generate more samples with the CLI commands below.

## Install

**Recommended** — install with [skills](https://github.com/vercel-labs/skills) in one command:

```bash
npx skills add wy51ai/edulab
```

To update to the latest version later:

```bash
npx skills update
```

Or use it as a Claude Code plugin marketplace:

```
/plugin marketplace add wy51ai/edulab
/plugin install edulab
```

Once installed, the skill activates on its trigger words, and other agents can also invoke it to generate these pages.

## Skills

| Skill | Focus | Visualization |
|---|---|---|
| `edu-solid-geometry` | Solid geometry with coordinate/vector methods | Three.js 3D model with step highlights |
| `edu-higher-math` | Double integrals, surface flux, first-order ODEs | SVG domain diagrams, surface/field sketches, slope fields |
| `edu-signals-control` | Negative-feedback transfer functions and high loop-gain limits | SVG feedback block diagram, loop-gain slider, Bode-style samples |

## Skill: edu-solid-geometry

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

## Skill: edu-higher-math

Turns a higher-mathematics problem into a self-contained interactive lesson page. Current first-release coverage:

| Topic | What is solved exactly | Visual |
|---|---|---|
| Double integral | Cartesian rectangle examples and polar examples with Jacobian | Region samples and accumulated result |
| Surface flux | Parametric surface flux via `F(r(u,v)) · (r_u x r_v)` | Surface mesh with field and normal arrows |
| First-order ODE | Initial-value problems solved by SymPy `dsolve` | Slope field plus exact solution curve |

**Trigger words**: higher math, calculus, double integral, polar integral, surface integral, flux, differential equation, ODE, slope field; 高等数学、二重积分、极坐标积分、曲面积分、通量、微分方程、斜率场、解这道高数题, etc.

### Generate from the command line

```bash
cd skills/edu-higher-math
python3 scripts/generate.py double-integral ./double-integral.html
python3 scripts/generate.py polar-integral ./polar-integral.html
python3 scripts/generate.py surface-flux ./surface-flux.html
python3 scripts/generate.py ode ./ode.html
python3 scripts/generate.py random 7 ./higher-math-random.html
python3 lib/calculus_kernel.py
```

This first release deliberately does not claim arbitrary OCR parsing, every calculus topic, PDEs, closed-surface theorem selection, or "solve any ODE" coverage.

## Skill: edu-signals-control

Turns a signals/control-system feedback problem into a self-contained interactive lesson page. Current first-release coverage:

| Topic | What is solved exactly | Visual |
|---|---|---|
| Single-loop negative feedback | `H(s)=G(s)/(1+G(s)B(s))` | Feedback block diagram with highlighted signal paths |
| High loop-gain limit | Symbolic limit such as `k -> infinity` | Loop-gain slider showing the shrinking `1/(kA)` term |
| First-order feedback network | Examples such as `F(s)=1/(tau*s+1)` | Bode-style magnitude samples for closed-loop vs high-gain response |

**Trigger words**: signals and systems, control systems, feedback block diagram, closed-loop transfer function, high loop gain, Bode sample, Laplace transfer function; 信号与系统、自动控制、反馈框图、闭环传递函数、传递函数、拉普拉斯域、k趋于无穷、运放负反馈, etc.

### Generate from the command line

```bash
cd skills/edu-signals-control
python3 scripts/generate.py feedback-limit ./feedback-limit.html
python3 scripts/generate.py first-order-feedback ./first-order-feedback.html
python3 scripts/generate.py random 7 ./signals-control-random.html
python3 lib/control_kernel.py
```

This first release deliberately does not claim arbitrary block-diagram reduction, MIMO systems, nonlinear systems, root-locus design, controller tuning, or stability proof automation.

## How it works

1. **Get a problem spec** — normalize text/image/random entry points into structured data with topic, givens, query, and language.
2. **Exact kernel computation** — SymPy computes exact coordinates, vectors, integrals, flux values, ODE solutions, transfer functions, or feedback limits. Never by hand.
3. **Assemble and inject the template** — feed `lesson` / `steps` / `model` or `visual` data into the skill's HTML template. Visual samples come from the same symbolic source as the answer.
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
    ├── edu-solid-geometry/
    │   ├── SKILL.md             # skill description and workflow
    │   ├── template/lesson.html # data-driven template (generic 3D renderer + data island)
    │   ├── lib/
    │   │   ├── geometry_kernel.py  # sympy exact-computation core
    │   │   └── bodies.py           # edge-topology library for solids
    │   ├── scripts/generate.py  # template injection + example builders
    │   └── references/
    │       ├── problem-schema.md   # data format
    │       └── conventions.md      # coordinate conventions, solution recipes, self-check
    ├── edu-higher-math/
        ├── SKILL.md
        ├── template/lesson.html
        ├── lib/calculus_kernel.py
        ├── scripts/generate.py
        └── references/
            ├── problem-schema.md
            └── conventions.md
    └── edu-signals-control/
        ├── SKILL.md
        ├── template/lesson.html
        ├── lib/control_kernel.py
        ├── scripts/generate.py
        └── references/
            ├── problem-schema.md
            └── conventions.md
```

## Extending

- **Add a problem type**: add a solver function in `geometry_kernel.py` (see the recipe table in `references/conventions.md`), then add a `build_*` in `generate.py`.
- **Add a solid**: add a coordinate-construction function in `geometry_kernel.py`, then add its edge topology in `bodies.py`.
- **Add a higher-math topic**: add an exact solver and samples in `calculus_kernel.py`, then register a builder in `skills/edu-higher-math/scripts/generate.py`.
- **Add a signals/control topic**: add an exact transfer-function solver and samples in `control_kernel.py`, then register a builder in `skills/edu-signals-control/scripts/generate.py`.

## License

[Apache-2.0](LICENSE)

## Author

WY · [@akokoi1](https://x.com/akokoi1)

Stars, issues, and PRs are welcome.
