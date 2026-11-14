"""`career-pilot brief`: print only the profile keys a mode needs, to save tokens.

The full profile is long. A mode, or a subagent that cannot see the profile,
gets just its slice. The `privacy` section (your forbidden terms) is never
included in any brief.
"""

from __future__ import annotations

from typing import Any

import yaml

from career_pilot.profile import Profile, ProfileError

BRIEF_KEYS: dict[str, tuple[str, ...]] = {
    "run": (
        "candidate",
        "sources",
        "cvs",
        "answers",
        "boards",
        "search",
        "filters",
        "scoring",
        "routing",
        "routes",
        "daily_caps",
        "letters",
        "tracker",
        "sync",
        "adapters",
    ),
    "sync": ("candidate", "boards", "sync", "followup", "letters", "tracker", "adapters"),
    "review": (
        "candidate",
        "sources",
        "cvs",
        "answers",
        "letters",
        "routes",
        "tracker",
        "adapters",
    ),
    "search": ("boards", "search", "filters"),
    "score": ("scoring", "routing", "routes", "filters"),
    "apply": ("candidate", "sources", "cvs", "answers", "routes"),
}


def brief_for(profile: Profile, mode: str) -> dict[str, Any]:
    """The slice of the profile a mode needs. Raises ProfileError for an unknown mode."""
    if mode not in BRIEF_KEYS:
        raise ProfileError(f"Unknown mode '{mode}'. Choose one of: {', '.join(BRIEF_KEYS)}.")
    return {key: profile[key] for key in BRIEF_KEYS[mode] if key in profile}


def render_brief(profile: Profile, mode: str) -> str:
    """The brief as compact YAML text."""
    return yaml.safe_dump(brief_for(profile, mode), sort_keys=False, allow_unicode=True)
