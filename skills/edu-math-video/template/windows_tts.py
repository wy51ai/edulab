"""Offline Windows desktop voices. Text travels in a JSON file, never shell code."""
from functools import lru_cache
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile


def _run_job(job, timeout):
    shell = shutil.which("powershell") or shutil.which("pwsh")
    if not shell:
        raise RuntimeError("Windows TTS requires PowerShell and an installed Chinese desktop voice")
    script = Path(__file__).with_suffix(".ps1")
    with tempfile.TemporaryDirectory(prefix="edulab-speech-") as folder:
        source = Path(folder) / "job.json"
        source.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8-sig")
        try:
            result = subprocess.run([shell, "-NoProfile", "-NonInteractive", "-File", str(script), str(source)],
                                    capture_output=True, encoding="utf-8", timeout=timeout,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(f"Windows TTS timed out after {timeout:g}s") from error
        if result.returncode:
            raise RuntimeError("Windows TTS failed: " + result.stderr.strip())
        return result.stdout.lstrip("\ufeff").strip()


@lru_cache(maxsize=1)
def list_voices():
    return json.loads(_run_job({"mode": "voices"}, timeout=15))


def choose_voice(preferred=""):
    voices = list_voices()
    if preferred:
        if any(voice["name"] == preferred for voice in voices):
            return preferred
        raise RuntimeError(f"WINDOWS_VOICE={preferred!r} is not an installed desktop voice")
    chinese = [voice for voice in voices if voice["culture"].startswith("zh")]
    if not chinese:
        raise RuntimeError("No Chinese desktop voice: install one in Windows Settings > Time & language > Speech")
    return chinese[0]["name"]


def synthesize(text, output, voice, speed, timeout=120):
    if not math.isfinite(speed) or speed <= 0:
        raise ValueError("speech speed must be positive and finite")
    _run_job({"mode": "speak", "text": text, "output": str(Path(output).resolve()), "voice": voice,
              "rate": max(-10, min(10, round(10 * math.log2(speed))))}, timeout=timeout)


def synthesize_many(clips, voice, speed, timeout=120):
    """Write separate clips while loading the local speech engine only once."""
    if not math.isfinite(speed) or speed <= 0:
        raise ValueError("speech speed must be positive and finite")
    clips = [{"text": text, "output": str(Path(output).resolve())} for text, output in clips]
    if not clips:
        return
    _run_job({"mode": "batch", "clips": clips, "voice": voice,
              "rate": max(-10, min(10, round(10 * math.log2(speed))))}, timeout=timeout)
