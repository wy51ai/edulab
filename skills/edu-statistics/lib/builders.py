# -*- coding: utf-8 -*-
"""题型 → schema 组装。统计题复用统一骨架 _base / _expr / _answer。"""
import steps


def _base(type_slug, title, problem, hint, slider_label):
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
# 统计图表
# ---------------------------------------------------------------------------

def build_stat_chart(p):
    a, b, c, d = p["a"], p["b"], p["c"], p["d"]
    T, maxBar = p["T"], p["maxBar"]
    problem = (f"四（1）班统计同学们最喜欢的运动项目（每人只选一项）："
               f"跳绳 {a} 人、篮球 {b} 人、足球 {c} 人，其余的人喜欢跑步。"
               f"全班共 {T} 人。喜欢跑步的有多少人？")
    d0 = _base("stat-chart", "条形统计图 · 补全数据", problem,
               f"拖动绿色「跑步」柱顶，把柱补到正确高度（人数为整数）；"
               f"当全班合计 = {T} 人时答对。", "跑步人数 d")
    d0["scene"] = {
        "kind": "chart", "cap": "运动项目统计图（条形图）",
        "world": {"xMax": 6, "yMax": maxBar + 1, "pad": 40},
        "points": [
            {"name": "barD", "x": 5.0, "y": 0, "snap": "grid", "constraint": "v-line",
             "ymin": 0, "ymax": maxBar, "color": "#2ecc71", "label": ""},
        ],
        "cats": [
            {"name": "跳绳", "color": "#e2553f", "val": a, "x": 1.0},
            {"name": "篮球", "color": "#3b7dd8", "val": b, "x": 2.33},
            {"name": "足球", "color": "#f5a623", "val": c, "x": 3.66},
            {"name": "跑步", "color": "#2ecc71", "val": d, "x": 5.0, "fill": True},
        ],
        "known": {"a": a, "b": b, "c": c, "T": T, "maxBar": maxBar},
        "dragToT": "barD", "dragAxis": "y",
        "param": {"min": 0, "max": maxBar, "step": 1, "value": 0,
                  "label": "跑步人数 d", "answer": d},
    }
    d0["answer"] = {"d": d, "T": T}
    d0["readouts"] = [
        _expr("跳绳", "a", unit="人", color="#e2553f"),
        _expr("篮球", "b", unit="人", color="#3b7dd8"),
        _expr("足球", "c", unit="人", color="#f5a623"),
        _expr("跑步", "d", unit="人", color="#2ecc71"),
        _expr("全班合计", "total", unit="人"),
        _answer("目标总人数", f"{T} 人"),
    ]
    d0["status"] = {
        "before": {"text": f"拖动绿色柱顶，补全「跑步」人数；全班合计应等于 {T} 人。", "color": "amber"},
        "at": {"text": f"答对了！跑步 {d} 人，全班 {a} + {b} + {c} + {d} = {T} 人。", "color": "green"},
        "after": {"text": "已超过目标，往下调一点…", "color": "blue"},
    }
    d0["steps"] = steps.stat_chart_steps(p)
    return d0


# ---------------------------------------------------------------------------
# 可能性（树状图）
# ---------------------------------------------------------------------------

def build_probability_tree(p):
    m, n, total, fav = p["m"], p["n"], p["total"], p["fav"]
    rule, cond = p["rule"], p["cond"]
    colorsA, colorsB = p["colorsA"], p["colorsB"]
    namesA = "、".join(c["name"] for c in colorsA)
    namesB = "、".join(c["name"] for c in colorsB)
    problem = (f"转盘 A 平均分成 {m} 格（{namesA}），转盘 B 平均分成 {n} 格"
               f"（{namesB}），两个转盘各转一次。用树状图数一数：{cond} 的结果"
               f"一共有几种？")
    d0 = _base("probability-tree", "可能性 · 树状图（枚举）", problem,
               f"拖动下方橙色手柄，沿数轴数出符合条件的叶子数；"
               f"红色圆点 = 符合条件，数到 {fav} 种就对了。", "符合条件的结果数")
    d0["scene"] = {
        "kind": "tree", "cap": "树状图 · 转盘 A × 转盘 B",
        "world": {"xMax": total + 2, "yMax": 7, "pad": 40},
        "points": [
            {"name": "cnt", "x": 1.0, "y": 0.9, "snap": "grid", "constraint": "h-line",
             "min": 1, "max": total, "color": "#f5a623", "label": ""},
        ],
        "known": {"m": m, "n": n, "total": total, "fav": fav, "rule": rule,
                  "colorsA": colorsA, "colorsB": colorsB},
        "dragToT": "cnt", "dragAxis": "x",
        "param": {"min": 1, "max": total, "step": 1, "value": 1,
                  "label": "符合条件的结果数", "answer": fav},
    }
    d0["answer"] = {"fav": fav, "total": total}
    d0["readouts"] = [
        _expr("转盘 A 格数", "m"),
        _expr("转盘 B 格数", "n"),
        _expr("所有结果", "total", unit="种"),
        _expr("我数到", "c", unit="种", color="#f5a623"),
        _answer("符合条件", f"{fav} 种"),
    ]
    d0["status"] = {
        "before": {"text": f"拖动橙色手柄数一数：{cond} 的结果有几种？", "color": "amber"},
        "at": {"text": f"答对了！共有 {total} 种结果，{cond} 的有 {fav} 种。", "color": "green"},
        "after": {"text": f"数多了，{cond} 只有 {fav} 种，往回拖一点…", "color": "blue"},
    }
    d0["steps"] = steps.probability_tree_steps(p)
    return d0
