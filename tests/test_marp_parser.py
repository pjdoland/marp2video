"""Tests for deck2video.marp_parser — Marp markdown parsing."""

from __future__ import annotations

import textwrap

import pytest

from deck2video.marp_parser import parse_marp
from deck2video.models import Slide


# ---------------------------------------------------------------------------
# Basic parsing
# ---------------------------------------------------------------------------

class TestBasicParsing:
    def test_minimal_deck(self, tmp_deck):
        slides = parse_marp(str(tmp_deck))
        assert len(slides) == 2

    def test_slide_indices_start_at_one(self, tmp_deck):
        slides = parse_marp(str(tmp_deck))
        assert slides[0].index == 1
        assert slides[1].index == 2

    def test_notes_extracted(self, tmp_deck):
        slides = parse_marp(str(tmp_deck))
        assert slides[0].notes == "Hello world."

    def test_slide_without_notes(self, tmp_deck):
        slides = parse_marp(str(tmp_deck))
        assert slides[1].notes is None

    def test_body_does_not_contain_comments(self, tmp_deck):
        slides = parse_marp(str(tmp_deck))
        assert "<!--" not in slides[0].body
        assert "Hello world" not in slides[0].body

    def test_body_preserved(self, tmp_deck):
        slides = parse_marp(str(tmp_deck))
        assert "# Slide One" in slides[0].body


# ---------------------------------------------------------------------------
# Front matter handling
# ---------------------------------------------------------------------------

class TestFrontMatter:
    def test_front_matter_skipped(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text(textwrap.dedent("""\
            ---
            marp: true
            theme: default
            paginate: true
            ---

            # Only Slide

            <!-- Notes here. -->
            """))
        slides = parse_marp(str(md))
        assert len(slides) == 1
        assert "marp" not in slides[0].body
        assert "theme" not in slides[0].body

    def test_no_separators_raises(self, tmp_path):
        md = tmp_path / "bad.md"
        md.write_text("# Just a heading\n\nSome text.")
        with pytest.raises(ValueError, match="No slide separators"):
            parse_marp(str(md))


# ---------------------------------------------------------------------------
# Multi-line and multiple comments
# ---------------------------------------------------------------------------

class TestComments:
    def test_multiline_notes(self, tmp_path):
        md = tmp_path / "multi.md"
        md.write_text(textwrap.dedent("""\
            ---
            marp: true
            ---

            # Slide

            <!-- First line.
            Second line. -->
            """))
        slides = parse_marp(str(md))
        assert "First line." in slides[0].notes
        assert "Second line." in slides[0].notes

    def test_multiple_comments_concatenated(self, tmp_path):
        md = tmp_path / "multi.md"
        md.write_text(textwrap.dedent("""\
            ---
            marp: true
            ---

            # Slide

            <!-- Part one. -->

            Some body text.

            <!-- Part two. -->
            """))
        slides = parse_marp(str(md))
        assert "Part one." in slides[0].notes
        assert "Part two." in slides[0].notes

    def test_empty_comment_produces_empty_notes(self, tmp_path):
        md = tmp_path / "empty.md"
        md.write_text(textwrap.dedent("""\
            ---
            marp: true
            ---

            # Slide

            <!--  -->
            """))
        slides = parse_marp(str(md))
        # Whitespace-only comment gets stripped to empty string, which is
        # still joined into notes (not None).
        assert slides[0].notes == ""


# ---------------------------------------------------------------------------
# Marp directive filtering
# ---------------------------------------------------------------------------

class TestDirectiveFiltering:
    @pytest.mark.parametrize("directive", [
        "_class: lead",
        "_paginate: false",
        "paginate: true",
        "backgroundColor: #fff",
        "backgroundImage: url(bg.png)",
        "header: My Header",
        "footer: My Footer",
        "color: red",
        "theme: gaia",
        "style: section { color: red; }",
    ])
    def test_directive_not_in_notes(self, tmp_path, directive):
        md = tmp_path / "dir.md"
        md.write_text(textwrap.dedent(f"""\
            ---
            marp: true
            ---

            <!-- {directive} -->

            # Slide
            """))
        slides = parse_marp(str(md))
        assert slides[0].notes is None

    def test_directive_mixed_with_notes(self, tmp_path):
        md = tmp_path / "mix.md"
        md.write_text(textwrap.dedent("""\
            ---
            marp: true
            ---

            <!-- _class: lead -->

            # Slide

            <!-- This is actual narration. -->
            """))
        slides = parse_marp(str(md))
        assert slides[0].notes == "This is actual narration."


# ---------------------------------------------------------------------------
# Video directive
# ---------------------------------------------------------------------------

class TestVideoDirective:
    def test_video_path_extracted(self, tmp_deck_with_video):
        slides = parse_marp(str(tmp_deck_with_video))
        assert slides[1].video == "assets/demo.mov"

    def test_video_slide_still_has_notes(self, tmp_deck_with_video):
        slides = parse_marp(str(tmp_deck_with_video))
        assert slides[1].notes == "Watch the demo."

    def test_non_video_slides_have_no_video(self, tmp_deck_with_video):
        slides = parse_marp(str(tmp_deck_with_video))
        assert slides[0].video is None
        assert slides[2].video is None

    def test_video_not_in_notes(self, tmp_deck_with_video):
        slides = parse_marp(str(tmp_deck_with_video))
        assert "assets/demo.mov" not in (slides[1].notes or "")

    def test_video_case_insensitive(self, tmp_path):
        md = tmp_path / "vid.md"
        md.write_text(textwrap.dedent("""\
            ---
            marp: true
            ---

            <!-- Video: recording.mp4 -->

            # Demo
            """))
        slides = parse_marp(str(md))
        assert slides[0].video == "recording.mp4"

    def test_video_path_with_spaces(self, tmp_path):
        md = tmp_path / "vid.md"
        md.write_text(textwrap.dedent("""\
            ---
            marp: true
            ---

            <!-- video: my recordings/demo file.mov -->

            # Demo
            """))
        slides = parse_marp(str(md))
        assert slides[0].video == "my recordings/demo file.mov"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_many_slides(self, tmp_path):
        parts = ["---\nmarp: true\n---\n"]
        for i in range(20):
            parts.append(f"\n# Slide {i+1}\n\n<!-- Note {i+1}. -->\n")
        md = tmp_path / "big.md"
        md.write_text("\n---\n".join(parts))
        slides = parse_marp(str(md))
        assert len(slides) == 20
        assert slides[19].index == 20

    def test_slide_with_only_body(self, tmp_path):
        md = tmp_path / "body.md"
        md.write_text(textwrap.dedent("""\
            ---
            marp: true
            ---

            # Just a heading

            Some content but no comments at all.
            """))
        slides = parse_marp(str(md))
        assert slides[0].notes is None
        assert "Just a heading" in slides[0].body

    def test_slide_dataclass_defaults(self):
        s = Slide(index=1, body="hello", notes=None)
        assert s.video is None
