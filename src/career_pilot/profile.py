"""Load the user's profile (config/profile.yml in the data dir)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from career_pilot.paths import display_path

PROFILE_RELATIVE = Path("config") / "profile.yml"

Profile = dict[str, Any]


class ProfileError(Exception):
    """The profile is missing, unreadable or does not make sense."""


def profile_path(data_dir: Path) -> Path:
    return data_dir / PROFILE_RELATIVE


def load_profile(data_dir: Path) -> Profile:
    """Read the profile. Raises ProfileError with a fix when it cannot be used."""
    path = profile_path(data_dir)
    if not path.is_file():
        raise ProfileError(
            f"No profile at {display_path(path)}. "
            "Copy config/profile.example.yml there and fill in your own values."
        )
    try:
        loaded = yaml.safe_load(path.read_text())
    except yaml.YAMLError as error:
        raise ProfileError(f"{display_path(path)} is not valid YAML: {error}") from error
    if not isinstance(loaded, dict):
        raise ProfileError(f"{display_path(path)} must be a YAML mapping of keys and values.")
    return loaded


def optional_profile(data_dir: Path) -> Profile:
    """The profile if there is one, else an empty one (for tools that have defaults)."""
    if not profile_path(data_dir).is_file():
        return {}
    return load_profile(data_dir)


def lookup(profile: Profile, dotted_key: str, default: Any = None) -> Any:
    """Value at a dotted key such as `answers.start_date`, or the default."""
    node: Any = profile
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def data_path(data_dir: Path, value: object, default: str) -> Path:
    """A path from the profile: `~` expanded, relative paths resolved against the data dir."""
    raw = Path(str(value) if value else default).expanduser()
    return raw if raw.is_absolute() else data_dir / raw
