"""Exercise music configuration with local PCM fixtures, never online speech."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave

import numpy as np


SKILL = Path(__file__).resolve().parents[1] / "skills" / "edu-math-video"
UNSET = object()


class MusicLevelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.project = self.workspace / "lesson"
        shutil.copytree(SKILL / "template", self.project)
        for name in ("pron.py", "pron.json"):
            shutil.copy(SKILL / "shared" / name, self.workspace / name)
        binary = self.workspace / "node_modules" / "ffmpeg-static" / "ffmpeg"
        binary.parent.mkdir(parents=True)
        binary.touch()
        self.env = dict(os.environ, TTS_ENGINE="glm", GLM_API_KEY="", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        self.lines = [
            {"zh": "你好。", "tts": "你好[hǎo]。", "en": "Hello."},
            {"zh": "再见。", "tts": "再见。", "en": "Goodbye."},
        ]

    def configure(self, music_level=UNSET):
        episode = {"title": "Fixture", "output_name": "fixture", "pop_scenes": []}
        if music_level is not UNSET:
            episode["music_level"] = music_level
        (self.project / "episode.json").write_text(json.dumps(episode), encoding="utf-8")
        (self.project / "script.json").write_text(json.dumps([
            {"scene": "intro", "lines": self.lines}
        ], ensure_ascii=False), encoding="utf-8")

    def preview(self):
        return subprocess.run([sys.executable, str(self.project / "build_audio.py"), "--preview"],
                              env=self.env, capture_output=True, text=True, encoding="utf-8", timeout=30)

    def synthesize_local_fixture(self, forbid_music=False):
        # Keep the real timeline, normalization, ducking, stereo mix and WAV writer.
        # Only the external speech boundary is replaced by known local PCM samples.
        source = """
import runpy, sys, requests, wave
from pathlib import Path
import numpy as np
def reject_network(*args, **kwargs):
    raise AssertionError('Audio fixture attempted a network request')
requests.post = reject_network
sys.path.insert(0, sys.argv[1])
state = runpy.run_path(str(Path(sys.argv[1]) / 'build_audio.py'))
g = state['main'].__globals__
g['need_key'] = lambda: None
def local_pcm(text, output):
    with wave.open(output, 'wb') as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(48000)
        audio.writeframes(np.full(19200, 6553, dtype='<i2').tobytes())
g['tts'] = local_pcm
if sys.argv[2] == 'forbid':
    def reject_music(total):
        raise AssertionError('Background music was generated with music_level=0')
    g['make_music'] = reject_music
sys.argv = ['build_audio.py']
g['main']()
"""
        return subprocess.run([sys.executable, "-c", source, str(self.project), "forbid" if forbid_music else "allow"],
                              env=self.env, capture_output=True, text=True, encoding="utf-8", timeout=30)

    def timeline(self):
        return json.loads((self.project / "build" / "timeline.json").read_text(encoding="utf-8"))

    def samples(self):
        with wave.open(str(self.project / "build" / "mix.wav")) as audio:
            self.assertEqual(audio.getframerate(), 48000)
            self.assertEqual(audio.getnchannels(), 2)
            return np.frombuffer(audio.readframes(audio.getnframes()), dtype="<i2").reshape(-1, 2)

    # Catches accepting bools, coercing strings, ignoring bounds or generating invalid output.
    def test_invalid_music_level_fails_before_timeline_or_audio(self):
        for value in (-.1, 1.1, True, False, "0.5", None, [], float("inf"), float("nan")):
            with self.subTest(music_level=value):
                self.configure(value)
                result = self.preview()
                self.assertNotEqual(result.returncode, 0, "Invalid music_level was accepted")
                self.assertIn("music_level", result.stdout + result.stderr)
                self.assertFalse((self.project / "build" / "timeline.json").exists())
                self.assertFalse((self.project / "build" / "mix.wav").exists())

    # Catches muting only the final mix while still synthesizing music, or residual stereo music.
    def test_zero_music_skips_generation_and_leaves_silence_outside_narration(self):
        self.lines[0]["pause_after"] = .6
        self.configure(0)
        result = self.synthesize_local_fixture(forbid_music=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        samples = self.samples()
        speaking = np.zeros(len(samples), dtype=bool)
        for line in self.timeline()["scenes"][0]["lines"]:
            speaking[int(line["start"] * 48000):int(line["end"] * 48000)] = True
        self.assertTrue(np.all(samples[~speaking] == 0), "Music remains outside narration")
        self.assertGreater(np.abs(samples[speaking].astype(float)).max(), 20000)
        np.testing.assert_array_equal(samples[:, 0], samples[:, 1])

    # Catches an unused numeric setting: a quiet music setting must actually reduce idle audio.
    def test_half_music_level_halves_music_during_the_lead_in(self):
        self.configure(1)
        first = self.synthesize_local_fixture()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        full = self.samples().copy()
        self.configure(.5)
        second = self.synthesize_local_fixture()
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        half = self.samples()
        self.assertGreater(np.abs(full[:96000].astype(float)).max(), 100)
        np.testing.assert_allclose(half[:96000], full[:96000].astype(float) / 2, atol=1)

    # Catches changing old timing or audio when an episode omits the optional setting.
    def test_default_music_matches_level_one_and_keeps_legacy_timing(self):
        self.configure()
        result = self.synthesize_local_fixture()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        default_samples, default_timeline = self.samples().copy(), self.timeline()
        self.assertEqual(default_timeline["duration"], 7.55)
        self.assertEqual(default_timeline["scenes"][0]["lines"][0]["start"], 2.2)
        self.assertEqual(default_timeline["scenes"][0]["lines"][1]["start"], 3.05)
        self.configure(1)
        result = self.synthesize_local_fixture()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.timeline(), default_timeline)
        np.testing.assert_array_equal(self.samples(), default_samples)


if __name__ == "__main__":
    unittest.main()
