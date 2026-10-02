"""Exercise the real local biology-demo creator; no synthesis or network calls."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
SKILL = REPOSITORY / "skills" / "edu-math-video"
CREATOR = SKILL / "scripts" / "create_biology_demo.py"
EXAMPLE = SKILL / "examples" / "mitophagy-cell"


class BiologyDemoCreatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="biology-demo-test-")
        self.addCleanup(self.temp.cleanup)
        self.sandbox = Path(self.temp.name).resolve()
        self.workspace = self.sandbox / "workspace"
        self.workspace.mkdir()
        self.env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")

    def create(self, name="lesson", workspace=None, use_default_name=False):
        command = [sys.executable, str(CREATOR), "--workspace", str(workspace or self.workspace)]
        if not use_default_name:
            command += ["--name", name]
        return subprocess.run(command, env=self.env, capture_output=True, text=True,
                              encoding="utf-8", timeout=30)

    def run_check(self, project):
        # --check only checks executable existence, never invokes FFmpeg or TTS.
        env = dict(self.env, TTS_ENGINE="glm", FFMPEG_BINARY=sys.executable)
        return subprocess.run([sys.executable, str(project / "build_audio.py"), "--check"],
                              cwd=project, env=env, capture_output=True, text=True,
                              encoding="utf-8", timeout=30)

    def test_real_sources_are_copied_and_local_words_do_not_change_shared_dictionary(self):
        originals = {name: (SKILL / "shared" / name).read_bytes()
                     for name in ("pron.py", "pron.json")}
        result = self.create("cell_lesson")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        project = self.workspace / "cell_lesson"
        self.assertTrue((project / "build").is_dir())
        self.assertEqual(list((project / "build").iterdir()), [])
        for name in ("index.html", "anim.js", "script.json", "storyboard.md"):
            self.assertEqual((project / name).read_bytes(), (EXAMPLE / name).read_bytes(), name)
        self.assertEqual((project / "biology-model.js").read_bytes(),
                         (SKILL / "lib" / "biology-model.js").read_bytes())
        for name in ("engine.js", "render.mjs", "teaching.py", "windows_tts.py"):
            self.assertEqual((project / name).read_bytes(), (SKILL / "template" / name).read_bytes(), name)
        self.assertEqual((project / "pron.py").read_bytes(), originals["pron.py"])
        for name, original in originals.items():
            self.assertEqual((SKILL / "shared" / name).read_bytes(), original, name)
        local_words = json.loads((project / "pron.json").read_text(encoding="utf-8"))["words"]
        # Check specific reviewed biological readings, independently of creator constants.
        self.assertEqual(local_words["积累"], "_ lěi")
        self.assertEqual(local_words["降解"], "jiàng _")
        config = json.loads((project / "episode.json").read_text(encoding="utf-8"))
        self.assertEqual(config["music_level"], 0)
        original_config = json.loads((EXAMPLE / "episode.json").read_text(encoding="utf-8"))
        for key, value in original_config.items():
            if key != "music_level":
                self.assertEqual(config[key], value, key)
        for forbidden in ("node_modules", "__pycache__", ".env"):
            self.assertFalse((project / forbidden).exists(), forbidden)

    def test_generated_audio_uses_local_pronunciation_and_refuses_parent_fallback(self):
        # An unrelated user's workspace dictionary must never be used by this lesson.
        (self.workspace / "pron.py").write_text(
            "raise AssertionError('User workspace pronunciation was imported')\n", encoding="utf-8"
        )
        (self.workspace / "pron.json").write_text("{invalid parent dictionary", encoding="utf-8")
        result = self.create()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        project = self.workspace / "lesson"
        checked = self.run_check(project)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertIn("script errors: 0", checked.stdout)
        self.assertIn("未固定读音的生僻字/多音字: 0", checked.stdout)
        (project / "pron.py").unlink()
        missing = self.run_check(project)
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("Local pron.py missing", missing.stdout + missing.stderr)
        self.assertNotIn("User workspace pronunciation was imported", missing.stdout + missing.stderr)
        self.assertEqual((self.workspace / "pron.json").read_text(encoding="utf-8"),
                         "{invalid parent dictionary")

    def test_existing_destination_is_preserved(self):
        existing = self.workspace / "lesson"
        existing.mkdir()
        marker = existing / "user-work.txt"
        marker.write_bytes(b"Keep this existing work exactly.\n")
        result = self.create()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Already exists", result.stdout + result.stderr)
        self.assertEqual(marker.read_bytes(), b"Keep this existing work exactly.\n")
        self.assertEqual({item.name for item in existing.iterdir()}, {"user-work.txt"})

    def test_invalid_names_cannot_escape_or_create_windows_device_paths(self):
        invalid = ("../escape", "..\\escape", "nested/lesson", "nested\\lesson", "/absolute",
                   "C:\\absolute", ".", "..", "", "with space", "细胞", "CON", "prn", "AUX",
                   "nul", "COM1", "com9", "LPT1", "lpt9", "CONIN$", "x" * 65)
        for name in invalid:
            with self.subTest(name=name):
                result = self.create(name)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(list(self.workspace.iterdir()), [])
                self.assertEqual({item.name for item in self.sandbox.iterdir()}, {"workspace"})

    def test_missing_workspace_is_not_created(self):
        missing = self.sandbox / "missing-workspace"
        result = self.create(workspace=missing)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(missing.exists())

    def test_default_name_creates_a_portable_project(self):
        result = self.create(use_default_name=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.workspace / "cell-classroom-demo" / "build_audio.py").is_file())


if __name__ == "__main__":
    unittest.main()
