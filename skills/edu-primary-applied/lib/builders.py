# -*- coding: utf-8 -*-
"""题型 → 数据 schema 构建，产出注入 HTML 数据岛的完整 JSON。

统一 schema 顶层键：type / lesson / scene / answer / diagram / readouts /
status / steps / ui（区分题型靠 type + scene.kind，前端只硬编码 STATE[type]、
DRAW[scene.kind]、DIAGRAM[diagram.kind] 三张分派表）。
"""
import math

import steps


def _ceil10(x):
    return int(math.ceil(x / 10.0)) * 10


def _xstep(tMax):
    if tMax <= 16:
        return 2
    if tMax <= 32:
        return 4
    if tMax <= 48:
        return 5
    return 10


def _base(type_slug, title, problem, hint, slider_label):
    """组装所有题型共用的骨架。"""
    return {
        "type": type_slug,
        "lesson": {"title": title, "problem": problem, "hint": hint},
        "answer": {},
        "status": {
            "before": {"text": "", "color": "amber"},
            "at": {"text": "", "color": "green"},
            "after": {"text": "", "color": "blue"},
        },
        "steps": [],
        "ui": {"play": "▶ 播放", "pause": "⏸ 暂停", "sliderLabel": slider_label},
    }


def _expr(label, expr, unit=None, color=None, decimals=None):
    r = {"label": label, "kind": "expr", "expr": expr}
    if unit:
        r["unit"] = unit
    if color:
        r["color"] = color
    if decimals is not None:
        r["decimals"] = decimals
    return r


def _answer(label, value):
    return {"label": label, "kind": "answer", "value": value}


# ---------------------------------------------------------------------------
# 行程问题（迁移，scene.kind = road/circular，diagram.kind = st-graph）
# ---------------------------------------------------------------------------

def _motion_scene(kind, direction, tMax, span, lap, meet_word, after_word, carA, carB):
    return {
        "kind": "circular" if kind == "circular" else "road",
        "param": {"min": 0, "max": tMax, "step": 0.1, "value": 0,
                  "label": "时间 t（秒）", "answer": tMax - 5},
        "motion": {
            "kind": kind, "direction": direction,
            "span": span, "lap": lap,
            "meetWord": meet_word, "afterWord": after_word,
            "carA": carA, "carB": carB,
        },
    }


def _st_diagram(tMax, yMax, lines, meet, laps):
    return {
        "kind": "st-graph",
        "xMax": tMax, "yMax": yMax, "xStep": _xstep(tMax), "yStep": 10,
        "lines": lines, "meet": meet, "laps": laps,
    }


def _motion_readouts(tMeet, meet_word, gap_label="相距", with_laps=False):
    """四种读数：时间 / 甲已跑 / 乙已跑 / 还差(动态 gap) / 答案。"""
    r = [
        {"label": "当前时间", "kind": "expr", "expr": "t", "unit": "秒", "decimals": 1},
        {"label": "甲已跑", "kind": "expr", "expr": "ranA", "unit": "米", "color": "#e2553f"},
        {"label": "乙已跑", "kind": "expr", "expr": "ranB", "unit": "米", "color": "#3b7dd8"},
        {"label": gap_label, "kind": "gap"},
    ]
    if with_laps:
        r.append({"label": "圈数", "kind": "laps"})
    r.append({"label": f"{meet_word}时间", "kind": "answer", "value": f"{tMeet} 秒"})
    return r


def build_pursue(p):
    vA, vB, gap, dv = p["vA"], p["vB"], p["gap"], p["dv"]
    tMeet, xMeet = p["tMeet"], p["xMeet"]
    tMax = tMeet + 5
    span = _ceil10(max(vA * tMax, gap + vB * tMax) * 1.1)
    yMax = _ceil10(max(vA * tMax, gap + vB * tMax))

    problem = (f"甲、乙两车在同一条路上同向行驶。乙车在甲车前方 {gap} 米处；"
               f"甲车每秒跑 {vA} 米，乙车每秒跑 {vB} 米。甲车几秒后能追上乙车？")
    d = _base("pursue", "追及问题", problem,
              "拖动时间滑块，或点「播放」，观察全过程。", "时间 t（秒）")
    d["scene"] = _motion_scene(
        "linear", "same", tMax, span, None, "追上", "超过",
        {"name": "甲", "color": "#e2553f", "x0": 0, "v": vA},
        {"name": "乙", "color": "#3b7dd8", "x0": gap, "v": vB},
    )
    d["answer"].update({"tMeet": tMeet, "xMeet": xMeet, "gap": gap, "dv": dv})
    d["diagram"] = _st_diagram(
        tMax, yMax,
        [{"name": "甲", "color": "#e2553f", "b": 0, "k": vA},
         {"name": "乙", "color": "#3b7dd8", "b": gap, "k": vB}],
        {"t": tMeet, "s": xMeet, "label": "追上", "mode": "cross"}, None,
    )
    d["readouts"] = _motion_readouts(tMeet, "追上", gap_label="乙领先甲")
    d["status"] = {
        "before": {"text": "甲还在追赶乙…", "color": "amber"},
        "at": {"text": f"追上了！用时 {tMeet} 秒", "color": "green"},
        "after": {"text": "甲已经超过乙啦！", "color": "blue"},
    }
    d["steps"] = steps.pursue_steps(p)
    return d


def build_meet(p):
    vA, vB, total = p["vA"], p["vB"], p["total"]
    tMeet, xMeet = p["tMeet"], p["xMeet"]
    tMax = tMeet + 5
    span = _ceil10(max(vA * tMax, total) * 1.1)
    yMax = _ceil10(max(vA * tMax, total))

    problem = (f"甲、乙两车从相距 {total} 米的两地同时出发，相向而行。"
               f"甲车每秒跑 {vA} 米，乙车每秒跑 {vB} 米。几秒后两车相遇？")
    d = _base("meet", "相遇问题", problem,
              "拖动时间滑块，或点「播放」，观察全过程。", "时间 t（秒）")
    d["scene"] = _motion_scene(
        "linear", "opposite", tMax, span, None, "相遇", "错过",
        {"name": "甲", "color": "#e2553f", "x0": 0, "v": vA},
        {"name": "乙", "color": "#3b7dd8", "x0": total, "v": vB},
    )
    d["answer"].update({"tMeet": tMeet, "xMeet": xMeet, "total": total,
                        "sumV": vA + vB})
    d["diagram"] = _st_diagram(
        tMax, yMax,
        [{"name": "甲", "color": "#e2553f", "b": 0, "k": vA},
         {"name": "乙", "color": "#3b7dd8", "b": total, "k": -vB}],
        {"t": tMeet, "s": xMeet, "label": "相遇", "mode": "cross"}, None,
    )
    d["readouts"] = _motion_readouts(tMeet, "相遇", gap_label="两车相距")
    d["status"] = {
        "before": {"text": "两车正在相向靠近…", "color": "amber"},
        "at": {"text": f"相遇了！用时 {tMeet} 秒", "color": "green"},
        "after": {"text": "两车已经错过啦！", "color": "blue"},
    }
    d["steps"] = steps.meet_steps(p)
    return d


def build_circular(p, mode):
    L, vA, vB, tMeet = p["L"], p["vA"], p["vB"], p["tMeet"]
    tMax = tMeet + 5

    if mode == "same":
        dv = p["dv"]
        sMeet = p["sMeet"]
        problem = (f"甲、乙两人在周长 {L} 米的环形跑道上，从同一起点同时同向出发。"
                   f"甲每秒跑 {vA} 米，乙每秒跑 {vB} 米。甲第一次追上乙，需要几秒？")
        d = _base("circular-same", "环形跑道 · 追及", problem,
                  "拖动时间滑块，或点「播放」，观察全过程。", "时间 t（秒）")
        d["scene"] = _motion_scene(
            "circular", "same", tMax, L, L, "追上", "超过",
            {"name": "甲", "color": "#e2553f", "x0": 0, "v": vA},
            {"name": "乙", "color": "#3b7dd8", "x0": 0, "v": vB},
        )
        d["answer"].update({"tMeet": tMeet, "xMeet": sMeet, "gap": L, "dv": dv,
                            "sMeet": sMeet, "lapsA": p["lapsA"],
                            "lapsB": p["lapsB"], "lapGain": p["lapGain"]})
        yMax = _ceil10(vA * tMax)
        d["diagram"] = _st_diagram(
            tMax, yMax,
            [{"name": "甲", "color": "#e2553f", "b": 0, "k": vA},
             {"name": "乙", "color": "#3b7dd8", "b": 0, "k": vB}],
            {"t": tMeet, "s": vA * tMeet, "label": "追上", "mode": "lap"},
            [L * i for i in range(1, yMax // L + 1)],
        )
        d["readouts"] = _motion_readouts(tMeet, "追上", gap_label="还需多跑", with_laps=True)
        d["status"] = {
            "before": {"text": "甲领先乙，还需多跑一圈才能追上…", "color": "amber"},
            "at": {"text": f"追上了！甲比乙多跑一圈（{L} 米），用时 {tMeet} 秒", "color": "green"},
            "after": {"text": "甲已经套乙一圈啦！", "color": "blue"},
        }
        d["steps"] = steps.circular_same_steps(p)
    else:
        sMeet = p["sMeet"]
        problem = (f"甲、乙两人在周长 {L} 米的环形跑道上，从同一起点同时相向出发。"
                   f"甲每秒跑 {vA} 米，乙每秒跑 {vB} 米。几秒后两人第一次相遇？")
        d = _base("circular-opp", "环形跑道 · 相遇", problem,
                  "拖动时间滑块，或点「播放」，观察全过程。", "时间 t（秒）")
        d["scene"] = _motion_scene(
            "circular", "opposite", tMax, L, L, "相遇", "错过",
            {"name": "甲", "color": "#e2553f", "x0": 0, "v": vA},
            {"name": "乙", "color": "#3b7dd8", "x0": L, "v": vB},
        )
        d["answer"].update({"tMeet": tMeet, "xMeet": sMeet, "total": L,
                            "sumV": vA + vB, "sMeet": sMeet})
        yMax = _ceil10(L)
        d["diagram"] = _st_diagram(
            tMax, yMax,
            [{"name": "甲", "color": "#e2553f", "b": 0, "k": vA},
             {"name": "乙", "color": "#3b7dd8", "b": L, "k": -vB}],
            {"t": tMeet, "s": vA * tMeet, "label": "相遇", "mode": "cross"}, None,
        )
        d["readouts"] = _motion_readouts(tMeet, "相遇", gap_label="还需合跑")
        d["status"] = {
            "before": {"text": "两人相向而跑，正在靠近…", "color": "amber"},
            "at": {"text": f"相遇了！两人合跑一圈（{L} 米），用时 {tMeet} 秒", "color": "green"},
            "after": {"text": "两人已经错过啦！", "color": "blue"},
        }
        d["steps"] = steps.circular_opp_steps(p)
    return d


# ---------------------------------------------------------------------------
# 线段图（scene.kind = bar-model）
# 通用：滑块 = 答案量（学生拖动「找答案」），bars 的 var/expr 在 STATE vars 作用域求值。
# ---------------------------------------------------------------------------

def _bar_scene(param, bars, scale, known=None, ref=None, rel=None,
               diff_label="差", cap="线段图"):
    scene = {"kind": "bar-model", "param": param, "bars": bars, "scale": scale,
             "cap": cap, "diffLabel": diff_label}
    if known:
        scene["known"] = known
    if ref:
        scene["ref"] = ref
    if rel:
        scene["rel"] = rel
    return scene


def _bar_readouts(answer_value):
    return [
        {"label": "较小数", "kind": "expr", "expr": "a", "color": "#e2553f"},
        {"label": "较大数", "kind": "expr", "expr": "b", "color": "#3b7dd8"},
        {"label": "两数和", "kind": "expr", "expr": "sum"},
        {"label": "两数差", "kind": "expr", "expr": "diff"},
        {"label": "答案", "kind": "answer", "value": answer_value},
    ]


def build_sum_diff(p):
    a, b, S, D = p["a"], p["b"], p["S"], p["D"]
    problem = (f"甲、乙两数的和是 {S}，差是 {D}。甲是大数，乙是小数。"
               f"甲、乙两数各是多少？")
    d = _base("sum-diff", "和差问题", problem,
              f"拖动滑块，找到正确的较小数，让两数差等于 {D}。", "较小数 a")
    d["scene"] = _bar_scene(
        {"min": 1, "max": S - 1, "step": 1, "value": 1, "label": "较小数 a", "answer": a},
        [{"name": "较小数", "color": "#e2553f", "var": "a"},
         {"name": "较大数", "color": "#3b7dd8", "var": "b"}],
        S, rel={"bigOf": "sum-minus-a", "sum": S})
    d["answer"] = {"small": a, "big": b}
    d["readouts"] = _bar_readouts(f"较小数 = {a}，较大数 = {b}")
    d["status"] = {
        "before": {"text": f"还没找对，两数差还不是 {D}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！较小数 = {a}，较大数 = {b}", "color": "green"},
        "after": {"text": "超过答案了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.sum_diff_steps(p)
    return d


def build_sum_multiple(p):
    a, b, n, S = p["a"], p["b"], p["n"], p["S"]
    problem = (f"甲数是乙数的 {n} 倍，两数的和是 {S}。甲、乙两数各是多少？")
    d = _base("sum-multiple", "和倍问题", problem,
              f"拖动滑块，找到正确的较小数，让两数和等于 {S}。", "较小数 a")
    d["scene"] = _bar_scene(
        {"min": 1, "max": 2 * a, "step": 1, "value": 1, "label": "较小数 a", "answer": a},
        [{"name": "较小数", "color": "#e2553f", "var": "a"},
         {"name": "较大数", "color": "#3b7dd8", "var": "b"}],
        S, rel={"bigOf": "n-times-a", "n": n})
    d["answer"] = {"small": a, "big": b}
    d["readouts"] = _bar_readouts(f"乙数 = {a}，甲数 = {b}")
    d["status"] = {
        "before": {"text": f"还没找对，两数和还不是 {S}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！乙数 = {a}，甲数 = {b}", "color": "green"},
        "after": {"text": "超过答案了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.sum_multiple_steps(p)
    return d


def build_diff_multiple(p):
    a, b, n, D = p["a"], p["b"], p["n"], p["D"]
    problem = (f"甲数是乙数的 {n} 倍，甲数比乙数多 {D}。甲、乙两数各是多少？")
    d = _base("diff-multiple", "差倍问题", problem,
              f"拖动滑块，找到正确的较小数，让两数差等于 {D}。", "较小数 a")
    d["scene"] = _bar_scene(
        {"min": 1, "max": 2 * a, "step": 1, "value": 1, "label": "较小数 a", "answer": a},
        [{"name": "较小数", "color": "#e2553f", "var": "a"},
         {"name": "较大数", "color": "#3b7dd8", "var": "b"}],
        a + b, rel={"bigOf": "n-times-a", "n": n})
    d["answer"] = {"small": a, "big": b}
    d["readouts"] = _bar_readouts(f"乙数 = {a}，甲数 = {b}")
    d["status"] = {
        "before": {"text": f"还没找对，两数差还不是 {D}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！乙数 = {a}，甲数 = {b}", "color": "green"},
        "after": {"text": "超过答案了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.diff_multiple_steps(p)
    return d


# ---------------------------------------------------------------------------
# R2 线段图：盈亏 / 年龄 / 平均数
# ---------------------------------------------------------------------------

def build_profit_loss(p):
    n, a, c, b, deficit, total = p["n"], p["a"], p["c"], p["b"], p["d"], p["total"]
    problem = (f"幼儿园给小朋友分糖：每人分 {a} 颗，还剩 {b} 颗；每人分 {c} 颗，还差 {deficit} 颗。"
               f"一共有多少个小朋友？一共多少颗糖？")
    d = _base("profit-loss", "盈亏问题", problem,
              "拖动滑块，找到正确的人数，让两次分糖的总数相等。", "人数 n")
    d["scene"] = _bar_scene(
        {"min": 1, "max": n + 5, "step": 1, "value": 1, "label": "人数 n", "answer": n},
        [{"name": f"每人{a}颗的总数", "color": "#e2553f", "expr": "first"},
         {"name": f"每人{c}颗的总数", "color": "#3b7dd8", "expr": "second"}],
        total + 40, known={"a": a, "c": c, "b": b, "d": deficit, "total": total},
        diff_label="相差")
    d["answer"] = {"n": n, "total": total}
    d["readouts"] = [
        _expr("人数", "n"),
        _expr(f"每人{a}颗·总数", "first", color="#e2553f"),
        _expr(f"每人{c}颗·总数", "second", color="#3b7dd8"),
        _answer("答案", f"{n} 人 · {total} 颗"),
    ]
    d["status"] = {
        "before": {"text": f"两次分糖的总数还不相等，再试试…", "color": "amber"},
        "at": {"text": f"找对了！{n} 个小朋友，一共 {total} 颗糖", "color": "green"},
        "after": {"text": "人数超过答案了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.profit_loss_steps(p)
    return d


def build_age(p):
    P, Q, n, t = p["P"], p["Q"], p["n"], p["t"]
    problem = (f"爸爸今年 {P} 岁，儿子今年 {Q} 岁。几年后，爸爸的年龄是儿子的 {n} 倍？")
    d = _base("age", "年龄问题", problem,
              f"拖动滑块，找到正确的年数，让爸爸年龄是儿子的 {n} 倍。", "几年后 t")
    d["scene"] = _bar_scene(
        {"min": 0, "max": t + 6, "step": 1, "value": 0, "label": "几年后 t", "answer": t},
        [{"name": "儿子年龄", "color": "#e2553f", "expr": "son"},
         {"name": "爸爸年龄", "color": "#3b7dd8", "expr": "dad"}],
        P + 20, known={"P": P, "Q": Q, "n": n}, diff_label="年龄差")
    d["answer"] = {"t": t}
    d["readouts"] = [
        _expr("几年后", "t", unit="年"),
        _expr("儿子年龄", "son", unit="岁", color="#e2553f"),
        _expr("爸爸年龄", "dad", unit="岁", color="#3b7dd8"),
        _expr("年龄差", "diff", unit="岁"),
        _expr("爸爸÷儿子", "ratio", unit="倍", decimals=1),
        _answer("答案", f"{t} 年后"),
    ]
    d["status"] = {
        "before": {"text": f"还没找对，爸爸还不是儿子的 {n} 倍，再试试…", "color": "amber"},
        "at": {"text": f"找对了！{t} 年后，爸爸 {P + t} 岁，儿子 {Q + t} 岁，正好 {n} 倍", "color": "green"},
        "after": {"text": "超过答案了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.age_steps(p)
    return d


def build_average(p):
    x, y, z, A = p["x"], p["y"], p["z"], p["A"]
    problem = (f"甲、乙、丙三个数的平均数是 {A}。甲是 {x}，乙是 {y}。丙是多少？")
    d = _base("average", "平均数问题", problem,
              f"拖动滑块，找到正确的丙，让三个数的平均数等于 {A}。", "丙 z")
    d["scene"] = _bar_scene(
        {"min": 1, "max": z + 8, "step": 1, "value": 1, "label": "丙 z", "answer": z},
        [{"name": "甲", "color": "#e2553f", "var": "x"},
         {"name": "乙", "color": "#3b7dd8", "var": "y"},
         {"name": "丙", "color": "#2ecc71", "var": "z"}],
        z + 8, known={"x": x, "y": y, "A": A},
        ref={"expr": "A", "label": "平均数"})
    d["answer"] = {"z": z}
    d["readouts"] = [
        _expr("甲", "x", color="#e2553f"),
        _expr("乙", "y", color="#3b7dd8"),
        _expr("丙", "z", color="#2ecc71"),
        _expr("平均数", "avg", decimals=1),
        _answer("答案", f"丙 = {z}"),
    ]
    d["status"] = {
        "before": {"text": f"平均数还不是 {A}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！丙 = {z}，平均数正好是 {A}", "color": "green"},
        "after": {"text": "丙太大了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.average_steps(p)
    return d


# ---------------------------------------------------------------------------
# R2 其它：鸡兔同笼（swap）/ 植树（interval）
# ---------------------------------------------------------------------------

def build_chicken_rabbit(p):
    c, r, H, L = p["c"], p["r"], p["H"], p["L"]
    problem = (f"笼子里有鸡和兔，一共有 {H} 个头，{L} 条腿。鸡和兔各有多少只？")
    d = _base("chicken-rabbit", "鸡兔同笼", problem,
              f"拖动滑块，改变鸡的数量，让腿的总数等于 {L}。", "鸡的只数 c")
    d["scene"] = {
        "kind": "swap", "cap": "鸡兔同笼",
        "param": {"min": 0, "max": H, "step": 1, "value": 0, "label": "鸡的只数 c", "answer": c},
        "known": {"H": H, "L": L},
    }
    d["answer"] = {"c": c, "r": r}
    d["readouts"] = [
        _expr("鸡", "c", unit="只", color="#e2553f"),
        _expr("兔", "r", unit="只", color="#3b7dd8"),
        _expr("头数", "heads", unit="个"),
        _expr("腿数", "legs", unit="条"),
        _answer("答案", f"鸡 {c} 只 · 兔 {r} 只"),
    ]
    d["status"] = {
        "before": {"text": f"腿数还不是 {L} 条，再试试…", "color": "amber"},
        "at": {"text": f"找对了！鸡 {c} 只，兔 {r} 只，腿数正好 {L} 条", "color": "green"},
        "after": {"text": "腿数超过了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.chicken_rabbit_steps(p)
    return d


def build_plant(p):
    n, spacing, D, k = p["n"], p["d"], p["D"], p["k"]
    problem = (f"在一条长 {D} 米的路的一侧，每隔 {spacing} 米栽一棵树，两端都栽。一共要栽多少棵树？")
    d = _base("plant", "植树问题", problem,
              f"拖动滑块，找到正确的棵树，让每段间隔正好 {spacing} 米。", "棵树 k")
    d["scene"] = {
        "kind": "interval", "cap": "植树（两端都栽）",
        "param": {"min": 2, "max": k + 5, "step": 1, "value": 2, "label": "棵树 k", "answer": k},
        "known": {"d": spacing, "D": D},
    }
    d["answer"] = {"k": k, "n": n}
    d["readouts"] = [
        _expr("棵树", "k", unit="棵", color="#e2553f"),
        _expr("间隔数", "gaps", unit="段"),
        _expr("每段间隔", "spacing", unit="米", color="#3b7dd8", decimals=1),
        _answer("答案", f"{k} 棵"),
    ]
    d["status"] = {
        "before": {"text": f"每段间隔还不是 {d} 米，再试试…", "color": "amber"},
        "at": {"text": f"找对了！{k} 棵树，{n} 段间隔，每段正好 {d} 米", "color": "green"},
        "after": {"text": "树栽得太密了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.plant_steps(p)
    return d


# ---------------------------------------------------------------------------
# R3 工程（progress）/ 周期（sequence）/ 归一 / 归总
# ---------------------------------------------------------------------------

def build_work(p):
    t, a, b = p["t"], p["a"], p["b"]
    problem = (f"一项工程，甲单独做 {a} 天完成，乙单独做 {b} 天完成。两人合做，多少天完成？")
    d = _base("work", "工程问题", problem,
              "拖动滑块，找到合做天数，让两人完成的工程正好是全部（100%）。", "合做天数 t")
    d["scene"] = {
        "kind": "progress", "cap": "合做进度",
        "param": {"min": 1, "max": t + 5, "step": 1, "value": 1, "label": "合做天数 t", "answer": t},
        "known": {"a": a, "b": b},
    }
    d["answer"] = {"t": t}
    d["readouts"] = [
        _expr("甲完成", "pctA", unit="%", color="#e2553f"),
        _expr("乙完成", "pctB", unit="%", color="#3b7dd8"),
        _expr("合计", "pctTotal", unit="%"),
        _answer("答案", f"{t} 天"),
    ]
    d["status"] = {
        "before": {"text": "还没做完，两人合计不到 100%，继续加天数…", "color": "amber"},
        "at": {"text": f"找对了！两人合做 {t} 天正好做完（100%）", "color": "green"},
        "after": {"text": "天数多了，早已做完，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.work_steps(p)
    return d


def build_cycle(p):
    p_len, N, r = p["p"], p["N"], p["r"]
    colors = ["红", "黄", "蓝", "绿", "紫"][:p_len]
    hexes = ["#e2553f", "#f5a623", "#3b7dd8", "#2ecc71", "#9b59b6"][:p_len]
    color_name = colors[r - 1]
    problem = (f"有一串彩灯，按「{'、'.join(colors)}」的顺序循环排列。第 {N} 盏彩灯是什么颜色？")
    d = _base("cycle", "周期问题", problem,
              f"拖动滑块到第 {N} 盏，看看它是什么颜色。", "第 N 盏")
    d["scene"] = {
        "kind": "sequence", "cap": "周期彩灯",
        "param": {"min": 1, "max": N + 8, "step": 1, "value": 1, "label": "第 N 盏", "answer": N},
        "known": {"p": p_len, "colors": colors, "hex": hexes},
    }
    d["answer"] = {"N": N, "r": r, "color": color_name}
    d["readouts"] = [
        _expr("第 N 盏", "N", unit="盏"),
        _expr("颜色", "colorName"),
        _expr("余数", "r"),
        _answer("答案", f"第 {N} 盏 = {color_name}色"),
    ]
    d["status"] = {
        "before": {"text": f"还没滑到第 {N} 盏，继续…", "color": "amber"},
        "at": {"text": f"第 {N} 盏 = {color_name}色（{N} ÷ {p_len} 余 {r}）", "color": "green"},
        "after": {"text": f"已经滑过第 {N} 盏啦！", "color": "blue"},
    }
    d["steps"] = steps.cycle_steps(p)
    return d


def build_unit(p):
    u, m, n, w, ans = p["u"], p["m"], p["n"], p["w"], p["ans"]
    problem = (f"{m} 支同样的铅笔 {w} 元。买 {n} 支这样的铅笔，需要多少元？")
    d = _base("unit", "归一问题", problem,
              f"拖动滑块，找到正确的单价，让 {m} 支正好是 {w} 元。", "单价 u（元）")
    d["scene"] = _bar_scene(
        {"min": 1, "max": u + 6, "step": 1, "value": 1, "label": "单价 u（元）", "answer": u},
        [{"name": f"{m}支·现价", "color": "#e2553f", "expr": "known"},
         {"name": f"{m}支·已知", "color": "#3b7dd8", "expr": "w"}],
        w + 20, known={"m": m, "n": n, "w": w, "ans": ans}, diff_label="相差")
    d["answer"] = {"u": u, "ans": ans}
    d["readouts"] = [
        _expr("单价", "u", unit="元"),
        _expr(f"{m}支总价", "known", unit="元", color="#e2553f"),
        _expr(f"{n}支总价", "wanted", unit="元", color="#3b7dd8"),
        _answer("答案", f"{ans} 元"),
    ]
    d["status"] = {
        "before": {"text": f"{m} 支还不是 {w} 元，再试试…", "color": "amber"},
        "at": {"text": f"找对了！单价 {u} 元，{n} 支共 {ans} 元", "color": "green"},
        "after": {"text": "单价太高了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.unit_steps(p)
    return d


def build_aggregate(p):
    a, m, w, b, n = p["a"], p["m"], p["w"], p["b"], p["n"]
    problem = (f"一批糖果，每盒装 {a} 颗，正好装 {m} 盒。如果每盒装 {b} 颗，能装几盒？")
    d = _base("aggregate", "归总问题", problem,
              f"拖动滑块，找到正确的盒数，让每盒正好是 {b} 颗。", "盒数 n")
    d["scene"] = _bar_scene(
        {"min": 1, "max": n + 6, "step": 1, "value": 1, "label": "盒数 n", "answer": n},
        [{"name": "每盒(现)", "color": "#e2553f", "expr": "perbox"},
         {"name": "每盒(目标)", "color": "#3b7dd8", "expr": "b"}],
        b + 10, known={"w": w, "b": b}, diff_label="相差")
    d["answer"] = {"n": n, "b": b}
    d["readouts"] = [
        _expr("盒数", "n", unit="盒"),
        _expr("每盒(现)", "perbox", unit="颗", color="#e2553f", decimals=1),
        _expr("每盒(目标)", "b", unit="颗", color="#3b7dd8"),
        _answer("答案", f"{n} 盒"),
    ]
    d["status"] = {
        "before": {"text": f"每盒还不是 {b} 颗，再试试…", "color": "amber"},
        "at": {"text": f"找对了！{n} 盒，每盒正好 {b} 颗", "color": "green"},
        "after": {"text": "盒数太多，每盒不够 {b} 颗，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.aggregate_steps(p)
    return d


# ---------------------------------------------------------------------------
# R3 行程扩展：流水行船 / 火车过桥 / 平均速度
# ---------------------------------------------------------------------------

def build_boat(p):
    s_km, t1, t2, u, v, down, up = p["s"], p["t1"], p["t2"], p["u"], p["v"], p["down"], p["up"]
    problem = (f"甲、乙两港相距 {s_km} 千米。一艘船顺水从甲到乙用了 {t1} 小时，逆水从乙到甲用了 {t2} 小时。"
               f"水流速度是多少？")
    d = _base("boat", "流水行船", problem,
              f"拖动滑块，找到正确的水流速度，让顺水速度等于 {down} 千米/时。", "水流速度 u（千米/时）")
    d["scene"] = _bar_scene(
        {"min": 1, "max": u + 4, "step": 1, "value": 1, "label": "水流速度 u（千米/时）", "answer": u},
        [{"name": "顺水速度", "color": "#e2553f", "expr": "downV"},
         {"name": "逆水速度", "color": "#3b7dd8", "expr": "upV"}],
        down + 6, known={"v": v, "down": down, "up": up},
        ref={"expr": "down", "label": "顺水目标"}, diff_label="速度差")
    d["answer"] = {"u": u, "v": v}
    d["readouts"] = [
        _expr("水流速度", "u", unit="千米/时"),
        _expr("静水速度", "v", unit="千米/时"),
        _expr("顺水速度", "downV", unit="千米/时", color="#e2553f"),
        _expr("逆水速度", "upV", unit="千米/时", color="#3b7dd8"),
        _answer("答案", f"水流 {u} 千米/时"),
    ]
    d["status"] = {
        "before": {"text": f"顺水速度还不是 {down} 千米/时，再试试…", "color": "amber"},
        "at": {"text": f"找对了！水流 {u} 千米/时，静水 {v} 千米/时", "color": "green"},
        "after": {"text": "水流太快了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.boat_steps(p)
    return d


def build_train(p):
    L, B, v, t = p["L"], p["B"], p["v"], p["t"]
    problem = (f"一列火车长 {L} 米，以每秒 {v} 米的速度通过一座长 {B} 米的桥。"
               f"从车头上桥到车尾离桥，一共需要多少秒？")
    d = _base("train", "火车过桥", problem,
              "拖动滑块，或点「播放」，观察火车通过大桥的全过程。", "时间 t（秒）")
    d["scene"] = {
        "kind": "train", "cap": "火车过桥",
        "param": {"min": 0, "max": t + 5, "step": 0.1, "value": 0, "label": "时间 t（秒）", "answer": t},
        "known": {"L": L, "B": B, "v": v},
    }
    d["answer"] = {"t": t}
    d["readouts"] = [
        _expr("当前时间", "t", unit="秒", decimals=1),
        _expr("已行驶", "dist", unit="米", color="#e2553f", decimals=1),
        _expr("还需通过", "remain", unit="米", color="#3b7dd8", decimals=1),
        _answer("答案", f"{t} 秒"),
    ]
    d["status"] = {
        "before": {"text": "火车还在过桥…", "color": "amber"},
        "at": {"text": f"车尾离桥！一共用了 {t} 秒", "color": "green"},
        "after": {"text": "火车已经通过大桥啦！", "color": "blue"},
    }
    d["steps"] = steps.train_steps(p)
    return d


def build_avgspeed(p):
    v1, v2, avg, arith = p["v1"], p["v2"], p["avg"], p["arith"]
    problem = (f"小明从家到学校，去时每小时 {v1} 千米，回来每小时 {v2} 千米。"
               f"往返全程的平均速度是多少千米/时？")
    d = _base("avgspeed", "平均速度", problem,
              "拖动滑块，找到正确的平均速度（注意：不是两个速度的平均）。", "平均速度 v（千米/时）")
    d["scene"] = _bar_scene(
        {"min": 1, "max": avg + 6, "step": 1, "value": 1, "label": "平均速度 v（千米/时）", "answer": avg},
        [{"name": "平均速度", "color": "#e2553f", "expr": "v"},
         {"name": "速度平均", "color": "#3b7dd8", "expr": "arith"}],
        arith + 8, known={"v1": v1, "v2": v2, "arith": arith}, diff_label="相差")
    d["answer"] = {"avg": avg}
    d["readouts"] = [
        _expr("去时速度", "v1", unit="千米/时"),
        _expr("回来速度", "v2", unit="千米/时"),
        _expr("平均速度", "v", unit="千米/时", color="#e2553f"),
        _expr("速度平均", "arith", unit="千米/时", color="#3b7dd8"),
        _answer("答案", f"{avg} 千米/时"),
    ]
    d["status"] = {
        "before": {"text": f"平均速度还不对，再试试（提示：不是 {(v1 + v2) // 2}）…", "color": "amber"},
        "at": {"text": f"找对了！往返平均速度是 {avg} 千米/时", "color": "green"},
        "after": {"text": "超过答案了，往回调整…", "color": "blue"},
    }
    d["steps"] = steps.avgspeed_steps(p)
    return d


# ---------------------------------------------------------------------------
# A 组：分数 / 百分数 / 比与比例 / 浓度 / 行程扩展 / 还原 / 平均数变体 / 间隔变体
# ---------------------------------------------------------------------------

def _frac_cn(n, d):
    """把分率 1/a 之类转中文（1/2→一半，1/3→三分之一）。"""
    if n == 1 and d == 2:
        return "一半"
    if n == 1 and d == 3:
        return "三分之一"
    return f"{n}/{d}"


def build_fraction_part(p):
    d, n, W, part = p["d"], p["n"], p["W"], p["part"]
    problem = (f"求 {W} 的 {n}/{d} 是多少？")
    d0 = _base("fraction-part", "分数 · 求一个数的几分之几", problem,
               f"拖动滑块，找到正确的部分（{W}×{n}/{d}）。", "部分")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": W, "step": 1, "value": 1, "label": "部分", "answer": part},
        [{"name": "整体", "color": "#e2553f", "expr": "W"},
         {"name": "部分", "color": "#3b7dd8", "var": "p"}],
        W, known={"W": W, "n": n, "d": d})
    d0["answer"] = {"part": part}
    d0["readouts"] = [
        _expr("整体", "W", color="#e2553f"),
        _expr("部分", "p", color="#3b7dd8"),
        _answer("分率", f"{n}/{d}"),
        _answer("答案", f"{part}"),
    ]
    d0["status"] = {
        "before": {"text": f"部分还不是 {W} 的 {n}/{d}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！{W} × {n}/{d} = {part}", "color": "green"},
        "after": {"text": "部分超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.fraction_part_steps(p)
    return d0


def build_fraction_whole(p):
    d, n, W, part = p["d"], p["n"], p["W"], p["part"]
    problem = (f"一个数的 {n}/{d} 是 {part}，这个数是多少？")
    d0 = _base("fraction-whole", "分数 · 求单位「1」", problem,
               f"拖动滑块，找到正确的整体，让「整体×{n}/{d}」等于 {part}。", "整体（单位1）")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": W + 8, "step": 1, "value": 1, "label": "整体（单位1）", "answer": W},
        [{"name": "整体", "color": "#e2553f", "var": "w"},
         {"name": "部分", "color": "#3b7dd8", "expr": "w*n/d"}],
        W + 8, known={"part": part, "n": n, "d": d},
        ref={"expr": "part", "label": "已知部分"})
    d0["answer"] = {"W": W}
    d0["readouts"] = [
        _expr("整体", "w", color="#e2553f"),
        _expr("部分", "w*n/d", color="#3b7dd8"),
        _expr("已知部分", "part"),
        _answer("答案", f"{W}"),
    ]
    d0["status"] = {
        "before": {"text": f"整体×{n}/{d} 还不是 {part}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！这个数是 {W}（{W}×{n}/{d}={part}）", "color": "green"},
        "after": {"text": "整体超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.fraction_whole_steps(p)
    return d0


def build_fraction_ratio(p):
    d, n, k, A, B = p["d"], p["n"], p["k"], p["A"], p["B"]
    problem = (f"甲数是 {A}，乙数是 {B}。甲数是乙数的几分之几？（用 {d} 作分母，找分子）")
    d0 = _base("fraction-ratio", "分数 · 求一个数是另一个数的几分之几", problem,
               f"拖动滑块，找到正确的分子，让甲数 = 乙数 × 分子/{d}。", "分子 n")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": d - 1, "step": 1, "value": 1, "label": "分子 n", "answer": n},
        [{"name": "乙数", "color": "#3b7dd8", "expr": "B"},
         {"name": "甲数", "color": "#e2553f", "expr": "A"}],
        B, known={"d": d, "k": k})
    d0["answer"] = {"n": n, "d": d}
    d0["readouts"] = [
        _expr("分子", "n"),
        _expr("甲数", "A", color="#e2553f"),
        _expr("乙数", "B", color="#3b7dd8"),
        _answer("答案", f"{n}/{d}"),
    ]
    d0["status"] = {
        "before": {"text": f"甲数还不是乙数的 {n}/{d}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！甲数是乙数的 {n}/{d}（{A}÷{B}）", "color": "green"},
        "after": {"text": "分子超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.fraction_ratio_steps(p)
    return d0


def build_discount(p):
    A, d, price = p["A"], p["d"], p["price"]
    problem = (f"一件衣服原价 {A} 元，打 {d} 折出售，现价是多少元？")
    d0 = _base("discount", "百分数 · 折扣", problem,
               f"拖动滑块，找到正确的现价（原价×{d}/10）。", "现价（元）")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": A, "step": 1, "value": 1, "label": "现价（元）", "answer": price},
        [{"name": "原价", "color": "#e2553f", "expr": "A"},
         {"name": "现价", "color": "#3b7dd8", "var": "p"}],
        A, known={"A": A, "d": d})
    d0["answer"] = {"price": price}
    d0["readouts"] = [
        _expr("原价", "A", unit="元", color="#e2553f"),
        _expr("现价", "p", unit="元", color="#3b7dd8"),
        _answer("折扣", f"{d} 折"),
        _answer("答案", f"{price} 元"),
    ]
    d0["status"] = {
        "before": {"text": f"现价还不是 {A}×{d}/10，再试试…", "color": "amber"},
        "at": {"text": f"找对了！打 {d} 折，现价 {price} 元", "color": "green"},
        "after": {"text": "现价超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.discount_steps(p)
    return d0


def build_percent_change(p):
    A, x, price = p["A"], p["x"], p["price"]
    problem = (f"一件商品原价 {A} 元，涨价 {x}%，现价是多少元？")
    d0 = _base("percent-change", "百分数 · 增减百分之几", problem,
               f"拖动滑块，找到正确的现价（原价×(100+{x})/100）。", "现价（元）")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": A * 2, "step": 1, "value": 1, "label": "现价（元）", "answer": price},
        [{"name": "原价", "color": "#e2553f", "expr": "A"},
         {"name": "现价", "color": "#3b7dd8", "var": "p"}],
        A * 2, known={"A": A, "x": x})
    d0["answer"] = {"price": price}
    d0["readouts"] = [
        _expr("原价", "A", unit="元", color="#e2553f"),
        _expr("现价", "p", unit="元", color="#3b7dd8"),
        _answer("涨幅", f"{x}%"),
        _answer("答案", f"{price} 元"),
    ]
    d0["status"] = {
        "before": {"text": f"现价还不是 {A}×(100+{x})/100，再试试…", "color": "amber"},
        "at": {"text": f"找对了！涨价 {x}%，现价 {price} 元", "color": "green"},
        "after": {"text": "现价超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.percent_change_steps(p)
    return d0


def build_ratio_share(p):
    a, b, k, A, B, total = p["a"], p["b"], p["k"], p["A"], p["B"], p["total"]
    problem = (f"把 {total} 元按 {a}:{b} 分给甲、乙两人。甲、乙各分多少元？")
    d0 = _base("ratio-share", "比 · 按比例分配", problem,
               f"拖动滑块，找到正确的每份数，让甲:乙 = {a}:{b}。", "每份 k")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": k + 8, "step": 1, "value": 1, "label": "每份 k", "answer": k},
        [{"name": "甲", "color": "#e2553f", "expr": "a*k"},
         {"name": "乙", "color": "#3b7dd8", "expr": "b*k"}],
        total, known={"a": a, "b": b, "total": total})
    d0["answer"] = {"A": A, "B": B}
    d0["readouts"] = [
        _expr("每份", "k", unit="元"),
        _expr("甲", "a*k", unit="元", color="#e2553f"),
        _expr("乙", "b*k", unit="元", color="#3b7dd8"),
        _expr("总数", "a*k+b*k", unit="元"),
        _answer("答案", f"甲 {A} 元 · 乙 {B} 元"),
    ]
    d0["status"] = {
        "before": {"text": f"甲:乙 还不是 {a}:{b}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！甲 {A} 元，乙 {B} 元", "color": "green"},
        "after": {"text": "每份超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.ratio_share_steps(p)
    return d0


def build_ratio_scale(p):
    n, d, real = p["n"], p["d"], p["real"]
    problem = (f"一个零件模型按 1:{n} 的比例制作，模型长 {d} 厘米。这个零件实际长多少厘米？")
    d0 = _base("ratio-scale", "比例 · 比例尺（模型比例）", problem,
               f"拖动滑块，找到正确的实际长度（模型长×{n}）。", "实际长度（厘米）")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": real + 10, "step": 1, "value": 1, "label": "实际长度（厘米）", "answer": real},
        [{"name": "模型", "color": "#e2553f", "expr": "d"},
         {"name": "实物", "color": "#3b7dd8", "var": "r"}],
        real + 10, known={"n": n, "d": d})
    d0["answer"] = {"real": real}
    d0["readouts"] = [
        _expr("模型", "d", unit="厘米", color="#e2553f"),
        _expr("实物", "r", unit="厘米", color="#3b7dd8"),
        _answer("比例", f"1:{n}"),
        _answer("答案", f"{real} 厘米"),
    ]
    d0["status"] = {
        "before": {"text": f"实际长度还不是 {d}×{n} 厘米，再试试…", "color": "amber"},
        "at": {"text": f"找对了！实际长 {real} 厘米", "color": "green"},
        "after": {"text": "超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.ratio_scale_steps(p)
    return d0


def build_concentration(p):
    g, c, salt = p["g"], p["c"], p["salt"]
    problem = (f"一杯盐水重 {g} 克，含盐率是 {c}%。这杯盐水里有多少克盐？")
    d0 = _base("concentration", "百分数 · 浓度", problem,
               f"拖动滑块，找到正确的盐量（盐水×{c}%）。", "盐（克）")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": g, "step": 1, "value": 1, "label": "盐（克）", "answer": salt},
        [{"name": "盐水", "color": "#e2553f", "expr": "g"},
         {"name": "盐", "color": "#3b7dd8", "var": "s"}],
        g, known={"g": g, "c": c})
    d0["answer"] = {"salt": salt}
    d0["readouts"] = [
        _expr("盐水", "g", unit="克", color="#e2553f"),
        _expr("盐", "s", unit="克", color="#3b7dd8"),
        _expr("水", "g-s", unit="克"),
        _answer("答案", f"{salt} 克"),
    ]
    d0["status"] = {
        "before": {"text": f"盐量还不是 {g}×{c}%，再试试…", "color": "amber"},
        "at": {"text": f"找对了！盐有 {salt} 克", "color": "green"},
        "after": {"text": "盐量超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.concentration_steps(p)
    return d0


def build_midpoint_meet(p):
    vA, vB, t, m, T = p["vA"], p["vB"], p["t"], p["m"], p["T"]
    tMax = t + 5
    span = _ceil10(max(vA * tMax, T) * 1.1)
    yMax = _ceil10(max(vA * tMax, T))
    problem = (f"甲、乙两人同时从相距 {T} 米的两地相向而行。甲每分走 {vA} 米，乙每分走 {vB} 米。"
               f"两人在距中点 {m} 米处相遇。他们走了多少分钟？")
    d0 = _base("midpoint-meet", "行程 · 中点相遇", problem,
               "拖动时间滑块，或点「播放」，观察两人在中点旁相遇。", "时间 t（分钟）")
    sc = _motion_scene(
        "linear", "opposite", tMax, span, None, "相遇", "错过",
        {"name": "甲", "color": "#e2553f", "x0": 0, "v": vA},
        {"name": "乙", "color": "#3b7dd8", "x0": T, "v": vB},
    )
    sc["motion"]["midpoint"] = T / 2
    d0["scene"] = sc
    d0["answer"].update({"t": t, "m": m, "T": T})
    d0["diagram"] = _st_diagram(
        tMax, yMax,
        [{"name": "甲", "color": "#e2553f", "b": 0, "k": vA},
         {"name": "乙", "color": "#3b7dd8", "b": T, "k": -vB}],
        {"t": t, "s": vA * t, "label": "相遇", "mode": "cross"}, None,
    )
    d0["readouts"] = [
        _expr("时间", "t", unit="分", decimals=0),
        _expr("甲走了", "ranA", unit="米", color="#e2553f"),
        _expr("乙走了", "ranB", unit="米", color="#3b7dd8"),
        _expr("距中点", "abs(posA-x0B/2)", unit="米"),
        _answer("答案", f"{t} 分钟"),
    ]
    d0["status"] = {
        "before": {"text": "两人还在走，相遇点离中点还不止 " + str(m) + " 米…", "color": "amber"},
        "at": {"text": f"相遇了！距中点 {m} 米，走了 {t} 分钟", "color": "green"},
        "after": {"text": "两人已经错过啦！", "color": "blue"},
    }
    d0["steps"] = steps.midpoint_meet_steps(p)
    return d0


def build_restore(p):
    a, b, c, d, W, X, r = p["a"], p["b"], p["c"], p["d"], p["W"], p["X"], p["r"]
    ea = _frac_cn(1, a)
    ec = _frac_cn(1, c)
    problem = (f"有一袋糖，第一次吃了总数的{ea}多 {b} 个，第二次吃了剩下的{ec}多 {d} 个，"
               f"最后还剩 {r} 个。原来有多少个糖？")
    d0 = _base("restore", "还原问题（逆推）", problem,
               f"拖动滑块，找到正确的原来数量，让「最后剩」等于 {r}。", "原来（个）")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": W + 20, "step": 1, "value": 1, "label": "原来（个）", "answer": W},
        [{"name": "原来", "color": "#e2553f", "var": "W"},
         {"name": "第一次剩", "color": "#3b7dd8", "expr": "X"},
         {"name": "最后剩", "color": "#2ecc71", "expr": "r"}],
        W + 20, known={"a": a, "b": b, "c": c, "d": d, "r0": r})
    d0["answer"] = {"W": W}
    d0["readouts"] = [
        _expr("原来", "W", unit="个", color="#e2553f"),
        _expr("第一次剩", "X", unit="个", color="#3b7dd8"),
        _expr("最后剩", "r", unit="个", color="#2ecc71"),
        _answer("答案", f"{W} 个"),
    ]
    d0["status"] = {
        "before": {"text": f"最后剩的还不是 {r} 个，再试试…", "color": "amber"},
        "at": {"text": f"找对了！原来有 {W} 个糖", "color": "green"},
        "after": {"text": "原来数量超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.restore_steps(p)
    return d0


def build_average_move(p):
    a, b, give = p["a"], p["b"], p["give"]
    problem = (f"甲有 {a} 个苹果，乙有 {b} 个苹果。甲给乙多少个，两人的苹果就一样多？")
    d0 = _base("average-move", "平均数 · 移多补少", problem,
               f"拖动滑块，找到正确的给数，让两人一样多。", "给的个数")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": give + 8, "step": 1, "value": 1, "label": "给的个数", "answer": give},
        [{"name": "甲现在", "color": "#e2553f", "expr": "a-g"},
         {"name": "乙现在", "color": "#3b7dd8", "expr": "b+g"}],
        a, known={"a": a, "b": b})
    d0["answer"] = {"give": give}
    d0["readouts"] = [
        _expr("给的", "g", unit="个"),
        _expr("甲现在", "a-g", unit="个", color="#e2553f"),
        _expr("乙现在", "b+g", unit="个", color="#3b7dd8"),
        _answer("答案", f"给 {give} 个"),
    ]
    d0["status"] = {
        "before": {"text": "两人还不一样多，再试试…", "color": "amber"},
        "at": {"text": f"找对了！甲给乙 {give} 个，两人都有 {a - give} 个", "color": "green"},
        "after": {"text": "给多了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.average_move_steps(p)
    return d0


_STAIRS = {
    "楼": {"title": "间隔问题 · 爬楼梯", "item": "楼", "segWord": "层", "unit": "秒",
           "problem": lambda n, t: f"小明从 1 楼走到 {n} 楼，每上一层楼要用 {t} 秒，一共要用多少秒？"},
    "段": {"title": "间隔问题 · 锯木头", "item": "段", "segWord": "次", "unit": "分",
           "problem": lambda n, t: f"把一根木头锯成 {n} 段，锯一次要用 {t} 分钟，一共要用多少分钟？"},
    "下": {"title": "间隔问题 · 敲钟", "item": "下", "segWord": "个间隔", "unit": "秒",
           "problem": lambda n, t: f"时钟敲 {n} 下，每两下之间的间隔是 {t} 秒，从敲第一下到敲完一共要用多少秒？"},
}


def build_stairs(p):
    scenario, n, t, total = p["scenario"], p["n"], p["t"], p["total"]
    meta = _STAIRS[scenario]
    unit = meta["unit"]
    d0 = _base("stairs", meta["title"], meta["problem"](n, t),
               f"拖动滑块，找到正确的总时间（{n-1} 个间隔 × {t}）。", f"一共（{unit}）")
    d0["scene"] = {
        "kind": "interval", "cap": meta["title"],
        "param": {"min": 1, "max": total + 8, "step": 1, "value": 1,
                  "label": f"一共（{unit}）", "answer": total},
        "known": {"n": n, "t": t, "total": total, "unit": unit,
                  "item": meta["item"], "segWord": meta["segWord"]},
    }
    d0["answer"] = {"total": total}
    d0["readouts"] = [
        _expr(meta["item"] + "数", "n", color="#e2553f"),
        _expr("间隔数", "gaps"),
        _expr("每" + meta["segWord"], "spacing", unit=unit, color="#3b7dd8", decimals=1),
        _answer("答案", f"{total} {unit}"),
    ]
    d0["status"] = {
        "before": {"text": f"每{meta['segWord']}还不是 {t} {unit}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！{n-1} 个间隔 × {t} = {total} {unit}", "color": "green"},
        "after": {"text": "总时间超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.stairs_steps(p)
    return d0


# ---------------------------------------------------------------------------
# B 组：牛吃草 / 方阵 / 抽屉 / 时钟 / 消去法 / 等差数列 / 最优化 / 页码 / 三数和差倍
# ---------------------------------------------------------------------------

def build_cows(p):
    g, N, t, G = p["g"], p["N"], p["t"], p["G"]
    tMax = t + 8
    scale = N * tMax
    problem = (f"一片草地原有 {G} 份草，每天匀速长出 {g} 份。现有 {N} 头牛，每头牛每天吃 1 份草。"
               f"这些牛可以吃多少天？")
    d0 = _base("cows", "牛吃草问题", problem,
               f"拖动滑块，找到正确的天数，让牛吃掉的草正好等于原有草加长出的草。", "可吃天数")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": tMax, "step": 1, "value": 1, "label": "可吃天数", "answer": t},
        [{"name": "草总量", "color": "#e2553f", "expr": "G+g*t"},
         {"name": "牛已吃", "color": "#3b7dd8", "expr": "N*t"}],
        scale, known={"g": g, "N": N, "G": G}, diff_label="相差")
    d0["answer"] = {"t": t, "G": G}
    d0["readouts"] = [
        _expr("天数", "t", unit="天"),
        _expr("草总量", "G+g*t", unit="份", color="#e2553f"),
        _expr("牛已吃", "N*t", unit="份", color="#3b7dd8"),
        _expr("剩余草", "remain", unit="份"),
        _answer("答案", f"{t} 天"),
    ]
    d0["status"] = {
        "before": {"text": "草还没吃完，再想想…", "color": "amber"},
        "at": {"text": f"找对了！{N} 头牛可以吃 {t} 天", "color": "green"},
        "after": {"text": "草已经不够吃了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.cows_steps(p)
    return d0


def build_phalanx(p):
    n, total, outer = p["n"], p["total"], p["outer"]
    problem = (f"一个正方形方阵一共有 {total} 人。这个方阵每边站多少人？")
    d0 = _base("phalanx", "方阵问题", problem,
               f"拖动滑块，找到正确的每边人数，让方阵总人数等于 {total}。", "每边人数")
    d0["scene"] = {
        "kind": "phalanx", "cap": "方阵点阵",
        "param": {"min": 3, "max": n + 4, "step": 1, "value": 3, "label": "每边人数", "answer": n},
        "known": {"total": total, "outer": outer},
    }
    d0["answer"] = {"n": n, "total": total, "outer": outer}
    d0["readouts"] = [
        _expr("每边", "n", unit="人"),
        _expr("总人数", "n*n", unit="人", color="#e2553f"),
        _expr("最外层", "outer", unit="人", color="#3b7dd8"),
        _answer("答案", f"每边 {n} 人"),
    ]
    d0["status"] = {
        "before": {"text": f"总人数还不是 {total}，再加人…", "color": "amber"},
        "at": {"text": f"找对了！每边 {n} 人，共 {total} 人", "color": "green"},
        "after": {"text": "每边人数超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.phalanx_steps(p)
    return d0


def build_pigeonhole(p):
    n, k, r, m, least = p["n"], p["k"], p["r"], p["m"], p["least"]
    problem = (f"把 {m} 个苹果放进 {n} 个抽屉。不管怎么放，总有一个抽屉至少放进多少个苹果？")
    d0 = _base("pigeonhole", "抽屉原理", problem,
               f"拖动滑块，找到最小的 t，使 {n} 个抽屉各放 t 个就装得下 {m} 个苹果（{m}÷{n}={k} 余 {r}）。", "至少数")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": least + 4, "step": 1, "value": 1, "label": "至少数", "answer": least},
        [{"name": "苹果", "color": "#e2553f", "expr": "m"},
         {"name": "容量(每盒放 t)", "color": "#3b7dd8", "expr": "cap"}],
        n * (least + 4), known={"m": m, "n": n, "k": k, "r": r}, diff_label="相差")
    d0["answer"] = {"least": least}
    d0["readouts"] = [
        _expr("至少数", "t", unit="个"),
        _expr("苹果", "m", unit="个", color="#e2553f"),
        _expr("容量", "cap", unit="个", color="#3b7dd8"),
        _expr("苹果−容量", "short", unit="个"),
        _answer("答案", f"至少 {least} 个"),
    ]
    d0["status"] = {
        "before": {"text": "这个数还装不下全部苹果，再加一个…", "color": "amber"},
        "at": {"text": f"找对了！至少有一个抽屉放 {least} 个", "color": "green"},
        "after": {"text": "这个数比「至少」大，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.pigeonhole_steps(p)
    return d0


def build_clock(p):
    h, angle = p["h"], p["angle"]
    problem = (f"{h} 点整的时候，时针和分针所成的较小夹角是多少度？")
    d0 = _base("clock", "时钟问题（整点夹角）", problem,
               f"拖动滑块，找到正确的夹角（每过 1 小时，时针走 30°）。", "夹角（度）")
    d0["scene"] = {
        "kind": "clock", "cap": "钟面",
        "param": {"min": 0, "max": 180, "step": 1, "value": 0, "label": "夹角（度）", "answer": angle},
        "known": {"h": h, "angle": angle},
    }
    d0["answer"] = {"angle": angle}
    d0["readouts"] = [
        _expr("夹角", "cur", unit="°"),
        _answer("整点", f"{h} 点"),
        _answer("答案", f"{angle}°"),
    ]
    d0["status"] = {
        "before": {"text": "夹角还没到，再转转…", "color": "amber"},
        "at": {"text": f"找对了！{h} 点整夹角是 {angle}°", "color": "green"},
        "after": {"text": "夹角超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.clock_steps(p)
    return d0


def build_elimination(p):
    x, y, z = p["x"], p["y"], p["z"]
    S1, S2, S3 = p["S1"], p["S2"], p["S3"]
    problem = (f"甲、乙两数的和是 {S1}，乙、丙两数的和是 {S2}，甲、丙两数的和是 {S3}。甲数是多少？")
    d0 = _base("elimination", "消去法（等量代换）", problem,
               f"拖动滑块，找到正确的甲数，让「乙+丙」正好等于 {S2}。", "甲数")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": min(S1, S3) - 1, "step": 1, "value": 1, "label": "甲数", "answer": x},
        [{"name": "甲", "color": "#e2553f", "expr": "x"},
         {"name": "乙", "color": "#3b7dd8", "expr": "y"},
         {"name": "丙", "color": "#2ecc71", "expr": "z"}],
        max(S1, S2, S3), known={"S1": S1, "S2": S2, "S3": S3})
    d0["answer"] = {"x": x, "y": y, "z": z}
    d0["readouts"] = [
        _expr("甲", "x", color="#e2553f"),
        _expr("乙", "y", color="#3b7dd8"),
        _expr("丙", "z", color="#2ecc71"),
        _expr("乙+丙", "sumBC"),
        _answer("答案", f"甲 {x} · 乙 {y} · 丙 {z}"),
    ]
    d0["status"] = {
        "before": {"text": f"乙+丙 还不是 {S2}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！甲={x}，乙={y}，丙={z}", "color": "green"},
        "after": {"text": "甲数超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.elimination_steps(p)
    return d0


def build_arithmetic_seq(p):
    a, d, n, an = p["a"], p["d"], p["n"], p["an"]
    problem = (f"一个等差数列，首项是 {a}，公差是 {d}。它的第 {n} 项是多少？")
    d0 = _base("arithmetic-seq", "等差数列", problem,
               f"拖动滑块，找到正确的第 {n} 项（每次加 {d}）。", "第 n 项")
    d0["scene"] = _bar_scene(
        {"min": a, "max": an + 2 * d, "step": 1, "value": a, "label": "第 n 项", "answer": an},
        [{"name": "首项", "color": "#e2553f", "expr": "a"},
         {"name": "第 n 项", "color": "#3b7dd8", "expr": "an"}],
        an + 2 * d, known={"a": a, "d": d, "n": n}, diff_label="增加了")
    d0["answer"] = {"an": an}
    d0["readouts"] = [
        _expr("首项", "a", color="#e2553f"),
        _expr("第 n 项", "an", color="#3b7dd8"),
        _expr("增加了", "inc"),
        _answer("目标", f"增加 {(n - 1) * d}"),
        _answer("答案", f"第 {n} 项 = {an}"),
    ]
    d0["status"] = {
        "before": {"text": f"第 {n} 项还没到，再想想…", "color": "amber"},
        "at": {"text": f"找对了！第 {n} 项 = {an}", "color": "green"},
        "after": {"text": "超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.arithmetic_seq_steps(p)
    return d0


def build_optimize(p):
    a, b, pv, q, N = p["a"], p["b"], p["p"], p["q"], p["N"]
    optK, minCost = p["optK"], p["minCost"]
    problem = (f"有 {N} 人去划船。大船每条坐 {a} 人、租金 {pv} 元；小船每条坐 {b} 人、租金 {q} 元。"
               f"怎样租船最省钱？最省要花多少元？")
    d0 = _base("optimize", "最优化 · 租船最省钱", problem,
               f"拖动滑块，找总价最低的租船方案（大船人均更便宜）。", "大船数")
    d0["scene"] = _bar_scene(
        {"min": 0, "max": N // a + 1, "step": 1, "value": 0, "label": "大船数", "answer": optK},
        [{"name": "大船费", "color": "#e2553f", "expr": "bigCost"},
         {"name": "小船费", "color": "#3b7dd8", "expr": "smallCost"}],
        N * q, known={"a": a, "b": b, "p": pv, "q": q, "N": N, "minCost": minCost},
        ref={"expr": "minCost", "label": "最优总价"})
    d0["answer"] = {"optK": optK, "minCost": minCost}
    d0["readouts"] = [
        _expr("大船", "k", unit="条"),
        _expr("小船", "small", unit="条"),
        _expr("大船费", "bigCost", unit="元", color="#e2553f"),
        _expr("小船费", "smallCost", unit="元", color="#3b7dd8"),
        _expr("总价", "cost", unit="元"),
        _answer("答案", f"大船 {optK} 条，共 {minCost} 元"),
    ]
    d0["status"] = {
        "before": {"text": "还有更省钱的方案，再试试…", "color": "amber"},
        "at": {"text": f"找对了！这是最省钱的方案，共 {minCost} 元", "color": "green"},
        "after": {"text": "这个方案不是最省的，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.optimize_steps(p)
    return d0


def build_page_digit(p):
    n, total = p["n"], p["total"]
    problem = (f"编一本书的页码（从第 1 页开始），一共用了 {total} 个数字。这本书有多少页？")
    d0 = _base("page-digit", "页码问题", problem,
               f"拖动滑块，找到正确的页数，让已用数字正好等于 {total}。", "页数")
    d0["scene"] = _bar_scene(
        {"min": 10, "max": n + 10, "step": 1, "value": 10, "label": "页数", "answer": n},
        [{"name": "1位数数字", "color": "#e2553f", "expr": "one"},
         {"name": "2位数数字", "color": "#3b7dd8", "expr": "two"}],
        2 * (n + 10), known={"total": total},
        ref={"expr": "given", "label": "目标数字数"})
    d0["answer"] = {"n": n, "total": total}
    d0["readouts"] = [
        _expr("页数", "t", unit="页"),
        _expr("1位数数字", "one", unit="个", color="#e2553f"),
        _expr("2位数数字", "two", unit="个", color="#3b7dd8"),
        _expr("共用了", "total", unit="个数字"),
        _answer("答案", f"{n} 页"),
    ]
    d0["status"] = {
        "before": {"text": f"已用数字还不是 {total}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！这本书有 {n} 页", "color": "green"},
        "after": {"text": "页数超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.page_digit_steps(p)
    return d0


def build_sum_diff_three(p):
    a, b, c, D, n, S = p["a"], p["b"], p["c"], p["D"], p["n"], p["S"]
    problem = (f"甲、乙、丙三个数的和是 {S}。甲比乙多 {D}，丙是甲的 {n} 倍。三个数各是多少？")
    d0 = _base("sum-diff-three", "三个数的和差倍", problem,
               f"拖动滑块，找到正确的甲数，让三个数之和等于 {S}。", "甲数")
    d0["scene"] = _bar_scene(
        {"min": D + 1, "max": S // (n + 1), "step": 1, "value": D + 1, "label": "甲数", "answer": a},
        [{"name": "甲", "color": "#e2553f", "var": "a"},
         {"name": "乙", "color": "#3b7dd8", "expr": "a-D"},
         {"name": "丙", "color": "#2ecc71", "expr": "n*a"}],
        S, known={"D": D, "n": n, "S": S})
    d0["answer"] = {"a": a, "b": b, "c": c}
    d0["readouts"] = [
        _expr("甲", "a", color="#e2553f"),
        _expr("乙", "a-D", color="#3b7dd8"),
        _expr("丙", "n*a", color="#2ecc71"),
        _expr("三数和", "sum"),
        _answer("答案", f"甲 {a} · 乙 {b} · 丙 {c}"),
    ]
    d0["status"] = {
        "before": {"text": f"三个数之和还不是 {S}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！甲={a}，乙={b}，丙={c}", "color": "green"},
        "after": {"text": "甲数超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.sum_diff_three_steps(p)
    return d0


# ---------------------------------------------------------------------------
# C 组：盈亏两盈/两亏 + 植树一端/两端不栽/环形
# ---------------------------------------------------------------------------

def build_profit_loss_two_gain(p):
    n, a, b, c, d, total = p["n"], p["a"], p["b"], p["c"], p["d"], p["total"]
    problem = (f"把一批苹果分给小朋友。如果每人分 {a} 个，还剩 {b} 个；"
               f"如果每人分 {c} 个，还剩 {d} 个。一共有多少个小朋友？")
    d0 = _base("profit-loss-two-gain", "盈亏 · 两盈", problem,
               f"拖动滑块，找到正确的人数，让两种分法所需总量相差 {b - d} 个。", "人数")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": n + 8, "step": 1, "value": 1, "label": "人数", "answer": n},
        [{"name": f"每人{a}个共需", "color": "#e2553f", "expr": "needA"},
         {"name": f"每人{c}个共需", "color": "#3b7dd8", "expr": "needC"}],
        (n + 8) * c, known={"a": a, "b": b, "c": c, "d": d, "total": total},
        diff_label="差额")
    d0["answer"] = {"n": n, "total": total}
    d0["readouts"] = [
        _expr("人数", "t", unit="人"),
        _expr(f"每人{a}个共需", "needA", unit="个", color="#e2553f"),
        _expr(f"每人{c}个共需", "needC", unit="个", color="#3b7dd8"),
        _expr("差额", "diff", unit="个"),
        _answer("目标差额", f"{b - d} 个"),
        _answer("答案", f"{n} 人"),
    ]
    d0["status"] = {
        "before": {"text": f"差额还不是 {b - d}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！一共有 {n} 个小朋友", "color": "green"},
        "after": {"text": "差额超过目标了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.profit_loss_two_gain_steps(p)
    return d0


def build_profit_loss_two_loss(p):
    n, a, b, c, d, total = p["n"], p["a"], p["b"], p["c"], p["d"], p["total"]
    problem = (f"把一批苹果分给小朋友。如果每人分 {a} 个，还缺 {b} 个；"
               f"如果每人分 {c} 个，还缺 {d} 个。一共有多少个小朋友？")
    d0 = _base("profit-loss-two-loss", "盈亏 · 两亏", problem,
               f"拖动滑块，找到正确的人数，让两种分法所需总量相差 {d - b} 个。", "人数")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": n + 8, "step": 1, "value": 1, "label": "人数", "answer": n},
        [{"name": f"每人{a}个共需", "color": "#e2553f", "expr": "needA"},
         {"name": f"每人{c}个共需", "color": "#3b7dd8", "expr": "needC"}],
        (n + 8) * c, known={"a": a, "b": b, "c": c, "d": d, "total": total},
        diff_label="差额")
    d0["answer"] = {"n": n, "total": total}
    d0["readouts"] = [
        _expr("人数", "t", unit="人"),
        _expr(f"每人{a}个共需", "needA", unit="个", color="#e2553f"),
        _expr(f"每人{c}个共需", "needC", unit="个", color="#3b7dd8"),
        _expr("差额", "diff", unit="个"),
        _answer("目标差额", f"{d - b} 个"),
        _answer("答案", f"{n} 人"),
    ]
    d0["status"] = {
        "before": {"text": f"差额还不是 {d - b}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！一共有 {n} 个小朋友", "color": "green"},
        "after": {"text": "差额超过目标了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.profit_loss_two_loss_steps(p)
    return d0


def build_plant_one(p):
    n, spacing, D, k = p["n"], p["d"], p["D"], p["k"]
    problem = (f"在一条长 {D} 米的路的一侧，每隔 {spacing} 米栽一棵树，只在一端栽。一共要栽多少棵树？")
    d0 = _base("plant-one", "植树 · 一端栽", problem,
               f"拖动滑块，找到正确的棵树，让每段间隔正好 {spacing} 米。", "棵树 k")
    d0["scene"] = {
        "kind": "interval", "cap": "植树（一端栽）",
        "param": {"min": 2, "max": k + 5, "step": 1, "value": 2, "label": "棵树 k", "answer": k},
        "known": {"d": spacing, "D": D, "mode": "one"},
    }
    d0["answer"] = {"k": k, "n": n}
    d0["readouts"] = [
        _expr("棵树", "k", unit="棵", color="#e2553f"),
        _expr("间隔数", "gaps", unit="段"),
        _expr("每段间隔", "spacing", unit="米", color="#3b7dd8", decimals=1),
        _answer("答案", f"{k} 棵"),
    ]
    d0["status"] = {
        "before": {"text": f"每段间隔还不是 {spacing} 米，再试试…", "color": "amber"},
        "at": {"text": f"找对了！{k} 棵树，{n} 段间隔，每段正好 {spacing} 米", "color": "green"},
        "after": {"text": "树栽得太密了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.plant_one_steps(p)
    return d0


def build_plant_none(p):
    n, spacing, D, k = p["n"], p["d"], p["D"], p["k"]
    problem = (f"在一条长 {D} 米的路的一侧，每隔 {spacing} 米栽一棵树，两端都不栽。一共要栽多少棵树？")
    d0 = _base("plant-none", "植树 · 两端不栽", problem,
               f"拖动滑块，找到正确的棵树，让每段间隔正好 {spacing} 米。", "棵树 k")
    d0["scene"] = {
        "kind": "interval", "cap": "植树（两端不栽）",
        "param": {"min": 1, "max": k + 5, "step": 1, "value": 1, "label": "棵树 k", "answer": k},
        "known": {"d": spacing, "D": D, "mode": "none"},
    }
    d0["answer"] = {"k": k, "n": n}
    d0["readouts"] = [
        _expr("棵树", "k", unit="棵", color="#e2553f"),
        _expr("间隔数", "gaps", unit="段"),
        _expr("每段间隔", "spacing", unit="米", color="#3b7dd8", decimals=1),
        _answer("答案", f"{k} 棵"),
    ]
    d0["status"] = {
        "before": {"text": f"每段间隔还不是 {spacing} 米，再试试…", "color": "amber"},
        "at": {"text": f"找对了！{k} 棵树，{n} 段间隔，每段正好 {spacing} 米", "color": "green"},
        "after": {"text": "树栽得太密了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.plant_none_steps(p)
    return d0


def build_plant_ring(p):
    n, spacing, D, k = p["n"], p["d"], p["D"], p["k"]
    problem = (f"在一个周长 {D} 米的圆形池塘边，每隔 {spacing} 米栽一棵树。一共要栽多少棵树？")
    d0 = _base("plant-ring", "植树 · 环形", problem,
               f"拖动滑块，找到正确的棵树，让每段间隔正好 {spacing} 米。", "棵树 k")
    d0["scene"] = {
        "kind": "interval", "cap": "植树（环形）",
        "param": {"min": 2, "max": k + 5, "step": 1, "value": 2, "label": "棵树 k", "answer": k},
        "known": {"d": spacing, "D": D, "mode": "ring"},
    }
    d0["answer"] = {"k": k, "n": n}
    d0["readouts"] = [
        _expr("棵树", "k", unit="棵", color="#e2553f"),
        _expr("间隔数", "gaps", unit="段"),
        _expr("每段间隔", "spacing", unit="米", color="#3b7dd8", decimals=1),
        _answer("答案", f"{k} 棵"),
    ]
    d0["status"] = {
        "before": {"text": f"每段间隔还不是 {spacing} 米，再试试…", "color": "amber"},
        "at": {"text": f"找对了！{k} 棵树，{n} 段间隔，每段正好 {spacing} 米", "color": "green"},
        "after": {"text": "树栽得太密了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.plant_ring_steps(p)
    return d0


def build_overlap_venn(p):
    a, b, c, X, Y, T = p["a"], p["b"], p["c"], p["X"], p["Y"], p["T"]
    problem = (f"三（1）班语文优秀的有 {X} 人，数学优秀的有 {Y} 人，"
               f"至少一科优秀的有 {T} 人。两科都优秀的有几人？")
    d0 = _base("overlap-venn", "容斥 · 韦恩图", problem,
               f"拖动韦恩图下方的手柄（或滑块），调整「两科都优秀」的人数，"
               f"让「至少一科优秀」正好等于 {T} 人。", "两科都优 c")
    cMax = min(X, Y) - 1
    d0["scene"] = {
        "kind": "venn", "cap": "韦恩图（容斥）",
        "world": {"xMax": 10, "yMax": 8, "pad": 30},
        "points": [
            {"name": "H", "x": 1, "y": 1.2, "snap": "grid", "constraint": "h-line",
             "min": 1, "max": cMax, "color": "#f5a623", "label": "两科都优"},
        ],
        "dragToT": "H",
        "known": {"X": X, "Y": Y, "T": T},
        "param": {"min": 1, "max": cMax, "step": 1, "value": 1,
                  "label": "两科都优 c", "answer": c},
    }
    d0["answer"] = {"c": c, "X": X, "Y": Y, "T": T}
    d0["readouts"] = [
        _expr("只语文", "onlyA", unit="人", color="#e2553f"),
        _expr("只数学", "onlyB", unit="人", color="#3b7dd8"),
        _expr("两科都优", "c", unit="人", color="#f5a623"),
        _expr("至少一科", "total", unit="人"),
        _answer("答案", f"{c} 人"),
    ]
    d0["status"] = {
        "before": {"text": f"「至少一科优秀」还不是 {T} 人，再拖动手柄…", "color": "amber"},
        "at": {"text": f"找对了！两科都优 = {c} 人（{X} + {Y} − {T}）", "color": "green"},
        "after": {"text": "两科都优太多了，往回拖…", "color": "blue"},
    }
    d0["steps"] = steps.overlap_venn_steps(p)
    return d0


def build_match_count(p):
    m, n, total = p["m"], p["n"], p["total"]
    problem = (f"小明有 {m} 件上衣、{n} 条裤子。每天穿 1 件上衣和 1 条裤子，"
               f"一共有多少种不同的搭配？")
    d = _base("match-count", "排列组合 · 搭配", problem,
              "拖动滑块（或点播放），把上衣和裤子一条条连起来，数一数一共有几种搭配。",
              "已搭配数 t")
    d["scene"] = {
        "kind": "link-graph", "cap": "搭配连线图",
        "known": {"m": m, "n": n, "total": total},
        "param": {"min": 1, "max": total, "step": 1, "value": 1,
                  "label": "已搭配数 t", "answer": total},
    }
    d["answer"] = {"total": total}
    d["readouts"] = [
        _expr("上衣", "m", unit="件", color="#e2553f"),
        _expr("裤子", "n", unit="条", color="#3b7dd8"),
        _expr("已搭配", "matched", unit="种"),
        _answer("答案", f"{total} 种"),
    ]
    d["status"] = {
        "before": {"text": "还没连完，继续连线…", "color": "amber"},
        "at": {"text": f"找对了！{m} × {n} = {total} 种搭配", "color": "green"},
        "after": {"text": "已经超过总数啦！", "color": "blue"},
    }
    d["steps"] = steps.match_count_steps(p)
    return d


def build_logic_table(p):
    people, sports, perm = p["people"], p["sports"], p["perm"]
    cond1, cond2, cond3 = p["cond1"], p["cond2"], p["cond3"]
    mapping = "；".join(f"{people[i]} = {sports[perm[i]]}" for i in range(3))
    problem = (f"甲、乙、丙三位同学分别喜欢跑步、游泳、跳高中的一项，且各不相同。"
               f"已知：{cond1}；{cond2}。三人各喜欢什么运动？")
    d = _base("logic-table", "逻辑推理 · 排除法", problem,
              "把每个人下面的圆点拖到正确的运动那一列（也可以把滑块拨到头看答案）。",
              "提示步数")
    colors = ["#e2553f", "#3b7dd8", "#2ecc71"]
    yrow = [3, 2, 1]
    pts = []
    for i in range(3):
        pts.append({"name": people[i], "x": 1, "y": yrow[i], "snap": "grid",
                    "constraint": "h-line", "min": 1, "max": 3,
                    "ax": perm[i] + 1, "ay": yrow[i], "color": colors[i],
                    "label": people[i]})
    d["scene"] = {
        "kind": "logic-table", "cap": "逻辑推理（排除法表）",
        "world": {"xMax": 4, "yMax": 4, "pad": 40},
        "points": pts,
        "known": {"people": people, "sports": sports, "perm": perm,
                  "cond1": cond1, "cond2": cond2, "cond3": cond3},
        "param": {"min": 0, "max": 3, "step": 1, "value": 0,
                  "label": "提示步数", "answer": 3},
    }
    d["answer"] = {"mapping": mapping}
    d["readouts"] = [
        _expr("已答对", "correct", unit="人"),
        _answer("答案", mapping),
    ]
    d["status"] = {
        "before": {"text": "再想想线索，把每个人都拖到正确的位置…", "color": "amber"},
        "at": {"text": f"全对！{mapping}", "color": "green"},
        "after": {"text": "（已提示出全部答案）", "color": "blue"},
    }
    d["steps"] = steps.logic_table_steps(p)
    return d


def build_pancake(p):
    n, k, t, sides, total = p["n"], p["k"], p["t"], p["sides"], p["total"]
    problem = (f"烙 {n} 张饼，每张饼要烙两面，平底锅一次最多烙 {k} 张，"
               f"每面要烙 {t} 分钟。最少要多少分钟？")
    d = _base("pancake", "烙饼问题", problem,
              "拖动滑块（或点播放），看饼在锅里交替烙的过程，找到最少时间。",
              "时间（分钟）")
    d["scene"] = {
        "kind": "timeline", "cap": "烙饼时间轴",
        "known": {"n": n, "k": k, "t": t, "sides": sides, "total": total},
        "param": {"min": 0, "max": total, "step": 1, "value": 0,
                  "label": "时间（分钟）", "answer": total},
    }
    d["answer"] = {"total": total}
    d["readouts"] = [
        _expr("饼数", "n", unit="张"),
        _expr("已烙好", "done", unit="面"),
        _expr("总共", "sides", unit="面"),
        _answer("答案", f"{total} 分钟"),
    ]
    d["status"] = {
        "before": {"text": "还没烙完，继续…", "color": "amber"},
        "at": {"text": f"找对了！最少 {total} 分钟（{n} 张 × 2 面 ÷ 每次 2 面 × {t} 分钟）", "color": "green"},
        "after": {"text": "时间已经够了，全烙好啦！", "color": "blue"},
    }
    d["steps"] = steps.pancake_steps(p)
    return d


def build_tianji(p):
    order, qw_speed, tj_speed = p["order"], p["qw_speed"], p["tj_speed"]
    ans_lane, init_lane = p["ans_lane"], p["init_lane"]
    qw_desc = "、".join(f"第{j + 1}场齐王出{order[j]}" for j in range(3))
    problem = (f"田忌和齐王赛马，各有上、中、下三匹马。齐王出马顺序为：{qw_desc}。"
               f"田忌的马每档都比齐王同档慢一点点（田忌上胜齐王中、田忌中胜齐王下、田忌下最慢）。"
               f"田忌怎样安排出场才能赢 2 场？")
    d = _base("tianji", "田忌赛马", problem,
              "把田忌的三匹马拖到正确的出场位置（第 1/2/3 场），赢下 2 场就成功了。",
              "提示")
    hmap = {"上": "tianji-up", "中": "tianji-mid", "下": "tianji-low"}
    colors = {"上": "#e2553f", "中": "#3b7dd8", "下": "#2ecc71"}
    yrow = {"上": 3, "中": 2, "下": 1}
    pts = []
    for tj in ["上", "中", "下"]:
        pts.append({"name": hmap[tj], "horse": tj, "x": init_lane[tj], "y": yrow[tj],
                    "snap": "grid", "constraint": "h-line", "min": 1, "max": 3,
                    "ax": ans_lane[tj], "ay": yrow[tj], "color": colors[tj],
                    "label": "田忌" + tj})
    d["scene"] = {
        "kind": "matchup", "cap": "田忌赛马（对阵表）",
        "world": {"xMax": 4, "yMax": 5, "pad": 36},
        "points": pts,
        "known": {"order": order, "qw_speed": qw_speed, "tj_speed": tj_speed},
        "param": {"min": 0, "max": 1, "step": 1, "value": 0, "label": "提示", "answer": 1},
    }
    d["answer"] = {"wins": 2}
    d["readouts"] = [
        _expr("已胜", "wins", unit="局"),
        _expr("目标", "target", unit="局"),
        _answer("答案", "田忌胜 2 局（下对王上、上对王中、中对王下）"),
    ]
    d["status"] = {
        "before": {"text": "还没赢够 2 场，调整田忌的出场顺序…", "color": "amber"},
        "at": {"text": "赢了！田忌胜 2 场（下对王上、上对王中、中对王下）", "color": "green"},
        "after": {"text": "（已提示答案）", "color": "blue"},
    }
    d["steps"] = steps.tianji_steps(p)
    return d


def build_fraction_more_less(p):
    mode, k, m, B, D, A = p["mode"], p["k"], p["m"], p["B"], p["D"], p["A"]
    word = "多" if mode == "多" else "少"
    problem = f"乙有 {B} 个。甲比乙{word} 1/{k}。甲有多少个？"
    title = f"分数 · {word}几分之几"
    hint = f"拖动滑块，找到正确的甲，让「甲比乙{word}的部分」正好是乙的 1/{k}。"
    if mode == "多":
        param = {"min": B + 1, "max": A, "step": 1, "value": B + 1, "label": "甲 A", "answer": A}
        scale = A
    else:
        param = {"min": 1, "max": B - 1, "step": 1, "value": 1, "label": "甲 A", "answer": A}
        scale = B
    d0 = _base("fraction-more-less", title, problem, hint, "甲 A")
    d0["scene"] = _bar_scene(
        param,
        [{"name": "乙（单位1）", "color": "#3b7dd8", "expr": "B"},
         {"name": "甲", "color": "#e2553f", "var": "A"}],
        scale, known={"B": B, "D": D, "k": k, "mode": mode}, diff_label="相差")
    d0["answer"] = {"A": A, "D": D, "k": k}
    d0["readouts"] = [
        _expr("乙（单位1）", "B", unit="个", color="#3b7dd8"),
        _expr("甲", "A", unit="个", color="#e2553f"),
        _expr("相差", "diff", unit="个"),
        _expr("乙÷相差", "den", decimals=0),
        _answer("答案", f"甲 = {A} 个（比乙{word} 1/{k}）"),
    ]
    d0["status"] = {
        "before": {"text": f"甲比乙{word}的还不是 1/{k}，再试试…", "color": "amber"},
        "at": {"text": f"找对了！甲 = {A}，比乙{word} {D}（乙的 1/{k}）", "color": "green"},
        "after": {"text": "甲超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.fraction_more_less_steps(p)
    return d0


def build_interest(p):
    P, r, n, interest = p["P"], p["r"], p["n"], p["interest"]
    problem = f"小明把 {P} 元存入银行，年利率 {r}%，存 {n} 年。到期能拿到多少元利息？"
    d0 = _base("interest", "百分数 · 利率利息", problem,
               "拖动滑块，找到正确的利息（本金 × 利率 × 存期）。", "利息（元）")
    d0["scene"] = _bar_scene(
        {"min": 1, "max": interest + 5, "step": 1, "value": 1,
         "label": "利息（元）", "answer": interest},
        [{"name": "本金", "color": "#3b7dd8", "expr": "P"},
         {"name": "利息", "color": "#e2553f", "var": "interest"}],
        P, known={"P": P, "r": r, "n": n}, diff_label="利息")
    d0["answer"] = {"interest": interest}
    d0["readouts"] = [
        _expr("本金", "P", unit="元", color="#3b7dd8"),
        _expr("利息", "interest", unit="元", color="#e2553f"),
        _answer("利率", f"{r}% × {n} 年"),
        _answer("答案", f"{interest} 元"),
    ]
    d0["status"] = {
        "before": {"text": f"利息还不是 {interest} 元，再试试…", "color": "amber"},
        "at": {"text": f"找对了！{P} × {r}% × {n} = {interest} 元", "color": "green"},
        "after": {"text": "利息超过答案了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.interest_steps(p)
    return d0


def build_plant_two_sides(p):
    n, spacing, D, k, total = p["n"], p["d"], p["D"], p["k"], p["total"]
    problem = (f"在一条长 {D} 米的路的两侧，每隔 {spacing} 米栽一棵树，两端都栽。"
               f"一共要栽多少棵树？")
    d0 = _base("plant-two-sides", "植树 · 两侧都栽", problem,
               f"拖动滑块，找到正确的单侧棵树，让每段间隔正好 {spacing} 米。",
               "单侧棵树 k")
    d0["scene"] = {
        "kind": "interval", "cap": "植树（两侧都栽）",
        "param": {"min": 2, "max": k + 5, "step": 1, "value": 2,
                  "label": "单侧棵树 k", "answer": k},
        "known": {"d": spacing, "D": D, "mode": "two-sides"},
    }
    d0["answer"] = {"k": k, "n": n, "total": total}
    d0["readouts"] = [
        _expr("单侧棵树", "k", unit="棵", color="#e2553f"),
        _expr("两侧棵树", "2*k", unit="棵", color="#3b7dd8"),
        _expr("间隔数", "gaps", unit="段"),
        _expr("每段间隔", "spacing", unit="米", decimals=1),
        _answer("答案", f"共 {total} 棵"),
    ]
    d0["status"] = {
        "before": {"text": f"每段间隔还不是 {spacing} 米，再试试…", "color": "amber"},
        "at": {"text": f"找对了！单侧 {k} 棵，两侧共 {total} 棵", "color": "green"},
        "after": {"text": "树栽得太密了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.plant_two_sides_steps(p)
    return d0


def build_equation_balance(p):
    x, a, b, right = p["x"], p["a"], p["b"], p["right"]
    problem = f"解方程：{a}x + {b} = {right}。x 等于多少？"
    d0 = _base("equation-balance", "方程 · 天平图", problem,
               "拖动天平上的砝码 x（或拨滑块），让天平两边平衡。", "x")
    d0["scene"] = {
        "kind": "balance", "cap": "天平图（解方程）",
        "world": {"xMax": right + 4, "yMax": 6, "pad": 40},
        "points": [
            {"name": "xW", "x": 1, "y": 2, "snap": "grid", "constraint": "h-line",
             "min": 1, "max": x + 4, "ax": x, "ay": 2, "color": "#e2553f", "label": "x"},
        ],
        "dragToT": "xW",
        "known": {"a": a, "b": b, "right": right},
        "param": {"min": 1, "max": x + 4, "step": 1, "value": 1, "label": "x", "answer": x},
    }
    d0["answer"] = {"x": x}
    d0["readouts"] = [
        _expr("左盘", "left", unit="g", color="#e2553f"),
        _expr("右盘", "right", unit="g", color="#3b7dd8"),
        _expr("x", "x"),
        _answer("答案", f"x = {x}"),
    ]
    d0["status"] = {
        "before": {"text": "左盘还轻（左边 < 右边），加大 x…", "color": "amber"},
        "at": {"text": f"平衡了！{a}×{x} + {b} = {right}，x = {x}", "color": "green"},
        "after": {"text": "左盘太重了（左边 > 右边），减小 x…", "color": "blue"},
    }
    d0["steps"] = steps.equation_balance_steps(p)
    return d0


def build_triangle_equal(p):
    b, h, s0, mid, area = p["b"], p["h"], p["s0"], p["mid"], p["area"]
    problem = (f"一个三角形，底 {b} 格，高 {h} 格。拖动顶点 C 沿虚线左右移动"
               f"（高不变），面积始终是 {b} × {h} ÷ 2 = {area} 格²（等底等高，面积相等）。"
               f"把 C 拖到底边中点正上方（第 {mid} 格），变成等腰三角形。")
    d = _base("triangle-equal", "三角形 · 等底等高", problem,
              "拖动顶点 C（沿虚线左右移动，高不变），或拨动滑块。", "顶点 C 的横坐标")
    d["scene"] = {
        "kind": "geodrag", "cap": "三角形（等底等高 · 等积变形）",
        "world": {"xMax": b + 2, "yMax": h + 3, "pad": 36},
        "points": [
            {"name": "A", "x": 0, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "A"},
            {"name": "B", "x": b, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "B"},
            {"name": "C", "x": s0, "y": h, "snap": "grid", "constraint": "h-line",
             "min": 0, "max": b, "color": "#e2553f", "label": "C"},
        ],
        "poly": ["A", "B", "C"],
        "fill": "rgba(59,125,216,.12)", "stroke": "#3b7dd8",
        "target": {"name": "C", "x": mid, "y": h},
        "dragToT": "C",
        "param": {"min": 0, "max": b, "step": 1, "value": s0,
                  "label": "顶点 C 的横坐标", "answer": mid},
    }
    d["answer"] = {"area": area, "b": b, "h": h, "mid": mid}
    d["readouts"] = [
        _expr("底", "Bx-Ax", unit="格"),
        _expr("高", "Cy-Ay", unit="格"),
        _expr("顶点 C 横坐标", "Cx", unit="格", color="#e2553f"),
        _expr("面积", "(Bx-Ax)*(Cy-Ay)/2", unit="格²", color="#3b7dd8"),
        _answer("答案", f"面积 = {area} 格²（等底等高）"),
    ]
    d["status"] = {
        "before": {"text": "顶点 C 还没到中点正上方，继续拖动…", "color": "amber"},
        "at": {"text": f"找对了！顶点 C 在中点正上方（第 {mid} 格），是等腰三角形；面积仍是 {area} 格²", "color": "green"},
        "after": {"text": f"顶点 C 过了中点（第 {mid} 格），往回拖；面积仍是 {area} 格²", "color": "blue"},
    }
    d["steps"] = steps.triangle_equal_steps(p)
    return d


def build_para_equal(p):
    """平行四边形·等底等高（联动顶点 D/C + h-line 拖动，割补法拉正为长方形）。"""
    b, h, o, area = p["b"], p["h"], p["o"], p["area"]
    ax = 2                       # A 的横坐标（居中，留出左右斜动空间）
    problem = (f"一个平行四边形，底 {b} 格，高 {h} 格。拖动顶点 D 沿虚线左右移动"
               f"（对顶点 C 跟着联动，高不变），面积始终是 {b} × {h} = {area} 格²（等底等高）。"
               f"把 D 拖到 A 的正上方（第 {ax} 格），变成长方形。")
    d = _base("para-equal", "平行四边形 · 等底等高", problem,
              "拖动顶点 D（沿虚线左右移动，C 联动，高不变），或拨动滑块。", "顶点 D 的横坐标")
    d["scene"] = {
        "kind": "geodrag", "cap": "平行四边形（等底等高 · 割补法）",
        "world": {"xMax": b + 5, "yMax": h + 3, "pad": 36},
        "points": [
            {"name": "A", "x": ax, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "A"},
            {"name": "B", "x": ax + b, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "B"},
            {"name": "D", "x": ax + o, "y": h, "snap": "grid", "constraint": "h-line",
             "min": 0, "max": ax + 2, "color": "#e2553f", "label": "D"},
            {"name": "C", "x": ax + o + b, "y": h, "fixed": True, "color": "#3b7dd8", "label": "C",
             "depend": {"of": "D", "dx": b, "dy": 0}},
        ],
        "poly": ["A", "B", "C", "D"],
        "fill": "rgba(59,125,216,.12)", "stroke": "#3b7dd8",
        "target": {"name": "D", "x": ax, "y": h},
        "dragToT": "D",
        "param": {"min": 0, "max": ax + 2, "step": 1, "value": ax + o,
                  "label": "顶点 D 的横坐标", "answer": ax},
    }
    d["answer"] = {"area": area, "b": b, "h": h}
    d["readouts"] = [
        _expr("底", "Bx-Ax", unit="格"),
        _expr("高", "Dy-Ay", unit="格"),
        _expr("顶点 D 横坐标", "Dx", unit="格", color="#e2553f"),
        _expr("面积", "(Bx-Ax)*(Dy-Ay)", unit="格²", color="#3b7dd8"),
        _answer("答案", f"面积 = {area} 格²（等底等高）"),
    ]
    d["status"] = {
        "before": {"text": "还没拉正成长方形，继续拖动 D…", "color": "amber"},
        "at": {"text": f"找对了！D 在 A 的正上方，变成长方形；面积仍是 {area} 格²（等底等高）", "color": "green"},
        "after": {"text": "D 拖过头了，往回拖到 A 的正上方…", "color": "blue"},
    }
    d["steps"] = steps.para_equal_steps(p)
    return d


def build_tri_height(p):
    """三角形·已知底求高（v-line 拖动改高，面积公式逆用）。"""
    b, h, y0, mid, area = p["b"], p["h"], p["y0"], p["mid"], p["area"]
    problem = (f"一个三角形，底 {b} 格。要使面积等于 {area} 格²，高应该是多少格？"
               f"拖动顶点 C 上下移动（沿底边中点的竖线，改变高），把面积调到 {area} 格²。")
    d = _base("tri-height", "三角形 · 已知底求高", problem,
              "拖动顶点 C 上下移动（沿竖线改变高），或拨动滑块。", "高（格）")
    d["scene"] = {
        "kind": "geodrag", "cap": "三角形（底 × 高 ÷ 2）",
        "world": {"xMax": b + 2, "yMax": h + 3, "pad": 36},
        "points": [
            {"name": "A", "x": 0, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "A"},
            {"name": "B", "x": b, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "B"},
            {"name": "C", "x": mid, "y": y0, "snap": "grid", "constraint": "v-line",
             "min": 1, "max": h + 2, "color": "#e2553f", "label": "C"},
        ],
        "poly": ["A", "B", "C"],
        "fill": "rgba(59,125,216,.12)", "stroke": "#3b7dd8",
        "target": {"name": "C", "x": mid, "y": h},
        "dragToT": "C",
        "param": {"min": 1, "max": h + 2, "step": 1, "value": y0,
                  "label": "高（格）", "answer": h},
    }
    d["answer"] = {"h": h, "area": area, "b": b}
    d["readouts"] = [
        _expr("底", "Bx-Ax", unit="格"),
        _expr("高", "Cy-Ay", unit="格", color="#e2553f"),
        _expr("面积", "(Bx-Ax)*(Cy-Ay)/2", unit="格²", color="#3b7dd8"),
        _answer("答案", f"高 = {h} 格（面积 {area} 格²）"),
    ]
    d["status"] = {
        "before": {"text": f"面积还不到 {area} 格²，把 C 往上拉高…", "color": "amber"},
        "at": {"text": f"找对了！高 {h} 格时面积 = {b} × {h} ÷ 2 = {area} 格²", "color": "green"},
        "after": {"text": f"太高了，面积超过 {area} 格²，把 C 往下调…", "color": "blue"},
    }
    d["steps"] = steps.tri_height_steps(p)
    return d


def build_trapezoid(p):
    """梯形·等积变形（上底沿 h-line 平移，目标等腰梯形）。"""
    b, u, h, o0, mid, area = p["b"], p["u"], p["h"], p["o0"], p["mid"], p["area"]
    problem = (f"一个梯形，下底 {b} 格，上底 {u} 格，高 {h} 格。拖动顶点 D 左右移动"
               f"（上底跟着平移，高不变），面积始终是 {area} 格²。把 D 拖到第 {mid} 格，变成等腰梯形。")
    d = _base("trapezoid", "梯形 · 等积变形", problem,
              "拖动顶点 D（沿虚线左右移动，上底平移），或拨动滑块。", "顶点 D 的横坐标")
    d["scene"] = {
        "kind": "geodrag", "cap": "梯形（(上底+下底)×高÷2）",
        "world": {"xMax": b + 2, "yMax": h + 3, "pad": 36},
        "points": [
            {"name": "A", "x": 0, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "A"},
            {"name": "B", "x": b, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "B"},
            {"name": "D", "x": o0, "y": h, "snap": "grid", "constraint": "h-line",
             "min": 0, "max": b - u, "color": "#e2553f", "label": "D"},
            {"name": "C", "x": o0 + u, "y": h, "fixed": True, "color": "#3b7dd8", "label": "C",
             "depend": {"of": "D", "dx": u, "dy": 0}},
        ],
        "poly": ["A", "B", "C", "D"],
        "fill": "rgba(59,125,216,.12)", "stroke": "#3b7dd8",
        "target": {"name": "D", "x": mid, "y": h},
        "dragToT": "D",
        "param": {"min": 0, "max": b - u, "step": 1, "value": o0,
                  "label": "顶点 D 的横坐标", "answer": mid},
    }
    d["answer"] = {"area": area, "b": b, "u": u, "h": h}
    d["readouts"] = [
        _expr("下底", "Bx-Ax", unit="格"),
        _expr("上底", "Cx-Dx", unit="格"),
        _expr("高", "Dy-Ay", unit="格"),
        _expr("顶点 D 横坐标", "Dx", unit="格", color="#e2553f"),
        _expr("面积", "(Bx-Ax+Cx-Dx)*(Dy-Ay)/2", unit="格²", color="#3b7dd8"),
        _answer("答案", f"面积 = {area} 格²（等积变形）"),
    ]
    d["status"] = {
        "before": {"text": "还没变成等腰梯形，继续拖动 D…", "color": "amber"},
        "at": {"text": f"找对了！D 在第 {mid} 格，是等腰梯形；面积仍是 {area} 格²", "color": "green"},
        "after": {"text": f"D 过了中点，往回拖；面积仍是 {area} 格²", "color": "blue"},
    }
    d["steps"] = steps.trapezoid_steps(p)
    return d


def build_recompose(p):
    """平行四边形·割补法（拖 G 把左侧三角形平移到右侧，拼成长方形）。"""
    b, h, o, area = p["b"], p["h"], p["o"], p["area"]
    problem = (f"一个平行四边形，底 {b} 格，高 {h} 格。拖动红色三角形（割补），"
               f"把它从左边割下来、平移到右边，拼成一个长方形。面积不变，还是 {area} 格²。")
    d = _base("recompose", "平行四边形 · 割补法", problem,
              "拖动红色三角形的顶点 G，把它从左边移到右边拼成长方形。", "三角形平移量（格）")
    d["scene"] = {
        "kind": "geodrag", "cap": "平行四边形（割补法 · 平移拼长方形）",
        "world": {"xMax": b + o + 2, "yMax": h + 3, "pad": 36},
        "points": [
            # 隐藏锚点 A(0,0)：仅用于读数「底 = Bx-Ax」
            {"name": "A", "x": 0, "y": 0, "fixed": True, "hidden": True},
            # 剩余块（梯形）四个角：固定，蓝色
            {"name": "E", "x": o, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "E"},
            {"name": "B", "x": b, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "B"},
            {"name": "C", "x": b + o, "y": h, "fixed": True, "color": "#3b7dd8", "label": "C"},
            {"name": "D", "x": o, "y": h, "fixed": True, "color": "#3b7dd8", "label": "D"},
            # 被割下的三角形：G 是拖动点，G1/G2 为联动点（隐藏）
            {"name": "G", "x": 0, "y": 0, "snap": "grid", "constraint": "h-line",
             "min": 0, "max": b, "color": "#e2553f", "label": "拖动"},
            {"name": "G1", "x": o, "y": 0, "fixed": True, "hidden": True,
             "depend": {"of": "G", "dx": o, "dy": 0}},
            {"name": "G2", "x": o, "y": h, "fixed": True, "hidden": True,
             "depend": {"of": "G", "dx": o, "dy": h}},
        ],
        "poly": ["E", "B", "C", "D"],
        "fill": "rgba(59,125,216,.14)", "stroke": "#3b7dd8",
        "extra": [{"poly": ["G", "G1", "G2"], "fill": "rgba(226,85,63,.30)", "stroke": "#e2553f"}],
        "target": {"name": "G", "x": b, "y": 0},
        "dragToT": "G",
        "param": {"min": 0, "max": b, "step": 1, "value": 0,
                  "label": "三角形平移量（格）", "answer": b},
    }
    d["answer"] = {"area": area, "b": b, "h": h}
    d["readouts"] = [
        _expr("底", "Bx-Ax", unit="格"),
        _expr("高", "Cy-Ay", unit="格"),
        _expr("平移量", "Gx", unit="格", color="#e2553f"),
        _expr("面积", "(Bx-Ax)*(Cy-Ay)", unit="格²", color="#3b7dd8"),
        _answer("答案", f"面积 = {area} 格²（拼成长方形）"),
    ]
    d["status"] = {
        "before": {"text": "把红色三角形往右拖，割下来补到右边…", "color": "amber"},
        "at": {"text": f"拼好了！变成长方形，面积 = {b} × {h} = {area} 格²", "color": "green"},
        "after": {"text": f"已经拼成长方形了，面积 {area} 格² 不变", "color": "blue"},
    }
    d["steps"] = steps.recompose_steps(p)
    return d


def build_circle(p):
    """圆·周长：半径滑块驱动直径/周长，圆周率取 3。"""
    r, r0, dia, C = p["r"], p["r0"], p["d"], p["C"]
    problem = (f"一个圆，半径 {r} 格。圆周率取 3，这个圆的周长是多少格？"
               f"把半径拨到 {r} 格，看看周长是不是直径 × 3。")
    d = _base("circle", "圆 · 周长（圆周率取 3）", problem,
              "拨动滑块改变半径，看直径和周长怎么跟着变。", "半径（格）")
    d["scene"] = {
        "kind": "circle", "cap": "圆（周长 = 直径 × 3，圆周率取 3）",
        "world": {"xMax": max(2 * r + 4, C + 2), "yMax": 2 * r + 6, "pad": 36},
        "param": {"min": 1, "max": 6, "step": 1, "value": r0,
                  "label": "半径（格）", "answer": r},
    }
    d["answer"] = {"r": r, "d": dia, "C": C}
    d["readouts"] = [
        _expr("半径", "r", unit="格", color="#e2553f"),
        _expr("直径", "d", unit="格", color="#3b7dd8"),
        _expr("周长", "C", unit="格", color="#e2553f"),
        _answer("答案", f"周长 = 直径 × 3 = {dia} × 3 = {C} 格"),
    ]
    d["status"] = {
        "before": {"text": "继续拨动半径，看直径和周长怎么变…", "color": "amber"},
        "at": {"text": f"找对了！半径 {r} 格，周长 = 直径 × 3 = {dia} × 3 = {C} 格", "color": "green"},
        "after": {"text": f"半径超过 {r} 格了，往回拨一点", "color": "blue"},
    }
    d["steps"] = steps.circle_steps(p)
    return d


def build_circle_area(p):
    """圆·面积：半径滑块驱动直径/面积，圆周率取 3。"""
    r, r0, dia, S = p["r"], p["r0"], p["d"], p["S"]
    problem = (f"一个圆，半径 {r} 格。圆周率取 3，这个圆的面积是多少格²？"
               f"把半径拨到 {r} 格，看看面积是不是 3 个 r×r 方格。")
    d = _base("circle-area", "圆 · 面积（圆周率取 3）", problem,
              "拨动滑块改变半径，看面积怎么跟着变。", "半径（格）")
    d["scene"] = {
        "kind": "circle", "mode": "area",
        "cap": "圆（面积 = 半径² × 3，圆周率取 3）",
        "world": {"xMax": 5 * r + 5, "yMax": 2 * r + 6, "pad": 36},
        "param": {"min": 1, "max": 6, "step": 1, "value": r0,
                  "label": "半径（格）", "answer": r},
    }
    d["answer"] = {"r": r, "d": dia, "S": S}
    d["readouts"] = [
        _expr("半径", "r", unit="格", color="#e2553f"),
        _expr("直径", "d", unit="格", color="#3b7dd8"),
        _expr("面积", "S", unit="格²", color="#e2553f"),
        _answer("答案", f"面积 = 半径² × 3 = {r}² × 3 = {S} 格²"),
    ]
    d["status"] = {
        "before": {"text": "继续拨动半径，看面积怎么变…", "color": "amber"},
        "at": {"text": f"找对了！半径 {r} 格，面积 = {r}² × 3 = {S} 格²", "color": "green"},
        "after": {"text": f"半径超过 {r} 格了，往回拨一点", "color": "blue"},
    }
    d["steps"] = steps.circle_area_steps(p)
    return d


def build_semicircle(p):
    """半圆·周长：半径滑块驱动半圆弧长/直径/半圆周长，圆周率取 3。"""
    r, r0, dia, arc, C = p["r"], p["r0"], p["d"], p["arc"], p["C"]
    problem = (f"一个半圆，半径 {r} 格。圆周率取 3，这个半圆的周长是多少格？"
               f"把半径拨到 {r} 格，看看半圆周长是不是半圆弧 + 直径。")
    d = _base("semicircle", "半圆 · 周长（圆周率取 3）", problem,
              "拨动滑块改变半径，看半圆周长怎么跟着变。", "半径（格）")
    d["scene"] = {
        "kind": "circle", "mode": "semicircle",
        "cap": "半圆（周长 = 半圆弧 + 直径，圆周率取 3）",
        "world": {"xMax": 5 * r + 2, "yMax": 2 * r + 6, "pad": 36},
        "param": {"min": 1, "max": 6, "step": 1, "value": r0,
                  "label": "半径（格）", "answer": r},
    }
    d["answer"] = {"r": r, "d": dia, "arc": arc, "C": C}
    d["readouts"] = [
        _expr("半径", "r", unit="格", color="#e2553f"),
        _expr("直径", "d", unit="格", color="#3b7dd8"),
        _expr("半圆弧长", "arc", unit="格", color="#e2553f"),
        _expr("半圆周长", "C", unit="格", color="#3b7dd8"),
        _answer("答案", f"半圆周长 = 半圆弧 + 直径 = {arc} + {dia} = {C} 格"),
    ]
    d["status"] = {
        "before": {"text": "继续拨动半径，看半圆周长怎么变…", "color": "amber"},
        "at": {"text": f"找对了！半圆周长 = {arc} + {dia} = {C} 格（别漏掉直径）", "color": "green"},
        "after": {"text": f"半径超过 {r} 格了，往回拨一点", "color": "blue"},
    }
    d["steps"] = steps.semicircle_steps(p)
    return d
