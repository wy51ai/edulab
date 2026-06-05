#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate self-contained higher-mathematics lesson pages.
"""

from __future__ import annotations

import copy
import json
import random
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "template" / "lesson.html"
PLACEHOLDER = "__LESSON_DATA__"

sys.path.insert(0, str(SKILL_DIR / "lib"))
import calculus_kernel as ck  # noqa: E402


UI_ZH = {
    "previous": "上一步",
    "next": "下一步",
    "finish": "完成",
    "stepTemplate": "步骤 {current} / {total}",
    "visualLabel": "交互图示",
    "layersLabel": "图层",
}


def render_html(data: dict, out_path: Path) -> Path:
    """Inject lesson data into the HTML template."""
    template = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise RuntimeError(f"Template is missing placeholder {PLACEHOLDER}")

    payload_data = copy.deepcopy(data)
    payload_data.pop("_answer", None)
    payload = json.dumps(payload_data, ensure_ascii=False, indent=2)
    out_path.write_text(template.replace(PLACEHOLDER, payload), encoding="utf-8")
    return out_path


def build_double_integral_data() -> dict:
    sol = ck.solve_cartesian_double_integral("x + y", (0, 1), (0, 2))
    ans = sol["answer_latex"]
    title = r"计算二重积分 $\int_0^1\int_0^2 (x+y)\,dy\,dx$"

    steps = [
        {
            "title": "识别积分区域",
            "content": (
                r"<p>积分区域是矩形 $D=\{(x,y)\mid 0\le x\le 1,\ 0\le y\le 2\}$。</p>"
                r"<p>这一步先把二维区域画出来，避免把积分限和变量顺序混在一起。</p>"
            ),
            "highlight": ["domain"],
        },
        {
            "title": "先对 y 积分",
            "content": (
                r"<p>固定 $x$，内层积分为：</p>"
                r"$$\int_0^2 (x+y)\,dy = " + sol["inner_latex"] + r"$$"
            ),
            "highlight": ["domain", "slices"],
        },
        {
            "title": "再对 x 积分",
            "content": (
                r"<p>把内层结果沿 $x$ 从 $0$ 到 $1$ 积分：</p>"
                r"$$\int_0^1 " + sol["inner_latex"] + r"\,dx$$"
            ),
            "highlight": ["domain", "height"],
        },
        {
            "title": "得到精确答案",
            "content": (
                r"$$\int_0^1\int_0^2 (x+y)\,dy\,dx = " + ans + r"$$"
                r"<p>所以二重积分的值为 $" + ans + r"$。</p>"
            ),
            "highlight": ["domain", "height", "answer"],
        },
    ]

    return {
        "lesson": {
            "language": "zh-CN",
            "meta": "高等数学 · 二重积分",
            "title": title,
            "answerLabel": "二重积分的值",
            "answerValue": f"${ans}$",
            "ui": UI_ZH,
        },
        "steps": steps,
        "visual": {
            "type": "double_integral",
            "xBounds": sol["bounds_latex"]["x"],
            "yBounds": sol["bounds_latex"]["y"],
            "integrand": sol["integrand_latex"],
            "samples": sol["samples"],
            "layers": [
                {"id": "domain", "label": "积分区域"},
                {"id": "slices", "label": "内层切片"},
                {"id": "height", "label": "函数高度"},
                {"id": "answer", "label": "累计结果"},
            ],
        },
        "_answer": ans,
    }


def build_polar_integral_data() -> dict:
    sol = ck.solve_polar_double_integral("1", (0, 1), (0, "2*pi"))
    ans = sol["answer_latex"]
    steps = [
        {
            "title": "把区域写成极坐标",
            "content": r"<p>单位圆盘可写成 $0\le r\le 1,\ 0\le\theta\le 2\pi$。</p>",
            "highlight": ["domain"],
        },
        {
            "title": "不要忘记雅可比因子",
            "content": (
                r"<p>极坐标面积元是 $dA=r\,dr\,d\theta$。</p>"
                r"<p>原 integrand 为 $1$，所以实际积分 integrand 为 $" + sol["jacobian_integrand_latex"] + r"$。</p>"
            ),
            "highlight": ["domain", "jacobian"],
        },
        {
            "title": "先对 r 积分",
            "content": r"$$\int_0^1 r\,dr = " + sol["inner_latex"] + r"$$",
            "highlight": ["rings"],
        },
        {
            "title": "沿角度累积",
            "content": (
                r"$$\int_0^{2\pi}\int_0^1 r\,dr\,d\theta = " + ans + r"$$"
                r"<p>所以单位圆盘面积为 $" + ans + r"$。</p>"
            ),
            "highlight": ["rings", "answer"],
        },
    ]
    return {
        "lesson": {
            "language": "zh-CN",
            "meta": "高等数学 · 极坐标二重积分",
            "title": r"用极坐标计算单位圆盘面积 $\iint_D 1\,dA$",
            "answerLabel": "单位圆盘面积",
            "answerValue": f"${ans}$",
            "ui": UI_ZH,
        },
        "steps": steps,
        "visual": {
            "type": "polar_integral",
            "rBounds": sol["bounds_latex"]["r"],
            "thetaBounds": sol["bounds_latex"]["theta"],
            "integrand": sol["integrand_latex"],
            "jacobianIntegrand": sol["jacobian_integrand_latex"],
            "samples": sol["samples"],
            "layers": [
                {"id": "domain", "label": "圆盘区域"},
                {"id": "jacobian", "label": "面积元 r"},
                {"id": "rings", "label": "同心环"},
                {"id": "answer", "label": "结果"},
            ],
        },
        "_answer": ans,
    }


def build_surface_flux_data() -> dict:
    sol = ck.solve_surface_flux(("x", "y", "z"), ("u", "v", "1"), (0, 1), (0, 1))
    ans = sol["answer_latex"]
    field = r"\mathbf F=(x,y,z)"
    surface = r"\mathbf r(u,v)=(u,v,1)"
    steps = [
        {
            "title": "写出参数曲面",
            "content": (
                r"<p>曲面取参数化 $" + surface + r"$，其中 $0\le u\le 1,\ 0\le v\le 1$。</p>"
                r"<p>可视化中网格表示这个位于 $z=1$ 的单位正方形。</p>"
            ),
            "highlight": ["surface"],
        },
        {
            "title": "求有向法向量",
            "content": (
                r"<p>通量公式使用 $\mathbf r_u\times\mathbf r_v$：</p>"
                r"$$\mathbf r_u\times\mathbf r_v=(" + ", ".join(sol["normal_latex"]) + r")$$"
            ),
            "highlight": ["surface", "normal"],
        },
        {
            "title": "代入向量场",
            "content": (
                r"<p>给定 $" + field + r"$，代入曲面后与法向量点乘：</p>"
                r"$$\mathbf F(\mathbf r(u,v))\cdot(\mathbf r_u\times\mathbf r_v)=" + sol["integrand_latex"] + r"$$"
            ),
            "highlight": ["surface", "normal", "field"],
        },
        {
            "title": "化为二重积分",
            "content": (
                r"$$\int_0^1\int_0^1 " + sol["integrand_latex"] + r"\,dv\,du=" + ans + r"$$"
                r"<p>所以该曲面的通量为 $" + ans + r"$。</p>"
            ),
            "highlight": ["surface", "normal", "field", "answer"],
        },
    ]
    return {
        "lesson": {
            "language": "zh-CN",
            "meta": "高等数学 · 曲面积分 / 通量",
            "title": r"求向量场 $\mathbf F=(x,y,z)$ 穿过 $\mathbf r(u,v)=(u,v,1)$ 的通量",
            "answerLabel": "曲面通量",
            "answerValue": f"${ans}$",
            "ui": UI_ZH,
        },
        "steps": steps,
        "visual": {
            "type": "surface_flux",
            "surface": sol["samples"]["surface"],
            "vectors": sol["samples"]["vectors"],
            "integrand": sol["integrand_latex"],
            "layers": [
                {"id": "surface", "label": "参数曲面"},
                {"id": "normal", "label": "有向法向量"},
                {"id": "field", "label": "向量场"},
                {"id": "answer", "label": "通量"},
            ],
        },
        "_answer": ans,
    }


def build_ode_data() -> dict:
    sol = ck.solve_first_order_ode("y", 0, 1, sample_bounds=(-1, 1))
    ans = sol["solution_latex"]
    steps = [
        {
            "title": "识别微分方程",
            "content": r"<p>题目是初值问题 $\frac{dy}{dx}=y,\ y(0)=1$。</p>",
            "highlight": ["slope"],
        },
        {
            "title": "分离变量",
            "content": r"<p>当 $y\ne 0$ 时，$\frac{dy}{y}=dx$。</p>",
            "highlight": ["slope"],
        },
        {
            "title": "积分并代入初值",
            "content": r"<p>积分得 $\ln|y|=x+C$，由 $y(0)=1$ 可得 $C=0$。</p>",
            "highlight": ["initial"],
        },
        {
            "title": "得到解曲线",
            "content": (
                r"$$y=" + ans + r"$$"
                r"<p>所以该初值问题的解为 $" + ans + r"$。右侧斜率场中的粗线就是这条解曲线。</p>"
            ),
            "highlight": ["slope", "initial", "solution"],
        },
    ]
    return {
        "lesson": {
            "language": "zh-CN",
            "meta": "高等数学 · 微分方程",
            "title": r"求解初值问题 $\frac{dy}{dx}=y,\ y(0)=1$",
            "answerLabel": "微分方程的特解",
            "answerValue": f"$y={ans}$",
            "ui": UI_ZH,
        },
        "steps": steps,
        "visual": {
            "type": "ode_slope_field",
            "equation": sol["equation_latex"],
            "initial": sol["samples"]["initial"],
            "slopeField": sol["samples"]["slope_field"],
            "solutionCurve": sol["samples"]["solution_curve"],
            "layers": [
                {"id": "slope", "label": "斜率场"},
                {"id": "initial", "label": "初值点"},
                {"id": "solution", "label": "解曲线"},
            ],
        },
        "_answer": ans,
    }


def build_random_data(seed=0) -> dict:
    rng = random.Random(seed)
    return rng.choice(
        [
            build_double_integral_data,
            build_polar_integral_data,
            build_surface_flux_data,
            build_ode_data,
        ]
    )()


PROBLEMS = {
    "double-integral": build_double_integral_data,
    "polar-integral": build_polar_integral_data,
    "surface-flux": build_surface_flux_data,
    "ode": build_ode_data,
}


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    mode = "double-integral"
    out = None
    seed = 0

    for arg in args:
        if arg in PROBLEMS or arg == "random":
            mode = arg
        elif arg.isdigit():
            seed = int(arg)
        else:
            out = Path(arg)

    if out is None:
        out = Path.cwd() / f"{mode}.html"
    out.parent.mkdir(parents=True, exist_ok=True)

    data = build_random_data(seed) if mode == "random" else PROBLEMS[mode]()
    final_step = data["steps"][-1]["content"]
    assert data["_answer"] in data["lesson"]["answerValue"], "Answer card does not contain kernel answer"
    assert data["_answer"] in final_step, "Final step does not contain kernel answer"

    render_html(data, out)
    print(f"generated: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
