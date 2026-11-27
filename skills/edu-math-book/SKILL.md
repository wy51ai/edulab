---
name: edu-math-book
description: >-
  把任意一道高中数学题做成"书桌上翻开的习题册"互动网页：左页印着题面、关键词、设问和"先猜再掀纸片"的预测题，
  右页是铅笔素描的图形；点"看演示"后图形从书页立起来，钢笔在旁边草稿纸上逐字写出每一步推理链，彩色符号悬停联动图形，
  可带滑块参数实验。图形渲染器覆盖全部高中数学：solid（多面体 + 圆柱/圆锥/球，立体几何）、plane（坐标系、函数/导数图像、
  解析几何、平面几何、三角、统计柱状图，演示时像立体贺卡一样立起）、none（数列、不等式、概率计算、复数等无图题，右页是公式板）。
  可选"教室开场"：同学视频发问 + BGM + WebGL 教室，镜头落到课桌上。答案由 sympy 精确计算核对。
  触发词：书桌翻书, 互动试卷, 翻书演示, 习题册网页, 先猜后看, 做成书本样式的解题网页, 教室开场, 把这道题做成互动试卷,
  test-paper, interactive workbook page, desk book lesson.
---

# 高中数学题 → 书桌翻书互动网页

## 产出
一个 HTML（默认单文件；开场开启时同目录附带 `girl.mov / girl.webm / cmbg.mp3 / tex/textures.js`）。
壳（书桌、书本、道具、预测纸片、dock、钢笔手写、镜头、可选开场）全部在 `template/` 里，**每道题只写一个 `lesson.js`**。

## 依赖
- `python3` + **sympy**：核对答案（`python3 -c "import sympy"`）。
- `node` + **playwright / playwright-core**：`scripts/check.mjs` 截图自检。脚本会依次在 cwd、本技能目录、兄弟技能
  `edu-math-video/lesson` 里找。
- **缺库时先问用户是否安装，同意后再装**，不要擅自 `pip install` / `npm install`。

## 工作流程

### 1. 读题，定题型和渲染器
- 文字题直接抽取；图片题先读图，**把识别出的题面回显给用户确认**再继续。
- 选渲染器（详见 `references/renderers.md`）：

| 题型 | renderer |
|---|---|
| 立体几何（棱柱、棱锥、正方体、旋转体、截面、线面角/二面角/距离/体积） | `solid` |
| 函数与导数、三角函数图像、解析几何/圆锥曲线、平面几何、向量（平面）、线性规划、统计图 | `plane` |
| 数列、不等式证明、排列组合与概率计算、复数、二项式、纯代数推导 | `none` |

### 2. 用 sympy 精确求解（不要心算）
写一个临时脚本（放 cwd 或 /tmp）算出：最终答案、每一步要写的中间量、图形需要的坐标与关键点。
预测题的 4 个选项里要有 1 个正确答案和 3 个"典型错误"（漏条件、端点取错、公式记反…）。
lesson.js 里只放**结果**和可视化用的数值函数（`model(a)`、曲线 `f(x,a)`），并在文件头注释写一句"sympy 已核：…"。

### 3. 写 lesson.js
- 字段与写法见 `references/lesson-schema.md`；教学设计（关键句、推理链、预测题、配色）见 `references/pedagogy.md`。
- **先照着最接近的范例改**，不要从零写：

| 范例 | 演示什么 |
|---|---|
| `examples/solid_prism.js` | 直三棱柱：中位线 → 线面平行；滑块改边长让线面角 = 45°；线面距离 |
| `examples/solid_pyramid.js` | 三棱锥：二面角定高求体积；**带教室开场**（`intro.board` 黑板文字） |
| `examples/plane_function.js` | 三次函数单调性/极值/零点个数；导函数虚线、增减段着色、区域、滑块平移 |
| `examples/none_sequence.js` | 数列构造等比求通项 + 分组求和；右页公式板，KaTeX 推理链 |

- 文字里 `$AB$` 是几何符号（斜体，草稿纸上可悬停联动图形，`A1` 自动变 A₁）；`\( … \)` 是 KaTeX 公式。
  含 KaTeX 的字符串用 `String.raw\`…\`` 写，免得反斜杠被吃掉。

### 4. 生成
> 📍 成品写到**用户当前工作目录**（除非用户指定），**不要**写进技能目录。

```bash
python3 <skill>/scripts/generate.py lesson.js out/index.html            # 开场跟随 lesson 的 intro 字段（默认关）
python3 <skill>/scripts/generate.py lesson.js out/index.html --intro    # 强制带教室开场（会拷素材到 out/）
python3 <skill>/scripts/generate.py lesson.js out/index.html --no-intro
```
开场版建议用一个独立子目录输出（它会往 html 同目录拷 4 个素材文件）。

### 4.5 防闪烁硬规则（写 lesson.js 时必须遵守）
引擎已做了防抖（面可见性滞回、轮廓精确解、未变化帧不写 DOM、渲染异常保留上一帧），但下面这些只能靠 lesson 自己守：
1. **`model(a)` 必须是纯函数**：同一个 `a` 永远返回同样的点；禁止 `Math.random()`、`Date`、`performance.now()`、
   读写外部可变状态。随机出题在**写 lesson 之前**定好数，写成常量。
2. **点随参数连续变化**：不要在 `model` 里按阈值切换分支（`a > 1.5 ? … : …`）、不要在滑块范围内出现
   除零 / `Math.sqrt(负数)` / `tan(90°)`；`param.min/max` 要收在几何体存在的范围内。
3. **`model` 要轻**：每帧会被两张图各调一次。常量（如 `SQ3`、预解出来的系数）放在 `model` 外面；
   不要在里面做迭代求解、循环采样。
4. **面要合法**：每个面是**同一平面上的凸多边形**、顶点按边界顺序排列、至少 3 个不同点；整体是**闭合凸体**
   （每条棱恰好属于两个面）。非凸体拆成凸块或用 `extraEdges` 补棱。
5. **视角避开"侧对"**：`spec.view` 不要让某个侧面正好与视线平行（棱会在实线/虚线之间来回跳）；
   check.mjs 报 `[flicker]` 时把该步 `view` 转 10–20°。
6. **标签函数、`read`/`show`、`anim` 也必须是纯函数**；`anim` 用 `pingpong` 之类的连续函数，不要跳变。
7. **靠近图形中心的点给 `labelDir`**，否则标签方向不稳定。

### 5. 自检（必须做）
```bash
node <skill>/scripts/check.mjs out/index.html          # 截图到 out/_check/，打印 problems
```
- `problems` 必须为空，逐条修到没有为止：
  - `[lesson] …`：静态检查——缺字段、`model()` 不确定/有跳变/返回非有限值/太慢、面不共面/退化/不凸/不闭合、
    引用了不存在的点、KaTeX 语法错误、字符串里出现控制字符（`String.raw` 漏写）、`spec.a` 超出滑块范围。
  - `[flicker] #demoP-S …`：截图后让镜头视差晃动一圈，统计棱的实线/虚线翻转；有翻转就改该步 `spec.view`。
  - `[render] …` / `pageerror`：渲染时抛异常（滑块步骤会把参数从 min 扫到 max 一遍）。
  - `[slow] …`：帧率过低（`fps` 字段可看每一步帧率）。
- **逐张看截图**：`01_home.png`（左页是否溢出、图形是否清楚）、`02_flap.png`（掀开的答案）、`pN_sM.png`（每一步：
  图形高亮是否对准、标签是否互相压住、草稿纸是否写得下、立起来的图是否出画）。有问题改 lesson.js 重新生成。
  常见调整：`labelDir` 挪标签、`spec.view` 换角度、`figure.scale` 缩放、`plane.view` 改坐标范围、推理链拆成两步。
- `_check/` 是自检截图，交付时可以删掉。

### 6. 交付
告诉用户文件路径、怎么打开（直接双击；开场版需要和素材文件放在一起），并简述每一问的演示步骤。
深链：`index.html#demo2-3` 直接打开第 2 问第 3 步。

## 交互速览（写给用户看的）
左页：悬停设问 → 右页图形预览该问；点设问/“开始演示”进入演示。先选一个预测选项，再掀纸片看答案。
演示：← → 翻步，Esc 收起；草稿纸上彩色字母悬停 → 立体图上对应点/线/面闪烁；有滑块的步骤可拖动参数。
立体图可拖动旋转（书页上的平面图双击复位）。

## 注意
- lesson.js 会被内联进 `<script>`：不能出现 `</script`。引擎在独立作用域里，lesson 顶层随便起名，
  **只是不能重新声明 `core.js` 提供的辅助名**（`add sub mul dot mid len dist unit lerp cross centroidOf clamp01 ease
  pingpong rad deg SQ2 SQ3 SQ5 SQ6 foot footPlane angleAt fix slide travel tex geo fmt COL`）——直接用它们即可。
- 字体与 KaTeX 走 CDN，离线打开时公式会退化成源码；开场的 three.js 也走 CDN。
