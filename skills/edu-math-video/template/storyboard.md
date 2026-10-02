# 分镜 Storyboard

每句旁白一行。`句` 列必须是 `幕id 句号`（从 0 数），与 script.json 一一对应（`build_audio.py --check` 会核对）。
- **指**：这句提到的元素如何被点亮（glow / bump / hiBox），其余元素是否变淡。
- **动**：这句里图上发生的**一个**体现推理的动作（见 reference/visual-design.md 动作表）。第一幕和最后一幕可写"—"。
- **留**：动作结束后留在图上的标记（直角符号、等长标记、数值、着色）。
- **板书**：右侧板子写什么。

| 句 | 旁白要点 | 指 | 动 | 留 | 板书 |
|---|---|---|---|---|---|
| intro 0 | 直角三角形，∠C=90° | hiBox 直角条件 | — | chip ∠C=90° | — |
| intro 1 | AC=3，BC=4 | hiBox AC、BC | — | chip | — |
| intro 2 | D 是 AB 中点 | hiBox 中点条件 | — | chip | — |
| intro 3 | 求 CD | hiBox 所求 | — | chip 求 CD | — |
| figure 0 | 画图，C 直角，AC=3，BC=4 | AC、BC 依次 glow | 三边依次画出，直角符号画出 | 长度 3、4 弹出 | 已知：∠C、AC、BC |
| figure 1 | 取 AB 中点 D，连 CD，提问后停四秒 | AB glow，CD glow | 红点沿 AB 从 A 滑到中点 D；CD 画出 | D、等长 tick、红色 CD，停顿时保留问题字幕 | D 中点；求 CD |
| key 0 | 核对直角与中点条件 | AC、BC 与中点 tick | 直角符号逐渐画出；AD 的复制品滑到 DB 上检验中点等长 | 直角和中点 | 两项已知条件 |
| key 1 | 斜边中线 = 斜边一半 | CD 闪 | CD 的复制品转到 DA、再转到 DB；以 D 为心的圆画过 A、B、C | 三条红线 + 紫色虚线圆 | 结论 |
| key 2 | 延长 CD 到 E，使 DE=CD | — | 虚线从 D 长到 E；CD 复制品滑到 DE | E、等长 | 延长；DE=CD |
| key 3 | 对角线互相平分 + 直角 ⇒ 矩形 | 直角、D 中点 | 矩形区域逐渐着色 | 矩形 | 平行四边形 ⇒ 矩形 |
| key 4 | 对角线相等 | CE、AB 同时 glow | 对角线 CE 的复制品旋转到 AB 上重合 | CD 再闪 | 对角线相等 ⇒ CD = ½AB |
| solve 0 | 勾股：AB=5 | AC、BC 闪，AB 持续 glow | AB 旁数字从 0 数到 5 | AB = 5 | 勾股三行 |
| solve 1 | CD = AB÷2 = 2.5 | CD glow | DB 的复制品滑到 CD 上；CD 数字数到 2.5 | CD = 2.5 | CD = 2.5，盖章 |
| outro 0 | 回顾 | — | — | 三张卡片 | — |
| outro 1 | 原题答案；斜边变为十时中线是多少，停四秒 | — | — | 吉祥物 + 气泡，保留迁移问题字幕 | — |
| outro 2 | 迁移答案：仍是一半，中线五 | — | — | 气泡换成 CD=5 | AB=10 ⇒ CD=5 |
