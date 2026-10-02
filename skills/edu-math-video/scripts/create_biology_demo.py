#!/usr/bin/env python3
"""Create a local, self-contained copy of the mitophagy classroom example."""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
EXAMPLE_FILES = ("index.html", "anim.js", "episode.json", "script.json", "storyboard.md")
IGNORE = shutil.ignore_patterns("build", "node_modules", "__pycache__", "*.pyc", ".env", ".env.*")
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}
# Reviewed readings used by this example; the source shared dictionary stays untouched.
DEMO_WORDS = {
    "折叠": "zhé _",
    "减少": "_ shǎo",
    "积累": "_ lěi",
    "降解": "jiàng _",
}


def safe_name(value):
    """Accept one portable ASCII directory component, including on Windows."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value, flags=re.ASCII):
        raise argparse.ArgumentTypeError(
            "name must be 1-64 ASCII letters, digits, '-' or '_', starting with a letter or digit"
        )
    if value.upper() in WINDOWS_RESERVED:
        raise argparse.ArgumentTypeError("name is a reserved Windows device name")
    return value


def local_audio_source(template):
    """Pin only the generated copy to its own pronunciation files."""
    source = (template / "build_audio.py").read_text(encoding="utf-8")
    old = '_pron_dir = _find_up("pron.py")'
    if source.count(old) != 1:
        raise ValueError("template pronunciation loader changed; review it before creating a demo")
    new = '_pron_dir = ROOT if os.path.isfile(os.path.join(ROOT, "pron.py")) else None'
    source = source.replace(old, new, 1)
    source = source.replace(
        '"pron.py not found in this folder or any parent. Copy shared/pron.py + shared/pron.json "\n'
        '                     "from the edu-math-video skill to the workspace root."',
        '"Local pron.py missing. Restore pron.py + pron.json in this generated project."',
        1,
    )
    return source


def create_demo(workspace, name):
    """Copy verified local sources without running TTS, ASR or network commands."""
    workspace = Path(workspace).expanduser().resolve(strict=True)
    if not workspace.is_dir():
        raise ValueError("workspace must be an existing directory")
    name = safe_name(name)
    destination = workspace / name
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Already exists: {destination}. Choose another name; nothing was overwritten.")
    if destination.resolve().parent != workspace:
        raise ValueError("destination must stay directly inside the requested workspace")

    template = SKILL / "template"
    example = SKILL / "examples" / "mitophagy-cell"
    shared = SKILL / "shared"
    model = SKILL / "lib" / "biology-model.js"
    required = [template / "build_audio.py", model, shared / "pron.py", shared / "pron.json"]
    required.extend(example / filename for filename in EXAMPLE_FILES)
    for source in required:
        if not source.is_file():
            raise FileNotFoundError(f"Required local source missing: {source}")

    # Prepare all modifications before creating the destination.
    audio_source = local_audio_source(template)
    dictionary = json.loads((shared / "pron.json").read_text(encoding="utf-8"))
    if not isinstance(dictionary.get("words"), dict):
        raise ValueError("shared pron.json must contain a 'words' object")
    dictionary["words"].update(DEMO_WORDS)
    episode = json.loads((example / "episode.json").read_text(encoding="utf-8"))
    episode["music_level"] = 0

    # copytree refuses an existing destination, including a competing creation.
    shutil.copytree(template, destination, ignore=IGNORE)
    for filename in EXAMPLE_FILES:
        shutil.copy2(example / filename, destination / filename)
    shutil.copy2(model, destination / "biology-model.js")
    shutil.copy2(shared / "pron.py", destination / "pron.py")
    (destination / "pron.json").write_text(
        json.dumps(dictionary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "episode.json").write_text(
        json.dumps(episode, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "build_audio.py").write_text(audio_source, encoding="utf-8")
    (destination / "build").mkdir()
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="existing workspace containing shared Node dependencies")
    parser.add_argument("--name", type=safe_name, default="cell-classroom-demo", help="new ASCII project directory")
    arguments = parser.parse_args(argv)
    try:
        destination = create_demo(arguments.workspace, arguments.name)
    except (OSError, ValueError, argparse.ArgumentTypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Created: {destination}")
    print("Pronunciation files are local to this project; music_level=0.")
    print("Next: select a Python with numpy, requests and pypinyin, then run build_audio.py --check.")
    print("Preview: build_audio.py --preview; node render.mjs motion; node render.mjs stills auto.")
    print("No dependencies were installed; no TTS, ASR or network commands were run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
