# The profile

`config/profile.yml` in your data dir holds every value the skill uses. The committed
[`config/profile.example.yml`](../config/profile.example.yml) shows all keys with a fake person.
Run `career-pilot doctor` to check yours.

| Key | What it holds | Used by |
|---|---|---|
| `candidate` | Name, email, phone, address, city, links, spoken languages with honest levels | Forms, letters |
| `sources` | Paths to your facts file, your letter rules and your CV folder | Every mode |
| `cvs` | Your CV files, each with a `focus` and a `language` | Choosing a CV |
| `answers` | Standard answers: hours, start date, salary, work permit, licence, and `other` for extra form fields | Forms |
| `boards` | Each board's search URL, whether it has easy apply, and its tracker pages | Search, sync |
| `search` | Location, result pages per search, and keyword groups. A group may set `pages`, `location`, `locations`, `boards` and `note` | Search |
| `filters` | Title words to drop, maximum years required, drop closed listings | Step 4 |
| `scoring` | Tracks, criteria with rubrics, gates, minimums, thresholds | `career-pilot score` |
| `routing` | Ordered rules that turn a score into a route | `career-pilot score` |
| `routes` | Per route: label, priority, `auto_submit` | Steps 5 and 6 |
| `daily_caps` | Most jobs prepared for approval and auto-submitted per day | Step 4 |
| `letters` | Length, paragraphs, banned phrases, forbidden claims, dashes | `career-pilot letter-check` |
| `tracker` | Where the CSV and the application folders are; status folders on or off | `career-pilot tracker` |
| `sync` | How many days of email to read | Sync |
| `adapters` | Optional Gmail and Notion adapters, off by default | Sync, tracker mirror |
| `privacy` | Words that must never appear in the repo. Never shown to the agent | `career-pilot privacy-check` |

Paths may start with `~`. A relative path is inside the data dir.

## What goes where

| It is about... | Put it in |
|---|---|
| Numbers, answers, paths, IDs, boards | `config/profile.yml` |
| Who you are and what you want | `modes/_profile.md` |
| Your habits and tools ("run letters through X first") | `modes/_custom.md` |
| Facts a letter may claim | your facts file and `cv.md` |

The agent reads only the slice it needs: `career-pilot brief <mode>` prints it. This keeps the context small.
