# Privacy

Career Pilot handles your CV, your contact details and a list of everywhere you applied. This repository is public, so it is built to hold none of that.

## Two layers

| Layer | Where | Contains |
|---|---|---|
| Repo | this repository | Generic prompts, tools, templates and a fake example person |
| Data dir | `CAREER_PILOT_DATA_DIR`, default `~/career-pilot-data` | Your profile, CV, personal rules, tracker, letters and application folders |

The data dir must be outside the repo. `career-pilot setup-check` refuses a data dir inside it.

The prompts never contain values. They name a key (`answers.start_date`) and the agent reads the value from your profile at run time.

## What is checked

`career-pilot privacy-check` (also part of `setup-check`) looks at everything git would track or let you add:

- **File names**: profiles, CVs, facts files, trackers, tokens, databases, logs, browser state and application files.
- **File contents**: phone numbers, email addresses (except `example.*`), home folder paths, and real-looking IDs (fake ones start with zeros).
- **Your own words**: list names, streets or employers under `privacy.forbidden_terms` in your profile. They are checked in file names and file contents on your machine only. Never put them in a file in the repo.

The check prints the file, the line and the kind of finding. It never prints the matched text.

## In CI

Two workflows run on every push and pull request:

- `ci.yml`: lint, types and tests.
- `no-user-data.yml`: the same private-file and private-value check (`setup-check --repo-only`) and a secret scan with gitleaks.

## If something private was committed

1. Do not push it. If it is only in a local commit, amend or reset it.
2. If it was pushed, treat it as public: change any token or password in it, then remove it from history (for example with `git filter-repo`) and force-push, or recreate the repository.
3. Add the pattern to `.gitignore` and `PRIVATE_PATTERNS` in `src/career_pilot/privacy.py`, with a test.

## Secrets

Tokens (such as `NOTION_TOKEN`) come from environment variables or `<data dir>/.env`. They never go in the profile or in a file in the repo.
