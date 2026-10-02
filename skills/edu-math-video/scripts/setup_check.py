"""Cross-platform environment check, including native Windows TTS. Never sends narration."""
import json
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    project = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    failed = False
    def check(label, command, timeout=30):
        nonlocal failed
        try:
            result = subprocess.run(command, cwd=project, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=timeout)
            if result.returncode:
                raise RuntimeError(result.stderr.strip() or result.stdout.strip())
            print("OK", label)
            return result.stdout
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            failed = True
            print("MISSING", label, "->", error)
            return None

    check(f"Python dependencies (PY={sys.executable})", [sys.executable, "-c", "import numpy, requests, pypinyin, PIL"])
    details = check("Audio configuration", [sys.executable, str(project / "build_audio.py"), "--engine"])
    if details:
        config = json.loads(details)
        print("voice:", config["voice"], "(offline)" if config["engine"] in ("windows", "say") else "(online)")
        if config["engine"] == "glm" and not config["has_glm_key"]:
            failed = True
            print("MISSING GLM_API_KEY: configure your key or choose an available offline TTS engine")
        check("FFmpeg executable", [config["ffmpeg"], "-version"])
    node = shutil.which("node")
    if node:
        source = """
import {chromium} from 'playwright';
import ffmpeg from 'ffmpeg-static';
let browser;
try { browser = await chromium.launch({channel:'chrome'}); }
catch { browser = await chromium.launch(); }
await browser.close();
"""
        check("Node / Playwright / browser / ffmpeg-static", [node, "--input-type=module", "-e", source], 60)
    else:
        failed = True
        print("MISSING Node.js: install Node.js 18+")
    print("Fix MISSING items and run again." if failed else "ALL OK")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
