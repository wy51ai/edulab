# 解法配方与约定（conventions）

## 1. 好数配方表（答案先行拒绝采样）

核心思想：**先挑答案量与关系量，再反推已知量**——答案量天然整数，永不「算出答案再判规整」。

| 生成器 | 先挑 | 反推 | 约束 | 答案关系 |
| --- | --- | --- | --- | --- |
| `gen_pursue` | `dv∈[2,6]`、`tMeet∈[3,15]`、`vB∈[4,15]` | `vA=vB+dv`、`gap=dv·tMeet` | `gap∈[8,90]` | `tMeet=gap/(vA−vB)` |
| `gen_meet` | `tMeet∈[3,15]`、`vA,vB∈[4,18]` | `total=(vA+vB)·tMeet` | `total∈[60,400]` | `tMeet=total/(vA+vB)` |
| `gen_circular_same` | `L∈{60…240}`、`dv=因子(L)∈[2,6]` | `tMeet=L//dv`、`vA=vB+dv` | `tMeet∈[10,40]` | 甲多跑一圈 `L` |
| `gen_circular_opp` | `L∈{…}`、`vA,vB∈[4,12]` | `L%(vA+vB)==0`、`tMeet=L//(vA+vB)` | `tMeet∈[3,15]` | 合跑一圈 `L` |
| `gen_sum_diff` | 较小数 `a∈[4,30]`、差 `D∈[2,20]` | `b=a+D`、`S=2a+D` | `b≤60` | `a=(S−D)/2` |
| `gen_sum_multiple` | 较小数 `a∈[3,18]`、倍数 `n∈[2,8]` | `b=n·a`、`S=(n+1)·a` | `b≤80` | `a=S/(n+1)` |
| `gen_diff_multiple` | 较小数 `a∈[3,20]`、倍数 `n∈[2,6]` | `b=n·a`、`D=(n−1)·a` | `b≤90` | `a=D/(n−1)` |
| `gen_profit_loss` | 人数 `n∈[3,15]`、每人少 `a∈[2,8]`、两次差 `dd∈[2,5]` | `c=a+dd`、`spread=n·dd`、盈 `b∈[max(1,spread−c+1),spread−1]`、亏 `d=spread−b`、`total=a·n+b` | `spread≥3`、`d<c`（蓝条全程恒正） | `n=(b+d)/(c−a)` |
| `gen_age` | 儿子 `Q∈[5,12]`、倍数 `n∈[2,4]`、几年 `t∈[2,10]` | `P=n·Q+(n−1)·t` | `P≤60`、`P>Q` | `(P+t)/(Q+t)=n` |
| `gen_average` | `x<y<z` 且 `(x+y+z)%3==0` | `A=(x+y+z)//3` | `x∈[4,20]`、`y∈[8,28]`、`z∈[12,40]` | `z=3A−x−y` |
| `gen_chicken_rabbit` | 鸡 `c∈[3,12]`、兔 `r∈[2,10]` | `H=c+r`、`L=2c+4r` | — | `c=(4H−L)/2` |
| `gen_plant` | 间隔数 `n∈[4,12]`、间隔 `d∈[2,5]` | `D=n·d`、`k=n+1` | — | `k=D/d+1` |
| `gen_work` | 合做 `t∈[2,10]`、`x \| t²` | `a=t+x`、`b=t+t²/x` | `a,b≤40`、`a≠b` | `1/a+1/b=1/t` |
| `gen_cycle` | 周期 `p∈[3,5]`、序号 `N∈[12,40]` | `r=((N−1)%p)+1` | — | `r=(N−1)%p+1` |
| `gen_unit` | 单价 `u∈[2,8]`、`m∈[3,6]`、`n∈[4,9]` | `w=m·u`、`ans=n·u` | `n≠m` | `ans=n·(w/m)` |
| `gen_aggregate` | `a∈[3,8]`、`m∈[4,10]` | `w=a·m`、`b=因子(w)≠a`、`n=w//b` | `b∈[2,w−1]` | `n=w/b` |
| `gen_boat` | 顺 `p`、逆 `q`（均偶数，`p>q`） | `s=p·q`、`t1=q`、`t2=p`、`u=(p−q)/2`、`v=(p+q)/2` | `p,q∈{4,6,8,10,12}` | `u=(p−q)/2` |
| `gen_train` | 车长 `L∈[40,150]`、桥长 `B∈[100,300]`、速度 `v∈[5,15]` | `(L+B)%v==0`、`t=(L+B)/v` | `t∈[8,40]` | `t=(L+B)/v` |
| `gen_avgspeed` | `v1,v2`（均偶数，`v1≠v2`） | `(2·v1·v2)%(v1+v2)==0`、`avg=2·v1·v2/(v1+v2)`、`arith=(v1+v2)/2` | `v∈{4,6,8,10,12,16,20}` | `avg=2·v1·v2/(v1+v2)` |
| `gen_fraction_part` | 整体 `W=d·k`、分率 `n/d` | `part=W·n//d` | `n<d` | 部分 `=W·n/d` |
| `gen_fraction_whole` | 部分 `P=W·n//d`、分率 `n/d` | `W=P·d//n` | `n<d` | 整体 `=P·d/n` |
| `gen_fraction_ratio` | 甲 `=n·k`、乙 `=d·k`（`n<d` 互质） | — | `n<d` | 甲是乙的 `n/d` |
| `gen_discount` | 原价 `A`（可被 10 整除）、折 `d` | 现价 `=A·d//10` | `d∈[2,9]` | 现价 `=A·d/10` |
| `gen_percent_change` | 原价 `A`、涨 `x%`（`A·x` 可被 100 整除） | 现价 `=A+A·x//100` | — | 现价 `=A·(1+x%)` |
| `gen_ratio_share` | 比 `a:b`、每份 `k` | 甲 `=a·k`、乙 `=b·k`、总 `=(a+b)k` | — | 甲:乙 `=a:b` |
| `gen_ratio_scale` | 比例尺 `1:n`、图上 `d` | 实际 `=n·d` | — | 实际 `=n·d` |
| `gen_concentration` | 溶液 `g`、浓度 `c%`（`g·c` 可被 100 整除） | 盐 `=g·c//100` | — | 盐 `=g·c%` |
| `gen_midpoint_meet` | `v甲>v乙`、时间 `t`（速度差取偶） | 全程 `T=(v甲+v乙)t`、中点偏移 `m=(v甲−v乙)t/2` | — | 相遇点离中点 `m` |
| `gen_restore` | 答案 `W`（逆推） | 选参数使每步中间量整数 | — | 还原得 `W` |
| `gen_average_move` | 甲 `a>乙b` 且 `a−b` 偶 | 给 `(a−b)/2` | — | 各移 `(a−b)/2` 相等 |
| `gen_stairs` | 层/段/下数 `n`、每单位 `t` | 总 `=(n−1)·t` | — | 总 `=(n−1)·t` |
| `gen_cows` | 草日长 `g`、原有 `G`（`G` 可被 `t` 整除） | 牛数 `N=g+G//t` | — | 可吃 `t=G/(N−g)` 天 |
| `gen_phalanx` | 每边 `n` | 总数 `=n²`、外层 `=4n−4` | `n≥3` | 总数 `=n²` |
| `gen_pigeonhole` | 苹果 `m=n·k+r(r>0)`、抽屉 `n` | 至少 `=k+1` | — | 至少 `=⌈m/n⌉` |
| `gen_clock` | 整点 `h` | 夹角 `=30·h`（取较小角，模 360） | 避开分数答案 | 夹角 `=30·h` |
| `gen_elimination` | 两两和 `x+y、y+z、x+z` | 甲 `x=(①+③−②)/2` | 均整数 | `x=(①+③−②)/2` |
| `gen_arithmetic_seq` | 首项 `a`、公差 `d`、项数 `n` | 第 n 项 `=a+(n−1)d` | — | `an=a+(n−1)d` |
| `gen_optimize` | 大船 `a`人/`p`元、小船 `b`人/`q`元、共 `N` | 扫可行方案，取总价最小且唯一 | 大船人均更低、`optK≥2` | 总价 `=k·p+⌈余/b⌉·q` |
| `gen_page_digit` | 页数 `n≤99` | 数字 `=9+2·(n−9)` | `n≥10` | 数字 `=9+2·(n−9)` |
| `gen_sum_diff_three` | 甲 `a`、差 `D`、倍数 `n` | 乙 `=a−D`、丙 `=n·a`、和 `S` | `a>D` | 三数和 `=S` |
| `gen_profit_loss_two_gain` | 每人 `a` 余 `b`、每人 `c` 余 `d`（`c>a,b>d`） | `n=(b−d)/(c−a)`、`total=n·a+b` | — | 人数 `=n` |
| `gen_profit_loss_two_loss` | 每人 `a` 缺 `b`、每人 `c` 缺 `d`（`c>a,d>b`） | `n=(d−b)/(c−a)`、`total=n·a−b` | — | 人数 `=n` |
| `gen_plant_one` | 间隔数 `n`、间隔 `d` | 路长 `D=n·d`、棵树 `k=n` | — | 棵树 `=n` |
| `gen_plant_none` | 间隔数 `n`、间隔 `d` | 路长 `D=n·d`、棵树 `k=n−1` | — | 棵树 `=n−1` |
| `gen_plant_ring` | 间隔数 `n`、间隔 `d` | 路长 `D=n·d`、棵树 `k=n` | — | 棵树 `=n` |
| `gen_overlap_venn` | 只甲 `a≥3`、只乙 `b≥3`、两科都优 `c≥2` | `X=a+c`、`Y=b+c`、`T=a+b+c` | `c≤min(X,Y)−1` | `c=X+Y−T` |
| `gen_match_count` | 上衣 `m∈[2,4]`、裤子 `n∈[2,5]` | `total=m·n` | — | 搭配 `=m·n` |
| `gen_logic_table` | 3 人 × 3 运动的唯一排列 `perm` | 条件1=甲排除法、条件2=乙肯定、条件3=丙 | 唯一解 | 三人各一运动 |
| `gen_pancake` | 饼数 `n∈{3,5}`、锅容 `k=2`、每面 `t∈[2,3]` | `sides=2n`、`total=ceil(2n/k)·t` | `n` 奇 | `total=n·t` |
| `gen_tianji` | 齐王出马顺序（上/中/下随机） | 田忌 下→王上(负)、上→王中(胜)、中→王下(胜) | — | 赢 2 局 |
| `gen_fraction_more_less` | 分母 `k∈[2,6]`、相差 `m∈[2,5]` | `B=k·m`、`A=B±m` | `A>0` | 甲比乙 多/少 `1/k` |
| `gen_interest` | 本金 `P=100·m`（`m∈[1,5]`）、年利率 `r∈[2,6]`、存期 `n∈[1,5]` | `interest=m·r·n` | — | 利息 `=P·r%·n` |
| `gen_plant_two_sides` | 间隔数 `n∈[4,12]`、间隔 `d∈[2,5]` | `D=n·d`、`k=n+1`、`total=2k` | — | 两侧 `=2(n+1)` |
| `gen_equation_balance` | 答案 `x∈[2,6]`、系数 `a∈[2,4]`、常数 `b∈[1,6]` | `right=a·x+b` | — | `x=(right−b)/a` |
| `gen_triangle_equal` | 底 `b∈{6,8,10}`（偶）、高 `h∈[3,5]`、C 初始横坐标 `s0∈[1,b−1]`（≠中点） | `mid=b//2`、`area=b·h//2` | `s0≠mid` | 面积 `=b·h/2` 恒，目标 `C=(mid,h)` |
| `gen_para_equal` | 底 `b∈{6,8,10}`（偶）、高 `h∈[3,5]`、斜量 `o∈{±1,±2}` | `area=b·h` | `o≠0` | 面积 `=b·h` 恒，目标 `D=(2,h)`（拉正为长方形） |
| `gen_tri_height` | 底 `b∈{6,8,10}`（偶）、目标高 `h∈[3,5]`、初始高 `y0∈[1,h−1]` | `mid=b//2`、`area=b·h//2` | `y0<h` | 高 `=2·area/b`，目标 `C=(mid,h)` |
| `gen_trapezoid` | 下底 `b∈{6,8,10}`、上底 `u∈{2,4,6}`（偶，`<b`）、高 `h∈[3,5]`、`o0∈[0,b−u]` | `mid=(b−u)//2`、`area=(b+u)·h//2` | `o0≠mid` | 面积 `=(b+u)·h/2` 恒，目标 `D=(mid,h)`（等腰） |
| `gen_recompose` | 底 `b∈{6,8}`（偶）、高 `h∈[3,5]`、斜量 `o∈{2,3}` | `area=b·h` | — | 割补平移三角形，目标 `G=(b,0)`（拼成长方形） |
| `gen_circle` | 半径 `r∈[2,5]`、初始半径 `r0∈[1,6]`（≠r） | `d=2r`、`C=6r`（圆周率取 3） | `r0≠r` | 周长 `=直径×3=6r`，目标 `r` |
| `gen_circle_area` | 半径 `r∈[2,5]`、初始半径 `r0∈[1,6]`（≠r） | `d=2r`、`S=3r²`（圆周率取 3） | `r0≠r` | 面积 `=半径²×3=3r²`，目标 `r` |
| `gen_semicircle` | 半径 `r∈[2,5]`、初始半径 `r0∈[1,6]`（≠r） | `d=2r`、`arc=3r`、`C=5r`（圆周率取 3） | `r0≠r` | 半圆周长 `=半圆弧3r+直径2r=5r`，目标 `r` |

约定：线段图题型里 `a = 较小数`、`b = 较大数`、`a < b`。和/差/倍数关系由 `rel.bigOf`
（`sum-minus-a` 或 `n-times-a`）在 STATE 里统一解析。盈亏/年龄/平均数/归一/归总/流水行船/
平均速度用 `bar.expr`（复合表达式）而非 `bar.var`，并可用 `ref`（参照虚线）与 `diffPair`
（高亮差段）。

`MAX_ATTEMPTS=200`，失败抛 `NoGoodNumbers`。行程 `tMax = tMeet + 5`（动画越过相遇点、
又不跨过第二次追上/相遇）。

## 2. 渲染器家族（一个渲染器吃一类题型）

| scene.kind | 语义 | 吃进 |
| --- | --- | --- |
| `road` | 直线道路，两车/两人，双箭头标实时相距 | 追及、相遇、中点相遇 |
| `circular` | 环形跑道，取模定位，圈数标注 | 环形追及、环形相遇 |
| `bar-model` | N 个色块 + 差段高亮 + 参照虚线 + 双箭头，滑块=答案量 | 和差、和倍、差倍、盈亏、年龄、平均数、归一、归总、流水行船、平均速度、分数、折扣、百分数、比例、浓度、还原、移多补少、牛吃草、抽屉、消去法、等差数列、最优化、页码、三数和差倍、盈亏两盈两亏 |
| `swap` | 滑块=某种数，总量联动（点数 = 腿数/头数） | 鸡兔同笼 |
| `interval` | 点-段图（路 + 树），`mode` 驱动两端/一端/不栽/环形/层段下/两侧 | 植树、植树变体（含两侧）、爬楼、锯木、敲钟 |
| `progress` | 双进度条（甲乙合做） | 工程 |
| `sequence` | 周期色块循环 + 游标 | 周期 |
| `train` | 桥 + 车身（滑动动画） | 火车过桥 |
| `phalanx` | n×n 方阵点阵（外层红框 + 内层蓝点） | 方阵 |
| `clock` | 钟面（红时针 + 蓝分针 + 橙夹角弧） | 时钟夹角 |
| `venn` | 两圆交叠，拖手柄改重叠区 | 容斥/韦恩图 |
| `link-graph` | 两列点 + 逐一连线（红上衣/蓝裤子） | 排列组合·搭配 |
| `logic-table` | 3×3 排除表，拖圆点落列（拖点可交互） | 逻辑推理 |
| `timeline` | 烙饼时间轴（正面红/反面蓝/已烙好绿） | 烙饼问题 |
| `matchup` | 三条道对阵，拖马配对，逐场判胜/负 | 田忌赛马 |
| `balance` | 天平图，拖砝码使倾斜归零 | 方程/解方程 |
| `geodrag` | 整数网格 + 多边形 + 可拖顶点（等积变形通用底座；支持 `depend` 联动顶点、`extra` 多分块、`hidden` 锚点、h-line/v-line 拖动） | 三角形·等底等高 / 平行四边形·等底等高 / 三角形·已知底求高 / 梯形·等积变形 / 平行四边形·割补法 |
| `circle` | 圆 + 半径/直径 + 周长展开线段 / 面积方格 / 半圆（圆周率取 3，半径滑块驱动，`mode` 区分：周长/面积/半圆周长） | 圆的周长 / 圆的面积 / 半圆的周长 |

**关键**：渲染器按 `scene.kind` 复用，不是按题型各写一套。新题型只要 `scene.kind` 落在
既有家族里，前端渲染器零改动。

## 3. 统一物理模型（行程，前端唯一硬编码）

```
同向 same:     sA=vA·t;  sB=x0B+vB·t;  rate=vA−vB;  initGap=x0B(linear)/L(circular)
相向 opposite: sA=vA·t;  sB=x0B−vB·t;  rate=vA+vB;  initGap=x0B(linear)/L(circular)
gapDist = initGap − rate·t      (0 = 追上/相遇)
```

`carB.x0` 由 Python 注入：pursue=`gap`、meet=`total`、circular-same=`0`、circular-opp=`L`。

## 4. s-t 图：展开弧长（不取模）

s-t 图画**展开弧长**（不取模），取模只发生在环形**主画布**圆周上。因此环形同向追及 =
线性追及（两条正斜率直线相交）、环形相向 = 线性相遇（正/负斜率相交），s-t 图渲染器可完全
复用；圈线 `diagram.laps=[L,2L,…]` 画水平虚线。

## 5. 关键坑（照抄即可避雷）

1. **零依赖**：`evalExpr` 用 `new Function(...names, body)`（**不要**写 `new Function.apply`
   ——严格模式下 `Function.apply` 是原型方法而非构造器）。
2. **动态变量键**：缓存键 `expr + '|' + Object.keys(vars).join(',')`；不同题型 vars 键不同，
   天然隔离。不要用固定键序（旧版 `KEY_ORDER` 已废弃）。
3. **播放/滑块同步**：程序写 `slider.value=t` 不触发 `input`，无反馈环；`input` 里
   `playing=false`。
4. **整数滑块扫动**：`param.step===1` 时播放按 0.4s/1 的整数扫动（精确命中答案变绿），
   `step<1` 时按时间连续推进。
5. **帧率无关**：位置永远 `STATE[type](t)` 解析计算（绝不逐帧累加），`dt=min(…,0.05)` 封顶。
6. **JS 负数取模为负**：`mod = (s%L + L) % L`。
7. **答案读数用固定字符串** `readouts[kind="answer"].value`，绝不实时浮点重算。
8. **`span/yMax` 由 Python `ceil(x/10)*10` 注入**，前端不自适应。
9. **相向 s-t 图乙线可能越界**：Liang-Barsky 裁剪到 `[0,xMax]×[0,yMax]`（`clipSeg`）。
10. **线段图色块防溢出**：`bx(val)=min(max(val,0)·ux, maxW)` 封顶，`scale=较小数+较大数`
    的答案值，答案状态下两色块正好铺满全宽（和差题型任意 t 都铺满，因为 `a+b≡S`）。

## 6. 自检断言要点

- **答案四源一致**：`generators` 答案 == `answer` == `steps` 末步展示值 == 前端
  `STATE(t).phase==="at"`（滑块拨到答案处状态变绿）。
- **零依赖铁证**：无头打开 `file://` 断言 `requestfailed=0`、canvas 非空白。
- **红/蓝实体**：线段图两色块、运动两车，像素抽检红 `#e2553f` / 蓝 `#3b7dd8` 均存在。
- **交互**：滑块拨到答案 → 状态条 `green`；播放后前进、暂停后稳定。
- 参考 `tests/test_generators.py`（62 类 × 1000 次抽样）与 `tests/test_builders.py`（62 类 schema 自检）。

## 7. 扩展配方（加题型五步）

1. `lib/generators.py` 加一个答案先行的 `gen_*`（保证答案整数）。
2. `lib/builders.py` 加 `build_*`（复用 `_base` / `_bar_scene` / `_motion_scene`），
   选一个既有 `scene.kind`（`road`/`circular`/`bar-model`/…）或新增家族。
3. `lib/steps.py` 加 `*_steps`。
4. `scripts/generate.py` 的 `REGISTRY` 注册；`template/board.html` 的 `STATE` 加对应
   `type`（若 scene.kind 是既有家族，DRAW/DIAGRAM 无需改动）。
5. `tests/` 补一条单测；`SKILL.md` 题型清单 + `conventions.md` 配方表各加一行。
