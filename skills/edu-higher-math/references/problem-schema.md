# edu-higher-math Problem Schema

All entry points should be normalized into a small explicit spec before solving.
The first release supports these topics.

## Cartesian Double Integral

```jsonc
{
  "language": "zh-CN",
  "topic": "double_integral",
  "coordinates": "cartesian",
  "integrand": "x + y",
  "x_bounds": ["0", "1"],
  "y_bounds": ["0", "2"]
}
```

The kernel computes:

```text
int_{x=a}^{b} int_{y=c}^{d} f(x,y) dy dx
```

## Polar Double Integral

```jsonc
{
  "language": "zh-CN",
  "topic": "double_integral",
  "coordinates": "polar",
  "integrand": "1",
  "r_bounds": ["0", "1"],
  "theta_bounds": ["0", "2*pi"]
}
```

The kernel multiplies the integrand by the Jacobian `r`.

## Surface Flux

```jsonc
{
  "language": "zh-CN",
  "topic": "surface_flux",
  "vector_field": ["x", "y", "z"],
  "parametrization": ["u", "v", "1"],
  "u_bounds": ["0", "1"],
  "v_bounds": ["0", "1"]
}
```

The orientation is the one induced by `r_u x r_v`. Reverse the parameter order
or negate the normal in a later builder if a problem explicitly asks for the
opposite orientation.

## First-Order ODE IVP

```jsonc
{
  "language": "zh-CN",
  "topic": "ode",
  "rhs": "y",
  "initial": ["0", "1"],
  "sample_bounds": ["-1", "1"]
}
```

This means `dy/dx = rhs(x,y)` with `y(x0)=y0`.

## Lesson Data

Rendered HTML receives:

```jsonc
{
  "lesson": {
    "language": "zh-CN",
    "meta": "高等数学 · 二重积分",
    "title": "题面",
    "answerLabel": "答案说明",
    "answerValue": "$3$",
    "ui": {}
  },
  "steps": [
    {
      "title": "步骤标题",
      "content": "<p>MathJax HTML</p>",
      "highlight": ["domain", "answer"]
    }
  ],
  "visual": {
    "type": "double_integral | polar_integral | surface_flux | ode_slope_field",
    "layers": [{ "id": "domain", "label": "积分区域" }],
    "samples": {}
  }
}
```

Builders may keep an internal `_answer` key before rendering. The renderer strips
it from the HTML payload.
