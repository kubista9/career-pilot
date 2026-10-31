# Scoring and routing

The model judges each job against the listing. `career-pilot score` does the arithmetic, so the same numbers are applied the same way every run. Everything is configured in the profile.

## How a job is scored

1. **Filters** drop a job before it is scored: a banned word in the title, too many required years, a closed listing.
2. The job is put on a **track**. Most jobs use `default`. A special track (see below) has its own criteria.
3. The agent rates every **criterion** of the track as a whole number from 0 to its `max`, using the `rubric` and only evidence from the listing and your facts.
4. `career-pilot score` adds the ratings up and checks:
   - **gates**: a criterion below its gate drops the job;
   - **minimums**: a criterion below its minimum means the job cannot reach the threshold, however high the total;
   - **threshold**: the total needed to count as a match.
5. **Routing** turns the result into a route.

```bash
career-pilot score --track default --criteria skill=4,location=2,language=1,growth=0
```

```
score: 7/9 (threshold 6: met)
route: strong
auto_submit: false
```

## Why minimums exist

If location and language are worth points, a job that fits you in nothing but those can reach the threshold. A minimum of 1 on `skill` stops that: no skill fit, no match.

## Routing rules

`routing` is an ordered list. The first rule whose conditions all hold names the route. Conditions:

| Condition | Holds when |
|---|---|
| `track` | the job's track has this name |
| `apply_type` | the job's apply type equals this (for example `easy_apply`) |
| `tags_any` | the job has at least one of these tags |
| `tags_none` | the job has none of these tags |
| `meets_threshold` | the threshold check is `true` or `false` |
| `min_score` | the total is at least this and no minimum failed |

The last rule has no `when`, so every job gets a route. Tags are labels the agent adds from the listing, for example `local_language_required`.

## Routes

Each route says what happens to a job:

```yaml
routes:
  strong:
    label: Strong match
    priority: 1        # prepared first when a daily cap bites
    auto_submit: false # waits for your approval
```

`auto_submit` defaults to `false`. Switching it on for a route is your decision, route by route.

## A special track

A second track is for jobs that need different criteria. Example: a thesis project. It has no hours criterion because it is full-time, and its rules for a long commute differ.

```yaml
scoring:
  tracks:
    project:
      criteria:
        skill:    { max: 5, rubric: "..." }
        location: { max: 2, rubric: "..." }
        language: { max: 1, rubric: "..." }
        growth:   { max: 1, rubric: "..." }
      threshold: 6
routing:
  - when: { track: project, meets_threshold: true }
    route: project
```

A commute rule that only lowers the score (instead of dropping the job) is simply a `location` criterion without a gate. A rule that drops the job is a gate.
