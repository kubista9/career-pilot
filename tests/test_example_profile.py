"""The committed example profile is the documentation of the profile format, so it must work."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from career_pilot import tracker
from career_pilot.brief import BRIEF_KEYS, brief_for
from career_pilot.doctor import missing_keys, run_doctor
from career_pilot.letters import check_letter
from career_pilot.privacy import is_private_path, line_findings
from career_pilot.profile import Profile
from career_pilot.scoring import score_job
from tests.conftest import REPO_ROOT

EXAMPLE_PROFILE = REPO_ROOT / "config" / "profile.example.yml"
SEED_FILES = [
    "config/profile.example.yml",
    "cv.example.md",
    "examples/facts.example.md",
    "examples/cover-letter-rules.example.md",
    "examples/applications.example.csv",
    "modes/_profile.template.md",
    "modes/_custom.template.md",
]


@pytest.fixture
def example() -> Profile:
    loaded = yaml.safe_load(EXAMPLE_PROFILE.read_text())
    assert isinstance(loaded, dict)
    return loaded


def test_example_has_every_required_key(example: Profile) -> None:
    assert missing_keys(example) == []


def test_doctor_accepts_the_example_as_a_copy(example: Profile, tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    shutil.copy(EXAMPLE_PROFILE, tmp_path / "config" / "profile.yml")

    issues = run_doctor(tmp_path)

    assert [i for i in issues if i.level == "error"] == []
    assert any("candidate.full_name still looks like an example value" in i.message for i in issues)


def test_nothing_auto_submits_by_default(example: Profile) -> None:
    assert all(route["auto_submit"] is False for route in example["routes"].values())


def test_example_scoring_and_routing(example: Profile) -> None:
    match = {"skill": 4, "location": 2, "language": 1, "growth": 1}
    weak = {"skill": 1, "location": 1, "language": 0, "growth": 0}
    no_skill = {"skill": 0, "location": 2, "language": 1, "growth": 1}

    assert score_job(example, "default", match).route == "strong"
    assert score_job(example, "default", weak).route == "low_score"
    assert score_job(example, "default", no_skill).route == "low_score"
    assert score_job(example, "default", match, apply_type="easy_apply").route == "easy_apply"


def test_every_route_in_routing_exists(example: Profile) -> None:
    named = {rule["route"] for rule in example["routing"]}

    assert named <= set(example["routes"])
    assert "when" not in example["routing"][-1]


def test_the_three_common_boards_are_there(example: Profile) -> None:
    assert [board["name"] for board in example["boards"]] == ["LinkedIn", "Indeed", "Glassdoor"]
    assert all("{keywords}" in board["search_url"] for board in example["boards"])


@pytest.mark.parametrize("mode", sorted(BRIEF_KEYS))
def test_every_brief_works_on_the_example(example: Profile, mode: str) -> None:
    assert brief_for(example, mode)


def test_example_letter_rules_in_profile_are_usable(example: Profile) -> None:
    letters = example["letters"]
    text = "Dear Team,\n\n" + "I enjoy building small reliable services for real users. " * 2

    assert check_letter(text, max_chars=letters["max_chars"]) == []
    assert check_letter(
        text + " I am fluent Exampleish.", forbidden_claims=letters["forbidden_claims"]
    )


def test_example_tracker_rows_use_the_tracker_format() -> None:
    rows = tracker.load(REPO_ROOT / "examples" / "applications.example.csv")

    assert len(rows) == 3
    assert all(row["status"] in tracker.STATUSES for row in rows)
    assert all(row["letter_status"] in tracker.LETTER_STATUSES for row in rows)
    assert tracker.missing_fields(rows) == []


@pytest.mark.parametrize("name", SEED_FILES)
def test_seed_files_are_public_and_fake(name: str) -> None:
    path = REPO_ROOT / name

    assert path.is_file()
    assert not is_private_path(name)
    for line in path.read_text().splitlines():
        assert line_findings(line) == [], f"{name} has a private-looking value: {line[:40]}"


@pytest.mark.parametrize("mode", ["run", "review", "sync"])
def test_style_skill_is_off_in_the_example_and_reaches_drafting_modes(
    example: Profile, mode: str
) -> None:
    assert example["letters"]["style_skill"] == ""
    assert brief_for(example, mode)["letters"]["style_skill"] == ""
