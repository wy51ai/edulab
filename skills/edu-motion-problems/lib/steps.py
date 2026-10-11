# -*- coding: utf-8 -*-
"""分步讲解文案（全中文，Unicode − × ÷，不引入 KaTeX）。"""


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
