# -*- coding: utf-8 -*-
"""七题型 schema 自检：结构、关键字段、关系。"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

import builders          # noqa: E402
import generators as gn  # noqa: E402

TOP_KEYS = {"type", "lesson", "scene", "answer", "readouts", "status", "steps", "ui"}
LESSON_KEYS = {"title", "problem", "hint"}
STATUS_PHASES = {"before", "at", "after"}
SCENE_KINDS = {"road", "circular", "bar-model", "swap", "interval", "progress",
               "sequence", "train", "phalanx", "clock", "venn",
               "link-graph", "logic-table", "timeline", "matchup", "balance",
               "geodrag", "circle"}


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


def _assert_motion(d):
    mo = d["scene"]["motion"]
    assert d["diagram"]["kind"] == "st-graph"
    assert mo["carA"]["x0"] is not None and mo["carB"]["x0"] is not None
    assert d["answer"]["tMeet"] == d["scene"]["param"]["max"] - 5


def _assert_bar(d):
    assert d["scene"]["kind"] == "bar-model"
    assert "diagram" not in d or d.get("diagram") is None or d["diagram"] is None
    assert d["scene"]["bars"][0]["var"] == "a" and d["scene"]["bars"][1]["var"] == "b"
    assert d["scene"]["param"]["step"] == 1
    assert d["scene"]["param"]["max"] >= d["answer"]["small"] > d["scene"]["param"]["min"]
    assert d["answer"]["small"] == d["scene"]["scale"] - d["answer"]["big"]
    assert isinstance(d["answer"]["small"], int) and isinstance(d["answer"]["big"], int)


def test_pursue_schema():
    rng = random.Random(10)
    for _ in range(100):
        d = builders.build_pursue(gn.gen_pursue(rng))
        _assert_schema(d); _assert_motion(d)
        assert d["type"] == "pursue" and d["scene"]["kind"] == "road"
        assert d["scene"]["motion"]["direction"] == "same"
        assert d["scene"]["motion"]["carB"]["x0"] == d["answer"]["gap"]
        assert d["diagram"]["meet"]["mode"] == "cross"


def test_meet_schema():
    rng = random.Random(11)
    for _ in range(100):
        d = builders.build_meet(gn.gen_meet(rng))
        _assert_schema(d); _assert_motion(d)
        assert d["type"] == "meet" and d["scene"]["motion"]["direction"] == "opposite"
        assert d["scene"]["motion"]["carB"]["x0"] == d["answer"]["total"]
        assert d["diagram"]["lines"][1]["k"] == -d["scene"]["motion"]["carB"]["v"]


def test_circular_schema():
    rng = random.Random(12)
    for _ in range(100):
        d = builders.build_circular(gn.gen_circular_same(rng), "same")
        _assert_schema(d); _assert_motion(d)
        assert d["type"] == "circular-same" and d["scene"]["kind"] == "circular"
        assert d["scene"]["motion"]["lap"] == d["answer"]["gap"]
        assert d["diagram"]["meet"]["mode"] == "lap"
        assert "laps" in {r["kind"] for r in d["readouts"]}
    for _ in range(100):
        d = builders.build_circular(gn.gen_circular_opp(rng), "opposite")
        _assert_schema(d); _assert_motion(d)
        assert d["type"] == "circular-opp"
        assert d["scene"]["motion"]["carB"]["x0"] == d["answer"]["total"]


def test_sum_diff_schema():
    rng = random.Random(13)
    for _ in range(100):
        d = builders.build_sum_diff(gn.gen_sum_diff(rng))
        _assert_schema(d); _assert_bar(d)
        assert d["type"] == "sum-diff"
        assert d["scene"]["rel"]["bigOf"] == "sum-minus-a"
        assert d["scene"]["param"]["max"] == d["scene"]["rel"]["sum"] - 1


def test_sum_multiple_schema():
    rng = random.Random(14)
    for _ in range(100):
        d = builders.build_sum_multiple(gn.gen_sum_multiple(rng))
        _assert_schema(d); _assert_bar(d)
        assert d["type"] == "sum-multiple"
        assert d["scene"]["rel"]["bigOf"] == "n-times-a"
        assert d["answer"]["big"] == d["scene"]["rel"]["n"] * d["answer"]["small"]


def test_diff_multiple_schema():
    rng = random.Random(15)
    for _ in range(100):
        d = builders.build_diff_multiple(gn.gen_diff_multiple(rng))
        _assert_schema(d); _assert_bar(d)
        assert d["type"] == "diff-multiple"
        assert d["scene"]["rel"]["bigOf"] == "n-times-a"
        assert d["answer"]["big"] == d["scene"]["rel"]["n"] * d["answer"]["small"]


def test_profit_loss_schema():
    rng = random.Random(21)
    for _ in range(100):
        p = gn.gen_profit_loss(rng)
        d = builders.build_profit_loss(p)
        _assert_schema(d)
        assert d["type"] == "profit-loss" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["n"]
        assert d["answer"] == {"n": p["n"], "total": p["total"]}
        assert set(d["scene"]["known"]) == {"a", "c", "b", "d", "total"}


def test_age_schema():
    rng = random.Random(22)
    for _ in range(100):
        p = gn.gen_age(rng)
        d = builders.build_age(p)
        _assert_schema(d)
        assert d["type"] == "age" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["t"]
        assert d["answer"] == {"t": p["t"]}


def test_average_schema():
    rng = random.Random(23)
    for _ in range(100):
        p = gn.gen_average(rng)
        d = builders.build_average(p)
        _assert_schema(d)
        assert d["type"] == "average" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["z"]
        assert d["scene"]["ref"]["expr"] == "A"
        assert d["answer"] == {"z": p["z"]}


def test_chicken_rabbit_schema():
    rng = random.Random(24)
    for _ in range(100):
        p = gn.gen_chicken_rabbit(rng)
        d = builders.build_chicken_rabbit(p)
        _assert_schema(d)
        assert d["type"] == "chicken-rabbit" and d["scene"]["kind"] == "swap"
        assert d["scene"]["param"]["answer"] == p["c"]
        assert d["answer"] == {"c": p["c"], "r": p["r"]}


def test_plant_schema():
    rng = random.Random(25)
    for _ in range(100):
        p = gn.gen_plant(rng)
        d = builders.build_plant(p)
        _assert_schema(d)
        assert d["type"] == "plant" and d["scene"]["kind"] == "interval"
        assert d["scene"]["param"]["answer"] == p["k"]
        assert d["answer"] == {"k": p["k"], "n": p["n"]}


def test_work_schema():
    rng = random.Random(26)
    for _ in range(100):
        p = gn.gen_work(rng)
        d = builders.build_work(p)
        _assert_schema(d)
        assert d["type"] == "work" and d["scene"]["kind"] == "progress"
        assert d["scene"]["param"]["answer"] == p["t"]
        assert d["answer"] == {"t": p["t"]}


def test_cycle_schema():
    rng = random.Random(27)
    for _ in range(100):
        p = gn.gen_cycle(rng)
        d = builders.build_cycle(p)
        _assert_schema(d)
        assert d["type"] == "cycle" and d["scene"]["kind"] == "sequence"
        assert d["scene"]["param"]["answer"] == p["N"]
        assert d["answer"]["N"] == p["N"] and d["answer"]["r"] == p["r"]


def test_unit_schema():
    rng = random.Random(28)
    for _ in range(100):
        p = gn.gen_unit(rng)
        d = builders.build_unit(p)
        _assert_schema(d)
        assert d["type"] == "unit" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["u"]
        assert d["answer"] == {"u": p["u"], "ans": p["ans"]}


def test_aggregate_schema():
    rng = random.Random(29)
    for _ in range(100):
        p = gn.gen_aggregate(rng)
        d = builders.build_aggregate(p)
        _assert_schema(d)
        assert d["type"] == "aggregate" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["n"]
        assert d["answer"] == {"n": p["n"], "b": p["b"]}


def test_boat_schema():
    rng = random.Random(30)
    for _ in range(100):
        p = gn.gen_boat(rng)
        d = builders.build_boat(p)
        _assert_schema(d)
        assert d["type"] == "boat" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["u"]
        assert d["scene"]["ref"]["expr"] == "down"
        assert d["answer"] == {"u": p["u"], "v": p["v"]}


def test_train_schema():
    rng = random.Random(31)
    for _ in range(100):
        p = gn.gen_train(rng)
        d = builders.build_train(p)
        _assert_schema(d)
        assert d["type"] == "train" and d["scene"]["kind"] == "train"
        assert d["scene"]["param"]["answer"] == p["t"]
        assert d["answer"] == {"t": p["t"]}


def test_avgspeed_schema():
    rng = random.Random(32)
    for _ in range(100):
        p = gn.gen_avgspeed(rng)
        d = builders.build_avgspeed(p)
        _assert_schema(d)
        assert d["type"] == "avgspeed" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["avg"]
        assert d["answer"] == {"avg": p["avg"]}


# ---- A 组：分数 / 百分数 / 比与比例 / 浓度 / 行程扩展 / 还原 / 平均数变体 / 间隔变体 ----

def test_fraction_part_schema():
    rng = random.Random(41)
    for _ in range(100):
        p = gn.gen_fraction_part(rng)
        d = builders.build_fraction_part(p)
        _assert_schema(d)
        assert d["type"] == "fraction-part" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["part"]
        assert d["answer"] == {"part": p["part"]}
        assert d["scene"]["bars"][1]["var"] == "p"


def test_fraction_whole_schema():
    rng = random.Random(42)
    for _ in range(100):
        p = gn.gen_fraction_whole(rng)
        d = builders.build_fraction_whole(p)
        _assert_schema(d)
        assert d["type"] == "fraction-whole" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["W"]
        assert d["answer"] == {"W": p["W"]}
        assert d["scene"]["ref"]["expr"] == "part"


def test_fraction_ratio_schema():
    rng = random.Random(43)
    for _ in range(100):
        p = gn.gen_fraction_ratio(rng)
        d = builders.build_fraction_ratio(p)
        _assert_schema(d)
        assert d["type"] == "fraction-ratio" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["n"]
        assert d["answer"] == {"n": p["n"], "d": p["d"]}


def test_discount_schema():
    rng = random.Random(44)
    for _ in range(100):
        p = gn.gen_discount(rng)
        d = builders.build_discount(p)
        _assert_schema(d)
        assert d["type"] == "discount" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["price"]
        assert d["answer"] == {"price": p["price"]}


def test_percent_change_schema():
    rng = random.Random(45)
    for _ in range(100):
        p = gn.gen_percent_change(rng)
        d = builders.build_percent_change(p)
        _assert_schema(d)
        assert d["type"] == "percent-change" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["price"]
        assert d["answer"] == {"price": p["price"]}


def test_ratio_share_schema():
    rng = random.Random(46)
    for _ in range(100):
        p = gn.gen_ratio_share(rng)
        d = builders.build_ratio_share(p)
        _assert_schema(d)
        assert d["type"] == "ratio-share" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["k"]
        assert d["answer"] == {"A": p["A"], "B": p["B"]}


def test_ratio_scale_schema():
    rng = random.Random(47)
    for _ in range(100):
        p = gn.gen_ratio_scale(rng)
        d = builders.build_ratio_scale(p)
        _assert_schema(d)
        assert d["type"] == "ratio-scale" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["real"]
        assert d["answer"] == {"real": p["real"]}


def test_concentration_schema():
    rng = random.Random(48)
    for _ in range(100):
        p = gn.gen_concentration(rng)
        d = builders.build_concentration(p)
        _assert_schema(d)
        assert d["type"] == "concentration" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["salt"]
        assert d["answer"] == {"salt": p["salt"]}


def test_midpoint_meet_schema():
    rng = random.Random(49)
    for _ in range(100):
        p = gn.gen_midpoint_meet(rng)
        d = builders.build_midpoint_meet(p)
        _assert_schema(d)
        assert d["type"] == "midpoint-meet" and d["scene"]["kind"] == "road"
        assert d["scene"]["motion"]["direction"] == "opposite"
        assert d["scene"]["motion"]["carB"]["x0"] == p["T"]
        assert d["scene"]["motion"]["midpoint"] == p["T"] / 2
        assert d["scene"]["param"]["answer"] == p["t"]
        assert d["diagram"]["kind"] == "st-graph"
        assert d["answer"]["t"] == d["scene"]["param"]["max"] - 5


def test_restore_schema():
    rng = random.Random(50)
    for _ in range(100):
        p = gn.gen_restore(rng)
        d = builders.build_restore(p)
        _assert_schema(d)
        assert d["type"] == "restore" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["W"]
        assert d["answer"] == {"W": p["W"]}
        assert len(d["scene"]["bars"]) == 3


def test_average_move_schema():
    rng = random.Random(51)
    for _ in range(100):
        p = gn.gen_average_move(rng)
        d = builders.build_average_move(p)
        _assert_schema(d)
        assert d["type"] == "average-move" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["give"]
        assert d["answer"] == {"give": p["give"]}


def test_stairs_schema():
    rng = random.Random(52)
    for _ in range(100):
        p = gn.gen_stairs(rng)
        d = builders.build_stairs(p)
        _assert_schema(d)
        assert d["type"] == "stairs" and d["scene"]["kind"] == "interval"
        assert d["scene"]["param"]["answer"] == p["total"]
        assert d["answer"] == {"total": p["total"]}
        assert set(d["scene"]["known"]) >= {"n", "t", "total", "unit", "item", "segWord"}


# ---- B 组：牛吃草 / 方阵 / 抽屉 / 时钟 / 消去法 / 等差数列 / 最优化 / 页码 / 三数和差倍 ----

def test_cows_schema():
    rng = random.Random(53)
    for _ in range(100):
        p = gn.gen_cows(rng)
        d = builders.build_cows(p)
        _assert_schema(d)
        assert d["type"] == "cows" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["t"]
        assert d["answer"] == {"t": p["t"], "G": p["G"]}


def test_phalanx_schema():
    rng = random.Random(54)
    for _ in range(100):
        p = gn.gen_phalanx(rng)
        d = builders.build_phalanx(p)
        _assert_schema(d)
        assert d["type"] == "phalanx" and d["scene"]["kind"] == "phalanx"
        assert d["scene"]["param"]["answer"] == p["n"]
        assert d["answer"] == {"n": p["n"], "total": p["total"], "outer": p["outer"]}


def test_pigeonhole_schema():
    rng = random.Random(55)
    for _ in range(100):
        p = gn.gen_pigeonhole(rng)
        d = builders.build_pigeonhole(p)
        _assert_schema(d)
        assert d["type"] == "pigeonhole" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["least"]
        assert d["answer"] == {"least": p["least"]}


def test_clock_schema():
    rng = random.Random(56)
    for _ in range(100):
        p = gn.gen_clock(rng)
        d = builders.build_clock(p)
        _assert_schema(d)
        assert d["type"] == "clock" and d["scene"]["kind"] == "clock"
        assert d["scene"]["param"]["answer"] == p["angle"]
        assert d["answer"] == {"angle": p["angle"]}


def test_elimination_schema():
    rng = random.Random(57)
    for _ in range(100):
        p = gn.gen_elimination(rng)
        d = builders.build_elimination(p)
        _assert_schema(d)
        assert d["type"] == "elimination" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["x"]
        assert d["answer"] == {"x": p["x"], "y": p["y"], "z": p["z"]}
        assert len(d["scene"]["bars"]) == 3


def test_arithmetic_seq_schema():
    rng = random.Random(58)
    for _ in range(100):
        p = gn.gen_arithmetic_seq(rng)
        d = builders.build_arithmetic_seq(p)
        _assert_schema(d)
        assert d["type"] == "arithmetic-seq" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["an"]
        assert d["answer"] == {"an": p["an"]}


def test_optimize_schema():
    rng = random.Random(59)
    for _ in range(100):
        p = gn.gen_optimize(rng)
        d = builders.build_optimize(p)
        _assert_schema(d)
        assert d["type"] == "optimize" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["optK"]
        assert d["scene"]["ref"]["expr"] == "minCost"
        assert d["answer"] == {"optK": p["optK"], "minCost": p["minCost"]}


def test_page_digit_schema():
    rng = random.Random(60)
    for _ in range(100):
        p = gn.gen_page_digit(rng)
        d = builders.build_page_digit(p)
        _assert_schema(d)
        assert d["type"] == "page-digit" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["n"]
        assert d["scene"]["ref"]["expr"] == "given"
        assert d["answer"] == {"n": p["n"], "total": p["total"]}


def test_sum_diff_three_schema():
    rng = random.Random(61)
    for _ in range(100):
        p = gn.gen_sum_diff_three(rng)
        d = builders.build_sum_diff_three(p)
        _assert_schema(d)
        assert d["type"] == "sum-diff-three" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["a"]
        assert d["answer"] == {"a": p["a"], "b": p["b"], "c": p["c"]}
        assert len(d["scene"]["bars"]) == 3


# ---- C 组：盈亏两盈/两亏 + 植树一端/两端不栽/环形 ----

def test_profit_loss_two_gain_schema():
    rng = random.Random(62)
    for _ in range(100):
        p = gn.gen_profit_loss_two_gain(rng)
        d = builders.build_profit_loss_two_gain(p)
        _assert_schema(d)
        assert d["type"] == "profit-loss-two-gain" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["n"]
        assert d["answer"] == {"n": p["n"], "total": p["total"]}


def test_profit_loss_two_loss_schema():
    rng = random.Random(63)
    for _ in range(100):
        p = gn.gen_profit_loss_two_loss(rng)
        d = builders.build_profit_loss_two_loss(p)
        _assert_schema(d)
        assert d["type"] == "profit-loss-two-loss" and d["scene"]["kind"] == "bar-model"
        assert d["scene"]["param"]["answer"] == p["n"]
        assert d["answer"] == {"n": p["n"], "total": p["total"]}


def test_plant_one_schema():
    rng = random.Random(64)
    for _ in range(100):
        p = gn.gen_plant_one(rng)
        d = builders.build_plant_one(p)
        _assert_schema(d)
        assert d["type"] == "plant-one" and d["scene"]["kind"] == "interval"
        assert d["scene"]["param"]["answer"] == p["k"]
        assert d["scene"]["known"]["mode"] == "one"
        assert d["answer"] == {"k": p["k"], "n": p["n"]}


def test_plant_none_schema():
    rng = random.Random(65)
    for _ in range(100):
        p = gn.gen_plant_none(rng)
        d = builders.build_plant_none(p)
        _assert_schema(d)
        assert d["type"] == "plant-none" and d["scene"]["kind"] == "interval"
        assert d["scene"]["param"]["answer"] == p["k"]
        assert d["scene"]["known"]["mode"] == "none"
        assert d["answer"] == {"k": p["k"], "n": p["n"]}


def test_plant_ring_schema():
    rng = random.Random(66)
    for _ in range(100):
        p = gn.gen_plant_ring(rng)
        d = builders.build_plant_ring(p)
        _assert_schema(d)
        assert d["type"] == "plant-ring" and d["scene"]["kind"] == "interval"
        assert d["scene"]["param"]["answer"] == p["k"]
        assert d["scene"]["known"]["mode"] == "ring"
        assert d["answer"] == {"k": p["k"], "n": p["n"]}


def test_overlap_venn_schema():
    rng = random.Random(67)
    for _ in range(100):
        p = gn.gen_overlap_venn(rng)
        d = builders.build_overlap_venn(p)
        _assert_schema(d)
        assert d["type"] == "overlap-venn" and d["scene"]["kind"] == "venn"
        # 好数：答案量 c 恒整数，且 c = X + Y − T
        assert isinstance(p["c"], int)
        assert p["c"] == p["X"] + p["Y"] - p["T"]
        assert d["scene"]["param"]["answer"] == p["c"]
        assert d["scene"]["dragToT"] == "H"
        h = d["scene"]["points"][0]
        assert h["snap"] == "grid" and h["constraint"] == "h-line"
        assert h["min"] == 1 and h["max"] == min(p["X"], p["Y"]) - 1
        assert d["answer"] == {"c": p["c"], "X": p["X"], "Y": p["Y"], "T": p["T"]}


def test_match_count_schema():
    rng = random.Random(68)
    for _ in range(100):
        p = gn.gen_match_count(rng)
        d = builders.build_match_count(p)
        _assert_schema(d)
        assert d["type"] == "match-count" and d["scene"]["kind"] == "link-graph"
        assert p["total"] == p["m"] * p["n"]
        assert d["scene"]["param"]["answer"] == p["total"]
        assert d["scene"]["known"]["m"] == p["m"] and d["scene"]["known"]["n"] == p["n"]
        assert d["answer"] == {"total": p["total"]}


def test_logic_table_schema():
    rng = random.Random(69)
    for _ in range(100):
        p = gn.gen_logic_table(rng)
        d = builders.build_logic_table(p)
        _assert_schema(d)
        assert d["type"] == "logic-table" and d["scene"]["kind"] == "logic-table"
        assert len(d["scene"]["points"]) == 3
        for i, pt in enumerate(d["scene"]["points"]):
            assert pt["snap"] == "grid" and pt["constraint"] == "h-line"
            assert pt["ax"] == p["perm"][i] + 1
        assert d["scene"]["param"]["answer"] == 3


def test_pancake_schema():
    rng = random.Random(70)
    for _ in range(100):
        p = gn.gen_pancake(rng)
        d = builders.build_pancake(p)
        _assert_schema(d)
        assert d["type"] == "pancake" and d["scene"]["kind"] == "timeline"
        assert p["n"] in (3, 5) and p["k"] == 2
        assert p["total"] == ((2 * p["n"] + p["k"] - 1) // p["k"]) * p["t"]
        assert d["scene"]["param"]["answer"] == p["total"]
        assert d["answer"] == {"total": p["total"]}


def test_tianji_schema():
    rng = random.Random(71)
    for _ in range(100):
        p = gn.gen_tianji(rng)
        d = builders.build_tianji(p)
        _assert_schema(d)
        assert d["type"] == "tianji" and d["scene"]["kind"] == "matchup"
        assert len(d["scene"]["points"]) == 3
        # 田忌上/中/下三匹马各对位：上→中(胜)、中→下(胜)、下→上(负) = 赢 2 局
        assert d["answer"] == {"wins": 2}
        for pt in d["scene"]["points"]:
            assert pt["snap"] == "grid" and 1 <= pt["ax"] <= 3


def test_fraction_more_less_schema():
    rng = random.Random(72)
    for _ in range(100):
        p = gn.gen_fraction_more_less(rng)
        d = builders.build_fraction_more_less(p)
        _assert_schema(d)
        assert d["type"] == "fraction-more-less" and d["scene"]["kind"] == "bar-model"
        assert p["B"] == p["k"] * p["m"]
        assert p["A"] == (p["B"] + p["m"] if p["mode"] == "多" else p["B"] - p["m"])
        assert d["scene"]["param"]["answer"] == p["A"]
        assert d["answer"] == {"A": p["A"], "D": p["D"], "k": p["k"]}


def test_interest_schema():
    rng = random.Random(73)
    for _ in range(100):
        p = gn.gen_interest(rng)
        d = builders.build_interest(p)
        _assert_schema(d)
        assert d["type"] == "interest" and d["scene"]["kind"] == "bar-model"
        assert p["interest"] == p["m"] * p["r"] * p["n"]
        assert d["scene"]["param"]["answer"] == p["interest"]
        assert d["answer"] == {"interest": p["interest"]}


def test_plant_two_sides_schema():
    rng = random.Random(74)
    for _ in range(100):
        p = gn.gen_plant_two_sides(rng)
        d = builders.build_plant_two_sides(p)
        _assert_schema(d)
        assert d["type"] == "plant-two-sides" and d["scene"]["kind"] == "interval"
        assert p["D"] == p["n"] * p["d"] and p["k"] == p["n"] + 1
        assert p["total"] == 2 * p["k"]
        assert d["scene"]["known"]["mode"] == "two-sides"
        assert d["scene"]["param"]["answer"] == p["k"]
        assert d["answer"] == {"k": p["k"], "n": p["n"], "total": p["total"]}


def test_equation_balance_schema():
    rng = random.Random(75)
    for _ in range(100):
        p = gn.gen_equation_balance(rng)
        d = builders.build_equation_balance(p)
        _assert_schema(d)
        assert d["type"] == "equation-balance" and d["scene"]["kind"] == "balance"
        assert p["right"] == p["a"] * p["x"] + p["b"]
        assert d["scene"]["dragToT"] == "xW"
        assert d["scene"]["param"]["answer"] == p["x"]
        pt = d["scene"]["points"][0]
        assert pt["snap"] == "grid" and pt["constraint"] == "h-line"
        assert pt["ax"] == p["x"]


def test_triangle_equal_schema():
    rng = random.Random(76)
    for _ in range(100):
        p = gn.gen_triangle_equal(rng)
        d = builders.build_triangle_equal(p)
        _assert_schema(d)
        assert d["type"] == "triangle-equal" and d["scene"]["kind"] == "geodrag"
        assert d["scene"]["target"] == {"name": "C", "x": p["mid"], "y": p["h"]}
        assert d["scene"]["dragToT"] == "C"
        assert d["scene"]["param"]["answer"] == p["mid"]
        c = d["scene"]["points"][2]
        assert c["name"] == "C" and c["snap"] == "grid" and c["constraint"] == "h-line"
        assert c["min"] == 0 and c["max"] == p["b"]
        assert d["scene"]["poly"] == ["A", "B", "C"]
        assert d["answer"]["area"] == p["area"]
        assert isinstance(p["area"], int)


def test_para_equal_schema():
    rng = random.Random(77)
    for _ in range(100):
        p = gn.gen_para_equal(rng)
        d = builders.build_para_equal(p)
        _assert_schema(d)
        assert d["type"] == "para-equal" and d["scene"]["kind"] == "geodrag"
        assert d["scene"]["target"] == {"name": "D", "x": 2, "y": p["h"]}
        assert d["scene"]["dragToT"] == "D"
        assert d["scene"]["param"]["answer"] == 2
        dd = d["scene"]["points"][2]
        assert dd["name"] == "D" and dd["snap"] == "grid" and dd["constraint"] == "h-line"
        c = d["scene"]["points"][3]
        assert c["name"] == "C" and c["fixed"] and c["depend"] == {"of": "D", "dx": p["b"], "dy": 0}
        assert d["scene"]["poly"] == ["A", "B", "C", "D"]
        assert d["answer"]["area"] == p["area"]


def test_tri_height_schema():
    rng = random.Random(78)
    for _ in range(100):
        p = gn.gen_tri_height(rng)
        d = builders.build_tri_height(p)
        _assert_schema(d)
        assert d["type"] == "tri-height" and d["scene"]["kind"] == "geodrag"
        assert d["scene"]["target"] == {"name": "C", "x": p["mid"], "y": p["h"]}
        assert d["scene"]["dragToT"] == "C"
        assert d["scene"]["param"]["answer"] == p["h"]
        c = d["scene"]["points"][2]
        assert c["name"] == "C" and c["snap"] == "grid" and c["constraint"] == "v-line"
        assert d["scene"]["poly"] == ["A", "B", "C"]
        assert d["answer"]["h"] == p["h"] and d["answer"]["area"] == p["area"]


def test_trapezoid_schema():
    rng = random.Random(79)
    for _ in range(100):
        p = gn.gen_trapezoid(rng)
        d = builders.build_trapezoid(p)
        _assert_schema(d)
        assert d["type"] == "trapezoid" and d["scene"]["kind"] == "geodrag"
        assert d["scene"]["target"] == {"name": "D", "x": p["mid"], "y": p["h"]}
        assert d["scene"]["dragToT"] == "D"
        assert d["scene"]["param"]["answer"] == p["mid"]
        dd = d["scene"]["points"][2]
        assert dd["name"] == "D" and dd["snap"] == "grid" and dd["constraint"] == "h-line"
        c = d["scene"]["points"][3]
        assert c["name"] == "C" and c["fixed"] and c["depend"] == {"of": "D", "dx": p["u"], "dy": 0}
        assert d["scene"]["poly"] == ["A", "B", "C", "D"]
        assert d["answer"]["area"] == p["area"]


def test_recompose_schema():
    rng = random.Random(80)
    for _ in range(100):
        p = gn.gen_recompose(rng)
        d = builders.build_recompose(p)
        _assert_schema(d)
        assert d["type"] == "recompose" and d["scene"]["kind"] == "geodrag"
        assert d["scene"]["target"] == {"name": "G", "x": p["b"], "y": 0}
        assert d["scene"]["dragToT"] == "G"
        assert d["scene"]["param"]["answer"] == p["b"]
        g = d["scene"]["points"][5]
        assert g["name"] == "G" and g["snap"] == "grid" and g["constraint"] == "h-line"
        assert d["scene"]["poly"] == ["E", "B", "C", "D"]
        ex = d["scene"]["extra"][0]
        assert ex["poly"] == ["G", "G1", "G2"]
        g1 = d["scene"]["points"][6]
        g2 = d["scene"]["points"][7]
        assert g1["depend"] == {"of": "G", "dx": p["o"], "dy": 0} and g1["hidden"]
        assert g2["depend"] == {"of": "G", "dx": p["o"], "dy": p["h"]} and g2["hidden"]
        assert d["answer"]["area"] == p["area"]


def test_circle_schema():
    rng = random.Random(81)
    for _ in range(100):
        p = gn.gen_circle(rng)
        d = builders.build_circle(p)
        _assert_schema(d)
        assert d["type"] == "circle" and d["scene"]["kind"] == "circle"
        assert d["scene"]["param"]["answer"] == p["r"]
        assert d["scene"]["world"]["xMax"] == max(2 * p["r"] + 4, p["C"] + 2)
        assert d["scene"]["world"]["yMax"] == 2 * p["r"] + 6
        assert d["answer"]["C"] == p["C"] and d["answer"]["d"] == p["d"]


def test_circle_area_schema():
    rng = random.Random(82)
    for _ in range(100):
        p = gn.gen_circle_area(rng)
        d = builders.build_circle_area(p)
        _assert_schema(d)
        assert d["type"] == "circle-area" and d["scene"]["kind"] == "circle"
        assert d["scene"]["mode"] == "area"
        assert d["scene"]["param"]["answer"] == p["r"]
        assert d["scene"]["world"]["xMax"] == 5 * p["r"] + 5
        assert d["answer"]["S"] == p["S"] and d["answer"]["d"] == p["d"]


def test_semicircle_schema():
    rng = random.Random(83)
    for _ in range(100):
        p = gn.gen_semicircle(rng)
        d = builders.build_semicircle(p)
        _assert_schema(d)
        assert d["type"] == "semicircle" and d["scene"]["kind"] == "circle"
        assert d["scene"]["mode"] == "semicircle"
        assert d["scene"]["param"]["answer"] == p["r"]
        assert d["scene"]["world"]["xMax"] == 5 * p["r"] + 2
        assert d["answer"]["C"] == p["C"] and d["answer"]["arc"] == p["arc"]


if __name__ == "__main__":
    test_pursue_schema()
    test_meet_schema()
    test_circular_schema()
    test_sum_diff_schema()
    test_sum_multiple_schema()
    test_diff_multiple_schema()
    test_profit_loss_schema()
    test_age_schema()
    test_average_schema()
    test_chicken_rabbit_schema()
    test_plant_schema()
    test_work_schema()
    test_cycle_schema()
    test_unit_schema()
    test_aggregate_schema()
    test_boat_schema()
    test_train_schema()
    test_avgspeed_schema()
    test_fraction_part_schema()
    test_fraction_whole_schema()
    test_fraction_ratio_schema()
    test_discount_schema()
    test_percent_change_schema()
    test_ratio_share_schema()
    test_ratio_scale_schema()
    test_concentration_schema()
    test_midpoint_meet_schema()
    test_restore_schema()
    test_average_move_schema()
    test_stairs_schema()
    test_cows_schema()
    test_phalanx_schema()
    test_pigeonhole_schema()
    test_clock_schema()
    test_elimination_schema()
    test_arithmetic_seq_schema()
    test_optimize_schema()
    test_page_digit_schema()
    test_sum_diff_three_schema()
    test_profit_loss_two_gain_schema()
    test_profit_loss_two_loss_schema()
    test_plant_one_schema()
    test_plant_none_schema()
    test_plant_ring_schema()
    test_overlap_venn_schema()
    test_match_count_schema()
    test_logic_table_schema()
    test_pancake_schema()
    test_tianji_schema()
    test_fraction_more_less_schema()
    test_interest_schema()
    test_plant_two_sides_schema()
    test_equation_balance_schema()
    test_triangle_equal_schema()
    test_para_equal_schema()
    test_tri_height_schema()
    test_trapezoid_schema()
    test_recompose_schema()
    test_circle_schema()
    test_circle_area_schema()
    test_semicircle_schema()
    print("OK  62 题型 schema 自检全部通过")
