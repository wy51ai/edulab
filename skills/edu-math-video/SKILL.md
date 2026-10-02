---
name: edu-math-video
description: Use when asked to make an explainer / walkthrough video (讲解视频、解题视频、例题精讲、生物微课、细胞动画) for a math problem (geometry, algebra, functions, motion/行程 problems) or a supported biology mechanism, from a problem screenshot or text, with Chinese narration (GLM-TTS or a supported offline fallback), bilingual zh+en subtitles and Canvas animation rendered to MP4.
---

# 数学与生物讲解视频 (edu-math-video)

把数学题或适用的生物机制做成 16:9、1920×1080、带中文配音 + 中英双语字幕 + Canvas 动画的 MP4。保留数学题的笔记本风格与解题接口；生物机制可用具体的细胞剖面模型。技能名保持不变。

流水线（每个视频一个文件夹）：

```
script.json ──build_audio.py──► build/timeline.json + build/mix.wav + ../<name>.srt
     (旁白)     (GLM-TTS + 合成音乐)          │
anim.js + engine.js ◄─────────────────────────┘ (按旁白时间点驱动动画)
     └──node render.mjs video──► ../<name>.mp4
```

**核心原则：画面跟着旁白走，而且图会"讲题"。** 每句旁白，图上都有一个动作把这句推理演出来（线段滑过去重合、三角形叠上去、相机转到俯视、动点移动……），不是只多出一条线、一个标签。每个动画都用"第 k 句旁白开始的时刻"`S.at(k, f)` 定时，绝不写死秒数。

生物课程以可追问的视觉现象开场，一句旁白解释一个可见变化，结尾用迁移问题检查是否理解。用同一模型完成“整体 → 局部 → 机制变化 → 回到整体”。先验证约一分钟样片，再扩展整课。不得为了吸引观看改变科学因果，也不承诺流量或未经测量的学习效果。

**本技能自带全部代码**，不要从别的项目复制文件：
- `template/`：可直接运行的完整示例项目（直角三角形斜边中线题）。`engine.js` 是通用引擎（不改），`anim.js` / `script.json` / `episode.json` / `problem.png` 是每道题都要重写的。
- `shared/pron.py` + `shared/pron.json`：读音控制（GLM-TTS 没有 SSML/拼音输入）。
- `examples/cone-parallel/`：立体几何完整示例（anim.js + storyboard.md + script.json）：相机斜视↔俯视、侧面展开成扇形、内错角旋转、平面平移。做立体几何、圆、多问题时先读它。
- `lib/biology-model.js`：可复用 Canvas 动物细胞模型；同一目标线粒体经历包裹、闭合、移动、与溶酶体融合和内部降解。`examples/mitophagy-cell/` 是约一分钟的完整示例，`scripts/create_biology_demo.py` 可将其创建为独立项目。
- `scripts/`：Windows 使用 `new_video.ps1` + `setup_check.py`；其他平台使用 `new_video.sh`（建项目）、`setup_check.sh`（查环境）、`make_problem_png.py`（文字题→图片+高亮框）、`problem_boxes.py`（截图→高亮框坐标）、`contact_sheet.py`（截图拼图审查）。

下文 `SKILL` = 本文件所在目录，`WS` = **用户当前所在的目录（你的工作目录，`$PWD`）**：视频文件夹建在这里，mp4/srt 也输出到这里。**不要因为别的目录（包括本技能所在的项目）已经有 `.env`、`node_modules`、`pron.json` 就把 WS 换过去**，缺什么由 `new_video.sh` 和第 2 步补齐。`PROJ` = 本视频文件夹，`PY` = `setup_check.sh` 报告的 python（macOS 上一般是 `/usr/bin/python3`；PATH 里的 `python3` 可能没有 numpy）。

## 必须遵守的规则

**退出码不是 0 就是没完成。** `--check` 退出码 1（哪怕只剩一个 ⚠ 多音字）、`motion` 退出码 1、截图里有问题，都不能写"只是警告、不影响"然后继续。修好再往下走。

1. **按下面 11 步完成所需检查，每步的"通过标准"满足了才能继续。** 不要把必要核对留到昂贵导出之后。
2. **先提出具体问题，再讲清依据。** 可以用视觉现象开场。解题课程在使用条件前展示原题图片并指明对应条件；不必逐字念整段题干。独立机制微课无需虚构原题图片。
3. **`tts` 字段只能是能念出来的中文。** 不能有阿拉伯数字、`= + − × ÷ / ^ √ ∠ △ ∥ ° ( )` 等符号：`AC=3` 写成 `AC等于三`，`x²` 写成 `x的平方`。字幕 `zh` 字段保留正常数学写法。`--check` 会报错拦住。
4. **读音必须固定。** 调 TTS 之前 `--check` 必须显示 `未固定读音的生僻字/多音字: 0` 且 `script errors: 0`。多音字的标注写在该字**后面**：`长[cháng]`、`要[yào]求`。**不能**写成 `中点[zhōng]`（那会把"点"读成 zhōng）。
5. **API Key 只能由用户提供。** 需要 GLM-TTS 但缺 `GLM_API_KEY` 时按 [reference/glm-tts-setup.md](reference/glm-tts-setup.md#没有-glm-key-时兜底引擎) 处理。已有免费离线配音偏好时继续使用，不要重复询问。不要编造 key、模型名或接口地址，不打印 key，不写进项目文件夹。
6. **画面不遮挡字幕**（默认字幕框 y≈914~1044，主要教学内容保持在 y ≤ 860）。数学题可用左图右板；生物模型可以占主画面，标签贴着结构，并用 `episode.motion_regions` 配置动作检查区域。
7. **先写分镜，再写动画。** `storyboard.md` 给每句旁白规划"指/动/留"，按 [reference/visual-design.md](reference/visual-design.md) 的动作表选动作；`node render.mjs motion` 必须通过。
8. **先预览再生成完整成品。** 用 `--preview` + `stills auto` 检查版面与机制；新风格先做 45～60 秒样片，审阅后再批量导出。
9. **看图验证。** 每次渲染截图后都要打开 `build/sheet.png` 亲眼检查（用读图工具），不能只看命令有没有报错。汇报时写你实际看到了什么，不要凭印象全部打勾。
10. **不要修改 `engine.js`**，除非用户要求换风格；需要新图形就在 `anim.js` 里写函数。
11. **不要把 `node_modules`、`package*.json` 复制进视频文件夹**，依赖在 `WS` 根目录装一次，所有视频共享。

## 11 个步骤

### 第 1 步：弄清题目，自己先把题解对
- 拿到题目文字（有截图就先读图）。**先自己完整解一遍并验算**，写下：已知条件清单、所求、关键思路（1~2 个）、每一步计算、最终答案、验算方法。
- 答案不确定或题目看不清时，问用户，不要猜。
- 生物课列出细胞类型、结构位置、机制顺序和证据边界；按 [reference/biology-visuals.md](reference/biology-visuals.md) 核对。区分题目实测、一般机制和推断；不得把活性氧数据讲成存活率。
- **通过标准：** 你能用 3~6 个"幕"讲完，每一幕一句话说清目的；答案已验算。

### 第 2 步：建项目、查环境
```bash
bash SKILL/scripts/new_video.sh "$PWD" <ascii_folder_name>     # WS 就是当前目录
bash SKILL/scripts/setup_check.sh WS/<ascii_folder_name>
```
Windows PowerShell（无需 Bash 或创建符号链接权限）：
```powershell
& SKILL/scripts/new_video.ps1 -Workspace $PWD -Name my_problem
python SKILL/scripts/setup_check.py ./my_problem
```
`PY` = 通过检查的 Python。在 Windows 无 key 且已安装中文桌面语音时，`auto` 优先使用离线配音；明确选择 `TTS_ENGINE=windows` 可保证不调用在线 TTS。

细胞机制样片可改用专用入口，它创建独立项目并复制模型，不改技能内示例：
```bash
PY SKILL/scripts/create_biology_demo.py --workspace WS --name cell-classroom-demo
PY SKILL/scripts/setup_check.py WS/cell-classroom-demo
```

- `new_video.sh` 会把 `pron.py`/`pron.json` 链接到技能自带的共享词表，并在找得到时把 `node_modules` 链接到已有安装（不复制）；找不到才需要在 `WS` 下 `npm install`。python 包用 `PY -m pip install --user numpy requests pypinyin pillow`。
- `new_video.sh` 报 `ERROR: ... is where the skill is installed` 说明你把 WS 设成了技能所在的项目，改用当前目录。
- 默认音色是 `chuichui`（锤锤），用户可以在 `.env` 里用 `GLM_VOICE` 换。
- 需要 GLM-TTS 而缺 `GLM_API_KEY` 时，按 [reference/glm-tts-setup.md](reference/glm-tts-setup.md) 引导配置（推荐放 `~/.config/math-problem-video/.env`）。**不要去别的项目找 `.env` 用，也不要因此换工作目录。** 用户选择免费配音或不想配 key：使用兜底引擎，`setup_check.sh` 会显示所选引擎；装 edge-tts 前先征得用户同意。
- **通过标准：** `setup_check.sh` 输出 `ALL OK`。

### 第 3 步：测试 TTS（验证 key 和音色）
```bash
cd PROJ && PY build_audio.py --say "我们一起看清这个过程。"
```
- 成功会打印 `WROTE build/say_xxxx.wav` 和 `voice: ...`（`edge:` / `say:` 开头 = 兜底引擎）。401/403 = key 错或没余额，告诉用户，不要重试 10 次。
- 首次选择音色时提供试听（音色表见 glm-tts-setup.md）；已有选择继续使用。
- **通过标准：** 生成了 wav。

### 第 4 步：准备题目图片 `problem.png` 和高亮框
解题课程执行本步；独立机制微课可以使用自己的概念示意，直接进入讲稿与分镜，不虚构题目证据。
二选一（细节见 [reference/animation.md](reference/animation.md#题目图片与高亮框)）：
- **只有文字**：`PY SKILL/scripts/make_problem_png.py --text "完整题目" --mark "条件1" "条件2" ... "所求" --out PROJ/problem.png`，它直接输出 `srcW/srcH/boxes`。
- **有截图**：复制到 `PROJ/`，必要时 `problem_boxes.py crop` 裁掉无关部分并存为 `problem.png`；然后 `problem_boxes.py grid` 出坐标网格图，读出每个条件的像素框；再 `problem_boxes.py check` 画框确认。
- 把尺寸和框填进 `anim.js` 顶部的 `PROBLEM`。
- **通过标准：** 你打开了 `*.preview.png` 或 `*.check.png`，文字完整（没有 ☒/□ 方框），每个框都恰好罩住对应文字。

### 第 5 步：写 `episode.json` 和 `script.json`
按 [reference/script-writing.md](reference/script-writing.md) 写。要点：
- `episode.json`：`title`（视频标题）、`output_name`（输出文件名，如 `斜边中线_Median_to_Hypotenuse`）、`pop_scenes`（要加"啵"音效的幕）；可选 `music_level` 是有限数字 `0..1`，默认 `1`，`0` 不生成背景音乐，保留旁白和配置音效。
- `motion_regions` 可省略，或写为含可选 `figure` / `board` 的对象；各值为 `[x,y,width,height]`，四个有限整数，坐标非负，宽高为正，必须在 1920×1080 内。未配置的区域使用原默认 `figure: [0,110,925,770]`、`board: [925,110,995,770]`。非法配置会在写时间轴或渲染前失败。细胞样片使用 `figure: [40,130,1840,736]`；区域只配置测量，不会自动排版或证明机制正确。
- `script.json`：幕的数组，每幕 `{"scene": "英文id", "lines": [{"zh","tts","en"}, ...]}`。开头提出问题并建立条件，结尾给出答案或机制结论，并安排适当迁移问题。
- 按 [reference/teaching-quality.md](reference/teaching-quality.md) 核对教学顺序。提问句可加 `pause_after` 留出思考时间；使用定理的句子可声明 `theorem`，列出条件、依据和结论，检查结果在 `build/teaching_report.txt`。这个检查只验证结构，数学仍需验算，条件仍须画进动画。
- 每句旁白 ≤ 36 个汉字宽（否则字幕折两行），一句只讲一件事。
- **通过标准：** JSON 合法；每一幕的 id 都有计划好的画面。

### 第 6 步：写分镜 `storyboard.md`
**先读 [reference/visual-design.md](reference/visual-design.md)**，再按 `template/storyboard.md` 的格式给每句旁白写一行：`| 幕id 句号 | 旁白要点 | 指 | 动 | 留 | 板书 |`。
- "指"：这句提到的元素怎么点亮。"动"：图上**一个**体现推理的动作，从动作表里选（相等→复制滑过去重合，全等→三角形叠上去，立体↔平面→相机转动，求长度→数字计数……）。"留"：动作后留下的标记。
- 除第一幕和最后一幕外，"动"不能空，也不能只写"出现/显示"。每幕至少一个连续运动。
- 先想清楚：只看图、不看板子，观众能不能看懂这一步为什么成立？不能就换动作。
- 先在 storyboard.md 顶部写**图形清单**：题目里所有的点、线段、平行/垂直/中点关系、已知长度，全部要画出来，位置按数据计算。
- 生物课的清单包含细胞类型、膜与细胞器、目标 ID、运输起终点、过程状态和示意说明；整体与局部来自同一模型。镜头先定位，再稳定展示机制。
- **通过标准：** 每句都有一行；图形清单完整；你能说出每一幕里"最能让人看懂"的那个动作。

### 第 7 步：读音与脚本检查，修到 0
```bash
cd PROJ && PY build_audio.py --check ; cat build/pron_report.txt
```
- `ERROR` 行：按提示改 `script.json`（通常是 tts 里有数字/符号，或 anim.js 缺 `SC.<id>`；第 8 步写完 anim.js 前后者会报错，属正常）。
- `⚠ 多音/生僻` 行：按 [reference/pronunciation.md](reference/pronunciation.md) 处理：该字后面加 `[拼音]`，或反复出现的词加进 `pron.json` 的 `words`，确认默认读音正确的词加进 `ok`。
- **通过标准：** `未固定读音的生僻字/多音字: 0` 且 `script errors: 0`，退出码 0。

### 第 8 步：写 `anim.js`
按 storyboard.md 逐句实现，API 见 [reference/animation.md](reference/animation.md)。先通读 `template/anim.js`（示例）再动手，结构保持一致：
- `PROBLEM`（第 4 步的数据）、`TAGS`（每幕左上角标签）、图形函数（如 `fig(st)`）、`SC.<id> = (lt, S) => {...}`（每幕一个）。
- 每个元素的出现时间 = 旁白提到它的时刻：`S.P(S.at(k, f), 时长)`。
- 每句：`glow(..., bump(lt, at(k)))` 点亮提到的元素 → 分镜里的动作（`slideSeg`、`movePoly`、`camTween`、动点、`countTo`…）→ 留下标记。
- 右侧 `board()` + `bl(行号, 文字, S.at(k, f), lt)` 逐行写推导（与图同色），最后 `stamp()` 盖章给答案。
- 生物课可让模型占主画面，标签跟随对应结构，文字仅保留必要名称和结论。复用模型时以 `BiologyModel.sample(time, cues)` 计算状态，`draw(ctx, state, time, viewport)` 绘制，`project(point, state, viewport)` 投影标注；示例用旁白时间点生成阶段 cues，保持同一目标与镜头连贯。
- **通过标准：** `PY build_audio.py --check` 无 ERROR。

### 第 9 步：免费预览：动作检查 + 版面检查
```bash
cd PROJ && PY build_audio.py --preview && node render.mjs motion && node render.mjs stills auto && PY SKILL/scripts/contact_sheet.py .
```
- `motion` 在每句里取 6 帧，比较 `episode.motion_regions` 的图形区（默认左半屏）：`STATIC`（没变化）必须修；每幕至少一句 `MOVE`。不通过就回到分镜换更好的动作，不要只加一个无意义的晃动来凑数。
- `stills auto` 在每句旁白快结束时截一帧（此时这句该出现的东西都应在画面上）。命令输出 `FAILED: page error` 说明 anim.js 有 JS 错误，先修。
- 打开 `build/sheet.png`（多于 12 张时是 `sheet_1.png`、`sheet_2.png`…）逐张检查，对照 [reference/animation.md 的审查清单](reference/animation.md#审查清单)：没有重叠、没有出界、没有挡住字幕、每句提到的东西都画出来了、数值与解答一致。
- 有问题 → 改 anim.js → 重跑本步。
- 生物机制逐项检查 [视觉与因果审查清单](reference/biology-visuals.md#视觉与因果审查清单)。包裹、闭合双膜自噬体、与溶酶体融合、内部降解必须可追踪；ROS 颗粒只能是示意。像素变化不能代替科学审查。
- **通过标准：** `motion check passed`；全部截图检查通过（在回复里逐幕说明你看到了什么）。

### 第 10 步：生成真实配音，再检查同步与画面
```bash
cd PROJ && PY build_audio.py && node render.mjs motion && node render.mjs stills auto && PY SKILL/scripts/contact_sheet.py .
```
- TTS 按文本缓存在 `build/tts/`，改了某句只会重新合成那一句。
- Windows 离线配音对待生成片段去重，并在每个批次中共用语音引擎；已匹配的 48 kHz 单声道 16-bit PCM 直接保存，不改变语音采样。
- 可选 `PY build_audio.py --asr` 会把配音发送到智谱识别服务，需有发送该内容的授权；选择离线流程时跳过，不因 key 存在就自动外传。已授权的检查结果写入 `build/asr_report.txt`；字母序列不匹配标 ✗，退出码 1，修正读音后再核对。没有运行识别时不得声称通过机器听写。
- 真实时长与预览不同，重新看一遍 sheet。
- **通过标准：** 打印 `mix + srt written`；真实时间轴的运动和截图检查通过；说明是否做过听写以及实际验证范围。提供试听，含字母点名和固定读音的词要重点核对。

### 第 11 步：渲染视频并交付
```bash
cd PROJ && node render.mjs video 6      # 6 = 并行浏览器页数（不是帧率！帧率固定 30）
```
- 输出 `WS/<output_name>.mp4` 和 `WS/<output_name>.srt`（WS = 用户的当前目录）。2~3 分钟的视频约需几分钟。
- 默认 x264 `fast`，保持 1080p、30 fps、CRF 18。完整导出成功后保存缓存；后续输入与成品哈希一致时打印 `CACHE HIT` 并复用 MP4。缓存不替代脚本、动作和画面检查。外部/动态资源或需要强制重新生成时用 `node render.mjs video 6 --fresh`；`--preset medium` 可选择原压缩设置。边界与旧项目升级见 [reference/performance.md](reference/performance.md)。
- 交付时告诉用户：mp4/srt 路径、实际时长、各幕内容和实际验证范围。提供可播放的成品；未核对的音频读音不要宣称已验证。用户反馈读错时：加到 `pron.json` 或行内标注 → 再跑第 10、11 步（只会重合成改过的句子）。

## 常见错误（真实发生过）

| 错误做法 | 正确做法 |
|---|---|
| 当前目录没有 `.env`/`node_modules`，就把项目建到有这些东西的别的目录（例如技能所在的项目） | WS 永远是用户当前目录；缺依赖由 new_video.sh 链接，缺 key 请用户配置 `~/.config/math-problem-video/.env` |
| 从别的视频文件夹（化学 chem 等）复制代码 | 用 `new_video.sh` 从本技能 `template/` 建项目 |
| 编造 `GLM_MODEL=glm-4-voice`、`api.zhipuai.cn` 等配置 | 模型只有 `glm-tts`，地址已写在 build_audio.py；只需用户提供 `GLM_API_KEY`，可选 `GLM_VOICE` |
| `node render.mjs video 24` 以为是 24fps | 参数是并行数；预览版面用 `stills auto`，不要反复渲染整段视频 |
| `中点[zhōng]` | 标注只作用于紧挨着的前一个字：`中[zhōng]点`（其实"中点"不需要标） |
| tts 里写 `AC=3`、`60 − 7t`、`x²` | `AC等于三`、`六十减七t`、`x的平方` |
| 题目截图随便放在 (50,50) 400×400 | 用 `PROBLEM` + `problemCard()` 自动适配到标题下方的卡片里 |
| 用绝对秒数定时 `if (lt > 12.5)` | `S.at(k, f)`：第 k 句开始后 f 比例处 |
| 渲染完不看画面就交付 | 每次都看 `build/sheet.png` |
| tts 里手动写 `C、O` 或 `C,O` 来分开字母 | 不用管：pron.py 自动把相邻字母拆成 `C O`（实测逗号、顿号会多出停顿） |
| `--check` 还有 ⚠ 就调 TTS | 修到 0；否则会花钱合成出错误读音 |
| 为了"保险"把常见词都加进 `pron.json` 或行内标注 | 只标会读错的字；替换成同音字会破坏断句（`直搅三搅形`），`pron.py` 已经只在上下文会读错时才替换 |
| 一个分句二十多个字不加标点 | 在换气处加逗号，分句 ≤ 18 字（`--check` 会 warn），否则 TTS 自己在词中间停 |
| 题目图片里 `x²` 显示成 `x☒` 却没发现 | 审查时放大看文字；make_problem_png.py 已自动换字体 |
| 用编辑工具改 JSON 后出现弯引号 `“`，解析失败 | JSON 语法引号必须是英文 `"`；见 troubleshooting.md |
| 图一次画好，之后每句只多一条线/一个标签，解释全在板子上 | 每句都有"指→动→留"；相等就滑过去重合，立体↔俯视用 `camTween`；`render.mjs motion` 必须通过 |
| 需要俯视图时在旁边另画一张图 | 同一个 3D 模型 `camTween` 转到 pitch = π/2 |
| 一句旁白塞三四个知识点 | 一句一个点，画面同步出现一个元素 |

## 参考文件
- [reference/performance.md](reference/performance.md)：配音与视频提速、缓存范围、强制重建、实测条件与旧项目升级。
- [reference/glm-tts-setup.md](reference/glm-tts-setup.md)：智谱 GLM-TTS 注册、API Key、`.env`、音色、语速、报错处理。**引导用户配置时读这个。**
- [reference/teaching-quality.md](reference/teaching-quality.md)：条件检查、思考停顿、迁移练习与动画教学审阅。
- [reference/biology-visuals.md](reference/biology-visuals.md)：细胞模型差异、连续镜头、自噬顺序、示意与证据边界、视觉因果审查。做生物机制课时必读。
- [reference/script-writing.md](reference/script-writing.md)：`script.json` 格式、幕的设计、数学式子的口语写法对照表。
- [reference/pronunciation.md](reference/pronunciation.md)：读音控制原理、标注语法、`pron.json`、数学常见多音字。
- [reference/visual-design.md](reference/visual-design.md)：**讲解动画怎么设计**：指→动→留→连、推理→动画动作表、立体转俯视、圆锥展开、分镜格式。写分镜前必读。
- [reference/animation.md](reference/animation.md)：engine.js API、场景写法、版面坐标、几何/函数/立体/行程题画法、审查清单。
- [reference/troubleshooting.md](reference/troubleshooting.md)：报错与处理。
