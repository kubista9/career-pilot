from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from career_pilot import tracker
from career_pilot.tracker import DuplicateError, TrackerError

TODAY = date(2026, 11, 2)


@pytest.fixture
def csv_path(tmp_path: Path) -> Path:
    return tmp_path / "tracker" / "applications.csv"


def add(csv_path: Path, job_id: str = "board:1", company: str = "Acme B.V.", **extra: str) -> None:
    values = {"job_id": job_id, "company": company, "role": "Developer", **extra}
    tracker.add(csv_path, values, today=TODAY)


def test_add_fills_defaults_and_dates(csv_path: Path) -> None:
    add(csv_path, route="strong", cv="cv.pdf")

    [row] = tracker.load(csv_path)
    assert row["status"] == "to_review"
    assert row["letter_status"] == "none"
    assert row["found"] == row["updated"] == "2026-11-02"


def test_csv_round_trips_commas_and_quotes(csv_path: Path) -> None:
    add(csv_path, notes='Ready, "tab 3", second line')

    assert tracker.load(csv_path)[0]["notes"] == 'Ready, "tab 3", second line'


def test_missing_tracker_is_empty(csv_path: Path) -> None:
    assert tracker.load(csv_path) == []


@pytest.mark.parametrize("missing", ["job_id", "company", "role"])
def test_required_fields(csv_path: Path, missing: str) -> None:
    values = {"job_id": "b:1", "company": "Acme", "role": "Dev", missing: " "}
    with pytest.raises(TrackerError, match=missing):
        tracker.add(csv_path, values)


def test_invalid_choices_are_rejected(csv_path: Path) -> None:
    with pytest.raises(TrackerError, match="status must be one of"):
        add(csv_path, status="sent")
    with pytest.raises(TrackerError, match="letter_status must be one of"):
        add(csv_path, letter_status="written")
    with pytest.raises(TrackerError, match="score must be a whole number"):
        add(csv_path, score="high")


def test_duplicate_by_job_id(csv_path: Path) -> None:
    add(csv_path)

    with pytest.raises(DuplicateError, match="same job ID"):
        tracker.add(csv_path, {"job_id": "BOARD:1", "company": "Other", "role": "Other"})


def test_duplicate_by_company_and_role_ignores_case_and_punctuation(csv_path: Path) -> None:
    add(csv_path)

    with pytest.raises(DuplicateError, match="same company and role"):
        tracker.add(csv_path, {"job_id": "other:9", "company": "acme bv", "role": "DEVELOPER"})
    assert len(tracker.load(csv_path)) == 1


def test_find_reports_the_reason(csv_path: Path) -> None:
    add(csv_path)
    rows = tracker.load(csv_path)

    assert tracker.find(rows, job_id="board:2") == []
    [(row, reason)] = tracker.find(rows, job_id="board:1")
    assert (row["company"], reason) == ("Acme B.V.", "same job ID")


def test_set_status_updates_row_and_notes(csv_path: Path) -> None:
    add(csv_path, notes="Ready")

    row, moved = tracker.set_status(csv_path, "board:1", "applied", note="Submitted", today=TODAY)

    assert (row["status"], row["notes"], moved) == ("applied", "Ready; Submitted", "")
    assert tracker.load(csv_path)[0]["status"] == "applied"


def test_unknown_job_id(csv_path: Path) -> None:
    with pytest.raises(TrackerError, match="No job with ID"):
        tracker.set_status(csv_path, "board:404", "applied")


@pytest.mark.parametrize("locked", ["interview", "offer", "rejected"])
@pytest.mark.parametrize("back", ["to_review", "applied"])
def test_locked_statuses_never_move_back(csv_path: Path, locked: str, back: str) -> None:
    add(csv_path, status=locked)

    with pytest.raises(TrackerError, match="never moved back"):
        tracker.set_status(csv_path, "board:1", back)


def test_locked_statuses_can_still_progress(csv_path: Path) -> None:
    add(csv_path, status="interview")

    row, _ = tracker.set_status(csv_path, "board:1", "offer")

    assert row["status"] == "offer"


def make_folder(applications: Path, status: str, name: str = "acme-b-v") -> Path:
    folder = applications / status / "2026-11" / name
    folder.mkdir(parents=True)
    (folder / "cover-letter.txt").write_text("letter")
    return folder


def test_status_change_moves_the_folder_and_writes_the_manifest(
    csv_path: Path, tmp_path: Path
) -> None:
    applications = tmp_path / "applications"
    make_folder(applications, "to-review")
    add(csv_path)

    _, moved = tracker.set_status(
        csv_path, "board:1", "applied", applications_dir=applications, today=TODAY
    )

    assert moved.startswith("moved to-review/2026-11/acme-b-v to applied/2026-11/acme-b-v")
    assert (
        applications / "applied" / "2026-11" / "acme-b-v" / "cover-letter.txt"
    ).read_text() == "letter"
    assert not (applications / "to-review" / "2026-11" / "acme-b-v").exists()
    manifest = (applications / "MOVE-MANIFEST.tsv").read_text().split("\t")
    assert manifest[2].strip() == "moved"


def test_move_never_overwrites_an_existing_folder(csv_path: Path, tmp_path: Path) -> None:
    applications = tmp_path / "applications"
    source = make_folder(applications, "to-review")
    target = make_folder(applications, "applied")
    add(csv_path)

    _, moved = tracker.set_status(csv_path, "board:1", "applied", applications_dir=applications)

    assert "already exists, nothing moved" in moved
    assert source.is_dir() and target.is_dir()
    assert (target / "cover-letter.txt").read_text() == "letter"


def test_move_without_a_folder_does_nothing(csv_path: Path, tmp_path: Path) -> None:
    add(csv_path)

    _, moved = tracker.set_status(
        csv_path, "board:1", "applied", applications_dir=tmp_path / "applications"
    )

    assert moved == "no folder found, nothing moved"


def test_counts_and_missing_fields(csv_path: Path) -> None:
    add(csv_path, "b:1", "A", route="strong", cv="x.pdf", link="https://x.test/1")
    add(csv_path, "b:2", "B", route="strong", status="applied")
    add(csv_path, "b:3", "C")

    rows = tracker.load(csv_path)
    assert tracker.counts(rows) == {
        "status": {"to_review": 2, "applied": 1},
        "route": {"strong": 2, "(none)": 1},
    }
    assert tracker.missing_fields(rows) == [
        ("b:2", ["cv", "link"]),
        ("b:3", ["route", "cv", "link"]),
    ]


def test_slugify() -> None:
    assert tracker.slugify("Acme B.V. (NL)") == "acme-b-v-nl"


def test_not_relevant_rows_are_logged_and_counted_apart(csv_path: Path) -> None:
    add(csv_path, "b:1", "A", status="not_relevant", notes="Not relevant: bachelor only")
    add(csv_path, "b:2", "B")

    assert tracker.counts(tracker.load(csv_path))["status"] == {"not_relevant": 1, "to_review": 1}
    row, _ = tracker.set_status(csv_path, "b:1", "to_review", note="Reconsidered")
    assert row["status"] == "to_review"


def test_old_csv_without_followup_column_still_loads(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True)
    csv_path.write_text("job_id,company,role,status\nb:1,Acme,Dev,applied\n")

    [row] = tracker.load(csv_path)

    assert row["followup"] == ""
    assert row["status"] == "applied"


def test_followups_due_lists_rejected_and_stale_jobs(csv_path: Path) -> None:
    add(csv_path, "b:1", "Quiet", status="applied")
    add(csv_path, "b:2", "Fresh", status="applied")
    add(csv_path, "b:3", "No", status="rejected")
    add(csv_path, "b:4", "Waiting", status="to_review")
    rows = tracker.load(csv_path)
    rows[1]["updated"] = "2026-11-06"

    due = tracker.followups_due(rows, 5, today=date(2026, 11, 7))

    assert [row["job_id"] for row in due["stale"]] == ["b:1"]
    assert [row["job_id"] for row in due["rejected"]] == ["b:3"]


def test_followup_resets_the_clock_and_ends_the_rejection_reminder(csv_path: Path) -> None:
    add(csv_path, "b:1", "Quiet", status="applied")
    add(csv_path, "b:2", "No", status="rejected")

    tracker.mark_followup(csv_path, "b:1", note="status request", today=date(2026, 11, 7))
    tracker.mark_followup(csv_path, "b:2", today=date(2026, 11, 7))
    rows = tracker.load(csv_path)

    assert rows[0]["followup"] == "2026-11-07"
    assert "Follow-up email 2026-11-07: status request" in rows[0]["notes"]
    assert tracker.followups_due(rows, 5, today=date(2026, 11, 9)) == {"rejected": [], "stale": []}
    later = tracker.followups_due(rows, 5, today=date(2026, 11, 12))
    assert [row["job_id"] for row in later["stale"]] == ["b:1"]


def test_followup_for_unknown_job(csv_path: Path) -> None:
    with pytest.raises(TrackerError):
        tracker.mark_followup(csv_path, "b:404")


def test_followups_skip_routes_and_old_rejections(csv_path: Path) -> None:
    add(csv_path, "b:1", "Easy", status="applied", route="easy_apply")
    add(csv_path, "b:2", "Direct", status="applied", route="strong")
    add(csv_path, "b:3", "Fresh no", status="rejected", route="strong")
    add(csv_path, "b:4", "Old no", status="rejected", route="strong")
    rows = tracker.load(csv_path)
    rows[3]["updated"] = "2026-09-01"

    due = tracker.followups_due(
        rows, 5, today=date(2026, 11, 7), skip_routes=["easy_apply"], rejected_within_days=14
    )

    assert [row["job_id"] for row in due["stale"]] == ["b:2"]
    assert [row["job_id"] for row in due["rejected"]] == ["b:3"]


def add_role(csv_path: Path, job_id: str, company: str, role: str) -> None:
    tracker.add(csv_path, {"job_id": job_id, "company": company, "role": role}, today=TODAY)


def test_c_cpp_and_csharp_are_different_roles(csv_path: Path) -> None:
    add_role(csv_path, "b:1", "Acme Example", "C++ Developer")

    rows = tracker.load(csv_path)
    assert tracker.find(rows, company="Acme Example", role="C# Developer") == []
    assert tracker.find(rows, company="Acme Example", role="C Developer") == []
    assert tracker.find(rows, company="Acme Example", role="c++ developer")


def test_accents_fold_to_the_base_letter(csv_path: Path) -> None:
    add_role(csv_path, "b:1", "Acme Example", "Développeur")

    rows = tracker.load(csv_path)
    assert tracker.find(rows, company="Acme Example", role="Developpeur")
    assert not tracker.find(rows, company="Acme Example", role="Dveloppeur")


def test_names_without_latin_letters_are_never_checked(csv_path: Path) -> None:
    add_role(csv_path, "b:1", "Пример Один", "Разработчик")
    add_role(csv_path, "b:2", "Пример Два", "Разработчик")  # no DuplicateError

    assert len(tracker.load(csv_path)) == 2
    assert tracker.find(tracker.load(csv_path), company="Пример Один", role="Разработчик") == []


def test_job_ids_compare_exactly_apart_from_case_and_spaces(csv_path: Path) -> None:
    add_role(csv_path, "board:0000000010", "Acme Example", "Dev")

    rows = tracker.load(csv_path)
    assert tracker.find(rows, job_id="board:00000000-10") == []
    assert tracker.find(rows, job_id=" BOARD:0000000010 ")


def test_company_without_ascii_does_not_move_the_month_folder(
    csv_path: Path, tmp_path: Path
) -> None:
    applications = tmp_path / "applications"
    other = make_folder(applications, "to-review", "other-company")
    add_role(csv_path, "b:1", "Пример Один", "Dev")

    _, moved = tracker.set_status(csv_path, "b:1", "applied", applications_dir=applications)

    assert "nothing moved" in moved
    assert (other / "cover-letter.txt").read_text() == "letter"
    assert not (applications / "applied").exists()


def test_similar_role_is_found_but_never_refuses_an_add(csv_path: Path) -> None:
    add_role(csv_path, "b:1", "Acme Example", "Backend Developer (part-time)")

    rows = tracker.load(csv_path)
    for role in ("Backend Developer (part-time) (EN)", "Backend Developer"):
        [(row, reason)] = tracker.find(rows, company="Acme Example", role=role)
        assert row["job_id"] == "b:1" and reason == tracker.SIMILAR
    add_role(csv_path, "b:2", "Acme Example", "Backend Developer")
    assert len(tracker.load(csv_path)) == 2


def test_extra_columns_survive_a_write(csv_path: Path) -> None:
    add_role(csv_path, "b:1", "Acme Example", "Dev")
    text = csv_path.read_text().replace("notes\n", "notes,my_column\n").rstrip("\n")
    csv_path.write_text(text + ",mine\n")

    tracker.mark_followup(csv_path, "b:1", today=TODAY)
    add_role(csv_path, "b:2", "Beta Example", "Dev")

    first, second = tracker.load(csv_path)
    assert first["my_column"] == "mine" and second["my_column"] == ""
    assert csv_path.read_text().splitlines()[0].endswith(",notes,my_column")


def test_row_with_more_cells_than_the_header_does_not_crash(csv_path: Path) -> None:
    add_role(csv_path, "b:1", "Acme Example", "Dev")
    with csv_path.open("a") as handle:
        handle.write("b:2,Beta,Dev,,,,,,,,,,,,,extra,more\r\n")

    assert [row["job_id"] for row in tracker.load(csv_path)] == ["b:1", "b:2"]


def test_csv_with_a_byte_order_mark_keeps_its_job_ids(csv_path: Path) -> None:
    add_role(csv_path, "b:1", "Acme Example", "Dev")
    csv_path.write_bytes(b"\xef\xbb\xbf" + csv_path.read_bytes())

    tracker.mark_followup(csv_path, "b:1", today=TODAY)

    assert tracker.load(csv_path)[0]["job_id"] == "b:1"
    assert not csv_path.read_bytes().startswith(b"\xef\xbb\xbf")


def test_formula_cells_are_escaped_on_disk_and_round_trip(csv_path: Path) -> None:
    evil = '=HYPERLINK("http://x.example.com","x")'
    add_role(csv_path, "b:1", evil, "-role")
    tracker.set_status(csv_path, "b:1", "applied", note="@note")
    tracker.mark_followup(csv_path, "b:1", note="+call", today=TODAY)
    add_role(csv_path, "b:2", "'=already quoted", "Dev")

    first, second = tracker.load(csv_path)
    assert first["company"] == evil and first["role"] == "-role"
    assert first["notes"] == "@note; Follow-up email 2026-11-02: +call"
    assert second["company"] == "'=already quoted"
    text = csv_path.read_text()
    assert "'=HYPERLINK" in text and "\n=" not in text and ",=" not in text


def test_negative_score_is_not_escaped(csv_path: Path) -> None:
    tracker.add(
        csv_path,
        {"job_id": "b:1", "company": "Acme Example", "role": "Dev", "score": "-2"},
        today=TODAY,
    )

    assert ",-2," in csv_path.read_text()
    assert tracker.load(csv_path)[0]["score"] == "-2"


def _add_in_process(args: tuple[str, int]) -> int:
    path, number = args
    tracker.add(
        Path(path), {"job_id": f"b:{number}", "company": f"Company {number}", "role": "Dev"}
    )
    return number


def test_parallel_adds_lose_no_rows(csv_path: Path) -> None:
    import multiprocessing

    with multiprocessing.get_context("fork").Pool(10) as pool:
        done = pool.map(_add_in_process, [(str(csv_path), n) for n in range(20)])

    assert len(done) == 20
    assert len(tracker.load(csv_path)) == 20
    assert [p.name for p in csv_path.parent.iterdir() if p.name.endswith(".tmp")] == []


def test_folder_in_another_month_is_found_and_keeps_its_month(
    csv_path: Path, tmp_path: Path
) -> None:
    applications = tmp_path / "applications"
    folder = applications / "to-review" / "2026-10" / "acme-example"
    folder.mkdir(parents=True)
    add_role(csv_path, "b:1", "Acme Example", "Dev")  # found 2026-11

    _, moved = tracker.set_status(csv_path, "b:1", "applied", applications_dir=applications)

    assert moved == "moved to-review/2026-10/acme-example to applied/2026-10/acme-example"
    assert (applications / "applied" / "2026-10" / "acme-example").is_dir()
    assert not folder.exists()


def test_several_folders_in_other_months_move_nothing(csv_path: Path, tmp_path: Path) -> None:
    applications = tmp_path / "applications"
    for month in ("2026-09", "2026-10"):
        (applications / "to-review" / month / "acme-example").mkdir(parents=True)
    add_role(csv_path, "b:1", "Acme Example", "Dev")

    _, moved = tracker.set_status(csv_path, "b:1", "applied", applications_dir=applications)

    assert moved.startswith("several folders found, nothing moved")
    assert "2026-09" in moved and "2026-10" in moved
    assert (applications / "to-review" / "2026-09" / "acme-example").is_dir()
    assert (applications / "to-review" / "2026-10" / "acme-example").is_dir()


def test_private_files_and_folders_are_created_owner_only(csv_path: Path, tmp_path: Path) -> None:
    import os
    import stat

    applications = tmp_path / "applications"
    make_folder(applications, "to-review")
    (applications / "MOVE-MANIFEST.tsv").write_text("")
    (applications / "MOVE-MANIFEST.tsv").chmod(0o644)  # an older version's manifest
    add(csv_path)
    previous = os.umask(0o022)
    try:
        tracker.set_status(csv_path, "board:1", "applied", applications_dir=applications)
        tracker.mark_followup(csv_path, "board:1")
    finally:
        os.umask(previous)

    def mode(path: Path) -> int:
        return stat.S_IMODE(path.stat().st_mode)

    assert mode(csv_path) == 0o600
    assert mode(applications / "MOVE-MANIFEST.tsv") == 0o600
    assert mode(applications / "applied") == 0o700
    assert mode(applications / "applied" / "2026-11") == 0o700
