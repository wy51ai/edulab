# -*- coding: utf-8 -*-
"""统计题中文分步讲解（全 Unicode − × ÷，无需公式渲染器）。"""


def stat_chart_steps(p):
    a, b, c, d, T = p["a"], p["b"], p["c"], p["d"], p["T"]
    return [
        {"title": "读图",
         "content": f"从条形图读出已知人数：跳绳 {a} 人、篮球 {b} 人、足球 {c} 人。"},
        {"title": "求三项之和",
         "content": f"跳绳 + 篮球 + 足球 = {a} + {b} + {c} = {a + b + c} 人。"},
        {"title": "用总数减",
         "content": f"全班共 {T} 人，跑步 = {T} − {a + b + c} = {d} 人。"},
        {"title": "补全统计图",
         "content": f"把「跑步」柱拖到 {d} 人的高度，全班合计正好等于 {T} 人。"},
    ]


def probability_tree_steps(p):
    m, n, total, fav = p["m"], p["n"], p["total"], p["fav"]
    rule, cond = p["rule"], p["cond"]
    namesA = "、".join(c["name"] for c in p["colorsA"])
    namesB = "、".join(c["name"] for c in p["colorsB"])
    if rule == "first":
        why = f"转盘 A 停在红色时，转盘 B 有 {n} 种可能，所以共 {n} 种。"
    elif rule == "atleast":
        why = (f"A 红色（B 任取 {n} 种）+ B 红色（A 任取 {m} 种）− 重复的「都红」1 种"
               f" = {m} + {n} − 1 = {fav} 种。")
    elif rule == "same":
        why = f"两个转盘都停红、都停黄… 共有 {m} 种颜色，对应 {m} 种结果。"
    else:  # different
        why = f"共 {total} 种结果，减去同色 {m} 种，得 {fav} 种。"
    return [
        {"title": "画树状图",
         "content": f"第一层：转盘 A 有 {m} 个分支（{namesA}）；每个分支下，转盘 B 再分 {n} 个分支（{namesB}）。"},
        {"title": "数总结果",
         "content": f"结果总数 = {m} × {n} = {total} 种。"},
        {"title": "圈出符合条件",
         "content": f"在树状图里圈出「{cond}」的叶子。"},
        {"title": "数符合条件的结果",
         "content": f"{why} 所以符合条件的有 {fav} 种，可能性 = {fav}/{total}。"},
    ]
