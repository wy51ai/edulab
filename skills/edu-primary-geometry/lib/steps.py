# -*- coding: utf-8 -*-
"""几何题中文分步讲解（全 Unicode − × ÷，无需公式渲染器）。"""


def area_parallelogram_steps(p):
    a, h, S = p["a"], p["h"], p["S"]
    return [
        {"title": "数底和高",
         "content": f"平行四边形的底是 {a} 厘米，高是 {h} 厘米（高是顶点到底边的垂直距离）。"},
        {"title": "沿高剪开",
         "content": f"从顶点沿高剪下一个直角三角形（两条直角边分别是 {p['dx0']} 和 {h}）。"},
        {"title": "平移拼成长方形",
         "content": f"把剪下的三角形平移到另一边，拼成一个长 {a} 厘米、宽 {h} 厘米的长方形。"},
        {"title": "面积不变",
         "content": f"剪拼前后面积不变，所以平行四边形面积 = 长方形面积 = 长 × 宽 = {a} × {h}。"},
        {"title": "得出公式",
         "content": f"平行四边形面积 = 底 × 高 = {a} × {h} = {S}（平方厘米）。"},
    ]


def area_triangle_steps(p):
    a, h, S = p["a"], p["h"], p["S"]
    return [
        {"title": "数底和高",
         "content": f"三角形的底是 {a} 厘米，高是 {h} 厘米。"},
        {"title": "复制一个全等三角形",
         "content": "再拿一个完全一样的三角形，倒过来拼在一起。"},
        {"title": "拼成平行四边形",
         "content": f"两个全等三角形拼成一个底 {a} 厘米、高 {h} 厘米的平行四边形，面积 = {a} × {h}。"},
        {"title": "取一半",
         "content": f"三角形面积是平行四边形的一半，所以 = {a} × {h} ÷ 2。"},
        {"title": "得出公式",
         "content": f"三角形面积 = 底 × 高 ÷ 2 = {a} × {h} ÷ 2 = {S}（平方厘米）。"},
    ]


def area_trapezoid_steps(p):
    a, b, h, S = p["a"], p["b"], p["h"], p["S"]
    return [
        {"title": "数上底、下底和高",
         "content": f"梯形的上底是 {a} 厘米，下底是 {b} 厘米，高是 {h} 厘米。"},
        {"title": "复制一个全等梯形",
         "content": "再拿一个完全一样的梯形，倒过来拼在一起。"},
        {"title": "拼成平行四边形",
         "content": f"两个全等梯形拼成一个底 {a} + {b} = {a + b} 厘米、高 {h} 厘米的平行四边形。"},
        {"title": "取一半",
         "content": f"梯形面积是平行四边形的一半，所以 = ({a} + {b}) × {h} ÷ 2。"},
        {"title": "得出公式",
         "content": f"梯形面积 = (上底 + 下底) × 高 ÷ 2 = ({a} + {b}) × {h} ÷ 2 = {S}（平方厘米）。"},
    ]


def area_circle_steps(p):
    r, S = p["r"], p["S"]
    return [
        {"title": "分成扇形",
         "content": f"把圆沿半径分成许多个相等的扇形（半径 = {r} 厘米）。"},
        {"title": "越分越细",
         "content": "扇形分得越多，拼出来的图形越接近长方形。"},
        {"title": "拼成长方形",
         "content": f"拼成的近似长方形，宽 ≈ 半径 {r}，长 ≈ 半周长 π×{r}（π≈3 时约 {3 * r}）。"},
        {"title": "面积公式",
         "content": f"圆面积 = π × 半径² ≈ 3 × {r} × {r}。"},
        {"title": "得出结果",
         "content": f"圆面积 ≈ 3 × {r}² = {S}（平方厘米）。"},
    ]


def composite_area_steps(p):
    a, H, b, h, S = p["a"], p["H"], p["b"], p["h"], p["S"]
    return [
        {"title": "分割成两个长方形",
         "content": f"沿辅助线（x = {a}）把 L 形分成：竖长方形 {a} × {H} 和横长方形 {b} × {h}。"},
        {"title": "分别求面积",
         "content": f"竖长方形面积 = {a} × {H} = {a * H}；横长方形面积 = {b} × {h} = {b * h}。"},
        {"title": "相加",
         "content": f"总面积 = {a * H} + {b * h}。"},
        {"title": "得出结果",
         "content": f"组合图形面积 = {a * H} + {b * h} = {S}（平方厘米）。"},
    ]


def grid_count_steps(p):
    G, f, hb, S = p["G"], p["f"], p["hb"], p["S"]
    return [
        {"title": "数满格",
         "content": f"先数图形完整覆盖的满格，共 {f} 格。"},
        {"title": "数半格",
         "content": f"再数只被盖住一半的格子，共 {hb} 格，按 {hb} ÷ 2 = {hb // 2} 格计算。"},
        {"title": "相加",
         "content": f"估算面积 = 满格 + 半格 ÷ 2 = {f} + {hb // 2}。"},
        {"title": "得出结果",
         "content": f"图形面积约 = {f} + {hb} ÷ 2 = {S}（平方厘米）。"},
    ]


def three_view_steps(p):
    cols, heights, front = p["cols"], p["heights"], p["front"]
    hs = "、".join(str(x) for x in heights)
    return [
        {"title": "看清立体",
         "content": f"这个立体由 {cols} 列小方块组成，各列高度分别是 {hs}。"},
        {"title": "从正面看",
         "content": f"正面看过去，每列的高度就是小方块个数，一共 {front} 个。"},
        {"title": "数格子",
         "content": f"正面视图格子数 = {' + '.join(str(x) for x in heights)} = {front}。"},
        {"title": "得出结果",
         "content": f"从正面看一共有 {front} 个小方块（格子）。"},
    ]


def transform_symmetry_steps(p):
    mode, ax, ay, rule = p["mode"], p["ax"], p["ay"], p["rule"]
    A = p["A"]
    verb = {"translate": "平移", "reflect": "对称"}[mode]
    return [
        {"title": "找对应点",
         "content": f"点 A({A[0]},{A[1]}) 经过「{rule}」后，落到哪个位置？"},
        {"title": "按规则变换",
         "content": f"把 A 点按{verb}规则移动，得到对应点 A'。"},
        {"title": "核对坐标",
         "content": f"A' 的坐标应为 ({ax}, {ay})。"},
        {"title": "得出结果",
         "content": f"A 的对应点 A' = ({ax}, {ay})。"},
    ]


def cuboid_volume_steps(p):
    a, b, c, V, S = p["a"], p["b"], p["c"], p["V"], p["S"]
    return [
        {"title": "看长宽高",
         "content": f"长方体的长 = {a}，宽 = {b}，高 = {c}（单位：厘米）。"},
        {"title": "体积公式",
         "content": f"体积 = 长 × 宽 × 高 = {a} × {b} × {c}。"},
        {"title": "计算体积",
         "content": f"体积 = {a} × {b} × {c} = {V}（立方厘米）。"},
        {"title": "表面积",
         "content": f"表面积 = 2 × (长×宽 + 长×高 + 宽×高) = {S}（平方厘米）。"},
    ]
