"""`career-pilot letter-check`: the mechanical rules for a cover letter.

It checks length, paragraphs, dashes, phrases and patterns. It cannot judge
whether a sentence is true: the agent still checks every claim against the
facts files.

Length is measured on the body: the paragraphs, without the date, a reference
line, the greeting or the sign-off.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

DEFAULT_MAX_CHARS = 2000
DEFAULT_MAX_PARAGRAPHS = 4
MIN_BLOCK_CHARS = 40  # shorter blocks are the date, the greeting or the sign-off
NOT_BODY = re.compile(r"^(dear |job reference|kind regards|sincerely|best regards|regards)", re.I)

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


def body_paragraphs(text: str) -> list[str]:
    """The paragraphs of the letter body, without date, reference line, greeting and sign-off."""
    blocks = (block.strip() for block in re.split(r"\n\s*\n", text.strip()))
    return [b for b in blocks if len(b) >= MIN_BLOCK_CHARS and not NOT_BODY.match(b)]


def check_letter(
    text: str,
    *,
    min_chars: int = 0,
    max_chars: int = DEFAULT_MAX_CHARS,
    min_paragraphs: int = 0,
    max_paragraphs: int = DEFAULT_MAX_PARAGRAPHS,
    min_paragraph_chars: int = 0,
    banned_phrases: Iterable[str] = (),
    forbidden_claims: Iterable[str] = (),
    forbidden_patterns: Iterable[str] = (),
    allow_dashes: bool = False,
) -> list[str]:
    """Problems found in a letter. An empty list means it passes the mechanical rules.

    Patterns are regular expressions. A pattern that is not valid raises re.error.
    """
    issues: list[str] = []
    paragraphs = body_paragraphs(text)

    length = len("\n\n".join(paragraphs))
    if length > max_chars:
        issues.append(f"the body is {length} characters, the maximum is {max_chars}")
    if length < min_chars:
        issues.append(f"the body is {length} characters, the minimum is {min_chars}")

    if len(paragraphs) > max_paragraphs:
        issues.append(f"{len(paragraphs)} paragraphs, the maximum is {max_paragraphs}")
    if len(paragraphs) < min_paragraphs:
        issues.append(f"{len(paragraphs)} paragraphs, the minimum is {min_paragraphs}")
    for number, paragraph in enumerate(paragraphs, start=1):
        if len(paragraph) < min_paragraph_chars:
            issues.append(
                f"paragraph {number} is {len(paragraph)} characters, the minimum is "
                f"{min_paragraph_chars}"
            )

    if not allow_dashes and any(dash in text for dash in DASHES):
        issues.append("contains an em or en dash; use a hyphen")

    lowered = text.lower()
    for phrase in (*DEFAULT_BANNED_PHRASES, *banned_phrases):
        if phrase.lower() in lowered:
            issues.append(f"uses the phrase '{phrase}'")
    for claim in forbidden_claims:
        if claim.lower() in lowered:
            issues.append(f"makes a claim the profile forbids: '{claim}'")
    for pattern in forbidden_patterns:
        if re.search(pattern, text, re.I):
            issues.append(f"matches the forbidden pattern '{pattern}'")
    return issues
