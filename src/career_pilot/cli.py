"""Command-line entry point: `career-pilot <command>`."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from career_pilot import __version__, tracker
from career_pilot.brief import BRIEF_KEYS, render_brief
from career_pilot.doctor import run_doctor
from career_pilot.letters import (
    DEFAULT_MAX_CHARS,
    DEFAULT_MAX_PARAGRAPHS,
    body_paragraphs,
    check_letter,
)
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
from career_pilot.profile import (
    Profile,
    ProfileError,
    data_path,
    load_profile,
    lookup,
    optional_profile,
)
from career_pilot.scoring import parse_criteria, score_job

EXIT_OK = 0
EXIT_PRIVATE_FILES = 1
EXIT_DATA_DIR = 2
EXIT_PROFILE = 3
EXIT_TRACKER = 4
EXIT_LETTER = 5
DEFAULT_STALE_DAYS = 5


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


# --- repo and data dir checks -----------------------------------------------------------------


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


def doctor() -> int:
    issues = run_doctor(resolve_data_dir())
    for issue in issues:
        print(issue)
    errors = sum(issue.level == "error" for issue in issues)
    if not issues:
        print("Ready: the profile is complete and every file it points to exists.")
    elif not errors:
        print("Usable, with warnings. Fix them before relying on the results.")
    return EXIT_PROFILE if errors else EXIT_OK


# --- scoring, briefs, letters -----------------------------------------------------------------


def score(track: str, criteria: str, apply_type: str | None, tags: list[str], as_json: bool) -> int:
    try:
        profile = load_profile(resolve_data_dir())
        result = score_job(profile, track, parse_criteria(criteria), apply_type, tags)
    except (ProfileError, KeyError, ValueError) as error:
        print(f"Score: PROBLEM - {error}")
        return EXIT_PROFILE
    if as_json:
        print(json.dumps(result.as_dict()))
        return EXIT_OK
    verdict = "met" if result.meets_threshold else "not met"
    print(f"score: {result.total}/{result.maximum} (threshold {result.threshold}: {verdict})")
    if result.gates_failed:
        print(f"dropped: below the gate on {', '.join(result.gates_failed)}")
    if result.minimums_failed:
        print(f"below the minimum on: {', '.join(result.minimums_failed)}")
    print(f"route: {result.route}")
    print(f"auto_submit: {str(result.auto_submit).lower()}")
    return EXIT_OK


def brief(mode: str) -> int:
    try:
        print(render_brief(load_profile(resolve_data_dir()), mode), end="")
    except ProfileError as error:
        print(f"Brief: PROBLEM - {error}")
        return EXIT_PROFILE
    return EXIT_OK


LIMIT_OPTIONS = (
    "min_chars",
    "max_chars",
    "min_paragraphs",
    "max_paragraphs",
    "min_paragraph_chars",
)


def letter_check(file: str, limits: dict[str, int]) -> int:
    text = sys.stdin.read() if file == "-" else Path(file).expanduser().read_text()
    try:
        profile = optional_profile(resolve_data_dir())
    except ProfileError as error:
        print(f"Letter check: PROBLEM - {error}")
        return EXIT_PROFILE
    settings: dict[str, Any] = {**(lookup(profile, "letters", {}) or {}), **limits}
    try:
        issues = check_letter(
            text,
            min_chars=int(settings.get("min_chars", 0)),
            max_chars=int(settings.get("max_chars", DEFAULT_MAX_CHARS)),
            min_paragraphs=int(settings.get("min_paragraphs", 0)),
            max_paragraphs=int(settings.get("max_paragraphs", DEFAULT_MAX_PARAGRAPHS)),
            min_paragraph_chars=int(settings.get("min_paragraph_chars", 0)),
            banned_phrases=settings.get("banned_phrases") or [],
            forbidden_claims=settings.get("forbidden_claims") or [],
            forbidden_patterns=settings.get("forbidden_patterns") or [],
            allow_dashes=bool(settings.get("allow_dashes", False)),
        )
    except re.error as error:
        print(f"Letter check: PROBLEM - a forbidden pattern in the profile is not valid: {error}")
        return EXIT_PROFILE
    if not issues:
        length = len("\n\n".join(body_paragraphs(text)))
        print(f"Letter check: OK (body of {length} characters)")
        return EXIT_OK
    print("Letter check: PROBLEM")
    for issue in issues:
        print(f"  - {issue}")
    return EXIT_LETTER


# --- tracker ----------------------------------------------------------------------------------


def tracker_paths(profile: Profile, data_dir: Path) -> tuple[Path, Path | None]:
    """The tracker file, and the applications folder if status folders are switched on."""
    csv_path = data_path(data_dir, lookup(profile, "tracker.file"), "tracker/applications.csv")
    if not lookup(profile, "tracker.status_folders", False):
        return csv_path, None
    folder = data_path(data_dir, lookup(profile, "tracker.applications_dir"), "applications")
    return csv_path, folder


def run_tracker(args: argparse.Namespace) -> int:
    data_dir = resolve_data_dir()
    try:
        profile = optional_profile(data_dir)
        csv_path, applications_dir = tracker_paths(profile, data_dir)
        if getattr(args, "days", 0) is None:
            args.days = int(lookup(profile, "followup.stale_days", DEFAULT_STALE_DAYS))
            if not args.skip_route:
                args.skip_route = list(lookup(profile, "followup.skip_routes", []) or [])
            if args.rejected_within is None:
                configured = lookup(profile, "followup.rejected_within_days", None)
                args.rejected_within = None if configured is None else int(configured)
        return tracker_command(args, csv_path, applications_dir)
    except (ProfileError, tracker.TrackerError) as error:
        print(f"Tracker: PROBLEM - {error}")
        return EXIT_TRACKER


def tracker_command(args: argparse.Namespace, csv_path: Path, applications_dir: Path | None) -> int:
    if args.tracker_command == "add":
        values = {
            field: getattr(args, field) or "" for field in tracker.FIELDS if hasattr(args, field)
        }
        row = tracker.add(csv_path, values)
        print(f"Added {row['job_id']}: {row['company']}, {row['role']} ({row['status']})")
    elif args.tracker_command == "find":
        rows = tracker.load(csv_path)
        matches = tracker.find(rows, args.job_id, args.company, args.role)
        if not matches:
            print("new: not in the tracker")
        for row, reason in matches:
            print(
                f"duplicate: {row['job_id']}, {row['company']}, {row['role']} "
                f"[{row['status']}] ({reason})"
            )
    elif args.tracker_command == "status":
        row, moved = tracker.set_status(
            csv_path,
            args.job_id,
            args.status,
            note=args.note or "",
            applications_dir=None if args.no_move else applications_dir,
        )
        print(f"{row['job_id']} is now {row['status']}")
        if moved:
            print(f"Folder: {moved}")
    elif args.tracker_command == "list":
        for row in tracker.load(csv_path):
            if args.status in (None, row["status"]) and args.route in (None, row["route"]):
                print(
                    f"{row['job_id']}\t{row['status']}\t{row['route']}\t{row['score']}\t"
                    f"{row['company']}\t{row['role']}"
                )
    elif args.tracker_command == "followups":
        due = tracker.followups_due(
            tracker.load(csv_path),
            args.days,
            skip_routes=args.skip_route or (),
            rejected_within_days=args.rejected_within,
        )
        if args.json:
            print(json.dumps(due))
        else:
            titles = {
                "rejected": "Rejected, no follow-up yet (ask for feedback)",
                "stale": f"Applied, nothing for {args.days}+ days (ask for the status)",
            }
            for group, rows in due.items():
                print(f"{titles[group]}: {len(rows)}")
                for row in rows:
                    print(
                        f"  {row['job_id']}\t{row['company']}\t{row['role']}\t"
                        f"last activity {tracker.last_activity(row) or 'unknown'}"
                    )
    elif args.tracker_command == "followup":
        row = tracker.mark_followup(csv_path, args.job_id, note=args.note or "")
        print(f"{row['job_id']}: follow-up recorded for {row['followup']}")
    elif args.tracker_command == "counts":
        print(json.dumps(tracker.counts(tracker.load(csv_path))))
    elif args.tracker_command == "check":
        problems = tracker.missing_fields(tracker.load(csv_path))
        for job_id, fields in problems:
            print(f"{job_id}: missing {', '.join(fields)}")
        if not problems:
            print("Tracker: OK - route, CV and link are filled in for every job")
    return EXIT_OK


# --- parser -----------------------------------------------------------------------------------


def add_tracker_parser(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = commands.add_parser("tracker", help="Add, find and update jobs in the local tracker.")
    sub = parser.add_subparsers(dest="tracker_command", required=True)

    add = sub.add_parser("add", help="Add a job. Refuses duplicates.")
    for field in tracker.FIELDS:
        if field not in ("found", "updated", "followup"):
            add.add_argument(f"--{field.replace('_', '-')}", dest=field, default="")

    find = sub.add_parser("find", help="Is this job already in the tracker?")
    find.add_argument("--job-id")
    find.add_argument("--company")
    find.add_argument("--role")

    status = sub.add_parser("status", help="Change a job's status.")
    status.add_argument("job_id")
    status.add_argument("status", choices=tracker.STATUSES)
    status.add_argument("--note")
    status.add_argument(
        "--no-move", action="store_true", help="Do not move the job's folder (status folders on)."
    )

    listing = sub.add_parser("list", help="List jobs, one per line.")
    listing.add_argument("--status", choices=tracker.STATUSES)
    listing.add_argument("--route")

    followups = sub.add_parser(
        "followups", help="Rejected jobs without a follow-up, and applied jobs gone quiet."
    )
    followups.add_argument(
        "--days",
        type=int,
        help="Days of silence that make a job stale (default: followup.stale_days, else 5).",
    )
    followups.add_argument(
        "--skip-route",
        action="append",
        help="A route that never gets a follow-up (default: followup.skip_routes). Repeatable.",
    )
    followups.add_argument(
        "--rejected-within",
        type=int,
        help="Only rejections this many days old (default: followup.rejected_within_days).",
    )
    followups.add_argument("--json", action="store_true")

    followup = sub.add_parser("followup", help="Record that a follow-up email was sent.")
    followup.add_argument("job_id")
    followup.add_argument("--note")

    sub.add_parser("counts", help="Number of jobs per status and per route (JSON).")
    sub.add_parser("check", help="List jobs with an empty route, CV or link.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="career-pilot",
        description="Helpers for the career-pilot skill. Never submits or sends anything.",
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
    commands.add_parser("doctor", help="Check that the profile is complete and its files exist.")

    scoring = commands.add_parser("score", help="Add up a job's criteria and pick its route.")
    scoring.add_argument("--track", default="default")
    scoring.add_argument(
        "--criteria", required=True, help="name=number pairs, e.g. skill=3,growth=1"
    )
    scoring.add_argument("--apply-type")
    scoring.add_argument("--tag", action="append", default=[], dest="tags")
    scoring.add_argument("--json", action="store_true", dest="as_json")

    brief_parser = commands.add_parser("brief", help="Print only the profile keys a mode needs.")
    brief_parser.add_argument("mode", choices=sorted(BRIEF_KEYS))

    letter = commands.add_parser("letter-check", help="Check a cover letter against the rules.")
    letter.add_argument("file", help="Letter text file, or - for standard input.")
    for option in LIMIT_OPTIONS:
        letter.add_argument(
            f"--{option.replace('_', '-')}",
            type=int,
            dest=option,
            help="Replaces the value from the profile for this check.",
        )

    add_tracker_parser(commands)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "setup-check":
        return setup_check(
            create=args.create_data_dir,
            repo_only=args.repo_only,
            repo_root=find_repo_root(Path.cwd()),
        )
    if args.command == "privacy-check":
        return privacy_check(find_repo_root(Path.cwd()))
    if args.command == "doctor":
        return doctor()
    if args.command == "score":
        return score(args.track, args.criteria, args.apply_type, args.tags, args.as_json)
    if args.command == "brief":
        return brief(args.mode)
    if args.command == "letter-check":
        limits = {o: getattr(args, o) for o in LIMIT_OPTIONS if getattr(args, o) is not None}
        return letter_check(args.file, limits)
    if args.command == "tracker":
        return run_tracker(args)
    return EXIT_OK  # pragma: no cover - argparse rejects unknown commands


if __name__ == "__main__":
    sys.exit(main())
