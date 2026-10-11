# -*- coding: utf-8 -*-
"""统计好数生成器单测：1000 次抽样断言数据/总数/答案恒整数、关系恒成立。"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

import generators as gn  # noqa: E402

N = 1000


def test_stat_chart():
    rng = random.Random(1)
    for _ in range(N):
        p = gn.gen_stat_chart(rng)
        assert p["T"] == p["a"] + p["b"] + p["c"] + p["d"]
        for k in ("a", "b", "c", "d", "T", "maxBar"):
            assert isinstance(p[k], int)
        assert p["d"] >= 3 and p["maxBar"] > max(p["a"], p["b"], p["c"], p["d"])
        # 答案量 d 在 [3,10]，反推 T 恒整数
        assert p["d"] <= p["maxBar"]


def test_probability_tree():
    rng = random.Random(2)
    for _ in range(N):
        p = gn.gen_probability_tree(rng)
        m, n = p["m"], p["n"]
        assert m in (2, 3) and n in (2, 3)
        assert p["total"] == m * n
        assert len(p["colorsA"]) == m and len(p["colorsB"]) == n
        assert p["colorsA"][0]["name"] == "红" and p["colorsB"][0]["name"] == "红"
        fav = p["fav"]
        assert isinstance(fav, int) and 2 <= fav <= p["total"]
        # 规则与 fav 恒一致（答案先行反推）
        if p["rule"] == "first":
            assert fav == n
        elif p["rule"] == "atleast":
            assert fav == m + n - 1
        elif p["rule"] == "same":
            assert m == n and fav == m
        elif p["rule"] == "different":
            assert m == n and fav == m * (m - 1)
        else:
            raise AssertionError("未知规则 " + p["rule"])


if __name__ == "__main__":
    test_stat_chart()
    test_probability_tree()
    print(f"OK  2 类 × {N} 次抽样全部通过")
