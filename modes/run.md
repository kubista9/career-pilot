# Mode: run

The daily hunt. You work through seven steps without asking the user anything. Make reasonable choices and write your assumptions in the tracker notes. The user reads the summary at the end. Never wait for input before step 7.

Apply `_shared.md` throughout, especially the safety rules.

## Dry run

If the user asked for `run dry`, do steps 1 to 4, write the summary of step 7, and stop. Search, filter, score and route as normal, but write nothing: no tracker rows, no folders, no job description or letter files, no drafts, no forms, no adapter updates, no saved jobs on a board. For step 2 do a `sync dry`. For each job report its ID, title, company, route, the score with the ratings and why, and what a normal run would have done next (prepare, submit automatically, wait for approval). Use it to test a new profile and its scoring. Steps 5 and 6 are skipped.

## 1. Load

1. Run `career-pilot doctor`. It lists missing or unfilled profile keys and unreadable source files. Stop if a required key is missing. Flag everything else.
2. Read the sources you will need (`_shared.md`, "Sources of truth").
3. Check that every file in `cvs` exists. If one is missing, flag "attach CV manually" for jobs that need it.
4. Do not open writing, grammar or design tools yet. Open one only when `_custom.md` says so and a step needs it.

## 2. Sync

Follow `modes/sync.md` before searching, so the tracker is current and the duplicate check is right.

## 3. Search

For every board in `boards`, run every group in `search.groups`. Each board gets its own tab; each board may get one browser subagent.

A group can narrow or change that: `boards` limits it to those boards, `locations` runs one search per location, `location` replaces `search.location`, `pages` replaces `search.pages`. Its `note` is a hint for the board filters (for example "use the part-time filter").

- Use the board's `search_url`, with filters where the board has them, sorted by newest. Check that the filters applied.
- Look through the first `search.pages` result pages. Open a result only if its title could fit and `career-pilot tracker find` says it is not known yet.
- Work at a human pace. Never log in.
- If a search returns nothing, reload once, note it and move on. Do not stop early because the first searches looked empty.
- Count the searches you run and report done and planned in the summary.
- Save a good match on the board (its save or bookmark button) only if `_custom.md` asks for it. Never unsave anything.

For each opened job, read the full description and write down: job ID (`board:id`), title, company, location, work mode, hours, apply type (`easy_apply` or the way the form works), requirements, language of the listing, posting age, salary, contact.

## 4. Filter and score

1. **Filters.** Apply `filters` from the profile. A dropped job is not stored.
2. **Duplicates.** `career-pilot tracker find` by job ID, then by company and role. Skip a duplicate. Flag an existing duplicate in the summary instead of removing it.
3. **Track and tags.** Choose the track. Add tags the routing rules use (for example `local_language_required`).
4. **Rate** each criterion of the track against its rubric, with evidence from the listing, the CV and the facts file.
5. **Score.** Run `career-pilot score --track <track> --criteria a=1,b=2 --apply-type <type> --tag <tag>`. It prints the total, whether the threshold and the minimums are met, and the route. A job whose route is `dropped` is not stored.
6. **Caps.** If a cap in `daily_caps` is reached, stop preparing that kind of job. Log the rest in the tracker as `to_review` with the note "over daily cap".

## 5. Prepare

For every job that will be applied to or kept ready:

1. Create the job's folder in `tracker.applications_dir` and write the job description file: first line "<Company> - <Role>", then the listing link, then the facts from the listing (location, hours, compensation, about, responsibilities, requirements, how to apply). Plain text, facts only.
2. Choose the CV by `focus`.
3. Look for the contact (see `_shared.md`).
4. Draft a cover letter only if the route needs approval, or the form requires one. An optional letter field stays empty unless `_custom.md` says otherwise. Follow `_shared.md`, "Answers and letters" (including the plan first when `letters.plan_first` is true). Save it as `cover-letter.txt` in the job's folder.
5. For email-only applications, also write the ready-to-send email (to, subject, body, attachments) into `application-notes.txt`, and create it as a draft if an email adapter is enabled. Do not send it.

Write what you did in `application-notes.txt`: route, CV, contact, answers you will give, ID, and what is open.

## 6. Apply

What happens depends on the route, set in `routes.<route>.auto_submit`.

**`auto_submit: false` (the default)**: do not fill or submit anything. Open the application page, leave it open, note the ID. Status `to_review`, notes "Ready, <ID>". The user approves in `review` mode.

**`auto_submit: true`**: submit only if every check passes:

- every required question can be answered truthfully from `answers` and the facts files;
- the CV file is the chosen one, confirmed by its full file name on the form;
- a required letter was written, checked and attached;
- no account, login, password, CAPTCHA, verification, payment or legal confirmation is needed;
- nothing on the page looks wrong.

Fill the form, review it, submit and wait for the site's confirmation message. On confirmation: status `applied`, letter status `sent` or `not_needed`, note "Submitted <date>". If any check fails: do not submit. Leave the page open, status `to_review`, notes "Blocked: <reason>, <ID>".

A job in a special track, such as a graduation project, uses the route its rules give it. It auto-submits only if that route has `auto_submit: true`.

## 7. Log and summarise

1. Add or update every job with `career-pilot tracker add` or `tracker status`. Fields: job ID, company, role, route, score, status, apply type, CV, letter status, dates, link, notes. The CV is never empty.
2. If `adapters` has a tracker mirror enabled, update it from the same rows.
3. Write the summary in the format from `_shared.md`. Count from the tracker.
4. Close with one question: which IDs to approve, edit or drop. Do not send anything.
