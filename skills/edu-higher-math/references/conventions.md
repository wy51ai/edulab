# edu-higher-math Conventions

## Exactness

- Use SymPy for all final answers.
- Use `sympy.latex(sympy.simplify(expr))` for displayed formulas.
- Numeric samples are for visualization only and must derive from the same symbolic expression.
- Reject or clarify problems that leave undeclared parameters or produce non-finite samples.

## Double Integrals

Cartesian rectangle:

```text
int_{x=a}^{b} int_{y=c}^{d} f(x,y) dy dx
```

Polar:

```text
int_{theta=a}^{b} int_{r=c}^{d} f(r,theta) * r dr dtheta
```

Always call out the Jacobian in teaching steps.

## Surface Flux

Parametric surface:

```text
r(u,v) = (x(u,v), y(u,v), z(u,v))
n dS = r_u x r_v du dv
flux = int int F(r(u,v)) dot (r_u x r_v) du dv
```

This first release follows the induced orientation. Do not silently change sign
for "upward", "outward", or "downward" unless the builder explicitly encodes that
orientation and explains it.

## ODE

First-order IVP:

```text
dy/dx = f(x,y), y(x0)=y0
```

Use `sympy.dsolve` with `ics` for exact solutions. The slope field samples
`f(x,y)` on a grid; the solution curve samples the exact solution.

## Self-Checks

- Kernel expected value equals known regression cases.
- `lesson.answerValue` contains `_answer`.
- Last step contains `_answer`.
- HTML payload does not leave `__LESSON_DATA__`.
- No `NaN` or `Infinity` appears in visualization samples.
