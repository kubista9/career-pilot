"""Guards that keep private data out of the git repository.

Private data (profile, CV, personal rules, tokens, browser state, the tracker,
generated applications) lives in the data dir outside the repo. These checks
are a second line of defence for files that end up in the repo by mistake:
one looks at file names, the other at file contents. Neither ever prints the
text it matched, only the file, the line and the kind of finding.
"""

from __future__ import annotations

import fnmatch
import re
import shutil
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

# Keep in sync with the PRIVATE DATA section of .gitignore.
PRIVATE_PATTERNS: tuple[str, ...] = (
    ".env",
    ".env.*",
    "*.token",
    "*.key",
    "secrets/*",
    "profile.yml",
    "cv.md",
    "facts.md",
    "never-claim*",
    "_profile.md",
    "_custom.md",
    "*.pdf",
    "*.docx",
    "private/*",
    "career-pilot-data/*",
    "/data/*",
    "applications/*",
    "runs/*",
    "logs/*",
    "*.log",
    "browser-profile/*",
    "playwright-profile/*",
    "*.cookies",
    "cookies.json",
    "storage-state.json",
    "*.har",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "*.bak*",
    "*.tmp*",
    "output/*",
    "jds/*",
    "job-description-*.txt",
    "cover-letter*.txt",
    "application-notes.txt",
    "applications.csv",
    "index.csv",
    "MOVE-MANIFEST.tsv",
)

# Files that look private by name but are safe templates.
ALLOWED_FILES: tuple[str, ...] = (".env.example",)

# Content scan: files that are never scanned.
SKIP_SUFFIXES: tuple[str, ...] = (".lock", ".png", ".jpg", ".jpeg", ".gif", ".ico")
MAX_SCAN_BYTES = 1_000_000

PHONE = re.compile(r"\+\d[\d \-()]{7,}\d")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)")
HOME_PATH = re.compile(r"/(?:Users|home)/([A-Za-z0-9._-]+)/")
UUID = re.compile(
    r"\b([0-9a-fA-F]{8})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-[0-9a-fA-F]{12}\b"
)

SAFE_EMAIL_DOMAINS = ("example.com", "example.org", "example.net", "users.noreply.github.com")
SAFE_EMAILS = ("git@github.com",)
SAFE_HOME_NAMES = ("example", "you", "user", "yourname", "name", "runner", "alex")


@dataclass(frozen=True)
class Finding:
    """A private-looking value in a file. Holds no matched text, only where and what kind."""

    path: str
    line: int
    kind: str

    def __str__(self) -> str:
        where = self.path if self.line == 0 else f"{self.path}:{self.line}"
        return f"{where} ({self.kind})"


def is_private_path(relative_path: str) -> bool:
    """Return True if a repo-relative path looks like private data."""
    path = PurePosixPath(relative_path)
    if path.name in ALLOWED_FILES:
        return False
    for pattern in PRIVATE_PATTERNS:
        if pattern.startswith("/") and pattern.endswith("/*"):
            # Anchored folder: only at the top of the repository.
            if len(path.parts) > 1 and path.parts[0] == pattern[1:-2]:
                return True
        elif pattern.endswith("/*"):
            folder = pattern[:-2]
            if folder in path.parts[:-1]:
                return True
        elif fnmatch.fnmatch(path.name, pattern):
            return True
    return False


def git_executable() -> str:
    """Absolute path of the git executable."""
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git is not installed or not on PATH.")
    return git


def visible_repo_files(repo_root: Path) -> list[str]:
    """Files git would track: committed ones plus untracked ones not ignored."""
    result = subprocess.run(  # noqa: S603 - fixed git arguments, no user input
        [git_executable(), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    return [name for name in result.stdout.decode().split("\0") if name]


def unprotected_private_files(repo_root: Path) -> list[str]:
    """Private-looking files that git tracks or would pick up with `git add`."""
    return sorted(name for name in visible_repo_files(repo_root) if is_private_path(name))


def line_findings(line: str, forbidden_terms: Iterable[str] = ()) -> list[str]:
    """Kinds of private-looking values found in one line of text."""
    kinds: list[str] = []
    if any(
        digits.strip("0") for digits in (re.sub(r"\D", "", m.group()) for m in PHONE.finditer(line))
    ):
        kinds.append("phone number")
    for email in EMAIL.finditer(line):
        domain = email.group(1).lower()
        if email.group().lower() not in SAFE_EMAILS and domain not in SAFE_EMAIL_DOMAINS:
            kinds.append("email address")
            break
    if any(m.group(1).lower() not in SAFE_HOME_NAMES for m in HOME_PATH.finditer(line)):
        kinds.append("home folder path")
    for uuid in UUID.finditer(line):
        # The fake IDs in the examples start with four all-zero groups.
        if "".join(uuid.group(1, 2, 3, 4)).strip("0"):
            kinds.append("real-looking id")
            break
    lowered = line.lower()
    if any(term.lower() in lowered for term in forbidden_terms if term.strip()):
        kinds.append("forbidden term")
    return kinds


def scan_content(repo_root: Path, forbidden_terms: Iterable[str] = ()) -> list[Finding]:
    """Scan every text file git would track for phone numbers, emails, home paths and ids.

    `forbidden_terms` are checked too, in file names and in contents (your own name,
    address, the name of your private files ...). They come from
    your private profile, so they only exist on your machine, never in CI.
    """
    terms = list(forbidden_terms)
    findings: list[Finding] = []
    for name in visible_repo_files(repo_root):
        if any(term.lower() in name.lower() for term in terms if term.strip()):
            findings.append(Finding(name, 0, "forbidden term in the file name"))
        path = repo_root / name
        if name.endswith(SKIP_SUFFIXES) or not path.is_file():
            continue
        if path.stat().st_size > MAX_SCAN_BYTES:
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            findings.extend(Finding(name, number, kind) for kind in line_findings(line, terms))
    return findings


def local_forbidden_terms(data_dir: Path) -> list[str]:
    """Terms from privacy.forbidden_terms in the profile in the data dir, if there is one."""
    import yaml  # local import: only needed when a profile exists

    profile = data_dir / "config" / "profile.yml"
    if not profile.is_file():
        return []
    loaded = yaml.safe_load(profile.read_text())
    if not isinstance(loaded, dict):
        return []
    privacy = loaded.get("privacy")
    terms = privacy.get("forbidden_terms") if isinstance(privacy, dict) else None
    return [str(term) for term in terms] if isinstance(terms, list) else []
