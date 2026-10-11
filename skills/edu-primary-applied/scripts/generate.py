#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate.py — 把结构化数据注入 template/board.html，产出单页小学应用题交互课件。

数据由 lib/ 的「答案先行好数采样」驱动（单一数据源）：答案量恒为整数，题目、动画、
副图、步骤数值严格一致。零外部依赖（纯标准库 random + math）。

用法（任意 Python3）：
    python3 scripts/generate.py list                 # 列出题型
    python3 scripts/generate.py pursue               # 随机出一题，写技能 output/
    python3 scripts/generate.py pursue 42            # 指定种子（可复现）
    python3 scripts/generate.py sum-diff 7 ./s.html  # 指定输出文件
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
    """注入数据岛 __LESSON_DATA__，写出单文件 HTML。"""
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


def build_pursue(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_pursue(gn.gen_pursue(random.Random(seed))), seed)


def build_meet(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_meet(gn.gen_meet(random.Random(seed))), seed)


def build_circular_same(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_circular(gn.gen_circular_same(random.Random(seed)), "same"), seed)


def build_circular_opp(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_circular(gn.gen_circular_opp(random.Random(seed)), "opposite"), seed)


def build_sum_diff(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_sum_diff(gn.gen_sum_diff(random.Random(seed))), seed)


def build_sum_multiple(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_sum_multiple(gn.gen_sum_multiple(random.Random(seed))), seed)


def build_diff_multiple(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_diff_multiple(gn.gen_diff_multiple(random.Random(seed))), seed)


def build_profit_loss(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_profit_loss(gn.gen_profit_loss(random.Random(seed))), seed)


def build_age(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_age(gn.gen_age(random.Random(seed))), seed)


def build_average(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_average(gn.gen_average(random.Random(seed))), seed)


def build_chicken_rabbit(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_chicken_rabbit(gn.gen_chicken_rabbit(random.Random(seed))), seed)


def build_plant(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_plant(gn.gen_plant(random.Random(seed))), seed)


def build_work(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_work(gn.gen_work(random.Random(seed))), seed)


def build_cycle(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_cycle(gn.gen_cycle(random.Random(seed))), seed)


def build_unit(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_unit(gn.gen_unit(random.Random(seed))), seed)


def build_aggregate(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_aggregate(gn.gen_aggregate(random.Random(seed))), seed)


def build_boat(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_boat(gn.gen_boat(random.Random(seed))), seed)


def build_train(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_train(gn.gen_train(random.Random(seed))), seed)


def build_avgspeed(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_avgspeed(gn.gen_avgspeed(random.Random(seed))), seed)


# ---- A 组：分数 / 百分数 / 比与比例 / 浓度 / 行程扩展 / 还原 / 平均数变体 / 间隔变体 ----

def build_fraction_part(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_fraction_part(gn.gen_fraction_part(random.Random(seed))), seed)


def build_fraction_whole(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_fraction_whole(gn.gen_fraction_whole(random.Random(seed))), seed)


def build_fraction_ratio(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_fraction_ratio(gn.gen_fraction_ratio(random.Random(seed))), seed)


def build_discount(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_discount(gn.gen_discount(random.Random(seed))), seed)


def build_percent_change(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_percent_change(gn.gen_percent_change(random.Random(seed))), seed)


def build_ratio_share(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_ratio_share(gn.gen_ratio_share(random.Random(seed))), seed)


def build_ratio_scale(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_ratio_scale(gn.gen_ratio_scale(random.Random(seed))), seed)


def build_concentration(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_concentration(gn.gen_concentration(random.Random(seed))), seed)


def build_midpoint_meet(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_midpoint_meet(gn.gen_midpoint_meet(random.Random(seed))), seed)


def build_restore(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_restore(gn.gen_restore(random.Random(seed))), seed)


def build_average_move(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_average_move(gn.gen_average_move(random.Random(seed))), seed)


def build_stairs(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_stairs(gn.gen_stairs(random.Random(seed))), seed)


def build_cows(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_cows(gn.gen_cows(random.Random(seed))), seed)


def build_phalanx(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_phalanx(gn.gen_phalanx(random.Random(seed))), seed)


def build_pigeonhole(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_pigeonhole(gn.gen_pigeonhole(random.Random(seed))), seed)


def build_clock(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_clock(gn.gen_clock(random.Random(seed))), seed)


def build_elimination(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_elimination(gn.gen_elimination(random.Random(seed))), seed)


def build_arithmetic_seq(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_arithmetic_seq(gn.gen_arithmetic_seq(random.Random(seed))), seed)


def build_optimize(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_optimize(gn.gen_optimize(random.Random(seed))), seed)


def build_page_digit(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_page_digit(gn.gen_page_digit(random.Random(seed))), seed)


def build_sum_diff_three(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_sum_diff_three(gn.gen_sum_diff_three(random.Random(seed))), seed)


def build_profit_loss_two_gain(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_profit_loss_two_gain(gn.gen_profit_loss_two_gain(random.Random(seed))), seed)


def build_profit_loss_two_loss(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_profit_loss_two_loss(gn.gen_profit_loss_two_loss(random.Random(seed))), seed)


def build_plant_one(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_plant_one(gn.gen_plant_one(random.Random(seed))), seed)


def build_plant_none(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_plant_none(gn.gen_plant_none(random.Random(seed))), seed)


def build_plant_ring(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_plant_ring(gn.gen_plant_ring(random.Random(seed))), seed)


def build_overlap_venn(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_overlap_venn(gn.gen_overlap_venn(random.Random(seed))), seed)


def build_match_count(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_match_count(gn.gen_match_count(random.Random(seed))), seed)


def build_logic_table(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_logic_table(gn.gen_logic_table(random.Random(seed))), seed)


def build_pancake(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_pancake(gn.gen_pancake(random.Random(seed))), seed)


def build_tianji(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_tianji(gn.gen_tianji(random.Random(seed))), seed)


def build_fraction_more_less(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_fraction_more_less(gn.gen_fraction_more_less(random.Random(seed))), seed)


def build_interest(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_interest(gn.gen_interest(random.Random(seed))), seed)


def build_plant_two_sides(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_plant_two_sides(gn.gen_plant_two_sides(random.Random(seed))), seed)


def build_equation_balance(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_equation_balance(gn.gen_equation_balance(random.Random(seed))), seed)


def build_triangle_equal(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_triangle_equal(gn.gen_triangle_equal(random.Random(seed))), seed)


def build_para_equal(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_para_equal(gn.gen_para_equal(random.Random(seed))), seed)


def build_tri_height(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_tri_height(gn.gen_tri_height(random.Random(seed))), seed)


def build_trapezoid(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_trapezoid(gn.gen_trapezoid(random.Random(seed))), seed)


def build_recompose(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_recompose(gn.gen_recompose(random.Random(seed))), seed)


def build_circle(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_circle(gn.gen_circle(random.Random(seed))), seed)


def build_circle_area(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_circle_area(gn.gen_circle_area(random.Random(seed))), seed)


def build_semicircle(seed=None):
    seed = _seed_of(seed)
    return _finish(builders.build_semicircle(gn.gen_semicircle(random.Random(seed))), seed)


REGISTRY = {
    "pursue": build_pursue,
    "meet": build_meet,
    "circular-same": build_circular_same,
    "circular-opp": build_circular_opp,
    "sum-diff": build_sum_diff,
    "sum-multiple": build_sum_multiple,
    "diff-multiple": build_diff_multiple,
    "profit-loss": build_profit_loss,
    "age": build_age,
    "average": build_average,
    "chicken-rabbit": build_chicken_rabbit,
    "plant": build_plant,
    "work": build_work,
    "cycle": build_cycle,
    "unit": build_unit,
    "aggregate": build_aggregate,
    "boat": build_boat,
    "train": build_train,
    "avgspeed": build_avgspeed,
    "fraction-part": build_fraction_part,
    "fraction-whole": build_fraction_whole,
    "fraction-ratio": build_fraction_ratio,
    "discount": build_discount,
    "percent-change": build_percent_change,
    "ratio-share": build_ratio_share,
    "ratio-scale": build_ratio_scale,
    "concentration": build_concentration,
    "midpoint-meet": build_midpoint_meet,
    "restore": build_restore,
    "average-move": build_average_move,
    "stairs": build_stairs,
    "cows": build_cows,
    "phalanx": build_phalanx,
    "pigeonhole": build_pigeonhole,
    "clock": build_clock,
    "elimination": build_elimination,
    "arithmetic-seq": build_arithmetic_seq,
    "optimize": build_optimize,
    "page-digit": build_page_digit,
    "sum-diff-three": build_sum_diff_three,
    "profit-loss-two-gain": build_profit_loss_two_gain,
    "profit-loss-two-loss": build_profit_loss_two_loss,
    "plant-one": build_plant_one,
    "plant-none": build_plant_none,
    "plant-ring": build_plant_ring,
    "overlap-venn": build_overlap_venn,
    "match-count": build_match_count,
    "logic-table": build_logic_table,
    "pancake": build_pancake,
    "tianji": build_tianji,
    "fraction-more-less": build_fraction_more_less,
    "interest": build_interest,
    "plant-two-sides": build_plant_two_sides,
    "equation-balance": build_equation_balance,
    "triangle-equal": build_triangle_equal,
    "para-equal": build_para_equal,
    "tri-height": build_tri_height,
    "trapezoid": build_trapezoid,
    "recompose": build_recompose,
    "circle": build_circle,
    "circle-area": build_circle_area,
    "semicircle": build_semicircle,
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
