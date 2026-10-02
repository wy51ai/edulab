"""Canonical PCM output without resampling already compatible speech clips."""
from pathlib import Path
import os
import subprocess
import wave


def to_pcm_wav(source, output, ffmpeg, sample_rate=48000):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValueError("source and output must be different files")
    temporary = output.with_name(output.name + ".part.wav")
    try:
        frames = None
        try:
            with wave.open(str(source), "rb") as audio:
                if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getcomptype()) == (1, 2, sample_rate, "NONE"):
                    candidate = audio.readframes(audio.getnframes())
                    if len(candidate) == audio.getnframes() * 2:
                        frames = candidate
        except (wave.Error, EOFError):
            pass  # compressed audio and unusual WAV layouts still use FFmpeg
        if frames is not None:
            with wave.open(str(temporary), "wb") as audio:
                audio.setparams((1, 2, sample_rate, 0, "NONE", "not compressed"))
                audio.writeframes(frames)
        else:
            subprocess.run([str(ffmpeg), "-y", "-loglevel", "error", "-i", str(source),
                            "-map_metadata", "-1", "-fflags", "+bitexact", "-ar", str(sample_rate),
                            "-ac", "1", str(temporary)], check=True)
        os.replace(temporary, output)
        source.unlink()
    finally:
        if temporary.exists():
            temporary.unlink()
