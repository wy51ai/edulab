"""Offline behavioral checks. Run: python -m unittest discover -s tests -v"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

SKILL = Path(__file__).resolve().parents[1] / "skills" / "edu-math-video"


class AudioPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.project = self.workspace / "lesson"
        shutil.copytree(SKILL / "template", self.project)
        for name in ("pron.py", "pron.json"):
            shutil.copy(SKILL / "shared" / name, self.workspace / name)
        # Preview never launches FFmpeg; isolate executable discovery from PATH.
        binary = self.workspace / "node_modules" / "ffmpeg-static" / "ffmpeg"
        binary.parent.mkdir(parents=True)
        binary.touch()
        self.env = dict(os.environ, TTS_ENGINE="glm", GLM_API_KEY="", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        self.lines = [
            {"zh": "你好。", "tts": "你好[hǎo]。", "en": "Hello."},
            {"zh": "再见。", "tts": "再见。", "en": "Goodbye."},
        ]

    def run_audio(self, *args):
        (self.project / "script.json").write_text(json.dumps([
            {"scene": "intro", "lines": self.lines}
        ], ensure_ascii=False), encoding="utf-8")
        return subprocess.run([sys.executable, str(self.project / "build_audio.py"), *args],
                              env=self.env, capture_output=True, text=True, encoding="utf-8", timeout=30)

    def timeline(self):
        return json.loads((self.project / "build" / "timeline.json").read_text(encoding="utf-8"))

    def test_legacy_preview_preserves_line_and_scene_times(self):
        result = self.run_audio("--preview")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        tl = self.timeline()
        self.assertEqual(tl["duration"], 8.05)
        self.assertEqual(tl["scenes"][0]["lines"][1]["start"], 3.3)
        self.assertNotIn("hold_end", tl["scenes"][0]["lines"][0])
        self.assertTrue(tl["preview_only"])
        self.assertFalse((self.project / "build" / "mix.wav").exists())

    def test_pause_delays_next_line_without_stretching_narration(self):
        self.lines[0]["pause_after"] = 3.25
        result = self.run_audio("--preview")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        tl = self.timeline()
        first, second = tl["scenes"][0]["lines"]
        self.assertEqual(first["end"], 2.85)
        self.assertEqual(first["hold_end"], 6.1)
        self.assertEqual(second["start"], 6.55)
        self.assertEqual(tl["duration"], 11.3)

    def test_invalid_pause_fails_before_creating_timeline(self):
        for invalid in (-1, True, "four", 31, float("inf")):
            with self.subTest(pause=invalid):
                self.lines[0]["pause_after"] = invalid
                result = self.run_audio("--preview")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("pause_after", result.stdout + result.stderr)
                self.assertFalse((self.project / "build" / "timeline.json").exists())

    def test_declared_theorem_requires_conditions_and_evidence(self):
        self.lines[0]["theorem"] = {"name": "勾股定理", "conclusion": "AB^2 = AC^2 + BC^2"}
        result = self.run_audio("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conditions", result.stdout + result.stderr)

    def test_complete_theorem_emits_reviewable_proof_chain(self):
        self.lines[0]["theorem"] = {
            "name": "勾股定理",
            "conditions": [{"claim": "∠C = 90°", "reason": "题目已知"}],
            "conclusion": "AB^2 = AC^2 + BC^2",
        }
        result = self.run_audio("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = (self.project / "build" / "teaching_report.txt").read_text(encoding="utf-8")
        self.assertIn("∠C = 90°", report)
        self.assertIn("题目已知", report)
        self.assertIn("AB^2 = AC^2 + BC^2", report)

    def test_windows_ffmpeg_static_exe_is_found_without_path_override(self):
        binary = self.workspace / "node_modules" / "ffmpeg-static" / "ffmpeg"
        binary.rename(binary.with_suffix(".exe"))
        self.env.pop("FFMPEG_BINARY", None)
        result = self.run_audio("--preview")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_offline_audition_does_not_send_audio_to_asr_when_key_exists(self):
        # Exercise the real audition command. Speech synthesis has its own SAPI integration test.
        self.env["GLM_API_KEY"] = "test-key-do-not-send"
        source = """
import runpy, sys, requests
from pathlib import Path
sys.path.insert(0, sys.argv[1])
state = runpy.run_path(str(Path(sys.argv[1]) / 'build_audio.py'))
g = state['main'].__globals__
g['ENGINE'], g['VOICE'] = 'windows', 'windows:Offline Test'
g['tts'] = lambda text, output: Path(output).write_bytes(b'local test clip')
def reject_network(*args, **kwargs):
    raise AssertionError('Offline audition attempted online speech recognition')
requests.post = reject_network
sys.argv = ['build_audio.py', '--say', '你好[hǎo]。']
g['main']()
"""
        result = subprocess.run([sys.executable, "-c", source, str(self.project)], env=self.env,
                                capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("ASR heard:", result.stdout)


def load_template_module(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / "template" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AudioMathTests(unittest.TestCase):
    def test_box_filter_keeps_same_alignment_for_even_and_odd_windows(self):
        module = load_template_module("audio_math")
        signal = np.array([0., 0., 1., 0., 2., 0., 0.])
        for window in (1, 2, 3, 4, 9):
            with self.subTest(window=window):
                # NumPy convolution is an independent reference for the former mixer.
                expected = np.convolve(signal, np.ones(window) / window, mode="same")
                actual = module.box_mean(signal, window)
                np.testing.assert_allclose(actual, expected, atol=1e-12)


class WindowsSpeechTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows SAPI integration")
    def test_installed_chinese_voice_writes_nonempty_pcm_without_network(self):
        backend = load_template_module("windows_tts")
        voices = backend.list_voices()
        chinese = [v for v in voices if v["culture"].startswith("zh")]
        if not chinese:
            self.skipTest("No installed Chinese desktop voice")
        import wave
        with tempfile.TemporaryDirectory() as folder:
            audio = Path(folder) / "speech.wav"
            backend.synthesize("你好，我们来看一道数学题。", audio, chinese[0]["name"], 1.0, timeout=30)
            with wave.open(str(audio)) as wav:
                self.assertEqual(wav.getframerate(), 48000)
                self.assertEqual(wav.getnchannels(), 1)
                self.assertEqual(wav.getsampwidth(), 2)
                samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2")
                self.assertGreater(len(samples), 4800)
                self.assertGreater(np.abs(samples.astype(float)).max(), 100)


if __name__ == "__main__":
    unittest.main()
