# training-log

Turns a Google Sheets training log into a static dashboard. Replaces the graphs
in Strong/Hevy for a program that progresses by reps-then-load, not by 1RM.

## Data source

Google Sheet, two tabs. The id is not in the repo: it comes from
`TRAININGLOG_SHEET_ID` (`.env` locally, `GOOGLE_SHEET_ID` secret in CI).

**`tracking`** — one row per set. Columns:
`date, exercise, checkbox, value1, value2, value3, reps, rpe, comments`

- `date` is `dd/mm/yyyy`, sometimes with ` HH:MM:SS` or ` HH:MM`
- `value1` is **load in kg**. `value2`/`value3` are only used by cardio rows (10 rows total) and mean time/distance
- `reps` holds seconds, not reps, for timed holds (Wall Sit)
- `checkbox` must be `TRUE`; `FALSE` and blank rows are not completed sets
- blank separator rows between blocks; skip rows with no `exercise`
- non-exercise rows in the same column: `Workout start`, `Workout end` (timestamps → session duration),
  `Sleep score` (1-10), `Body weight` (kg), `Meditation`

**`program`** — one row per prescribed exercise. Columns:
`session, order, exercise, sets, lo, hi, unit, valid_from`

- `exercise` matches `tracking.exercise` after lowercase+trim
- `unit` is `reps` or `sec`
- `lo`/`hi` are the rep range; `lo == hi` means a fixed target, not a ceiling
- `valid_from` dates a **complete snapshot** of the program. Changing anything means
  copying the whole block with a new date, so historical adherence is judged against
  the prescription in force at the time

## Data facts that are easy to get wrong

- **Blank and `0` in `value1` both mean bodyweight.** Treating blank as missing silently
  zeroes 90 of 190 Pull up sets
- **Name collisions differing only by case or trailing space**: `Calf Raises`/`Calf raises`,
  `Wall Sit`/`Wall sit`, `Meditation `, `Body weight `. Normalize with lowercase+strip
- **Pull up `value1` is added weight**, not assistance. Effective load = bodyweight + value1.
  Evidence: within one session load rises as reps fall
- Bodyweight is logged in `tracking`, not configured. Latest entry: 73 kg
- Log spans 2025-01-03 → 2026-10-19, ~3,057 completed sets, 69 exercises

## What the dashboard shows

Ordered by what the user acts on:

1. **Flag line** — exercises at the top of their rep range, under range, or stale
2. **Program panel** — each session in program order: exercise, target, last session's
   actual sets, status. Plain aligned columns; no boxes, no tables, no muscle-group headings
3. **Progression chart** — per exercise, reps per set against a shaded target band, with
   load stepping below on a shared x-axis. One point per session. The reps line follows the
   **limiting set** (lowest reps), because that gates adding load
4. **Session length & sleep** sparklines
5. **Stat strip** at the bottom

Status rules: every set at or above `hi` → add load; any set below `lo` → below range;
nothing logged for 14 days → stale; `lo == hi` → met or below only.

Estimated 1RM was tried and dropped on purpose: the goal is not a one-rep max, and
Epley is unreliable above ~10 reps, where most of these sets sit. Don't reintroduce it.

## Architecture

```
config.py              Config.load("config.toml")
sources/base.py        Source protocol: fetch(tab) -> list[dict]
sources/csv_source.py  local CSV export             <- current
sources/sheets.py      Sheets API, service account  <- written, never run live
ingest.py              parse, normalize names, split streams, program snapshots
metrics.py             program status, per-session series
render.py              payload dict -> template placeholder -> site/index.html
templates/dashboard.html   one /*__DATA__*/ slot, charts drawn client-side
cli.py                 `traininglog build` | `traininglog check`
```

Both sources return the same raw rows, so swapping is one config value. No runtime
dependencies: stdlib `csv` and `tomllib` are enough at this size, and `render` is a
single string replace rather than a template engine. Google libraries are the
`sheets` extra only.

`make all` = lint, test, build. 18 tests over a hand-built fixture slice that covers
the traps above.

`site/` is the build output and is gitignored; `docs/` is prose only. CI has two
workflows: `ci.yml` lints and tests, `pages.yml` builds from the live sheet and
deploys to Pages (needs the `GOOGLE_SERVICE_ACCOUNT` secret, and Pages source set
to GitHub Actions). `TRAININGLOG_SOURCE` overrides `config.toml`'s `source`, which
is how CI reads the sheet while the committed config stays on `csv`.

The published Pages site is public even from a private repo on Free/Pro plans.

Charts are hand-written SVG, no chart library — full control over the two-panel layout
and it keeps the page self-contained. Colors come from a validated categorical palette
(blue slot 1 = reps, orange slot 2 = load); both themes are defined at token level.

## Conventions

- Comments: only where the code is not self-evident. No section banners, no restating the line
- `README.md` stays short and links out; detail goes in `docs/*.md`
- Keep `TODO.md` current
- Dates in docs and comments are absolute, never "last week"
- Do not commit or push; leave that to the user
- Git identity under `personal/` resolves to `ldiezantich@gmail.com` via `includeIf`.
  Remote is `github-personal:lluis-diezantich/training-log.git`.
  `gh` is only authenticated as the work account, so `gh repo create` would target the
  wrong one — create the repo in the browser or add the personal account to `gh` first

## Current program (valid_from 2026-10-03)

```
Upper     Bench Press          2×6-8
          Pull Up              2×6-8
          Lateral Raises       2×8-12
          Bicep Curl           2×8-12
          Triceps Extension    2×8-12
          Wrist Curls          2×8-15
          Wrist Extension      2×8-15
Lower A   Band knee extension  1×12-15
          Wall sit             3×30 sec
          Calf Raises          2×15-20
          RDL                  2×6-8
          U RDL                2×8-12
Rest
```

Deadlift is **not** in the current program despite the old sheet header reading
"Lower A - Deadlift".
