# Workflow

The prompts in [`modes/`](../modes) are the single source of truth for what the skill does. This diagram only
shows the same flow at a glance. If the two ever disagree, the prompts are right.

```mermaid
flowchart TD
    start([career-pilot run]) --> load[1 Load<br/>profile and sources]
    load --> sync[2 Sync<br/>email and board trackers]
    sync --> search[3 Search<br/>every board, every group]
    search --> filter{4 Dropped by a hard filter<br/>or already tracked?}
    filter -- yes --> skipped[Skipped, not stored]
    filter -- no --> track{Special track?}
    track -- no --> rateDefault[Rate the criteria<br/>of the default track]
    track -- yes --> rateSpecial[Rate the criteria<br/>of the special track]
    rateDefault --> score[career-pilot score<br/>total, threshold, route]
    rateSpecial --> score
    score --> gate{Below a gate?}
    gate -- yes --> skipped
    gate -- no --> cap{Daily cap reached?}
    cap -- yes --> overCap[Tracked as to_review<br/>over daily cap]
    cap -- no --> prepare[5 Prepare<br/>folder, CV, letter if needed]
    prepare --> auto{6 Does the route<br/>have auto_submit on?}
    auto -- no --> ready[Ready: left open<br/>and waiting for your approval]
    auto -- yes --> checks{Every check passes?}
    checks -- yes --> submit[Submit and wait<br/>for the confirmation]
    checks -- no --> blocked[Left open: blocked,<br/>status to_review]
    ready --> log
    submit --> log
    blocked --> log
    overCap --> log
    log[7 Log and summarise<br/>tracker and chat summary] --> reply{You reply by ID<br/>review mode}
    reply -- edit --> edit[Change the letter,<br/>show it, wait for your OK]
    edit --> reply
    reply -- ok --> approved[Submit that ID only]
    reply -- nothing more --> done([Done])
    approved --> done
```

## The seven steps

| Step | What happens | Mode file |
|---|---|---|
| 1 Load | Check the profile and the files it points to | [run](../modes/run.md) |
| 2 Sync | Update statuses from email and the boards' own "applied" pages | [sync](../modes/sync.md) |
| 3 Search | Run the search plan on every board | [run](../modes/run.md) |
| 4 Filter and score | Drop, deduplicate, rate, score, route | [run](../modes/run.md) |
| 5 Prepare | Job folder, CV choice, contact, letter if needed | [run](../modes/run.md) |
| 6 Apply | Submit only where the route allows it. Everything else waits | [run](../modes/run.md) |
| 7 Log and summarise | Tracker, summary, the question for you | [run](../modes/run.md) |
| after the summary | Edits, approvals, feedback | [review](../modes/review.md) |

## Five things the diagram makes visible

- **Hard-filter exit**: a job that fails a filter or a gate is dropped and not stored.
- **Special track**: an optional second scoring track (for example a thesis project) with its own criteria.
- **Approval gate**: a route without `auto_submit` never submits. The page waits for you.
- **Daily cap**: past `daily_caps`, jobs are tracked but not prepared.
- **Review loop**: an edit is never an approval. Only an explicit OK for an ID sends it.
