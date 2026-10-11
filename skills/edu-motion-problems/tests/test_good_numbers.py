# -*- coding: utf-8 -*-
"""好数生成器单测：1000 次抽样断言答案恒整数、关系恒成立。"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

import good_numbers as gn  # noqa: E402

N = 1000


def test_pursue():
    rng = random.Random(1)
    for _ in range(N):
        p = gn.gen_pursue(rng)
        assert p["dv"] == p["vA"] - p["vB"]
        assert p["gap"] == p["dv"] * p["tMeet"]
        assert p["xMeet"] == p["vA"] * p["tMeet"]
        assert p["gap"] == p["xMeet"] - p["vB"] * p["tMeet"]
        assert isinstance(p["tMeet"], int)


def test_meet():
    rng = random.Random(2)
    for _ in range(N):
        p = gn.gen_meet(rng)
        assert p["total"] == (p["vA"] + p["vB"]) * p["tMeet"]
        assert p["xMeet"] == p["vA"] * p["tMeet"]
        assert p["total"] == p["xMeet"] + p["vB"] * p["tMeet"]
        assert isinstance(p["tMeet"], int)


def test_circular_same():
    rng = random.Random(3)
    for _ in range(N):
        p = gn.gen_circular_same(rng)
        L, dv = p["L"], p["dv"]
        assert L % dv == 0
        assert p["tMeet"] == L // dv
        assert 10 <= p["tMeet"] <= 40
        assert p["sMeet"] == (p["vA"] * p["tMeet"]) % L
        assert p["lapsA"] == (p["vA"] * p["tMeet"]) // L
        assert p["lapsB"] == (p["vB"] * p["tMeet"]) // L
        assert p["lapGain"] == p["lapsA"] - p["lapsB"] == 1


def test_circular_opp():
    rng = random.Random(4)
    for _ in range(N):
        p = gn.gen_circular_opp(rng)
        L, sv = p["L"], p["vA"] + p["vB"]
        assert L % sv == 0
        assert p["tMeet"] == L // sv
        assert 3 <= p["tMeet"] <= 15
        assert p["sMeet"] == (p["vA"] * p["tMeet"]) % L


if __name__ == "__main__":
    test_pursue()
    test_meet()
    test_circular_same()
    test_circular_opp()
    print(f"OK  {N}x4 次抽样全部通过")
