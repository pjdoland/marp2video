"""Utility helpers: silent WAV generation, ffprobe duration queries."""

from __future__ import annotations

import json
import logging
import shutil
import struct
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def check_ffmpeg() -> None:
    """Exit with helpful instructions if ffmpeg / ffprobe are missing."""
    missing = [
        tool for tool in ("ffmpeg", "ffprobe") if shutil.which(tool) is None
    ]
    if not missing:
        logger.debug("ffmpeg/ffprobe found on PATH")
    if missing:
        print(
            f"Error: {', '.join(missing)} not found on PATH.\n"
            "Install ffmpeg:\n"
            "  macOS:   brew install ffmpeg\n"
            "  Ubuntu:  sudo apt install ffmpeg\n"
            "  Windows: https://ffmpeg.org/download.html\n",
            file=sys.stderr,
        )
        sys.exit(1)


def generate_silent_wav(path: Path, duration: float, sample_rate: int = 24000) -> None:
    """Write a silent WAV file of the given duration (pure Python, no deps)."""
    num_channels = 1
    bits_per_sample = 16
    num_samples = int(sample_rate * duration)
    data_size = num_samples * num_channels * (bits_per_sample // 8)

    with open(path, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))  # chunk size
        f.write(struct.pack("<H", 1))   # PCM
        f.write(struct.pack("<H", num_channels))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", sample_rate * num_channels * bits_per_sample // 8))
        f.write(struct.pack("<H", num_channels * bits_per_sample // 8))
        f.write(struct.pack("<H", bits_per_sample))
        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(b"\x00" * data_size)


def get_audio_duration(path: Path) -> float:
    """Get duration of an audio file in seconds using ffprobe."""
    return _get_duration(path)


def get_video_duration(path: Path) -> float:
    """Get duration of a video file in seconds using ffprobe."""
    return _get_duration(path)


def get_video_fps(path: Path) -> float:
    """Get the framerate of a video file using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-select_streams", "v:0",
            "-show_streams",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {result.stderr}")
    info = json.loads(result.stdout)
    # r_frame_rate is a fraction like "30/1" or "30000/1001"
    rate_str = info["streams"][0]["r_frame_rate"]
    num, den = rate_str.split("/")
    return float(num) / float(den)


def _get_duration(path: Path) -> float:
    """Get duration of a media file in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {result.stderr}")
    info = json.loads(result.stdout)
    duration = float(info["format"]["duration"])
    logger.debug("Duration of %s: %.4fs", path, duration)
    return duration
