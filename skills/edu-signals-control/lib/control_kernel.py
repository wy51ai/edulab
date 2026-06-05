#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
control_kernel.py - exact feedback/control-system computation core for edulab.

The kernel owns all symbolic transfer-function answers. Lesson templates may
draw numeric samples, but must not recompute closed-loop formulas in JavaScript.
"""

from __future__ import annotations

import math
from typing import Mapping, Sequence

import sympy as sp


s = sp.Symbol("s")
k = sp.Symbol("k")
A = sp.Symbol("A")
tau = sp.Symbol("tau")
omega = sp.Symbol("omega")
F = sp.Function("F")


def _locals(extra=None):
    base = {
        "s": s,
        "k": k,
        "A": A,
        "tau": tau,
        "omega": omega,
        "w": omega,
        "I": sp.I,
        "j": sp.I,
        "pi": sp.pi,
        "E": sp.E,
        "e": sp.E,
        "sqrt": sp.sqrt,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "exp": sp.exp,
        "log": sp.log,
        "Abs": sp.Abs,
        "abs": sp.Abs,
        "F": F,
    }
    if extra:
        base.update(extra)
    return base


def expr(value, extra=None):
    """Parse compact transfer-function strings into SymPy expressions."""
    return sp.sympify(value, locals=_locals(extra))


def tex(value) -> str:
    rendered = sp.latex(sp.simplify(value))
    return rendered.replace(r"F{\left(s \right)}", "F(s)")


def _float(value) -> float:
    val = float(sp.N(value, 14))
    if not math.isfinite(val):
        raise ValueError(f"Non-finite sample value: {value!r}")
    return val


def _numeric_complex(value) -> complex:
    number = complex(sp.N(value, 14))
    if not math.isfinite(number.real) or not math.isfinite(number.imag):
        raise ValueError(f"Non-finite complex sample value: {value!r}")
    return number


def _magnitude_db(value: complex) -> float:
    return 20.0 * math.log10(max(abs(value), 1e-12))


def _phase_deg(value: complex) -> float:
    return math.degrees(math.atan2(value.imag, value.real))


def _parameter_subs(parameter_values: Mapping[str, object] | None) -> dict[sp.Expr, sp.Expr]:
    values = {"A": 1, "tau": sp.Rational(1, 4), "k": 40}
    if parameter_values:
        values.update(parameter_values)
    return {expr(name): expr(value) for name, value in values.items()}


def closed_loop_transfer(forward_gain, feedback, feedback_sign: str = "negative") -> sp.Expr:
    """Return the exact single-loop closed-loop transfer H(s)."""
    G = expr(forward_gain)
    B = expr(feedback)
    if feedback_sign == "negative":
        denominator = 1 + G * B
    elif feedback_sign == "positive":
        denominator = 1 - G * B
    else:
        raise ValueError("feedback_sign must be 'negative' or 'positive'")
    return sp.simplify(G / denominator)


def limit_high_loop_gain(closed_loop, variable="k", target=sp.oo) -> sp.Expr:
    """Return the exact high-loop-gain limit, usually k -> infinity."""
    variable_expr = expr(variable)
    return sp.simplify(sp.limit(expr(closed_loop), variable_expr, target))


def bode_samples(
    transfer,
    feedback,
    high_gain_limit,
    parameter_values: Mapping[str, object] | None = None,
    sample_omegas: Sequence[float] = (0.1, 0.3, 1, 3, 10),
) -> list[dict[str, float]]:
    """Sample transfer expressions at s = j*omega for the SVG visual."""
    transfer_expr = expr(transfer)
    feedback_expr = expr(feedback)
    limit_expr = expr(high_gain_limit)
    substitutions = _parameter_subs(parameter_values)

    samples = []
    for item in sample_omegas:
        w = _float(item)
        point_subs = dict(substitutions)
        point_subs.update({s: sp.I * w, omega: w})

        closed_value = _numeric_complex(transfer_expr.subs(point_subs))
        feedback_value = _numeric_complex(feedback_expr.subs(point_subs))
        limit_value = _numeric_complex(limit_expr.subs(point_subs))
        samples.append(
            {
                "omega": round(w, 6),
                "closedLoopMagnitudeDb": _magnitude_db(closed_value),
                "closedLoopPhaseDeg": _phase_deg(closed_value),
                "highGainMagnitudeDb": _magnitude_db(limit_value),
                "highGainPhaseDeg": _phase_deg(limit_value),
                "feedbackMagnitudeDb": _magnitude_db(feedback_value),
                "feedbackPhaseDeg": _phase_deg(feedback_value),
            }
        )
    return samples


def solve_negative_feedback_loop(
    forward_gain="k*A",
    feedback="F(s)",
    parameter_values: Mapping[str, object] | None = None,
    sample_omegas: Sequence[float] = (0.1, 0.3, 1, 3, 10),
) -> dict:
    """Solve the single-loop negative-feedback transfer and high-gain limit."""
    G = expr(forward_gain)
    B = expr(feedback)
    loop_gain = sp.simplify(G * B)
    closed = sp.simplify(G / (1 + loop_gain))
    high_gain = sp.simplify(sp.limit(closed, k, sp.oo))

    samples = {"bode": []}
    unresolved = (
        (closed.free_symbols | B.free_symbols | high_gain.free_symbols)
        - set(_parameter_subs(parameter_values).keys())
        - {s}
    )
    if not unresolved:
        try:
            samples["bode"] = bode_samples(
                closed,
                B,
                high_gain,
                parameter_values=parameter_values,
                sample_omegas=sample_omegas,
            )
        except (TypeError, ValueError):
            samples["bode"] = []

    return {
        "kind": "negative_feedback_loop",
        "forward_gain": G,
        "feedback": B,
        "loop_gain": loop_gain,
        "closed_loop": closed,
        "high_gain_limit": high_gain,
        "forward_gain_latex": tex(G),
        "feedback_latex": tex(B),
        "loop_gain_latex": tex(loop_gain),
        "closed_loop_latex": tex(closed),
        "high_gain_limit_latex": tex(high_gain),
        "answer_latex": tex(closed) + r"\xrightarrow{k\to\infty}" + tex(high_gain),
        "samples": samples,
    }


def _self_check():
    generic = solve_negative_feedback_loop("k*A", "F(s)")
    expected = A * k / (A * k * F(s) + 1)
    assert sp.simplify(generic["closed_loop"] - expected) == 0
    assert sp.simplify(generic["high_gain_limit"] - 1 / F(s)) == 0

    first_order = solve_negative_feedback_loop(
        "k*A",
        "1/(tau*s + 1)",
        parameter_values={"A": 2, "tau": sp.Rational(1, 4), "k": 40},
    )
    assert sp.simplify(first_order["high_gain_limit"] - (tau * s + 1)) == 0
    assert len(first_order["samples"]["bode"]) >= 3
    print("control_kernel self-check ok")


if __name__ == "__main__":
    _self_check()
