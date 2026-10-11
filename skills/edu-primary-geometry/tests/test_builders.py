# -*- coding: utf-8 -*-
"""几何题型 schema 自检：结构、关键字段、关系。"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

import builders          # noqa: E402
import generators as gn  # noqa: E402

TOP_KEYS = {"type", "lesson", "scene", "answer", "readouts", "status", "steps", "ui"}
LESSON_KEYS = {"title", "problem", "hint"}
STATUS_PHASES = {"before", "at", "after"}
SCENE_KINDS = {"cut-rearrange", "geodrag", "grid-split", "grid", "solid-views",
               "grid-transform", "solid-net"}


def _assert_schema(d):
    assert TOP_KEYS.issubset(d.keys()), f"缺顶层键: {TOP_KEYS - d.keys()}"
    assert LESSON_KEYS.issubset(d["lesson"].keys())
    assert d["scene"]["kind"] in SCENE_KINDS
    param = d["scene"]["param"]
    for k in ("min", "max", "step", "value", "label", "answer"):
        assert k in param, f"param 缺键 {k}"
    for ph in STATUS_PHASES:
        assert "text" in d["status"][ph] and "color" in d["status"][ph]
    assert d["steps"], "解题步骤为空"
    for s in d["steps"]:
        assert "title" in s and "content" in s
    assert d["readouts"], "读数为空"
    kinds = {r["kind"] for r in d["readouts"]}
    assert {"expr", "answer"}.issubset(kinds)
    assert d["ui"]["play"] and d["ui"]["pause"] and d["ui"]["sliderLabel"]


def test_area_parallelogram_schema():
    rng = random.Random(10)
    for _ in range(100):
        p = gn.gen_area_parallelogram(rng)
        d = builders.build_area_parallelogram(p)
        _assert_schema(d)
        assert d["type"] == "area-parallelogram" and d["scene"]["kind"] == "cut-rearrange"
        assert d["scene"]["param"]["answer"] == 2
        assert d["answer"]["S"] == p["a"] * p["h"]
        D = d["scene"]["points"][2]
        assert D["name"] == "D" and D["snap"] == "grid" and D["constraint"] == "h-line"
        assert D["min"] == 0 and D["max"] == p["dxMax"]
        assert d["scene"]["known"] == {"a": p["a"], "h": p["h"]}


def test_area_triangle_schema():
    rng = random.Random(11)
    for _ in range(100):
        p = gn.gen_area_triangle(rng)
        d = builders.build_area_triangle(p)
        _assert_schema(d)
        assert d["type"] == "area-triangle" and d["scene"]["kind"] == "cut-rearrange"
        assert d["scene"]["variant"] == "triangle"
        assert d["scene"]["param"]["answer"] == 2
        assert d["answer"]["S"] == p["a"] * p["h"] // 2
        D = d["scene"]["points"][2]
        assert D["name"] == "D" and D["snap"] == "grid" and D["constraint"] == "h-line"
        assert D["min"] == 1 and D["max"] == p["a"] - 1
        assert d["scene"]["known"] == {"a": p["a"], "h": p["h"]}


def test_area_trapezoid_schema():
    rng = random.Random(12)
    for _ in range(100):
        p = gn.gen_area_trapezoid(rng)
        d = builders.build_area_trapezoid(p)
        _assert_schema(d)
        assert d["type"] == "area-trapezoid" and d["scene"]["variant"] == "trapezoid"
        assert d["answer"]["S"] == (p["a"] + p["b"]) * p["h"] // 2
        D = d["scene"]["points"][2]
        assert D["name"] == "D" and D["constraint"] == "h-line"
        assert D["min"] == p["a"] and D["max"] == p["b"]
        assert d["scene"]["known"] == {"a": p["a"], "b": p["b"], "h": p["h"]}


def test_area_circle_schema():
    rng = random.Random(13)
    for _ in range(100):
        p = gn.gen_area_circle(rng)
        d = builders.build_area_circle(p)
        _assert_schema(d)
        assert d["type"] == "area-circle" and d["scene"]["variant"] == "circle"
        assert d["scene"]["points"] == []
        assert d["scene"]["param"]["min"] == p["nMin"] and d["scene"]["param"]["max"] == p["nMax"]
        assert d["scene"]["param"]["answer"] == p["nMax"]
        assert d["answer"]["S"] == 3 * p["r"] * p["r"]


def test_composite_area_schema():
    rng = random.Random(14)
    for _ in range(100):
        p = gn.gen_composite_area(rng)
        d = builders.build_composite_area(p)
        _assert_schema(d)
        assert d["type"] == "composite-area" and d["scene"]["kind"] == "grid-split"
        assert d["scene"]["dragToT"] == "cut"
        cut = d["scene"]["points"][0]
        assert cut["name"] == "cut" and cut["constraint"] == "h-line"
        assert cut["ax"] == p["a"]
        assert d["scene"]["param"]["answer"] == p["a"]
        assert d["answer"]["S"] == p["a"] * p["H"] + p["b"] * p["h"]


def test_grid_count_schema():
    rng = random.Random(15)
    for _ in range(100):
        p = gn.gen_grid_count(rng)
        d = builders.build_grid_count(p)
        _assert_schema(d)
        assert d["type"] == "grid-count" and d["scene"]["kind"] == "grid"
        assert d["scene"]["points"] == []
        assert d["scene"]["param"]["answer"] == p["S"]
        assert d["answer"]["S"] == p["S"]
        assert d["scene"]["known"]["widths"] == p["widths"]


def test_three_view_schema():
    rng = random.Random(16)
    for _ in range(100):
        p = gn.gen_three_view(rng)
        d = builders.build_three_view(p)
        _assert_schema(d)
        assert d["type"] == "three-view" and d["scene"]["kind"] == "solid-views"
        assert d["scene"]["points"] == []
        assert d["scene"]["param"]["answer"] == p["front"]
        assert d["answer"]["front"] == p["front"]


def test_transform_symmetry_schema():
    rng = random.Random(17)
    for _ in range(100):
        p = gn.gen_transform_symmetry(rng)
        d = builders.build_transform_symmetry(p)
        _assert_schema(d)
        assert d["type"] == "transform-symmetry" and d["scene"]["kind"] == "grid-transform"
        Ap = d["scene"]["points"][0]
        assert Ap["name"] == "Ap" and Ap["snap"] == "grid"
        assert Ap["ax"] == p["ax"] and Ap["ay"] == p["ay"]
        assert Ap["ymin"] == 1 and Ap["ymax"] == 6
        assert d["answer"] == {"ax": p["ax"], "ay": p["ay"]}
        assert d["scene"]["known"]["mode"] == p["mode"]


def test_cuboid_volume_schema():
    rng = random.Random(18)
    for _ in range(100):
        p = gn.gen_cuboid_volume(rng)
        d = builders.build_cuboid_volume(p)
        _assert_schema(d)
        assert d["type"] == "cuboid-volume" and d["scene"]["kind"] == "solid-net"
        assert d["scene"]["points"] == []
        assert d["scene"]["param"]["answer"] == p["V"]
        assert d["answer"]["V"] == p["a"] * p["b"] * p["c"]
        assert d["scene"]["known"] == {"a": p["a"], "b": p["b"], "c": p["c"], "S": p["S"]}


if __name__ == "__main__":
    test_area_parallelogram_schema()
    test_area_triangle_schema()
    test_area_trapezoid_schema()
    test_area_circle_schema()
    test_composite_area_schema()
    test_grid_count_schema()
    test_three_view_schema()
    test_transform_symmetry_schema()
    test_cuboid_volume_schema()
    print("OK  9 题型 schema 自检全部通过")
