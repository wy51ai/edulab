# -*- coding: utf-8 -*-
"""答案先行「好数」采样：几何量恒为整数（底/高/面积/体积），纯标准库 random + math。

几何好数约定：
  - 底/高取整数；平行四边形/长方形面积 = 底 × 高 恒整数；
  - 三角形保证 底 × 高 为偶数（÷2 得整数）；
  - 梯形保证 (上底 + 下底) × 高 为偶数；
  - 圆面积 π ≈ 3 或半径取整（S = πr² 得整数/整倍 π）；
  - 长方体长宽高整数 → 体积/表面积整数。

失败抛 NoGoodNumbers（MAX_ATTEMPTS=200）。
"""
import random as _random

MAX_ATTEMPTS = 200


class NoGoodNumbers(Exception):
    pass


# ---------------------------------------------------------------------------
# 面积公式推导
# ---------------------------------------------------------------------------

def gen_area_parallelogram(rng, spec=None):
    """平行四边形面积：底 a、高 h 整数；面积 S = a·h。初始歪斜 dx0（非长方形便于剪拼）。"""
    s = spec or {}
    a = rng.randint(*s.get("a", (4, 8)))     # 底
    h = rng.randint(*s.get("h", (3, 5)))     # 高
    dx0 = rng.randint(*s.get("dx0", (1, 2)))  # 初始歪斜（顶点 D 的横向偏移）
    dxMax = s.get("dxMax", 3)                 # 顶点 D 可拖范围 [0, dxMax]
    return {"a": a, "h": h, "S": a * h, "dx0": dx0, "dxMax": dxMax}


def gen_area_triangle(rng, spec=None):
    """三角形面积：底 a(偶数)、高 h；S = a·h/2 恒整数。顶点 D 沿底边平行线拖（等积变形）。"""
    s = spec or {}
    a = rng.choice([4, 6, 8])                 # 底（偶数保证 a·h 偶）
    h = rng.randint(*s.get("h", (3, 5)))      # 高
    cx0 = rng.randint(2, a - 1)               # 顶点 D 初始 x（底边内）
    return {"a": a, "h": h, "S": a * h // 2, "cx0": cx0, "cxMin": 1, "cxMax": a - 1}


def gen_area_trapezoid(rng, spec=None):
    """梯形面积：上底 a、下底 b、高 h；(a+b)·h 为偶数 → S=(a+b)·h/2 恒整数。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        a = rng.randint(*s.get("a", (2, 4)))  # 上底
        b = rng.randint(*s.get("b", (5, 8)))  # 下底
        h = rng.randint(*s.get("h", (3, 5)))  # 高
        if (a + b) * h % 2 == 0:
            # 上底右端点 D 的 x∈[a, b]（保证上底长 a 且不越界），C = D.x − a
            return {"a": a, "b": b, "h": h, "S": (a + b) * h // 2,
                    "dx0": (a + b) // 2, "dxMin": a, "dxMax": b}
    raise NoGoodNumbers("area_trapezoid")


def gen_area_circle(rng, spec=None):
    """圆面积：半径 r 整数、π≈3；S = 3r²。等分数 N 从 nMin 到 nMax（越大越近长方形）。"""
    s = spec or {}
    r = rng.randint(*s.get("r", (3, 6)))
    return {"r": r, "S": 3 * r * r, "pi": 3, "nMin": 4, "nMax": 16}


def gen_composite_area(rng, spec=None):
    """组合图形(L形)：竖矩形 a×H + 横矩形 b×h（h<H）；S = a·H + b·h。拖竖直辅助线切分。"""
    s = spec or {}
    a = rng.randint(*s.get("a", (2, 5)))      # 竖矩形宽
    H = rng.randint(*s.get("H", (4, 7)))      # 竖矩形高
    b = rng.randint(*s.get("b", (3, 6)))      # 横矩形宽
    h = rng.randint(*s.get("h", (2, 3)))      # 横矩形高（< H）
    return {"a": a, "H": H, "b": b, "h": h, "S": a * H + b * h}


def gen_grid_count(rng, spec=None):
    """不规则图形估算(数方格)：方格纸 G×G；阶梯形满格 widths[i]、每行 1 个半格；
    面积 = 满格 f + 半格 hb/2 恒整数（半格行数为偶保证 hb 偶）。"""
    s = spec or {}
    G = rng.randint(*s.get("G", (6, 8)))      # 方格纸边长(格)
    rows = rng.choice([2, 4])                 # 半格行数（偶）
    widths = [rng.randint(2, G - 1) for _ in range(rows)]  # 每行满格数
    f = sum(widths)                           # 满格数
    hb = rows                                 # 半格数（每行 1 个半格）
    return {"G": G, "rows": rows, "widths": widths, "f": f, "hb": hb, "S": f + hb // 2}


def gen_three_view(rng, spec=None):
    """观察物体：cols 列小方块柱状体；正面格子 = 各列高度和、俯视 = 列数、侧面 = 最高列。"""
    s = spec or {}
    cols = rng.randint(*s.get("cols", (3, 4)))
    heights = [rng.randint(1, 3) for _ in range(cols)]
    return {"cols": cols, "heights": heights, "front": sum(heights),
            "top": cols, "side": max(heights)}


def gen_transform_symmetry(rng, spec=None):
    """平移/轴对称：三角形 A(1,1),B(4,1),C(1,4)；拖对应点 A' 到变换后坐标 (ax, ay)。"""
    s = spec or {}
    mode = rng.choice(["translate", "reflect"])
    A = (1, 1); B = (4, 1); C = (1, 4)
    if mode == "translate":
        dx = rng.randint(3, 5); dy = rng.randint(1, 3)
        ax, ay = A[0] + dx, A[1] + dy
        rule = f"向右平移 {dx} 格、向上平移 {dy} 格"
    else:                                      # 关于竖直轴 x=6 对称
        k = 6
        ax, ay = 2 * k - A[0], A[1]
        rule = f"关于竖直轴 x = {k} 轴对称"
    return {"mode": mode, "A": A, "B": B, "C": C, "ax": ax, "ay": ay, "rule": rule}


def gen_cuboid_volume(rng, spec=None):
    """长方体体积/表面积：长 a、宽 b、高 c 整数；V=a·b·c、S=2(ab+bc+ca)。"""
    s = spec or {}
    a = rng.randint(*s.get("a", (2, 5)))
    b = rng.randint(*s.get("b", (2, 5)))
    c = rng.randint(*s.get("c", (2, 5)))
    return {"a": a, "b": b, "c": c, "V": a * b * c, "S": 2 * (a * b + b * c + c * a)}
