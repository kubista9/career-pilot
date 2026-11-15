# Changelog

All notable changes are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0] - 2026-11-15

### Added

- The `career-pilot` skill with three modes: `run`, `sync` and `review`.
- Helper commands: `doctor`, `setup-check`, `tracker`, `score`, `letter-check`, `brief` and `privacy-check`.
- A fake example profile, CV and seed files for new users.
- A private-data guard in CI: file and value checks plus a gitleaks secret scan.
- Docs: getting started, profile, scoring, privacy, skill conventions and the workflow diagram.
- Plan-first letters, two approval steps, follow-up emails and dry runs in the modes.
- Follow-up emails: find rejected and stale jobs and record sent follow-ups.
- Search stages with radius, maximum age and one subagent per board.
- A check on every run for whether an application needs a CV.
- Next-step suggestions for every job in the run summary.
- Letter drafts go through the user's own writing-style skill.
- ATS research with sources and a list of local checks.
- The target workflow doc with diagrams and a table per step.
- Preflight, knock-outs and the sent steps in the workflow diagram.
- Application forms are filled in during prepare and never submitted.
- Optional `form_facts` and `accounts` blocks in the profile.

### Changed

- `letter-check` measures the letter body only and accepts limit overrides.
- The private-data workflow runs gitleaks directly.

### Fixed

- Tracker: duplicate detection, hand-added columns are kept and writes are guarded.
