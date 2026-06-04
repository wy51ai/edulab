# edulab

[简体中文](README.zh-CN.md) · **English**

A collection of education skills that turn academic problems into **interactive lesson web pages**.

edulab is a [Claude Code](https://claude.com/claude-code) plugin (plugin + marketplace). The goal: give it a problem, get back a single self-contained HTML page you can open in any browser — complete with a worked explanation and a visualization, turning "I read it" into "I can rotate it and actually see it."

The first skill, **edu-solid-geometry**, solves solid geometry problems using the "coordinate system + vector method," driven by exact [sympy](https://www.sympy.org) computation. It outputs a lesson page with step-by-step analysis (MathJax) on the left and an interactive 3D model (Three.js) on the right.

## Preview

[index.html](index.html) in the project root is a finished sample (regular quadrilateral pyramid · line-plane angle). Open it directly in a browser:

- **Left**: problem statement / answer / step-by-step analysis, formulas rendered with MathJax
- **Right**: the matching 3D model — rotate and zoom, with key elements highlighted per step and the camera moving along
- The answer, the 3D coordinates, and every intermediate value are **consistent at the source** (all derived from one sympy computation)

More samples live in [skills/edu-solid-geometry/output/](skills/edu-solid-geometry/output/) (cube / box, etc.).

## Install

**Recommended** — install with [skills](https://github.com/vercel-labs/skills) in one command:

```bash
npx skills add wy51ai/edulab
```

Or use it as a Claude Code plugin marketplace:

```
/plugin marketplace add wy51ai/edulab
/plugin install edulab
```

Once installed, the skill activates on its trigger words, and other agents can also invoke it to generate these pages.

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

## How it works

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
    └── edu-solid-geometry/
        ├── SKILL.md             # skill description and workflow
        ├── template/lesson.html # data-driven template (generic 3D renderer + data island)
        ├── lib/
        │   ├── geometry_kernel.py  # sympy exact-computation core
        │   └── bodies.py           # edge-topology library for solids
        ├── scripts/generate.py  # template injection + example builders
        ├── output/              # internal development samples
        └── references/
            ├── problem-schema.md   # data format
            └── conventions.md      # coordinate conventions, solution recipes, self-check
```

## Extending

- **Add a problem type**: add a solver function in `geometry_kernel.py` (see the recipe table in `references/conventions.md`), then add a `build_*` in `generate.py`.
- **Add a solid**: add a coordinate-construction function in `geometry_kernel.py`, then add its edge topology in `bodies.py`.

## License

[MIT](LICENSE)

## Author

WY · [@akokoi1](https://x.com/akokoi1)

Stars, issues, and PRs are welcome.
