# Getting started

You need [Claude Code](https://claude.com/claude-code), [uv](https://docs.astral.sh/uv/) and Python 3.13.

## 1. Install

```bash
git clone https://github.com/kubista9/career-pilot.git
cd career-pilot
uv sync
uv tool install --editable .
```

The last line puts the `career-pilot` command on your PATH so the skill can call it from anywhere.

## 2. Create your data dir

Your profile, CV and tracker live in a folder outside the repo, so they can never be committed by accident. The default is `~/career-pilot-data`. To use another folder, set `CAREER_PILOT_DATA_DIR`.

```bash
career-pilot setup-check --create-data-dir
```

## 3. Copy the examples and make them yours

```bash
D=~/career-pilot-data
cp config/profile.example.yml $D/config/profile.yml
cp cv.example.md $D/cv.md
cp modes/_profile.template.md $D/modes/_profile.md
cp modes/_custom.template.md $D/modes/_custom.md
cp examples/facts.example.md $D/facts.md
cp examples/cover-letter-rules.example.md $D/cover-letter-rules.md
mkdir -p $D/cv
```

Then:

1. Rewrite `facts.md` about yourself. It is the source of truth for every claim in your letters.
2. Put your CV PDFs in `$D/cv/` and list them under `cvs` in the profile.
3. Fill in `config/profile.yml`: [every key is explained here](profile.md).
4. Describe yourself and what you want in `modes/_profile.md`.

## 4. Check it

```bash
career-pilot doctor
```

It lists missing keys (errors) and values that still look like the example (warnings). Fix them until it says "Ready".

## 5. Run

Start Claude Code inside this repository and type:

```
/career-pilot run
```

The run ends with a summary. Reply by ID in the same chat: `/career-pilot review` handles edits and approvals. Nothing is sent until a route has `auto_submit: true` or you approve that ID. To update statuses only, use `/career-pilot sync`.

## Try it safely first

`/career-pilot run dry` searches, scores and routes jobs and shows what a real run would do. It writes nothing and sends nothing. `/career-pilot sync dry` does the same for status updates.

## Updating

`git pull`. Your files in the data dir are never touched. If a new version adds profile keys, `career-pilot doctor` tells you.
