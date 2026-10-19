# Data model

Source: a Google Sheet whose id is supplied through `TRAININGLOG_SHEET_ID`,
not committed. See [setup](setup.md).

## `tracking` — one row per set

| column | meaning |
|---|---|
| `date` | `dd/mm/yyyy`, sometimes with ` HH:MM:SS` or ` HH:MM` |
| `exercise` | exercise name, or a marker row (below) |
| `checkbox` | `TRUE` means the set was completed |
| `value1` | **load in kg** |
| `value2`, `value3` | cardio only (time, distance) — 10 rows in total, ignored |
| `reps` | reps, or **seconds** for timed holds |
| `rpe` | 1-10, optional |
| `comments` | free text, unused |

Marker rows in the `exercise` column, handled as separate streams:
`Workout start` / `Workout end` (timestamps → session duration), `Sleep score`,
`Body weight`. `Meditation` is ignored. Blank rows separate blocks.

## `program` — one row per prescribed exercise

| column | meaning |
|---|---|
| `session` | `Upper`, `Lower A`, … Sessions render in sheet order |
| `order` | position within the session |
| `exercise` | must match `tracking.exercise` after lowercase + whitespace collapse |
| `sets` | prescribed set count |
| `lo`, `hi` | rep range. `lo == hi` is a fixed target, not a ceiling |
| `unit` | `reps` or `sec` |
| `valid_from` | `yyyy-mm-dd`, dates a **complete snapshot** |

Rows sharing a `valid_from` are one whole version of the program, and the latest
version at or before the report date wins outright. To change anything, copy the
whole block, paste it below, and set a new date. Adherence then stays judged
against the prescription that was actually in force.

## Traps

**Blank and `0` in `value1` both mean bodyweight.** Treating blank as missing
zeroes 90 of 190 `Pull up` sets, all of them from 2026.

**Pull-up load is added weight, not assistance.** Within one session the load
rises as reps fall, which only happens when weight is being added. Effective
load is bodyweight + `value1`; bodyweight comes from the log, not config.

**Names collide on case and trailing space**: `Calf Raises`/`Calf raises`,
`Wall Sit`/`Wall sit`, `Meditation `, `Body weight `. `ingest.key()` collapses
both. Never match on the raw string.

**91 completed rows have no reps.** They cannot feed any chart and are dropped;
`traininglog build` prints the count so the gap stays visible.
