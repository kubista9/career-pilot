from __future__ import annotations

import json
from pathlib import Path

import pytest

from career_pilot.cli import (
    EXIT_LETTER,
    EXIT_OK,
    EXIT_PROFILE,
    EXIT_TRACKER,
    main,
)
from tests.conftest import SAMPLE_PROFILE, write_profile


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str]:
    code = main(list(argv))
    return code, capsys.readouterr().out


def test_score_prints_total_and_route(data_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(capsys, "score", "--criteria", "skill=4,location=2,language=1,growth=1")

    assert code == EXIT_OK
    assert out.splitlines() == [
        "score: 8/9 (threshold 6: met)",
        "route: strong",
        "auto_submit: false",
    ]


def test_score_json_and_tags(data_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(
        capsys, "score", "--track", "special", "--criteria", "skill=5,commute=2",
        "--tag", "needs_local_language", "--json",
    )  # fmt: skip

    assert code == EXIT_OK
    assert json.loads(out)["route"] == "local"


def test_score_reports_a_dropped_job(data_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(capsys, "score", "--track", "special", "--criteria", "skill=5,commute=0")

    assert code == EXIT_OK
    assert "dropped: below the gate on commute" in out
    assert "route: dropped" in out


def test_score_problem_exits_with_the_profile_code(
    data_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out = run(capsys, "score", "--criteria", "skill=9")

    assert code == EXIT_PROFILE
    assert "PROBLEM" in out


def test_brief_prints_yaml_for_the_mode(data_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(capsys, "brief", "search")

    assert code == EXIT_OK
    assert out.startswith("boards:")
    assert "answers" not in out


def test_doctor_exit_codes(
    data_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out = run(capsys, "doctor")
    assert code == EXIT_OK
    assert "Usable, with warnings" in out

    broken = {k: v for k, v in SAMPLE_PROFILE.items() if k != "routing"}
    write_profile(data_dir, broken)
    code, out = run(capsys, "doctor")
    assert code == EXIT_PROFILE
    assert "ERROR: routing is missing or empty" in out


def test_letter_check_uses_profile_limits(
    data_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    letter = tmp_path / "letter.txt"
    letter.write_text("Dear Team,\n\n" + "I like building useful software for real people. " * 3)

    code, out = run(capsys, "letter-check", str(letter))
    assert code == EXIT_OK
    assert "Letter check: OK" in out

    code, out = run(capsys, "letter-check", str(letter), "--max-chars", "50")
    assert code == EXIT_LETTER
    assert "the maximum is 50" in out


def test_tracker_flow(data_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(
        capsys, "tracker", "add", "--job-id", "board:1", "--company", "Acme", "--role", "Dev",
        "--route", "strong", "--cv", "cv.pdf", "--link", "https://board.test/1",
    )  # fmt: skip
    assert (code, out) == (EXIT_OK, "Added board:1: Acme, Dev (to_review)\n")

    code, out = run(
        capsys, "tracker", "add", "--job-id", "board:1", "--company", "Acme", "--role", "Dev"
    )
    assert code == EXIT_TRACKER
    assert "Already in the tracker" in out

    _, out = run(capsys, "tracker", "find", "--company", "acme", "--role", "dev")
    assert out.startswith("duplicate: board:1")
    _, out = run(capsys, "tracker", "find", "--job-id", "board:2")
    assert out == "new: not in the tracker\n"

    code, out = run(capsys, "tracker", "status", "board:1", "applied", "--note", "Submitted")
    assert (code, out) == (EXIT_OK, "board:1 is now applied\n")

    _, out = run(capsys, "tracker", "list", "--status", "applied")
    assert out.startswith("board:1\tapplied\tstrong")
    _, out = run(capsys, "tracker", "counts")
    assert json.loads(out)["status"] == {"applied": 1}
    _, out = run(capsys, "tracker", "check")
    assert out.startswith("Tracker: OK")

    code, out = run(capsys, "tracker", "status", "board:404", "applied")
    assert code == EXIT_TRACKER


def test_tracker_moves_folders_when_status_folders_are_on(
    data_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    profile = {**SAMPLE_PROFILE, "tracker": {"status_folders": True}}
    write_profile(data_dir, profile)
    run(capsys, "tracker", "add", "--job-id", "b:1", "--company", "Acme", "--role", "Dev")
    month = next(
        iter(__import__("csv").DictReader((data_dir / "tracker/applications.csv").open()))
    )["found"][:7]
    folder = data_dir / "applications" / "to-review" / month / "acme"
    folder.mkdir(parents=True)

    code, out = run(capsys, "tracker", "status", "b:1", "applied")

    assert code == EXIT_OK
    assert "Folder: moved" in out
    assert (data_dir / "applications" / "applied" / month / "acme").is_dir()

    run(capsys, "tracker", "add", "--job-id", "b:2", "--company", "Beta", "--role", "Dev")
    (data_dir / "applications" / "to-review" / month / "beta").mkdir(parents=True)
    _, out = run(capsys, "tracker", "status", "b:2", "applied", "--no-move")
    assert "Folder" not in out
    assert (data_dir / "applications" / "to-review" / month / "beta").is_dir()


def test_letter_check_reads_the_new_limits_and_patterns_from_the_profile(
    data_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    letters = {
        "min_paragraphs": 3,
        "min_paragraph_chars": 200,
        "forbidden_patterns": [r"https?://"],
    }
    write_profile(data_dir, {**SAMPLE_PROFILE, "letters": letters})
    letter = tmp_path / "letter.txt"
    letter.write_text(
        "Dear Team,\n\n"
        + "I like building useful software for real people. " * 2
        + "https://example.com"
    )

    code, out = run(capsys, "letter-check", str(letter))

    assert code == EXIT_LETTER
    assert "1 paragraphs, the minimum is 3" in out
    assert "paragraph 1 is" in out
    assert "forbidden pattern 'https?://'" in out


def test_letter_check_reports_an_invalid_pattern(
    data_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_profile(data_dir, {**SAMPLE_PROFILE, "letters": {"forbidden_patterns": ["("]}})
    letter = tmp_path / "letter.txt"
    letter.write_text("Dear Team,\n\nSome text that is long enough to count as a paragraph here.")

    code, out = run(capsys, "letter-check", str(letter))

    assert code == EXIT_PROFILE
    assert "not valid" in out


def test_letter_check_options_replace_the_profile_for_one_check(
    data_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_profile(data_dir, {**SAMPLE_PROFILE, "letters": {"min_paragraphs": 3}})
    letter = tmp_path / "letter.txt"
    letter.write_text(
        "Dear Team,\n\n" + "Short non-tech letters are fine with two paragraphs. " * 2
    )

    code, _ = run(capsys, "letter-check", str(letter))
    assert code == EXIT_LETTER

    code, out = run(capsys, "letter-check", str(letter), "--min-paragraphs", "1")
    assert (code, out.startswith("Letter check: OK")) == (EXIT_OK, True)


def test_followups_command_and_followup_record(
    data_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run(capsys, "tracker", "add", "--job-id", "b:1", "--company", "Acme", "--role", "Dev")
    run(capsys, "tracker", "add", "--job-id", "b:2", "--company", "Beta", "--role", "Dev")
    run(capsys, "tracker", "status", "b:2", "rejected", "--no-move")

    code, out = run(capsys, "tracker", "followups", "--days", "0", "--json")
    assert code == EXIT_OK
    assert [row["job_id"] for row in json.loads(out)["rejected"]] == ["b:2"]

    code, out = run(capsys, "tracker", "followup", "b:2", "--note", "asked for feedback")
    assert code == EXIT_OK
    assert "follow-up recorded" in out

    _, out = run(capsys, "tracker", "followups")
    assert "Rejected, no follow-up yet (ask for feedback): 0" in out
    assert "nothing for 5+ days" in out


@pytest.mark.parametrize("argv", [(), ("--company", "Acme"), ("--role", "Dev")])
def test_tracker_find_needs_a_job_id_or_company_and_role(
    data_dir: Path, capsys: pytest.CaptureFixture[str], argv: tuple[str, ...]
) -> None:
    code, out = run(capsys, "tracker", "find", *argv)

    assert code == EXIT_TRACKER
    assert out.startswith("Tracker: PROBLEM - ")


def test_tracker_reports_similar_roles_as_warnings(
    data_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run(capsys, "tracker", "add", "--job-id", "b:1", "--company", "Acme", "--role", "Developer")

    code, out = run(capsys, "tracker", "find", "--company", "Acme", "--role", "Senior Developer")
    assert code == EXIT_OK
    assert out.startswith("similar: b:1, Acme, Developer")

    code, out = run(
        capsys,
        "tracker",
        "add",
        "--job-id",
        "b:2",
        "--company",
        "Acme",
        "--role",
        "Senior Developer",
    )
    assert code == EXIT_OK
    lines = out.splitlines()
    assert lines[0].startswith("Added b:2")
    assert lines[1].startswith("Warning: similar") and "b:1" in lines[1]
