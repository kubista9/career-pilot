"""`career-pilot tracker`: the local application tracker (one CSV file).

The CSV is the source of truth for what was found, scored, prepared and sent.
This module is the only thing that should write it, so duplicates, statuses and
folder moves follow the same rules every run.
"""

from __future__ import annotations

import csv
import fcntl  # shortcut: POSIX only, so no Windows; switch to a portable lock if Windows is needed
import os
import re
import tempfile
import unicodedata
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping
from contextlib import contextmanager
from datetime import date
from pathlib import Path

FIELDS: tuple[str, ...] = (
    "job_id",
    "company",
    "role",
    "route",
    "score",
    "status",
    "apply_type",
    "cv",
    "letter_status",
    "found",
    "updated",
    "followup",
    "link",
    "notes",
)
# `not_relevant`: logged so it is not seen again, never prepared or sent.
STATUSES: tuple[str, ...] = (
    "to_review",
    "applied",
    "interview",
    "offer",
    "rejected",
    "not_relevant",
)
LETTER_STATUSES: tuple[str, ...] = ("none", "drafted", "sent", "not_needed")

# A tracker or an email never moves these back to "not yet sent" or "applied".
LOCKED_STATUSES = frozenset({"interview", "offer", "rejected"})
UNLOCKING_STATUSES = frozenset({"to_review", "applied"})

# Fields that should be filled for the summary's "to fix" list.
EXPECTED_FIELDS: tuple[str, ...] = ("route", "cv", "link")

MANIFEST = "MOVE-MANIFEST.tsv"
SIMILAR = "similar role at the same company"

# A spreadsheet runs a cell that starts with one of these as a formula.
FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r")

Row = dict[str, str]


class TrackerError(Exception):
    """The tracker cannot do what was asked."""


class DuplicateError(TrackerError):
    """The job is already in the tracker."""


def normalize(text: str) -> str:
    """Lower case letters and digits only, so 'Acme B.V.' and 'acme bv' compare equal.

    Accents fold to the base letter; `+` and `#` count, so C, C++ and C# differ.
    """
    spelled = text.casefold().replace("+", "plus").replace("#", "sharp")
    folded = unicodedata.normalize("NFKD", spelled)
    return re.sub(r"[^a-z0-9]+", "", "".join(c for c in folded if not unicodedata.combining(c)))


def slugify(text: str) -> str:
    """Folder name for a company: lower case words joined by hyphens."""
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")


def escape_cell(value: str) -> str:
    """Prefix `'` so a spreadsheet does not run the cell as a formula."""
    return "'" + value if value.lstrip("'").startswith(FORMULA_STARTS) else value


def unescape_cell(value: str) -> str:
    return value[1:] if value.startswith("'") and escape_cell(value[1:]) == value else value


def load(path: Path) -> list[Row]:
    """All rows, or an empty list if the tracker does not exist yet.

    Columns the user added by hand are kept after the known ones.
    """
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:  # sig: spreadsheets add a BOM
        reader = csv.DictReader(handle)
        extras = [name for name in reader.fieldnames or () if name and name not in FIELDS]
        return [
            {name: unescape_cell(row.get(name) or "") for name in (*FIELDS, *extras)}
            for row in reader
        ]


@contextmanager
def locked(path: Path) -> Iterator[None]:
    """Hold an exclusive lock from load to save, so parallel runs do not lose rows."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path.with_name(f"{path.name}.lock"), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)  # closing releases the lock


def save(path: Path, rows: Iterable[Mapping[str, str]]) -> None:
    """Write all rows (replace the file in one step so a crash cannot leave half a file)."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    listed = list(rows)
    extras = list(dict.fromkeys(name for row in listed for name in row if name not in FIELDS))
    # mkstemp creates the file 0600 with a unique name in the same folder (os.replace is atomic).
    descriptor, name = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}.", suffix=".tmp")
    temp = Path(name)
    try:
        with os.fdopen(descriptor, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=[*FIELDS, *extras], restval="")
            writer.writeheader()
            for row in listed:
                writer.writerow({k: v if k == "score" else escape_cell(v) for k, v in row.items()})
        os.replace(temp, path)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def find(
    rows: Iterable[Row],
    job_id: str | None = None,
    company: str | None = None,
    role: str | None = None,
) -> list[tuple[Row, str]]:
    """Rows that are the same job, with the reason: same job ID, or same company and role.

    A role that contains the other at the same company is reported as `SIMILAR` (a warning).
    A name with no Latin letter or digit normalizes to "" and is never checked.
    """
    wanted_id = (job_id or "").strip().casefold()
    wanted_company, wanted_role = normalize(company or ""), normalize(role or "")
    matches: list[tuple[Row, str]] = []
    for row in rows:
        if wanted_id and row["job_id"].strip().casefold() == wanted_id:
            matches.append((row, "same job ID"))
        elif wanted_company and wanted_role and normalize(row["company"]) == wanted_company:
            other = normalize(row["role"])
            if other == wanted_role:
                matches.append((row, "same company and role"))
            elif other and (other in wanted_role or wanted_role in other):
                matches.append((row, SIMILAR))
    return matches


def check_choice(value: str, allowed: tuple[str, ...], what: str) -> None:
    if value not in allowed:
        raise TrackerError(f"{what} must be one of: {', '.join(allowed)}. Got '{value}'.")


def add(
    path: Path,
    values: Mapping[str, str],
    *,
    today: date | None = None,
    allow_duplicate: bool = False,
) -> Row:
    """Add a job. Refuses a duplicate unless told otherwise."""
    row: Row = {field: values.get(field, "") for field in FIELDS}
    for required in ("job_id", "company", "role"):
        if not row[required].strip():
            raise TrackerError(f"{required} is required.")
    row["status"] = row["status"] or "to_review"
    row["letter_status"] = row["letter_status"] or "none"
    check_choice(row["status"], STATUSES, "status")
    check_choice(row["letter_status"], LETTER_STATUSES, "letter_status")
    if row["score"] and not row["score"].lstrip("-").isdigit():
        raise TrackerError(f"score must be a whole number. Got '{row['score']}'.")

    with locked(path):
        rows = load(path)
        # A similar role is only a warning for the caller, never a reason to refuse.
        duplicates = [
            hit
            for hit in find(rows, row["job_id"], row["company"], row["role"])
            if hit[1] != SIMILAR
        ]
        if duplicates and not allow_duplicate:
            existing, reason = duplicates[0]
            raise DuplicateError(f"Already in the tracker as {existing['job_id']} ({reason}).")

        stamp = (today or date.today()).isoformat()
        row["found"] = row["found"] or stamp
        row["updated"] = stamp
        save(path, [*rows, row])
    return row


def folder_for(applications_dir: Path, status: str, row: Row) -> Path:
    """`<applications>/<status>/<YYYY-MM>/<company>`: where the job's files live."""
    month = row["found"][:7]
    return applications_dir / status.replace("_", "-") / month / slugify(row["company"])


def move_folder(applications_dir: Path, row: Row, new_status: str) -> str:
    """Move the job's folder to its new status folder. Never overwrites, never deletes."""
    slug = slugify(row["company"])
    if not slug:  # the folder name would be the whole month folder
        return "company name has no letters or digits for a folder name, nothing moved"
    destination = folder_for(applications_dir, new_status, row)
    sources = [
        folder_for(applications_dir, status, row)
        for status in STATUSES
        if folder_for(applications_dir, status, row) != destination
    ]
    sources = [candidate for candidate in sources if candidate.is_dir()][:1]
    if not sources:  # the folder may sit in another month than the `found` date
        sources = sorted(
            candidate
            for status in STATUSES
            if status != new_status
            for candidate in (applications_dir / status.replace("_", "-")).glob(f"*/{slug}")
            if candidate.is_dir()
        )
    if not sources:
        return "no folder found, nothing moved"
    if len(sources) > 1:
        listed = ", ".join(str(path.relative_to(applications_dir)) for path in sources)
        return f"several folders found, nothing moved: {listed}"
    source = sources[0]
    destination = applications_dir / new_status.replace("_", "-") / source.parent.name / slug
    if destination.exists():
        return f"{destination} already exists, nothing moved"
    for missing in reversed([p for p in destination.parents if not p.exists()]):
        missing.mkdir(mode=0o700)
    source.rename(destination)
    manifest = os.open(applications_dir / MANIFEST, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    os.fchmod(manifest, 0o600)  # also fixes a manifest an older version made 644
    with os.fdopen(manifest, "a") as handle:
        handle.write(f"{source}\t{destination}\tmoved\n")
    old, new = (path.relative_to(applications_dir) for path in (source, destination))
    return f"moved {old} to {new}"


def set_status(
    path: Path,
    job_id: str,
    status: str,
    *,
    note: str = "",
    applications_dir: Path | None = None,
    today: date | None = None,
) -> tuple[Row, str]:
    """Change a job's status. Returns the row and a line about the folder move, if any."""
    check_choice(status, STATUSES, "status")
    with locked(path):
        rows = load(path)
        matches = [row for row, _ in find(rows, job_id=job_id)]
        if not matches:
            raise TrackerError(f"No job with ID {job_id} in the tracker.")
        row = matches[0]
        if row["status"] in LOCKED_STATUSES and status in UNLOCKING_STATUSES:
            raise TrackerError(
                f"{row['job_id']} is {row['status']}; it is never moved back to {status}."
            )
        row["status"] = status
        row["updated"] = (today or date.today()).isoformat()
        if note:
            row["notes"] = f"{row['notes']}; {note}" if row["notes"] else note
        save(path, rows)
    moved = move_folder(applications_dir, row, status) if applications_dir else ""
    return row, moved


def counts(rows: Iterable[Row]) -> dict[str, dict[str, int]]:
    """How many jobs per status, per route and per route and status, for the summary."""
    listed = list(rows)
    return {
        "status": dict(Counter(row["status"] for row in listed)),
        "route": dict(Counter(row["route"] or "(none)" for row in listed)),
    }


def parse_day(text: str) -> date | None:
    """An ISO date from a tracker field, or None if it is empty or not a date."""
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def last_activity(row: Row) -> date | None:
    """The later of the last update and the last follow-up email."""
    days = [day for day in (parse_day(row["updated"]), parse_day(row["followup"])) if day]
    return max(days) if days else None


def followups_due(
    rows: Iterable[Row],
    stale_days: int,
    today: date | None = None,
    *,
    skip_routes: Iterable[str] = (),
    rejected_within_days: int | None = None,
) -> dict[str, list[Row]]:
    """Jobs that call for a follow-up email.

    `rejected`: rejected and no follow-up sent yet (ask why, and what to improve). This is due
    at once, as soon as the rejection is in the tracker. With `rejected_within_days` an old
    rejection is left out, because asking weeks later is no use.
    `stale`: applied and nothing has happened for `stale_days` days (ask for the status).
    Jobs on a route in `skip_routes` (for example easy apply, which has no contact) never count.
    A follow-up email resets the clock, so a job is never asked twice in a row.
    """
    now = today or date.today()
    skipped = set(skip_routes)
    rejected: list[Row] = []
    stale: list[Row] = []
    for row in rows:
        if row["route"] in skipped:
            continue
        last = last_activity(row)
        if row["status"] == "rejected" and not row["followup"]:
            recent = rejected_within_days is None or (
                last is not None and (now - last).days <= rejected_within_days
            )
            if recent:
                rejected.append(row)
        elif row["status"] == "applied" and last is not None and (now - last).days >= stale_days:
            stale.append(row)
    return {"rejected": rejected, "stale": stale}


def mark_followup(path: Path, job_id: str, *, note: str = "", today: date | None = None) -> Row:
    """Record that a follow-up email was sent for a job (not merely drafted)."""
    with locked(path):
        rows = load(path)
        matches = [row for row, _ in find(rows, job_id=job_id)]
        if not matches:
            raise TrackerError(f"No job with ID {job_id} in the tracker.")
        row = matches[0]
        stamp = (today or date.today()).isoformat()
        row["followup"] = stamp
        row["updated"] = stamp
        entry = f"Follow-up email {stamp}" + (f": {note}" if note else "")
        row["notes"] = f"{row['notes']}; {entry}" if row["notes"] else entry
        save(path, rows)
    return row


def missing_fields(rows: Iterable[Row]) -> list[tuple[str, list[str]]]:
    """Jobs with an empty route, CV or link, for the summary's 'to fix' list."""
    problems = [(row["job_id"], [f for f in EXPECTED_FIELDS if not row[f]]) for row in rows]
    return [(job_id, fields) for job_id, fields in problems if fields]
