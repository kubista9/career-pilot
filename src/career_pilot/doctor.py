"""`career-pilot doctor`: is the profile complete, and can the agent read what it points to?"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from career_pilot.paths import display_path
from career_pilot.profile import Profile, ProfileError, load_profile, lookup

# Keys the modes cannot work without.
REQUIRED_KEYS: tuple[str, ...] = (
    "candidate.full_name",
    "candidate.email",
    "sources.facts",
    "sources.letter_rules",
    "sources.cv_dir",
    "cvs",
    "answers.hours_per_week",
    "answers.start_date",
    "boards",
    "search.groups",
    "scoring.tracks",
    "routing",
    "routes",
    "daily_caps",
)

ZERO_PHONE = re.compile(r"^\+?[\s\-()0]+$")


@dataclass(frozen=True)
class Issue:
    level: str  # "error" or "warning"
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper()}: {self.message}"


def example_values(node: Any, prefix: str = "") -> list[str]:
    """Keys whose value still looks like the example profile (Alex Example, example.com, ...)."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            found.extend(example_values(value, f"{prefix}{key}."))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.extend(example_values(value, f"{prefix}{index}."))
    elif isinstance(node, str) and (
        "example" in node.lower() or (node.strip() and ZERO_PHONE.match(node))
    ):
        found.append(prefix.rstrip("."))
    return found


def missing_keys(profile: Profile) -> list[str]:
    return [key for key in REQUIRED_KEYS if lookup(profile, key) in (None, "", [], {})]


def check_files(profile: Profile, data_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    for key in ("sources.facts", "sources.letter_rules"):
        value = lookup(profile, key)
        if value and not Path(str(value)).expanduser().is_file():
            issues.append(Issue("warning", f"{key} points to a file that does not exist"))
    cv_dir_value = lookup(profile, "sources.cv_dir")
    cvs = lookup(profile, "cvs", [])
    if cv_dir_value and isinstance(cvs, list):
        cv_dir = Path(str(cv_dir_value)).expanduser()
        for cv in cvs:
            name = cv.get("file") if isinstance(cv, dict) else None
            if name and not (cv_dir / str(name)).is_file():
                issues.append(Issue("warning", f"CV file {name} is not in sources.cv_dir"))
    if not (data_dir / "cv.md").is_file():
        issues.append(Issue("warning", "cv.md is missing from the data dir"))
    return issues


def run_doctor(data_dir: Path) -> list[Issue]:
    """Everything wrong or unfinished in the profile. An empty list means ready to run."""
    if not data_dir.is_dir():
        return [Issue("error", f"The data dir {display_path(data_dir)} does not exist")]
    try:
        profile = load_profile(data_dir)
    except ProfileError as error:
        return [Issue("error", str(error))]

    issues = [Issue("error", f"{key} is missing or empty") for key in missing_keys(profile)]
    issues.extend(
        Issue("warning", f"{key} still looks like an example value")
        for key in example_values(profile)
        if not key.startswith("privacy.")
    )
    issues.extend(check_files(profile, data_dir))
    return issues
