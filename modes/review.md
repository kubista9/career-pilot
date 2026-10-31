# Mode: review

The user answers the summary from `run`. Each answer is about one ID. Handle every ID on its own. Apply `_shared.md`.

Find each ID in the tracker notes and in `application-notes.txt` in the job's folder. If an ID is unknown, ask.

## What an answer can be

| The user says | You do |
|---|---|
| An edit ("put this in the second paragraph", "more about my last project") | Change the letter as asked, keeping the user's wording and the letter rules. Run `career-pilot letter-check` and check the facts again. Show the new text in the chat. Wait for the user's next explicit OK for this ID. An edit is **never** an approval |
| An approval ("ok send", "ok submit") | Do the approved step (below) for that ID only |
| A question or a doubt | Answer it. Change nothing |
| A drop ("skip 4") | Set the row to `to_review` with the note "Dropped by user". Do not submit |
| Feedback on how the run works ("score these lower", "stop applying to X") | Restate what you understood, answer questions, and collect the feedback. Ask whether to save it. Save preferences to `DATA_DIR/modes/_custom.md` or the profile, never to a file in the repo |

If you are unsure whether the user approved, treat it as not approved and ask.

## Doing an approved step

1. Make the final letter file if the form needs one (the format the profile or `_custom.md` names), and save it in the job's folder.
2. Open the page you left open, or reopen the listing. Fill every field with `answers`, upload the CV and the approved letter, or paste the text, and review the form.
3. Submit, or for an email application send the approved email through the email adapter with the attachments. Wait for the confirmation.
4. Stop and tell the user if an account, login, CAPTCHA or verification blocks it. Do not work around it.
5. After a confirmed submit: status `applied`, letter status `sent`, note "Submitted <date>", move the folder if `tracker.status_folders` is on. Confirm in the chat, per ID.

An approval for an easy-apply job that failed its checks: if the checks failed because information is missing, say what is missing. Otherwise submit.

## Feedback loop

Before any expensive work (final letters, uploads, submissions), recap in a few lines what you understood for each ID. If the user corrects you, update the recap and ask again. Move on only when the user has no more feedback or gives a clear OK.
