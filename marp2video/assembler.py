"""Assemble per-slide video segments and concatenate into the final MP4."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .utils import get_audio_duration


def _make_segment(
    index: int,
    image: Path,
    audio: Path,
    temp_dir: Path,
    fps: int,
) -> Path:
    """Create a single .ts segment: image looped for the audio duration + audio."""
    duration = get_audio_duration(audio)
    segment = temp_dir / f"segment_{index:03d}.ts"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-framerate", str(fps),
        "-i", str(image),
        "-i", str(audio),
        "-t", f"{duration:.4f}",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-f", "mpegts",
        str(segment),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffmpeg segment error (slide {index}):", result.stderr, file=sys.stderr)
        raise RuntimeError(f"ffmpeg failed on segment {index}")
    return segment


def assemble_video(
    images: list[Path],
    audio_files: list[Path],
    output: Path,
    *,
    temp_dir: Path,
    fps: int,
) -> None:
    """Build per-slide segments and concatenate into the final MP4."""
    segments: list[Path] = []
    for i, (img, aud) in enumerate(zip(images, audio_files), start=1):
        print(f"  Encoding segment {i}/{len(images)}…")
        seg = _make_segment(i, img, aud, temp_dir, fps)
        segments.append(seg)

    # Write concat list
    concat_file = temp_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output),
    ]
    print(f"  Concatenating {len(segments)} segments…")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ffmpeg concat error:", result.stderr, file=sys.stderr)
        raise RuntimeError("ffmpeg concat failed")

    print(f"  Output: {output} ({output.stat().st_size / 1024 / 1024:.1f} MB)")
