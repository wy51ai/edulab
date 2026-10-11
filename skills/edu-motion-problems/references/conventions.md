# 解法配方与约定（conventions）

## 1. 好数配方表（答案先行拒绝采样）

核心思想：**先挑答案量 tMeet 和速度差/速度和，再反推路程量**——答案量（追上/相遇时间、
相遇点、圈数）天然整数，永远不需要「算出答案再判规整」。

| 生成器 | 先挑 | 反推 | 约束 | 答案关系 |
| --- | --- | --- | --- | --- |
| `gen_pursue` | `dv∈[2,6]`、`tMeet∈[3,15]`、`vB∈[4,15]` | `vA=vB+dv`、`gap=dv·tMeet` | `gap∈[8,90]` | `tMeet=gap/(vA−vB)` |
| `gen_meet` | `tMeet∈[3,15]`、`vA,vB∈[4,18]` | `total=(vA+vB)·tMeet` | `total∈[60,400]` | `tMeet=total/(vA+vB)` |
| `gen_circular_same` | `L∈{60,80,100,120,160,200,240}`、`dv=因子(L)∈[2,6]` | `tMeet=L//dv`、`vB∈[2,8]`、`vA=vB+dv` | `tMeet∈[10,40]` | 甲多跑一圈 `L` 追上 |
| `gen_circular_opp` | `L∈{…}`、`vA,vB∈[4,12]` | `L%(vA+vB)==0`、`tMeet=L//(vA+vB)` | `tMeet∈[3,15]` | 合跑一圈 `L` 相遇 |

`sMeet=(vA·tMeet) mod L`；`lapsA=⌊vA·tMeet/L⌋`；`lapsB=⌊vB·tMeet/L⌋`；环形同向 `lapGain=1`。

`MAX_ATTEMPTS=200`，失败抛 `NoGoodNumbers`。`tMax = tMeet + 5`（保证动画越过相遇点、又不
跨过第二次追上/相遇）。

## 2. 统一物理模型（前端唯一硬编码）

四题型归一成 `kind × direction` 矩阵，`motionState(t)` 一把钥匙开四把锁：

```
同向 same:     sA=vA·t;  sB=x0B+vB·t;  rate=vA−vB;  initGap=x0B(linear)/L(circular)
相向 opposite: sA=vA·t;  sB=x0B−vB·t;  rate=vA+vB;  initGap=x0B(linear)/L(circular)
gapDist = initGap − rate·t      (0 = 追上/相遇)
```

`carB.x0` 由 Python 注入，四种题型分别是 `gap / total / 0 / L`（见 problem-schema）。

## 3. s-t 图：展开弧长（不取模）

s-t 图画**展开弧长**（`sA=vA·t`、`sB=x0B+dirSign·vB·t`，均不取模），取模只发生在环形**主
画布**的圆周显示上。因此：

- 环形同向追及 → s-t 图 = 线性追及（两条正斜率直线，追上 = 甲线比乙线高一圈 L）。
- 环形相向相遇 → s-t 图 = 线性相遇（正/负斜率直线相交）。

s-t 图渲染器因此可完全复用；圈线 `graph.laps=[L,2L,…]` 画水平虚线表示「每多一圈」。

## 4. 关键坑（照抄即可避雷）

1. **零依赖**：`evalExpr` 用 `new Function(...names, body)`（**不要**写 `new Function.apply`
   ——严格模式下 `Function.apply` 是原型方法而非构造器，报 `Function.apply is not a constructor`）。
2. **播放/滑块同步**：程序写 `slider.value=t` 不触发 `input`（DOM 规范），天然无反馈环；
   `input` 事件里 `playing=false`，rAF 里 `t+=dt` 后写 `slider.value`。
3. **帧率无关**：位置永远 `motionState(t)` 解析计算（绝不逐帧累加），`dt=min(…,0.05)` 封顶。
4. **JS 负数取模为负**：`mod = (s%L + L) % L`。
5. **答案读数用固定字符串** `readouts[kind="answer"].value`，绝不实时浮点重算（避免「9.9 秒追上」）。
6. **`span/yMax` 由 Python `ceil(x/10)*10` 注入**，前端不做自适应。
7. **相向 s-t 图乙线可能越界**：用 Liang-Barsky 把直线裁剪到 `[0,xMax]×[0,yMax]`（`clipSeg`），
   乙线降到 0（回到起点）即停止绘制，不会画出负距离。

## 5. 自检断言要点

- 答案四源一致：`good_numbers` 答案 == `answer.tMeet` == `graph.meet.t` == 末步骤展示值
  == 前端 `motionState(tMeet).gapDist≈0`。
- 零依赖铁证：无头打开 `file://` 断言 `requestfailed=0`、双 canvas 非空白。
- 交互：滑块拨到 `tMeet` → 状态条 `green`；播放后时间前进、暂停后稳定。
- 参考 `tests/test_good_numbers.py`（1000 次抽样）与 `tests/test_builders.py`（schema 自检）。
