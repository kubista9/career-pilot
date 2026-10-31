"""`career-pilot letter-check`: the mechanical rules for a cover letter.

It checks length, paragraphs, dashes and phrases. It cannot judge whether a
sentence is true: the agent still checks every claim against the facts files.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

DEFAULT_MAX_CHARS = 2000
DEFAULT_MAX_PARAGRAPHS = 4
MIN_PARAGRAPH_CHARS = 40  # shorter blocks are the greeting, a reference line or the sign-off

# Phrases that make a letter read as machine-written. Add your own in letters.banned_phrases.
DEFAULT_BANNED_PHRASES: tuple[str, ...] = (
    "i am writing to express",
    "i am excited to apply",
    "passionate about",
    "dynamic environment",
    "fast-paced",
    "delve",
    "tapestry",
    "leverage my",
    "proven track record",
    "synergy",
)

DASHES = ("—", "–")  # em dash, en dash


def check_letter(
    text: str,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
    max_paragraphs: int = DEFAULT_MAX_PARAGRAPHS,
    banned_phrases: Iterable[str] = (),
    forbidden_claims: Iterable[str] = (),
    allow_dashes: bool = False,
) -> list[str]:
    """Problems found in a letter. An empty list means it passes the mechanical rules."""
    issues: list[str] = []
    length = len(text.strip())
    if length > max_chars:
        issues.append(f"{length} characters, the limit is {max_chars}")

    paragraphs = [
        block
        for block in re.split(r"\n\s*\n", text.strip())
        if len(block.strip()) >= MIN_PARAGRAPH_CHARS
    ]
    if len(paragraphs) > max_paragraphs:
        issues.append(f"{len(paragraphs)} paragraphs, the limit is {max_paragraphs}")

    if not allow_dashes and any(dash in text for dash in DASHES):
        issues.append("contains an em or en dash; use a hyphen")

    lowered = text.lower()
    for phrase in (*DEFAULT_BANNED_PHRASES, *banned_phrases):
        if phrase.lower() in lowered:
            issues.append(f"uses the phrase '{phrase}'")
    for claim in forbidden_claims:
        if claim.lower() in lowered:
            issues.append(f"makes a claim the profile forbids: '{claim}'")
    return issues
