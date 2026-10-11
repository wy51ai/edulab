# -*- coding: utf-8 -*-
"""题型 → 数据 schema 构建，产出注入 HTML 数据岛的完整 JSON。

三题型共用一个 schema：顶层键 type / lesson / motion / answer / graph / readouts /
status / steps / ui。区分靠 motion.kind(linear|circular) + motion.direction(same|opposite)。
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


def _base(p, type_slug, kind, direction, title, problem, meet_word, after_word):
    """组装三题型共用的骨架。"""
    tMeet = p["tMeet"]
    tMax = tMeet + 5
    return {
        "type": type_slug,
        "lesson": {"title": title, "problem": problem,
                   "hint": "拖动时间滑块，或点「播放」，观察全过程。"},
        "motion": {
            "kind": kind, "direction": direction, "tMax": tMax,
            "meetWord": meet_word, "afterWord": after_word,
        },
        "answer": {"tMeet": tMeet},
        "status": {
            "before": {"text": "", "color": "amber"},
            "at": {"text": "", "color": "green"},
            "after": {"text": "", "color": "blue"},
        },
        "steps": [],
        "ui": {"play": "▶ 播放", "pause": "⏸ 暂停", "sliderLabel": "时间 t（秒）"},
    }


def _readouts(tMeet, meet_word, gap_label="相距", with_laps=False):
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
    d = _base(p, "pursue", "linear", "same", "追及问题", problem, "追上", "超过")
    d["motion"].update({
        "span": span, "lap": None,
        "carA": {"name": "甲", "color": "#e2553f", "x0": 0, "v": vA},
        "carB": {"name": "乙", "color": "#3b7dd8", "x0": gap, "v": vB},
    })
    d["answer"].update({"xMeet": xMeet, "gap": gap, "dv": dv})
    d["graph"] = {
        "xMax": tMax, "yMax": yMax, "xStep": _xstep(tMax), "yStep": 10,
        "lines": [
            {"name": "甲", "color": "#e2553f", "b": 0, "k": vA},
            {"name": "乙", "color": "#3b7dd8", "b": gap, "k": vB},
        ],
        "meet": {"t": tMeet, "s": xMeet, "label": "追上", "mode": "cross"},
        "laps": None,
    }
    d["readouts"] = _readouts(tMeet, "追上", gap_label="乙领先甲")
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
    d = _base(p, "meet", "linear", "opposite", "相遇问题", problem, "相遇", "错过")
    d["motion"].update({
        "span": span, "lap": None,
        "carA": {"name": "甲", "color": "#e2553f", "x0": 0, "v": vA},
        "carB": {"name": "乙", "color": "#3b7dd8", "x0": total, "v": vB},
    })
    d["answer"].update({"xMeet": xMeet, "total": total, "sumV": vA + vB})
    d["graph"] = {
        "xMax": tMax, "yMax": yMax, "xStep": _xstep(tMax), "yStep": 10,
        "lines": [
            {"name": "甲", "color": "#e2553f", "b": 0, "k": vA},
            {"name": "乙", "color": "#3b7dd8", "b": total, "k": -vB},
        ],
        "meet": {"t": tMeet, "s": xMeet, "label": "相遇", "mode": "cross"},
        "laps": None,
    }
    d["readouts"] = _readouts(tMeet, "相遇", gap_label="两车相距")
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
        d = _base(p, "circular-same", "circular", "same", "环形跑道 · 追及", problem, "追上", "超过")
        d["motion"].update({
            "span": L, "lap": L,
            "carA": {"name": "甲", "color": "#e2553f", "x0": 0, "v": vA},
            "carB": {"name": "乙", "color": "#3b7dd8", "x0": 0, "v": vB},
        })
        d["answer"].update({"xMeet": sMeet, "gap": L, "dv": dv,
                            "sMeet": sMeet, "lapsA": p["lapsA"],
                            "lapsB": p["lapsB"], "lapGain": p["lapGain"]})
        yMax = _ceil10(vA * tMax)
        d["graph"] = {
            "xMax": tMax, "yMax": yMax, "xStep": _xstep(tMax), "yStep": 10,
            "lines": [
                {"name": "甲", "color": "#e2553f", "b": 0, "k": vA},
                {"name": "乙", "color": "#3b7dd8", "b": 0, "k": vB},
            ],
            "meet": {"t": tMeet, "s": vA * tMeet, "label": "追上", "mode": "lap"},
            "laps": [L * i for i in range(1, yMax // L + 1)],
        }
        d["readouts"] = _readouts(tMeet, "追上", gap_label="还需多跑", with_laps=True)
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
        d = _base(p, "circular-opp", "circular", "opposite", "环形跑道 · 相遇", problem, "相遇", "错过")
        d["motion"].update({
            "span": L, "lap": L,
            "carA": {"name": "甲", "color": "#e2553f", "x0": 0, "v": vA},
            "carB": {"name": "乙", "color": "#3b7dd8", "x0": L, "v": vB},
        })
        d["answer"].update({"xMeet": sMeet, "total": L, "sumV": vA + vB, "sMeet": sMeet})
        yMax = _ceil10(L)
        d["graph"] = {
            "xMax": tMax, "yMax": yMax, "xStep": _xstep(tMax), "yStep": 10,
            "lines": [
                {"name": "甲", "color": "#e2553f", "b": 0, "k": vA},
                {"name": "乙", "color": "#3b7dd8", "b": L, "k": -vB},
            ],
            "meet": {"t": tMeet, "s": vA * tMeet, "label": "相遇", "mode": "cross"},
            "laps": None,
        }
        d["readouts"] = _readouts(tMeet, "相遇", gap_label="还需合跑")
        d["status"] = {
            "before": {"text": "两人相向而跑，正在靠近…", "color": "amber"},
            "at": {"text": f"相遇了！两人合跑一圈（{L} 米），用时 {tMeet} 秒", "color": "green"},
            "after": {"text": "两人已经错过啦！", "color": "blue"},
        }
        d["steps"] = steps.circular_opp_steps(p)
    return d
