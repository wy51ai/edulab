# -*- coding: utf-8 -*-
"""好数生成：答案先行的拒绝采样。

核心思想：先挑「答案 tMeet」和「速度差/速度和」，再反推路程量——
这样答案量（追上/相遇时间、相遇点、圈数）天然是整数，永不需要「算出答案再判规整」。
"""
import random

MAX_ATTEMPTS = 200


class NoGoodNumbers(Exception):
    pass


def _divisors(n, lo, hi):
    """返回 n 在 [lo, hi] 内的所有正因子。"""
    return [d for d in range(lo, hi + 1) if n % d == 0]


def gen_pursue(rng, spec=None):
    """线性同向追及：乙在前 gap 米，甲追乙。tMeet = gap/(vA-vB) 必为整数。"""
    s = spec or {}
    vB_r = s.get("vB", (4, 15))
    dv_r = s.get("dv", (2, 6))
    tm_r = s.get("tMeet", (3, 15))
    gap_r = s.get("gap", (8, 90))
    for _ in range(MAX_ATTEMPTS):
        dv = rng.randint(*dv_r)
        tMeet = rng.randint(*tm_r)
        vB = rng.randint(*vB_r)
        vA = vB + dv
        gap = dv * tMeet
        if not (gap_r[0] <= gap <= gap_r[1]):
            continue
        return {"vA": vA, "vB": vB, "gap": gap, "dv": dv,
                "tMeet": tMeet, "xMeet": vA * tMeet}
    raise NoGoodNumbers("pursue")


def gen_meet(rng, spec=None):
    """线性相向相遇：相距 total 米，相向而行。tMeet = total/(vA+vB) 必为整数。"""
    s = spec or {}
    va_r = s.get("vA", (4, 18))
    vb_r = s.get("vB", (4, 18))
    tm_r = s.get("tMeet", (3, 15))
    total_r = s.get("total", (60, 400))
    for _ in range(MAX_ATTEMPTS):
        tMeet = rng.randint(*tm_r)
        vA = rng.randint(*va_r)
        vB = rng.randint(*vb_r)
        total = (vA + vB) * tMeet
        if not (total_r[0] <= total <= total_r[1]):
            continue
        return {"vA": vA, "vB": vB, "total": total, "tMeet": tMeet,
                "xMeet": vA * tMeet}
    raise NoGoodNumbers("meet")


def gen_circular_same(rng, spec=None):
    """环形同向追及：同点同向出发，甲比乙多跑一圈追上。tMeet = L/(vA-vB)。"""
    s = spec or {}
    Ls = s.get("L", [60, 80, 100, 120, 160, 200, 240])
    dv_r = s.get("dv", (2, 6))
    vb_r = s.get("vB", (2, 8))
    for _ in range(MAX_ATTEMPTS):
        L = rng.choice(Ls)
        dvs = _divisors(L, dv_r[0], dv_r[1])
        if not dvs:
            continue
        dv = rng.choice(dvs)
        tMeet = L // dv
        if not (10 <= tMeet <= 40):  # 保证 tMax=tMeet+5 不跨过第二次追上(2*tMeet)
            continue
        vB = rng.randint(*vb_r)
        vA = vB + dv
        sMeet = (vA * tMeet) % L
        lapsA = (vA * tMeet) // L
        lapsB = (vB * tMeet) // L
        return {"L": L, "vA": vA, "vB": vB, "dv": dv, "tMeet": tMeet,
                "sMeet": sMeet, "lapsA": lapsA, "lapsB": lapsB,
                "lapGain": lapsA - lapsB}
    raise NoGoodNumbers("circular_same")


def gen_circular_opp(rng, spec=None):
    """环形相向相遇：同点相向出发，合跑一圈相遇。tMeet = L/(vA+vB)。"""
    s = spec or {}
    Ls = s.get("L", [60, 80, 100, 120, 160, 200, 240])
    va_r = s.get("vA", (4, 12))
    vb_r = s.get("vB", (4, 12))
    for _ in range(MAX_ATTEMPTS):
        L = rng.choice(Ls)
        vA = rng.randint(*va_r)
        vB = rng.randint(*vb_r)
        sv = vA + vB
        if L % sv != 0:
            continue
        tMeet = L // sv
        if not (3 <= tMeet <= 15):
            continue
        sMeet = (vA * tMeet) % L
        return {"L": L, "vA": vA, "vB": vB, "tMeet": tMeet, "sMeet": sMeet}
    raise NoGoodNumbers("circular_opp")
