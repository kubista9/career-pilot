from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from career_pilot.privacy import (
    Finding,
    is_private_path,
    line_findings,
    local_forbidden_terms,
    scan_content,
    unprotected_private_files,
)
from tests.conftest import REPO_ROOT, git, write

# Files that would be private data if they ended up in the repo.
PRIVATE_SAMPLES = [
    ".env",
    ".env.local",
    "notion.token",
    "secrets/api.txt",
    "facts.md",
    "docs/facts.md",
    "never-claim.md",
    "Example-CV.pdf",
    "cv/letter.docx",
    "cv.md",
    "config/profile.yml",
    "modes/_profile.md",
    "modes/_custom.md",
    "private/notes.md",
    "career-pilot-data/tracker/applications.csv",
    "data/applications.csv",
    "applications/acme/cover-letter.md",
    "runs/2026-10-19/report.md",
    "logs/run.jsonl",
    "debug.log",
    "browser-profile/Default/Cookies",
    "playwright-profile/state.bin",
    "linkedin.cookies",
    "cookies.json",
    "storage-state.json",
    "linkedin.har",
    "state.sqlite",
    "state.sqlite3",
    "jobs.db",
    "facts.md.bak",
    "facts.yaml.bak-2026-10-30T10:00:00",
    ".settings.yaml.123.tmp",
    "output/report.md",
    "jds/acme.txt",
    "job-description-backend-developer.txt",
    "cover-letter.txt",
    "application-notes.txt",
    "applications.csv",
    "index.csv",
    "MOVE-MANIFEST.tsv",
]

PUBLIC_SAMPLES = [
    "README.md",
    "LICENSE",
    "src/career_pilot/cli.py",
    ".env.example",
    "config/profile.example.yml",
    "cv.example.md",
    "modes/_shared.md",
    "modes/_profile.template.md",
    "modes/_custom.template.md",
    ".claude/skills/career-pilot/SKILL.md",
    ".github/workflows/ci.yml",
    "docs/privacy.md",
    "examples/applications.example.csv",
    "tests/test_privacy.py",
]


@pytest.mark.parametrize("path", PRIVATE_SAMPLES)
def test_private_paths_are_recognised(path: str) -> None:
    assert is_private_path(path)


@pytest.mark.parametrize("path", PUBLIC_SAMPLES)
def test_public_paths_are_not_flagged(path: str) -> None:
    assert not is_private_path(path)


@pytest.mark.parametrize("path", PRIVATE_SAMPLES)
def test_gitignore_ignores_every_private_sample(path: str) -> None:
    # --no-index: check the rules themselves, independent of what is committed.
    result = git(REPO_ROOT, "check-ignore", "--no-index", "-v", path)
    assert result.strip(), f"{path} is not ignored by .gitignore"


@pytest.mark.parametrize("path", PUBLIC_SAMPLES)
def test_gitignore_keeps_public_files(path: str) -> None:
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", path], cwd=REPO_ROOT, capture_output=True
    )
    assert result.returncode == 1, f"{path} should not be ignored"


def test_private_files_copied_into_repo_stay_invisible(temp_repo: Path) -> None:
    for name in PRIVATE_SAMPLES:
        write(temp_repo / name)
    write(temp_repo / "src" / "app.py")

    assert unprotected_private_files(temp_repo) == []
    assert "facts.md" not in git(temp_repo, "status", "--porcelain", "--untracked-files=all")


def test_private_file_is_reported_without_gitignore(temp_repo: Path) -> None:
    (temp_repo / ".gitignore").unlink()
    write(temp_repo / "facts.md")
    write(temp_repo / "Example-CV.pdf")
    write(temp_repo / "src" / "app.py")

    assert unprotected_private_files(temp_repo) == ["Example-CV.pdf", "facts.md"]


def test_force_added_private_file_is_reported(temp_repo: Path) -> None:
    write(temp_repo / "jobs.db")
    git(temp_repo, "add", "--force", "jobs.db")

    assert unprotected_private_files(temp_repo) == ["jobs.db"]


# --- content scan ---------------------------------------------------------------------------

# Built from parts so this file itself never contains a real-looking value.
PHONE = "+" + "31 6" + "12 345 678"
EMAIL = "someone" + "@" + "mail.test"
HOME = "/" + "Users" + "/" + "someone" + "/docs"
UUID = "1b2c3d4e-" + "1111-2222-3333-" + "444455556666"


@pytest.mark.parametrize(
    ("line", "kind"),
    [
        (f"phone: {PHONE}", "phone number"),
        (f"email: {EMAIL}", "email address"),
        (f"path: {HOME}", "home folder path"),
        (f"id: {UUID}", "real-looking id"),
    ],
)
def test_line_findings_flag_private_looking_values(line: str, kind: str) -> None:
    assert line_findings(line) == [kind]


@pytest.mark.parametrize(
    "line",
    [
        "phone: +00 0 0000 0000",
        "email: alex@example.com",
        "email: 12345+me@users.noreply.github.com",
        "clone: git@github.com:owner/repo.git",
        "path: /Users/example/docs",
        "path: /home/runner/work",
        "id: 00000000-0000-0000-0000-000000000006",
        "python >=3.13 and +0.1 are not phone numbers",
    ],
)
def test_line_findings_allow_fake_values(line: str) -> None:
    assert line_findings(line) == []


def test_forbidden_terms_are_case_insensitive_and_never_echoed() -> None:
    assert line_findings("Born in Exampleville", ["exampleville"]) == ["forbidden term"]
    assert str(Finding("a.md", 3, "forbidden term")) == "a.md:3 (forbidden term)"


def test_scan_content_reports_file_line_and_kind_only(temp_repo: Path) -> None:
    write(temp_repo / "docs" / "notes.md", f"fine\ncall me: {PHONE}\n")
    write(temp_repo / "uv.lock", f"{EMAIL}\n")

    assert scan_content(temp_repo) == [Finding("docs/notes.md", 2, "phone number")]


def test_forbidden_terms_are_also_checked_in_file_names(temp_repo: Path) -> None:
    write(temp_repo / "docs" / "exampleville-notes.md", "fine\n")

    [finding] = scan_content(temp_repo, ["Exampleville"])

    assert finding == Finding("docs/exampleville-notes.md", 0, "forbidden term in the file name")
    assert str(finding) == "docs/exampleville-notes.md (forbidden term in the file name)"


def test_scan_content_skips_ignored_and_binary_files(temp_repo: Path) -> None:
    write(temp_repo / "cv.md", f"{PHONE}\n")  # ignored: private file
    (temp_repo / "logo.bin").write_bytes(b"\xff\xfe\x00 not text")

    assert scan_content(temp_repo) == []


def test_local_forbidden_terms_come_from_the_profile(tmp_path: Path) -> None:
    assert local_forbidden_terms(tmp_path) == []
    write(tmp_path / "config" / "profile.yml", "privacy:\n  forbidden_terms: [Exampleville, 'x']\n")

    assert local_forbidden_terms(tmp_path) == ["Exampleville", "x"]
