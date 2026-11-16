from __future__ import annotations

from pathlib import Path

import pytest

from career_pilot.cli import EXIT_DATA_DIR, EXIT_OK, EXIT_PRIVATE_FILES, EXIT_PROFILE, main
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


# --- a broken profile -----------------------------------------------------------------------


def profile_in(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, content: str | bytes) -> None:
    path = tmp_path / "data" / "config" / "profile.yml"
    path.parent.mkdir(parents=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)
    monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path / "data"))


def test_broken_yaml_fails_with_the_line_number_and_no_profile_text(
    in_repo: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_in(tmp_path, monkeypatch, "privacy:\n  forbidden_terms: [Exampleville, \n  : : x\n")

    assert main(["privacy-check"]) == EXIT_PROFILE
    out = capsys.readouterr().out
    assert "Profile: PROBLEM" in out
    assert "line 3" in out
    assert "Exampleville" not in out
    assert "File contents: OK" in out  # the scan still ran


@pytest.mark.parametrize(
    "content",
    [
        b"privacy:\n  forbidden_terms: [\xff\xfe]\n",
        "- Exampleville\n",
        "privacy:\n  forbidden_terms: Exampleville\n",
        "privacy:\n  forbidden_terms: [Exampleville, [nested]]\n",
    ],
    ids=["not-utf8", "list-profile", "string-terms", "nested-term"],
)
def test_unusable_profile_fails_with_code_3(
    in_repo: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    content: str | bytes,
) -> None:
    profile_in(tmp_path, monkeypatch, content)

    assert main(["privacy-check"]) == EXIT_PROFILE
    out = capsys.readouterr().out
    assert "Profile: PROBLEM" in out
    assert "Exampleville" not in out
    assert main(["setup-check", "--repo-only"]) == EXIT_PROFILE


def test_number_terms_are_checked_as_text(
    in_repo: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_in(tmp_path, monkeypatch, "privacy:\n  forbidden_terms: [4321]\n")
    write(in_repo / "notes.md", "flat 4321\n")

    assert main(["privacy-check"]) == EXIT_PRIVATE_FILES
    assert "notes.md:1 (forbidden term)" in capsys.readouterr().out


def test_broken_profile_and_a_private_value_are_both_reported(
    in_repo: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_in(tmp_path, monkeypatch, "privacy:\n  forbidden_terms: [\n")
    write(in_repo / "notes.md", "call " + "06 " + "1234 5678\n")

    assert main(["privacy-check"]) == EXIT_PRIVATE_FILES
    out = capsys.readouterr().out
    assert "Profile: PROBLEM" in out
    assert "notes.md:1 (phone number)" in out


def test_no_profile_is_fine_and_silent(
    in_repo: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path))

    assert main(["privacy-check"]) == EXIT_OK
    assert "Profile" not in capsys.readouterr().out


def test_doctor_on_broken_yaml_does_not_print_the_snippet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    profile_in(tmp_path, monkeypatch, "answers:\n  note: Exampleville\n  : : x\n")

    assert main(["doctor"]) == EXIT_PROFILE
    out = capsys.readouterr().out
    assert "line 3" in out
    assert "Exampleville" not in out
