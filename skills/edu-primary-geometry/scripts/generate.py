#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate.py — 把结构化数据注入 template/board.html，产出单页小学几何交互课件。

数据由 lib/ 的「答案先行好数采样」驱动（单一数据源）：底/高/面积/体积恒为整数，
题目、动画、步骤数值严格一致。零外部依赖（纯标准库 random + math）。

用法（任意 Python3）：
    python3 scripts/generate.py list                 # 列出题型
    python3 scripts/generate.py area-parallelogram   # 随机出一题，写技能 output/
    python3 scripts/generate.py area-parallelogram 42   # 指定种子（可复现）
    python3 scripts/generate.py area-parallelogram 7 ./s.html  # 指定输出文件
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
import generators as gn  # noqa: E402
import builders          # noqa: E402


def render_html(data: dict, out_path: Path) -> Path:
    template = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise RuntimeError(f"模板中未找到占位符 {PLACEHOLDER}")
    out_path.write_text(template.replace(PLACEHOLDER, json.dumps(data, ensure_ascii=False)),
                        encoding="utf-8")
    return out_path


def _seed_of(seed):
    return seed if seed is not None else random.randrange(2 ** 31)


def _finish(data, seed):
    data["seed"] = seed
    return data


def build_area_parallelogram(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_area_parallelogram(gn.gen_area_parallelogram(random.Random(seed))), seed)


def build_area_triangle(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_area_triangle(gn.gen_area_triangle(random.Random(seed))), seed)


def build_area_trapezoid(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_area_trapezoid(gn.gen_area_trapezoid(random.Random(seed))), seed)


def build_area_circle(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_area_circle(gn.gen_area_circle(random.Random(seed))), seed)


def build_composite_area(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_composite_area(gn.gen_composite_area(random.Random(seed))), seed)


def build_grid_count(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_grid_count(gn.gen_grid_count(random.Random(seed))), seed)


def build_three_view(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_three_view(gn.gen_three_view(random.Random(seed))), seed)


def build_transform_symmetry(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_transform_symmetry(gn.gen_transform_symmetry(random.Random(seed))), seed)


def build_cuboid_volume(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_cuboid_volume(gn.gen_cuboid_volume(random.Random(seed))), seed)


REGISTRY = {
    "area-parallelogram": build_area_parallelogram,
    "area-triangle": build_area_triangle,
    "area-trapezoid": build_area_trapezoid,
    "area-circle": build_area_circle,
    "composite-area": build_composite_area,
    "grid-count": build_grid_count,
    "three-view": build_three_view,
    "transform-symmetry": build_transform_symmetry,
    "cuboid-volume": build_cuboid_volume,
}


def _write(data, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    render_html(data, out)
    print("written:", out, "| type:", data["type"], "| answer:", data["answer"])


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
            for _ in range(2):
                data = fn()
                _write(data, out_dir / f"{key}-{data['seed']}.html")
        return

    key = argv[0]
    if key not in REGISTRY:
        print(f"未知题型 '{key}'。可用题型：", ", ".join(REGISTRY))
        return

    seed = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else None
    data = REGISTRY[key](seed)

    if len(argv) > 2:
        out = Path(argv[2])
    else:
        out = SKILL_DIR / "output" / f"{key}-{data['seed']}.html"
    _write(data, out)


if __name__ == "__main__":
    main(sys.argv[1:])
