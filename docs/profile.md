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
| `search` | Location, result pages per search, `next_stage_below`, and keyword groups. A group may set `stage`, `pages`, `location`, `locations`, `radius_km`, `max_age_days`, `boards` and `note`. A keyword can hold phrases joined with OR | Search |
| `filters` | Title words to drop, maximum years required, drop closed listings | Step 4 |
| `scoring` | Tracks, criteria with rubrics, gates, minimums, thresholds | `career-pilot score` |
| `routing` | Ordered rules that turn a score into a route | `career-pilot score` |
| `routes` | Per route: label, priority, `auto_submit` | Steps 5 and 6 |
| `daily_caps` | Most jobs prepared for approval and auto-submitted per day | Step 4 |
| `letters` | Body length and paragraph limits (minimum and maximum), banned phrases, forbidden claims, forbidden patterns, dashes, and `plan_first` | `career-pilot letter-check`, run and review |
| `tracker` | Where the CSV and the application folders are; status folders on or off | `career-pilot tracker` |
| `sync` | How many days of email to read | Sync |
| `followup` | `stale_days`: days of silence after which an applied job gets a status request (default 5). `rejected_within_days`: only follow up on rejections this recent. `skip_routes`: routes that never get a follow-up | `career-pilot tracker followups` |
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
