# -*- coding: utf-8 -*-
"""好数生成器单测：1000 次抽样断言答案恒整数、关系恒成立。"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

import generators as gn  # noqa: E402

N = 1000


def test_pursue():
    rng = random.Random(1)
    for _ in range(N):
        p = gn.gen_pursue(rng)
        assert p["dv"] == p["vA"] - p["vB"]
        assert p["gap"] == p["dv"] * p["tMeet"]
        assert p["xMeet"] == p["vA"] * p["tMeet"]
        assert p["gap"] == p["xMeet"] - p["vB"] * p["tMeet"]
        assert isinstance(p["tMeet"], int)


def test_meet():
    rng = random.Random(2)
    for _ in range(N):
        p = gn.gen_meet(rng)
        assert p["total"] == (p["vA"] + p["vB"]) * p["tMeet"]
        assert p["xMeet"] == p["vA"] * p["tMeet"]
        assert p["total"] == p["xMeet"] + p["vB"] * p["tMeet"]
        assert isinstance(p["tMeet"], int)


def test_circular_same():
    rng = random.Random(3)
    for _ in range(N):
        p = gn.gen_circular_same(rng)
        L, dv = p["L"], p["dv"]
        assert L % dv == 0
        assert p["tMeet"] == L // dv
        assert 10 <= p["tMeet"] <= 40
        assert p["sMeet"] == (p["vA"] * p["tMeet"]) % L
        assert p["lapsA"] == (p["vA"] * p["tMeet"]) // L
        assert p["lapsB"] == (p["vB"] * p["tMeet"]) // L
        assert p["lapGain"] == p["lapsA"] - p["lapsB"] == 1


def test_circular_opp():
    rng = random.Random(4)
    for _ in range(N):
        p = gn.gen_circular_opp(rng)
        L, sv = p["L"], p["vA"] + p["vB"]
        assert L % sv == 0
        assert p["tMeet"] == L // sv
        assert 3 <= p["tMeet"] <= 15
        assert p["sMeet"] == (p["vA"] * p["tMeet"]) % L


def test_sum_diff():
    rng = random.Random(11)
    for _ in range(N):
        p = gn.gen_sum_diff(rng)
        assert p["a"] < p["b"]
        assert p["S"] == p["a"] + p["b"]
        assert p["D"] == p["b"] - p["a"]
        assert isinstance(p["a"], int) and isinstance(p["b"], int)
        assert p["a"] >= 4


def test_sum_multiple():
    rng = random.Random(12)
    for _ in range(N):
        p = gn.gen_sum_multiple(rng)
        assert p["b"] == p["n"] * p["a"]
        assert p["S"] == p["a"] + p["b"]
        assert p["S"] % (p["n"] + 1) == 0
        assert isinstance(p["a"], int) and isinstance(p["b"], int)


def test_diff_multiple():
    rng = random.Random(13)
    for _ in range(N):
        p = gn.gen_diff_multiple(rng)
        assert p["b"] == p["n"] * p["a"]
        assert p["D"] == p["b"] - p["a"]
        assert p["D"] % (p["n"] - 1) == 0
        assert isinstance(p["a"], int) and isinstance(p["b"], int)


def test_profit_loss():
    rng = random.Random(21)
    for _ in range(N):
        p = gn.gen_profit_loss(rng)
        assert p["b"] + p["d"] == p["n"] * (p["c"] - p["a"])
        assert p["total"] == p["a"] * p["n"] + p["b"]
        assert p["total"] == p["c"] * p["n"] - p["d"]
        assert 1 <= p["b"] <= p["n"] * (p["c"] - p["a"]) - 1
        assert isinstance(p["n"], int) and isinstance(p["total"], int)


def test_age():
    rng = random.Random(22)
    for _ in range(N):
        p = gn.gen_age(rng)
        assert p["P"] == p["n"] * p["Q"] + (p["n"] - 1) * p["t"]
        assert p["P"] + p["t"] == p["n"] * (p["Q"] + p["t"])
        assert p["P"] > p["Q"] and p["P"] <= 60
        assert isinstance(p["t"], int)


def test_average():
    rng = random.Random(23)
    for _ in range(N):
        p = gn.gen_average(rng)
        assert p["x"] < p["y"] < p["z"]
        assert (p["x"] + p["y"] + p["z"]) % 3 == 0
        assert p["A"] == (p["x"] + p["y"] + p["z"]) // 3
        assert isinstance(p["A"], int)


def test_chicken_rabbit():
    rng = random.Random(24)
    for _ in range(N):
        p = gn.gen_chicken_rabbit(rng)
        assert p["H"] == p["c"] + p["r"]
        assert p["L"] == 2 * p["c"] + 4 * p["r"]
        assert isinstance(p["c"], int) and isinstance(p["r"], int)


def test_plant():
    rng = random.Random(25)
    for _ in range(N):
        p = gn.gen_plant(rng)
        assert p["D"] == p["n"] * p["d"]
        assert p["k"] == p["n"] + 1
        assert isinstance(p["k"], int)


def test_work():
    rng = random.Random(26)
    for _ in range(N):
        p = gn.gen_work(rng)
        # 1/a + 1/b = 1/t  ⟺  a·b = t·(a+b)
        assert p["a"] * p["b"] == p["t"] * (p["a"] + p["b"])
        assert p["a"] != p["b"] and p["a"] <= 40 and p["b"] <= 40
        assert isinstance(p["t"], int)


def test_cycle():
    rng = random.Random(27)
    for _ in range(N):
        p = gn.gen_cycle(rng)
        assert p["r"] == ((p["N"] - 1) % p["p"]) + 1
        assert 1 <= p["r"] <= p["p"]
        assert isinstance(p["N"], int)


def test_unit():
    rng = random.Random(28)
    for _ in range(N):
        p = gn.gen_unit(rng)
        assert p["w"] == p["m"] * p["u"]
        assert p["ans"] == p["n"] * p["u"]
        assert p["n"] != p["m"]
        assert isinstance(p["ans"], int)


def test_aggregate():
    rng = random.Random(29)
    for _ in range(N):
        p = gn.gen_aggregate(rng)
        assert p["w"] == p["a"] * p["m"]
        assert p["b"] != p["a"] and p["w"] % p["b"] == 0
        assert p["n"] == p["w"] // p["b"]
        assert isinstance(p["n"], int)


def test_boat():
    rng = random.Random(30)
    for _ in range(N):
        p = gn.gen_boat(rng)
        assert p["down"] > p["up"]
        assert p["s"] == p["down"] * p["t1"] == p["up"] * p["t2"]
        assert 2 * p["u"] == p["down"] - p["up"]
        assert 2 * p["v"] == p["down"] + p["up"]
        assert isinstance(p["u"], int) and isinstance(p["v"], int)


def test_train():
    rng = random.Random(31)
    for _ in range(N):
        p = gn.gen_train(rng)
        assert (p["L"] + p["B"]) % p["v"] == 0
        assert p["t"] == (p["L"] + p["B"]) // p["v"]
        assert 8 <= p["t"] <= 40
        assert isinstance(p["t"], int)


def test_avgspeed():
    rng = random.Random(32)
    for _ in range(N):
        p = gn.gen_avgspeed(rng)
        assert p["v1"] != p["v2"]
        assert (2 * p["v1"] * p["v2"]) % (p["v1"] + p["v2"]) == 0
        assert p["avg"] == (2 * p["v1"] * p["v2"]) // (p["v1"] + p["v2"])
        assert p["arith"] == (p["v1"] + p["v2"]) // 2
        assert isinstance(p["avg"], int)


# ---- A 组：分数 / 百分数 / 比与比例 / 浓度 / 行程扩展 / 还原 / 平均数变体 / 间隔变体 ----

def test_fraction_part():
    rng = random.Random(41)
    for _ in range(N):
        p = gn.gen_fraction_part(rng)
        assert math.gcd(p["n"], p["d"]) == 1
        assert p["W"] == p["d"] * p["k"]
        assert p["part"] == p["n"] * p["k"]
        assert 0 < p["n"] < p["d"]
        assert isinstance(p["part"], int) and isinstance(p["W"], int)


def test_fraction_whole():
    rng = random.Random(42)
    for _ in range(N):
        p = gn.gen_fraction_whole(rng)
        assert math.gcd(p["n"], p["d"]) == 1
        assert p["W"] == p["d"] * p["k"]
        assert p["part"] == p["n"] * p["k"]
        assert 0 < p["n"] < p["d"]
        assert isinstance(p["W"], int)


def test_fraction_ratio():
    rng = random.Random(43)
    for _ in range(N):
        p = gn.gen_fraction_ratio(rng)
        assert math.gcd(p["n"], p["d"]) == 1
        assert p["A"] == p["n"] * p["k"]
        assert p["B"] == p["d"] * p["k"]
        assert p["A"] < p["B"]
        assert isinstance(p["n"], int)


def test_discount():
    rng = random.Random(44)
    for _ in range(N):
        p = gn.gen_discount(rng)
        assert p["A"] % 10 == 0
        assert p["price"] == p["A"] * p["d"] // 10
        assert 0 < p["price"] < p["A"]
        assert isinstance(p["price"], int)


def test_percent_change():
    rng = random.Random(45)
    for _ in range(N):
        p = gn.gen_percent_change(rng)
        assert p["A"] % 100 == 0
        assert p["price"] == p["A"] * (100 + p["x"]) // 100
        assert p["price"] > p["A"]
        assert isinstance(p["price"], int)


def test_ratio_share():
    rng = random.Random(46)
    for _ in range(N):
        p = gn.gen_ratio_share(rng)
        assert math.gcd(p["a"], p["b"]) == 1
        assert p["b"] > p["a"]
        assert p["A"] == p["a"] * p["k"]
        assert p["B"] == p["b"] * p["k"]
        assert p["total"] == p["A"] + p["B"]
        assert isinstance(p["A"], int) and isinstance(p["B"], int)


def test_ratio_scale():
    rng = random.Random(47)
    for _ in range(N):
        p = gn.gen_ratio_scale(rng)
        assert p["real"] == p["n"] * p["d"]
        assert isinstance(p["real"], int)


def test_concentration():
    rng = random.Random(48)
    for _ in range(N):
        p = gn.gen_concentration(rng)
        assert p["g"] % 100 == 0
        assert p["salt"] == p["g"] * p["c"] // 100
        assert 0 < p["salt"] < p["g"]
        assert isinstance(p["salt"], int)


def test_midpoint_meet():
    rng = random.Random(49)
    for _ in range(N):
        p = gn.gen_midpoint_meet(rng)
        assert p["vA"] > p["vB"]
        assert p["m"] == (p["vA"] - p["vB"]) * p["t"] // 2
        assert p["T"] == (p["vA"] + p["vB"]) * p["t"]
        assert p["m"] >= 1
        assert isinstance(p["t"], int) and isinstance(p["m"], int)


def test_restore():
    rng = random.Random(50)
    for _ in range(N):
        p = gn.gen_restore(rng)
        assert p["W"] % p["a"] == 0
        assert p["X"] == p["W"] - (p["W"] // p["a"] + p["b"])
        assert p["X"] % p["c"] == 0
        assert p["r"] == p["X"] - (p["X"] // p["c"] + p["d"])
        assert p["X"] > 0 and p["r"] > 0
        assert isinstance(p["W"], int)


def test_average_move():
    rng = random.Random(51)
    for _ in range(N):
        p = gn.gen_average_move(rng)
        assert p["a"] > p["b"]
        assert (p["a"] - p["b"]) % 2 == 0
        assert p["give"] == (p["a"] - p["b"]) // 2
        assert p["a"] - p["give"] == p["b"] + p["give"]
        assert isinstance(p["give"], int)


def test_stairs():
    rng = random.Random(52)
    for _ in range(N):
        p = gn.gen_stairs(rng)
        assert p["scenario"] in ("楼", "段", "下")
        assert p["total"] == (p["n"] - 1) * p["t"]
        assert isinstance(p["total"], int)


# ---- B 组：牛吃草 / 方阵 / 抽屉 / 时钟 / 消去法 / 等差数列 / 最优化 / 页码 / 三数和差倍 ----

def test_cows():
    rng = random.Random(53)
    for _ in range(N):
        p = gn.gen_cows(rng)
        assert p["N"] > p["g"]
        assert p["G"] == (p["N"] - p["g"]) * p["t"]
        assert p["G"] > 0 and p["t"] >= 3
        assert isinstance(p["t"], int)


def test_phalanx():
    rng = random.Random(54)
    for _ in range(N):
        p = gn.gen_phalanx(rng)
        assert p["total"] == p["n"] * p["n"]
        assert p["outer"] == 4 * p["n"] - 4
        assert p["n"] >= 4


def test_pigeonhole():
    rng = random.Random(55)
    for _ in range(N):
        p = gn.gen_pigeonhole(rng)
        assert p["m"] == p["n"] * p["k"] + p["r"]
        assert 0 < p["r"] < p["n"]
        assert p["least"] == p["k"] + 1
        assert p["m"] > p["n"] * p["k"]


def test_clock():
    rng = random.Random(56)
    for _ in range(N):
        p = gn.gen_clock(rng)
        assert p["angle"] == 30 * p["h"]
        assert 1 <= p["h"] <= 6
        assert isinstance(p["angle"], int)


def test_elimination():
    rng = random.Random(57)
    for _ in range(N):
        p = gn.gen_elimination(rng)
        assert p["S1"] == p["x"] + p["y"]
        assert p["S2"] == p["y"] + p["z"]
        assert p["S3"] == p["x"] + p["z"]
        assert not (p["x"] == p["y"] == p["z"])


def test_arithmetic_seq():
    rng = random.Random(58)
    for _ in range(N):
        p = gn.gen_arithmetic_seq(rng)
        assert p["an"] == p["a"] + (p["n"] - 1) * p["d"]
        assert p["an"] > p["a"]


def test_optimize():
    rng = random.Random(59)
    for _ in range(N):
        p = gn.gen_optimize(rng)
        a, b, pr, q, npeople = p["a"], p["b"], p["p"], p["q"], p["N"]
        assert pr * b < q * a
        best, bestk = None, []
        for k in range(0, npeople // a + 2):
            rest = max(0, npeople - k * a)
            small = -(-rest // b)
            cost = k * pr + small * q
            if best is None or cost < best:
                best, bestk = cost, [k]
            elif cost == best:
                bestk.append(k)
        assert len(bestk) == 1
        assert p["optK"] == bestk[0] and p["minCost"] == best
        assert p["optK"] >= 2


def test_page_digit():
    rng = random.Random(60)
    for _ in range(N):
        p = gn.gen_page_digit(rng)
        assert 10 <= p["n"] <= 99
        assert p["one"] == 9 and p["two"] == p["n"] - 9
        assert p["total"] == 9 + 2 * (p["n"] - 9)
        assert isinstance(p["total"], int)


def test_sum_diff_three():
    rng = random.Random(61)
    for _ in range(N):
        p = gn.gen_sum_diff_three(rng)
        assert p["b"] == p["a"] - p["D"]
        assert p["c"] == p["n"] * p["a"]
        assert p["S"] == p["a"] + p["b"] + p["c"]
        assert p["b"] >= 1 and p["a"] > p["D"]


# ---- C 组：盈亏两盈/两亏 + 植树一端/两端不栽/环形 ----

def test_profit_loss_two_gain():
    rng = random.Random(62)
    for _ in range(N):
        p = gn.gen_profit_loss_two_gain(rng)
        assert p["c"] > p["a"] and p["b"] > p["d"]
        assert p["b"] - p["d"] == p["n"] * (p["c"] - p["a"])
        assert p["total"] == p["n"] * p["a"] + p["b"]
        assert p["total"] == p["n"] * p["c"] + p["d"]
        assert p["total"] > 0 and isinstance(p["n"], int)


def test_profit_loss_two_loss():
    rng = random.Random(63)
    for _ in range(N):
        p = gn.gen_profit_loss_two_loss(rng)
        assert p["c"] > p["a"] and p["d"] > p["b"]
        assert p["d"] - p["b"] == p["n"] * (p["c"] - p["a"])
        assert p["total"] == p["n"] * p["a"] - p["b"]
        assert p["total"] == p["n"] * p["c"] - p["d"]
        assert p["total"] > 0 and isinstance(p["n"], int)


def test_plant_one():
    rng = random.Random(64)
    for _ in range(N):
        p = gn.gen_plant_one(rng)
        assert p["D"] == p["n"] * p["d"]
        assert p["k"] == p["n"]
        assert isinstance(p["k"], int) and p["k"] >= 4


def test_plant_none():
    rng = random.Random(65)
    for _ in range(N):
        p = gn.gen_plant_none(rng)
        assert p["D"] == p["n"] * p["d"]
        assert p["k"] == p["n"] - 1
        assert isinstance(p["k"], int) and p["k"] >= 3


def test_plant_ring():
    rng = random.Random(66)
    for _ in range(N):
        p = gn.gen_plant_ring(rng)
        assert p["D"] == p["n"] * p["d"]
        assert p["k"] == p["n"]
        assert isinstance(p["k"], int) and p["k"] >= 4


# ---- 板块 C+D：容斥/排列组合/逻辑推理/烙饼/田忌/分数差率/利率/植树两侧/天平 ----

def test_overlap_venn():
    rng = random.Random(67)
    for _ in range(N):
        p = gn.gen_overlap_venn(rng)
        assert p["X"] == p["a"] + p["c"]
        assert p["Y"] == p["b"] + p["c"]
        assert p["T"] == p["a"] + p["b"] + p["c"]
        assert p["c"] == p["X"] + p["Y"] - p["T"]
        assert p["c"] >= 2 and p["a"] >= 3 and p["b"] >= 3
        assert isinstance(p["c"], int) and isinstance(p["X"], int) and isinstance(p["Y"], int) and isinstance(p["T"], int)


def test_match_count():
    rng = random.Random(68)
    for _ in range(N):
        p = gn.gen_match_count(rng)
        assert 2 <= p["m"] <= 4 and 2 <= p["n"] <= 5
        assert p["total"] == p["m"] * p["n"]
        assert isinstance(p["total"], int)


def test_logic_table():
    rng = random.Random(69)
    for _ in range(N):
        p = gn.gen_logic_table(rng)
        assert sorted(p["perm"]) == [0, 1, 2]  # 唯一排列
        assert len(p["people"]) == 3 and len(p["sports"]) == 3
        assert p["cond1"] and p["cond2"] and p["cond3"]


def test_pancake():
    rng = random.Random(70)
    for _ in range(N):
        p = gn.gen_pancake(rng)
        assert p["n"] in (3, 5) and p["k"] == 2
        assert p["sides"] == 2 * p["n"]
        assert p["total"] == ((2 * p["n"] + p["k"] - 1) // p["k"]) * p["t"]
        assert isinstance(p["total"], int) and p["t"] in (2, 3)


def test_tianji():
    rng = random.Random(71)
    for _ in range(N):
        p = gn.gen_tianji(rng)
        assert set(p["order"]) == {"上", "中", "下"}
        # 田忌上对王中(胜)、中对王下(胜)、下对王上(负) → 赢 2 局
        assert p["tj_speed"]["上"] > p["qw_speed"]["中"]
        assert p["tj_speed"]["中"] > p["qw_speed"]["下"]
        assert p["tj_speed"]["下"] < p["qw_speed"]["上"]
        for tj in ["上", "中", "下"]:
            assert 1 <= p["ans_lane"][tj] <= 3
            assert 1 <= p["init_lane"][tj] <= 3


def test_fraction_more_less():
    rng = random.Random(72)
    for _ in range(N):
        p = gn.gen_fraction_more_less(rng)
        assert p["mode"] in ("多", "少")
        assert 2 <= p["k"] <= 6 and 2 <= p["m"] <= 5
        assert p["B"] == p["k"] * p["m"] and p["D"] == p["m"]
        assert p["A"] == (p["B"] + p["m"] if p["mode"] == "多" else p["B"] - p["m"])
        assert p["A"] > 0 and isinstance(p["A"], int)


def test_interest():
    rng = random.Random(73)
    for _ in range(N):
        p = gn.gen_interest(rng)
        assert p["P"] == 100 * p["m"]
        assert p["interest"] == p["m"] * p["r"] * p["n"]
        assert isinstance(p["interest"], int) and p["interest"] >= 2


def test_plant_two_sides():
    rng = random.Random(74)
    for _ in range(N):
        p = gn.gen_plant_two_sides(rng)
        assert p["D"] == p["n"] * p["d"]
        assert p["k"] == p["n"] + 1
        assert p["total"] == 2 * p["k"]
        assert isinstance(p["total"], int) and p["total"] >= 10


def test_equation_balance():
    rng = random.Random(75)
    for _ in range(N):
        p = gn.gen_equation_balance(rng)
        assert 2 <= p["x"] <= 6 and 2 <= p["a"] <= 4
        assert p["right"] == p["a"] * p["x"] + p["b"]
        assert isinstance(p["right"], int) and p["right"] >= 5


def test_triangle_equal():
    rng = random.Random(76)
    for _ in range(N):
        p = gn.gen_triangle_equal(rng)
        assert p["b"] in (6, 8, 10) and p["b"] % 2 == 0
        assert 3 <= p["h"] <= 5
        assert 1 <= p["s0"] <= p["b"] - 1
        assert p["s0"] != p["mid"]
        assert p["mid"] == p["b"] // 2
        assert p["area"] == p["b"] * p["h"] // 2
        assert isinstance(p["area"], int)


def test_para_equal():
    rng = random.Random(77)
    for _ in range(N):
        p = gn.gen_para_equal(rng)
        assert p["b"] in (6, 8, 10) and p["b"] % 2 == 0
        assert 3 <= p["h"] <= 5
        assert p["o"] in (-2, -1, 1, 2)
        assert p["area"] == p["b"] * p["h"]
        assert isinstance(p["area"], int)


def test_tri_height():
    rng = random.Random(78)
    for _ in range(N):
        p = gn.gen_tri_height(rng)
        assert p["b"] in (6, 8, 10) and p["b"] % 2 == 0
        assert 3 <= p["h"] <= 5
        assert 1 <= p["y0"] <= p["h"] - 1
        assert p["mid"] == p["b"] // 2
        assert p["area"] == p["b"] * p["h"] // 2
        assert isinstance(p["area"], int)


def test_trapezoid():
    rng = random.Random(79)
    for _ in range(N):
        p = gn.gen_trapezoid(rng)
        assert p["b"] in (6, 8, 10) and p["b"] % 2 == 0
        assert p["u"] in (2, 4, 6) and p["u"] < p["b"] and p["u"] % 2 == 0
        assert 3 <= p["h"] <= 5
        assert 0 <= p["o0"] <= p["b"] - p["u"]
        assert p["o0"] != p["mid"]
        assert p["mid"] == (p["b"] - p["u"]) // 2
        assert p["area"] == (p["b"] + p["u"]) * p["h"] // 2
        assert isinstance(p["area"], int)


def test_recompose():
    rng = random.Random(80)
    for _ in range(N):
        p = gn.gen_recompose(rng)
        assert p["b"] in (6, 8) and p["b"] % 2 == 0
        assert 3 <= p["h"] <= 5
        assert p["o"] in (2, 3)
        assert p["area"] == p["b"] * p["h"]
        assert isinstance(p["area"], int)


def test_circle():
    rng = random.Random(81)
    for _ in range(N):
        p = gn.gen_circle(rng)
        assert 2 <= p["r"] <= 5
        assert 1 <= p["r0"] <= 6 and p["r0"] != p["r"]
        assert p["d"] == 2 * p["r"]
        assert p["C"] == 6 * p["r"]
        assert isinstance(p["C"], int)


def test_circle_area():
    rng = random.Random(82)
    for _ in range(N):
        p = gn.gen_circle_area(rng)
        assert 2 <= p["r"] <= 5
        assert 1 <= p["r0"] <= 6 and p["r0"] != p["r"]
        assert p["d"] == 2 * p["r"]
        assert p["S"] == 3 * p["r"] * p["r"]
        assert isinstance(p["S"], int)


def test_semicircle():
    rng = random.Random(83)
    for _ in range(N):
        p = gn.gen_semicircle(rng)
        assert 2 <= p["r"] <= 5
        assert 1 <= p["r0"] <= 6 and p["r0"] != p["r"]
        assert p["d"] == 2 * p["r"]
        assert p["arc"] == 3 * p["r"]
        assert p["C"] == 5 * p["r"]
        assert isinstance(p["C"], int)


if __name__ == "__main__":
    test_pursue()
    test_meet()
    test_circular_same()
    test_circular_opp()
    test_sum_diff()
    test_sum_multiple()
    test_diff_multiple()
    test_profit_loss()
    test_age()
    test_average()
    test_chicken_rabbit()
    test_plant()
    test_work()
    test_cycle()
    test_unit()
    test_aggregate()
    test_boat()
    test_train()
    test_avgspeed()
    test_fraction_part()
    test_fraction_whole()
    test_fraction_ratio()
    test_discount()
    test_percent_change()
    test_ratio_share()
    test_ratio_scale()
    test_concentration()
    test_midpoint_meet()
    test_restore()
    test_average_move()
    test_stairs()
    test_cows()
    test_phalanx()
    test_pigeonhole()
    test_clock()
    test_elimination()
    test_arithmetic_seq()
    test_optimize()
    test_page_digit()
    test_sum_diff_three()
    test_profit_loss_two_gain()
    test_profit_loss_two_loss()
    test_plant_one()
    test_plant_none()
    test_plant_ring()
    test_overlap_venn()
    test_match_count()
    test_logic_table()
    test_pancake()
    test_tianji()
    test_fraction_more_less()
    test_interest()
    test_plant_two_sides()
    test_equation_balance()
    test_triangle_equal()
    test_para_equal()
    test_tri_height()
    test_trapezoid()
    test_recompose()
    test_circle()
    test_circle_area()
    test_semicircle()
    print(f"OK  62 类 × {N} 次抽样全部通过")
