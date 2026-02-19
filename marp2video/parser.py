"""Marp markdown parser — splits slides and extracts speaker notes."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Slide:
    index: int
    body: str
    notes: str | None


# Matches HTML comments, including multi-line ones.
_COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)

# Marp directive comments start with an underscore or a known directive keyword.
# These should not be treated as speaker notes.
_DIRECTIVE_RE = re.compile(
    r"^\s*_?\s*(class|paginate|header|footer|backgroundColor|backgroundImage|"
    r"backgroundPosition|backgroundRepeat|backgroundSize|color|theme|math|marp|"
    r"size|style|headingDivider|lang|title|description|author|image|keywords|url)\b",
    re.IGNORECASE,
)


def parse_marp(path: str) -> list[Slide]:
    """Parse a Marp markdown file into a list of Slide objects.

    The file is split on ``---`` delimiters (horizontal rules that Marp uses
    as slide separators).  The first ``---`` block is treated as YAML front
    matter and is skipped.  For every remaining block we extract HTML comments
    as speaker notes and treat everything else as the slide body.
    """
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    # Split on lines that are exactly "---" (possibly with surrounding whitespace).
    parts = re.split(r"\n---\s*\n", raw)

    # The first part is the YAML front-matter block — skip it.
    if len(parts) < 2:
        raise ValueError(
            "No slide separators (---) found. Is this a valid Marp deck?"
        )

    slide_parts = parts[1:]  # everything after front matter
    slides: list[Slide] = []

    for i, part in enumerate(slide_parts):
        notes_fragments: list[str] = []

        def _collect(m: re.Match) -> str:
            content = m.group(1).strip()
            # Skip Marp directive comments (e.g. <!-- _class: lead -->)
            if _DIRECTIVE_RE.match(content):
                return ""
            notes_fragments.append(content)
            return ""

        body = _COMMENT_RE.sub(_collect, part).strip()
        notes = "\n".join(notes_fragments) if notes_fragments else None

        slides.append(Slide(index=i + 1, body=body, notes=notes))

    return slides
