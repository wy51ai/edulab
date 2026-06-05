---
name: edu-signals-control
description: >-
  Turn introductory signals/control-system feedback problems into
  self-contained interactive lesson pages. Use for single-loop negative
  feedback, closed-loop transfer functions, high loop-gain limits, Bode-style
  samples, and Chinese 信号与系统 / 自动控制 requests such as 反馈框图、闭环传递函数、
  传递函数、拉普拉斯域、k趋于无穷、运放负反馈.
---

# 信号与控制反馈题 -> 交互网页

## What This Skill Produces

A browser-openable HTML lesson page: problem statement, exact answer, MathJax
steps, a feedback block diagram, a loop-gain slider, and sampled frequency
response curves. The current first-release slice covers:

- 单环负反馈 / single-loop negative feedback.
- 闭环传递函数 / closed-loop transfer function:
  `H(s)=G(s)/(1+G(s)B(s))`.
- 高环路增益极限 / high loop-gain limit, especially `k -> infinity`.
- 一阶反馈网络 examples such as `F(s)=1/(tau*s+1)`.

Do not promise arbitrary block-diagram reduction, MIMO systems, nonlinear
systems, root-locus design, controller tuning, stability proof automation, OCR
parsing, or "solve any control-system problem". If the problem is outside the
single-loop contract, explain the nearest supported form before approximating.

## Dependency

The compute core `lib/control_kernel.py` depends on `sympy`. Before running:

```bash
python3 -c "import sympy"
```

If a dependency is missing, ask before installing it. Use a Python interpreter
that can import SymPy.

## Workflow

1. Normalize the problem into a spec. See `references/problem-schema.md`.
2. Use `lib/control_kernel.py` for exact symbolic computation. Do not
   hand-calculate final transfer functions.
3. Build lesson data with `scripts/generate.py` or a small custom builder.
4. Render HTML with `render_html(data, out)`. Write output to the user's current
   working directory unless they specified another path.
5. Verify the answer appears in both `lesson.answerValue` and the final step,
   then preview the HTML when practical.

## CLI Examples

From the repository root or any user working directory:

```bash
python3 skills/edu-signals-control/scripts/generate.py feedback-limit ./feedback-limit.html
python3 skills/edu-signals-control/scripts/generate.py first-order-feedback ./first-order-feedback.html
python3 skills/edu-signals-control/scripts/generate.py random 7 ./signals-control-random.html
python3 skills/edu-signals-control/lib/control_kernel.py
```

If no output path is provided, the script writes `<mode>.html` to the current
working directory.

## Correctness Rules

- SymPy is the source of truth for exact transfer functions and limits.
- JavaScript may draw precomputed samples, but must not recompute final answers.
- The negative-feedback sign convention is explicit: denominator `1+G(s)B(s)`.
- The answer card and final step must include the kernel answer.
- Generated output belongs in the user's cwd or explicit output path, not in the
  skill directory.

## Files

- `lib/control_kernel.py` - exact transfer-function computation and samples.
- `scripts/generate.py` - data builders, CLI, and template injection.
- `template/lesson.html` - standalone lesson UI.
- `references/problem-schema.md` - supported problem/data contract.
- `references/conventions.md` - formulas, sign conventions, and self-checks.
