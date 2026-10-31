"""Command-line entry point: `career-pilot <command>`."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from career_pilot import __version__
from career_pilot.paths import (
    DataDirError,
    check_data_dir,
    create_data_dir,
    display_path,
    resolve_data_dir,
)
from career_pilot.privacy import (
    git_executable,
    local_forbidden_terms,
    scan_content,
    unprotected_private_files,
)

EXIT_OK = 0
EXIT_PRIVATE_FILES = 1
EXIT_DATA_DIR = 2


def find_repo_root(start: Path) -> Path:
    """Top folder of the git repository containing `start`."""
    result = subprocess.run(  # noqa: S603 - fixed git arguments, no user input
        [git_executable(), "rev-parse", "--show-toplevel"],
        cwd=start,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("career-pilot must be run inside the career-pilot git repository.")
    return Path(result.stdout.strip())


def privacy_check(repo_root: Path) -> int:
    """Report private-looking files and values that git tracks or would pick up."""
    data_dir = resolve_data_dir()
    status = EXIT_OK

    leaks = unprotected_private_files(repo_root)
    if leaks:
        print("Private files: PROBLEM - these private-looking files would be committed:")
        for name in leaks:
            print(f"  - {name}")
        print("Move them to the data dir, or fix .gitignore.")
        status = EXIT_PRIVATE_FILES
    else:
        print("Private files: OK - none are tracked or addable")

    findings = scan_content(repo_root, local_forbidden_terms(data_dir))
    if findings:
        print("File contents: PROBLEM - private-looking values (the values are not shown):")
        for finding in findings:
            print(f"  - {finding}")
        status = EXIT_PRIVATE_FILES
    else:
        print("File contents: OK - no phone numbers, emails, home paths or real ids")

    return status


def setup_check(create: bool, repo_only: bool, repo_root: Path) -> int:
    """Report where private data lives and whether the repo is free of it."""
    status = EXIT_OK

    if not repo_only:
        data_dir = resolve_data_dir()
        try:
            if create:
                for folder in create_data_dir(data_dir, repo_root):
                    print(f"Created {display_path(folder)}")
            check_data_dir(data_dir, repo_root)
            print(f"Data dir: {display_path(data_dir)} (exists, outside the repo)")
        except DataDirError as error:
            print(f"Data dir: PROBLEM - {error}")
            status = EXIT_DATA_DIR

    return status or privacy_check(repo_root)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="career-pilot",
        description="Local-first job-hunt helper. Never submits or sends anything.",
    )
    parser.add_argument("--version", action="version", version=f"career-pilot {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser(
        "setup-check", help="Check the data dir and that no private data is in the repo."
    )
    check.add_argument(
        "--create-data-dir",
        action="store_true",
        help="Create the data dir and its sub-folders if missing (outside the repo only).",
    )
    check.add_argument(
        "--repo-only",
        action="store_true",
        help="Skip the data dir check and only check the repo (used in CI).",
    )
    commands.add_parser(
        "privacy-check", help="Check that no private file or value is tracked or addable in git."
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = find_repo_root(Path.cwd())
    if args.command == "setup-check":
        return setup_check(
            create=args.create_data_dir, repo_only=args.repo_only, repo_root=repo_root
        )
    if args.command == "privacy-check":
        return privacy_check(repo_root)
    return EXIT_OK  # pragma: no cover - argparse rejects unknown commands


if __name__ == "__main__":
    sys.exit(main())
