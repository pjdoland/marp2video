# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

marp2video converts Marp and Slidev markdown slide decks into narrated MP4 videos. It runs a 4-step pipeline: parse markdown into slides, render PNGs via marp-cli (or Slidev CLI), synthesize speech from speaker notes using Chatterbox TTS, and assemble everything into a video with ffmpeg. The presentation format is auto-detected but can be overridden with `--format marp|slidev`.

## Running the Tool

```bash
# First-time setup (must be sourced, not executed)
source setup.sh

# Basic usage (auto-detects Marp or Slidev)
python -m marp2video presentation.md --voice path/to/voice.wav

# Explicit format override
python -m marp2video presentation.md --format slidev --voice voice.wav

# With all TTS options
python -m marp2video presentation.md \
    --voice voice.wav \
    --device cpu \
    --exaggeration 0.5 \
    --cfg-weight 0.3 \
    --temperature 0.6 \
    --pronunciations pronunciations.json \
    --audio-padding 300 \
    --output output.mp4
```

### Pronunciation Overrides

Create a JSON file mapping words or phrases to phonetic respellings that the TTS engine will pronounce correctly:

```json
{
  "kubectl": "cube control",
  "nginx": "engine X",
  "PostgreSQL": "post gress Q L"
}
```

Pass it with `--pronunciations pronunciations.json`. Matching is case-insensitive; longer phrases are matched first so multi-word keys take priority over single-word ones.

## Architecture

The pipeline is orchestrated by `__main__.py` and flows through four modules in sequence:

0. **detect.py** -- Auto-detects format (`"marp"` or `"slidev"`) by checking YAML frontmatter keys, directive comments, and Vue component syntax. Falls back to Marp. Skipped when `--format` is explicit.
1. **parser.py** / **slidev_parser.py** -- Splits markdown on `---` delimiters, extracts speaker notes from `<!-- -->` HTML comments into `Slide` dataclasses (index, body, notes). The Slidev parser additionally strips per-slide frontmatter and does not filter Marp-style directive comments.
2. **renderer.py** / **slidev_renderer.py** -- Calls marp-cli or Slidev CLI (via npx or global install) to produce one PNG per slide. Marp output: `slides.001`, `slides.002`, etc. (no extension). Slidev output: `slides.001.png`, `slides.002.png`, etc.
3. **tts.py** -- Synthesizes each slide's notes with Chatterbox TTS. Long notes are split by sentence and each sentence is generated separately, then concatenated with `torch.cat` into one WAV per slide. Slides without notes get a silent WAV. An optional pronunciation mapping (JSON) applies case-insensitive text substitutions before synthesis to correct mispronounced terms.
4. **assembler.py** -- Creates per-slide MPEG-TS segments (image looped for audio duration) then concatenates into the final MP4 using ffmpeg's concat demuxer.

**utils.py** provides shared helpers: ffmpeg/ffprobe checks, silent WAV generation, and audio duration queries.

## Key Conventions

- Heavy imports (torch, torchaudio, chatterbox) are lazy-loaded only when TTS is needed.
- All file paths use `pathlib.Path`. Temp files follow the pattern `audio_001.wav`, `slides.001`, `segment_001.ts`.
- Subprocess calls use `capture_output=True`; stderr is printed only on failure.
- Device auto-detection order: CUDA, MPS (Apple Silicon), CPU.
- On pipeline failure, the temp directory is preserved for debugging. On success, it's cleaned up unless `--keep-temp` is set.

## System Dependencies

Python 3.11, Node.js/npm (for marp-cli via npx), ffmpeg/ffprobe. The `setup.sh` script validates all of these, creates the venv, and installs Python packages. For Slidev support: `npm install -g @slidev/cli` and playwright-chromium (installed via `npx playwright install chromium`).

## Tests

```bash
# Run all tests
python -m pytest

# Run a specific test file
python -m pytest tests/test_parser.py

# Run with verbose output (default via pyproject.toml)
python -m pytest -v
```

Tests use pytest and live in `tests/`. All external dependencies (ffmpeg, marp-cli, slidev, torch, chatterbox) are mocked — tests run fast with no system requirements beyond Python. Test modules mirror the source modules: `test_parser.py`, `test_slidev_parser.py`, `test_utils.py`, `test_renderer.py`, `test_slidev_renderer.py`, `test_tts.py`, `test_assembler.py`, `test_detect.py`, `test_main.py`.
