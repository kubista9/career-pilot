# Mode: sync

Bring the tracker up to date with what really happened: replies in email, and the "applied" pages of the job boards. Read-only everywhere except the tracker and the application folders. Apply `_shared.md`.

If a job is missing from the tracker, add it first (`career-pilot tracker add`) with the fields visible on the page, and the note "added from <source>". Match existing rows by job ID, then by company and role.

## 1. Email (read only)

Only if the `gmail` adapter in the profile is enabled and available. Search the last `sync.email_days` days (default 7) with general terms (application, interview, unfortunately, offer) plus the user's own words from `_custom.md`.

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

## 4. Report

List what you changed automatically, what you only propose, and anything you could not check. Rows that are `rejected`, `interview` or `offer` are never reverted by a board tracker.
