"""Chatterbox TTS wrapper — synthesises speaker notes to WAV files."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from .utils import generate_silent_wav


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, keeping punctuation attached."""
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p]


def _resolve_device(device: str) -> str:
    """Pick a torch device, respecting the user's choice or auto-detecting."""
    import torch

    if device != "auto":
        print(f"  Using device: {device}")
        return device

    if torch.cuda.is_available():
        print("  Using CUDA for TTS")
        return "cuda"
    if torch.backends.mps.is_available():
        print("  Using MPS (Apple Silicon) for TTS")
        return "mps"

    print(
        "  WARNING: No GPU available — using CPU for TTS. "
        "This will be much slower.",
        file=sys.stderr,
    )
    return "cpu"


def _load_model(device: str = "auto"):
    """Load ChatterboxTTS once."""
    import torchaudio  # noqa: F401 — ensure it's importable early
    from chatterbox.tts import ChatterboxTTS

    resolved = _resolve_device(device)
    model = ChatterboxTTS.from_pretrained(device=resolved)
    return model


def generate_audio_for_slides(
    slides,
    *,
    temp_dir: Path,
    voice_path: str | None,
    device: str = "auto",
    exaggeration: float = 0.5,
    cfg_weight: float = 0.5,
    temperature: float = 0.8,
    hold_duration: float,
) -> list[Path]:
    """Generate a WAV file for every slide. Returns list of audio paths.

    Slides with speaker notes get TTS synthesis; slides without notes get a
    silent WAV of ``hold_duration`` seconds.
    """
    # Only import the heavy model when we actually need TTS.
    need_tts = any(s.notes for s in slides)
    model = _load_model(device) if need_tts else None

    import torch
    import torchaudio

    audio_paths: list[Path] = []
    errors: list[str] = []

    for slide in slides:
        out_path = temp_dir / f"audio_{slide.index:03d}.wav"

        if slide.notes is None:
            generate_silent_wav(out_path, hold_duration)
            print(f"  Slide {slide.index}: silent ({hold_duration}s)")
        else:
            try:
                sentences = _split_sentences(slide.notes)
                chunks: list = []
                for j, sentence in enumerate(sentences):
                    wav = model.generate(
                        sentence,
                        audio_prompt_path=voice_path,
                        exaggeration=exaggeration,
                        cfg_weight=cfg_weight,
                        temperature=temperature,
                    )
                    chunks.append(wav)
                    if len(sentences) > 1:
                        print(f"  Slide {slide.index}: sentence {j + 1}/{len(sentences)} OK")

                combined = torch.cat(chunks, dim=1)
                torchaudio.save(str(out_path), combined, model.sr)
                print(f"  Slide {slide.index}: TTS OK ({len(sentences)} sentence{'s' if len(sentences) != 1 else ''})")
            except Exception as exc:
                msg = f"Slide {slide.index}: TTS failed ({exc}), substituting silence"
                print(f"  {msg}", file=sys.stderr)
                errors.append(msg)
                generate_silent_wav(out_path, hold_duration)

        audio_paths.append(out_path)

    return audio_paths
