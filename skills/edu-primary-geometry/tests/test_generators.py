# -*- coding: utf-8 -*-
"""几何好数生成器单测：1000 次抽样断言底/高/面积恒整数、关系恒成立。"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

import generators as gn  # noqa: E402

N = 1000


def test_area_parallelogram():
    rng = random.Random(1)
    for _ in range(N):
        p = gn.gen_area_parallelogram(rng)
        assert p["S"] == p["a"] * p["h"]
        assert isinstance(p["a"], int) and isinstance(p["h"], int) and isinstance(p["S"], int)
        assert p["a"] >= 4 and p["h"] >= 3
        assert 0 <= p["dx0"] <= p["dxMax"]


def test_area_triangle():
    rng = random.Random(2)
    for _ in range(N):
        p = gn.gen_area_triangle(rng)
        assert p["S"] == p["a"] * p["h"] // 2
        assert isinstance(p["a"], int) and isinstance(p["h"], int) and isinstance(p["S"], int)
        assert p["a"] in (4, 6, 8)
        assert 1 <= p["cx0"] <= p["a"] - 1
        assert p["cxMin"] == 1 and p["cxMax"] == p["a"] - 1


def test_area_trapezoid():
    rng = random.Random(3)
    for _ in range(N):
        p = gn.gen_area_trapezoid(rng)
        assert (p["a"] + p["b"]) * p["h"] % 2 == 0
        assert p["S"] == (p["a"] + p["b"]) * p["h"] // 2
        assert isinstance(p["S"], int)
        assert p["dxMin"] == p["a"] and p["dxMax"] == p["b"]
        assert p["a"] <= p["dx0"] <= p["b"]


def test_area_circle():
    rng = random.Random(4)
    for _ in range(N):
        p = gn.gen_area_circle(rng)
        assert p["S"] == 3 * p["r"] * p["r"]
        assert isinstance(p["S"], int)
        assert 3 <= p["r"] <= 6
        assert p["nMin"] == 4 and p["nMax"] == 16


def test_composite_area():
    rng = random.Random(5)
    for _ in range(N):
        p = gn.gen_composite_area(rng)
        assert p["S"] == p["a"] * p["H"] + p["b"] * p["h"]
        assert isinstance(p["S"], int)
        assert p["h"] < p["H"]


def test_grid_count():
    rng = random.Random(6)
    for _ in range(N):
        p = gn.gen_grid_count(rng)
        assert p["rows"] in (2, 4)
        assert len(p["widths"]) == p["rows"]
        assert all(2 <= w <= p["G"] - 1 for w in p["widths"])
        assert p["f"] == sum(p["widths"])
        assert p["hb"] == p["rows"]
        assert p["S"] == p["f"] + p["hb"] // 2
        assert isinstance(p["S"], int)


def test_three_view():
    rng = random.Random(7)
    for _ in range(N):
        p = gn.gen_three_view(rng)
        assert p["cols"] in (3, 4)
        assert len(p["heights"]) == p["cols"]
        assert all(1 <= x <= 3 for x in p["heights"])
        assert p["front"] == sum(p["heights"])
        assert p["top"] == p["cols"]
        assert p["side"] == max(p["heights"])


def test_transform_symmetry():
    rng = random.Random(8)
    for _ in range(N):
        p = gn.gen_transform_symmetry(rng)
        assert p["mode"] in ("translate", "reflect")
        assert p["A"] == (1, 1) and p["B"] == (4, 1) and p["C"] == (1, 4)
        if p["mode"] == "translate":
            assert 4 <= p["ax"] <= 6 and 2 <= p["ay"] <= 4
        else:
            assert p["ax"] == 11 and p["ay"] == 1
        assert p["rule"]


def test_cuboid_volume():
    rng = random.Random(9)
    for _ in range(N):
        p = gn.gen_cuboid_volume(rng)
        assert p["V"] == p["a"] * p["b"] * p["c"]
        assert p["S"] == 2 * (p["a"] * p["b"] + p["b"] * p["c"] + p["c"] * p["a"])
        assert 2 <= p["a"] <= 5 and 2 <= p["b"] <= 5 and 2 <= p["c"] <= 5
        assert isinstance(p["V"], int) and isinstance(p["S"], int)


if __name__ == "__main__":
    test_area_parallelogram()
    test_area_triangle()
    test_area_trapezoid()
    test_area_circle()
    test_composite_area()
    test_grid_count()
    test_three_view()
    test_transform_symmetry()
    test_cuboid_volume()
    print(f"OK  9 类 × {N} 次抽样全部通过")
