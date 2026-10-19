# Metrics

The program progresses by reps, then load: work up the rep range at a fixed
weight, and when every set reaches the top, add weight and start again. Every
metric here serves that loop.

## Status per exercise

Evaluated against the prescription in force, using the most recent session:

| status | rule |
|---|---|
| `stale` | nothing logged for more than `stale_days` (14). Checked first |
| `add-load` | every set at or above `hi` — the range is finished |
| `below-range` | any set under `lo` |
| `short-sets` | fewer sets than prescribed, otherwise on target |
| `on-target` | anything else |
| `untracked` | never logged. Hidden from the panel |

A fixed target (`lo == hi`, e.g. Wall sit 3×30 sec) can only be met or missed —
hitting 30 seconds is success, not a signal to progress.

## Progression chart

Per exercise, one point per session:

- **Top panel** — reps for every set, against a shaded target band. The line
  follows the **lowest-rep set**, because that is what gates adding load.
- **Bottom panel** — load as a step line, since load holds then jumps. Omitted
  when the exercise has no load in its last 3 sessions, which is how timed and
  band work share the same chart.

Two panels on one shared x-axis rather than two y-scales on one plot: aligning
independent scales invents a correlation that is not in the data.
