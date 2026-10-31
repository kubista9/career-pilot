from __future__ import annotations

import stat
from pathlib import Path

import pytest

from career_pilot.paths import (
    DATA_DIR_ENV,
    DATA_SUBDIRS,
    DataDirError,
    check_data_dir,
    create_data_dir,
    resolve_data_dir,
)


def test_default_data_dir_is_in_the_home_folder() -> None:
    assert resolve_data_dir({}) == (Path.home() / "career-pilot-data").resolve()


def test_env_variable_overrides_data_dir(tmp_path: Path) -> None:
    assert resolve_data_dir({DATA_DIR_ENV: str(tmp_path / "p")}) == (tmp_path / "p")


def test_missing_data_dir_explains_how_to_create_it(tmp_path: Path) -> None:
    with pytest.raises(DataDirError, match="--create-data-dir"):
        check_data_dir(tmp_path / "missing", repo_root=tmp_path / "repo")


def test_data_dir_inside_repo_is_rejected(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "private").mkdir(parents=True)
    with pytest.raises(DataDirError, match="inside the repository"):
        check_data_dir(repo / "private", repo_root=repo)


def test_create_data_dir_makes_owner_only_folders(tmp_path: Path) -> None:
    root = tmp_path / "data-dir"
    created = create_data_dir(root, repo_root=tmp_path / "repo")

    assert root in created
    for name in DATA_SUBDIRS:
        assert (root / name).is_dir()
    assert stat.S_IMODE(root.stat().st_mode) == 0o700
    check_data_dir(root, repo_root=tmp_path / "repo")


def test_create_data_dir_is_idempotent(tmp_path: Path) -> None:
    root = tmp_path / "data-dir"
    create_data_dir(root, repo_root=tmp_path / "repo")
    assert create_data_dir(root, repo_root=tmp_path / "repo") == []


def test_create_refuses_inside_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    with pytest.raises(DataDirError, match="Refusing"):
        create_data_dir(repo / "private", repo_root=repo)
    assert not (repo / "private").exists()
