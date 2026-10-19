# Setup

## Local

```sh
make install
```

Export both tabs as CSV into `data/raw/` (gitignored):

```
data/raw/tracking.csv
data/raw/program.csv
```

```sh
make build      # writes site/index.html
make check      # row counts per tab
make test
make lint
```

Every target runs through `uv run`, so no activation step. To call the CLI
directly instead, either prefix it with `uv run` or activate the venv first
with `source .venv/bin/activate`.

`config.toml` holds tab names, output path and status rules. The sheet id is not
committed — copy `.env.example` to `.env` (gitignored, loaded by the Makefile):

```
TRAININGLOG_SHEET_ID=<the segment between /d/ and /edit in the sheet URL>
GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/training-log/service-account.json
```

Neither is needed for local CSV builds; both are needed for `source = "sheets"`.

## Reading the sheet directly

Set `source = "sheets"` in `config.toml` and follow
[Google Cloud setup](google-cloud.md) once, then:

```sh
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/training-log/service-account.json
make check      # row counts per tab, to confirm access
make build
```

Nothing else changes: both sources return the same rows, so `ingest` onward is
untouched. `SheetsSource` has not been run against the live API yet.

## Publishing

`.github/workflows/pages.yml` builds from the sheet and deploys to GitHub Pages
on push to `main`, nightly at 05:17 UTC, and on demand. Two things have to be in
place first:

1. **Settings → Pages → Source: GitHub Actions** (not "Deploy from a branch")
2. Two repository secrets under **Settings → Secrets and variables → Actions**:
   `GOOGLE_SERVICE_ACCOUNT` (the whole service account JSON) and
   `GOOGLE_SHEET_ID` (the spreadsheet id)

Until the secret exists the workflow fails on purpose, with a message pointing
at [Google Cloud setup](google-cloud.md).

The job sets `TRAININGLOG_SOURCE=sheets`, so the committed `config.toml` can
stay on `csv` for local work. Output goes to `site/`, which is gitignored — the
page is built in CI from the live sheet rather than committed.

**The published site is public.** On Free and Pro accounts, Pages serves
publicly even from a private repository; access control needs Enterprise Cloud.
The page contains bodyweight, sleep scores and full training history.
