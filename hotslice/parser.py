"""Markdown parsing and slide splitting for hotslice."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field

from markdown_it import MarkdownIt


# Matches sequences of emoji characters (including ZWJ and variation selectors)
_EMOJI_RE = re.compile(
    "(["
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
    "\U0001F680-\U0001F6FF"  # Transport and Map
    "\U0001F1E0-\U0001F1FF"  # Flags
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U0000FE0F"             # Variation Selector-16
    "\U0000200D"             # Zero Width Joiner
    "]+)"
)


def _wrap_emojis(html: str) -> str:
    """Wrap emoji sequences in <span class="emoji"> outside of HTML tags.

    This allows CSS to reset gradient-text effects for emoji characters
    so they render with their native color appearance.
    """
    parts = re.split(r"(<[^>]+>)", html)
    for i, part in enumerate(parts):
        if not part.startswith("<"):
            parts[i] = _EMOJI_RE.sub(r'<span class="emoji">\1</span>', part)
    return "".join(parts)


@dataclass
class SlideData:
    """Parsed slide content."""

    html: str
    index: int
    notes: str = ""


@dataclass
class DeckData:
    """Full parsed deck with metadata."""

    slides: list[SlideData]
    title: str = ""
    frontmatter: dict = field(default_factory=dict)


def _create_parser() -> MarkdownIt:
    """Create a markdown-it-py parser with GFM-like features."""
    md = MarkdownIt("gfm-like", {"html": True, "linkify": True, "typographer": True})
    return md


def _extract_frontmatter(text: str) -> tuple[dict, str]:
    """Extract TOML frontmatter fenced by +++ lines.

    Returns (frontmatter_dict, remaining_text).
    """
    pattern = re.compile(r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n?", re.DOTALL)
    match = pattern.match(text)
    if match:
        try:
            fm = tomllib.loads(match.group(1))
        except tomllib.TOMLDecodeError:
            fm = {}
        remaining = text[match.end() :]
        return fm, remaining
    return {}, text


def _extract_title(slides_md: list[str], frontmatter: dict) -> str:
    """Extract title from frontmatter or first heading."""
    if "title" in frontmatter:
        return frontmatter["title"]

    # Look for first # heading in the first slide
    for line in slides_md[0].splitlines() if slides_md else []:
        line = line.strip()
        if line.startswith("# ") and not line.startswith("##"):
            return line.lstrip("# ").strip()

    return "Untitled Presentation"


def parse_deck(markdown_text: str, separator: str = "^---$") -> DeckData:
    """Parse a markdown string into a DeckData object.

    Splits the markdown on the separator pattern, extracts frontmatter
    from the beginning if present, and parses each slide chunk to HTML.
    """
    md = _create_parser()
    sep_re = re.compile(separator, re.MULTILINE)

    # Extract frontmatter
    frontmatter, text = _extract_frontmatter(markdown_text)

    # Split into slide chunks
    chunks = sep_re.split(text)

    # Filter out empty chunks but keep whitespace-only ones that might be intentional
    chunks = [c for c in chunks if c.strip()]

    title = _extract_title(chunks, frontmatter)

    slides = []
    for i, chunk in enumerate(chunks):
        html = _wrap_emojis(md.render(chunk.strip()))
        slides.append(SlideData(html=html, index=i))

    return DeckData(slides=slides, title=title, frontmatter=frontmatter)
