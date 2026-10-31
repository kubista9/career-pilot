"""The documentation links to real files, and the prompts and the diagram describe the same flow."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.conftest import REPO_ROOT

MARKDOWN_FILES = sorted(
    [*REPO_ROOT.glob("*.md"), *REPO_ROOT.glob("docs/*.md"), *REPO_ROOT.glob("modes/*.md")]
)
LINK = re.compile(r"\]\(([^)\s]+)\)")


def relative_links(path: Path) -> list[str]:
    links = LINK.findall(path.read_text())
    return [link for link in links if not link.startswith(("http://", "https://", "#", "mailto:"))]


@pytest.mark.parametrize("path", MARKDOWN_FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_relative_links_point_to_existing_files(path: Path) -> None:
    for link in relative_links(path):
        target = (path.parent / link.split("#")[0]).resolve()
        assert target.exists(), f"{path.name} links to {link}, which does not exist"


def test_shared_rules_list_seven_steps_and_the_diagram_names_them() -> None:
    shared = (REPO_ROOT / "modes" / "_shared.md").read_text()
    section = shared.split("## The seven steps")[1].split("\n## ")[0]
    steps = re.findall(r"^(\d)\. \*\*([^*]+)\*\*", section, re.M)
    diagram = (REPO_ROOT / "docs" / "workflow.md").read_text()

    assert [number for number, _ in steps] == list("1234567")
    for number, name in steps:
        assert f"{number} {name.split()[0]}" in diagram, f"step {number} missing in the diagram"


def test_run_mode_has_the_same_seven_steps() -> None:
    run = (REPO_ROOT / "modes" / "run.md").read_text()

    assert re.findall(r"^## (\d)\. ", run, re.M) == list("1234567")


def test_every_mode_in_the_skill_router_has_a_file() -> None:
    skill = (REPO_ROOT / ".claude" / "skills" / "career-pilot" / "SKILL.md").read_text()
    routed = re.findall(r"^\| `[\w ()]+` .*?\| `modes/(\w+\.md)` \|", skill, re.M)

    assert sorted(routed) == ["review.md", "run.md", "sync.md"]
    for mode in routed:
        assert (REPO_ROOT / "modes" / mode).is_file()
