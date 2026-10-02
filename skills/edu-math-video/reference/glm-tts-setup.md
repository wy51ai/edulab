# GLM-TTS 配置（智谱开放平台）

配音用智谱 **GLM-TTS**。调用代码已经写好在 `build_audio.py` 的 `tts()` 里，**只需要用户提供 API Key**（音色可选）。不要改接口地址、模型名，也不要换别的 TTS。

## 固定参数（已写在代码里，仅供核对）

| 项 | 值 |
|---|---|
| 接口 | `POST https://open.bigmodel.cn/api/paas/v4/audio/speech` |
| 认证 | Header `Authorization: Bearer <GLM_API_KEY>` |
| model | `glm-tts`（唯一可选值） |
| input | 要读的文本，**最长 1024 字符** |
| voice | `chuichui`（锤锤，默认）、`tongtong`（彤彤）、`xiaochen`（小陈）、`jam`、`kazi`、`douji`、`luodo`（动动动物圈系列）；也可以是用户的复刻音色 id |
| speed | 0.5 ~ 2，默认 1.0；本流水线用 1.05（`GLM_SPEED` 可改） |
| response_format | `wav`（返回 24kHz，代码会转成 48kHz 并去掉元数据） |
| watermark_enabled | `false`（只有用户在控制台开通了"去水印"才生效，否则仍带水印，不影响使用） |

**没有** SSML、拼音、音素、情感标签输入。行内拼音会被直接念出来，所以读音控制靠 `pron.py` 换同音字（见 pronunciation.md）。

## 引导用户配置（缺 key 时照这个跟用户说）

发给用户的话可以这样写（按需要改写）：

> 配音使用智谱 GLM-TTS，需要你的 API Key：
> 1. 打开 https://bigmodel.cn 注册/登录（手机号即可）。
> 2. 进入 https://bigmodel.cn/usercenter/proj-mgmt/apikeys ，点"添加新的 API Key"，复制它。
> 3. 确认账户有余额或可用资源包（TTS 按调用计费，价格以控制台为准）。
> 4. 把 key 写进 `~/.config/math-problem-video/.env`（所有目录都能用；没有就新建）：
>    ```
>    mkdir -p ~/.config/math-problem-video
>    cat >> ~/.config/math-problem-video/.env <<'EOF'
>    GLM_API_KEY=你复制的key
>    GLM_VOICE=chuichui
>    EOF
>    chmod 600 ~/.config/math-problem-video/.env
>    ```
>    （也可以只给某个工作目录配置：写进 `<WS>/.env`。）
>    `GLM_VOICE` 可选：chuichui（锤锤，默认）、tongtong（彤彤，女声）、xiaochen（小陈，男声）等。
> 5. （可选）不想要 AI 水印：控制台右上角 个人中心 → 安全管理 → 去水印管理 → 打开开关。
>
> 配好告诉我，我先合成一句测试音给你听。

规则：
- **让用户自己把 key 写进 `~/.config/math-problem-video/.env`（或 `<WS>/.env`）**。如果用户直接把 key 发给你，可以替他写进去，但不要在回复里复述 key，不要写进视频文件夹、脚本或任何会被分享的文件。
- 查找顺序：环境变量 `GLM_API_KEY` / `GLM_VOICE` / `GLM_SPEED` > 项目往上最近的 `.env` > `~/.config/math-problem-video/.env`。
- **不要从别的项目目录拷贝或读取 `.env`**，也不要为了用到别处的 key 而把视频建在别的目录。
- 如果 `WS` 是 git 仓库，确认 `.gitignore` 里有 `.env`，没有就加上。
- 不要把 key 写死在 `build_audio.py` 里。

## 验证

```bash
bash SKILL/scripts/setup_check.sh PROJ                 # 应显示 OK GLM_API_KEY ... (value not shown)
cd PROJ && PY build_audio.py --say "你好，我们来看一道数学题。"
```
成功：`WROTE .../build/say_xxxxxxxx.wav`。把路径发给用户试听音色。

## 报错对照

| 现象 | 原因 | 处理 |
|---|---|---|
| `GLM_API_KEY is missing` | 没配 key | 按上面引导用户 |
| `TTS failed (401)` | key 错误/失效/复制不全 | 请用户重新复制 key |
| `TTS failed (403)` 或提示余额不足 | 账户欠费/无权限 | 请用户充值或检查资源包 |
| `TTS failed (400)` | 文本超长或参数错误；voice 名写错 | 检查 tts 文本长度（<1024）、`GLM_VOICE` 拼写 |
| `TTS failed (429)` / 连续超时 | 并发或频率限制 | 等一会重跑（已合成的句子有缓存，不会重复计费） |
| 读音不对 | TTS 自己猜读音 | 见 pronunciation.md，改完只重合成那一句 |

## 没有 GLM key 时：兜底引擎

`build_audio.py` 用 `TTS_ENGINE` 选择配音引擎（写在 `.env` 或环境变量里），默认 `auto`：有 `GLM_API_KEY` 用 GLM，否则装了 edge-tts 用 edge，否则在 macOS 上用 `say`。

| 引擎 | 需要什么 | 音质 | 音色变量（默认） |
|---|---|---|---|
| `glm` | `GLM_API_KEY`（付费） | 最好，唯一支持 `--asr` 核对 | `GLM_VOICE`（chuichui） |
| `edge` | `PY -m pip install --user edge-tts`，联网；免费、无需 key（微软 Edge 朗读接口，非官方，可能失效） | 接近 GLM | `EDGE_VOICE`（zh-CN-XiaoxiaoNeural；男声 zh-CN-YunxiNeural） |
| `say` | macOS 自带，离线，什么都不用装 | 机械感明显，只适合预览/内部用 | `SAY_VOICE`（Tingting，其他中文音色读不了字母） |

- **装 edge-tts 前先问用户。**
- 语速都跟 `GLM_SPEED` 走。缓存按引擎+音色分开，换引擎会重新合成。
- 字母：GLM/edge 用空格分开（`P A B`）；`say` 的 Tingting 会吞掉空格分开的字母，所以 `say` 引擎自动改用顿号（`P、A、B`，ASR 实测逐个读对，代价是字母间有小停顿）。
- 没有 GLM key 时 `--asr` 会跳过（`ASR SKIPPED`）：交付时告诉用户字母读音没有机器核对。
- 用了兜底引擎，交付时要告诉用户用的是哪个引擎，以及配置 GLM key 后重跑第 10、11 步即可换成 GLM 配音。

## 换音色 / 语速

改 `.env` 的 `GLM_VOICE` 或 `GLM_SPEED`，重跑 `PY build_audio.py`。缓存文件名包含音色和语速，所以会全部重新合成（会产生费用，先告诉用户）。

## Windows 免费离线配音

Windows 已安装中文**桌面语音**时（如 Microsoft Yaoyao/Huihui），无 GLM key 的 `TTS_ENGINE=auto` 优先使用它，语音由本机 `System.Speech` 合成。无需 edge-tts 或网络；没有中文桌面语音时到 Windows 设置的“时间和语言 → 语音”安装。可先查看列表：

```powershell
python -c "import sys; sys.path.insert(0, 'PROJ'); import windows_tts; print(windows_tts.list_voices())"
$env:TTS_ENGINE = 'windows'
$env:WINDOWS_VOICE = 'Microsoft Yaoyao Desktop' # 按列表中的完整名称填写；省略时用第一个中文语音
python PROJ/build_audio.py --say '你好，我们来看一道数学题。'
```

`GLM_SPEED` 仍控制速度，Windows 映射为系统语速。`TTS_TIMEOUT` 为每次合成的超时秒数，默认 120；Edge 最多尝试三次，每次均有这个上限。不会在合成失败后静默切换到另一服务。GLM/Edge 会将旁白发送给相应服务；Windows/say 均离线。

`ffmpeg-static` 的 Windows `ffmpeg.exe` 会自动发现。也可在环境或 `.env` 中设置 `FFMPEG_BINARY` 为实际文件的绝对路径；渲染器读取的是**进程环境**中的同名变量（不加载 `.env`）。

```powershell
$env:FFMPEG_BINARY = 'C:/tools/ffmpeg/bin/ffmpeg.exe'
```

没有 GLM key 时 `--asr` 仍会明确跳过，字母与中文读音需人工试听。`python SKILL/scripts/setup_check.py PROJ` 可在所有平台检查依赖、浏览器和实际配音选择，而不发送旁白。
