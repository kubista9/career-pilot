from __future__ import annotations

from pathlib import Path

import pytest

from career_pilot.cli import EXIT_DATA_DIR, EXIT_OK, EXIT_PRIVATE_FILES, main
from career_pilot.paths import DATA_DIR_ENV
from tests.conftest import write


@pytest.fixture
def in_repo(temp_repo: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(temp_repo)
    return temp_repo


def test_setup_check_passes_with_data_dir_outside_repo(
    in_repo: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "data-dir"
    root.mkdir()
    monkeypatch.setenv(DATA_DIR_ENV, str(root))

    assert main(["setup-check"]) == EXIT_OK
    out = capsys.readouterr().out
    assert "exists, outside the repo" in out
    assert "Private files: OK" in out
    assert "File contents: OK" in out


def test_missing_data_dir_fails_and_creates_nothing_in_repo(
    in_repo: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path / "missing"))
    before = sorted(p.name for p in in_repo.iterdir())

    assert main(["setup-check"]) == EXIT_DATA_DIR
    assert "does not exist" in capsys.readouterr().out
    assert sorted(p.name for p in in_repo.iterdir()) == before
    assert not (tmp_path / "missing").exists()


def test_repo_only_skips_the_data_dir(
    in_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path / "missing"))

    assert main(["setup-check", "--repo-only"]) == EXIT_OK


def test_create_flag_creates_data_dir(
    in_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "new-root"
    monkeypatch.setenv(DATA_DIR_ENV, str(root))

    assert main(["setup-check", "--create-data-dir"]) == EXIT_OK
    assert (root / "tracker").is_dir()


def test_data_dir_inside_repo_fails(
    in_repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv(DATA_DIR_ENV, str(in_repo / "private"))

    assert main(["setup-check", "--create-data-dir"]) == EXIT_DATA_DIR
    assert "inside the repository" in capsys.readouterr().out
    assert not (in_repo / "private").exists()


def test_private_file_in_repo_is_reported(
    in_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (in_repo / ".gitignore").unlink()
    write(in_repo / "facts.md", "fake facts\n")

    assert main(["privacy-check"]) == EXIT_PRIVATE_FILES
    out = capsys.readouterr().out
    assert "facts.md" in out
    assert "fake facts" not in out  # names only, never contents


def test_private_value_in_a_file_is_reported_without_showing_it(
    in_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    secret = "+" + "31 6" + "12 345 678"
    write(in_repo / "notes.md", f"call {secret}\n")

    assert main(["privacy-check"]) == EXIT_PRIVATE_FILES
    out = capsys.readouterr().out
    assert "notes.md:1 (phone number)" in out
    assert secret not in out
