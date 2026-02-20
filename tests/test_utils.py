"""Tests for marp2video.utils — ffmpeg helpers and WAV generation."""

from __future__ import annotations

import json
import struct
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from marp2video.utils import (
    check_ffmpeg,
    generate_silent_wav,
    get_audio_duration,
    get_video_duration,
    get_video_fps,
)


# ---------------------------------------------------------------------------
# generate_silent_wav
# ---------------------------------------------------------------------------

class TestGenerateSilentWav:
    def test_file_created(self, tmp_path):
        p = tmp_path / "out.wav"
        generate_silent_wav(p, duration=1.0)
        assert p.exists()

    def test_riff_header(self, tmp_path):
        p = tmp_path / "out.wav"
        generate_silent_wav(p, duration=0.5)
        data = p.read_bytes()
        assert data[:4] == b"RIFF"
        assert data[8:12] == b"WAVE"

    def test_pcm_format(self, tmp_path):
        p = tmp_path / "out.wav"
        generate_silent_wav(p, duration=0.5)
        data = p.read_bytes()
        # fmt chunk starts at offset 12
        assert data[12:16] == b"fmt "
        fmt_size = struct.unpack_from("<I", data, 16)[0]
        assert fmt_size == 16  # PCM
        audio_format = struct.unpack_from("<H", data, 20)[0]
        assert audio_format == 1  # PCM

    def test_sample_rate(self, tmp_path):
        p = tmp_path / "out.wav"
        generate_silent_wav(p, duration=0.5, sample_rate=48000)
        data = p.read_bytes()
        sr = struct.unpack_from("<I", data, 24)[0]
        assert sr == 48000

    def test_mono_channel(self, tmp_path):
        p = tmp_path / "out.wav"
        generate_silent_wav(p, duration=0.5)
        data = p.read_bytes()
        channels = struct.unpack_from("<H", data, 22)[0]
        assert channels == 1

    def test_data_size_matches_duration(self, tmp_path):
        p = tmp_path / "out.wav"
        duration = 2.0
        sample_rate = 24000
        generate_silent_wav(p, duration=duration, sample_rate=sample_rate)
        data = p.read_bytes()
        # data chunk header at offset 36
        assert data[36:40] == b"data"
        data_size = struct.unpack_from("<I", data, 40)[0]
        expected = int(sample_rate * duration) * 1 * 2  # mono, 16-bit
        assert data_size == expected

    def test_all_samples_are_zero(self, tmp_path):
        p = tmp_path / "out.wav"
        generate_silent_wav(p, duration=0.1)
        data = p.read_bytes()
        # Audio data starts at offset 44
        audio_data = data[44:]
        assert audio_data == b"\x00" * len(audio_data)

    def test_file_size_correct(self, tmp_path):
        p = tmp_path / "out.wav"
        duration = 1.0
        sample_rate = 24000
        generate_silent_wav(p, duration=duration, sample_rate=sample_rate)
        data = p.read_bytes()
        # RIFF size field = total file size - 8
        riff_size = struct.unpack_from("<I", data, 4)[0]
        assert riff_size == len(data) - 8

    def test_zero_duration(self, tmp_path):
        p = tmp_path / "out.wav"
        generate_silent_wav(p, duration=0.0)
        assert p.exists()
        data = p.read_bytes()
        # Should still have valid header, just no audio data
        assert data[:4] == b"RIFF"
        data_size = struct.unpack_from("<I", data, 40)[0]
        assert data_size == 0


# ---------------------------------------------------------------------------
# check_ffmpeg
# ---------------------------------------------------------------------------

class TestCheckFfmpeg:
    def test_passes_when_both_available(self):
        with patch("marp2video.utils.shutil.which", return_value="/usr/bin/ffmpeg"):
            # Should not raise or exit
            check_ffmpeg()

    def test_exits_when_ffmpeg_missing(self):
        def fake_which(name):
            return None  # everything missing
        with patch("marp2video.utils.shutil.which", side_effect=fake_which):
            with pytest.raises(SystemExit):
                check_ffmpeg()

    def test_exits_when_ffprobe_missing(self):
        def fake_which(name):
            return "/usr/bin/ffmpeg" if name == "ffmpeg" else None
        with patch("marp2video.utils.shutil.which", side_effect=fake_which):
            with pytest.raises(SystemExit):
                check_ffmpeg()


# ---------------------------------------------------------------------------
# get_audio_duration / get_video_duration (mocked ffprobe)
# ---------------------------------------------------------------------------

def _mock_ffprobe_result(duration_str: str):
    """Return a mock subprocess result with ffprobe JSON output."""
    output = json.dumps({"format": {"duration": duration_str}})
    result = MagicMock()
    result.returncode = 0
    result.stdout = output
    result.stderr = ""
    return result


class TestGetAudioDuration:
    def test_returns_duration(self, tmp_path):
        with patch("marp2video.utils.subprocess.run", return_value=_mock_ffprobe_result("3.456")):
            d = get_audio_duration(tmp_path / "audio.wav")
            assert d == pytest.approx(3.456)

    def test_ffprobe_failure_raises(self, tmp_path):
        result = MagicMock()
        result.returncode = 1
        result.stderr = "error"
        with patch("marp2video.utils.subprocess.run", return_value=result):
            with pytest.raises(RuntimeError, match="ffprobe failed"):
                get_audio_duration(tmp_path / "audio.wav")


class TestGetVideoDuration:
    def test_returns_duration(self, tmp_path):
        with patch("marp2video.utils.subprocess.run", return_value=_mock_ffprobe_result("12.5")):
            d = get_video_duration(tmp_path / "video.mp4")
            assert d == pytest.approx(12.5)


# ---------------------------------------------------------------------------
# get_video_fps (mocked ffprobe)
# ---------------------------------------------------------------------------

class TestGetVideoFps:
    def _mock_fps_result(self, rate_str: str):
        output = json.dumps({"streams": [{"r_frame_rate": rate_str}]})
        result = MagicMock()
        result.returncode = 0
        result.stdout = output
        result.stderr = ""
        return result

    def test_integer_fps(self, tmp_path):
        with patch("marp2video.utils.subprocess.run", return_value=self._mock_fps_result("30/1")):
            assert get_video_fps(tmp_path / "v.mp4") == pytest.approx(30.0)

    def test_fractional_fps(self, tmp_path):
        with patch("marp2video.utils.subprocess.run", return_value=self._mock_fps_result("30000/1001")):
            assert get_video_fps(tmp_path / "v.mp4") == pytest.approx(29.97, rel=1e-2)

    def test_24fps(self, tmp_path):
        with patch("marp2video.utils.subprocess.run", return_value=self._mock_fps_result("24/1")):
            assert get_video_fps(tmp_path / "v.mp4") == pytest.approx(24.0)

    def test_60fps(self, tmp_path):
        with patch("marp2video.utils.subprocess.run", return_value=self._mock_fps_result("60/1")):
            assert get_video_fps(tmp_path / "v.mp4") == pytest.approx(60.0)

    def test_ffprobe_failure_raises(self, tmp_path):
        result = MagicMock()
        result.returncode = 1
        result.stderr = "no such file"
        with patch("marp2video.utils.subprocess.run", return_value=result):
            with pytest.raises(RuntimeError, match="ffprobe failed"):
                get_video_fps(tmp_path / "v.mp4")
