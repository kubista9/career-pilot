# Security

## What counts

Report any of these:

- Private data in the repo or its history: a name, contact detail, employer, home path, ID, token or scoring number of a real person.
- A prompt or command path that could send, submit or apply without the user's approval, or that creates accounts, logs in or solves CAPTCHAs on its own.
- A way for text from a job listing, an email or a web page to act as an instruction to the agent.
- A secret or token committed or printed to a log.
- A gap in `career-pilot privacy-check` that lets a private file or value through.

## How to report

Use GitHub's private vulnerability reporting: open the Security tab of the repository and choose "Report a vulnerability". Do not open a public issue, and do not paste private data into one.

If you reported private data that was already pushed, assume it is public and rotate any token in it. See [docs/privacy.md](docs/privacy.md).

## Supported versions

The latest release.
