# -*- coding: utf-8 -*-
"""三题型 schema 自检：结构、关键字段、物理关系。"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

import builders           # noqa: E402
import good_numbers as gn  # noqa: E402

TOP_KEYS = {"type", "lesson", "motion", "answer", "graph", "readouts", "status", "steps", "ui"}
LESSON_KEYS = {"title", "problem", "hint"}
STATUS_PHASES = {"before", "at", "after"}


def _assert_schema(d):
    assert TOP_KEYS.issubset(d.keys()), f"缺顶层键: {TOP_KEYS - d.keys()}"
    assert LESSON_KEYS.issubset(d["lesson"].keys())
    for ph in STATUS_PHASES:
        assert "text" in d["status"][ph] and "color" in d["status"][ph]
    assert d["steps"], "解题步骤为空"
    for s in d["steps"]:
        assert "title" in s and "content" in s
    assert d["motion"]["tMax"] == d["answer"]["tMeet"] + 5
    for car in ("carA", "carB"):
        c = d["motion"][car]
        for k in ("name", "color", "x0", "v"):
            assert k in c
    kinds = {r["kind"] for r in d["readouts"]}
    assert {"expr", "gap", "answer"}.issubset(kinds)


def test_pursue_schema():
    rng = random.Random(10)
    for _ in range(200):
        p = gn.gen_pursue(rng)
        d = builders.build_pursue(p)
        _assert_schema(d)
        assert d["type"] == "pursue"
        assert d["motion"]["kind"] == "linear" and d["motion"]["direction"] == "same"
        assert d["motion"]["carB"]["x0"] == p["gap"]
        assert d["graph"]["lines"][1]["k"] == p["vB"]
        assert d["graph"]["lines"][0]["k"] == p["vA"]
        assert d["graph"]["meet"]["mode"] == "cross"
        assert d["answer"]["xMeet"] == p["xMeet"]


def test_meet_schema():
    rng = random.Random(11)
    for _ in range(200):
        p = gn.gen_meet(rng)
        d = builders.build_meet(p)
        _assert_schema(d)
        assert d["type"] == "meet"
        assert d["motion"]["direction"] == "opposite"
        assert d["motion"]["carB"]["x0"] == p["total"]
        assert d["graph"]["lines"][1]["k"] == -p["vB"]
        assert d["answer"]["xMeet"] == p["xMeet"]


def test_circular_schema():
    rng = random.Random(12)
    for _ in range(200):
        p = gn.gen_circular_same(rng)
        d = builders.build_circular(p, "same")
        _assert_schema(d)
        assert d["type"] == "circular-same"
        assert d["motion"]["kind"] == "circular"
        assert d["motion"]["lap"] == p["L"]
        assert d["motion"]["carB"]["x0"] == 0
        assert d["graph"]["meet"]["mode"] == "lap"
        assert d["graph"]["laps"], "环形追及应含圈线"
        kinds = {r["kind"] for r in d["readouts"]}
        assert "laps" in kinds
    for _ in range(200):
        p = gn.gen_circular_opp(rng)
        d = builders.build_circular(p, "opposite")
        _assert_schema(d)
        assert d["type"] == "circular-opp"
        assert d["motion"]["carB"]["x0"] == p["L"]
        assert d["graph"]["lines"][1]["k"] == -p["vB"]
        assert d["graph"]["meet"]["mode"] == "cross"


if __name__ == "__main__":
    test_pursue_schema()
    test_meet_schema()
    test_circular_schema()
    print("OK  三题型 schema 自检全部通过")
