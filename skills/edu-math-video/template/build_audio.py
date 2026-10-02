"""Narration + music + subtitles for one video.

  PY build_audio.py --check      lint script.json + pronunciation report (build/pron_report.txt). No API calls.
                                 Must print "未固定读音...: 0" and "script errors: 0" before anything else.
  PY build_audio.py --preview    no API calls: estimated line durations -> build/timeline.json (preview_only),
                                 so `node render.mjs stills auto` can check layout before paying for TTS.
  PY build_audio.py --say "文本"  one TTS clip -> build/say_<hash>.wav (API-key test / audition a reading),
                                 then speech recognition prints what was actually heard
  PY build_audio.py --asr        after the real run: speech-recognise every clip (GLM-ASR, cached in build/asr.json)
                                 -> build/asr_report.txt; lines whose LETTER sequence (AB, CD, t ...) differs from
                                 the script are flagged (e.g. "CO" heard as 口)
  PY build_audio.py              real run: GLM-TTS for every line (cached by text in build/tts/), timeline,
                                 music + SFX, mix.wav, ../<output_name>.srt

PY = a python3 that has numpy, requests, pypinyin (on macOS usually /usr/bin/python3).
GLM_API_KEY / GLM_VOICE come from the environment, the nearest .env above this folder, or
~/.config/math-problem-video/.env (user-level, shared by all workspaces).

TTS engine (TTS_ENGINE=auto|glm|windows|edge|say):
  glm   GLM-TTS, needs GLM_API_KEY. Best quality; the only engine with --asr checking.
  windows  Windows installed desktop voices, offline (WINDOWS_VOICE, default first Chinese voice).
           Preferred over edge when auto has no GLM key on Windows.
  edge  fallback: Microsoft Edge neural voices via `pip install edge-tts`, free, no key, needs internet
        (EDGE_VOICE, default zh-CN-XiaoxiaoNeural)
  say   last resort: macOS built-in `say`, offline, robotic (SAY_VOICE, default Tingting: the other zh voices
        cannot read Latin letters)
"""
import hashlib, json, math, os, re, shutil, struct, subprocess, sys, wave
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import requests
from audio_math import box_mean, get_music_level
from audio_io import to_pcm_wav
from teaching import check_teaching
import windows_tts

ROOT = os.path.dirname(os.path.abspath(__file__))


def _find_up(name):
    """Nearest ancestor directory (including ROOT) that contains `name`, else None."""
    d = ROOT
    while True:
        if os.path.exists(os.path.join(d, name)):
            return d
        if os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)


def _find_ff():
    explicit = ENV.get("FFMPEG_BINARY")
    if explicit:
        binary = os.path.abspath(os.path.expanduser(explicit))
        if os.path.isfile(binary):
            return binary
        raise SystemExit(f"FFMPEG_BINARY does not point to a file: {binary}")
    d = _find_up("node_modules/ffmpeg-static/ffmpeg.exe")
    if d:
        return os.path.join(d, "node_modules/ffmpeg-static/ffmpeg.exe")
    d = _find_up("node_modules/ffmpeg-static/ffmpeg")  # shared node_modules at the workspace root
    if d:
        return os.path.join(d, "node_modules/ffmpeg-static/ffmpeg")
    if shutil.which("ffmpeg"):
        return shutil.which("ffmpeg")
    raise SystemExit("ffmpeg not found: run `npm install playwright@1.49 ffmpeg-static` in the workspace root.")


_pron_dir = _find_up("pron.py")
if not _pron_dir:
    raise SystemExit("pron.py not found in this folder or any parent. Copy shared/pron.py + shared/pron.json "
                     "from the edu-math-video skill to the workspace root.")
sys.path.insert(0, _pron_dir)
import pron  # noqa: E402  shared pronunciation control (<workspace>/pron.py + pron.json)

BUILD = os.path.join(ROOT, "build")
TTS_DIR = os.path.join(BUILD, "tts")
os.makedirs(TTS_DIR, exist_ok=True)
SR = 48000


USER_ENV = os.path.expanduser("~/.config/math-problem-video/.env")  # one key for every workspace


def load_env():
    """Priority: environment variables > nearest .env above the project > ~/.config/math-problem-video/.env"""
    env = {}
    d = _find_up(".env")
    for f in [USER_ENV] + ([os.path.join(d, ".env")] if d else []):  # later files override earlier ones
        if not os.path.exists(f):
            continue
        for line in open(f, encoding="utf-8"):
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k.strip()] = v.strip().strip("\"'")
    for key in ("GLM_API_KEY", "GLM_VOICE", "GLM_SPEED", "TTS_ENGINE", "EDGE_VOICE", "SAY_VOICE",
                "WINDOWS_VOICE", "TTS_TIMEOUT", "FFMPEG_BINARY"):
        if os.environ.get(key):
            env[key] = os.environ[key]
    return env


ENV = load_env()
FF = _find_ff()
VOICES = ("tongtong", "chuichui", "xiaochen", "jam", "kazi", "douji", "luodo")
SPEED = float(ENV.get("GLM_SPEED", "1.05"))
TTS_TIMEOUT = float(ENV.get("TTS_TIMEOUT", "120"))
if not math.isfinite(SPEED) or SPEED <= 0 or not math.isfinite(TTS_TIMEOUT) or TTS_TIMEOUT <= 0:
    raise SystemExit("GLM_SPEED and TTS_TIMEOUT must be positive finite numbers")


def _has_edge():
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        return False


def pick_engine():
    want = ENV.get("TTS_ENGINE", "auto").lower()
    if want != "auto":
        return want
    if ENV.get("GLM_API_KEY"):
        return "glm"
    if os.name == "nt":
        try:
            windows_tts.choose_voice(ENV.get("WINDOWS_VOICE", ""))
            return "windows"
        except RuntimeError:
            if ENV.get("WINDOWS_VOICE"):
                raise  # do not silently replace a specifically requested voice
    if _has_edge():
        return "edge"
    if shutil.which("say"):
        return "say"
    return "glm"  # nothing available: need_key() explains what to set up


ENGINE = pick_engine()
# VOICE also keys the TTS cache, so each engine gets its own clips (GLM keeps the plain voice name: old caches stay valid)
VOICE = {"glm": ENV.get("GLM_VOICE", "chuichui"),
         "edge": "edge:" + ENV.get("EDGE_VOICE", "zh-CN-XiaoxiaoNeural"),
         "say": "say:" + ENV.get("SAY_VOICE", "Tingting")}.get(ENGINE)
if ENGINE == "windows":
    VOICE = "windows:" + windows_tts.choose_voice(ENV.get("WINDOWS_VOICE", ""))
if VOICE is None:
    raise SystemExit(f"TTS_ENGINE={ENGINE!r}: use auto, glm, windows, edge or say")
LETTER_SEP = "、" if ENGINE == "say" else " "  # see pron.to_tts
EPISODE = json.load(open(os.path.join(ROOT, "episode.json"), encoding="utf-8"))
MUSIC_LEVEL = get_music_level(EPISODE)
OUT_NAME = EPISODE["output_name"]
POP_SCENES = set(EPISODE.get("pop_scenes", []))  # scenes whose lines each get a soft "pop" SFX
TRANSPOSE = 5  # D major, bright and bouncy


def strip_wav(raw: bytes) -> bytes:
    """Keep only fmt + data chunks (drops AIGC / LIST metadata watermark chunks)."""
    i, fmt, data = 12, None, None
    while i < len(raw) - 8:
        cid = raw[i:i + 4]
        sz = struct.unpack("<I", raw[i + 4:i + 8])[0]
        if cid == b"fmt ":
            fmt = raw[i + 8:i + 8 + sz]
        elif cid == b"data":
            data = raw[i + 8:i + 8 + sz]
        i += 8 + sz + (sz & 1)
    assert fmt and data, "bad wav"
    body = b"fmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
    return b"RIFF" + struct.pack("<I", 4 + len(body)) + b"WAVE" + body


def _to_wav(src, out):
    """Any audio file -> 48 kHz mono wav without metadata."""
    to_pcm_wav(src, out, FF, SR)


def tts_windows_batch(jobs):
    raw = [(text, out + ".raw.wav") for text, out in jobs]
    try:
        windows_tts.synthesize_many(raw, VOICE.split(":", 1)[1], SPEED,
                                    timeout=TTS_TIMEOUT * len(raw))
        for (_, source), (_, output) in zip(raw, jobs):
            _to_wav(source, output)
    finally:
        for _, source in raw:
            if os.path.exists(source):
                os.remove(source)


def tts_edge(text, out):
    import asyncio
    import edge_tts
    tmp = out + ".mp3"
    rate = f"{round((SPEED - 1) * 100):+d}%"
    for attempt in range(3):
        try:
            async def bounded_save():
                await asyncio.wait_for(edge_tts.Communicate(text, VOICE.split(":", 1)[1], rate=rate).save(tmp),
                                       timeout=TTS_TIMEOUT)
            asyncio.run(bounded_save())
            return _to_wav(tmp, out)
        except Exception as e:  # network hiccups: the service is free but unofficial
            if os.path.exists(tmp):
                os.remove(tmp)
            print("edge-tts retry", attempt, e, file=sys.stderr)
    raise RuntimeError(f"edge-tts failed  text: {text}")


def tts_say(text, out):
    tmp = out + ".aiff"
    # `say` rate is words per minute; ~190 matches GLM's pace for Chinese at speed 1.0
    subprocess.run(["say", "-v", VOICE.split(":", 1)[1], "-r", str(round(190 * SPEED)), "-o", tmp, text],
                   check=True, timeout=TTS_TIMEOUT)
    _to_wav(tmp, out)


def tts(text: str, out: str):
    if os.path.exists(out):
        return
    if ENGINE == "edge":
        return tts_edge(text, out)
    if ENGINE == "say":
        return tts_say(text, out)
    if ENGINE == "windows":
        tmp = out + ".raw.wav"
        try:
            windows_tts.synthesize(text, tmp, VOICE.split(":", 1)[1], SPEED, timeout=TTS_TIMEOUT)
            return _to_wav(tmp, out)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    for attempt in range(4):
        r = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/audio/speech",
            headers={"Authorization": f"Bearer {ENV['GLM_API_KEY']}"},
            json={"model": "glm-tts", "input": text, "voice": VOICE, "response_format": "wav",
                  "speed": SPEED, "watermark_enabled": False},
            timeout=TTS_TIMEOUT,
        )
        if r.status_code == 200 and r.content[:4] == b"RIFF":
            tmp = out + ".raw.wav"
            open(tmp, "wb").write(strip_wav(r.content))
            return _to_wav(tmp, out)  # resample to 48k, drop all metadata
        print("TTS retry", attempt, r.status_code, r.text[:300], file=sys.stderr)
        if r.status_code in (400, 401, 403):  # bad key / bad request / no balance: retrying will not help
            break
    raise RuntimeError(f"TTS failed ({r.status_code}): {r.text[:300]}  text: {text}")


def asr(path):
    """Speech recognition of one clip with GLM-ASR (same key). Cached by file name in build/asr.json."""
    cache_f = os.path.join(BUILD, "asr.json")
    cache = json.load(open(cache_f, encoding="utf-8")) if os.path.exists(cache_f) else {}
    k = os.path.basename(path)
    if k not in cache:
        r = requests.post("https://open.bigmodel.cn/api/paas/v4/audio/transcriptions",
                          headers={"Authorization": f"Bearer {ENV['GLM_API_KEY']}"},
                          files={"file": (k, open(path, "rb"), "audio/wav")},
                          data={"model": "glm-asr-2512", "stream": "false"}, timeout=120)
        if r.status_code != 200:
            return f"<ASR failed {r.status_code}: {r.text[:120]}>"
        cache[k] = r.json().get("text", "")
        json.dump(cache, open(cache_f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return cache[k]


def letters(s):
    # the recogniser itself confuses T/D and M/N (tested: a clear "T" comes back as "D"), so treat them as equal
    return re.sub(r"[^A-Z]", "", s.upper()).translate(str.maketrans("DN", "TM"))


def read_wav(path):
    with wave.open(path) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    return a


def trim(a, thr=0.004):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    s = max(0, idx[0] - int(0.03 * SR))
    e = min(len(a), idx[-1] + int(0.08 * SR))
    return a[s:e]


# ---------------------------------------------------------------- music synth
def midi_hz(m):
    return 440.0 * 2 ** ((m + TRANSPOSE - 69) / 12)


def pluck(f, dur, amp=1.0, bright=1.0):
    t = np.arange(int(dur * SR)) / SR
    y = np.zeros_like(t)
    for k in range(1, 9):
        if f * k > SR / 2.2:
            break
        y += (bright ** (k - 1)) / k * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.5 + 2.2 * k))
    att = np.minimum(1, t / 0.004)
    return amp * y * att


def bell(f, dur, amp=1.0):
    t = np.arange(int(dur * SR)) / SR
    y = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
         + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 12))
    return amp * y * np.exp(-t * 3.2) * np.minimum(1, t / 0.002)


def bass(f, dur, amp=1.0):
    t = np.arange(int(dur * SR)) / SR
    y = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) + 0.08 * np.sin(2 * np.pi * 3 * f * t)
    env = np.minimum(1, t / 0.01) * np.exp(-t * 2.0)
    return amp * y * env


RNG = np.random.default_rng(7)


def kick(amp=1.0):
    t = np.arange(int(0.25 * SR)) / SR
    f = 50 + 90 * np.exp(-t * 35)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(ph) * np.exp(-t * 14)


def shaker(amp=1.0):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    x = RNG.standard_normal(n)
    x = np.diff(x, prepend=0)  # crude highpass
    return amp * x * np.exp(-t * 70) * np.minimum(1, t / 0.004)


def clap(amp=1.0):
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    x = RNG.standard_normal(n)
    x = x - np.convolve(x, np.ones(8) / 8, mode="same")
    env = np.exp(-t * 28) + 0.6 * np.exp(-np.maximum(0, t - 0.012) * 40) * (t > 0.012)
    return amp * x * env


def add(buf, sig, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def make_music(total):
    bpm = 92
    beat = 60 / bpm
    bar = beat * 4
    L = int((total + 2) * SR)
    mus = np.zeros(L, np.float32)
    # C  G  Am  F  |  F  G  Em  Am  (ukulele-pop loop)
    prog = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72]),
            (41, [60, 65, 69, 72]), (43, [59, 62, 67, 74]), (40, [59, 64, 67, 71]), (45, [60, 64, 69, 76])]
    melody = [  # (beat offset within 2-bar phrase, midi, beats)
        [(0, 76, 1), (1, 79, 1), (2, 81, .5), (2.5, 79, .5), (3, 76, 1), (4.5, 74, .5), (5, 76, 1), (6, 72, 2)],
        [(0, 72, 1), (1, 74, 1), (2, 76, .5), (2.5, 74, .5), (3, 72, 1), (4, 69, 1), (5, 71, 1), (6, 67, 2)],
        [(0, 81, .5), (.5, 79, .5), (1, 76, 1), (2, 79, 1), (3, 84, 1), (4.5, 83, .5), (5, 81, 1), (6, 79, 2)],
        [(0, 77, 1), (1, 76, 1), (2, 74, 1), (3, 72, 1), (4, 71, 1), (5, 74, 1), (6, 72, 2)],
    ]
    nbars = int(total / bar) + 1
    for b in range(nbars):
        t0 = b * bar
        root, ch = prog[b % len(prog)]
        final = b >= nbars - 1
        intro = b < 2
        # arpeggio pluck: 8ths pattern
        pat = [0, 2, 1, 3, 2, 1, 3, 2]
        for k in range(8):
            if final and k > 0:
                break
            n = ch[pat[k]]
            add(mus, pluck(midi_hz(n), 1.2, 0.16 if k % 2 == 0 else 0.11, 0.55), t0 + k * beat / 2)
        # chord strum on 1 (slight spread)
        for i, n in enumerate(ch[:3]):
            add(mus, pluck(midi_hz(n - 12), 2.4 if final else 1.6, 0.08, 0.7), t0 + i * 0.018)
        if intro:
            continue
        # bass
        for off, mul in [(0, 1), (1.5, 1), (2, 1), (3.5, 1)]:
            if final and off > 0:
                break
            add(mus, bass(midi_hz(root - 12 if root > 44 else root), beat * 1.2, 0.30), t0 + off * beat)
        if final:
            add(mus, bell(midi_hz(84), 3.0, 0.12), t0)
            continue
        # drums
        add(mus, kick(0.35), t0)
        add(mus, kick(0.28), t0 + 2 * beat)
        add(mus, clap(0.10), t0 + beat)
        add(mus, clap(0.10), t0 + 3 * beat)
        for s in range(8):
            add(mus, shaker(0.05 if s % 2 else 0.028), t0 + s * beat / 2)
        # bells melody every other 8-bar block
        blk = (b - 2) // 8
        if blk % 2 == 1 or b < 10:
            ph = melody[((b - 2) // 2) % len(melody)]
            half = (b - 2) % 2
            for off, m, d in ph:
                if (off >= 4) == bool(half):
                    add(mus, bell(midi_hz(m), max(0.4, d * beat * 1.6), 0.055), t0 + (off - 4 * half) * beat)
    # fade out tail
    fo = int(3.0 * SR)
    end = int(total * SR)
    mus[end - fo:end] *= np.linspace(1, 0, fo)
    mus[end:] = 0
    # a touch of "room": simple feedback echo
    d = int(beat * 0.75 * SR)
    wet = np.zeros_like(mus)
    wet[d:] += mus[:-d] * 0.22
    wet[2 * d:] += mus[:-2 * d] * 0.08
    return (mus + wet)[: int(total * SR)]


def whoosh(dur=0.9, amp=0.25):
    n = int(dur * SR)
    x = RNG.standard_normal(n)
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(n, 1 / SR)
    lo = np.fft.irfft(X * np.exp(-((fr - 500) / 400) ** 2), n)
    hi = np.fft.irfft(X * np.exp(-((fr - 2600) / 1500) ** 2), n)
    t = np.linspace(0, 1, n)
    mixv = np.sin(np.pi * t)  # sweep up then down
    y = lo * (1 - mixv) + hi * mixv
    env = np.sin(np.pi * t) ** 1.6
    y = y * env
    return amp * y / (np.abs(y).max() + 1e-9)


def pop(amp=0.18):
    t = np.arange(int(0.12 * SR)) / SR
    f = 350 + 900 * np.exp(-t * 45)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(ph) * np.exp(-t * 30)


SUBS = str.maketrans("0123456789+-", "₀₁₂₃₄₅₆₇₈₉₊₋")
SUPS = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")


def plain(s):
    """H_2SO_4 / OH^- markup (drawn as real sub/superscripts on canvas) -> Unicode for the SRT."""
    s = re.sub(r"_(\d)", lambda m: m[1].translate(SUBS), s)
    return re.sub(r"\^([0-9+\-]+)", lambda m: m[1].translate(SUPS), s)


def srt_time(s):
    ms = int(round(s * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"




# ---------------------------------------------------------------- script lint
# The `tts` text is what GLM-TTS reads. Digits, formulas and symbols get read unpredictably (or skipped),
# so they must be written out as speakable Chinese: "AB等于五", "三的平方", "二点五", "六十分之七t".
TTS_BAD = re.compile(r"[0-9=+\-−×÷*/^_√∠△∥⊥°%²³<>≤≥≠≈∽≌∈∉⊂∪∩∞π±·•→⇒∴∵|{}\[\]()（）]")
LOWER_RUN = re.compile(r"[a-z]{2,}")  # sin, cos, log, max ... TTS spells or mangles them
CLAUSE_SPLIT = re.compile(r"[，。、；：！？,.!?:;…—]+")
MAX_CLAUSE = 18  # longer runs without punctuation: GLM-TTS picks its own break, often mid-word


def vis_width(s):
    """Approximate subtitle width in Chinese-character units (ASCII ≈ 0.55)."""
    return sum(1 if ord(c) > 0x2E80 else 0.55 for c in s)


def lint_script(script):
    errors, warns = [], []
    anim = open(os.path.join(ROOT, "anim.js"), encoding="utf-8").read()
    sc_ids = set(re.findall(r"SC\.(\w+)\s*=", anim))
    tags_block = re.search(r"const TAGS\s*=\s*\{(.*?)\n\};", anim, re.S)
    tag_ids = set(re.findall(r"^\s*(\w+)\s*:", tags_block.group(1), re.M)) if tags_block else set()
    seen = set()
    for sc in script:
        sid = sc.get("scene")
        if not sid or not re.fullmatch(r"[A-Za-z_]\w*", sid):
            errors.append(f"scene id {sid!r} must be a plain identifier (letters, digits, _)")
            continue
        if sid in seen:
            errors.append(f"[{sid}] duplicate scene id")
        seen.add(sid)
        if sid not in sc_ids:
            errors.append(f"[{sid}] anim.js has no SC.{sid} = (lt, S) => {{...}}")
        if sid not in tag_ids:
            warns.append(f"[{sid}] no TAGS entry in anim.js (no top-left scene tag)")
        if not sc.get("lines"):
            errors.append(f"[{sid}] has no lines")
        for li, ln in enumerate(sc.get("lines", [])):
            where = f"[{sid} {li}]"
            for k in ("zh", "en"):
                if not ln.get(k, "").strip():
                    errors.append(f"{where} missing '{k}'")
            spoken = pron.strip(ln.get("tts", ln.get("zh", "")))
            bad = sorted(set(TTS_BAD.findall(spoken)))
            if bad:
                errors.append(f"{where} tts text has {' '.join(bad)} -> write it as spoken Chinese in 'tts': {spoken}")
            for cl in CLAUSE_SPLIT.split(spoken):
                if len(re.sub(r"\s", "", cl)) > MAX_CLAUSE:
                    warns.append(f"{where} clause without punctuation > {MAX_CLAUSE} chars, TTS may break it anywhere: "
                                 f"add a comma where you would breathe: {cl}")
            low = LOWER_RUN.findall(spoken)
            if low:
                warns.append(f"{where} tts has latin words {low}: say them in Chinese (sin -> 正弦) or check by ear")
            if len(pron.to_tts(ln.get("tts", ln.get("zh", "")))[0]) > 1000:
                errors.append(f"{where} tts text > 1000 chars (GLM-TTS limit 1024): split the line")
            zw = vis_width(pron.strip(ln.get("zh", "")))
            if zw > 36:
                warns.append(f"{where} zh subtitle ≈{zw:.0f} chars wide -> wraps to 2 lines (box top rises to y≈860); "
                             "prefer splitting into two lines")
            if len(ln.get("en", "")) > 95:
                warns.append(f"{where} en subtitle {len(ln['en'])} chars -> wraps; shorten it")
    teaching_errors, _ = check_teaching(script)
    errors += teaching_errors
    errors += lint_storyboard(script)
    return errors, warns


NO_ACTION = {"", "-", "—", "无", "none", "n/a", "同上"}
NO_ACTION_RE = re.compile(r"\s*(无|没有|不动|保持|同上|none|no\b|n/a|—|-)", re.I)
HIGHLIGHT_ONLY = re.compile(r"glow|闪|高亮|脉冲|亮起|pulse|highlight|出现|显示|标出", re.I)
MOTION_WORDS = re.compile(r"滑|移|转|旋|放大|缩|展开|剪开|落|长出|画出|生长|数到|计数|飞|拖|折|滚|扫|叠|铺|变形|沿|运动|来回|拼", re.I)


def lint_storyboard(script):
    """storyboard.md must plan a figure action for every narration line (first and last scene may use —)."""
    path = os.path.join(ROOT, "storyboard.md")
    if not os.path.exists(path):
        return ["storyboard.md missing: write the per-line storyboard first (reference/visual-design.md)"]
    rows, act = {}, None
    for line in open(path, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.lstrip().startswith("|") or len(cells) < 3:
            continue
        if act is None and any(c.startswith("动") for c in cells):
            act = next(i for i, c in enumerate(cells) if c.startswith("动"))
            continue
        if act is not None and act < len(cells):
            rows[re.sub(r"\s+", " ", cells[0])] = cells[act]
    if act is None:
        return ["storyboard.md: table header needs a column named 动 (the figure action)"]
    errs, first, last = [], script[0]["scene"], script[-1]["scene"]
    for sc in script:
        for li, _ in enumerate(sc["lines"]):
            key = f"{sc['scene']} {li}"
            if key not in rows:
                errs.append(f"storyboard.md has no row '| {key} |'")
            elif sc["scene"] not in (first, last) and (rows[key].lower() in NO_ACTION or NO_ACTION_RE.match(rows[key])):
                errs.append(f"[{key}] storyboard 动 is empty: every explanation line needs a figure action")
            elif sc["scene"] not in (first, last) and HIGHLIGHT_ONLY.search(rows[key]) and not MOTION_WORDS.search(rows[key]):
                errs.append(f"[{key}] storyboard 动 is only a highlight ('{rows[key]}'): glow/闪 belongs in 指; "
                            "pick a motion from reference/visual-design.md (滑、转、平移、放大、展开、飞入、计数…)")
    return errs


def load_script():
    script = json.load(open(os.path.join(ROOT, "script.json"), encoding="utf-8"))
    jobs, report, unpinned = [], [], 0
    for si, sc in enumerate(script):
        for li, ln in enumerate(sc["lines"]):
            src = ln.get("tts", ln["zh"])
            text, notes = pron.to_tts(src, LETTER_SEP)
            issues = pron.lint(src)
            ln["zh"] = pron.strip(ln["zh"])  # subtitles never show the markup
            ln["tts_text"] = text
            if notes or issues:
                report.append(f"[{sc['scene']} {li}] {pron.strip(src)}")
                report += [f"    固定  {o} -> {r}  (送给TTS: {x})" for o, r, x in notes]
                report += [f"    ⚠ {k}  {c}  猜测读 {g}  (可能: {rs})  …{ctx}…" for c, k, g, rs, ctx in issues]
                unpinned += len(issues)
            h = hashlib.md5(f"{VOICE}|{SPEED}|{text}".encode()).hexdigest()[:10]
            ln["wav"] = os.path.join(TTS_DIR, f"{h}.wav")  # keyed by text only, so reordering lines reuses the cache
            jobs.append((text, ln["wav"]))
    return script, jobs, report, unpinned


def need_key():
    if ENGINE == "edge" and not _has_edge():
        raise SystemExit("TTS_ENGINE=edge but edge-tts is not installed: ask the user, then `PY -m pip install --user edge-tts`")
    if ENGINE == "say" and not shutil.which("say"):
        raise SystemExit("TTS_ENGINE=say needs macOS (`say` not found). Use glm or edge.")
    if ENGINE != "glm":
        print(f"note: TTS engine = {ENGINE} ({VOICE}), fallback quality; GLM-TTS (GLM_API_KEY) sounds better "
              "and enables --asr.", file=sys.stderr)
        return
    if not ENV.get("GLM_API_KEY"):
        raise SystemExit("GLM_API_KEY is missing. Ask the user to put `GLM_API_KEY=...` in ~/.config/math-problem-video/.env "
                         "(works in every directory) or in the workspace-root .env "
                         "(key from https://bigmodel.cn/usercenter/proj-mgmt/apikeys). Never invent or print a key. "
                         "Without a key: TTS_ENGINE=edge (pip install edge-tts) or TTS_ENGINE=say (macOS).")
    if VOICE not in VOICES:
        print(f"note: GLM_VOICE={VOICE!r} is not a system voice {VOICES}; OK only if it is a cloned voice id.", file=sys.stderr)


def main():
    if "--engine" in sys.argv:
        print(json.dumps({"engine": ENGINE, "voice": VOICE, "ffmpeg": FF,
                          "has_glm_key": bool(ENV.get("GLM_API_KEY"))}, ensure_ascii=False))
        return
    if "--say" in sys.argv:
        src = sys.argv[sys.argv.index("--say") + 1]
        text, notes = pron.to_tts(src, LETTER_SEP)
        for o, r, x in notes:
            print(f"固定  {o} -> {r}  (送给TTS: {x})")
        for c, k, g, rs, ctx in pron.lint(src):
            print(f"⚠ {k}  {c}  猜测读 {g}  (可能: {rs})  …{ctx}…")
        need_key()
        out = os.path.join(BUILD, "say_" + hashlib.md5(f"{VOICE}|{SPEED}|{text}".encode()).hexdigest()[:8] + ".wav")
        tts(text, out)
        print("voice:", VOICE, " sent to TTS:", text)
        print("WROTE", out)
        if ENGINE == "glm" and ENV.get("GLM_API_KEY"):
            print("ASR heard:", asr(out))
        return

    if "--asr" in sys.argv:
        if not ENV.get("GLM_API_KEY"):  # recognition is GLM-ASR only; clips from any engine can be checked with a key
            print("ASR SKIPPED: no GLM_API_KEY. Tell the user the letter readings were not machine-checked "
                  "and list the lines with point names (AB, PAD ...) for them to listen to.")
            raise SystemExit(0)
        if ENGINE == "glm":
            need_key()
        script, _, _, _ = load_script()
        rows, bad = [], 0
        for sc in script:
            for li, ln in enumerate(sc["lines"]):
                if not os.path.exists(ln["wav"]):
                    raise SystemExit("clips missing: run `PY build_audio.py` (real TTS) before --asr")
                heard = asr(ln["wav"])
                want = pron.strip(ln.get("tts", ln["zh"]))
                ok = letters(heard) == letters(want)
                bad += not ok
                rows.append(f"{'  ' if ok else '✗ '}[{sc['scene']} {li}] 稿: {want}\n      听: {heard}")
        rep = "\n".join(rows) + f"\n\n字母读错的句子: {bad}  (✗ = 听到的字母序列与稿子不一致；汉字读音仍需人工听)\n"
        open(os.path.join(BUILD, "asr_report.txt"), "w", encoding="utf-8").write(rep)
        print(rep)
        raise SystemExit(1 if bad else 0)

    script, jobs, report, unpinned = load_script()
    errors, warns = lint_script(script)
    _, teaching_report = check_teaching(script)
    open(os.path.join(BUILD, "teaching_report.txt"), "w", encoding="utf-8").write(teaching_report)
    rep = "\n".join(report) + f"\n\n未固定读音的生僻字/多音字: {unpinned}  (用 字[pīn] 标注，或加到 pron.json)\n"
    rep += "\n".join(["", *[f"ERROR {e}" for e in errors], *[f"warn  {w}" for w in warns],
                      f"script errors: {len(errors)}   warnings: {len(warns)}", ""])
    open(os.path.join(BUILD, "pron_report.txt"), "w", encoding="utf-8").write(rep)
    print(rep)
    if "--check" in sys.argv:
        raise SystemExit(1 if (unpinned or errors) else 0)
    if errors:
        raise SystemExit("Fix the script errors above first.")

    LEAD = {script[0]["scene"]: 2.2}  # first scene: let the title draw before the voice starts
    GAP, TAIL = 0.45, 0.9
    preview = "--preview" in sys.argv
    if preview:
        durs = [0.2 * len(re.sub(r"[，。、；：！？,.!? ]", "", ln["tts_text"])) + 0.25 for sc in script for ln in sc["lines"]]
    else:
        if unpinned:
            raise SystemExit("Resolve the pronunciation report before TTS (see build/pron_report.txt).")
        need_key()
        unique = list({output: text for text, output in jobs}.items())
        pending = [(text, output) for output, text in unique if not os.path.exists(output)]
        with ThreadPoolExecutor(4) as ex:
            if ENGINE == "windows" and pending:
                size = min(16, max(1, (len(pending) + 3) // 4))
                groups = [pending[i:i + size] for i in range(0, len(pending), size)]
                list(ex.map(tts_windows_batch, groups))
            else:
                list(ex.map(lambda j: tts(*j), pending))
        print("TTS cache:", len(unique) - len(pending), "/", len(unique), "unique clips reused")
        print("TTS done:", len(jobs), "clips  voice:", VOICE)

    t = 0.0
    scenes, voice_parts, sfx, k = [], [], [], 0
    for si, sc in enumerate(script):
        st = t
        if si > 0:
            sfx.append(("whoosh", st - 0.35))
        t += LEAD.get(sc["scene"], 1.0)
        lines = []
        for li, ln in enumerate(sc["lines"]):
            if preview:
                d = durs[k]
            else:
                a = trim(read_wav(ln["wav"]))
                d = len(a) / SR
                voice_parts.append((t, a))
            k += 1
            line = {"zh": ln["zh"], "en": ln["en"], "start": round(t, 3), "end": round(t + d, 3)}
            pause = ln.get("pause_after", 0)
            if pause:
                line["hold_end"] = round(t + d + pause, 3)
            lines.append(line)
            if sc["scene"] in POP_SCENES:
                sfx.append(("pop", t))
            t += d + pause + GAP
        t += TAIL - GAP + (3.2 if si == len(script) - 1 else 0)
        scenes.append({"id": sc["scene"], "start": round(st, 3), "end": round(t, 3), "lines": lines})
    total = round(t, 3)
    tl = {"duration": total, "fps": 30, "scenes": scenes}
    if preview:
        tl["preview_only"] = True
    json.dump(tl, open(os.path.join(BUILD, "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("duration", total, "s", "(ESTIMATED, preview only: no audio written)" if preview else "")
    if preview:
        return

    L = int(total * SR)
    voice = np.zeros(L, np.float32)
    for st, a in voice_parts:
        add(voice, a, st)
    pk = np.abs(voice).max()
    voice *= 0.8 / pk

    music = np.zeros(L, np.float32)
    if MUSIC_LEVEL:
        music = make_music(total)
        music *= 0.5 / (np.abs(music).max() + 1e-9)
        # sidechain ducking from voice envelope
        win = int(0.05 * SR)
        env = box_mean(np.abs(voice), win)
        active = (env > 0.01).astype(np.float32)
        kk = int(0.35 * SR)
        active = box_mean(active, kk)
        active = np.clip(active * 1.5, 0, 1)
        gain = 0.55 - 0.33 * active  # music ~ -5 dB idle, ~ -13 dB under speech
        music *= gain * MUSIC_LEVEL

    fx = np.zeros(L, np.float32)
    for kind, at in sfx:
        add(fx, whoosh() if kind == "whoosh" else pop(), max(0, at))

    mix = voice + music + fx
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    stereo = np.stack([mix, mix], 1)
    # slight stereo width on music only
    stereo[:, 0] += 0.04 * np.roll(music, 300)
    stereo[:, 1] -= 0.04 * np.roll(music, 300)
    stereo = np.clip(stereo, -1, 1)
    with wave.open(os.path.join(BUILD, "mix.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((stereo * 32767).astype("<i2").tobytes())

    # bilingual SRT next to the mp4
    out, n = [], 1
    for sc in scenes:
        for ln in sc["lines"]:
            out.append(f"{n}\n{srt_time(ln['start'])} --> {srt_time(ln.get('hold_end', ln['end']) + 0.25)}\n{plain(ln['zh'])}\n{plain(ln['en'])}\n")
            n += 1
    srt = os.path.join(ROOT, "..", OUT_NAME + ".srt")
    open(srt, "w", encoding="utf-8").write("\n".join(out))
    print("mix + srt written:", os.path.normpath(srt))


if __name__ == "__main__":
    main()
