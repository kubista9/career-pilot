# Career Pilot

A job-hunt assistant for [Claude Code](https://claude.com/claude-code). One skill runs the daily routine: it searches job boards, drops duplicates, scores every job against your own criteria, tracks everything in a local file and prepares applications for you to review.

**Nothing is sent without your approval unless you switch auto-submit on for a route. It never creates accounts, logs in, solves CAPTCHAs or messages anyone on its own.**

This repository is generic. Everything about you (profile, CV, rules, tracker) lives in a data dir outside the repo and is never committed.

## How it works

```
/career-pilot run      search, score, prepare, apply what the routes allow, summarise
/career-pilot sync     update statuses from email and the boards' "applied" pages
/career-pilot review   answer the summary: edit a letter, approve an ID, give feedback
```

The flow is in [docs/workflow.md](docs/workflow.md). Small `career-pilot` commands do the mechanical work (scoring, the tracker, letter checks) so the model spends its effort on judgement, not arithmetic.

## Quick start

```bash
git clone https://github.com/kubista9/career-pilot.git && cd career-pilot
uv sync && uv tool install --editable .
career-pilot setup-check --create-data-dir
```

Then copy the examples into your data dir, make them yours and run `career-pilot doctor`. [The full steps are in docs/getting-started.md](docs/getting-started.md).

## What is where

| Path | What it holds |
|---|---|
| [`.claude/skills/career-pilot/`](.claude/skills/career-pilot/SKILL.md) | The skill: a short router |
| [`modes/`](modes) | The prompts: `run`, `sync`, `review` and the shared rules |
| [`config/profile.example.yml`](config/profile.example.yml) | Every profile key, with a fake person |
| [`examples/`](examples), [`cv.example.md`](cv.example.md) | Fake seed files: facts, letter rules, tracker |
| [`src/career_pilot/`](src/career_pilot) | The `career-pilot` command: `doctor`, `tracker`, `score`, `letter-check`, `brief`, `privacy-check` |
| [`docs/`](docs) | [Getting started](docs/getting-started.md), [profile](docs/profile.md), [scoring](docs/scoring.md), [privacy](docs/privacy.md), [skill conventions](docs/skill-conventions.md) |
| `.github/workflows/` | CI and the private-data guard |

## Privacy

Your data stays in `~/career-pilot-data` (or `CAREER_PILOT_DATA_DIR`). The repo ignores profiles, CVs, trackers, tokens and application files, `career-pilot privacy-check` fails if any private file or value would be committed, and CI repeats the check with a secret scan. See [docs/privacy.md](docs/privacy.md).

## Development

```bash
make check
```

Runs lint, format check, type check, tests and the privacy check. See [AGENTS.md](AGENTS.md) for the repo rules.

## Licence

MIT. See [LICENSE](LICENSE).
