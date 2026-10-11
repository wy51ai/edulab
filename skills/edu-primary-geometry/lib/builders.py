# -*- coding: utf-8 -*-
"""题型 → schema 组装。几何题复用统一骨架 _base / _expr / _answer。"""
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
# 面积公式推导
# ---------------------------------------------------------------------------

def build_area_parallelogram(p):
    a, h, S = p["a"], p["h"], p["S"]
    dx0, dxMax = p["dx0"], p["dxMax"]
    problem = f"一个平行四边形，底是 {a} 厘米，高是 {h} 厘米。它的面积是多少平方厘米？"
    d0 = _base("area-parallelogram", "平行四边形面积 · 剪拼", problem,
               f"拖动绿色顶点 D（等积变形，面积不变）；或播放动画，看平行四边形剪拼成长方形。",
               "剪拼进度")
    d0["scene"] = {
        "kind": "cut-rearrange", "cap": "平行四边形 → 长方形",
        "world": {"xMax": a + dxMax + 1, "yMax": h + 2, "pad": 34},
        "points": [
            {"name": "A", "x": 0, "y": 0, "fixed": True, "color": "#e2553f", "label": "A"},
            {"name": "B", "x": a, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "B"},
            {"name": "D", "x": dx0, "y": h, "snap": "grid", "constraint": "h-line",
             "min": 0, "max": dxMax, "color": "#2ecc71", "label": "D 拖我"},
        ],
        "known": {"a": a, "h": h},
        "param": {"min": 0, "max": 2, "step": 0.1, "value": 0,
                  "label": "剪拼进度", "answer": 2},
    }
    d0["answer"] = {"S": S, "a": a, "h": h}
    d0["readouts"] = [
        _expr("底", "a", unit="厘米", color="#3b7dd8"),
        _expr("高", "h", unit="厘米", color="#e2553f"),
        _expr("面积", "S", unit="平方厘米", color="#2ecc71"),
        _answer("公式", f"S = {a} × {h} = {S} cm²"),
    ]
    d0["status"] = {
        "before": {"text": "拖动顶点 D 看面积不变；再播放动画看剪拼…", "color": "amber"},
        "at": {"text": f"拼成长方形！面积 = 底 × 高 = {a} × {h} = {S}（平方厘米）", "color": "green"},
        "after": {"text": "已到达结论", "color": "blue"},
    }
    d0["steps"] = steps.area_parallelogram_steps(p)
    return d0


def build_area_triangle(p):
    a, h, S = p["a"], p["h"], p["S"]
    cx0, cxMin, cxMax = p["cx0"], p["cxMin"], p["cxMax"]
    problem = f"一个三角形，底是 {a} 厘米，高是 {h} 厘米。它的面积是多少平方厘米？"
    d0 = _base("area-triangle", "三角形面积 · 双拼", problem,
               f"拖动绿色顶点（等积变形，面积不变）；或播放动画，看两个全等三角形拼成平行四边形。",
               "拼图进度")
    d0["scene"] = {
        "kind": "cut-rearrange", "cap": "三角形 → 平行四边形", "variant": "triangle",
        "world": {"xMax": 2 * a, "yMax": h + 2, "pad": 34},
        "points": [
            {"name": "A", "x": 0, "y": 0, "fixed": True, "color": "#e2553f", "label": "A"},
            {"name": "B", "x": a, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "B"},
            {"name": "D", "x": cx0, "y": h, "snap": "grid", "constraint": "h-line",
             "min": cxMin, "max": cxMax, "color": "#2ecc71", "label": "C 拖我"},
        ],
        "known": {"a": a, "h": h},
        "param": {"min": 0, "max": 2, "step": 0.1, "value": 0,
                  "label": "拼图进度", "answer": 2},
    }
    d0["answer"] = {"S": S, "a": a, "h": h}
    d0["readouts"] = [
        _expr("底", "a", unit="厘米", color="#3b7dd8"),
        _expr("高", "h", unit="厘米", color="#e2553f"),
        _expr("面积", "S", unit="平方厘米", color="#2ecc71"),
        _answer("公式", f"S = {a} × {h} ÷ 2 = {S} cm²"),
    ]
    d0["status"] = {
        "before": {"text": "拖动顶点看等积变形；再播放看双拼成平行四边形…", "color": "amber"},
        "at": {"text": f"拼成平行四边形！三角形面积 = 底 × 高 ÷ 2 = {a} × {h} ÷ 2 = {S}", "color": "green"},
        "after": {"text": "已到达结论", "color": "blue"},
    }
    d0["steps"] = steps.area_triangle_steps(p)
    return d0


def build_area_trapezoid(p):
    a, b, h, S = p["a"], p["b"], p["h"], p["S"]
    dx0, dxMin, dxMax = p["dx0"], p["dxMin"], p["dxMax"]
    problem = f"一个梯形，上底 {a} 厘米，下底 {b} 厘米，高 {h} 厘米。它的面积是多少平方厘米？"
    d0 = _base("area-trapezoid", "梯形面积 · 双拼", problem,
               f"拖动绿色顶点 D（上底平移，面积不变）；或播放动画，看两个全等梯形拼成平行四边形。",
               "拼图进度")
    d0["scene"] = {
        "kind": "cut-rearrange", "cap": "梯形 → 平行四边形", "variant": "trapezoid",
        "world": {"xMax": 2 * b + 1, "yMax": h + 2, "pad": 34},
        "points": [
            {"name": "A", "x": 0, "y": 0, "fixed": True, "color": "#e2553f", "label": "A"},
            {"name": "B", "x": b, "y": 0, "fixed": True, "color": "#3b7dd8", "label": "B"},
            {"name": "D", "x": dx0, "y": h, "snap": "grid", "constraint": "h-line",
             "min": dxMin, "max": dxMax, "color": "#2ecc71", "label": "D 拖我"},
        ],
        "known": {"a": a, "b": b, "h": h},
        "param": {"min": 0, "max": 2, "step": 0.1, "value": 0,
                  "label": "拼图进度", "answer": 2},
    }
    d0["answer"] = {"S": S, "a": a, "b": b, "h": h}
    d0["readouts"] = [
        _expr("上底", "a", unit="厘米", color="#3b7dd8"),
        _expr("下底", "b", unit="厘米", color="#e2553f"),
        _expr("面积", "S", unit="平方厘米", color="#2ecc71"),
        _answer("公式", f"S = ({a} + {b}) × {h} ÷ 2 = {S} cm²"),
    ]
    d0["status"] = {
        "before": {"text": "拖动顶点 D 看等积变形；再播放看双拼成平行四边形…", "color": "amber"},
        "at": {"text": f"拼成平行四边形！梯形面积 = (上底 + 下底) × 高 ÷ 2 = {S}", "color": "green"},
        "after": {"text": "已到达结论", "color": "blue"},
    }
    d0["steps"] = steps.area_trapezoid_steps(p)
    return d0


def build_area_circle(p):
    r, S, pi = p["r"], p["S"], p["pi"]
    nMin, nMax = p["nMin"], p["nMax"]
    problem = f"一个圆，半径是 {r} 厘米（π 取 3）。它的面积约是多少平方厘米？"
    d0 = _base("area-circle", "圆面积 · 扇形展开", problem,
               f"拖动滑块改变等分数 N，N 越大扇形拼出的图形越接近长方形。",
               "等分数 N")
    d0["scene"] = {
        "kind": "cut-rearrange", "cap": "圆 → 近似长方形", "variant": "circle",
        "world": {"xMax": 2 * r + 2, "yMax": 2 * r + 2, "pad": 24},
        "points": [],
        "known": {"r": r, "pi": pi},
        "param": {"min": nMin, "max": nMax, "step": 1, "value": nMin,
                  "label": "等分数 N", "answer": nMax},
    }
    d0["answer"] = {"S": S, "r": r}
    d0["readouts"] = [
        _expr("半径", "r", unit="厘米", color="#e2553f"),
        _expr("等分数", "N", unit="份"),
        _expr("面积", "S", unit="平方厘米", color="#2ecc71"),
        _answer("公式", f"S = πr² ≈ 3 × {r}² = {S} cm²"),
    ]
    d0["status"] = {
        "before": {"text": "增加等分数 N，看扇形拼出的图形越来越接近长方形…", "color": "amber"},
        "at": {"text": f"拼成近似长方形！圆面积 ≈ πr² ≈ 3 × {r}² = {S}（平方厘米）", "color": "green"},
        "after": {"text": "已到达结论", "color": "blue"},
    }
    d0["steps"] = steps.area_circle_steps(p)
    return d0


def build_composite_area(p):
    a, H, b, h, S = p["a"], p["H"], p["b"], p["h"], p["S"]
    problem = f"一个 L 形组合图形（竖长方形 {a}×{H}，横长方形 {b}×{h}）。它的面积是多少平方厘米？"
    d0 = _base("composite-area", "组合图形面积 · 分割", problem,
               f"拖动绿色辅助线，把 L 形切成两个长方形，再分别求面积相加。",
               "辅助线位置 x")
    d0["scene"] = {
        "kind": "grid-split", "cap": "L 形 → 两个长方形",
        "world": {"xMax": a + b + 1, "yMax": H + 1, "pad": 30},
        "points": [
            {"name": "cut", "x": a + b - 1, "y": H, "snap": "grid", "constraint": "h-line",
             "min": 1, "max": a + b - 1, "ax": a, "ay": H, "color": "#2ecc71", "label": "辅助线"},
        ],
        "dragToT": "cut",
        "known": {"a": a, "H": H, "b": b, "h": h},
        "param": {"min": 1, "max": a + b - 1, "step": 1, "value": a + b - 1,
                  "label": "辅助线 x", "answer": a},
    }
    d0["answer"] = {"S": S}
    d0["readouts"] = [
        _expr("竖长方形", "a*H", unit="平方厘米", color="#3b7dd8"),
        _expr("横长方形", "b*h", unit="平方厘米", color="#e2553f"),
        _expr("总面积", "S", unit="平方厘米", color="#2ecc71"),
        _answer("答案", f"{S} 平方厘米"),
    ]
    d0["status"] = {
        "before": {"text": "拖动辅助线，把 L 形切成两个长方形…", "color": "amber"},
        "at": {"text": f"切对了！面积 = {a}×{H} + {b}×{h} = {S}（平方厘米）", "color": "green"},
        "after": {"text": "辅助线位置不对，调整…", "color": "blue"},
    }
    d0["steps"] = steps.composite_area_steps(p)
    return d0


def build_grid_count(p):
    G, rows, widths, f, hb, S = p["G"], p["rows"], p["widths"], p["f"], p["hb"], p["S"]
    problem = f"数一数方格纸上这个不规则图形（{G}×{G} 方格）：面积约是多少平方厘米？"
    d0 = _base("grid-count", "不规则图形估算 · 数方格", problem,
               f"满格按 1 格、半格按半格数，拖动滑块找到面积。",
               "面积（平方厘米）")
    d0["scene"] = {
        "kind": "grid", "cap": "数方格估面积",
        "world": {"xMax": G, "yMax": G, "pad": 30},
        "points": [],
        "known": {"G": G, "rows": rows, "widths": widths, "f": f, "hb": hb},
        "param": {"min": 1, "max": S + 4, "step": 1, "value": 1,
                  "label": "面积（平方厘米）", "answer": S},
    }
    d0["answer"] = {"S": S}
    d0["readouts"] = [
        _expr("满格", "f", unit="格", color="#3b7dd8"),
        _expr("半格", "hb", unit="格", color="#e2553f"),
        _expr("面积", "S", unit="平方厘米", color="#2ecc71"),
        _answer("答案", f"约 {S} 平方厘米"),
    ]
    d0["status"] = {
        "before": {"text": "数一数满格和半格，找到面积…", "color": "amber"},
        "at": {"text": f"找对了！{f} 满格 + {hb} 半格÷2 = {S}（平方厘米）", "color": "green"},
        "after": {"text": "面积估大了，往回调整…", "color": "blue"},
    }
    d0["steps"] = steps.grid_count_steps(p)
    return d0


def build_three_view(p):
    cols, heights, front = p["cols"], p["heights"], p["front"]
    top, side = p["top"], p["side"]
    hs = "、".join(str(x) for x in heights)
    problem = f"用小方块摆了一个立体（{cols} 列，各列高度 {hs}）。从正面看，一共有多少个小方块（格子）？"
    d0 = _base("three-view", "观察物体 · 三视图", problem,
               f"从正面数每列的高度，拖动滑块找到正面视图的格子数。",
               "正面格子数")
    d0["scene"] = {
        "kind": "solid-views", "cap": "立体 → 三视图",
        "world": {"xMax": cols + 2, "yMax": max(heights) + 2, "pad": 30},
        "points": [],
        "known": {"cols": cols, "heights": heights, "top": top, "side": side},
        "param": {"min": 1, "max": front + 3, "step": 1, "value": 1,
                  "label": "正面格子数", "answer": front},
    }
    d0["answer"] = {"front": front}
    d0["readouts"] = [
        _expr("列数", "cols", unit="列", color="#3b7dd8"),
        _expr("正面", "front", unit="格", color="#e2553f"),
        _answer("答案", f"正面 {front} 格"),
    ]
    d0["status"] = {
        "before": {"text": "从正面数一数每列高度…", "color": "amber"},
        "at": {"text": f"找对了！正面视图 = {front} 格", "color": "green"},
        "after": {"text": "数多了，再数数…", "color": "blue"},
    }
    d0["steps"] = steps.three_view_steps(p)
    return d0


def build_transform_symmetry(p):
    mode, A, B, C, ax, ay, rule = p["mode"], p["A"], p["B"], p["C"], p["ax"], p["ay"], p["rule"]
    problem = (f"方格纸上有一个三角形 A({A[0]},{A[1]})、B({B[0]},{B[1]})、C({C[0]},{C[1]})。"
               f"{rule}。请把 A 的对应点 A' 拖到正确位置。")
    d0 = _base("transform-symmetry", "平移 / 轴对称 · 找对应点", problem,
               f"拖动绿色点 A'，把它放到 A 点经过「{rule}」后的位置。",
               "提示")
    d0["scene"] = {
        "kind": "grid-transform", "cap": "方格纸 · " + rule,
        "world": {"xMax": 12, "yMax": 8, "pad": 30},
        "points": [
            {"name": "Ap", "x": A[0], "y": A[1], "snap": "grid",
             "min": 1, "max": 11, "ymin": 1, "ymax": 6,
             "ax": ax, "ay": ay, "color": "#2ecc71", "label": "A' 拖我"},
        ],
        "known": {"mode": mode, "A": A, "B": B, "C": C, "ax": ax, "ay": ay, "rule": rule},
        "param": {"min": 0, "max": 1, "step": 1, "value": 0, "label": "提示", "answer": 1},
    }
    d0["answer"] = {"ax": ax, "ay": ay}
    d0["readouts"] = [
        _expr("A' 横坐标", "Ax", unit="格", color="#3b7dd8"),
        _expr("A' 纵坐标", "Ay", unit="格", color="#e2553f"),
        _answer("答案", f"A' = ({ax}, {ay})"),
    ]
    d0["status"] = {
        "before": {"text": f"把 A' 拖到 A 经过「{rule}」后的位置…", "color": "amber"},
        "at": {"text": f"找对了！A' = ({ax}, {ay})", "color": "green"},
        "after": {"text": "（已提示答案）", "color": "blue"},
    }
    d0["steps"] = steps.transform_symmetry_steps(p)
    return d0


def build_cuboid_volume(p):
    a, b, c, V, S = p["a"], p["b"], p["c"], p["V"], p["S"]
    problem = f"一个长方体，长 {a} 厘米、宽 {b} 厘米、高 {c} 厘米。它的体积是多少立方厘米？"
    d0 = _base("cuboid-volume", "长方体 · 体积 / 表面积", problem,
               f"看长方体和它的展开图，拖动滑块找到体积。",
               "体积（立方厘米）")
    d0["scene"] = {
        "kind": "solid-net", "cap": "长方体 + 展开图",
        "world": {"xMax": a + b + 3, "yMax": b + c + 3, "pad": 26},
        "points": [],
        "known": {"a": a, "b": b, "c": c, "S": S},
        "param": {"min": 1, "max": V + 8, "step": 1, "value": 1,
                  "label": "体积（立方厘米）", "answer": V},
    }
    d0["answer"] = {"V": V}
    d0["readouts"] = [
        _expr("长", "a", unit="厘米", color="#3b7dd8"),
        _expr("宽", "b", unit="厘米", color="#e2553f"),
        _expr("高", "c", unit="厘米", color="#2ecc71"),
        _expr("体积", "V", unit="立方厘米"),
        _answer("答案", f"V = {a}×{b}×{c} = {V} cm³"),
    ]
    d0["status"] = {
        "before": {"text": "长 × 宽 × 高，找到体积…", "color": "amber"},
        "at": {"text": f"找对了！V = {a} × {b} × {c} = {V}（立方厘米）", "color": "green"},
        "after": {"text": "体积估大了，调整…", "color": "blue"},
    }
    d0["steps"] = steps.cuboid_volume_steps(p)
    return d0
