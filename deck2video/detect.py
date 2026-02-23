"""Auto-detect whether a markdown file is a Marp or Slidev presentation."""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Slidev-only frontmatter keys (not used by Marp)
_SLIDEV_FRONTMATTER_KEYS = {
    "transition",
    "clicks",
    "drawings",
    "routerMode",
    "aspectRatio",
    "canvasWidth",
    "themeConfig",
    "fonts",
    "favicon",
    "titleTemplate",
}

# Marp directive comments: <!-- _class: ... -->, <!-- paginate: ... -->, etc.
_MARP_DIRECTIVE_RE = re.compile(
    r"<!--\s*_?\s*(class|paginate|header|footer|backgroundColor|backgroundImage|"
    r"backgroundPosition|backgroundRepeat|backgroundSize|color|theme|math|"
    r"size|style|headingDivider)\s*:",
    re.IGNORECASE,
)

# Vue/Slidev component syntax
_VUE_COMPONENT_RE = re.compile(
    r"<(v-click|v-clicks|v-after|v-click-hide|Arrow|RenderWhen|SlidevVideo)\b",
)


def detect_format(path: str) -> str:
    """Detect whether *path* is a Marp or Slidev presentation.

    Returns ``"marp"`` or ``"slidev"``.
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # --- 1. Parse YAML frontmatter (first --- block) ---
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # 2. Explicit marp: true
        if re.search(r"^\s*marp\s*:\s*true\s*$", frontmatter, re.MULTILINE):
            logger.info("Detected Marp format (marp: true in frontmatter)")
            return "marp"

        # 3. Slidev-only frontmatter keys
        for line in frontmatter.splitlines():
            key_match = re.match(r"^\s*(\w+)\s*:", line)
            if key_match and key_match.group(1) in _SLIDEV_FRONTMATTER_KEYS:
                logger.info(
                    "Detected Slidev format (frontmatter key: %s)",
                    key_match.group(1),
                )
                return "slidev"

    # --- Body checks (everything after frontmatter) ---
    body = content
    if frontmatter_match:
        body = content[frontmatter_match.end() :]

    # 4. Marp directive comments in body
    if _MARP_DIRECTIVE_RE.search(body):
        logger.info("Detected Marp format (directive comments in body)")
        return "marp"

    # 5. Vue/Slidev component syntax
    if _VUE_COMPONENT_RE.search(body):
        logger.info("Detected Slidev format (Vue component syntax in body)")
        return "slidev"

    # 6. Fallback — Marp (backward compatible)
    logger.info("No format signals found, defaulting to Marp")
    return "marp"
