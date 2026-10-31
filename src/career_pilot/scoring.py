"""`career-pilot score`: add up the criteria of a job and pick its route.

The model rates each criterion against the listing. This module does the
arithmetic and the routing so the numbers are always applied the same way.
All values come from `scoring` and `routing` in the profile.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from career_pilot.profile import Profile, ProfileError, lookup

DROPPED = "dropped"


@dataclass(frozen=True)
class ScoreResult:
    track: str
    total: int
    maximum: int
    threshold: int
    meets_threshold: bool
    gates_failed: list[str] = field(default_factory=list)
    minimums_failed: list[str] = field(default_factory=list)
    route: str = DROPPED
    auto_submit: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "track": self.track,
            "score": self.total,
            "max": self.maximum,
            "threshold": self.threshold,
            "meets_threshold": self.meets_threshold,
            "gates_failed": self.gates_failed,
            "minimums_failed": self.minimums_failed,
            "route": self.route,
            "auto_submit": self.auto_submit,
        }


def parse_criteria(text: str) -> dict[str, int]:
    """Turn `skill=3,location=2` into a dict. Raises ProfileError on a malformed pair."""
    values: dict[str, int] = {}
    for pair in filter(None, (part.strip() for part in text.split(","))):
        name, separator, number = pair.partition("=")
        if not separator or not name.strip() or not number.strip().lstrip("-").isdigit():
            raise ProfileError(
                f"Cannot read '{pair}'. Write criteria as name=number, e.g. skill=3."
            )
        values[name.strip()] = int(number)
    return values


def _mapping(value: object, what: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProfileError(f"{what} must be a mapping in the profile.")
    return value


def _matches(
    when: Mapping[str, Any],
    *,
    track: str,
    apply_type: str | None,
    tags: set[str],
    total: int,
    meets_threshold: bool,
    minimums_ok: bool,
) -> bool:
    """True if every condition of a routing rule holds."""
    if "track" in when and when["track"] != track:
        return False
    if "apply_type" in when and when["apply_type"] != apply_type:
        return False
    if "tags_any" in when and not tags & set(when["tags_any"]):
        return False
    if "tags_none" in when and tags & set(when["tags_none"]):
        return False
    if "meets_threshold" in when and when["meets_threshold"] != meets_threshold:
        return False
    return not ("min_score" in when and not (minimums_ok and total >= when["min_score"]))


def score_job(
    profile: Profile,
    track: str,
    ratings: Mapping[str, int],
    apply_type: str | None = None,
    tags: Iterable[str] = (),
) -> ScoreResult:
    """Total, threshold check and route for one job. Raises ProfileError on bad input."""
    tracks = _mapping(lookup(profile, "scoring.tracks"), "scoring.tracks")
    if track not in tracks:
        raise ProfileError(f"Unknown track '{track}'. Tracks in the profile: {', '.join(tracks)}.")
    definition = _mapping(tracks[track], f"scoring.tracks.{track}")
    criteria = _mapping(definition.get("criteria"), f"scoring.tracks.{track}.criteria")

    if set(ratings) != set(criteria):
        missing = sorted(set(criteria) - set(ratings))
        extra = sorted(set(ratings) - set(criteria))
        raise ProfileError(
            f"Track '{track}' needs exactly these criteria: {', '.join(criteria)}."
            + (f" Missing: {', '.join(missing)}." if missing else "")
            + (f" Unknown: {', '.join(extra)}." if extra else "")
        )
    for name, value in ratings.items():
        maximum = int(_mapping(criteria[name], f"criterion {name}")["max"])
        if not 0 <= value <= maximum:
            raise ProfileError(f"{name} must be between 0 and {maximum}, not {value}.")

    total = sum(ratings.values())
    maximum_total = sum(int(c["max"]) for c in criteria.values())
    threshold = int(definition["threshold"])
    gates_failed = sorted(
        n for n, least in (definition.get("gates") or {}).items() if ratings[n] < least
    )
    minimums_failed = sorted(
        n for n, least in (definition.get("min") or {}).items() if ratings[n] < least
    )
    meets_threshold = total >= threshold and not minimums_failed

    route = DROPPED
    if not gates_failed:
        rules = lookup(profile, "routing")
        if not isinstance(rules, list):
            raise ProfileError("routing must be a list of rules in the profile.")
        for rule in rules:
            when = _mapping(rule.get("when") or {}, "a routing rule's 'when'")
            if _matches(
                when,
                track=track,
                apply_type=apply_type,
                tags=set(tags),
                total=total,
                meets_threshold=meets_threshold,
                minimums_ok=not minimums_failed,
            ):
                route = str(rule["route"])
                break
        else:
            raise ProfileError("No routing rule matched. End the list with a rule without 'when'.")

    routes = _mapping(lookup(profile, "routes", {}), "routes")
    if route != DROPPED and route not in routes:
        raise ProfileError(f"Routing names the route '{route}', which is not in 'routes'.")
    auto_submit = route != DROPPED and bool(routes[route].get("auto_submit", False))

    return ScoreResult(
        track=track,
        total=total,
        maximum=maximum_total,
        threshold=threshold,
        meets_threshold=meets_threshold,
        gates_failed=gates_failed,
        minimums_failed=minimums_failed,
        route=route,
        auto_submit=auto_submit,
    )
