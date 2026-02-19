# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

marp2video converts Marp markdown slide decks into narrated MP4 videos. It runs a 4-step pipeline: parse markdown into slides, render PNGs via marp-cli, synthesize speech from speaker notes using Chatterbox TTS, and assemble everything into a video with ffmpeg.

## Running the Tool

```bash
# First-time setup (must be sourced, not executed)
source setup.sh

# Basic usage
python -m marp2video presentation.md --voice path/to/voice.wav

# With all TTS options
python -m marp2video presentation.md \
    --voice voice.wav \
    --device cpu \
    --exaggeration 0.5 \
    --cfg-weight 0.3 \
    --temperature 0.6 \
    --output output.mp4
```

## Architecture

The pipeline is orchestrated by `__main__.py` and flows through four modules in sequence:

1. **parser.py** -- Splits markdown on `---` delimiters, extracts speaker notes from `<!-- -->` HTML comments into `Slide` dataclasses (index, body, notes).
2. **renderer.py** -- Calls marp-cli (via npx or global install) to produce one PNG per slide. Output files are named `slides.001`, `slides.002`, etc. (no file extension).
3. **tts.py** -- Synthesizes each slide's notes with Chatterbox TTS. Long notes are split by sentence and each sentence is generated separately, then concatenated with `torch.cat` into one WAV per slide. Slides without notes get a silent WAV.
4. **assembler.py** -- Creates per-slide MPEG-TS segments (image looped for audio duration) then concatenates into the final MP4 using ffmpeg's concat demuxer.

**utils.py** provides shared helpers: ffmpeg/ffprobe checks, silent WAV generation, and audio duration queries.

## Key Conventions

- Heavy imports (torch, torchaudio, chatterbox) are lazy-loaded only when TTS is needed.
- All file paths use `pathlib.Path`. Temp files follow the pattern `audio_001.wav`, `slides.001`, `segment_001.ts`.
- Subprocess calls use `capture_output=True`; stderr is printed only on failure.
- Device auto-detection order: CUDA, MPS (Apple Silicon), CPU.
- On pipeline failure, the temp directory is preserved for debugging. On success, it's cleaned up unless `--keep-temp` is set.

## System Dependencies

Python 3.11, Node.js/npm (for marp-cli via npx), ffmpeg/ffprobe. The `setup.sh` script validates all of these, creates the venv, and installs Python packages.

## Tests

No test infrastructure exists yet.
