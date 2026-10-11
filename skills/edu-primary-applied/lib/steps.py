# -*- coding: utf-8 -*-
"""分步讲解文案（全中文，Unicode − × ÷，不引入 KaTeX）。"""


# ---------------------------------------------------------------------------
# 行程问题（迁移）
# ---------------------------------------------------------------------------

def pursue_steps(p):
    vA, vB, gap, dv = p["vA"], p["vB"], p["gap"], p["dv"]
    tMeet, xMeet = p["tMeet"], p["xMeet"]
    return [
        {"title": "理解题意",
         "content": f"甲、乙两车在同一条路上同向行驶。乙车在甲车前方 {gap} 米处；甲车每秒跑 {vA} 米，乙车每秒跑 {vB} 米。问：甲车几秒后追上乙车？"},
        {"title": "求速度差",
         "content": f"甲车每秒比乙车多跑：{vA} − {vB} = {dv}（米）。也就是说，甲车每秒钟能追上 {dv} 米。"},
        {"title": "求追上时间",
         "content": f"追上时间 = 路程差 ÷ 速度差 = {gap} ÷ {dv} = {tMeet}（秒）。"},
        {"title": "验算",
         "content": f"甲车 {tMeet} 秒跑 {vA} × {tMeet} = {xMeet} 米；乙车 {tMeet} 秒跑 {vB} × {tMeet} = {vB * tMeet} 米，再加上前面的 {gap} 米，正好也是 {gap + vB * tMeet} 米。两边相等，追上了！"},
    ]


def meet_steps(p):
    vA, vB, total = p["vA"], p["vB"], p["total"]
    tMeet, xMeet = p["tMeet"], p["xMeet"]
    return [
        {"title": "理解题意",
         "content": f"甲、乙两车从相距 {total} 米的两地同时出发，相向而行。甲车每秒跑 {vA} 米，乙车每秒跑 {vB} 米。问：几秒后两车相遇？"},
        {"title": "求速度和",
         "content": f"两车每秒一共靠近：{vA} + {vB} = {vA + vB}（米）。"},
        {"title": "求相遇时间",
         "content": f"相遇时间 = 总路程 ÷ 速度和 = {total} ÷ {vA + vB} = {tMeet}（秒）。"},
        {"title": "验算",
         "content": f"甲车 {tMeet} 秒跑 {vA} × {tMeet} = {xMeet} 米；乙车 {tMeet} 秒跑 {vB} × {tMeet} = {vB * tMeet} 米。两段加起来 {xMeet} + {vB * tMeet} = {total} 米，正好是全程，相遇了！"},
    ]


def circular_same_steps(p):
    L, vA, vB, dv = p["L"], p["vA"], p["vB"], p["dv"]
    tMeet, sMeet = p["tMeet"], p["sMeet"]
    lapsA, lapsB = p["lapsA"], p["lapsB"]
    return [
        {"title": "理解题意",
         "content": f"甲、乙两人在周长 {L} 米的环形跑道上，从同一起点同时同向出发。甲每秒跑 {vA} 米，乙每秒跑 {vB} 米。问：甲第一次追上乙，需要几秒？"},
        {"title": "求速度差",
         "content": f"甲每秒比乙多跑：{vA} − {vB} = {dv}（米）。"},
        {"title": "追上 = 多跑一圈",
         "content": f"因为是同向绕圈，甲要追上乙，必须比乙多跑整整一圈，也就是 {L} 米。"},
        {"title": "求追上时间",
         "content": f"追上时间 = 一圈长度 ÷ 速度差 = {L} ÷ {dv} = {tMeet}（秒）。"},
        {"title": "验算",
         "content": f"甲 {tMeet} 秒跑 {vA} × {tMeet} = {vA * tMeet} 米（{lapsA} 圈多 {sMeet} 米），乙跑 {vB} × {tMeet} = {vB * tMeet} 米（{lapsB} 圈多 {sMeet} 米）。甲正好比乙多跑 {L} 米，追上了！"},
    ]


def circular_opp_steps(p):
    L, vA, vB = p["L"], p["vA"], p["vB"]
    tMeet = p["tMeet"]
    return [
        {"title": "理解题意",
         "content": f"甲、乙两人在周长 {L} 米的环形跑道上，从同一起点同时相向出发。甲每秒跑 {vA} 米，乙每秒跑 {vB} 米。问：几秒后两人第一次相遇？"},
        {"title": "求速度和",
         "content": f"两人每秒一共靠近：{vA} + {vB} = {vA + vB}（米）。"},
        {"title": "合跑一圈",
         "content": f"因为是相向而行，两人相遇时正好合跑了一圈，也就是 {L} 米。"},
        {"title": "求相遇时间",
         "content": f"相遇时间 = 一圈长度 ÷ 速度和 = {L} ÷ {vA + vB} = {tMeet}（秒）。"},
        {"title": "验算",
         "content": f"甲 {tMeet} 秒跑 {vA} × {tMeet} = {vA * tMeet} 米，乙跑 {vB} × {tMeet} = {vB * tMeet} 米。加起来 {vA * tMeet + vB * tMeet} = {L} 米，正好一圈，相遇了！"},
    ]


# ---------------------------------------------------------------------------
# 线段图（和差 / 和倍 / 差倍）
# ---------------------------------------------------------------------------

def sum_diff_steps(p):
    a, b, S, D = p["a"], p["b"], p["S"], p["D"]
    return [
        {"title": "理解题意",
         "content": f"甲、乙两数的和是 {S}，差是 {D}。甲是大数，乙是小数。求两数各是多少。"},
        {"title": "画线段图",
         "content": f"画两条线段：甲（大数）比乙（小数）长 {D}，两条线段一共长 {S}。"},
        {"title": "去掉差，就变成两份相等",
         "content": f"从和里减去差：{S} − {D} = {S - D}。这正好是「两个较小数」的和。"},
        {"title": "求较小数",
         "content": f"较小数 = ({S} − {D}) ÷ 2 = {S - D} ÷ 2 = {a}。"},
        {"title": "求较大数",
         "content": f"较大数 = 较小数 + 差 = {a} + {D} = {b}。（验算：{a} + {b} = {S}，{b} − {a} = {D}）"},
    ]


def sum_multiple_steps(p):
    a, b, n, S = p["a"], p["b"], p["n"], p["S"]
    return [
        {"title": "理解题意",
         "content": f"甲数是乙数的 {n} 倍，两数的和是 {S}。求两数各是多少。"},
        {"title": "画线段图",
         "content": f"把乙数看成 1 份，甲数就是 {n} 份，合起来是 {n} + 1 = {n + 1} 份。"},
        {"title": "求 1 份（乙数）",
         "content": f"1 份 = 和 ÷ 份数 = {S} ÷ {n + 1} = {a}。所以乙数 = {a}。"},
        {"title": "求甲数",
         "content": f"甲数 = 乙数 × {n} = {a} × {n} = {b}。（验算：{a} + {b} = {S}）"},
    ]


def diff_multiple_steps(p):
    a, b, n, D = p["a"], p["b"], p["n"], p["D"]
    return [
        {"title": "理解题意",
         "content": f"甲数是乙数的 {n} 倍，甲数比乙数多 {D}。求两数各是多少。"},
        {"title": "画线段图",
         "content": f"把乙数看成 1 份，甲数是 {n} 份，甲比乙多 {n} − 1 = {n - 1} 份。"},
        {"title": "求 1 份（乙数）",
         "content": f"{n - 1} 份 = {D}，所以 1 份 = {D} ÷ {n - 1} = {a}。乙数 = {a}。"},
        {"title": "求甲数",
         "content": f"甲数 = 乙数 × {n} = {a} × {n} = {b}。（验算：{b} − {a} = {D}）"},
    ]


# ---------------------------------------------------------------------------
# R2 线段图：盈亏 / 年龄 / 平均数
# ---------------------------------------------------------------------------

def profit_loss_steps(p):
    n, a, c, b, d, total = p["n"], p["a"], p["c"], p["b"], p["d"], p["total"]
    return [
        {"title": "理解题意",
         "content": f"每人分 {a} 颗，剩 {b} 颗；每人分 {c} 颗，少 {d} 颗。求人数和糖数。"},
        {"title": "找两次分配的差",
         "content": f"第一次每人 {a} 颗，第二次每人 {c} 颗，每人相差 {c} − {a} = {c - a} 颗。"},
        {"title": "盈亏相加",
         "content": f"第一次剩 {b} 颗，第二次少 {d} 颗，两次总共相差 {b} + {d} = {b + d} 颗。"},
        {"title": "求人数",
         "content": f"人数 = 总相差 ÷ 每人相差 = {b + d} ÷ {c - a} = {n}（人）。"},
        {"title": "求糖数",
         "content": f"糖数 = 每人 {a} 颗 × {n} 人 + 剩 {b} 颗 = {a} × {n} + {b} = {total}（颗）。"},
    ]


def age_steps(p):
    P, Q, n, t = p["P"], p["Q"], p["n"], p["t"]
    later = Q + t
    return [
        {"title": "理解题意",
         "content": f"爸爸今年 {P} 岁，儿子今年 {Q} 岁。几年后爸爸的年龄是儿子的 {n} 倍？"},
        {"title": "年龄差不变",
         "content": f"不管过多少年，爸爸总比儿子大：{P} − {Q} = {P - Q}（岁），这个差永远不变。"},
        {"title": "把差看成 (n−1) 份",
         "content": f"爸爸是儿子的 {n} 倍，爸爸就比儿子多 {n} − 1 = {n - 1} 份，这 {n - 1} 份正好是 {P - Q} 岁。"},
        {"title": "求儿子几年后的年龄",
         "content": f"1 份 = {P - Q} ÷ {n - 1} = {later}（岁）。所以儿子几年后是 {later} 岁。"},
        {"title": "求过了几年",
         "content": f"儿子现在 {Q} 岁，几年后 {later} 岁，所以过了 {later} − {Q} = {t}（年）。"
                     f"（验算：{P} + {t} = {P + t}，{Q} + {t} = {Q + t}，{P + t} ÷ {Q + t} = {n}）"},
    ]


def average_steps(p):
    x, y, z, A = p["x"], p["y"], p["z"], p["A"]
    return [
        {"title": "理解题意",
         "content": f"甲、乙、丙三个数的平均数是 {A}，甲是 {x}，乙是 {y}。求丙。"},
        {"title": "求三个数的和",
         "content": f"三个数的和 = 平均数 × 3 = {A} × 3 = {A * 3}。"},
        {"title": "求丙",
         "content": f"丙 = 总和 − 甲 − 乙 = {A * 3} − {x} − {y} = {z}。"},
        {"title": "验算",
         "content": f"({x} + {y} + {z}) ÷ 3 = {x + y + z} ÷ 3 = {A}，平均数正好是 {A}。"},
    ]


# ---------------------------------------------------------------------------
# R2 其它：鸡兔同笼 / 植树
# ---------------------------------------------------------------------------

def chicken_rabbit_steps(p):
    c, r, H, L = p["c"], p["r"], p["H"], p["L"]
    return [
        {"title": "理解题意",
         "content": f"鸡和兔一共 {H} 个头，{L} 条腿。求鸡和兔各几只。"},
        {"title": "假设全是鸡",
         "content": f"假设 {H} 只全是鸡，腿数 = 2 × {H} = {2 * H} 条。"},
        {"title": "求差",
         "content": f"实际有 {L} 条腿，比全是鸡时多了 {L} − {2 * H} = {L - 2 * H} 条。"
                     f"每把一只鸡换成一只兔，腿数多 4 − 2 = 2 条。"},
        {"title": "求兔",
         "content": f"兔 = ({L} − {2 * H}) ÷ 2 = {L - 2 * H} ÷ 2 = {r}（只）。"},
        {"title": "求鸡",
         "content": f"鸡 = 总数 − 兔 = {H} − {r} = {c}（只）。（验算：2 × {c} + 4 × {r} = {L} 条腿）"},
    ]


def plant_steps(p):
    n, d, D, k = p["n"], p["d"], p["D"], p["k"]
    return [
        {"title": "理解题意",
         "content": f"一条 {D} 米长的路，每隔 {d} 米栽一棵，两端都栽。求棵树。"},
        {"title": "求间隔数",
         "content": f"间隔数 = 路长 ÷ 间隔 = {D} ÷ {d} = {n}（段）。"},
        {"title": "两端都栽：棵数 = 段数 + 1",
         "content": f"两端都栽时，棵数比段数多 1：{n} + 1 = {k}（棵）。"},
        {"title": "验算",
         "content": f"{k} 棵树之间有 {k - 1} = {n} 段，每段 {d} 米，总长 {n} × {d} = {D} 米，正好。"},
    ]


# ---------------------------------------------------------------------------
# R3 工程 / 周期 / 归一 / 归总
# ---------------------------------------------------------------------------

def work_steps(p):
    t, a, b = p["t"], p["a"], p["b"]
    return [
        {"title": "理解题意",
         "content": f"甲单独做 {a} 天，乙单独做 {b} 天。求合做几天完成。"},
        {"title": "求各自效率",
         "content": f"甲每天做工程的 1 ÷ {a} = 1/{a}，乙每天做工程的 1 ÷ {b} = 1/{b}。"},
        {"title": "求合做效率",
         "content": f"两人每天合做：1/{a} + 1/{b} = {b}/{a * b} + {a}/{a * b} = {a + b}/{a * b}，也就是每天完成全部的 1/{t}。"},
        {"title": "求合做时间",
         "content": f"合做时间 = 1 ÷ (1/{a} + 1/{b}) = {a} × {b} ÷ ({a} + {b}) = {a * b} ÷ {a + b} = {t}（天）。"},
        {"title": "验算",
         "content": f"{t} 天里甲完成 {t}/{a}，乙完成 {t}/{b}，合起来 {t}/{a} + {t}/{b} = 1，正好做完。"},
    ]


def cycle_steps(p):
    p_len, N, r = p["p"], p["N"], p["r"]
    colors = ["红", "黄", "蓝", "绿", "紫"][:p_len]
    color = colors[r - 1]
    return [
        {"title": "理解题意",
         "content": f"彩灯按「{'、'.join(colors)}」的顺序循环排列，每 {p_len} 盏一个周期。求第 {N} 盏的颜色。"},
        {"title": "求余数",
         "content": f"{N} ÷ {p_len} = {N // p_len} 余 {r}。"},
        {"title": "看余数定颜色",
         "content": f"余数是 {r}，就是周期里的第 {r} 盏，所以第 {N} 盏是{color}色。"},
    ]


def unit_steps(p):
    u, m, n, w, ans = p["u"], p["m"], p["n"], p["w"], p["ans"]
    return [
        {"title": "理解题意",
         "content": f"{m} 支铅笔 {w} 元，求 {n} 支铅笔多少元。"},
        {"title": "先求单价（归一）",
         "content": f"1 支铅笔 = {w} ÷ {m} = {u}（元）。"},
        {"title": "再求总量",
         "content": f"{n} 支铅笔 = {u} × {n} = {ans}（元）。"},
        {"title": "验算",
         "content": f"{m} × {u} = {w} 元，{n} × {u} = {ans} 元，正确。"},
    ]


def aggregate_steps(p):
    a, m, w, b, n = p["a"], p["m"], p["w"], p["b"], p["n"]
    return [
        {"title": "理解题意",
         "content": f"每盒装 {a} 颗，装 {m} 盒。若每盒装 {b} 颗，求装几盒。"},
        {"title": "先求总量（归总）",
         "content": f"糖果总数 = 每盒 {a} 颗 × {m} 盒 = {a} × {m} = {w}（颗）。"},
        {"title": "再求盒数",
         "content": f"盒数 = 总量 ÷ 每盒 {b} 颗 = {w} ÷ {b} = {n}（盒）。"},
        {"title": "验算",
         "content": f"{n} × {b} = {w} 颗，正好是总数。"},
    ]


# ---------------------------------------------------------------------------
# R3 行程扩展：流水行船 / 火车过桥 / 平均速度
# ---------------------------------------------------------------------------

def boat_steps(p):
    s_km, t1, t2, u, v, down, up = p["s"], p["t1"], p["t2"], p["u"], p["v"], p["down"], p["up"]
    return [
        {"title": "理解题意",
         "content": f"两港相距 {s_km} 千米，顺水 {t1} 小时，逆水 {t2} 小时。求水流速度。"},
        {"title": "求顺水速度",
         "content": f"顺水速度 = 路程 ÷ 时间 = {s_km} ÷ {t1} = {down}（千米/时）。"},
        {"title": "求逆水速度",
         "content": f"逆水速度 = 路程 ÷ 时间 = {s_km} ÷ {t2} = {up}（千米/时）。"},
        {"title": "顺水 − 逆水 = 2 倍水流",
         "content": f"顺水 = 静水 + 水流，逆水 = 静水 − 水流，两者相差 2 倍水流：({down} − {up}) ÷ 2 = {down - up} ÷ 2 = {u}（千米/时）。"},
        {"title": "求静水速度",
         "content": f"静水速度 = ({down} + {up}) ÷ 2 = {down + up} ÷ 2 = {v}（千米/时）。"},
    ]


def train_steps(p):
    L, B, v, t = p["L"], p["B"], p["v"], p["t"]
    return [
        {"title": "理解题意",
         "content": f"火车长 {L} 米，速度 {v} 米/秒，桥长 {B} 米。求车头上桥到车尾离桥的时间。"},
        {"title": "走过的总路程 = 车长 + 桥长",
         "content": f"从车头上桥到车尾离桥，火车头一共要走：车长 + 桥长 = {L} + {B} = {L + B}（米）。"},
        {"title": "求时间",
         "content": f"时间 = 路程 ÷ 速度 = {L + B} ÷ {v} = {t}（秒）。"},
        {"title": "验算",
         "content": f"{v} × {t} = {L + B} 米，正好走完车长加桥长。"},
    ]


def avgspeed_steps(p):
    v1, v2, avg, arith = p["v1"], p["v2"], p["avg"], p["arith"]
    return [
        {"title": "理解题意",
         "content": f"去时 {v1} 千米/时，回来 {v2} 千米/时。求往返平均速度。"},
        {"title": "陷阱：不是简单的平均",
         "content": f"平均速度 ≠ ({v1} + {v2}) ÷ 2 = {arith}。因为去和回花的时间不一样。"},
        {"title": "假设路程",
         "content": f"假设单程 {v1 * v2} 千米。去时用 {v1 * v2} ÷ {v1} = {v2} 小时，回来用 {v1 * v2} ÷ {v2} = {v1} 小时。"
                     f"总路程 {2 * v1 * v2} 千米，总时间 {v1 + v2} 小时。"},
        {"title": "求平均速度",
         "content": f"平均速度 = 总路程 ÷ 总时间 = {2 * v1 * v2} ÷ {v1 + v2} = {avg}（千米/时）。"},
        {"title": "验算",
         "content": f"{avg} 比速度平均 {arith} 小，因为慢的那段花的时间更长。"},
    ]


# ---------------------------------------------------------------------------
# A 组：分数 / 百分数 / 比与比例 / 浓度 / 行程扩展 / 还原 / 平均数变体 / 间隔变体
# ---------------------------------------------------------------------------

def _frac_word(n, d):
    """分率中文：1/2→一半，1/3→三分之一。"""
    if n == 1 and d == 2:
        return "一半"
    if n == 1 and d == 3:
        return "三分之一"
    return f"{n}/{d}"


def fraction_part_steps(p):
    d, n, k, W, part = p["d"], p["n"], p["k"], p["W"], p["part"]
    return [
        {"title": "理解题意",
         "content": f"求 {W} 的 {n}/{d} 是多少，就是把这个整体平均分成 {d} 份，取其中的 {n} 份。"},
        {"title": "求每份",
         "content": f"每份 = 整体 ÷ 份数 = {W} ÷ {d} = {k}。"},
        {"title": "求 n 份",
         "content": f"{n} 份 = {k} × {n} = {part}。也就是 {W} × {n}/{d} = {part}。"},
        {"title": "结论",
         "content": f"所以 {W} 的 {n}/{d} 是 {part}。"},
    ]


def fraction_whole_steps(p):
    d, n, k, W, part = p["d"], p["n"], p["k"], p["W"], p["part"]
    return [
        {"title": "理解题意",
         "content": f"一个数的 {n}/{d} 是 {part}。也就是说，把这个数平均分成 {d} 份，其中的 {n} 份是 {part}。"},
        {"title": "求每份",
         "content": f"{n} 份是 {part}，所以每份 = {part} ÷ {n} = {k}。"},
        {"title": "求整体（单位「1」）",
         "content": f"整体有 {d} 份，所以整体 = {k} × {d} = {W}。"},
        {"title": "结论",
         "content": f"所以这个数是 {W}。验算：{W} × {n}/{d} = {part}。"},
    ]


def fraction_ratio_steps(p):
    d, n, k, A, B = p["d"], p["n"], p["k"], p["A"], p["B"]
    return [
        {"title": "理解题意",
         "content": f"甲数是 {A}，乙数是 {B}。求甲数是乙数的几分之几。"},
        {"title": "找公约数（约分单位）",
         "content": f"甲 = {n} × {k}，乙 = {d} × {k}，两数有公约数 {k}。"},
        {"title": "写成比例并约分",
         "content": f"甲 ÷ 乙 = {A} ÷ {B} = ({n} × {k}) ÷ ({d} × {k}) = {n}/{d}。"},
        {"title": "结论",
         "content": f"所以甲数是乙数的 {n}/{d}。"},
    ]


def discount_steps(p):
    A, d, price = p["A"], p["d"], p["price"]
    return [
        {"title": "理解题意",
         "content": f"原价 {A} 元，打 {d} 折。"},
        {"title": "理解折扣",
         "content": f"打 {d} 折就是按原价的 {d}/10 出售，也就是每 10 元只付 {d} 元。"},
        {"title": "求现价",
         "content": f"现价 = 原价 × {d}/10 = {A} × {d}/10 = {price}（元）。"},
        {"title": "结论",
         "content": f"所以现价是 {price} 元。"},
    ]


def percent_change_steps(p):
    A, x, price = p["A"], p["x"], p["price"]
    up = A * x // 100
    return [
        {"title": "理解题意",
         "content": f"原价 {A} 元，涨价 {x}%。"},
        {"title": "求涨价的部分",
         "content": f"涨价部分 = 原价 × {x}% = {A} × {x}% = {up}（元）。"},
        {"title": "求现价",
         "content": f"现价 = 原价 + 涨价部分 = {A} + {up} = {price}（元）。"},
        {"title": "结论",
         "content": f"所以现价是 {price} 元。"},
    ]


def ratio_share_steps(p):
    a, b, k, A, B, total = p["a"], p["b"], p["k"], p["A"], p["B"], p["total"]
    return [
        {"title": "理解题意",
         "content": f"把 {total} 元按 {a}:{b} 分给甲、乙。也就是甲占 {a} 份，乙占 {b} 份。"},
        {"title": "求总份数",
         "content": f"总份数 = {a} + {b} = {a + b}（份）。"},
        {"title": "求每份",
         "content": f"每份 = 总数 ÷ 总份数 = {total} ÷ {a + b} = {k}（元）。"},
        {"title": "求甲、乙",
         "content": f"甲 = {k} × {a} = {A}（元）；乙 = {k} × {b} = {B}（元）。"},
        {"title": "结论",
         "content": f"甲分 {A} 元，乙分 {B} 元。"},
    ]


def ratio_scale_steps(p):
    n, d, real = p["n"], p["d"], p["real"]
    return [
        {"title": "理解题意",
         "content": f"模型比例 1:{n}，模型长 {d} 厘米。也就是说，实物是模型的 {n} 倍。"},
        {"title": "求实际长度",
         "content": f"实际长度 = 模型长 × {n} = {d} × {n} = {real}（厘米）。"},
        {"title": "结论",
         "content": f"所以这个零件实际长 {real} 厘米。"},
    ]


def concentration_steps(p):
    g, c, salt = p["g"], p["c"], p["salt"]
    return [
        {"title": "理解题意",
         "content": f"盐水重 {g} 克，含盐率 {c}%。含盐率就是盐占盐水的百分比。"},
        {"title": "求盐的质量",
         "content": f"盐 = 盐水 × 含盐率 = {g} × {c}% = {salt}（克）。"},
        {"title": "求水的质量",
         "content": f"水 = 盐水 − 盐 = {g} − {salt} = {g - salt}（克）。"},
        {"title": "结论",
         "content": f"所以盐有 {salt} 克。"},
    ]


def midpoint_meet_steps(p):
    vA, vB, t, m, T = p["vA"], p["vB"], p["t"], p["m"], p["T"]
    mid = T // 2
    return [
        {"title": "理解题意",
         "content": f"两地相距 {T} 米，甲每分走 {vA} 米、乙每分走 {vB} 米，同时相向而行，在距中点 {m} 米处相遇。"},
        {"title": "求速度和",
         "content": f"两人每分钟一共靠近 {vA} + {vB} = {vA + vB}（米）。"},
        {"title": "求相遇时间",
         "content": f"相遇时间 = 全程 ÷ 速度和 = {T} ÷ {vA + vB} = {t}（分钟）。"},
        {"title": "验证距中点",
         "content": f"相遇时甲走了 {vA} × {t} = {vA * t} 米，比中点 {mid} 米多 {vA * t - mid} 米；乙走了 {vB * t} 米，比中点少 {mid - vB * t} 米。两边偏移都是 {m} 米，验证一致！"},
        {"title": "结论",
         "content": f"他们走了 {t} 分钟。"},
    ]


def restore_steps(p):
    a, b, c, d, W, X, r = p["a"], p["b"], p["c"], p["d"], p["W"], p["X"], p["r"]
    fa = _frac_word(1, a)
    fc = _frac_word(1, c)
    return [
        {"title": "理解题意",
         "content": f"一袋糖，第一次吃总数的{fa}多 {b} 个，第二次吃剩下的{fc}多 {d} 个，最后剩 {r} 个。"},
        {"title": "从后往前逆推（第二次）",
         "content": f"最后剩 {r} 个。第二次是「吃剩下的{fc}多 {d} 个」，倒回去：第二次吃之前有 {X} 个（{X} − {X // c} − {d} = {r}）。"},
        {"title": "从后往前逆推（第一次）",
         "content": f"第一次吃之前有 {W} 个（{W} − {W // a} − {b} = {X}）。"},
        {"title": "结论",
         "content": f"所以原来有 {W} 个糖。验算：{W} → 第一次剩 {X} → 最后剩 {r}。"},
    ]


def average_move_steps(p):
    a, b, give = p["a"], p["b"], p["give"]
    return [
        {"title": "理解题意",
         "content": f"甲有 {a} 个，乙有 {b} 个。甲给乙一些后，两人一样多。"},
        {"title": "求两人的差",
         "content": f"甲比乙多 {a} − {b} = {a - b}（个）。"},
        {"title": "移多补少：给差的一半",
         "content": f"甲把多出来的 {a - b} 个平均分，自己留一半、给乙一半：{a - b} ÷ 2 = {give}（个）。"},
        {"title": "验证",
         "content": f"给完后甲有 {a} − {give} = {a - give} 个，乙有 {b} + {give} = {b + give} 个，正好一样多！"},
        {"title": "结论",
         "content": f"甲给乙 {give} 个，两人的苹果就一样多。"},
    ]


def stairs_steps(p):
    scenario, n, t, total = p["scenario"], p["n"], p["t"], p["total"]
    if scenario == "楼":
        head = f"从 1 楼走到 {n} 楼，每上一层楼用 {t} 秒。"
        gaps_desc = f"从 1 楼到 {n} 楼要上 {n} − 1 = {n - 1} 层楼（1 楼不用爬）。"
        each, unit = "每层", "秒"
    elif scenario == "段":
        head = f"把一根木头锯成 {n} 段，锯一次用 {t} 分钟。"
        gaps_desc = f"锯成 {n} 段要锯 {n} − 1 = {n - 1} 次（锯一次多一段，最后一段不用锯）。"
        each, unit = "每次", "分钟"
    else:  # 下
        head = f"时钟敲 {n} 下，每两下之间的间隔是 {t} 秒。"
        gaps_desc = f"敲 {n} 下之间有 {n} − 1 = {n - 1} 个间隔（第一下是起点，不算间隔）。"
        each, unit = "每个间隔", "秒"
    return [
        {"title": "理解题意",
         "content": head + " 求一共用多长时间。"},
        {"title": "数间隔（不是数点数）",
         "content": gaps_desc + " 间隔数总是比点数少 1。"},
        {"title": "求总时间",
         "content": f"总时间 = 间隔数 × {each}时间 = {n - 1} × {t} = {total}（{unit}）。"},
        {"title": "结论",
         "content": f"所以一共要用 {total} {unit}。"},
    ]


# ---------------------------------------------------------------------------
# B 组：牛吃草 / 方阵 / 抽屉 / 时钟 / 消去法 / 等差数列 / 最优化 / 页码 / 三数和差倍
# ---------------------------------------------------------------------------

def cows_steps(p):
    g, N, t, G = p["g"], p["N"], p["t"], p["G"]
    return [
        {"title": "理解题意",
         "content": f"草地原有 {G} 份草，每天匀速长出 {g} 份。{N} 头牛每头每天吃 1 份，问能吃多少天。"},
        {"title": "每天净消耗",
         "content": f"{N} 头牛每天吃 {N} 份，草每天长 {g} 份，所以每天真正消耗原有草 {N} − {g} = {N - g}（份）。"},
        {"title": "求可吃天数",
         "content": f"可吃天数 = 原有草 ÷ 每天净消耗 = {G} ÷ {N - g} = {t}（天）。"},
        {"title": "验证",
         "content": f"{t} 天里草共长出 {g} × {t} = {g * t} 份，加上原有 {G} 份，共 {G + g * t} 份；牛共吃 {N} × {t} = {N * t} 份。两边相等！"},
        {"title": "结论",
         "content": f"这些牛可以吃 {t} 天。"},
    ]


def phalanx_steps(p):
    n, total, outer = p["n"], p["total"], p["outer"]
    return [
        {"title": "理解题意",
         "content": f"一个正方形方阵一共有 {total} 人，求每边站多少人。"},
        {"title": "总数与边长的关系",
         "content": f"正方形方阵每边 {n} 人，总数 = 每边 × 每边 = {n} × {n} = {n * n}（人）。"},
        {"title": "求每边人数",
         "content": f"反过来，每边人数 × 每边人数 = {total}，因为 {n} × {n} = {total}，所以每边 {n} 人。"},
        {"title": "顺带：最外层人数",
         "content": f"最外层 = 4 × 每边 − 4（四个角重复数了一次）= 4 × {n} − 4 = {outer}（人）。"},
        {"title": "结论",
         "content": f"方阵每边站 {n} 人。"},
    ]


def pigeonhole_steps(p):
    n, k, r, m, least = p["n"], p["k"], p["r"], p["m"], p["least"]
    return [
        {"title": "理解题意",
         "content": f"把 {m} 个苹果放进 {n} 个抽屉，问「总有一个抽屉至少放几个」。"},
        {"title": "先平均分",
         "content": f"{m} ÷ {n} = {k} 余 {r}，即每个抽屉先放 {k} 个，还剩 {r} 个。"},
        {"title": "剩余的要继续放",
         "content": f"剩下的 {r} 个还要放进去，无论放哪个抽屉，都会让某个抽屉达到 {k} + 1 = {least}（个）。"},
        {"title": "反证法说明「至少」",
         "content": f"假如每个抽屉最多放 {k} 个，那 {n} 个抽屉最多放 {n} × {k} = {n * k} 个，可苹果有 {m} = {n * k} + {r} 个，放不下！所以一定有一个抽屉至少 {least} 个。"},
        {"title": "结论",
         "content": f"总有一个抽屉至少放进 {least} 个苹果。"},
    ]


def clock_steps(p):
    h, angle = p["h"], p["angle"]
    return [
        {"title": "理解题意",
         "content": f"钟面上 {h} 点整，求时针和分针的较小夹角。"},
        {"title": "分针指 12",
         "content": f"整点时，分针指向 12（0°）。"},
        {"title": "时针每小时走 30°",
         "content": f"钟面一圈 360° 平均分给 12 小时，每小时时针走 360° ÷ 12 = 30°。{h} 点整时针走了 {h} × 30° = {angle}°。"},
        {"title": "取较小夹角",
         "content": f"时针在 {angle}°、分针在 0°，夹角就是 {angle}°（小于 180°，就是较小夹角）。"},
        {"title": "结论",
         "content": f"{h} 点整时针和分针的夹角是 {angle}°。"},
    ]


def elimination_steps(p):
    x, y, z = p["x"], p["y"], p["z"]
    S1, S2, S3 = p["S1"], p["S2"], p["S3"]
    return [
        {"title": "理解题意",
         "content": f"甲+乙={S1}，乙+丙={S2}，甲+丙={S3}。求甲。"},
        {"title": "把三个和加起来",
         "content": f"①+②+③：(甲+乙)+(乙+丙)+(甲+丙) = {S1} + {S2} + {S3} = {S1 + S2 + S3}，也就是 2 个(甲+乙+丙)。"},
        {"title": "求三者之和",
         "content": f"甲+乙+丙 = {S1 + S2 + S3} ÷ 2 = {(S1 + S2 + S3) // 2}。"},
        {"title": "用乙+丙消去",
         "content": f"甲 = (甲+乙+丙) − (乙+丙) = {(S1 + S2 + S3) // 2} − {S2} = {x}。"},
        {"title": "顺带求出乙和丙",
         "content": f"乙 = {S1} − {x} = {y}，丙 = {S3} − {x} = {z}。验证：乙+丙 = {y} + {z} = {S2}。"},
        {"title": "结论",
         "content": f"甲 = {x}，乙 = {y}，丙 = {z}。"},
    ]


def arithmetic_seq_steps(p):
    a, d, n, an = p["a"], p["d"], p["n"], p["an"]
    return [
        {"title": "理解题意",
         "content": f"等差数列首项 {a}、公差 {d}，求第 {n} 项。"},
        {"title": "第 n 项的通项公式",
         "content": f"第 n 项 = 首项 + (n−1) × 公差。"},
        {"title": "代入计算",
         "content": f"第 {n} 项 = {a} + ({n} − 1) × {d} = {a} + {n - 1} × {d} = {a} + {(n - 1) * d} = {an}。"},
        {"title": "结论",
         "content": f"所以第 {n} 项是 {an}。"},
    ]


def optimize_steps(p):
    a, b, pv, q = p["a"], p["b"], p["p"], p["q"]
    N, optK, minCost = p["N"], p["optK"], p["minCost"]
    small_needed = -(-(N - optK * a) // b) if N - optK * a > 0 else 0
    return [
        {"title": "理解题意",
         "content": f"{N} 人划船，大船坐 {a} 人/条 {pv} 元，小船坐 {b} 人/条 {q} 元，求最省钱的租法。"},
        {"title": "比较人均价格",
         "content": f"大船人均 {pv} ÷ {a} 元，小船人均 {q} ÷ {b} 元，大船人均更便宜，所以尽量多租大船。"},
        {"title": "列方案比较",
         "content": f"依次试大船 0、1、2……条，补足小船，算出每种总价。发现大船 {optK} 条时总价最小。"},
        {"title": "最小总价方案",
         "content": f"大船 {optK} 条可坐 {optK * a} 人，还剩 {N - optK * a} 人，需小船 {small_needed} 条。总价 = {optK} × {pv} + {small_needed} × {q} = {minCost}（元）。"},
        {"title": "结论",
         "content": f"租大船 {optK} 条、小船 {small_needed} 条最省钱，共 {minCost} 元。"},
    ]


def page_digit_steps(p):
    n, total = p["n"], p["total"]
    return [
        {"title": "理解题意",
         "content": f"从第 1 页开始编号，一共用了 {total} 个数字，求这本书有几页。"},
        {"title": "分位数段统计",
         "content": f"第 1~9 页每页 1 个数字，共 9 个；从第 10 页起每页 2 个数字。"},
        {"title": "求两位数的页数",
         "content": f"两位数的数字 = 总数 − 9 = {total} − 9 = {total - 9}（个），两位数的页数 = {total - 9} ÷ 2 = {(total - 9) // 2}（页）。"},
        {"title": "求总页数",
         "content": f"总页数 = 9 + {n - 9} = {n}（页）。"},
        {"title": "验证",
         "content": f"9 页一位数用 9 个数字，{n - 9} 页两位数用 2 × {n - 9} = {2 * (n - 9)} 个数字，共 9 + {2 * (n - 9)} = {total} 个数字。"},
        {"title": "结论",
         "content": f"这本书有 {n} 页。"},
    ]


def sum_diff_three_steps(p):
    a, b, c, D, n, S = p["a"], p["b"], p["c"], p["D"], p["n"], p["S"]
    return [
        {"title": "理解题意",
         "content": f"甲、乙、丙三个数的和是 {S}，甲比乙多 {D}，丙是甲的 {n} 倍。"},
        {"title": "用甲表示乙",
         "content": f"乙 = 甲 − {D}。"},
        {"title": "用甲表示丙",
         "content": f"丙 = 甲的 {n} 倍 = {n} × 甲。"},
        {"title": "列方程求和",
         "content": f"甲 + (甲 − {D}) + {n} × 甲 = {S}，即 {n + 2} × 甲 − {D} = {S}。"},
        {"title": "求甲",
         "content": f"甲 = ({S} + {D}) ÷ {n + 2} = {S + D} ÷ {n + 2} = {a}。"},
        {"title": "求乙和丙",
         "content": f"乙 = {a} − {D} = {b}，丙 = {n} × {a} = {c}。验证：{a} + {b} + {c} = {S}。"},
        {"title": "结论",
         "content": f"甲 = {a}，乙 = {b}，丙 = {c}。"},
    ]


# ---------------------------------------------------------------------------
# C 组：盈亏两盈/两亏 + 植树一端/两端不栽/环形
# ---------------------------------------------------------------------------

def profit_loss_two_gain_steps(p):
    n, a, b, c, d, total = p["n"], p["a"], p["b"], p["c"], p["d"], p["total"]
    return [
        {"title": "理解题意",
         "content": f"每人分 {a} 个余 {b} 个，每人分 {c} 个余 {d} 个。两次分法人数相同、总数相同。"},
        {"title": "求两次剩余之差",
         "content": f"第一种分法剩余 {b} 个，第二种剩余 {d} 个，相差 {b} − {d} = {b - d}（个）。"},
        {"title": "每人多分的差",
         "content": f"第二种比第一种每人多分 {c} − {a} = {c - a}（个）。"},
        {"title": "求人数",
         "content": f"每人多分 {c - a} 个，总共多分掉 {b - d} 个，所以人数 = {b - d} ÷ {c - a} = {n}（人）。"},
        {"title": "验证",
         "content": f"每人 {a} 个：{n} × {a} = {n * a}，加余 {b} 得总数 {total}；每人 {c} 个：{n} × {c} = {n * c}，加余 {d} 得总数 {total}。一致！"},
        {"title": "结论",
         "content": f"一共有 {n} 个小朋友。"},
    ]


def profit_loss_two_loss_steps(p):
    n, a, b, c, d, total = p["n"], p["a"], p["b"], p["c"], p["d"], p["total"]
    return [
        {"title": "理解题意",
         "content": f"每人分 {a} 个缺 {b} 个，每人分 {c} 个缺 {d} 个。两次分法人数相同、总数相同。"},
        {"title": "求两次缺口之差",
         "content": f"第二种分法比第一种多缺 {d} − {b} = {d - b}（个）。"},
        {"title": "每人多分的差",
         "content": f"第二种比第一种每人多分 {c} − {a} = {c - a}（个）。"},
        {"title": "求人数",
         "content": f"每人多分 {c - a} 个，缺口就多 {d - b} 个，所以人数 = {d - b} ÷ {c - a} = {n}（人）。"},
        {"title": "验证",
         "content": f"总数 = {n} × {a} − {b} = {total}，也等于 {n} × {c} − {d} = {total}。一致！"},
        {"title": "结论",
         "content": f"一共有 {n} 个小朋友。"},
    ]


def plant_one_steps(p):
    n, d, D, k = p["n"], p["d"], p["D"], p["k"]
    return [
        {"title": "理解题意",
         "content": f"一条 {D} 米长的路，每隔 {d} 米栽一棵，只在一端栽。求棵树。"},
        {"title": "求间隔数",
         "content": f"间隔数 = 路长 ÷ 间隔 = {D} ÷ {d} = {n}（段）。"},
        {"title": "一端栽：棵数 = 段数",
         "content": f"只在一端栽时，棵树等于间隔数：{n}（棵）。"},
        {"title": "验算",
         "content": f"{k} 棵树把路分成 {k} = {n} 段，每段 {d} 米，总长 {n} × {d} = {D} 米，正好。"},
    ]


def plant_none_steps(p):
    n, d, D, k = p["n"], p["d"], p["D"], p["k"]
    return [
        {"title": "理解题意",
         "content": f"一条 {D} 米长的路，每隔 {d} 米栽一棵，两端都不栽。求棵树。"},
        {"title": "求间隔数",
         "content": f"间隔数 = 路长 ÷ 间隔 = {D} ÷ {d} = {n}（段）。"},
        {"title": "两端不栽：棵数 = 段数 − 1",
         "content": f"两端都不栽时，棵数比段数少 1：{n} − 1 = {k}（棵）。"},
        {"title": "验算",
         "content": f"{k} 棵树之间有 {k + 1} = {n} 段，每段 {d} 米，总长 {n} × {d} = {D} 米，正好。"},
    ]


def plant_ring_steps(p):
    n, d, D, k = p["n"], p["d"], p["D"], p["k"]
    return [
        {"title": "理解题意",
         "content": f"周长 {D} 米的圆形池塘，每隔 {d} 米栽一棵。求棵树。"},
        {"title": "求间隔数",
         "content": f"间隔数 = 周长 ÷ 间隔 = {D} ÷ {d} = {n}（段）。"},
        {"title": "环形：棵数 = 段数",
         "content": f"环形闭合，首尾相连，棵数等于间隔数：{n}（棵）。"},
        {"title": "验算",
         "content": f"{k} 棵树把圆周分成 {k} = {n} 段，每段 {d} 米，总长 {n} × {d} = {D} 米，正好。"},
    ]


def overlap_venn_steps(p):
    a, b, c, X, Y, T = p["a"], p["b"], p["c"], p["X"], p["Y"], p["T"]
    return [
        {"title": "理解题意",
         "content": f"语文优秀 {X} 人、数学优秀 {Y} 人、至少一科优秀 {T} 人。问两科都优秀几人？"},
        {"title": "画韦恩图",
         "content": f"两个圆分别表示语文优秀、数学优秀，重叠部分就是「两科都优秀」c 人；"
                     f"只语文 {a} 人、只数学 {b} 人。"},
        {"title": "找重复计算",
         "content": f"语文优秀 + 数学优秀 = {X} + {Y} = {X + Y}，这里把「两科都优秀」的 c 人数了两次。"},
        {"title": "求两科都优秀",
         "content": f"至少一科 = 语文 + 数学 − 两科都优，即 {T} = {X} + {Y} − c，"
                     f"所以 c = {X} + {Y} − {T} = {c}（人）。"},
        {"title": "验算",
         "content": f"只语文 {X} − {c} = {a}，只数学 {Y} − {c} = {b}，两科都优 {c}，"
                     f"合计 {a} + {b} + {c} = {T} 人，正好。"},
    ]


def match_count_steps(p):
    m, n, total = p["m"], p["n"], p["total"]
    return [
        {"title": "理解题意",
         "content": f"{m} 件上衣、{n} 条裤子，每次各选 1 件，问一共有几种搭配。"},
        {"title": "连线枚举",
         "content": f"每 1 件上衣都能和 {n} 条裤子各配一次；"
                     f"第 1 件上衣连 {n} 条线，第 2 件再连 {n} 条线……"},
        {"title": "用乘法",
         "content": f"搭配数 = 上衣数 × 裤子数 = {m} × {n} = {total}（种）。"},
        {"title": "验算",
         "content": f"连线图上一共画了 {total} 条线，正好 = {m} × {n}。"},
    ]


def logic_table_steps(p):
    people, sports, perm = p["people"], p["sports"], p["perm"]
    cond1, cond2, cond3 = p["cond1"], p["cond2"], p["cond3"]
    others = [sports[x] for x in range(3) if x != perm[0]]
    return [
        {"title": "理解题意",
         "content": f"三人各喜欢一项运动且不重复。线索：{cond1}；{cond2}。"},
        {"title": "由条件 1 推出甲",
         "content": f"甲不是{others[0]}、也不是{others[1]}，三选一排除两项，"
                     f"所以甲 = {sports[perm[0]]}。"},
        {"title": "由条件 2 推出乙",
         "content": f"{cond2}，所以乙 = {sports[perm[1]]}。"},
        {"title": "剩下的是丙",
         "content": f"三个运动只剩 {sports[perm[2]]}，所以丙 = {sports[perm[2]]}。"},
        {"title": "验算",
         "content": f"甲={sports[perm[0]]}、乙={sports[perm[1]]}、丙={sports[perm[2]]}，"
                     f"三人各不相同，符合所有条件。"},
    ]


def pancake_steps(p):
    n, k, t, sides, total = p["n"], p["k"], p["t"], p["sides"], p["total"]
    return [
        {"title": "理解题意",
         "content": f"{n} 张饼，每张两面，共 {sides} 面；锅一次最多烙 {k} 张（{k} 面）。"},
        {"title": "算总面数",
         "content": f"总面数 = {n} × 2 = {sides}（面）。"},
        {"title": "算最少次数",
         "content": f"每次烙 {k} 面，最少烙 {sides} ÷ {k} = {sides // k}（次）。"},
        {"title": "求总时间",
         "content": f"每次 {t} 分钟，总时间 = {sides // k} × {t} = {total}（分钟）。"},
        {"title": "交替烙（关键）",
         "content": f"不要等一张饼两面都烙好再换下一张：先烙 1 号、2 号正面，"
                     f"再把 1 号翻面、放进 3 号正面……交替烙才能最省时间。"},
    ]


def tianji_steps(p):
    order, qw_speed, tj_speed = p["order"], p["qw_speed"], p["tj_speed"]
    ans_lane = p["ans_lane"]
    lane_of = {tj: ans_lane[tj] for tj in ["上", "中", "下"]}
    return [
        {"title": "理解题意",
         "content": f"齐王出马顺序：第1场{order[0]}、第2场{order[1]}、第3场{order[2]}。"
                     f"田忌的上等马能胜齐王的中等马，中等马能胜齐王的下等马，下等马最慢。"},
        {"title": "让一步（舍一局）",
         "content": "用田忌最慢的下等马去对齐王最快的上等马，输掉这局。"},
        {"title": "赢两局",
         "content": f"田忌上等马对齐王中等马（第 {lane_of['上']} 场）、"
                     f"田忌中等马对齐王下等马（第 {lane_of['中']} 场），各胜一局。"},
        {"title": "结果",
         "content": f"田忌胜 2 局、输 1 局，总比分 2∶1 取胜。"},
    ]


def fraction_more_less_steps(p):
    mode, k, m, B, D, A = p["mode"], p["k"], p["m"], p["B"], p["D"], p["A"]
    word = "多" if mode == "多" else "少"
    return [
        {"title": "理解题意",
         "content": f"乙有 {B} 个。甲比乙{word} 1/{k}。求甲有多少个。"},
        {"title": "找单位「1」",
         "content": f"「比乙{word}」是把乙看作单位「1」（乙 = {B}）。"},
        {"title": "求相差量",
         "content": f"甲比乙{word}的部分 = 乙 × 1/{k} = {B} × 1/{k} = {D}（个）。"},
        {"title": "求甲",
         "content": f"甲 = 乙 {word} 相差量 = {B} {'+' if mode == '多' else '−'} {D} = {A}（个）。"},
        {"title": "验算",
         "content": f"{D} ÷ {B} = 1/{k}，甲确实比乙{word} 1/{k}。"},
    ]


def interest_steps(p):
    P, r, n, interest = p["P"], p["r"], p["n"], p["interest"]
    return [
        {"title": "理解题意",
         "content": f"本金 {P} 元，年利率 {r}%，存 {n} 年。求利息。"},
        {"title": "一年利息",
         "content": f"一年利息 = 本金 × 利率 = {P} × {r}% = {P} × {r} ÷ 100 = {P * r // 100}（元）。"},
        {"title": "多年利息",
         "content": f"{n} 年利息 = 一年利息 × {n} = {P * r // 100} × {n} = {interest}（元）。"},
        {"title": "验算",
         "content": f"{P} × {r}% × {n} = {P} × {r} ÷ 100 × {n} = {interest} 元，正好。"},
    ]


def plant_two_sides_steps(p):
    n, d, D, k, total = p["n"], p["d"], p["D"], p["k"], p["total"]
    return [
        {"title": "理解题意",
         "content": f"长 {D} 米的路两侧，每隔 {d} 米栽一棵，两端都栽。求两侧总棵数。"},
        {"title": "求间隔数",
         "content": f"间隔数 = 路长 ÷ 间隔 = {D} ÷ {d} = {n}（段）。"},
        {"title": "求单侧棵数",
         "content": f"两端都栽，单侧棵数 = 间隔数 + 1 = {n} + 1 = {k}（棵）。"},
        {"title": "求两侧总棵数",
         "content": f"两侧都栽，总棵数 = 单侧 × 2 = {k} × 2 = {total}（棵）。"},
        {"title": "验算",
         "content": f"每侧 {k} 棵，两侧共 {total} 棵，正好。"},
    ]


def equation_balance_steps(p):
    x, a, b, right = p["x"], p["a"], p["b"], p["right"]
    return [
        {"title": "理解题意",
         "content": f"天平左盘 = {a}x + {b}，右盘 = {right}。平衡时两边相等。"},
        {"title": "列方程",
         "content": f"{a}x + {b} = {right}。"},
        {"title": "移项",
         "content": f"{a}x = {right} − {b} = {right - b}。"},
        {"title": "求 x",
         "content": f"x = {right - b} ÷ {a} = {x}。"},
        {"title": "验算",
         "content": f"{a} × {x} + {b} = {a * x} + {b} = {right}，两边相等，天平平衡。"},
    ]


def triangle_equal_steps(p):
    b, h, s0, mid, area = p["b"], p["h"], p["s0"], p["mid"], p["area"]
    return [
        {"title": "理解题意",
         "content": f"一个三角形，底 {b} 格，高 {h} 格。顶点 C 可以沿一条与底边平行的线左右移动（高始终是 {h} 格）。"},
        {"title": "三角形面积公式",
         "content": f"三角形面积 = 底 × 高 ÷ 2 = {b} × {h} ÷ 2 = {area}（格²）。"},
        {"title": "等底等高，面积不变",
         "content": f"C 左右移动时，底还是 {b} 格，高还是 {h} 格，所以面积始终是 {area} 格²。这就叫「等底等高的三角形面积相等」。"},
        {"title": "变成等腰三角形",
         "content": f"把 C 拖到底边中点正上方（第 {mid} 格），左右两腰一样长，就变成了等腰三角形。"},
        {"title": "验证",
         "content": f"C 停在（第 {mid} 格，高 {h}），三角形面积仍是 {b} × {h} ÷ 2 = {area} 格²。"},
    ]


def para_equal_steps(p):
    b, h, o, area = p["b"], p["h"], p["o"], p["area"]
    return [
        {"title": "理解题意",
         "content": f"一个平行四边形，底 {b} 格，高 {h} 格。顶点 D 可以沿与底边平行的线左右移动（对顶点 C 跟着联动，高始终是 {h} 格）。"},
        {"title": "平行四边形面积公式",
         "content": f"平行四边形面积 = 底 × 高 = {b} × {h} = {area}（格²）。"},
        {"title": "等底等高，面积不变",
         "content": f"D 左右移动时，底还是 {b} 格，高还是 {h} 格，所以面积始终是 {area} 格²。这就叫「等底等高的平行四边形面积相等」。"},
        {"title": "割补变成长方形",
         "content": f"把 D 拖到 A 的正上方（C 自然落到 B 的正上方），就变成长方形；面积不变，还是 {b} × {h} = {area} 格²。"},
        {"title": "验证",
         "content": f"长方形长 {b} 格、宽 {h} 格，面积 = {b} × {h} = {area} 格²，正好。"},
    ]


def tri_height_steps(p):
    b, h, y0, mid, area = p["b"], p["h"], p["y0"], p["mid"], p["area"]
    return [
        {"title": "理解题意",
         "content": f"一个三角形，底 {b} 格。要使面积等于 {area} 格²，高应该是多少格？"},
        {"title": "面积公式逆用",
         "content": f"三角形面积 = 底 × 高 ÷ 2。已知面积 {area} 格²、底 {b} 格，求高。"},
        {"title": "求高",
         "content": f"高 = 面积 × 2 ÷ 底 = {area} × 2 ÷ {b} = {area * 2} ÷ {b} = {h}（格）。"},
        {"title": "验证",
         "content": f"把 C 拉到高 {h} 格，面积 = {b} × {h} ÷ 2 = {area} 格²，正好。"},
    ]


def trapezoid_steps(p):
    b, u, h, o0, mid, area = p["b"], p["u"], p["h"], p["o0"], p["mid"], p["area"]
    return [
        {"title": "理解题意",
         "content": f"一个梯形，下底 {b} 格，上底 {u} 格，高 {h} 格。顶点 D 可以左右移动（上底跟着平移，高不变）。"},
        {"title": "梯形面积公式",
         "content": f"梯形面积 = （上底 + 下底）× 高 ÷ 2 = （{u} + {b}）× {h} ÷ 2 = {b + u} × {h} ÷ 2 = {area}（格²）。"},
        {"title": "等积变形",
         "content": f"D 左右移动时，上底还是 {u} 格、下底还是 {b} 格、高还是 {h} 格，所以面积始终是 {area} 格²。"},
        {"title": "变成等腰梯形",
         "content": f"把 D 拖到第 {mid} 格，上底正好居中，左右两腰一样长，就是等腰梯形。"},
        {"title": "验证",
         "content": f"D 停在第 {mid} 格，梯形面积仍是 （{u} + {b}）× {h} ÷ 2 = {area} 格²。"},
    ]


def recompose_steps(p):
    b, h, o, area = p["b"], p["h"], p["o"], p["area"]
    return [
        {"title": "理解题意",
         "content": f"一个平行四边形，底 {b} 格，高 {h} 格。沿着高把它剪成一个三角形和一个梯形。"},
        {"title": "割补",
         "content": f"把左边的三角形割下来，平移到右边，正好补成一个长方形。"},
        {"title": "长方形面积",
         "content": f"拼成的长方形长 {b} 格、宽 {h} 格，面积 = {b} × {h} = {area} 格²。"},
        {"title": "验证",
         "content": f"所以平行四边形面积 = 底 × 高 = {b} × {h} = {area} 格²，割补前后面积不变。"},
    ]


def circle_steps(p):
    r, dia, C = p["r"], p["d"], p["C"]
    return [
        {"title": "理解题意",
         "content": f"一个圆，半径 {r} 格。圆周率取 3，求这个圆的周长。"},
        {"title": "先求直径",
         "content": f"直径 = 半径 × 2 = {r} × 2 = {dia}（格）。"},
        {"title": "周长公式（圆周率取 3）",
         "content": f"周长 = 直径 × 圆周率 = {dia} × 3 = {C}（格）。"},
        {"title": "验证",
         "content": f"把半径拨到 {r} 格，直径 {dia} 格、周长 {C} 格，正好。"},
    ]


def circle_area_steps(p):
    r, dia, S = p["r"], p["d"], p["S"]
    return [
        {"title": "理解题意",
         "content": f"一个圆，半径 {r} 格。圆周率取 3，求这个圆的面积。"},
        {"title": "面积公式（圆周率取 3）",
         "content": f"圆面积 = 半径 × 半径 × 圆周率 = {r} × {r} × 3 = {S}（格²）。"},
        {"title": "用方格理解",
         "content": f"圆周率取 3，圆的面积正好是 3 个「半径 × 半径」的小方格，即 3 × {r}² = {S} 格²。"},
        {"title": "验证",
         "content": f"把半径拨到 {r} 格，面积 = {r}² × 3 = {S} 格²，正好。"},
    ]


def semicircle_steps(p):
    r, dia, arc, C = p["r"], p["d"], p["arc"], p["C"]
    return [
        {"title": "理解题意",
         "content": f"一个半圆，半径 {r} 格。圆周率取 3，求这个半圆的周长。"},
        {"title": "半圆弧长",
         "content": f"半圆弧长 = 圆周长的一半 = 直径 × 3 ÷ 2 = {dia} × 3 ÷ 2 = {arc}（格）。"},
        {"title": "别忘了直径",
         "content": f"半圆周长 = 半圆弧长 + 直径 = {arc} + {dia} = {C}（格）。很多同学会漏掉直径！"},
        {"title": "验证",
         "content": f"把半径拨到 {r} 格，半圆周长 = {arc} + {dia} = {C} 格，正好。"},
    ]
