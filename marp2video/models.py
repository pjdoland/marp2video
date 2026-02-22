"""Shared data models and parsing constants."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Slide:
    index: int
    body: str
    notes: str | None
    video: str | None = None


# Matches HTML comments, including multi-line ones.
COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)

# Video directive: <!-- video: path/to/file.mov -->
VIDEO_RE = re.compile(r"^\s*video:\s*(.+?)\s*$", re.IGNORECASE)
