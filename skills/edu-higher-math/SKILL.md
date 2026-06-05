---
name: edu-higher-math
description: >-
  Turn higher-mathematics problems into self-contained interactive lesson pages.
  Use for double integrals, polar integrals, surface integrals, flux, first-order
  differential equations, slope fields, and Chinese 高等数学 requests such as
  二重积分、曲面积分、通量、微分方程、斜率场、解这道高数题.
---

# 高等数学解题 -> 交互网页

## What This Skill Produces

A browser-openable HTML lesson page: problem statement, exact answer, MathJax
steps, and an interactive visualization panel. The current implementation covers
three reliable vertical slices:

- 二重积分 / double integrals: rectangular Cartesian regions and polar unit-disk style examples.
- 曲面积分 / flux: parametric surface flux using `F(r(u,v)) · (r_u x r_v)`.
- 常微分方程 / ODE: first-order IVPs with slope-field and solution-curve visualization.

Do not promise arbitrary OCR parsing, every textbook problem shape, PDEs, or
"solve any ODE". If the problem is outside the supported contract, explain the
nearest supported form and ask before approximating.

## Dependency

The compute core `lib/calculus_kernel.py` depends on `sympy`. Before running:

```bash
python3 -c "import sympy"
```

If a dependency is missing, ask before installing it. Use a Python interpreter
that can import SymPy.

## Workflow

1. Normalize the problem into a spec. See `references/problem-schema.md`.
2. Use `lib/calculus_kernel.py` for exact symbolic computation. Do not hand-calculate final answers.
3. Build lesson data with `scripts/generate.py` or a short temporary builder.
4. Render HTML with `render_html(data, out)`. Write output to the user's current working directory unless they specified another path.
5. Verify the answer appears in both `lesson.answerValue` and the final step, then preview the HTML when practical.

## CLI Examples

From the repository root or any user working directory:

```bash
python3 skills/edu-higher-math/scripts/generate.py double-integral ./double-integral.html
python3 skills/edu-higher-math/scripts/generate.py polar-integral ./polar-integral.html
python3 skills/edu-higher-math/scripts/generate.py surface-flux ./surface-flux.html
python3 skills/edu-higher-math/scripts/generate.py ode ./ode.html
python3 skills/edu-higher-math/scripts/generate.py random 7 ./higher-math-random.html
```

If no output path is provided, the script writes `<mode>.html` to the current
working directory.

## Correctness Rules

- SymPy is the source of truth for exact answers and LaTeX strings.
- Visualization samples must come from the same symbolic expressions.
- JavaScript may draw samples, but it must not recompute exact answers.
- The answer card and final step must include the kernel answer.
- Generated output belongs in the user's cwd or explicit output path, not in the skill directory.

## Files

- `lib/calculus_kernel.py` - exact computation and deterministic samples.
- `scripts/generate.py` - data builders, CLI, and template injection.
- `template/lesson.html` - standalone lesson UI.
- `references/problem-schema.md` - supported problem/data contract.
- `references/conventions.md` - formulas, orientation rules, and self-checks.
