from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

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
