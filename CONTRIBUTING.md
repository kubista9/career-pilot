# Contributing

Thanks for helping. Career Pilot is small, so the process is too.

## Set up

```bash
uv sync
make check
```

Run `make check` before every commit. It runs lint, format check, type check, tests and the privacy check. CI runs the same checks plus a secret scan.

## The two-layer rule

This repository is generic and public. Everything about a real person lives in the data dir (`CAREER_PILOT_DATA_DIR`), outside the repo. Never commit names, contact details, employers, paths, IDs or scoring numbers. Examples use the fake person Alex Example, `example.com` and all-zero IDs.

The full rules are in [AGENTS.md](AGENTS.md). Its table says which file each kind of change goes in. [docs/privacy.md](docs/privacy.md) explains what the privacy check looks at.

## Enable the pre-push hook

```bash
make hooks
```

This sets `core.hooksPath` to `.githooks`, so `make check` runs before every push and a failure stops the push.

Turn it on. The terms that must never appear in the repo (your own name, street, employers) live only in your own profile under `privacy.forbidden_terms`. CI cannot see that file, so only the local privacy check can catch them. The hook makes sure it runs, with your data dir set.

## Commits

Make small commits, grouped by area. Use the subject `Area: what changed`, for example `Modes: fill application forms in prepare`. Areas in use: Modes, Docs, Profile, Tracker, Search, CI.

If `career-pilot privacy-check` fails, fix the cause. Do not edit the check to make it pass.

## Pull requests

Open a pull request against `main`. The template asks what changed, which commit does what and what you checked. Change the prompts before the diagram in [docs/workflow.md](docs/workflow.md).

Security and privacy problems go through [SECURITY.md](SECURITY.md), not a public issue.
