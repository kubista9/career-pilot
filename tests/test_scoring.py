from __future__ import annotations

import copy
from typing import Any

import pytest

from career_pilot.profile import ProfileError
from career_pilot.scoring import DROPPED, parse_criteria, score_job
from tests.conftest import SAMPLE_PROFILE

FULL = {"skill": 4, "location": 2, "language": 1, "growth": 1}


def profile() -> dict[str, Any]:
    return copy.deepcopy(SAMPLE_PROFILE)


def test_parse_criteria() -> None:
    assert parse_criteria("skill=3, location=2") == {"skill": 3, "location": 2}


@pytest.mark.parametrize("text", ["skill", "skill=", "=3", "skill=x"])
def test_parse_criteria_rejects_malformed_pairs(text: str) -> None:
    with pytest.raises(ProfileError, match="name=number"):
        parse_criteria(text)


def test_total_threshold_and_route_of_a_match() -> None:
    result = score_job(profile(), "default", FULL)

    assert (result.total, result.maximum, result.threshold) == (8, 9, 6)
    assert result.meets_threshold
    assert result.route == "strong"
    assert not result.auto_submit


def test_below_threshold_goes_to_the_last_rule() -> None:
    result = score_job(
        profile(), "default", {"skill": 1, "location": 1, "language": 0, "growth": 0}
    )

    assert not result.meets_threshold
    assert result.route == "low_score"
    assert result.auto_submit  # the sample profile opts in for this route


def test_minimum_blocks_the_threshold_even_with_a_high_total() -> None:
    p = profile()
    p["scoring"]["tracks"]["default"]["threshold"] = 4

    result = score_job(p, "default", {"skill": 0, "location": 2, "language": 1, "growth": 1})

    assert result.total == 4
    assert result.minimums_failed == ["skill"]
    assert not result.meets_threshold
    assert result.route == "low_score"


def test_minimum_blocks_min_score_rules_too() -> None:
    ratings = {"skill": 5, "commute": 2}
    assert score_job(profile(), "special", ratings, tags=["needs_local_language"]).route == "local"

    p = profile()
    p["scoring"]["tracks"]["special"]["min"] = {"skill": 5}
    ratings = {"skill": 4, "commute": 2}
    assert score_job(p, "special", ratings, tags=["needs_local_language"]).route == "low_score"


def test_gate_drops_the_job() -> None:
    result = score_job(profile(), "special", {"skill": 5, "commute": 0})

    assert result.route == DROPPED
    assert result.gates_failed == ["commute"]
    assert not result.auto_submit


def test_apply_type_rule_comes_first() -> None:
    result = score_job(profile(), "default", FULL, apply_type="easy_apply")

    assert result.route == "easy_apply"
    assert result.auto_submit


def test_tags_choose_between_special_routes() -> None:
    ratings = {"skill": 5, "commute": 2}

    assert score_job(profile(), "special", ratings).route == "special"
    assert score_job(profile(), "special", ratings, tags=["needs_local_language"]).route == "local"


def test_unknown_track_lists_the_tracks() -> None:
    with pytest.raises(ProfileError, match="default, special"):
        score_job(profile(), "nope", FULL)


def test_wrong_criteria_are_named() -> None:
    with pytest.raises(ProfileError, match="Missing: growth. Unknown: luck"):
        score_job(profile(), "default", {"skill": 1, "location": 1, "language": 1, "luck": 1})


def test_rating_above_max_is_rejected() -> None:
    with pytest.raises(ProfileError, match="skill must be between 0 and 5"):
        score_job(profile(), "default", {**FULL, "skill": 6})


def test_routing_without_a_final_rule_is_reported() -> None:
    p = profile()
    p["routing"] = [{"when": {"track": "special"}, "route": "special"}]

    with pytest.raises(ProfileError, match="No routing rule matched"):
        score_job(p, "default", FULL)


def test_route_missing_from_routes_is_reported() -> None:
    p = profile()
    p["routing"] = [{"route": "ghost"}]

    with pytest.raises(ProfileError, match="'ghost'"):
        score_job(p, "default", FULL)
