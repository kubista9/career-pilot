# Mode: sync

Bring the tracker up to date with what really happened: replies in email, and the "applied" pages of the job boards. Read-only everywhere except the tracker and the application folders. Apply `_shared.md`.

If the user asked for `sync dry`, do all the reading and matching but change nothing: list each change you would make, and why.

If a job is missing from the tracker, add it first (`career-pilot tracker add`) with the fields visible on the page, and the note "added from <source>". Match existing rows by job ID, then by company and role.

## 1. Email (read only)

Only if the `gmail` adapter in the profile is enabled and available. Search the last `sync.email_days` days (default 7) with general terms (application, interview, unfortunately, offer) plus the user's own words from `_custom.md`.

A keyword search is only the first pass: it misses mail that uses other words (a booked call, a bounce, a rejection in another language). Also list all recent mail without promotions and newsletters, pick every message from or about a company in the tracker or from a recruiting system (applicant tracking systems, calendar invites, delivery failures), and read the full body of each. Never decide from a subject or snippet alone.

Never send, reply, draft, label, archive, delete or forward.

Update only clear cases and add "Email <date>: <reason>" to the notes:

| Email says | New status |
|---|---|
| A clear rejection | `rejected` |
| An interview or call invitation or booking | `interview` |
| An offer | `offer` |
| An automatic "we received your application" for a `to_review` row | `applied` |

An unclear email changes nothing. List it in the summary as a proposal. An email about an application that is not in the tracker goes in the summary, not in the tracker, unless it clearly is an application by the user.

## 2. Board trackers

For each board with `tracker_urls` in the profile (keys `applied`, `interviews`, `clicked_apply`, `drafts`), open the pages in the user's already logged-in browser. Never log in.

| Page | Action |
|---|---|
| Applied | Make the tracker say `applied`. Add a missing row as `applied`, note "From <board> tracker <date>" |
| Interviews | Make the tracker say `interview` |
| Clicked apply | Add a missing row as `to_review`, note "Clicked apply, check whether it was sent". Do not mark it applied: a click does not prove it was sent |
| Drafts | Finish the application with the checks from `run.md` step 6 if the route allows auto-submit, otherwise leave it open and note it |

## 3. Folders

If `tracker.status_folders` is true, `career-pilot tracker status` moves the job's folder to the folder of the new status by itself. It never overwrites and writes every move to `MOVE-MANIFEST.tsv`.

## 4. Reconcile per company

For each company, compare the tracker and the folders with the email receipts and rejections and the board's applied page. Report applied, not applied and rejected per company. Move a folder to `applied` only for a confirmed submission (a receipt in email or on the board) or the user's word. Ask before any broad move.

## 5. Follow-up emails

Run `career-pilot tracker followups`. It lists two groups:

- **Rejected, no follow-up yet.** The company said no. This is due at once: draft it in the same sync that found the rejection, do not wait. Draft a very short email that thanks them, names the role and the application date, and asks why the application was not chosen and what could be improved. Only recent rejections are listed (`followup.rejected_within_days`).
- **Applied, gone quiet.** The status is `applied` and nothing has happened for `followup.stale_days` days (default 5). Draft a short email that names the role and the application date and asks kindly for the status. Ask at most twice per application: look for "Follow-up email" in the notes.

Do this after steps 1 to 4, so a reply that just arrived has already updated the tracker and the job no longer counts as stale. In `sync dry` only list the jobs. Jobs on a route in `followup.skip_routes` are left out by the command.

Keep it reasonable. If the rejection already gives a clear reason (availability, hours, a language or experience requirement), a request for feedback adds nothing: do not draft it, and list the reason in the summary.

For each job:

1. Find a real recruiting contact first (`_shared.md`, "Emails"). Never guess an address. A no-reply address, or one that bounced, is not a contact: say "no contact found" and move on.
2. Write the email in the user's voice following `sources.letter_rules` and `_custom.md`: under 80 words, plain, no links, no excuses and no pushing. Skip a rejection that already explains the reason in detail only if the user's `_custom.md` says so.
3. Create a draft. Send nothing. The user sends it, or says "send" for that job.
4. After the email is really sent, run `career-pilot tracker followup <job_id> --note "<what was asked>"`. A draft alone does not count, so the job stays on the list until it is sent.

List the drafts in the summary: job, contact, which group, and the first line.

## 6. Report

List what you changed automatically, what you only propose, and anything you could not check. Rows that are `rejected`, `interview` or `offer` are never reverted by a board tracker.
