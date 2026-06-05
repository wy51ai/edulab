# edulab

**简体中文** · [English](README.md)

教育类技能集合：把学科问题转成**可交互的教学网页**。

edulab 是一个 [Claude Code](https://claude.com/claude-code) 插件（plugin + marketplace）。它的目标是：给一道题，产出一个能直接用浏览器打开、自带讲解和可视化的单页 HTML，让"看懂"变成"能动手转一转看明白"。

首个技能 **edu-solid-geometry** 负责立体几何解题：用"建系 + 向量法"求解，由 [sympy](https://www.sympy.org) 精确计算驱动，输出左侧分步解析（MathJax）+ 右侧可交互 3D 模型（Three.js）的教学网页。

## 效果预览

![edulab 效果预览 —— 线面角教学网页](demo1.png)

根目录的 [index.html](index.html) 是一个成品样例（正四棱锥·线面角），直接用浏览器打开即可查看：

- **左侧**：题面 / 答案 / 分步解析，公式用 MathJax 渲染
- **右侧**：题目对应的 3D 模型，可旋转缩放，分步高亮关键元素并切换镜头
- 答案、3D 坐标、每步中间数值**同源一致**（都来自同一份 sympy 计算）

更多样例见 [skills/edu-solid-geometry/output/](skills/edu-solid-geometry/output/)（cube / box 等）。

## 安装

**推荐** —— 用 [skills](https://github.com/vercel-labs/skills) 一行命令安装：

```bash
npx skills add wy51ai/edulab
```

后续更新到最新版：

```bash
npx skills update
```

或作为 Claude Code 插件市场使用：

```
/plugin marketplace add wy51ai/edulab
/plugin install edulab
```

安装后，技能会随触发词自动激活，也可被其他 agent 调用来生成这类网页。

## 技能：edu-solid-geometry

把一道立体几何题解成一个自包含的交互教学网页。支持三种入口：

| 入口 | 说明 |
|---|---|
| 文字题目 | 直接抽取题面求解 |
| 上传图片 | 视觉读图识别题目，回显确认后求解 |
| 随机出题 | 随机参数求解，答案不规整自动重抽 |

**覆盖题型**：正方体 / 长方体、棱锥 / 棱柱、圆柱 / 圆锥上的——线面角、二面角、异面直线夹角、点到平面距离、体积等。统一用"建系 + 向量法"。

**触发词**：立体几何、线面角、二面角、异面直线、点到平面距离、正四棱锥、解这道几何题、随机出一道立体几何题、这张图里的立体几何题；solid geometry, line-plane angle, dihedral angle, distance to plane, interactive geometry solution page 等。

### 依赖

计算核心 `lib/geometry_kernel.py` 依赖 **sympy**。用任意一个能 import sympy 的 `python3` 即可：

```bash
python3 -m pip install sympy   # 若缺 sympy
```

### 命令行直接生成（不经过 Claude）

```bash
cd skills/edu-solid-geometry
python3 scripts/generate.py cube   ./cube.html     # 正方体·线面角
python3 scripts/generate.py box    ./box.html      # 长方体·体积
python3 scripts/generate.py random 7 ./random.html # 随机出题（seed=7）
python3 lib/geometry_kernel.py                     # kernel 内置样例自检
```

> 不传输出路径时，默认写到**当前工作目录（cwd）**。

## 工作原理

1. **得到 problem spec** —— 三入口归一成结构化描述（几何体类型与尺寸、已知条件、所求、语言）。
2. **kernel 精确计算** —— sympy 算出精确坐标、关键向量、法向量、最终答案及各步中间量（LaTeX 字符串），绝不心算。
3. **组装并注入模板** —— 把 `lesson` / `steps` / `model` 数据注入数据驱动模板 `template/lesson.html`，3D 顶点坐标由 `kernel.to_three(...)` 给出，与解题同源。
4. **自检** —— kernel 答案 == 答案卡 == 末步骤展示值；本地静态服务 + 预览检查无报错、公式与高亮正常。
5. **交付** —— 成品写到用户当前工作目录，命名形如 `solution-<题目简述>.html`。

## 目录结构

```
edulab/
├── .claude-plugin/
│   ├── plugin.json              # 插件元信息
│   └── marketplace.json         # 市场清单
├── index.html                   # 成品样例（正四棱锥·线面角）
└── skills/
    └── edu-solid-geometry/
        ├── SKILL.md             # 技能说明与工作流程
        ├── template/lesson.html # 数据驱动模板（通用 3D 渲染器 + 数据岛）
        ├── lib/
        │   ├── geometry_kernel.py  # sympy 精确计算核心
        │   └── bodies.py           # 几何体棱拓扑库
        ├── scripts/generate.py  # 注入模板 + 范例构建函数
        ├── output/              # 技能内部开发样例
        └── references/
            ├── problem-schema.md   # 数据格式
            └── conventions.md      # 建系约定、解法配方、自检
```

## 扩展

- **加题型**：在 `geometry_kernel.py` 加求解函数（见 `references/conventions.md` 配方表），在 `generate.py` 加一个 `build_*`。
- **加几何体**：在 `geometry_kernel.py` 加坐标构建函数，在 `bodies.py` 加棱拓扑。

## License

[Apache-2.0](LICENSE)

## 作者

WY · [@akokoi1](https://x.com/akokoi1)

欢迎 star、issue、PR。
