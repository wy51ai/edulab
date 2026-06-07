#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analytic_kernel.py — 解析几何 sympy 精确求解核心。

设计哲学（单一数据源）：答案、坐标、步骤数值、前端交互引擎的"理论范围"全部从这里的
sympy 精确结果导出，杜绝心算与不一致。

核心套路：含参直线 x = m·y + c（c 由"过定点"确定），代入圆锥曲线得关于 y 的二次方程，
韦达定理给出 y1+y2, y1·y2（精确），由此把目标量（数量积/弦长/面积/斜率积…）写成 m 的
表达式，再用 range_over_m 求其取值范围（含开闭端点判定）。

m 的几何含义：直线 x=my+c 的斜率为 1/m，即 m=cotθ（θ 为倾斜角）。
 - m=0  → 竖直线（θ=90°）
 - m→∞ → 水平线（θ=0°，前端滑块拖到 0° 即此情形）
"""
import sympy as sp
import conics
from conics import x, y

m = sp.symbols('m', real=True)
u = sp.symbols('u', nonnegative=True)     # u = m^2


# ---------------- 通用工具 ----------------
def tex(e):
    return sp.latex(sp.nsimplify(sp.simplify(e)))


def fnum(e):
    return float(sp.N(e))


def is_clean(e):
    """答案是否"规整"（有理数或最简根式），用于随机出题筛选。"""
    e = sp.nsimplify(sp.simplify(e))
    return e.is_rational or (e.free_symbols == set() and sp.simplify(e - sp.nsimplify(e)) == 0)


def interval_latex(lo, hi, lo_closed, hi_closed):
    lb = '[' if lo_closed else '('
    rb = ']' if hi_closed else ')'
    lo_s = r'-\infty' if lo == -sp.oo else tex(lo)
    hi_s = r'+\infty' if hi == sp.oo else tex(hi)
    return r"%s%s,\ %s%s" % (lb, lo_s, hi_s, rb)


# ---------------- 含参直线 ∩ 圆锥曲线 + 韦达 ----------------
def chord_setup(conic, through):
    """直线 x = m·y + c 过点 through，与 conic 联立 → 关于 y 的二次。返回韦达量等。"""
    x0, y0 = sp.nsimplify(through[0]), sp.nsimplify(through[1])
    c = x0 - m * y0
    sub = sp.expand(conic['implicit'].subs(x, m * y + c))
    num = sp.numer(sp.together(sub))
    poly = sp.Poly(num, y)
    coeffs = poly.all_coeffs()
    if len(coeffs) != 3:
        raise ValueError(f"联立未得到 y 的二次方程：{poly}")
    A, B, C = coeffs
    return {
        'm': m, 'c': c, 'A': A, 'B': B, 'C': C, 'poly': poly,
        'ysum': sp.simplify(-B / A), 'yprod': sp.simplify(C / A),
        'disc': sp.simplify(B**2 - 4 * A * C),
    }


def _xy_from_y(cs, M=None):
    """由韦达量给出 x1+x2, x1x2（用于把目标量化成 m 的表达式）。"""
    ys, yp = cs['ysum'], cs['yprod']
    xs = m * ys + 2 * cs['c']                 # x1+x2
    xp = m**2 * yp + m * cs['c'] * ys + cs['c']**2   # x1·x2
    return sp.simplify(xs), sp.simplify(xp)


# ---------------- 目标量（写成 m 的表达式）----------------
def dot_product_expr(conic, through, M):
    """以 M 为顶点，A、B 为交点的数量积 MA·MB 关于 m 的表达式。"""
    cs = chord_setup(conic, through)
    ys, yp = cs['ysum'], cs['yprod']
    xs, xp = _xy_from_y(cs)
    Mx, My = sp.nsimplify(M[0]), sp.nsimplify(M[1])
    # (x1-Mx)(x2-Mx)+(y1-My)(y2-My) = xp - Mx*xs + Mx^2 + yp - My*ys + My^2
    expr = xp - Mx * xs + Mx**2 + yp - My * ys + My**2
    return sp.simplify(expr), cs


def chord_len_sq_expr(conic, through):
    """弦长平方 |AB|^2 关于 m 的表达式。|AB|^2=(1+m^2)[(y1+y2)^2-4y1y2]。"""
    cs = chord_setup(conic, through)
    expr = (1 + m**2) * (cs['ysum']**2 - 4 * cs['yprod'])
    return sp.simplify(expr), cs


def triangle_area_expr(conic, through, vertex):
    """△(vertex,A,B) 面积 = 1/2·|AB|·d(vertex,l)。返回面积关于 m 的表达式。"""
    cs = chord_setup(conic, through)
    chord = sp.sqrt((1 + m**2) * (cs['ysum']**2 - 4 * cs['yprod']))
    # 直线 x - m y - c = 0，点到直线距离 d=|vx - m vy - c|/sqrt(1+m^2)
    vx, vy = sp.nsimplify(vertex[0]), sp.nsimplify(vertex[1])
    d = sp.Abs(vx - m * vy - cs['c']) / sp.sqrt(1 + m**2)
    return sp.simplify(sp.Rational(1, 2) * chord * d), cs


# ---------------- 取值范围（关键：含开闭端点判定）----------------
def range_over_m(expr, horizontal_valid=True):
    """目标量 expr(m) 在 m∈ℝ 上的取值范围；horizontal_valid=True 表示水平线（m→∞）
    也是合法直线（如椭圆过内点的弦），其极限值也被取到（端点闭）。

    返回 dict：lo,hi（sympy）、lo_closed,hi_closed、latex、lo_f,hi_f（float）、argmax/argmin。
    """
    g = sp.simplify(expr)
    cand = []   # (value, attained?)

    # 驻点
    dg = sp.together(sp.diff(g, m))
    for r in sp.solve(sp.numer(dg), m):
        if r.is_real:
            cand.append((sp.simplify(g.subs(m, r)), True))
    # m=0（竖直线，总是合法）
    cand.append((sp.simplify(g.subs(m, 0)), True))
    # m→±∞（水平线）
    Lp = sp.limit(g, m, sp.oo)
    cand.append((sp.simplify(Lp), bool(horizontal_valid) and Lp.is_finite))

    finite = [(v, a) for (v, a) in cand if v.is_finite]
    lo_val = min(finite, key=lambda t: fnum(t[0]))[0]
    hi_val = max(finite, key=lambda t: fnum(t[0]))[0]
    # 无界判定
    hi = sp.oo if (Lp == sp.oo or any((not v.is_finite and v == sp.oo) for v, _ in cand)) else hi_val
    lo = -sp.oo if (Lp == -sp.oo) else lo_val
    lo_closed = (lo != -sp.oo) and any(a for (v, a) in cand if sp.simplify(v - lo) == 0)
    hi_closed = (hi != sp.oo) and any(a for (v, a) in cand if sp.simplify(v - hi) == 0)
    return {
        'lo': lo, 'hi': hi, 'lo_closed': lo_closed, 'hi_closed': hi_closed,
        'lo_f': (None if lo == -sp.oo else fnum(lo)),
        'hi_f': (None if hi == sp.oo else fnum(hi)),
        'latex': interval_latex(lo, hi, lo_closed, hi_closed),
    }


# ---------------- 定值（与 m 无关）----------------
def is_constant_in_m(expr):
    e = sp.simplify(expr)
    return sp.simplify(sp.diff(e, m)) == 0, sp.simplify(e.subs(m, 0))


def slope_product_central(conic, P):
    """P 为曲线上定点，A 为曲线上动点，B 为 A 关于中心的对称点。
    返回 k_PA·k_PB（应为定值 -b²/a²，与 A 位置无关）。"""
    t = sp.symbols('t', real=True)
    cx, cy = conic['center']
    if conic['kind'] == 'ellipse':
        A = (cx + conic['a'] * sp.cos(t), cy + conic['b'] * sp.sin(t))
    else:
        raise ValueError("slope_product_central 目前支持椭圆")
    B = (2 * cx - A[0], 2 * cy - A[1])
    Px, Py = sp.nsimplify(P[0]), sp.nsimplify(P[1])
    kA = (A[1] - Py) / (A[0] - Px)
    kB = (B[1] - Py) / (B[0] - Px)
    prod = sp.simplify(sp.trigsimp(kA * kB))
    return prod


# ---------------- 离心率范围（形状参数题）----------------
def ecc_range_focal_ratio(k):
    """双曲线右支上存在 P 使 |PF₁| = k|PF₂|（k>1）求 e 的范围。

    右支焦半径：|PF₁|−|PF₂|=2a 且 |PF₂|≥c−a。由 k|PF₂|−|PF₂|=2a 得 |PF₂|=2a/(k−1)，
    代入 |PF₂|≥c−a 得 e ≤ (k+1)/(k−1)；又 e>1。故 e ∈ (1, (k+1)/(k−1)]。
    返回 dict：lo,hi,lo_closed,hi_closed,lo_f,hi_f,latex,k。
    """
    k = sp.nsimplify(k)
    if k <= 1:
        raise ValueError("k 必须 > 1")
    hi = sp.simplify((k + 1) / (k - 1))
    lo = sp.Integer(1)
    return {
        'lo': lo, 'hi': hi, 'lo_closed': False, 'hi_closed': True,
        'lo_f': 1.0, 'hi_f': fnum(hi),
        'latex': interval_latex(lo, hi, False, True), 'k': k,
    }


# =====================================================================
# 自检：旗舰题（椭圆 x²/4+y²/3=1，M(-1,0)，过 F(1,0) 的弦，MA·MB 范围）
# =====================================================================
if __name__ == "__main__":
    E = conics.ellipse(2, sp.sqrt(3))
    print("椭圆:", E['eq_latex'], " 焦点", E['foci'])

    expr, cs = dot_product_expr(E, (1, 0), (-1, 0))
    print("\n二次方程系数 (A,B,C):", cs['A'], cs['B'], cs['C'])
    print("韦达 y1+y2 =", cs['ysum'], " y1y2 =", cs['yprod'])
    print("MA·MB(m) =", expr, "=", sp.simplify(expr.rewrite(sp.Add)))
    print("化简:", sp.apart(expr, m))

    rg = range_over_m(expr, horizontal_valid=True)
    print("\n范围:", rg['latex'], " floats:", rg['lo_f'], rg['hi_f'],
          " closed:", rg['lo_closed'], rg['hi_closed'])
    assert rg['lo_f'] == -3.0 and abs(rg['hi_f'] - 1.75) < 1e-12, "旗舰范围应为 [-3, 7/4]"
    assert rg['lo_closed'] and rg['hi_closed'], "两端均应闭（水平线取到 -3，竖直线取到 7/4）"
    print("\n✅ 旗舰自检通过：MA·MB ∈", rg['latex'])

    # 弦长（过焦点）范围自检：椭圆通径 2b²/a=3 为最短，长轴 2a=4 为最长
    cl2, _ = chord_len_sq_expr(E, (1, 0))
    rgc = range_over_m(cl2, horizontal_valid=True)
    print("弦长² 范围:", rgc['latex'], "→ 弦长 ∈ [",
          sp.sqrt(rgc['lo']), ",", sp.sqrt(rgc['hi']), "]")
