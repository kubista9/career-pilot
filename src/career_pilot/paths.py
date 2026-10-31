"""Location of the data dir, where all of your private data lives."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

DATA_DIR_ENV = "CAREER_PILOT_DATA_DIR"
DEFAULT_DATA_DIR = Path("~/career-pilot-data")

# Sub-folders created inside the data dir.
DATA_SUBDIRS: tuple[str, ...] = (
    "config",
    "modes",
    "tracker",
    "applications",
    "runs",
    "logs",
    "browser-profile",
)


class DataDirError(Exception):
    """The data dir is missing or in an unsafe place."""


def resolve_data_dir(env: Mapping[str, str] | None = None) -> Path:
    """Data dir from CAREER_PILOT_DATA_DIR, else the default path."""
    environ = os.environ if env is None else env
    raw = environ.get(DATA_DIR_ENV) or str(DEFAULT_DATA_DIR)
    return Path(raw).expanduser().resolve()


def is_inside(path: Path, folder: Path) -> bool:
    """True if `path` is `folder` or somewhere below it."""
    resolved = path.resolve()
    root = folder.resolve()
    return resolved == root or root in resolved.parents


def check_data_dir(data_dir: Path, repo_root: Path) -> None:
    """Raise DataDirError unless the data dir exists outside the repo."""
    if is_inside(data_dir, repo_root):
        raise DataDirError(
            f"The data dir {display_path(data_dir)} is inside the repository. "
            f"Private data must live outside it. Set {DATA_DIR_ENV} to a folder outside the repo."
        )
    if not data_dir.resolve().is_dir():
        raise DataDirError(
            f"The data dir {display_path(data_dir)} does not exist. "
            "Create it with: career-pilot setup-check --create-data-dir"
        )


def create_data_dir(data_dir: Path, repo_root: Path) -> list[Path]:
    """Create the data dir and its sub-folders (outside the repo only)."""
    if is_inside(data_dir, repo_root):
        raise DataDirError(
            f"Refusing to create the data dir inside the repository: {display_path(data_dir)}"
        )
    root = data_dir.resolve()
    created: list[Path] = []
    for folder in (root, *(root / name for name in DATA_SUBDIRS)):
        if not folder.exists():
            folder.mkdir(parents=True, mode=0o700)
            created.append(folder)
    return created


def display_path(path: Path) -> str:
    """Show a path with the home folder abbreviated as ~."""
    home = Path.home()
    try:
        return "~/" + str(path.relative_to(home))
    except ValueError:
        return str(path)
