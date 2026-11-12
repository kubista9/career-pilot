# Mode: review

The user answers the summary from `run`. Each answer is about one ID. Handle every ID on its own. Apply `_shared.md`.

Find each ID in the tracker notes and in `application-notes.txt` in the job's folder. If an ID is unknown, ask.

## What an answer can be

There are two different approvals. A letter OK approves the text. Only a send OK sends.

| The user says | You do |
|---|---|
| An edit ("put this in the second paragraph", "more about my last project") | Change the letter as asked, keeping the user's wording and the letter rules. Run `career-pilot letter-check` and check the facts again. Show the new text in the chat. Wait for the next explicit OK for this ID. An edit is **never** an approval |
| A plan confirmation (when `letters.plan_first` is true) | Write the full letter from the confirmed plan |
| A letter OK ("1. letter ok", "1. looks good", or a plain "1. okay") | The text is approved. Finalize the letter (below). Nothing is sent. Ask once whether to send |
| A send OK ("ok send", "ok submit", "send the application") | Do the sending steps (below) for that ID only |
| A question or a doubt | Answer it. Change nothing |
| A drop ("skip 4") | Set the row to `to_review` with the note "Dropped by user". Do not submit |
| Feedback on how the run works ("score these lower", "stop applying to X") | Restate what you understood, answer questions, and collect the feedback. Ask whether to save it. Save preferences to `DATA_DIR/modes/_custom.md` or the profile, never to a file in the repo |

If you are unsure what the user approved, treat it as a letter OK at most and ask.

## Finalizing an approved letter

Read the user's current copy of the letter and sync it into `cover-letter.txt` first. Then make the final letter file if the form needs one, in the format the profile or `_custom.md` names, and save it in the job's folder under one clear name. Tell the user where it is and what its first lines say. Nothing is uploaded or sent. If the user edits the letter afterwards, build the file again and move the old one to `_to_delete`.

## Before you touch a form

For every ID, stop and report any failure:

1. the letter text equals the user's current copy, with no placeholders and no typos or claims the user has not accepted;
2. the hours and the start date in the letter match the listing;
3. the CV check still holds on the form as it is now: if the form takes a CV, it is the newest export and equals the CV recorded in the tracker; if the tracker says `not_needed`, the form really asks for none;
4. the answers come from `answers` and the facts files. Ask only about fields they do not cover.

## Sending an approved ID

One application at a time.

1. Open the form in a visible tab, fill every field using element references, upload the CV (only if the form takes one) and the final letter (or paste the text), and review.
2. Stop before a privacy or terms checkbox and ask once whether to tick it. A CAPTCHA, an account or a verification is the user's: hand over, do not work around it.
3. Press the final Send or Submit only after the user's explicit send OK for that ID. Without it, the user presses Send themselves.
4. For an email application create a draft with the letter as the body, a one-line intro and the CV attached unless the tracker says `not_needed` (or a note to attach it), and tell the user where it is. Send it only on the explicit send OK, one email at a time.
5. Wait for the site's confirmation.

An approval for an easy-apply job that failed its checks: if the checks failed because information is missing, say what is missing. Otherwise submit.

## After sending

- If the user sent it themselves, wait for their word before changing anything.
- Then: status `applied`; letter status `sent` only if a letter was really sent; a note with the date, the CV, the hours, the route and "check for a reply in 7 days"; move the folder if `tracker.status_folders` is on. Close that job's tabs.
- If the user gave new standing facts or answers, add them to the facts file after copying a backup, and say so.
- Confirm in the chat, per ID.

## Feedback loop

Before any expensive work (final letters, uploads, submissions), recap in a few lines what you understood for each ID. If the user corrects you, update the recap and ask again. Move on only when the user has no more feedback or gives a clear OK.

Learn from edits. When the user changed a letter, compare their final text with your draft and learn from every change: wording, added or removed paragraphs, tone, facts. Offer to save reusable paragraphs, in the user's own wording, to the letter rules file, and new personal facts to the facts file.

End every loop with this question and apply the answer, with backups, before sending anything: "What should I update about letter writing (the rules, templates, reusable paragraphs) or about you (the facts file, standing answers)?"
