#!/usr/bin/env python3
"""Build a desk-and-book interactive lesson page from a lesson.js file.

usage:
  python3 generate.py lesson.js out.html            # intro follows LESSON.intro (default: off)
  python3 generate.py lesson.js out.html --intro    # force the classroom intro on
  python3 generate.py lesson.js out.html --no-intro # force it off

Without intro the result is ONE self-contained html file (fonts / KaTeX from CDN).
With intro, the video, music and wood textures are copied next to the html (girl.mov, girl.webm, cmbg.mp3, tex/textures.js).
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TPL = SKILL / "template"
INTRO_ASSETS = SKILL / "assets" / "intro"


def strip_intro(html: str) -> str:
    return re.sub(r"<!--INTRO:BEGIN-->.*?<!--INTRO:END-->", "", html, flags=re.S)


def keep_intro(html: str) -> str:
    return html.replace("<!--INTRO:BEGIN-->", "").replace("<!--INTRO:END-->", "")


def lesson_wants_intro(src: str) -> bool:
    # a light check for `intro: true` / `intro: {` at the top level of the lesson object
    return bool(re.search(r"^\s*intro\s*:\s*(true|\{)", src, flags=re.M))


def lesson_title(src: str) -> str:
    m = re.search(r"^\s*pageTitle\s*:\s*['\"`](.+?)['\"`]", src, flags=re.M) or \
        re.search(r"^\s*title\s*:\s*['\"`](.+?)['\"`]", src, flags=re.M)
    return m.group(1) if m else "互动试卷"


def build(lesson_path: Path, out: Path, intro=None) -> Path:
    src = lesson_path.read_text(encoding="utf-8")
    if "</script" in src.lower():
        sys.exit("lesson.js must not contain '</script' (it is inlined into a <script> tag)")
    if not re.search(r"\b(const|var|let)\s+LESSON\s*=", src):
        sys.exit("lesson.js must define `const LESSON = {...}`")
    use_intro = lesson_wants_intro(src) if intro is None else intro

    html = (TPL / "book.html").read_text(encoding="utf-8")
    parts = {
        "/*@@CSS@@*/": (TPL / "book.css").read_text(encoding="utf-8"),
        "/*@@CORE@@*/": (TPL / "core.js").read_text(encoding="utf-8"),
        "/*@@LESSON@@*/": src,
        "/*@@RENDERERS@@*/": (TPL / "renderers.js").read_text(encoding="utf-8"),
        "/*@@PROPS@@*/": (TPL / "props.js").read_text(encoding="utf-8"),
        "/*@@SCENE@@*/": (TPL / "scene.js").read_text(encoding="utf-8"),
        "/*@@INTRO_GL@@*/": (TPL / "intro_gl.js").read_text(encoding="utf-8") if use_intro else "",
    }
    html = keep_intro(html) if use_intro else strip_intro(html)
    html = html.replace("@@TITLE@@", lesson_title(src))   # before inlining, so lesson text can never be mistaken for a marker
    for k, v in parts.items():
        html = html.replace(k, v)

    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    if use_intro:
        for name in ("girl.mov", "girl.webm", "cmbg.mp3"):
            shutil.copy2(INTRO_ASSETS / name, out.parent / name)
        (out.parent / "tex").mkdir(exist_ok=True)
        shutil.copy2(INTRO_ASSETS / "tex" / "textures.js", out.parent / "tex" / "textures.js")
    print(f"wrote {out}  ({out.stat().st_size // 1024} KB, intro={'on' if use_intro else 'off'})")
    if use_intro:
        print(f"  + intro assets copied to {out.parent} (girl.mov, girl.webm, cmbg.mp3, tex/textures.js)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lesson")
    ap.add_argument("out")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--intro", dest="intro", action="store_true", default=None)
    g.add_argument("--no-intro", dest="intro", action="store_false")
    a = ap.parse_args()
    build(Path(a.lesson), Path(a.out), a.intro)


if __name__ == "__main__":
    main()
