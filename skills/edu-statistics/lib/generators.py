# -*- coding: utf-8 -*-
"""答案先行「好数」采样：统计量恒为整数（数据/总数/占比角），纯标准库 random + math。

统计好数约定：
  - 数据样本取整数，总数为整数（必要时整十/整百）；
  - 扇形占比角 = 整度数（挑 占比 × 360° ∈ Z 的数据）；
  - 可能性（树状图）等可能事件数为整数，枚举不漏不重。

失败抛 NoGoodNumbers（MAX_ATTEMPTS=200）。
"""
import random as _random

MAX_ATTEMPTS = 200


class NoGoodNumbers(Exception):
    pass


# ---------------------------------------------------------------------------
# 统计图表
# ---------------------------------------------------------------------------

def gen_stat_chart(rng, spec=None):
    """条形统计图·补全缺失柱：先挑 跳绳 a、篮球 b、足球 c、跑步 d（答案量），
    反推全班总数 T = a+b+c+d。跑步柱缺省，学生拖动柱顶补全到 d。"""
    s = spec or {}
    a = rng.randint(*s.get("a", (3, 8)))    # 跳绳
    b = rng.randint(*s.get("b", (4, 9)))    # 篮球
    c = rng.randint(*s.get("c", (3, 8)))    # 足球
    d = rng.randint(*s.get("d", (3, 10)))   # 跑步（答案量）
    maxBar = max(a, b, c, d) + 2
    return {"a": a, "b": b, "c": c, "d": d,
            "T": a + b + c + d, "maxBar": maxBar}


# ---------------------------------------------------------------------------
# 可能性（树状图）
# ---------------------------------------------------------------------------

def gen_probability_tree(rng, spec=None):
    """树状图枚举：转盘 A（m 等份）× 转盘 B（n 等份），共 m×n 种等可能结果。
    先挑 m、n 与条件规则，反推 fav（符合条件的结果数，答案量，恒整数）。
    规则：first=转盘A停红色 / atleast=至少一个红色 / same=两次同色(m==n) /
    different=两次不同色(m==n)。"""
    s = spec or {}
    m = rng.randint(*s.get("m", (2, 3)))    # 转盘 A 格数
    n = rng.randint(*s.get("n", (2, 3)))    # 转盘 B 格数
    total = m * n
    rules = ["first", "atleast"]
    if m == n:
        rules += ["same", "different"]
    rule = rng.choice(rules)
    if rule == "first":
        fav = n
        cond = "转盘 A 停在红色"
    elif rule == "atleast":
        fav = m + n - 1
        cond = "至少一个转盘停在红色"
    elif rule == "same":
        fav = m
        cond = "两个转盘停在同一种颜色"
    else:  # different
        fav = m * (m - 1)
        cond = "两个转盘停在不同的颜色"
    colors = [{"name": "红", "hex": "#e2553f"},
              {"name": "黄", "hex": "#f5a623"},
              {"name": "蓝", "hex": "#3b7dd8"}]
    return {"m": m, "n": n, "total": total, "rule": rule, "cond": cond,
            "fav": fav, "colorsA": colors[:m], "colorsB": colors[:n]}
