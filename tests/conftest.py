from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from career_pilot.paths import DATA_DIR_ENV

REPO_ROOT = Path(__file__).resolve().parents[1]


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """An empty git repository using this project's .gitignore."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    shutil.copy(REPO_ROOT / ".gitignore", repo / ".gitignore")
    return repo


def write(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


# A small valid profile for tests. The real example profile is tested separately.
SAMPLE_PROFILE: dict[str, Any] = {
    "candidate": {"full_name": "Test Person", "email": "test" + "@" + "mail.test"},
    "sources": {
        "facts": "~/none/facts.md",
        "letter_rules": "~/none/rules.md",
        "cv_dir": "~/none/cv",
    },
    "cvs": [{"file": "cv-software.pdf", "focus": "software"}],
    "answers": {"hours_per_week": 16, "start_date": "2027-01-04"},
    "boards": [{"name": "Board", "search_url": "https://board.test/search?q={keywords}"}],
    "search": {"groups": [{"name": "core", "keywords": ["developer"]}]},
    "scoring": {
        "tracks": {
            "default": {
                "criteria": {
                    "skill": {"max": 5},
                    "location": {"max": 2},
                    "language": {"max": 1},
                    "growth": {"max": 1},
                },
                "min": {"skill": 1},
                "threshold": 6,
            },
            "special": {
                "criteria": {"skill": {"max": 5}, "commute": {"max": 2}},
                "gates": {"commute": 1},
                "threshold": 5,
            },
        }
    },
    "routing": [
        {"when": {"apply_type": "easy_apply"}, "route": "easy_apply"},
        {
            "when": {"track": "special", "tags_any": ["needs_local_language"], "min_score": 6},
            "route": "local",
        },
        {
            "when": {
                "track": "special",
                "tags_none": ["needs_local_language"],
                "meets_threshold": True,
            },
            "route": "special",
        },
        {"when": {"meets_threshold": True}, "route": "strong"},
        {"route": "low_score"},
    ],
    "routes": {
        "strong": {"priority": 1, "auto_submit": False},
        "special": {"priority": 2, "auto_submit": False},
        "local": {"priority": 3, "auto_submit": False},
        "easy_apply": {"priority": 4, "auto_submit": True},
        "low_score": {"priority": 5, "auto_submit": True},
    },
    "daily_caps": {"approval": 10, "auto_submit": 20},
    "privacy": {"forbidden_terms": ["Exampleville"]},
}


def write_profile(data_dir: Path, profile: dict[str, Any] | None = None) -> Path:
    path = data_dir / "config" / "profile.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(SAMPLE_PROFILE if profile is None else profile))
    return path


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A data dir with the sample profile, set as CAREER_PILOT_DATA_DIR."""
    root = tmp_path / "data-dir"
    root.mkdir()
    write_profile(root)
    monkeypatch.setenv(DATA_DIR_ENV, str(root))
    return root
