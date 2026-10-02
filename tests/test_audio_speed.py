"""Lossless offline speedups: skip redundant conversion, share a SAPI session."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
import wave

import numpy as np

TEMPLATE = Path(__file__).resolve().parents[1] / "skills" / "edu-math-video" / "template"


def load(name):
    spec = importlib.util.spec_from_file_location(name, TEMPLATE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_pcm(path, rate=48000):
    samples = (np.sin(np.arange(rate // 10) * 2 * np.pi * 440 / rate) * 10000).astype("<i2").tobytes()
    with wave.open(str(path), "wb") as audio:
        audio.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        audio.writeframes(samples)
    return samples


class PcmConversionTests(unittest.TestCase):
    def test_matching_pcm_avoids_ffmpeg_and_preserves_every_sample(self):
        module = load("audio_io")
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "source.wav", Path(folder) / "out.wav"
            expected = write_pcm(source)
            with mock.patch.object(module.subprocess, "run", side_effect=AssertionError("Redundant FFmpeg")):
                module.to_pcm_wav(source, output, "unused-ffmpeg")
            with wave.open(str(output)) as audio:
                self.assertEqual(audio.getparams()[:3], (1, 2, 48000))
                self.assertEqual(audio.readframes(audio.getnframes()), expected)
            self.assertFalse(source.exists())

    def test_real_resampling_still_uses_ffmpeg_for_other_rates(self):
        module = load("audio_io")
        binary = os.environ.get("FFMPEG_BINARY")
        if not binary or not Path(binary).is_file():
            self.skipTest("Set FFMPEG_BINARY for resampling integration")
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "source.wav", Path(folder) / "out.wav"
            write_pcm(source, 16000)
            with mock.patch.object(module.subprocess, "run", wraps=module.subprocess.run) as conversion:
                module.to_pcm_wav(source, output, binary)
                self.assertEqual(conversion.call_count, 1)
            with wave.open(str(output)) as audio:
                self.assertEqual(audio.getparams()[:3], (1, 2, 48000))
                self.assertEqual(audio.getnframes(), 4800)

    def test_failed_conversion_does_not_delete_the_source(self):
        module = load("audio_io")
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "source.wav", Path(folder) / "out.wav"
            source.write_bytes(b"invalid audio")
            error = subprocess.CalledProcessError(1, "ffmpeg")
            with mock.patch.object(module.subprocess, "run", side_effect=error):
                with self.assertRaises(subprocess.CalledProcessError):
                    module.to_pcm_wav(source, output, "unused-ffmpeg")
            self.assertEqual(source.read_bytes(), b"invalid audio")


class WindowsBatchTests(unittest.TestCase):
    def test_empty_batch_does_not_launch_a_speech_process(self):
        backend = load("windows_tts")
        with mock.patch.object(backend, "_run_job", side_effect=AssertionError("Empty batch launched")):
            backend.synthesize_many([], "unused", 1.0)

    def test_invalid_speed_is_rejected_before_launch(self):
        backend = load("windows_tts")
        for speed in [0, -1, float("nan"), float("inf")]:
            with self.subTest(speed=speed), mock.patch.object(backend, "_run_job", side_effect=AssertionError("Bad speed launched")):
                with self.assertRaises(ValueError):
                    backend.synthesize_many([("你好", "unused.wav")], "unused", speed)

    @unittest.skipUnless(os.name == "nt", "Windows SAPI integration")
    def test_one_speech_process_writes_separate_lossless_clips(self):
        backend = load("windows_tts")
        chinese = [v for v in backend.list_voices() if v["culture"].startswith("zh")]
        if not chinese:
            self.skipTest("No installed Chinese voice")
        voice = chinese[0]["name"]
        texts = ["观察细胞。", "两层膜闭合。"]
        with tempfile.TemporaryDirectory() as folder:
            reference, jobs = [], []
            for i, text in enumerate(texts):
                single = Path(folder) / f"single{i}.wav"
                backend.synthesize(text, single, voice, 1.0, timeout=30)
                with wave.open(str(single)) as audio:
                    reference.append(audio.readframes(audio.getnframes()))
                jobs.append((text, Path(folder) / f"batch{i}.wav"))
            with mock.patch.object(backend, "_run_job", wraps=backend._run_job) as process:
                backend.synthesize_many(jobs, voice, 1.0, timeout=30)
                self.assertEqual(process.call_count, 1)
            for i, (_, output) in enumerate(jobs):
                with wave.open(str(output)) as audio:
                    self.assertEqual(audio.getparams()[:3], (1, 2, 48000))
                    self.assertEqual(audio.readframes(audio.getnframes()), reference[i])
