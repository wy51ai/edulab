#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate self-contained signals/control-systems lesson pages.
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
import control_kernel as ck  # noqa: E402


UI_ZH = {
    "previous": "上一步",
    "next": "下一步",
    "finish": "完成",
    "stepTemplate": "步骤 {current} / {total}",
    "visualLabel": "反馈系统图示",
    "layersLabel": "当前关注",
    "gainLabel": "环路增益 k",
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


def _sample_solution():
    return ck.solve_negative_feedback_loop(
        forward_gain="k*A",
        feedback="1/(tau*s + 1)",
        parameter_values={"A": 1, "tau": 0.35, "k": 40},
        sample_omegas=(0.1, 0.2, 0.5, 1, 2, 5, 10),
    )


def build_feedback_limit_data() -> dict:
    symbolic = ck.solve_negative_feedback_loop("k*A", "F(s)")
    sample = _sample_solution()
    closed = symbolic["closed_loop_latex"]
    ans = symbolic["high_gain_limit_latex"]

    steps = [
        {
            "title": "读出负反馈关系",
            "content": (
                r"<p>输出 $y$ 经过反馈网络 $F(s)$ 回到求和点，并从输入 $x$ 中相减：</p>"
                r"$$u_i=x-F(s)y$$"
                r"<p>这里的关键是符号：反馈是负号，所以后面分母会出现 $1+$。</p>"
            ),
            "highlight": ["summer", "feedback"],
        },
        {
            "title": "写出前向通道",
            "content": (
                r"<p>放大器/前向通道的增益是 $kA$，因此：</p>"
                r"$$y=kA\,u_i=kA\left(x-F(s)y\right)$$"
            ),
            "highlight": ["forward", "signal"],
        },
        {
            "title": "把 y 项移到同一边",
            "content": (
                r"$$y+kAF(s)y=kAx$$"
                r"$$y\left(1+kAF(s)\right)=kAx$$"
                r"<p>这一步就是从框图变成代数方程。</p>"
            ),
            "highlight": ["equation"],
        },
        {
            "title": "得到闭环传递函数",
            "content": (
                r"<p>定义 $H(s)=\frac{y}{x}$，所以：</p>"
                r"$$H(s)=\frac{y}{x}=" + closed + r"$$"
            ),
            "highlight": ["answer", "forward", "feedback"],
        },
        {
            "title": "让 k 趋于无穷大",
            "content": (
                r"<p>把分子分母同时除以 $kA$：</p>"
                r"$$H(s)=\frac{1}{F(s)+\frac{1}{kA}}$$"
                r"<p>当 $k\to\infty$ 时，$\frac{1}{kA}\to 0$，因此：</p>"
                r"$$\lim_{k\to\infty}H(s)=" + ans + r"$$"
            ),
            "highlight": ["answer", "limit"],
        },
    ]

    return {
        "lesson": {
            "language": "zh-CN",
            "meta": "信号与控制 · 单环负反馈",
            "title": r"由反馈框图求 $H(s)$，并计算 $k\to\infty$ 的极限",
            "answerLabel": "高环路增益极限",
            "answerValue": r"$\lim_{k\to\infty}H(s)=" + ans + r"$",
            "ui": UI_ZH,
        },
        "steps": steps,
        "visual": {
            "type": "negative_feedback_loop",
            "closedLoop": closed,
            "limit": ans,
            "forwardGain": symbolic["forward_gain_latex"],
            "feedback": symbolic["feedback_latex"],
            "loopGain": symbolic["loop_gain_latex"],
            "samples": sample["samples"],
            "gainSlider": {"min": 1, "max": 80, "value": 20},
            "layers": [
                {"id": "summer", "label": "求和点"},
                {"id": "forward", "label": "前向增益 kA"},
                {"id": "feedback", "label": "反馈网络 F(s)"},
                {"id": "equation", "label": "代数方程"},
                {"id": "limit", "label": "k 趋于无穷"},
                {"id": "answer", "label": "最终传递函数"},
            ],
        },
        "_answer": ans,
    }


def build_first_order_feedback_data() -> dict:
    sol = _sample_solution()
    closed = sol["closed_loop_latex"]
    ans = sol["high_gain_limit_latex"]

    steps = [
        {
            "title": "把反馈网络具体化",
            "content": (
                r"<p>取 $F(s)=\frac{1}{\tau s+1}$，它像一个一阶低通反馈网络。</p>"
                r"<p>仍然使用同一个负反馈公式。</p>"
            ),
            "highlight": ["feedback"],
        },
        {
            "title": "代入闭环公式",
            "content": (
                r"$$H(s)=\frac{kA}{1+kA\frac{1}{\tau s+1}}=" + closed + r"$$"
            ),
            "highlight": ["equation", "forward", "feedback"],
        },
        {
            "title": "观察高增益极限",
            "content": (
                r"<p>当 $k$ 很大时，闭环几乎由反馈网络的倒数决定：</p>"
                r"$$\lim_{k\to\infty}H(s)=" + ans + r"$$"
            ),
            "highlight": ["limit", "answer"],
        },
        {
            "title": "看频率响应的意义",
            "content": (
                r"<p>右下角曲线显示有限 $k$ 的闭环响应正在靠近高增益近似。</p>"
                r"<p>所以这个结论不是只背公式，而是能从幅相趋势上看出来：最终答案为 $" + ans + r"$。</p>"
            ),
            "highlight": ["limit", "answer", "bode"],
        },
    ]

    return {
        "lesson": {
            "language": "zh-CN",
            "meta": "信号与控制 · 一阶反馈网络",
            "title": r"负反馈系统中 $F(s)=\frac{1}{\tau s+1}$ 时的高增益近似",
            "answerLabel": "高环路增益极限",
            "answerValue": r"$\lim_{k\to\infty}H(s)=" + ans + r"$",
            "ui": UI_ZH,
        },
        "steps": steps,
        "visual": {
            "type": "first_order_feedback_loop",
            "closedLoop": closed,
            "limit": ans,
            "forwardGain": sol["forward_gain_latex"],
            "feedback": sol["feedback_latex"],
            "loopGain": sol["loop_gain_latex"],
            "samples": sol["samples"],
            "gainSlider": {"min": 1, "max": 80, "value": 40},
            "layers": [
                {"id": "summer", "label": "求和点"},
                {"id": "forward", "label": "前向增益 kA"},
                {"id": "feedback", "label": "一阶反馈 F(s)"},
                {"id": "equation", "label": "闭环公式"},
                {"id": "limit", "label": "高增益近似"},
                {"id": "bode", "label": "幅相采样"},
                {"id": "answer", "label": "最终结果"},
            ],
        },
        "_answer": ans,
    }


def build_random_data(seed=0) -> dict:
    rng = random.Random(seed)
    return rng.choice([build_feedback_limit_data, build_first_order_feedback_data])()


PROBLEMS = {
    "feedback-limit": build_feedback_limit_data,
    "first-order-feedback": build_first_order_feedback_data,
}


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    mode = "feedback-limit"
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
