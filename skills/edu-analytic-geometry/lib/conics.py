#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
conics.py — 圆锥曲线的 sympy 精确定义库。

每个构造函数返回一个 dict，含：
  kind / center / 半轴(a,b) 或 r / p ...        —— 几何参数（sympy 精确）
  c, foci, vertices, ecc, asymptotes, directrix —— 特殊量（按曲线类型）
  implicit  : 关于 x,y 的隐式表达式 = 0
  eq_latex  : 标准方程 LaTeX
  board     : 注入前端引擎 board.conics[*] 的 dict（浮点）

约定：a = x 方向半轴，b = y 方向半轴（椭圆）；双曲线 a=实半轴, b=虚半轴 + orient。
大多数高考题中心在原点，这里以原点为主，圆支持任意圆心。
"""
import sympy as sp

x, y = sp.symbols('x y', real=True)


def _f(e):
    """sympy 精确量 → float。"""
    return float(sp.N(e))


def _sq_latex(e):
    """把 a^2 写成尽量整洁的 LaTeX（整数直接显示）。"""
    e = sp.nsimplify(e)
    return sp.latex(sp.simplify(e))


def _term(numer_latex, denom):
    """分式项：分母为 1 时折叠为分子本身（x^2/1 → x^2）。"""
    denom = sp.simplify(sp.nsimplify(denom))
    if denom == 1:
        return numer_latex
    return r"\frac{%s}{%s}" % (numer_latex, _sq_latex(denom))


def ellipse(a, b, center=(0, 0)):
    """椭圆 (x-cx)^2/a^2 + (y-cy)^2/b^2 = 1。a=x 半轴, b=y 半轴。焦点在长轴上。"""
    a, b = sp.nsimplify(a), sp.nsimplify(b)
    cx, cy = sp.nsimplify(center[0]), sp.nsimplify(center[1])
    if a == b:
        raise ValueError("a==b 是圆，请用 circle()")
    if a > b:                       # 焦点在 x 轴
        c = sp.sqrt(a**2 - b**2)
        foci = {'F1': (cx - c, cy), 'F2': (cx + c, cy)}
        ecc = c / a
        verts = {'A1': (cx - a, cy), 'A2': (cx + a, cy), 'B1': (cx, cy - b), 'B2': (cx, cy + b)}
    else:                           # 焦点在 y 轴
        c = sp.sqrt(b**2 - a**2)
        foci = {'F1': (cx, cy - c), 'F2': (cx, cy + c)}
        ecc = c / b
        verts = {'A1': (cx, cy - b), 'A2': (cx, cy + b), 'B1': (cx - a, cy), 'B2': (cx + a, cy)}
    implicit = (x - cx)**2 / a**2 + (y - cy)**2 / b**2 - 1
    if cx == 0 and cy == 0:
        eq_latex = r"%s+%s=1" % (_term("x^2", a**2), _term("y^2", b**2))
    else:
        eq_latex = r"\frac{(x-%s)^2}{%s}+\frac{(y-%s)^2}{%s}=1" % (
            sp.latex(cx), _sq_latex(a**2), sp.latex(cy), _sq_latex(b**2))
    return {
        'kind': 'ellipse', 'a': a, 'b': b, 'c': c, 'center': (cx, cy),
        'foci': foci, 'vertices': verts, 'ecc': ecc,
        'implicit': implicit, 'eq_latex': eq_latex,
        'board': {'kind': 'ellipse', 'a': _f(a), 'b': _f(b), 'center': [_f(cx), _f(cy)]},
    }


def hyperbola(a, b, center=(0, 0), orient='x'):
    """双曲线。orient='x': (x)^2/a^2-(y)^2/b^2=1（焦点在 x 轴）；'y' 反之。a=实半轴,b=虚半轴。"""
    a, b = sp.nsimplify(a), sp.nsimplify(b)
    cx, cy = sp.nsimplify(center[0]), sp.nsimplify(center[1])
    c = sp.sqrt(a**2 + b**2)
    if orient == 'x':
        foci = {'F1': (cx - c, cy), 'F2': (cx + c, cy)}
        verts = {'A1': (cx - a, cy), 'A2': (cx + a, cy)}
        implicit = (x - cx)**2 / a**2 - (y - cy)**2 / b**2 - 1
        asym = (b / a, -b / a)
        eq_latex = r"%s-%s=1" % (_term("x^2", a**2), _term("y^2", b**2))
    else:
        foci = {'F1': (cx, cy - c), 'F2': (cx, cy + c)}
        verts = {'A1': (cx, cy - a), 'A2': (cx, cy + a)}
        implicit = (y - cy)**2 / a**2 - (x - cx)**2 / b**2 - 1
        asym = (a / b, -a / b)
        eq_latex = r"%s-%s=1" % (_term("y^2", a**2), _term("x^2", b**2))
    return {
        'kind': 'hyperbola', 'a': a, 'b': b, 'c': c, 'center': (cx, cy), 'orient': orient,
        'foci': foci, 'vertices': verts, 'ecc': c / a, 'asymptote_slopes': asym,
        'implicit': implicit, 'eq_latex': eq_latex,
        'board': {'kind': 'hyperbola', 'a': _f(a), 'b': _f(b), 'center': [_f(cx), _f(cy)],
                  'orient': orient, 'asymptotes': True},
    }


def parabola(p, vertex=(0, 0), axis='x'):
    """抛物线。axis='x': (y-cy)^2=2p(x-cx)（开口随 p 符号）；'y': (x-cx)^2=2p(y-cy)。"""
    p = sp.nsimplify(p)
    cx, cy = sp.nsimplify(vertex[0]), sp.nsimplify(vertex[1])
    if axis == 'x':
        focus = (cx + p / 2, cy)
        directrix = ('x', cx - p / 2)         # 准线 x = cx - p/2
        implicit = (y - cy)**2 - 2 * p * (x - cx)
        eq_latex = (r"y^2=%s x" % sp.latex(2 * p)) if (cx == 0 and cy == 0) else \
                   (r"(y-%s)^2=%s(x-%s)" % (sp.latex(cy), sp.latex(2 * p), sp.latex(cx)))
    else:
        focus = (cx, cy + p / 2)
        directrix = ('y', cy - p / 2)
        implicit = (x - cx)**2 - 2 * p * (y - cy)
        eq_latex = (r"x^2=%s y" % sp.latex(2 * p)) if (cx == 0 and cy == 0) else \
                   (r"(x-%s)^2=%s(y-%s)" % (sp.latex(cx), sp.latex(2 * p), sp.latex(cy))
                    )
    return {
        'kind': 'parabola', 'p': p, 'vertex': (cx, cy), 'axis': axis,
        'focus': focus, 'directrix': directrix,
        'implicit': implicit, 'eq_latex': eq_latex,
        'board': {'kind': 'parabola', 'p': _f(p), 'center': [_f(cx), _f(cy)], 'axis': axis},
    }


def circle(center, r):
    """圆 (x-cx)^2+(y-cy)^2=r^2。"""
    cx, cy = sp.nsimplify(center[0]), sp.nsimplify(center[1])
    r = sp.nsimplify(r)
    implicit = (x - cx)**2 + (y - cy)**2 - r**2
    if cx == 0 and cy == 0:
        eq_latex = r"x^2+y^2=%s" % _sq_latex(r**2)
    else:
        eq_latex = r"(x-%s)^2+(y-%s)^2=%s" % (sp.latex(cx), sp.latex(cy), _sq_latex(r**2))
    return {
        'kind': 'circle', 'center': (cx, cy), 'r': r,
        'implicit': implicit, 'eq_latex': eq_latex,
        'board': {'kind': 'circle', 'r': _f(r), 'center': [_f(cx), _f(cy)]},
    }


if __name__ == "__main__":
    e = ellipse(2, sp.sqrt(3))
    print("ellipse:", e['eq_latex'], "| foci", e['foci'], "| e =", e['ecc'])
    h = hyperbola(1, sp.sqrt(3))
    print("hyperbola:", h['eq_latex'], "| foci", h['foci'], "| asym", h['asymptote_slopes'])
    pa = parabola(2)
    print("parabola:", pa['eq_latex'], "| focus", pa['focus'], "| directrix", pa['directrix'])
    print("circle:", circle((0, 0), 2)['eq_latex'])
