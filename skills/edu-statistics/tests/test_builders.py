# -*- coding: utf-8 -*-
"""统计题型 schema 自检：结构、关键字段、关系。"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

import builders          # noqa: E402
import generators as gn  # noqa: E402

TOP_KEYS = {"type", "lesson", "scene", "answer", "readouts", "status", "steps", "ui"}
LESSON_KEYS = {"title", "problem", "hint"}
STATUS_PHASES = {"before", "at", "after"}
SCENE_KINDS = {"chart", "tree"}


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


def test_stat_chart_schema():
    rng = random.Random(10)
    for _ in range(100):
        p = gn.gen_stat_chart(rng)
        d = builders.build_stat_chart(p)
        _assert_schema(d)
        assert d["type"] == "stat-chart" and d["scene"]["kind"] == "chart"
        assert d["scene"]["param"]["answer"] == p["d"]
        assert d["answer"] == {"d": p["d"], "T": p["T"]}
        bar = d["scene"]["points"][0]
        assert bar["name"] == "barD" and bar["snap"] == "grid" and bar["constraint"] == "v-line"
        assert bar["ymin"] == 0 and bar["ymax"] == p["maxBar"]
        assert d["scene"]["dragToT"] == "barD" and d["scene"]["dragAxis"] == "y"
        fill = [c for c in d["scene"]["cats"] if c.get("fill")]
        assert len(fill) == 1 and fill[0]["name"] == "跑步"
        assert d["scene"]["known"] == {"a": p["a"], "b": p["b"], "c": p["c"],
                                       "T": p["T"], "maxBar": p["maxBar"]}


def test_probability_tree_schema():
    rng = random.Random(11)
    for _ in range(100):
        p = gn.gen_probability_tree(rng)
        d = builders.build_probability_tree(p)
        _assert_schema(d)
        assert d["type"] == "probability-tree" and d["scene"]["kind"] == "tree"
        assert d["scene"]["param"]["answer"] == p["fav"]
        assert d["scene"]["param"]["min"] == 1 and d["scene"]["param"]["max"] == p["total"]
        assert d["answer"] == {"fav": p["fav"], "total": p["total"]}
        cnt = d["scene"]["points"][0]
        assert cnt["name"] == "cnt" and cnt["snap"] == "grid" and cnt["constraint"] == "h-line"
        assert cnt["min"] == 1 and cnt["max"] == p["total"]
        assert d["scene"]["dragToT"] == "cnt" and d["scene"]["dragAxis"] == "x"
        assert d["scene"]["known"]["rule"] == p["rule"]
        assert len(d["scene"]["known"]["colorsA"]) == p["m"]
        assert len(d["scene"]["known"]["colorsB"]) == p["n"]


if __name__ == "__main__":
    test_stat_chart_schema()
    test_probability_tree_schema()
    print("OK  2 题型 schema 自检全部通过")
