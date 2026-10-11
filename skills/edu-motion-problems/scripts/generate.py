#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate.py — 把结构化数据注入 template/board.html，产出单页小学行程问题交互课件。

数据由 lib/ 的「答案先行好数采样」驱动（单一数据源）：答案量（追上/相遇时间、相遇点、
圈数）恒为整数，题目、动画、s-t 图、步骤数值严格一致。零外部依赖（纯标准库 random + math）。

用法（任意 Python3）：
    python3 scripts/generate.py list                 # 列出题型
    python3 scripts/generate.py pursue               # 随机出一题，写技能 output/
    python3 scripts/generate.py pursue 42            # 指定种子（可复现）
    python3 scripts/generate.py meet 7 ./sol.html    # 指定输出文件
    python3 scripts/generate.py all ./out_dir        # 全部题型，各出若干随机变体
"""

import json
import random
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "template" / "board.html"
PLACEHOLDER = "__LESSON_DATA__"

sys.path.insert(0, str(SKILL_DIR / "lib"))
import good_numbers as gn  # noqa: E402
import builders            # noqa: E402


def render_html(data: dict, out_path: Path) -> Path:
    """注入数据岛 __LESSON_DATA__，写出单文件 HTML。"""
    template = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise RuntimeError(f"模板中未找到占位符 {PLACEHOLDER}")
    out_path.write_text(template.replace(PLACEHOLDER, json.dumps(data, ensure_ascii=False)),
                        encoding="utf-8")
    return out_path


def _seed_of(seed):
    return seed if seed is not None else random.randrange(2 ** 31)


def build_pursue(seed=None):
    seed = _seed_of(seed)
    p = gn.gen_pursue(random.Random(seed))
    data = builders.build_pursue(p)
    data["seed"] = seed
    return data


def build_meet(seed=None):
    seed = _seed_of(seed)
    p = gn.gen_meet(random.Random(seed))
    data = builders.build_meet(p)
    data["seed"] = seed
    return data


def build_circular_same(seed=None):
    seed = _seed_of(seed)
    p = gn.gen_circular_same(random.Random(seed))
    data = builders.build_circular(p, "same")
    data["seed"] = seed
    return data


def build_circular_opp(seed=None):
    seed = _seed_of(seed)
    p = gn.gen_circular_opp(random.Random(seed))
    data = builders.build_circular(p, "opposite")
    data["seed"] = seed
    return data


REGISTRY = {
    "pursue": build_pursue,
    "meet": build_meet,
    "circular-same": build_circular_same,
    "circular-opp": build_circular_opp,
}


def _write(data, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    render_html(data, out)
    print("written:", out, f"(甲 {data['motion']['carA']['v']} m/s, 乙 {data['motion']['carB']['v']} m/s, tMeet={data['answer']['tMeet']} s)")


def main(argv):
    if not argv or argv[0] == "list":
        print("已注册题型:")
        for k in REGISTRY:
            print("  -", k)
        return

    if argv[0] == "all":
        out_dir = Path(argv[1]) if len(argv) > 1 else (SKILL_DIR / "output")
        out_dir.mkdir(parents=True, exist_ok=True)
        for key, fn in REGISTRY.items():
            for _ in range(2):  # 每型 2 个随机变体
                data = fn()
                _write(data, out_dir / f"{key}-{data['seed']}.html")
        return

    key = argv[0]
    if key not in REGISTRY:
        print(f"未知题型 {key}；可用: {', '.join(REGISTRY)}")
        sys.exit(1)

    rest = argv[1:]
    seed, out = None, None
    if rest and rest[0].lstrip("-").isdigit():
        seed = int(rest[0])
        rest = rest[1:]
    if rest:
        out = Path(rest[0])

    data = REGISTRY[key](seed)
    if out is None:
        out = SKILL_DIR / "output" / f"{key}-{data['seed']}.html"
    _write(data, out)


if __name__ == "__main__":
    main(sys.argv[1:])
