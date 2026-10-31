from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

from career_pilot.brief import BRIEF_KEYS, brief_for, render_brief
from career_pilot.doctor import example_values, missing_keys, run_doctor
from career_pilot.letters import check_letter
from career_pilot.profile import ProfileError, data_path, load_profile, lookup, optional_profile
from tests.conftest import SAMPLE_PROFILE, write_profile

PARAGRAPH = "I would like to work on your platform because it solves a real problem for users."


def letter(paragraphs: int = 3) -> str:
    return "Dear Team,\n\n" + "\n\n".join([PARAGRAPH] * paragraphs) + "\n\nKind regards,\nTest"


# --- letters ---------------------------------------------------------------------------------


def test_a_clean_letter_passes() -> None:
    assert check_letter(letter()) == []


def test_length_limit() -> None:
    issues = check_letter(letter(), max_chars=100)

    assert issues == [f"{len(letter().strip())} characters, the limit is 100"]


def test_greeting_and_sign_off_do_not_count_as_paragraphs() -> None:
    assert check_letter(letter(4)) == []
    assert check_letter(letter(5)) == ["5 paragraphs, the limit is 4"]


def test_dashes_are_flagged_unless_allowed() -> None:
    text = letter().replace("platform", "plat—form")

    assert check_letter(text) == ["contains an em or en dash; use a hyphen"]
    assert check_letter(text, allow_dashes=True) == []


def test_banned_and_forbidden_phrases() -> None:
    text = letter().replace("real problem", "Passionate About real problem")

    issues = check_letter(text, banned_phrases=["platform"])

    assert issues == ["uses the phrase 'passionate about'", "uses the phrase 'platform'"]
    assert check_letter(letter(), forbidden_claims=["real problem"]) == [
        "makes a claim the profile forbids: 'real problem'"
    ]


# --- profile and brief -------------------------------------------------------------------------


def test_load_profile_errors_explain_the_fix(tmp_path: Path) -> None:
    with pytest.raises(ProfileError, match="profile.example.yml"):
        load_profile(tmp_path)
    assert optional_profile(tmp_path) == {}

    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "profile.yml").write_text("- a list\n")
    with pytest.raises(ProfileError, match="mapping"):
        load_profile(tmp_path)
    (tmp_path / "config" / "profile.yml").write_text("a: [unclosed\n")
    with pytest.raises(ProfileError, match="not valid YAML"):
        load_profile(tmp_path)


def test_lookup_and_data_path(tmp_path: Path) -> None:
    assert lookup(SAMPLE_PROFILE, "answers.start_date") == "2027-01-04"
    assert lookup(SAMPLE_PROFILE, "answers.nope", "x") == "x"
    assert data_path(tmp_path, None, "tracker/a.csv") == tmp_path / "tracker" / "a.csv"
    assert data_path(tmp_path, "/abs/a.csv", "x") == Path("/abs/a.csv")


def test_brief_has_only_the_keys_of_the_mode() -> None:
    brief = brief_for(SAMPLE_PROFILE, "search")

    assert set(brief) == {"boards", "search"}
    assert "Test Person" not in render_brief(SAMPLE_PROFILE, "search")


@pytest.mark.parametrize("mode", sorted(BRIEF_KEYS))
def test_no_brief_ever_contains_the_privacy_section(mode: str) -> None:
    assert "privacy" not in brief_for(SAMPLE_PROFILE, mode)


def test_unknown_brief_mode() -> None:
    with pytest.raises(ProfileError, match="Choose one of"):
        brief_for(SAMPLE_PROFILE, "nope")


# --- doctor ------------------------------------------------------------------------------------


def test_doctor_reports_a_missing_data_dir(tmp_path: Path) -> None:
    [issue] = run_doctor(tmp_path / "missing")

    assert issue.level == "error"


def test_doctor_reports_missing_keys_as_errors(tmp_path: Path) -> None:
    profile = copy.deepcopy(SAMPLE_PROFILE)
    del profile["routing"]
    profile["answers"]["start_date"] = ""
    write_profile(tmp_path, profile)

    errors = [str(i) for i in run_doctor(tmp_path) if i.level == "error"]

    assert errors == [
        "ERROR: answers.start_date is missing or empty",
        "ERROR: routing is missing or empty",
    ]


def test_doctor_warns_about_missing_files_and_example_values(tmp_path: Path) -> None:
    profile = copy.deepcopy(SAMPLE_PROFILE)
    profile["candidate"]["email"] = "alex@example.com"
    profile["candidate"]["phone"] = "+00 0 0000 0000"
    write_profile(tmp_path, profile)

    messages = [i.message for i in run_doctor(tmp_path) if i.level == "warning"]

    assert "candidate.email still looks like an example value" in messages
    assert "candidate.phone still looks like an example value" in messages
    assert "sources.facts points to a file that does not exist" in messages
    assert "CV file cv-software.pdf is not in sources.cv_dir" in messages
    assert "cv.md is missing from the data dir" in messages
    assert not any(i.level == "error" for i in run_doctor(tmp_path))


def test_doctor_is_clean_when_everything_exists(tmp_path: Path) -> None:
    (tmp_path / "cv").mkdir()
    (tmp_path / "cv" / "cv-software.pdf").write_text("x")
    (tmp_path / "about.md").write_text("x")
    (tmp_path / "rules.md").write_text("x")
    (tmp_path / "cv.md").write_text("x")
    profile: dict[str, Any] = copy.deepcopy(SAMPLE_PROFILE)
    profile["sources"] = {
        "facts": str(tmp_path / "about.md"),
        "letter_rules": str(tmp_path / "rules.md"),
        "cv_dir": str(tmp_path / "cv"),
    }
    write_profile(tmp_path, profile)

    assert run_doctor(tmp_path) == []


def test_missing_keys_and_example_values_helpers() -> None:
    assert missing_keys(SAMPLE_PROFILE) == []
    assert example_values({"a": {"b": ["Example Person"]}, "c": "fine"}) == ["a.b.0"]
