"""Shared fixtures for marp2video tests."""

from __future__ import annotations

import textwrap

import pytest


# ---------------------------------------------------------------------------
# Minimal Marp decks (strings) used across multiple test modules
# ---------------------------------------------------------------------------

MINIMAL_DECK = textwrap.dedent("""\
    ---
    marp: true
    ---

    # Slide One

    <!-- Hello world. -->

    ---

    # Slide Two
    """)

DECK_WITH_VIDEO = textwrap.dedent("""\
    ---
    marp: true
    ---

    # Static Slide

    <!-- Narration for slide one. -->

    ---

    # Demo

    <!-- video: assets/demo.mov -->

    <!-- Watch the demo. -->

    ---

    # End
    """)

DECK_DIRECTIVES_ONLY = textwrap.dedent("""\
    ---
    marp: true
    ---

    <!-- _class: lead -->
    <!-- _paginate: false -->

    # Title
    """)


@pytest.fixture
def tmp_deck(tmp_path):
    """Write MINIMAL_DECK to a temp file and return its path."""
    p = tmp_path / "deck.md"
    p.write_text(MINIMAL_DECK)
    return p


@pytest.fixture
def tmp_deck_with_video(tmp_path):
    """Write DECK_WITH_VIDEO to a temp file and return its path."""
    p = tmp_path / "deck.md"
    p.write_text(DECK_WITH_VIDEO)
    return p


@pytest.fixture
def silent_wav(tmp_path):
    """Generate a short silent WAV and return its path."""
    from marp2video.utils import generate_silent_wav

    p = tmp_path / "silence.wav"
    generate_silent_wav(p, duration=1.0)
    return p
