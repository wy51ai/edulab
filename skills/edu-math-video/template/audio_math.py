"""Audio configuration and linear-time narration sidechain smoothing."""
import math
import numpy as np


def get_music_level(episode):
    """Return the optional background music multiplier, preserving legacy volume."""
    level = episode.get("music_level", 1)
    if (isinstance(level, bool) or not isinstance(level, (int, float))
            or not 0 <= level <= 1 or not math.isfinite(level)):
        raise ValueError("episode.music_level must be a finite number between 0 and 1")
    return float(level)


def box_mean(signal, window):
    """Equivalent to convolve(signal, ones(window)/window, mode='same').

    Keep NumPy's even-window alignment and max(input, window) output length.
    Cumulative sums avoid long convolution kernels on multi-minute 48 kHz audio.
    """
    if not isinstance(window, int) or isinstance(window, bool) or window < 1:
        raise ValueError("window must be a positive integer")
    signal = np.asarray(signal, dtype=np.float64)
    if signal.ndim != 1 or not len(signal):
        raise ValueError("signal must be a nonempty one-dimensional array")
    size = max(len(signal), window)
    # Full convolution cropped starting at (min(N, M)-1)//2.
    left = window - 1 - (min(len(signal), window) - 1) // 2
    padded = np.pad(signal, (left, size + window - 1 - len(signal) - left))
    sums = np.concatenate(([0.0], np.cumsum(padded, dtype=np.float64)))
    return (sums[window:] - sums[:-window]) / window
