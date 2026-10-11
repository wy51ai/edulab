# -*- coding: utf-8 -*-
"""好数生成：答案先行的拒绝采样（全题型）。

核心思想：先挑「答案量」和「关系量」，再反推已知量——答案量天然整数，永不「算出答案再判规整」。

行程问题：tMeet = gap/(vA−vB) 或 total/(vA+vB) 或 L/(vA∓vB)
线段图（和差/和倍/差倍/盈亏/年龄/平均数/归一/归总/流水行船/平均速度）：先挑答案量，反推关系量
其它（鸡兔同笼/植树/工程/周期/火车过桥）：先挑答案量，反推总量/时间
"""
import math
import random

MAX_ATTEMPTS = 200


class NoGoodNumbers(Exception):
    pass


def _divisors(n, lo, hi):
    """返回 n 在 [lo, hi] 内的所有正因子。"""
    return [d for d in range(lo, hi + 1) if n % d == 0]


# ---------------------------------------------------------------------------
# R1 行程问题（迁移）
# ---------------------------------------------------------------------------

def gen_pursue(rng, spec=None):
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
        if not (10 <= tMeet <= 40):
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


# ---------------------------------------------------------------------------
# R1 线段图（和差/和倍/差倍）
# ---------------------------------------------------------------------------

def gen_sum_diff(rng, spec=None):
    s = spec or {}
    a_r = s.get("a", (4, 30))
    d_r = s.get("D", (2, 20))
    for _ in range(MAX_ATTEMPTS):
        a = rng.randint(*a_r)
        D = rng.randint(*d_r)
        b = a + D
        if b > 60:
            continue
        return {"a": a, "b": b, "S": a + b, "D": D}
    raise NoGoodNumbers("sum_diff")


def gen_sum_multiple(rng, spec=None):
    s = spec or {}
    a_r = s.get("a", (3, 18))
    n_r = s.get("n", (2, 8))
    for _ in range(MAX_ATTEMPTS):
        a = rng.randint(*a_r)
        n = rng.randint(*n_r)
        b = n * a
        if b > 80:
            continue
        return {"a": a, "b": b, "n": n, "S": a + b}
    raise NoGoodNumbers("sum_multiple")


def gen_diff_multiple(rng, spec=None):
    s = spec or {}
    a_r = s.get("a", (3, 20))
    n_r = s.get("n", (2, 6))
    for _ in range(MAX_ATTEMPTS):
        a = rng.randint(*a_r)
        n = rng.randint(*n_r)
        b = n * a
        if b > 90:
            continue
        return {"a": a, "b": b, "n": n, "D": b - a}
    raise NoGoodNumbers("diff_multiple")


# ---------------------------------------------------------------------------
# R2 线段图：盈亏 / 年龄 / 平均数
# ---------------------------------------------------------------------------

def gen_profit_loss(rng, spec=None):
    """盈亏(一盈一亏)：每人 a 颗多 b 颗；每人 c 颗少 d 颗。人数 n=(b+d)/(c-a)，总数 total=a·n+b。"""
    s = spec or {}
    n_r = s.get("n", (3, 15))
    a_r = s.get("a", (2, 8))
    dd_r = s.get("dd", (2, 5))   # dd = c - a（两次分配差）
    for _ in range(MAX_ATTEMPTS):
        n = rng.randint(*n_r)
        a = rng.randint(*a_r)
        dd = rng.randint(*dd_r)
        c = a + dd
        spread = n * dd
        if spread < 3:
            continue
        # 约束「亏」d < c，使蓝条 second = c·t − d 在 t≥1 全程恒正（避免验证采样点出现负宽条）
        b = rng.randint(max(1, spread - c + 1), spread - 1)   # 盈
        d = spread - b                                        # 亏（1 ≤ d ≤ c-1）
        total = a * n + b
        return {"n": n, "a": a, "c": c, "b": b, "d": d, "total": total}
    raise NoGoodNumbers("profit_loss")


def gen_age(rng, spec=None):
    """年龄：爸爸 P 岁，儿子 Q 岁，几年后 t 爸爸年龄是儿子 n 倍。P = nQ + (n-1)t。"""
    s = spec or {}
    q_r = s.get("Q", (5, 12))
    n_r = s.get("n", (2, 4))
    t_r = s.get("t", (2, 10))
    for _ in range(MAX_ATTEMPTS):
        Q = rng.randint(*q_r)
        n = rng.randint(*n_r)
        t = rng.randint(*t_r)
        P = n * Q + (n - 1) * t
        if P > 60 or P <= Q:
            continue
        return {"P": P, "Q": Q, "n": n, "t": t}
    raise NoGoodNumbers("age")


def gen_average(rng, spec=None):
    """平均数：甲 x、乙 y、丙 z，平均数 A=(x+y+z)/3 整数。求丙 z（最大）。"""
    s = spec or {}
    x_r = s.get("x", (4, 20))
    y_r = s.get("y", (8, 28))
    z_r = s.get("z", (12, 40))
    for _ in range(MAX_ATTEMPTS):
        x = rng.randint(*x_r)
        y = rng.randint(*y_r)
        z = rng.randint(*z_r)
        if not (x < y < z):
            continue
        if (x + y + z) % 3 != 0:
            continue
        A = (x + y + z) // 3
        return {"x": x, "y": y, "z": z, "A": A}
    raise NoGoodNumbers("average")


# ---------------------------------------------------------------------------
# R2 其它：鸡兔同笼 / 植树
# ---------------------------------------------------------------------------

def gen_chicken_rabbit(rng, spec=None):
    """鸡兔同笼：鸡 c、兔 r，头 H=c+r，腿 L=2c+4r。"""
    s = spec or {}
    c_r = s.get("c", (3, 12))
    r_r = s.get("r", (2, 10))
    for _ in range(MAX_ATTEMPTS):
        c = rng.randint(*c_r)
        r = rng.randint(*r_r)
        return {"c": c, "r": r, "H": c + r, "L": 2 * c + 4 * r}
    raise NoGoodNumbers("chicken_rabbit")


def gen_plant(rng, spec=None):
    """植树(两端都栽)：间隔数 n，间隔 d 米，路长 D=n·d，棵树 k=n+1。"""
    s = spec or {}
    n_r = s.get("n", (4, 12))
    d_r = s.get("d", (2, 5))
    for _ in range(MAX_ATTEMPTS):
        n = rng.randint(*n_r)
        d = rng.randint(*d_r)
        D = n * d
        k = n + 1
        return {"n": n, "d": d, "D": D, "k": k}
    raise NoGoodNumbers("plant")


# ---------------------------------------------------------------------------
# R3 工程 / 周期 / 归一 / 归总
# ---------------------------------------------------------------------------

def gen_work(rng, spec=None):
    """工程：甲 a 天，乙 b 天，合做 t=ab/(a+b) 天。构造 t, x|t², a=t+x, b=t+t²/x。"""
    s = spec or {}
    t_r = s.get("t", (2, 10))
    for _ in range(MAX_ATTEMPTS):
        t = rng.randint(*t_r)
        xs = _divisors(t * t, 1, t * t - 1)
        if not xs:
            continue
        x = rng.choice(xs)
        a = t + x
        b = t + t * t // x
        if a > 40 or b > 40 or a == b:
            continue
        return {"t": t, "a": a, "b": b}
    raise NoGoodNumbers("work")


def gen_cycle(rng, spec=None):
    """周期：周期长度 p（颜色数），第 N 个，余数 r（1-based 位置在周期内）。"""
    s = spec or {}
    p_r = s.get("p", (3, 5))
    N_r = s.get("N", (12, 40))
    for _ in range(MAX_ATTEMPTS):
        p = rng.randint(*p_r)
        N = rng.randint(*N_r)
        r = ((N - 1) % p) + 1
        return {"p": p, "N": N, "r": r}
    raise NoGoodNumbers("cycle")


def gen_unit(rng, spec=None):
    """归一：m 件 w 元，求 n 件。单价 u=w/m，n 件 = n·u。"""
    s = spec or {}
    u_r = s.get("u", (2, 8))
    m_r = s.get("m", (3, 6))
    n_r = s.get("n", (4, 9))
    for _ in range(MAX_ATTEMPTS):
        u = rng.randint(*u_r)
        m = rng.randint(*m_r)
        n = rng.randint(*n_r)
        if n == m:
            continue
        w = m * u
        return {"u": u, "m": m, "n": n, "w": w, "ans": n * u}
    raise NoGoodNumbers("unit")


def gen_aggregate(rng, spec=None):
    """归总：每盒 a 个装 m 盒，共 w=a·m；若每盒 b 个，装 n=w/b 盒。"""
    s = spec or {}
    a_r = s.get("a", (3, 8))
    m_r = s.get("m", (4, 10))
    for _ in range(MAX_ATTEMPTS):
        a = rng.randint(*a_r)
        m = rng.randint(*m_r)
        w = a * m
        bs = [b for b in _divisors(w, 2, w - 1) if b != a]
        if not bs:
            continue
        b = rng.choice(bs)
        n = w // b
        return {"a": a, "m": m, "w": w, "b": b, "n": n}
    raise NoGoodNumbers("aggregate")


# ---------------------------------------------------------------------------
# R3 行程扩展：流水行船 / 火车过桥 / 平均速度
# ---------------------------------------------------------------------------

def gen_boat(rng, spec=None):
    """流水行船：顺水 p 千米/时，逆水 q 千米/时；两港相距 s=p·q，顺水 q 时、逆水 p 时。
    水流 u=(p-q)/2，静水 v=(p+q)/2。"""
    s = spec or {}
    ps = s.get("speeds", [4, 6, 8, 10, 12])
    for _ in range(MAX_ATTEMPTS):
        p = rng.choice(ps)
        qs = [x for x in ps if x < p]
        if not qs:
            continue
        q = rng.choice(qs)
        return {"s": p * q, "t1": q, "t2": p, "u": (p - q) // 2,
                "v": (p + q) // 2, "down": p, "up": q}
    raise NoGoodNumbers("boat")


def gen_train(rng, spec=None):
    """火车过桥：车长 L，桥长 B，速度 v，时间 t=(L+B)/v。"""
    s = spec or {}
    L_r = s.get("L", (40, 150))
    B_r = s.get("B", (100, 300))
    v_r = s.get("v", (5, 15))
    for _ in range(MAX_ATTEMPTS):
        L = rng.randint(*L_r)
        B = rng.randint(*B_r)
        v = rng.randint(*v_r)
        total = L + B
        if total % v != 0:
            continue
        t = total // v
        if not (8 <= t <= 40):
            continue
        return {"L": L, "B": B, "v": v, "t": t}
    raise NoGoodNumbers("train")


def gen_avgspeed(rng, spec=None):
    """平均速度：去 v1，回 v2（均偶数），平均 2·v1·v2/(v1+v2) 整数。"""
    s = spec or {}
    vs = s.get("vs", [4, 6, 8, 10, 12, 16, 20])
    for _ in range(MAX_ATTEMPTS):
        v1 = rng.choice(vs)
        v2 = rng.choice([x for x in vs if x != v1])
        if (2 * v1 * v2) % (v1 + v2) != 0:
            continue
        avg = (2 * v1 * v2) // (v1 + v2)
        return {"v1": v1, "v2": v2, "avg": avg, "arith": (v1 + v2) // 2}
    raise NoGoodNumbers("avgspeed")


# ---------------------------------------------------------------------------
# A 组：分数 / 百分数 / 比与比例 / 浓度 / 行程扩展 / 还原 / 平均数变体 / 间隔变体
# ---------------------------------------------------------------------------

def gen_fraction_part(rng, spec=None):
    """求一个数的几分之几：整体 W=d·k，分率 n/d（最简），部分 part=n·k。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        d = rng.randint(*s.get("d", (2, 8)))
        n = rng.randint(1, d - 1)
        if math.gcd(n, d) != 1:
            continue
        k = rng.randint(*s.get("k", (3, 12)))
        return {"d": d, "n": n, "k": k, "W": d * k, "part": n * k}
    raise NoGoodNumbers("fraction_part")


def gen_fraction_whole(rng, spec=None):
    """已知部分求整体（单位1）：部分 part=n·k，分率 n/d（最简），整体 W=d·k。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        d = rng.randint(*s.get("d", (2, 8)))
        n = rng.randint(1, d - 1)
        if math.gcd(n, d) != 1:
            continue
        k = rng.randint(*s.get("k", (3, 12)))
        return {"d": d, "n": n, "k": k, "W": d * k, "part": n * k}
    raise NoGoodNumbers("fraction_whole")


def gen_fraction_ratio(rng, spec=None):
    """求甲是乙的几分之几：甲=n·k、乙=d·k（gcd(n,d)=1），答案 n/d（滑块=分子 n）。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        d = rng.randint(*s.get("d", (3, 8)))
        n = rng.randint(1, d - 1)
        if math.gcd(n, d) != 1:
            continue
        k = rng.randint(*s.get("k", (2, 9)))
        return {"d": d, "n": n, "k": k, "A": n * k, "B": d * k}
    raise NoGoodNumbers("fraction_ratio")


def gen_discount(rng, spec=None):
    """折扣：原价 A（10 的倍数）、打 d 折 → 现价 = A·d/10。"""
    s = spec or {}
    A = 10 * rng.randint(*s.get("m", (3, 20)))
    d = rng.randint(*s.get("d", (2, 9)))
    return {"A": A, "d": d, "price": A * d // 10}


def gen_percent_change(rng, spec=None):
    """增减百分之几：原价 A（100 的倍数）、涨 x% → 现价 = A·(100+x)/100。"""
    s = spec or {}
    A = 100 * rng.randint(*s.get("m", (1, 5)))
    x = rng.randint(*s.get("x", (5, 40)))
    return {"A": A, "x": x, "price": A * (100 + x) // 100}


def gen_ratio_share(rng, spec=None):
    """按比例分配：比 a:b（最简）、每份 k → 甲=a·k、乙=b·k、总=(a+b)k。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        a = rng.randint(*s.get("a", (2, 5)))
        b = a + rng.randint(*s.get("db", (1, 4)))
        if math.gcd(a, b) != 1:
            continue
        k = rng.randint(*s.get("k", (3, 10)))
        return {"a": a, "b": b, "k": k, "A": a * k, "B": b * k, "total": (a + b) * k}
    raise NoGoodNumbers("ratio_share")


def gen_ratio_scale(rng, spec=None):
    """比例（模型比例 1:n）：模型长 d 厘米 → 实物 = n·d 厘米。"""
    s = spec or {}
    n = rng.randint(*s.get("n", (4, 12)))
    d = rng.randint(*s.get("d", (3, 15)))
    return {"n": n, "d": d, "real": n * d}


def gen_concentration(rng, spec=None):
    """盐水求溶质：溶液 g（100 的倍数）、浓度 c% → 盐 = g·c/100。"""
    s = spec or {}
    g = 100 * rng.randint(*s.get("m", (1, 4)))
    c = rng.randint(*s.get("c", (5, 35)))
    return {"g": g, "c": c, "salt": g * c // 100}


def gen_midpoint_meet(rng, spec=None):
    """中点相遇：vA>vB、时间 t，距中点 m=(vA−vB)·t/2，全程 T=(vA+vB)·t。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        vA = rng.randint(*s.get("vA", (5, 12)))
        vB = rng.randint(*s.get("vB", (3, 11)))
        if vB >= vA:
            continue
        t = rng.randint(*s.get("t", (2, 10)))
        if (vA - vB) * t % 2 != 0:
            continue
        m = (vA - vB) * t // 2
        if m < 1:
            continue
        return {"vA": vA, "vB": vB, "t": t, "m": m, "T": (vA + vB) * t}
    raise NoGoodNumbers("midpoint_meet")


def gen_restore(rng, spec=None):
    """还原（逆推）：原来 W，第一次吃 W/a 又 b，第二次吃剩余/c 又 d，剩 r。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        a = rng.randint(*s.get("a", (2, 3)))
        b = rng.randint(*s.get("b", (1, 2)))
        c = rng.randint(*s.get("c", (2, 3)))
        d = rng.randint(*s.get("d", (1, 2)))
        W = rng.randint(*s.get("W", (20, 120)))
        if W % a != 0:
            continue
        X = W - (W // a + b)          # 第一次后剩余
        if X <= 0 or X % c != 0:
            continue
        r = X - (X // c + d)          # 最后剩余
        if r <= 0:
            continue
        return {"a": a, "b": b, "c": c, "d": d, "W": W, "X": X, "r": r}
    raise NoGoodNumbers("restore")


def gen_average_move(rng, spec=None):
    """移多补少：甲 a、乙 b（a>b 且 a−b 偶），甲给乙 (a−b)/2 后一样多。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        a = rng.randint(*s.get("a", (10, 40)))
        b = rng.randint(2, a - 2)
        if (a - b) % 2 != 0:
            continue
        return {"a": a, "b": b, "give": (a - b) // 2}
    raise NoGoodNumbers("average_move")


def gen_stairs(rng, spec=None):
    """间隔变体（爬楼/锯木/敲钟）：n 个点、间隔 n−1、每段 t，总=(n−1)·t。"""
    s = spec or {}
    scenario = rng.choice(s.get("scenarios", ["楼", "段", "下"]))
    n = rng.randint(*s.get("n", (4, 10)))
    t = rng.randint(*s.get("t", (2, 6)))
    return {"scenario": scenario, "n": n, "t": t, "total": (n - 1) * t}


# ---------------------------------------------------------------------------
# B 组：牛吃草 / 方阵 / 抽屉 / 时钟 / 消去法 / 等差数列 / 最优化 / 页码 / 三数和差倍
# ---------------------------------------------------------------------------

def gen_cows(rng, spec=None):
    """牛吃草：草原有 G=(N−g)·t，每天长 g，N 头牛（每头每天吃 1 份），可吃 t 天。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        g = rng.randint(*s.get("g", (2, 6)))        # 每天生长 g 份
        N = rng.randint(*s.get("N", (8, 20)))       # 牛数
        if N <= g:
            continue
        t = rng.randint(*s.get("t", (3, 12)))       # 可吃天数（答案）
        G = (N - g) * t                              # 原有草量
        return {"g": g, "N": N, "t": t, "G": G}
    raise NoGoodNumbers("cows")


def gen_phalanx(rng, spec=None):
    """方阵：每边 n 人 → 总数 n²、最外层 4n−4。"""
    s = spec or {}
    n = rng.randint(*s.get("n", (4, 12)))
    return {"n": n, "total": n * n, "outer": 4 * n - 4}


def gen_pigeonhole(rng, spec=None):
    """抽屉原理：苹果 m=n·k+r（0<r<n）→ 至少一个抽屉 ≥ k+1。"""
    s = spec or {}
    n = rng.randint(*s.get("n", (3, 8)))            # 抽屉数
    k = rng.randint(*s.get("k", (1, 4)))             # 每抽屉平均
    r = rng.randint(1, n - 1)                        # 余数 0<r<n
    m = n * k + r                                    # 苹果数
    return {"n": n, "k": k, "r": r, "m": m, "least": k + 1}


def gen_clock(rng, spec=None):
    """时钟整点夹角（整数化）：h 点整，时针分针夹角 = 30·h（h∈1..6）。"""
    s = spec or {}
    h = rng.randint(*s.get("h", (1, 6)))
    return {"h": h, "angle": 30 * h}


def gen_elimination(rng, spec=None):
    """消去法：甲+乙=S1、乙+丙=S2、甲+丙=S3，求甲=(S1+S3−S2)/2。"""
    s = spec or {}
    x = rng.randint(*s.get("x", (4, 20)))            # 甲
    y = rng.randint(*s.get("y", (4, 20)))            # 乙
    z = rng.randint(*s.get("z", (4, 20)))            # 丙
    if x == y == z:
        x += 1
    return {"x": x, "y": y, "z": z,
            "S1": x + y, "S2": y + z, "S3": x + z}


def gen_arithmetic_seq(rng, spec=None):
    """等差数列：首项 a、公差 d，第 n 项 = a+(n−1)d。"""
    s = spec or {}
    a = rng.randint(*s.get("a", (2, 8)))             # 首项
    d = rng.randint(*s.get("d", (2, 5)))             # 公差
    n = rng.randint(*s.get("n", (5, 10)))            # 项数
    return {"a": a, "d": d, "n": n, "an": a + (n - 1) * d}


def gen_optimize(rng, spec=None):
    """租船最省钱：大船 a 人/p 元、小船 b 人/q 元、共 N 人，求总价最小的唯一大船数。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        a = rng.randint(*s.get("a", (4, 8)))         # 大船载客
        b = rng.randint(*s.get("b", (2, 4)))         # 小船载客
        p = rng.randint(*s.get("p", (8, 16)))        # 大船价
        q = rng.randint(*s.get("q", (5, 10)))        # 小船价
        if p * b >= q * a:                            # 大船人均要更便宜
            continue
        N = rng.randint(*s.get("N", (20, 60)))       # 总人数
        best, bestk = None, []
        for k in range(0, N // a + 2):
            rest = max(0, N - k * a)
            small = -(-rest // b)                     # ceil
            cost = k * p + small * q
            if best is None or cost < best:
                best, bestk = cost, [k]
            elif cost == best:
                bestk.append(k)
        if len(bestk) != 1:                           # 保证最小值唯一
            continue
        if bestk[0] < 2:                              # 大船数 ≥2，便于滑块采样两色块
            continue
        return {"a": a, "b": b, "p": p, "q": q, "N": N,
                "optK": bestk[0], "minCost": best}
    raise NoGoodNumbers("optimize")


def gen_page_digit(rng, spec=None):
    """页码数字个数：n 页（10≤n≤99），共 9 + 2·(n−9) 个数字。"""
    s = spec or {}
    n = rng.randint(*s.get("n", (12, 60)))
    total = 9 + 2 * (n - 9)
    return {"n": n, "total": total, "one": 9, "two": n - 9}


def gen_sum_diff_three(rng, spec=None):
    """三数和差倍：甲比乙多 D、丙是甲的 n 倍、总和 S，求甲（答案）。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        a = rng.randint(*s.get("a", (6, 15)))        # 甲
        D = rng.randint(*s.get("D", (2, 5)))         # 甲−乙
        if a - D < 1:
            continue
        n = rng.randint(*s.get("n", (2, 4)))         # 丙 = 甲·n
        b = a - D
        c = a * n
        return {"a": a, "b": b, "c": c, "D": D, "n": n, "S": a + b + c}
    raise NoGoodNumbers("sum_diff_three")


# ---------------------------------------------------------------------------
# C 组：盈亏两盈/两亏 + 植树一端/两端不栽/环形
# ---------------------------------------------------------------------------

def gen_profit_loss_two_gain(rng, spec=None):
    """两盈：每人 a 余 b、每人 c 余 d（c>a，b>d）→ 人数 n=(b−d)/(c−a)。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        n = rng.randint(*s.get("n", (4, 12)))
        a = rng.randint(*s.get("a", (2, 6)))
        c = rng.randint(*s.get("c", (3, 8)))
        if c <= a:
            continue
        d = rng.randint(*s.get("d", (1, 6)))       # 第二种分法剩余
        b = d + n * (c - a)                          # 第一种分法剩余（更多）
        total = n * a + b
        return {"n": n, "a": a, "b": b, "c": c, "d": d, "total": total}
    raise NoGoodNumbers("profit_loss_two_gain")


def gen_profit_loss_two_loss(rng, spec=None):
    """两亏：每人 a 缺 b、每人 c 缺 d（c>a，d>b）→ 人数 n=(d−b)/(c−a)。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        n = rng.randint(*s.get("n", (4, 12)))
        a = rng.randint(*s.get("a", (2, 6)))
        c = rng.randint(*s.get("c", (3, 8)))
        if c <= a:
            continue
        b = rng.randint(*s.get("b", (1, 5)))       # 第一种分法缺口
        d = b + n * (c - a)                          # 第二种分法缺口（更大）
        total = n * a - b
        return {"n": n, "a": a, "b": b, "c": c, "d": d, "total": total}
    raise NoGoodNumbers("profit_loss_two_loss")


def gen_plant_one(rng, spec=None):
    """植树(一端栽)：间隔数 n，间隔 d 米，路长 D=n·d，棵树 k=n。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        n = rng.randint(*s.get("n", (4, 12)))
        d = rng.randint(*s.get("d", (2, 5)))
        D = n * d
        return {"n": n, "d": d, "D": D, "k": n}
    raise NoGoodNumbers("plant_one")


def gen_plant_none(rng, spec=None):
    """植树(两端不栽)：间隔数 n，间隔 d 米，路长 D=n·d，棵树 k=n−1。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        n = rng.randint(*s.get("n", (4, 12)))
        d = rng.randint(*s.get("d", (2, 5)))
        D = n * d
        return {"n": n, "d": d, "D": D, "k": n - 1}
    raise NoGoodNumbers("plant_none")


def gen_plant_ring(rng, spec=None):
    """植树(环形)：间隔数 n，间隔 d 米，周长 D=n·d，棵树 k=n。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        n = rng.randint(*s.get("n", (4, 12)))
        d = rng.randint(*s.get("d", (2, 5)))
        D = n * d
        return {"n": n, "d": d, "D": D, "k": n}
    raise NoGoodNumbers("plant_ring")


# ---------------------------------------------------------------------------
# 板块 C+D：容斥/排列组合/逻辑推理/烙饼/田忌/分数差率/利率/植树两侧/天平
# ---------------------------------------------------------------------------

def gen_overlap_venn(rng, spec=None):
    """容斥(韦恩图)：先挑 只语文 a、只数学 b、两科都优 c，反推 语文优 X=a+c、数学优 Y=b+c、至少一科 T=a+b+c。"""
    s = spec or {}
    a = rng.randint(*s.get("a", (3, 10)))   # 只语文
    b = rng.randint(*s.get("b", (3, 10)))   # 只数学
    c = rng.randint(*s.get("c", (2, 8)))    # 两科都优（答案量）
    return {"a": a, "b": b, "c": c, "X": a + c, "Y": b + c, "T": a + b + c}


def gen_match_count(rng, spec=None):
    """搭配/排列组合：上衣 m 件、裤子 n 条 → 搭配总数 = m·n（连线图逐一枚举）。"""
    s = spec or {}
    m = rng.randint(*s.get("m", (2, 4)))   # 上衣件数
    n = rng.randint(*s.get("n", (2, 5)))   # 裤子条数
    return {"m": m, "n": n, "total": m * n}


def gen_logic_table(rng, spec=None):
    """逻辑推理(排除法)：3 人 × 3 运动，唯一确定排列；甲=排除法、乙=肯定、丙=剩下。"""
    s = spec or {}
    people = ["甲", "乙", "丙"]
    sports = ["跑步", "游泳", "跳高"]
    perm = [0, 1, 2]
    rng.shuffle(perm)                      # perm[i] = 第 i 人的运动下标
    # 条件 1：甲既不是 A 也不是 B（A、B = 甲之外的两个运动）→ 甲唯一确定
    others = [x for x in range(3) if x != perm[0]]
    cond1 = f"甲既不是{sports[others[0]]}，也不是{sports[others[1]]}"
    cond2 = f"乙是{sports[perm[1]]}"
    cond3 = f"丙是{sports[perm[2]]}"
    return {"people": people, "sports": sports, "perm": perm,
            "cond1": cond1, "cond2": cond2, "cond3": cond3}


def gen_pancake(rng, spec=None):
    """烙饼问题：n 张饼（每张 2 面）、锅每次烙 k=2 张、每面 t 分钟 → 最少总时间 = ceil(2n/k)·t = n·t。"""
    s = spec or {}
    n = rng.choice([3, 5])                  # 饼数（奇数让交替烙有意义，且保证 40% 采样时刻红/蓝两面同现）
    k = 2                                   # 平底锅每次最多烙 2 张
    t = rng.randint(*s.get("t", (2, 3)))    # 每面分钟数
    sides = 2 * n
    total = (sides + k - 1) // k * t        # = n·t（k=2）
    return {"n": n, "k": k, "t": t, "sides": sides, "total": total}


def gen_tianji(rng, spec=None):
    """田忌赛马：齐王上/中/下出马顺序随机，田忌用 下对王上(负)、上对王中(胜)、中对王下(胜) 赢 2 局。"""
    s = spec or {}
    order = ["上", "中", "下"]
    rng.shuffle(order)                     # 齐王三场出马顺序（第 1..3 场）
    qw_speed = {"上": 6, "中": 4, "下": 2}  # 齐王马速
    tj_speed = {"上": 5, "中": 3, "下": 1}  # 田忌马速（各低一档，但上能胜中、中能胜下）
    target = {"上": "中", "中": "下", "下": "上"}  # 田忌马 → 应对的齐王马
    ans_lane = {tj: order.index(qw) + 1 for tj, qw in target.items()}
    init_lane = {tj: order.index(tj) + 1 for tj in ["上", "中", "下"]}  # 按同档对位 = 全输（起点）
    return {"order": order, "qw_speed": qw_speed, "tj_speed": tj_speed,
            "target": target, "ans_lane": ans_lane, "init_lane": init_lane}


def gen_fraction_more_less(rng, spec=None):
    """分数·多/少几分之几：乙 B=k·m、甲=B±m → 甲比乙 多/少 m/(k·m)=1/k。答案量 = 相差 m。"""
    s = spec or {}
    mode = rng.choice(["多", "少"])
    k = rng.randint(*s.get("k", (2, 6)))   # 分母（1/k）
    m = rng.randint(*s.get("m", (2, 5)))   # 相差（答案量，整数）
    B = k * m                              # 乙（单位「1」）
    A = B + m if mode == "多" else B - m   # 甲
    return {"mode": mode, "k": k, "m": m, "B": B, "D": m, "A": A}


def gen_interest(rng, spec=None):
    """利率/利息：本金 P=100·m、年利率 r%、存 n 年 → 利息 = P·r%·n = m·r·n（恒整数）。"""
    s = spec or {}
    m = rng.randint(*s.get("m", (1, 5)))   # 本金 = 100·m
    r = rng.randint(*s.get("r", (2, 6)))   # 年利率 %
    n = rng.randint(*s.get("n", (1, 5)))   # 存期（年）
    P = 100 * m
    return {"P": P, "r": r, "n": n, "interest": m * r * n, "m": m}


def gen_plant_two_sides(rng, spec=None):
    """植树(两侧)：间隔数 n、间隔 d 米 → 路长 D=n·d、单侧 k=n+1、两侧总 total=2(n+1)。"""
    s = spec or {}
    for _ in range(MAX_ATTEMPTS):
        n = rng.randint(*s.get("n", (4, 12)))
        d = rng.randint(*s.get("d", (2, 5)))
        D = n * d
        k = n + 1
        return {"n": n, "d": d, "D": D, "k": k, "total": 2 * k}
    raise NoGoodNumbers("plant_two_sides")


def gen_equation_balance(rng, spec=None):
    """方程/天平图：挑答案 x、系数 a、常数 b → 右盘 = a·x + b，天平左=右 时平衡。"""
    s = spec or {}
    x = rng.randint(*s.get("x", (2, 6)))   # 未知数（答案量）
    a = rng.randint(*s.get("a", (2, 4)))   # x 的系数
    b = rng.randint(*s.get("b", (1, 6)))   # 常数项
    return {"x": x, "a": a, "b": b, "right": a * x + b}


def gen_triangle_equal(rng, spec=None):
    """三角形·等底等高：底 b（偶）、高 h，顶点 C 沿 h-line 左右滑动，面积恒 b·h÷2。
    答案量 = 面积（整数）；目标横坐标 = b//2（底边中点正上方 → 等腰三角形）。"""
    s = spec or {}
    b = rng.choice(s.get("b", (6, 8, 10)))   # 底（偶数，保证面积/中点整数）
    h = rng.randint(*s.get("h", (3, 5)))     # 高
    mid = b // 2
    s0 = rng.randint(1, b - 1)               # 顶点 C 初始横坐标（偏离中点）
    if s0 == mid:
        s0 = mid + 1 if mid < b - 1 else mid - 1
    return {"b": b, "h": h, "s0": s0, "mid": mid, "area": b * h // 2}


def gen_para_equal(rng, spec=None):
    """平行四边形·等底等高：底 b（偶）、高 h，顶点 D 沿 h-line 左右滑动（斜量 o∈[−2,2]），
    对顶点 C=D+(b,0) 联动，面积恒 b·h；o=0 时变成长方形（割补法）。答案量 = 面积（整数）。"""
    s = spec or {}
    b = rng.choice(s.get("b", (6, 8, 10)))
    h = rng.randint(*s.get("h", (3, 5)))
    o = rng.choice(s.get("o", (-2, -1, 1, 2)))   # 初始斜量（非 0，起始非长方形）
    return {"b": b, "h": h, "o": o, "area": b * h}


def gen_tri_height(rng, spec=None):
    """三角形·已知底求高：底 b（偶）、目标高 h、面积 area=b·h÷2；顶点 C 沿 v-line 上下移动
    （变高），目标高 h；y0 为初始高（低于目标，非答案）。答案量 = 高 h（整数）。"""
    s = spec or {}
    b = rng.choice(s.get("b", (6, 8, 10)))
    h = rng.randint(*s.get("h", (3, 5)))
    y0 = rng.randint(1, h - 1)                  # 初始高（1..h-1，低于目标）
    return {"b": b, "h": h, "y0": y0, "mid": b // 2, "area": b * h // 2}


def gen_trapezoid(rng, spec=None):
    """梯形·等积变形：下底 b（偶）、上底 u（偶，<b）、高 h，顶点 D 沿 h-line 滑动（上底平移），
    面积恒 (b+u)·h÷2；目标 D.x=(b−u)//2（等腰梯形）。答案量 = 面积（整数）。"""
    s = spec or {}
    b = rng.choice(s.get("b", (6, 8, 10)))
    u = rng.choice(s.get("u", (2, 4, 6)))
    while u >= b:
        u -= 2
    h = rng.randint(*s.get("h", (3, 5)))
    mid = (b - u) // 2
    o0 = rng.randint(0, b - u)                  # D 初始横坐标（偏离中点）
    if o0 == mid:
        o0 = mid + 1 if mid < b - u else mid - 1
    return {"b": b, "u": u, "h": h, "o0": o0, "mid": mid, "area": (b + u) * h // 2}


def gen_recompose(rng, spec=None):
    """平行四边形·割补法：底 b（偶）、高 h、斜量 o，割下左侧三角形平移到右侧拼成长方形，
    面积恒 b·h；拖动点 G 从 0 滑到 b（拼成）。答案量 = 面积（整数）。"""
    s = spec or {}
    b = rng.choice(s.get("b", (6, 8)))
    h = rng.randint(*s.get("h", (3, 5)))
    o = rng.choice(s.get("o", (2, 3)))
    return {"b": b, "h": h, "o": o, "area": b * h}


def gen_circle(rng, spec=None):
    """圆·周长：半径 r（格），直径 = 2r、周长 = 直径 × 3 = 6r（圆周率取 3，答案量恒整数）。
    答案量 = 周长 C（整数）；r0 为初始半径（非答案）。"""
    s = spec or {}
    r = rng.randint(*s.get("r", (2, 5)))
    r0 = rng.randint(1, 6)
    if r0 == r:
        r0 = r + 1 if r < 6 else r - 1
    return {"r": r, "r0": r0, "d": 2 * r, "C": 6 * r}


def gen_circle_area(rng, spec=None):
    """圆·面积：半径 r（格），面积 = 半径² × 3 = 3r²（圆周率取 3，答案量恒整数）。
    答案量 = 面积 S（整数）；r0 为初始半径（非答案）。"""
    s = spec or {}
    r = rng.randint(*s.get("r", (2, 5)))
    r0 = rng.randint(1, 6)
    if r0 == r:
        r0 = r + 1 if r < 6 else r - 1
    return {"r": r, "r0": r0, "d": 2 * r, "S": 3 * r * r}


def gen_semicircle(rng, spec=None):
    """半圆·周长：半径 r（格），半圆弧长 = 直径×3÷2 = 3r、半圆周长 = 半圆弧 + 直径 = 5r
    （圆周率取 3，答案量恒整数）。答案量 = 半圆周长 C（整数）；r0 为初始半径（非答案）。"""
    s = spec or {}
    r = rng.randint(*s.get("r", (2, 5)))
    r0 = rng.randint(1, 6)
    if r0 == r:
        r0 = r + 1 if r < 6 else r - 1
    return {"r": r, "r0": r0, "d": 2 * r, "arc": 3 * r, "C": 5 * r}
