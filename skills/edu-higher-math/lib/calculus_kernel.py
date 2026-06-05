#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calculus_kernel.py - exact higher-mathematics computation core for edulab.

The kernel is the single source of truth for symbolic answers and numeric
visualization samples. Templates may draw samples, but must not recompute final
answers in JavaScript.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

import sympy as sp


x, y, z = sp.symbols("x y z")
r, theta = sp.symbols("r theta")
u, v = sp.symbols("u v")
Y = sp.Symbol("y")


def _locals(extra=None):
    base = {
        "x": x,
        "y": y,
        "z": z,
        "r": r,
        "theta": theta,
        "u": u,
        "v": v,
        "pi": sp.pi,
        "E": sp.E,
        "e": sp.E,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "sqrt": sp.sqrt,
        "exp": sp.exp,
        "log": sp.log,
        "abs": sp.Abs,
        "Abs": sp.Abs,
    }
    if extra:
        base.update(extra)
    return base


def expr(value, extra=None):
    """Parse a compact string/number into a SymPy expression."""
    return sp.sympify(value, locals=_locals(extra))


def tex(value) -> str:
    return sp.latex(sp.simplify(value))


def _bound_pair(bounds):
    if len(bounds) != 2:
        raise ValueError(f"Expected a two-item bound, got {bounds!r}")
    return expr(bounds[0]), expr(bounds[1])


def _float(value) -> float:
    val = float(sp.N(value, 12))
    if not math.isfinite(val):
        raise ValueError(f"Non-finite sample value: {value!r}")
    return val


def _linspace(a, b, count: int) -> list[sp.Expr]:
    a, b = expr(a), expr(b)
    if count <= 1:
        return [sp.simplify((a + b) / 2)]
    return [sp.simplify(a + (b - a) * sp.Rational(i, count - 1)) for i in range(count)]


def _numeric_points(points: Iterable[Sequence[sp.Expr]]) -> list[list[float]]:
    return [[_float(c) for c in point] for point in points]


def solve_cartesian_double_integral(integrand, x_bounds, y_bounds, sample_count=4):
    """Compute int_{x=a}^{b} int_{y=c}^{d} f(x,y) dy dx exactly."""
    f = expr(integrand)
    xa, xb = _bound_pair(x_bounds)
    ya, yb = _bound_pair(y_bounds)

    inner = sp.integrate(f, (y, ya, yb))
    exact = sp.simplify(sp.integrate(inner, (x, xa, xb)))

    xs = _linspace(xa, xb, sample_count)
    ys = _linspace(ya, yb, sample_count)
    cells = []
    for xi in xs:
        for yi in ys:
            cells.append(
                {
                    "x": _float(xi),
                    "y": _float(yi),
                    "value": _float(f.subs({x: xi, y: yi})),
                }
            )

    return {
        "kind": "cartesian_double_integral",
        "integrand_latex": tex(f),
        "bounds_latex": {
            "x": [tex(xa), tex(xb)],
            "y": [tex(ya), tex(yb)],
        },
        "inner_latex": tex(inner),
        "exact": exact,
        "answer_latex": tex(exact),
        "samples": {"cells": cells},
    }


def solve_polar_double_integral(integrand, r_bounds, theta_bounds, sample_count=5):
    """Compute polar double integrals with the Jacobian r."""
    f = expr(integrand)
    ra, rb = _bound_pair(r_bounds)
    ta, tb = _bound_pair(theta_bounds)
    jacobian_integrand = sp.simplify(f * r)

    inner = sp.integrate(jacobian_integrand, (r, ra, rb))
    exact = sp.simplify(sp.integrate(inner, (theta, ta, tb)))

    rings = []
    for ri in _linspace(ra, rb, sample_count):
        radius = _float(ri)
        points = []
        for ti in _linspace(ta, tb, 16):
            points.append([radius * math.cos(_float(ti)), radius * math.sin(_float(ti))])
        rings.append({"r": radius, "points": points})

    return {
        "kind": "polar_double_integral",
        "integrand_latex": tex(f),
        "jacobian_integrand_latex": tex(jacobian_integrand),
        "bounds_latex": {
            "r": [tex(ra), tex(rb)],
            "theta": [tex(ta), tex(tb)],
        },
        "inner_latex": tex(inner),
        "exact": exact,
        "answer_latex": tex(exact),
        "samples": {"rings": rings},
    }


def solve_surface_flux(vector_field, parametrization, u_bounds, v_bounds, sample_count=4):
    """Compute flux of F through r(u,v) using F(r(u,v)) dot (r_u x r_v)."""
    if len(vector_field) != 3 or len(parametrization) != 3:
        raise ValueError("vector_field and parametrization must each have 3 components")

    field = sp.Matrix([expr(c) for c in vector_field])
    surface = sp.Matrix([expr(c) for c in parametrization])
    ua, ub = _bound_pair(u_bounds)
    va, vb = _bound_pair(v_bounds)

    ru = surface.diff(u)
    rv = surface.diff(v)
    normal = sp.simplify(ru.cross(rv))
    substitutions = {x: surface[0], y: surface[1], z: surface[2]}
    field_on_surface = sp.Matrix([sp.simplify(c.subs(substitutions)) for c in field])
    integrand_uv = sp.simplify(field_on_surface.dot(normal))
    inner = sp.integrate(integrand_uv, (v, va, vb))
    exact = sp.simplify(sp.integrate(inner, (u, ua, ub)))

    surface_samples = []
    vector_samples = []
    for ui in _linspace(ua, ub, sample_count):
        for vi in _linspace(va, vb, sample_count):
            point = [sp.simplify(c.subs({u: ui, v: vi})) for c in surface]
            field_vec = [sp.simplify(c.subs({u: ui, v: vi})) for c in field_on_surface]
            normal_vec = [sp.simplify(c.subs({u: ui, v: vi})) for c in normal]
            surface_samples.append(_numeric_points([point])[0])
            if len(vector_samples) < 9:
                vector_samples.append(
                    {
                        "point": _numeric_points([point])[0],
                        "field": _numeric_points([field_vec])[0],
                        "normal": _numeric_points([normal_vec])[0],
                    }
                )

    return {
        "kind": "surface_flux",
        "field_latex": [tex(c) for c in field],
        "parametrization_latex": [tex(c) for c in surface],
        "normal_latex": [tex(c) for c in normal],
        "integrand_latex": tex(integrand_uv),
        "bounds_latex": {
            "u": [tex(ua), tex(ub)],
            "v": [tex(va), tex(vb)],
        },
        "exact": exact,
        "answer_latex": tex(exact),
        "samples": {"surface": surface_samples, "vectors": vector_samples},
    }


def solve_first_order_ode(rhs, x0, y0, sample_bounds=(-2, 2), sample_count=41):
    """Solve y' = rhs(x, y), y(x0)=y0 using SymPy dsolve."""
    y_func = sp.Function("y")
    rhs_expr_symbolic = expr(rhs, {"y": Y})
    rhs_expr_for_dsolve = rhs_expr_symbolic.subs(Y, y_func(x))
    equation = sp.Eq(sp.diff(y_func(x), x), rhs_expr_for_dsolve)
    solution = sp.dsolve(equation, ics={y_func(expr(x0)): expr(y0)})
    solution_expr = sp.simplify(solution.rhs)

    xa, xb = _bound_pair(sample_bounds)
    xs = _linspace(xa, xb, sample_count)
    solution_fn = sp.lambdify(x, solution_expr, "math")
    rhs_fn = sp.lambdify((x, Y), rhs_expr_symbolic, "math")

    solution_curve = []
    for xi in xs:
        xf = _float(xi)
        solution_curve.append({"x": xf, "y": float(solution_fn(xf))})

    slope_field = []
    x_grid = _linspace(xa, xb, 7)
    y_grid = _linspace(-2, 2, 7)
    for xi in x_grid:
        for yi in y_grid:
            xf, yf = _float(xi), _float(yi)
            m = float(rhs_fn(xf, yf))
            if math.isfinite(m):
                scale = math.sqrt(1 + m * m)
                slope_field.append(
                    {
                        "x": xf,
                        "y": yf,
                        "dx": 1 / scale,
                        "dy": m / scale,
                        "slope": m,
                    }
                )

    return {
        "kind": "first_order_ode",
        "rhs_latex": tex(rhs_expr_symbolic),
        "equation_latex": r"\frac{dy}{dx} = " + tex(rhs_expr_symbolic),
        "initial_latex": f"y({tex(expr(x0))})={tex(expr(y0))}",
        "solution_expr": solution_expr,
        "solution_latex": tex(solution_expr),
        "exact": solution_expr,
        "samples": {
            "slope_field": slope_field,
            "solution_curve": solution_curve,
            "initial": {"x": _float(expr(x0)), "y": _float(expr(y0))},
        },
    }


def _self_check():
    checks = [
        (
            "cartesian double integral",
            solve_cartesian_double_integral("x + y", (0, 1), (0, 2))["exact"],
            sp.Integer(3),
        ),
        (
            "polar unit disk area",
            solve_polar_double_integral("1", (0, 1), (0, "2*pi"))["exact"],
            sp.pi,
        ),
        (
            "surface flux plane z=1",
            solve_surface_flux(("x", "y", "z"), ("u", "v", "1"), (0, 1), (0, 1))["exact"],
            sp.Integer(1),
        ),
        (
            "ode y'=y",
            solve_first_order_ode("y", 0, 1)["solution_expr"],
            sp.exp(x),
        ),
    ]
    for name, got, expected in checks:
        ok = sp.simplify(got - expected) == 0
        print(f"{name}: {tex(got)}", "PASS" if ok else f"FAIL expected {tex(expected)}")
        assert ok
    print("higher-math kernel self-check PASS")


if __name__ == "__main__":
    _self_check()
