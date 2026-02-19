"""marp2video — Convert a Marp markdown presentation into a narrated MP4 video."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from .assembler import assemble_video
from .parser import parse_marp
from .renderer import render_slides
from .tts import generate_audio_for_slides
from .utils import check_ffmpeg


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="marp2video",
        description="Convert a Marp markdown presentation into a narrated MP4 video.",
    )
    parser.add_argument("input", help="Path to the Marp .md file")
    parser.add_argument("--output", help="Output MP4 path (default: <input>.mp4)")
    parser.add_argument("--voice", help="Path to a reference WAV for Chatterbox voice cloning")
    parser.add_argument("--device", default="auto",
                        help="Torch device: auto, cpu, cuda, or mps (default: auto)")
    parser.add_argument("--exaggeration", type=float, default=0.5,
                        help="Chatterbox exaggeration level (default: 0.5)")
    parser.add_argument("--cfg-weight", type=float, default=0.5,
                        help="Chatterbox CFG weight (default: 0.5)")
    parser.add_argument("--temperature", type=float, default=0.8,
                        help="Chatterbox sampling temperature (default: 0.8)")
    parser.add_argument("--hold-duration", type=float, default=3.0,
                        help="Seconds to hold slides with no speaker notes (default: 3)")
    parser.add_argument("--fps", type=int, default=24, help="Output framerate (default: 24)")
    parser.add_argument("--temp-dir", help="Where to write intermediate files (default: system temp)")
    parser.add_argument("--keep-temp", action="store_true",
                        help="Don't delete intermediate files after rendering")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found.", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_suffix(".mp4")

    # Pre-flight checks
    check_ffmpeg()

    # Set up temp directory
    if args.temp_dir:
        temp_dir = Path(args.temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        user_temp = True
    else:
        temp_dir = Path(tempfile.mkdtemp(prefix="marp2video_"))
        user_temp = False

    try:
        # Step 1: Parse
        print("[1/4] Parsing slides…")
        slides = parse_marp(str(input_path))
        print(f"  Found {len(slides)} slides")

        # Step 2: Render images
        print("[2/4] Rendering slide images…")
        images = render_slides(str(input_path), temp_dir, expected_count=len(slides))

        # Step 3: Generate audio
        print("[3/4] Generating audio…")
        audio_files = generate_audio_for_slides(
            slides,
            temp_dir=temp_dir,
            voice_path=args.voice,
            device=args.device,
            exaggeration=args.exaggeration,
            cfg_weight=args.cfg_weight,
            temperature=args.temperature,
            hold_duration=args.hold_duration,
        )

        # Step 4: Assemble video
        print("[4/4] Assembling video…")
        assemble_video(
            images,
            audio_files,
            output_path,
            temp_dir=temp_dir,
            fps=args.fps,
        )

        # Summary
        tts_count = sum(1 for s in slides if s.notes)
        silent_count = len(slides) - tts_count
        print(
            f"\nDone! {len(slides)} slides processed "
            f"({tts_count} narrated, {silent_count} silent)."
        )
        print(f"Output: {output_path}")

    except Exception:
        print(f"\nError encountered. Temp files preserved at: {temp_dir}", file=sys.stderr)
        raise

    else:
        # Cleanup on success
        if not args.keep_temp and not user_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)
        elif args.keep_temp:
            print(f"Temp files kept at: {temp_dir}")


if __name__ == "__main__":
    main()
