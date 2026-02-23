"""Tests for deck2video.detect — format auto-detection."""

from __future__ import annotations

from deck2video.detect import detect_format


class TestMarpDetection:
    def test_marp_true_in_frontmatter(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text("---\nmarp: true\ntheme: default\n---\n\n# Slide\n")
        assert detect_format(str(md)) == "marp"

    def test_marp_directive_comment_in_body(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text("---\ntitle: My Deck\n---\n\n<!-- _class: lead -->\n# Slide\n")
        assert detect_format(str(md)) == "marp"

    def test_marp_paginate_directive(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text("---\ntitle: My Deck\n---\n\n<!-- paginate: true -->\n# Slide\n")
        assert detect_format(str(md)) == "marp"


class TestSlidevDetection:
    def test_slidev_transition_frontmatter(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text("---\ntransition: slide-left\n---\n\n# Slide\n")
        assert detect_format(str(md)) == "slidev"

    def test_slidev_fonts_frontmatter(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text("---\nfonts:\n  sans: Roboto\n---\n\n# Slide\n")
        assert detect_format(str(md)) == "slidev"

    def test_slidev_drawings_frontmatter(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text("---\ndrawings:\n  enabled: true\n---\n\n# Slide\n")
        assert detect_format(str(md)) == "slidev"

    def test_slidev_vue_component_v_click(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text("---\ntitle: My Deck\n---\n\n# Slide\n\n<v-click>\nHello\n</v-click>\n")
        assert detect_format(str(md)) == "slidev"

    def test_slidev_vue_component_arrow(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text("---\ntitle: My Deck\n---\n\n<Arrow x1=\"10\" y1=\"20\" x2=\"30\" y2=\"40\" />\n")
        assert detect_format(str(md)) == "slidev"


class TestFallback:
    def test_ambiguous_defaults_to_marp(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text("---\ntitle: My Deck\n---\n\n# Just a plain slide\n")
        assert detect_format(str(md)) == "marp"

    def test_no_frontmatter_signals_defaults_to_marp(self, tmp_path):
        md = tmp_path / "deck.md"
        md.write_text("---\ntheme: default\n---\n\n# Slide 1\n---\n\n# Slide 2\n")
        assert detect_format(str(md)) == "marp"


class TestPriority:
    def test_marp_true_wins_over_slidev_keys(self, tmp_path):
        """marp: true should win even if Slidev keys are also present."""
        md = tmp_path / "deck.md"
        md.write_text("---\nmarp: true\ntransition: fade\n---\n\n# Slide\n")
        assert detect_format(str(md)) == "marp"

    def test_marp_directive_wins_over_vue_components(self, tmp_path):
        """Marp directives in body are checked before Vue components."""
        md = tmp_path / "deck.md"
        md.write_text(
            "---\ntitle: Deck\n---\n\n"
            "<!-- _class: lead -->\n"
            "<v-click>Hello</v-click>\n"
        )
        assert detect_format(str(md)) == "marp"
